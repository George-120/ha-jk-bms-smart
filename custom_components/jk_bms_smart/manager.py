"""Runtime manager: one RS485 bus, its BMS units, energy counters and the battery bank totals."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.storage import Store

from .bus import BmsState, JkBus
from .const import (
    CONF_CONNECTION,
    CONF_UNITS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_STALE_AFTER,
    DOMAIN,
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
        self._pending: Any = None
        self._unsubs: list[Any] = []

    # ---- life cycle

    async def async_setup(self) -> None:
        data = await self._store.async_load() or {}
        self.energy = {int(k): v for k, v in (data.get("energy") or {}).items()}
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

    async def _async_save(self, *_: Any) -> None:
        await self._store.async_save({"energy": {str(k): v for k, v in self.energy.items()}})

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
        return {
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

    def card_payload(self, address: int) -> dict[str, Any]:
        """Everything the card needs for one pack (kept out of the recorder)."""
        s = self.bus.states.get(address)
        out: dict[str, Any] = {
            "card_version": VERSION,
            "address": address,
            "name": self.unit_name(address),
            "online": self.online(address),
            "mode": self.bus.mode,
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
            st = s.settings
            out["settings"] = {
                "cell_uvp": st.cell_uvp, "cell_uvpr": st.cell_uvpr, "cell_ovp": st.cell_ovp, "cell_ovpr": st.cell_ovpr,
                "balance_trigger": st.balance_trigger, "balance_start": st.balance_start,
                "soc100_voltage": st.soc100_voltage, "soc0_voltage": st.soc0_voltage,
                "charge_voltage": st.charge_voltage, "float_voltage": st.float_voltage,
                "max_charge_current": st.max_charge_current, "max_discharge_current": st.max_discharge_current,
                "max_balance_current": st.max_balance_current, "design_capacity_ah": st.design_capacity_ah,
                "charge_switch": st.charge_switch, "discharge_switch": st.discharge_switch, "balance_switch": st.balance_switch,
                "charge_ot": st.charge_ot, "discharge_ot": st.discharge_ot, "charge_ut": st.charge_ut, "mos_ot": st.mos_ot,
            }
        if s.info:
            out["info"] = {
                "model": s.info.model, "hardware": s.info.hardware, "software": s.info.software,
                "serial": s.info.serial, "manufacturing_date": s.info.manufacturing_date,
            }
        energy = self.energy.get(address, {})
        out["charged_kwh"] = round(energy.get("charged", 0.0), 3)
        out["discharged_kwh"] = round(energy.get("discharged", 0.0), 3)
        return out
