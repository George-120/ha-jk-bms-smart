"""Long-term pack health: which cell runs out first, daily extremes and wire-resistance trends.

Pure Python (no Home Assistant imports) so it can be unit tested. The manager feeds it every
live-data frame and stores ``as_store()`` with the other counters.

* **Weakest cell** — while a pack is discharging below ``LOW_SOC`` the lowest cell is the one
  that will hit the protection first. We add up for how long each cell is the lowest; the cell
  with the most time is the weak one. A cell that is lowest *every* time at the bottom is a
  real capacity problem, a cell that changes is just noise.
* **Runs ahead when full** — the same at the top (charging above ``HIGH_SOC``): the cell that
  reaches full first.
* **Per day** — largest cell difference, lowest/highest cell and temperature, SoC range,
  charged/discharged Ah and the average balance-wire resistance per cell.
"""

from __future__ import annotations

from typing import Any

LOW_SOC = 30  # %: below this, while discharging, the lowest cell counts as "runs out first"
HIGH_SOC = 90  # %: above this, while charging, the highest cell counts as "full first"
MIN_CURRENT = 1.0  # A: ignore standby
MIN_SECONDS = 600  # need at least 10 minutes of evidence before naming a weak cell
KEEP_DAYS = 400


def _round(v: float | None, d: int) -> float | None:
    return None if v is None else round(v, d)


class HealthTracker:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.packs: dict[int, dict[str, Any]] = {}
        for key, pack in (data or {}).items():
            try:
                self.packs[int(key)] = pack
            except (TypeError, ValueError):
                continue

    def _pack(self, address: int, cells: int) -> dict[str, Any]:
        p = self.packs.setdefault(address, {"low_s": [], "high_s": [], "days": {}})
        for k in ("low_s", "high_s"):
            if len(p[k]) != cells:
                p[k] = (p[k] + [0.0] * cells)[:cells]
        return p

    def sample(self, address: int, c: Any, day: str, dt: float) -> None:
        """One live-data frame. ``c`` is a protocol.CellData, ``dt`` seconds since the last one."""
        if not c.cells:
            return
        n = len(c.cells)
        p = self._pack(address, n)
        lo_i = min(range(n), key=lambda i: c.cells[i])
        hi_i = max(range(n), key=lambda i: c.cells[i])
        if 0 < dt <= 120:
            if c.current <= -MIN_CURRENT and c.soc <= LOW_SOC:
                p["low_s"][lo_i] += dt
            elif c.current >= MIN_CURRENT and c.soc >= HIGH_SOC:
                p["high_s"][hi_i] += dt
        d = p["days"].get(day)
        if d is None:
            d = p["days"][day] = {"dmax": 0, "vmin": None, "vmax": None, "tmin": None, "tmax": None,
                                  "soc_min": None, "soc_max": None, "low": None, "ah_in": 0.0, "ah_out": 0.0,
                                  "res": [0.0] * n, "n": 0}
            self._trim(p)
        delta = round((c.cells[hi_i] - c.cells[lo_i]) * 1000)
        d["dmax"] = max(d["dmax"], delta)
        d["vmin"] = c.cells[lo_i] if d["vmin"] is None else min(d["vmin"], c.cells[lo_i])
        d["vmax"] = c.cells[hi_i] if d["vmax"] is None else max(d["vmax"], c.cells[hi_i])
        temps = [t for t in [c.mos_temp, *c.temps] if t is not None]
        if temps:
            d["tmin"] = min(temps) if d["tmin"] is None else min(d["tmin"], min(temps))
            d["tmax"] = max(temps) if d["tmax"] is None else max(d["tmax"], max(temps))
        if d["soc_min"] is None or c.soc < d["soc_min"]:
            d["soc_min"] = c.soc
            d["low"] = lo_i  # lowest cell at the emptiest moment of the day
        d["soc_max"] = c.soc if d["soc_max"] is None else max(d["soc_max"], c.soc)
        if 0 < dt <= 120:
            ah = c.current * dt / 3600
            if ah >= 0:
                d["ah_in"] += ah
            else:
                d["ah_out"] -= ah
        res = c.resistances or []
        if len(d["res"]) != n:
            d["res"] = [0.0] * n
            d["n"] = 0
        if len(res) == n and any(res):
            d["res"] = [a + b for a, b in zip(d["res"], res, strict=False)]
            d["n"] += 1

    @staticmethod
    def _trim(p: dict[str, Any]) -> None:
        days = sorted(p["days"])
        for old in days[:-KEEP_DAYS]:
            del p["days"][old]

    # ---- results

    def weak_cell(self, address: int) -> dict[str, Any]:
        p = self.packs.get(address)
        out: dict[str, Any] = {"weakest": None, "weakest_share": None, "first_full": None, "first_full_share": None,
                               "low_minutes": [], "high_minutes": []}
        if not p:
            return out
        for key, name in (("low_s", "weakest"), ("high_s", "first_full")):
            secs = p.get(key) or []
            out["low_minutes" if key == "low_s" else "high_minutes"] = [round(s / 60) for s in secs]
            total = sum(secs)
            if total >= MIN_SECONDS:
                i = max(range(len(secs)), key=lambda j: secs[j])
                out[name] = i + 1
                out[f"{name}_share"] = round(100 * secs[i] / total)
        return out

    def today(self, address: int, day: str) -> dict[str, Any] | None:
        p = self.packs.get(address)
        return self._export_day(day, p["days"][day]) if p and day in p["days"] else None

    def history(self, address: int, days: int = 90) -> list[dict[str, Any]]:
        p = self.packs.get(address)
        if not p:
            return []
        keys = sorted(p["days"])[-days:]
        return [self._export_day(k, p["days"][k]) for k in keys]

    @staticmethod
    def _export_day(day: str, d: dict[str, Any]) -> dict[str, Any]:
        n = d.get("n") or 0
        return {
            "day": day,
            "delta_max_mv": d.get("dmax"),
            "cell_min": _round(d.get("vmin"), 3),
            "cell_max": _round(d.get("vmax"), 3),
            "temp_min": _round(d.get("tmin"), 1),
            "temp_max": _round(d.get("tmax"), 1),
            "soc_min": d.get("soc_min"),
            "soc_max": d.get("soc_max"),
            "lowest_cell": None if d.get("low") is None else d["low"] + 1,
            "ah_in": round(d.get("ah_in") or 0, 1),
            "ah_out": round(d.get("ah_out") or 0, 1),
            "resistance_mohm": [round(r / n * 1000, 1) for r in d["res"]] if n else [],
        }

    def reset(self, address: int) -> None:
        p = self.packs.get(address)
        if p:
            p["low_s"] = [0.0] * len(p["low_s"])
            p["high_s"] = [0.0] * len(p["high_s"])

    def as_store(self) -> dict[str, Any]:
        return {str(k): v for k, v in self.packs.items()}
