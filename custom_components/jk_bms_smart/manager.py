"""Runtime manager: one RS485 bus, its BMS units, energy counters and the battery bank totals."""

from __future__ import annotations

import json
import logging
import math
import re
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .alerts import Alerts
from .bus import BmsState, JkBus
from .health import HealthTracker
from .labels import label
from .protocol import COMPARE_KEYS, WRITABLE, plan_changes
from .const import (
    BACKUP_DIR,
    CONF_CONNECTION,
    CONF_UNITS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_STALE_AFTER,
    DOMAIN,
    OPT_ALLOW_CHANGES,
    OPT_POLL_INTERVAL,
    OPT_STALE_AFTER,
    SIGNAL_UPDATE,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)

STORE_VERSION = 1


@dataclass
class Unit:
    address: int
    name: str
    cells: int = 16


class JkBmsManager:
    """Glue between the bus engine and Home Assistant."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        opts = entry.options
        self.units: list[Unit] = [
            Unit(int(u["address"]), u.get("name") or f"JK BMS {i + 1}", int(u.get("cells") or 16))
            for i, u in enumerate(entry.data.get(CONF_UNITS, []))
        ]
        self.poll_interval = float(opts.get(OPT_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        self.stale_after = float(opts.get(OPT_STALE_AFTER, DEFAULT_STALE_AFTER))
        self.allow_changes = bool(opts.get(OPT_ALLOW_CHANGES, False))
        self.bus = JkBus(
            hass.loop,
            entry.data[CONF_CONNECTION],
            poll_interval=self.poll_interval,
            on_update=self._on_bus_update,
        )
        self.signal = SIGNAL_UPDATE.format(entry.entry_id)
        self.version = VERSION
        self.own_entities: dict[str, str] = {}  # key -> entity_id, filled by entities
        self.energy: dict[int, dict[str, float]] = {}
        self._energy_ts: dict[int, float] = {}
        self._store: Store = Store(hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}.energy")
        self._health_store: Store = Store(hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}.health")
        self.health = HealthTracker()
        self._ema: dict[int, float] = {}  # smoothed current per pack (for time to full / empty)
        self._last_backup: dict[int, float] = {}
        self.alerts = Alerts(self)
        self._pending: Any = None
        self._unsubs: list[Any] = []

    # ---- life cycle

    async def async_setup(self) -> None:
        data = await self._store.async_load() or {}
        self.energy = {int(k): v for k, v in (data.get("energy") or {}).items()}
        self.health = HealthTracker((await self._health_store.async_load() or {}).get("packs"))
        await self.bus.open()  # raises BusError/PortBusy -> ConfigEntryNotReady
        self.bus.mode = self.entry.data.get("mode")
        self.bus.start([u.address for u in self.units])
        self._unsubs.append(
            async_track_time_interval(self.hass, self._async_save, timedelta(minutes=5))
        )

    async def async_unload(self) -> None:
        for unsub in self._unsubs:
            unsub()
        if self._pending:
            self._pending()
        await self.bus.close()
        await self._async_save()
        self.alerts.clear()

    async def _async_save(self, *_: Any) -> None:
        await self._store.async_save({"energy": {str(k): v for k, v in self.energy.items()}})
        await self._health_store.async_save({"packs": self.health.as_store()})

    # ---- updates

    @callback
    def _on_bus_update(self, address: int, frame_type: int) -> None:
        if address >= 0 and frame_type == 2:
            self._integrate(address)
        # coalesce: at most one entity refresh per second
        if self._pending is None:
            self._pending = async_call_later(self.hass, 1.0, self._flush)

    @callback
    def _flush(self, _now: Any = None) -> None:
        self._pending = None
        async_dispatcher_send(self.hass, self.signal)
        self.alerts.evaluate()

    def _integrate(self, address: int) -> None:
        """Charged / discharged kWh per BMS from DC power (trapezoid-free, short steps)."""
        state = self.bus.states.get(address)
        if not state or not state.cells:
            return
        now = time.monotonic()
        last = self._energy_ts.get(address)
        self._energy_ts[address] = now
        if last is None:
            return
        dt = now - last
        if dt <= 0 or dt > 120:  # gap too long: do not guess
            return
        self.health.sample(address, state.cells, dt_util.now().date().isoformat(), dt)
        k = 1 - math.exp(-dt / 120)  # ~2 minute smoothing
        prev = self._ema.get(address, state.cells.current)
        self._ema[address] = prev + (state.cells.current - prev) * k
        kwh = state.cells.power * dt / 3_600_000
        bucket = self.energy.setdefault(address, {"charged": 0.0, "discharged": 0.0})
        if kwh >= 0:
            bucket["charged"] += kwh
        else:
            bucket["discharged"] -= kwh

    # ---- accessors

    def state(self, address: int) -> BmsState | None:
        return self.bus.states.get(address)

    def online(self, address: int) -> bool:
        s = self.bus.states.get(address)
        return bool(s and s.online(time.monotonic(), self.stale_after))

    def unit_name(self, address: int) -> str:
        for u in self.units:
            if u.address == address:
                return u.name
        return f"JK BMS {address}"

    def bank(self) -> dict[str, Any]:
        """Totals across all online units."""
        units = [self.bus.states[u.address] for u in self.units if self.online(u.address)]
        cells = [s.cells for s in units if s.cells]
        if not cells:
            return {"online": 0, "total": len(self.units)}
        full = sum(c.full_ah for c in cells)
        remaining = sum(c.remaining_ah for c in cells)
        all_cells = [(v, s.address, i) for s in units if s.cells for i, v in enumerate(s.cells.cells)]
        vmin = min(all_cells)
        vmax = max(all_cells)
        voltage = sum(c.voltage for c in cells) / len(cells)
        energy_in = sum(self.energy.get(u.address, {}).get("charged", 0.0) for u in self.units)
        energy_out = sum(self.energy.get(u.address, {}).get("discharged", 0.0) for u in self.units)
        socs = [c.soc for c in cells]
        ema = sum(self._ema.get(s.address, s.cells.current) for s in units if s.cells)
        to_full, to_empty = _time_to(remaining, full, ema)
        return {
            "soc_spread": max(socs) - min(socs) if len(socs) > 1 else 0,
            "time_to_full_min": to_full,
            "time_to_empty_min": to_empty,
            "online": len(cells),
            "total": len(self.units),
            "soc": round(remaining / full * 100, 1) if full else round(sum(c.soc for c in cells) / len(cells), 1),
            "voltage": round(voltage, 2),
            "current": round(sum(c.current for c in cells), 2),
            "power": round(sum(c.power for c in cells), 0),
            "remaining_ah": round(remaining, 1),
            "full_ah": round(full, 1),
            "remaining_kwh": round(remaining * voltage / 1000, 2),
            "full_kwh": round(full * voltage / 1000, 2),
            "cell_min": vmin[0],
            "cell_min_where": f"{self.unit_name(vmin[1])} · {vmin[2] + 1}",
            "cell_max": vmax[0],
            "cell_max_where": f"{self.unit_name(vmax[1])} · {vmax[2] + 1}",
            "cell_delta": round(vmax[0] - vmin[0], 3),
            "temp_max": max((t for c in cells for t in [c.mos_temp, *c.temps] if t is not None), default=None),
            "problems": sorted({p for c in cells for p in c.problems}),
            "charged_kwh": round(energy_in, 3),
            "discharged_kwh": round(energy_out, 3),
        }

    # ---- health

    def time_to(self, address: int) -> tuple[int | None, int | None]:
        s = self.bus.states.get(address)
        if not s or not s.cells or not self.online(address):
            return None, None
        return _time_to(s.cells.remaining_ah, s.cells.full_ah, self._ema.get(address, s.cells.current))

    def health_payload(self, address: int) -> dict[str, Any]:
        to_full, to_empty = self.time_to(address)
        return {
            **self.health.weak_cell(address),
            "today": self.health.today(address, dt_util.now().date().isoformat()),
            "time_to_full_min": to_full,
            "time_to_empty_min": to_empty,
        }

    # ---- settings: compare, write, copy, back up

    def setting_label(self, key: str) -> str:
        return label(key, self.hass.config.language or "en")

    def settings_of(self, address: int) -> dict[str, Any] | None:
        s = self.bus.states.get(address)
        if not s or not s.settings:
            return None
        d = s.settings.as_dict()
        return {k: d.get(k) for k in WRITABLE}

    def settings_mismatch(self) -> dict[str, dict[str, Any]]:
        """{key: {pack name: value}} for every setting that is not the same on all online packs."""
        have = [(u, self.settings_of(u.address)) for u in self.units if self.online(u.address)]
        have = [(u, s) for u, s in have if s]
        if len(have) < 2:
            return {}
        out: dict[str, dict[str, Any]] = {}
        for key in COMPARE_KEYS:
            vals = {u.name: s.get(key) for u, s in have}
            if any(v is None for v in vals.values()):
                continue
            scale = WRITABLE[key].scale
            if len({round(float(v) * scale) for v in vals.values()}) > 1:
                out[key] = vals
        return out

    async def async_write(self, address: int, key: str, value: float, *, backup: bool = True) -> None:
        """Change one BMS setting (only when the user switched changes on)."""
        from .bus import BusError

        if not self.allow_changes:
            raise HomeAssistantError("Changing settings is switched off (Configure → Settings)")
        if backup:
            await self._auto_backup(address)
        try:
            await self.bus.write(address, key, float(value))
        except (ValueError, BusError) as err:
            raise HomeAssistantError(str(err)) from err

    async def async_apply(self, address: int, wanted: dict[str, Any], keys: list[str] | None = None,
                          *, dry_run: bool = False) -> dict[str, Any]:
        """Bring one pack to ``wanted`` (copy from another pack / restore a backup)."""
        current = self.settings_of(address)
        if current is None:
            raise HomeAssistantError(f"{self.unit_name(address)}: settings not received yet")
        changes = plan_changes(current, wanted, keys)
        result: dict[str, Any] = {
            "pack": self.unit_name(address),
            "changes": [{"key": k, "label": self.setting_label(k), "old": o, "new": n} for k, o, n in changes],
            "done": [], "failed": {},
        }
        if dry_run or not changes:
            return result
        if not self.allow_changes:
            raise HomeAssistantError("Changing settings is switched off (Configure → Settings)")
        await self._auto_backup(address, force=True)
        for key, _old, new in changes:
            try:
                await self.async_write(address, key, new, backup=False)
                result["done"].append(key)
            except HomeAssistantError as err:
                result["failed"][key] = str(err)
        return result

    @property
    def backup_dir(self) -> Path:
        return Path(self.hass.config.path(BACKUP_DIR))

    async def async_backup(self, address: int, reason: str = "manual") -> str:
        """Write the pack's settings to a JSON file; returns the file name."""
        settings = self.settings_of(address)
        if settings is None:
            raise HomeAssistantError(f"{self.unit_name(address)}: settings not received yet")
        s = self.bus.states.get(address)
        info = s.info if s else None
        now = dt_util.now()
        slug = re.sub(r"[^a-z0-9]+", "-", self.unit_name(address).lower()).strip("-") or f"bms-{address}"
        name = f"{now:%Y%m%d-%H%M%S}-{slug}{'-auto' if reason == 'auto' else ''}.json"
        doc = {
            "format": "jk_bms_smart.settings", "version": 1, "created": now.isoformat(), "reason": reason,
            "pack": self.unit_name(address), "address": address,
            "model": info.model if info else None, "firmware": info.software if info else None,
            "serial": info.serial if info else None, "settings": settings,
        }
        folder = self.backup_dir

        def _write() -> None:
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_text(json.dumps(doc, indent=2), encoding="utf-8")
            autos = sorted(p for p in folder.glob("*-auto.json"))
            for old in autos[:-30]:  # keep the last 30 automatic backups
                old.unlink(missing_ok=True)

        await self.hass.async_add_executor_job(_write)
        self._last_backup[address] = time.monotonic()
        return name

    async def _auto_backup(self, address: int, force: bool = False) -> None:
        """Before a change: keep a copy of how the pack was (at most once an hour per pack)."""
        last = self._last_backup.get(address)
        if not force and last and time.monotonic() - last < 3600:
            return
        try:
            await self.async_backup(address, "auto")
        except Exception as err:  # noqa: BLE001 - a backup problem must not block the change
            _LOGGER.warning("Automatic settings backup of %s failed: %s", self.unit_name(address), err)

    async def async_list_backups(self) -> list[dict[str, Any]]:
        folder = self.backup_dir

        def _read() -> list[dict[str, Any]]:
            out = []
            if not folder.is_dir():
                return out
            for path in sorted(folder.glob("*.json"), reverse=True)[:100]:
                try:
                    doc = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if doc.get("format") != "jk_bms_smart.settings":
                    continue
                out.append({"file": path.name, "created": doc.get("created"), "pack": doc.get("pack"),
                            "address": doc.get("address"), "reason": doc.get("reason"), "serial": doc.get("serial"),
                            "settings": doc.get("settings") or {}})
            return out

        return await self.hass.async_add_executor_job(_read)

    async def async_read_backup(self, file: str) -> dict[str, Any]:
        if not re.fullmatch(r"[\w.\-]+\.json", file):
            raise HomeAssistantError("Invalid backup file name")
        path = self.backup_dir / file

        def _read() -> dict[str, Any]:
            return json.loads(path.read_text(encoding="utf-8"))

        try:
            doc = await self.hass.async_add_executor_job(_read)
        except (OSError, ValueError) as err:
            raise HomeAssistantError(f"Cannot read {file}: {err}") from err
        if doc.get("format") != "jk_bms_smart.settings":
            raise HomeAssistantError(f"{file} is not a JK BMS Smart settings backup")
        return doc

    def card_payload(self, address: int) -> dict[str, Any]:
        """Everything the card needs for one pack (kept out of the recorder)."""
        s = self.bus.states.get(address)
        out: dict[str, Any] = {
            "card_version": VERSION,
            "address": address,
            "name": self.unit_name(address),
            "online": self.online(address),
            "mode": self.bus.mode,
            "allow_changes": self.allow_changes,
            "entities": {k.split(":", 1)[1]: v for k, v in self.own_entities.items() if k.startswith(f"{address}:")},
        }
        if not s:
            return out
        if s.cells:
            c = s.cells
            out.update(
                cells=c.cells,
                resistances=c.resistances,
                cell_min_index=c.cells.index(c.cell_min) if c.cells else None,
                cell_max_index=c.cells.index(c.cell_max) if c.cells else None,
                cell_avg=c.cell_avg,
                cell_delta=round(c.cell_max - c.cell_min, 3),
                voltage=c.voltage,
                current=c.current,
                power=c.power,
                soc=c.soc,
                soh=c.soh,
                remaining_ah=c.remaining_ah,
                full_ah=c.full_ah,
                cycles=c.cycles,
                mos_temp=c.mos_temp,
                temps=c.temps,
                balance_state=c.balance_state,
                balance_current=c.balance_current,
                charging=c.charging_enabled,
                discharging=c.discharging_enabled,
                heating=c.heating,
                precharge=c.precharge,
                charger_plugged=c.charger_plugged,
                alarms=c.alarms,
                problems=c.problems,
                runtime_s=c.runtime_s,
            )
        if s.settings:
            out["settings"] = {k: v for k, v in s.settings.as_dict().items() if k not in ("address",)}
        out["health"] = self.health_payload(address)
        if s.info:
            out["info"] = {
                "model": s.info.model, "hardware": s.info.hardware, "software": s.info.software,
                "serial": s.info.serial, "manufacturing_date": s.info.manufacturing_date,
            }
        energy = self.energy.get(address, {})
        out["charged_kwh"] = round(energy.get("charged", 0.0), 3)
        out["discharged_kwh"] = round(energy.get("discharged", 0.0), 3)
        return out


def _time_to(remaining_ah: float, full_ah: float, current: float) -> tuple[int | None, int | None]:
    """Minutes until full (charging) or empty (discharging) at the smoothed current; None when idle."""
    if current > 0.5 and full_ah > remaining_ah:
        return round((full_ah - remaining_ah) / current * 60), None
    if current < -0.5 and remaining_ah > 0:
        return None, round(remaining_ah / -current * 60)
    return None, None
