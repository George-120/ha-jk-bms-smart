"""Sensors per BMS and for the whole battery bank."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JkBmsConfigEntry
from .bus import BmsState
from .entity import JkEntity
from .manager import JkBmsManager

AH = "Ah"
MOHM = "mΩ"


@dataclass(frozen=True, kw_only=True)
class UnitSensor(SensorEntityDescription):
    value: Callable[[BmsState, JkBmsManager], Any]
    enabled: bool = True


def _c(fn: Callable[[Any], Any]) -> Callable[[BmsState, JkBmsManager], Any]:
    return lambda s, _m: fn(s.cells) if s.cells else None


def _s(fn: Callable[[Any], Any]) -> Callable[[BmsState, JkBmsManager], Any]:
    return lambda s, _m: fn(s.settings) if s.settings else None


V = dict(device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT)
A = dict(device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT)
T = dict(device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT)
DIAG = dict(entity_category=EntityCategory.DIAGNOSTIC)

UNIT_SENSORS: tuple[UnitSensor, ...] = (
    UnitSensor(key="soc", device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE,
               state_class=SensorStateClass.MEASUREMENT, value=_c(lambda c: c.soc)),
    UnitSensor(key="voltage", suggested_display_precision=2, value=_c(lambda c: c.voltage), **V),
    UnitSensor(key="current", suggested_display_precision=2, value=_c(lambda c: c.current), **A),
    UnitSensor(key="power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0, value=_c(lambda c: c.power)),
    UnitSensor(key="remaining_capacity", native_unit_of_measurement=AH, state_class=SensorStateClass.MEASUREMENT,
               suggested_display_precision=1, icon="mdi:battery-high", value=_c(lambda c: c.remaining_ah)),
    UnitSensor(key="full_capacity", native_unit_of_measurement=AH, state_class=SensorStateClass.MEASUREMENT,
               suggested_display_precision=1, icon="mdi:battery", value=_c(lambda c: c.full_ah)),
    UnitSensor(key="stored_energy", device_class=SensorDeviceClass.ENERGY_STORAGE, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2,
               value=_c(lambda c: round(c.remaining_ah * c.voltage / 1000, 3))),
    UnitSensor(key="soh", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT,
               icon="mdi:heart-pulse", value=_c(lambda c: c.soh)),
    UnitSensor(key="cycles", state_class=SensorStateClass.TOTAL_INCREASING, icon="mdi:battery-sync", value=_c(lambda c: c.cycles)),
    UnitSensor(key="cycle_capacity", native_unit_of_measurement=AH, state_class=SensorStateClass.TOTAL_INCREASING,
               suggested_display_precision=0, icon="mdi:battery-sync-outline", value=_c(lambda c: c.cycle_ah), **DIAG),
    UnitSensor(key="cell_min", suggested_display_precision=3, value=_c(lambda c: c.cell_min), **V),
    UnitSensor(key="cell_max", suggested_display_precision=3, value=_c(lambda c: c.cell_max), **V),
    UnitSensor(key="cell_avg", suggested_display_precision=3, value=_c(lambda c: c.cell_avg), **V),
    UnitSensor(key="cell_delta", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0,
               value=_c(lambda c: round((c.cell_max - c.cell_min) * 1000))),
    UnitSensor(key="cell_min_number", icon="mdi:numeric", value=_c(lambda c: c.cells.index(c.cell_min) + 1 if c.cells else None)),
    UnitSensor(key="cell_max_number", icon="mdi:numeric", value=_c(lambda c: c.cells.index(c.cell_max) + 1 if c.cells else None)),
    UnitSensor(key="mos_temperature", value=_c(lambda c: c.mos_temp), **T),
    UnitSensor(key="balance_current", suggested_display_precision=2, value=_c(lambda c: c.balance_current), **A),
    UnitSensor(key="balance_state", device_class=SensorDeviceClass.ENUM, options=["off", "charging", "discharging"],
               value=_c(lambda c: c.balance_state)),
    UnitSensor(key="problems", icon="mdi:alert-circle-outline", state_class=SensorStateClass.MEASUREMENT,
               value=_c(lambda c: len(c.problems))),
    UnitSensor(key="energy_charged", device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
               state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=2,
               value=lambda s, m: round(m.energy.get(s.address, {}).get("charged", 0.0), 3)),
    UnitSensor(key="energy_discharged", device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
               state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=2,
               value=lambda s, m: round(m.energy.get(s.address, {}).get("discharged", 0.0), 3)),
    UnitSensor(key="runtime", device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.SECONDS,
               suggested_unit_of_measurement=UnitOfTime.DAYS, value=_c(lambda c: c.runtime_s), **DIAG),
    # 1.2: health and time estimates
    UnitSensor(key="time_to_full", device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.MINUTES,
               suggested_unit_of_measurement=UnitOfTime.HOURS, suggested_display_precision=1, icon="mdi:battery-clock",
               value=lambda s, m: m.time_to(s.address)[0]),
    UnitSensor(key="time_to_empty", device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.MINUTES,
               suggested_unit_of_measurement=UnitOfTime.HOURS, suggested_display_precision=1, icon="mdi:battery-clock-outline",
               value=lambda s, m: m.time_to(s.address)[1]),
    UnitSensor(key="weakest_cell", icon="mdi:battery-alert-variant-outline",
               value=lambda s, m: m.health.weak_cell(s.address)["weakest"]),
    UnitSensor(key="cell_delta_max_today", device_class=SensorDeviceClass.VOLTAGE,
               native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, suggested_display_precision=0,
               icon="mdi:arrow-expand-vertical",
               value=lambda s, m: (m.health.today(s.address, _today()) or {}).get("delta_max_mv")),
    UnitSensor(key="heater_current", enabled=False, suggested_display_precision=2, value=_c(lambda c: c.heater_current), **A, **DIAG),
    # settings (read only)
    UnitSensor(key="design_capacity", native_unit_of_measurement=AH, suggested_display_precision=0, icon="mdi:battery-outline",
               value=_s(lambda s: s.design_capacity_ah), **DIAG),
    UnitSensor(key="cell_ovp", suggested_display_precision=3, value=_s(lambda s: s.cell_ovp), **{**V, "state_class": None}, **DIAG),
    UnitSensor(key="cell_uvp", suggested_display_precision=3, value=_s(lambda s: s.cell_uvp), **{**V, "state_class": None}, **DIAG),
    UnitSensor(key="charge_voltage_setting", suggested_display_precision=3, value=_s(lambda s: s.charge_voltage),
               **{**V, "state_class": None}, **DIAG),
    UnitSensor(key="balance_trigger", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
               suggested_display_precision=0, value=_s(lambda s: round(s.balance_trigger * 1000)), **DIAG),
    UnitSensor(key="max_charge_current", suggested_display_precision=0, value=_s(lambda s: s.max_charge_current),
               **{**A, "state_class": None}, **DIAG),
    UnitSensor(key="max_discharge_current", suggested_display_precision=0, value=_s(lambda s: s.max_discharge_current),
               **{**A, "state_class": None}, **DIAG),
)


@dataclass(frozen=True, kw_only=True)
class BankSensor(SensorEntityDescription):
    field: str


BANK_SENSORS: tuple[BankSensor, ...] = (
    BankSensor(key="bank_soc", field="soc", device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0),
    BankSensor(key="bank_power", field="power", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0),
    BankSensor(key="bank_current", field="current", suggested_display_precision=1, **A),
    BankSensor(key="bank_voltage", field="voltage", suggested_display_precision=2, **V),
    BankSensor(key="bank_stored_energy", field="remaining_kwh", device_class=SensorDeviceClass.ENERGY_STORAGE,
               native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    BankSensor(key="bank_capacity_energy", field="full_kwh", device_class=SensorDeviceClass.ENERGY_STORAGE,
               native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1),
    BankSensor(key="bank_remaining_capacity", field="remaining_ah", native_unit_of_measurement=AH,
               state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0, icon="mdi:battery-high"),
    BankSensor(key="bank_cell_min", field="cell_min", suggested_display_precision=3, **V),
    BankSensor(key="bank_cell_max", field="cell_max", suggested_display_precision=3, **V),
    BankSensor(key="bank_cell_delta", field="cell_delta_mv", device_class=SensorDeviceClass.VOLTAGE,
               native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0),
    BankSensor(key="bank_temperature_max", field="temp_max", **T),
    BankSensor(key="bank_energy_charged", field="charged_kwh", device_class=SensorDeviceClass.ENERGY,
               native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=2),
    BankSensor(key="bank_energy_discharged", field="discharged_kwh", device_class=SensorDeviceClass.ENERGY,
               native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=2),
    BankSensor(key="bank_units_online", field="online", icon="mdi:battery-check", state_class=SensorStateClass.MEASUREMENT),
    BankSensor(key="bank_soc_spread", field="soc_spread", native_unit_of_measurement=PERCENTAGE,
               state_class=SensorStateClass.MEASUREMENT, icon="mdi:arrow-split-vertical"),
    BankSensor(key="bank_time_to_full", field="time_to_full_min", device_class=SensorDeviceClass.DURATION,
               native_unit_of_measurement=UnitOfTime.MINUTES, suggested_unit_of_measurement=UnitOfTime.HOURS,
               suggested_display_precision=1, icon="mdi:battery-clock"),
    BankSensor(key="bank_time_to_empty", field="time_to_empty_min", device_class=SensorDeviceClass.DURATION,
               native_unit_of_measurement=UnitOfTime.MINUTES, suggested_unit_of_measurement=UnitOfTime.HOURS,
               suggested_display_precision=1, icon="mdi:battery-clock-outline"),
)


def _today() -> str:
    from homeassistant.util import dt as dt_util

    return dt_util.now().date().isoformat()


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    manager = entry.runtime_data
    entities: list[SensorEntity] = [JkBankSensor(manager, d) for d in BANK_SENSORS]
    for unit in manager.units:
        entities += [JkUnitSensor(manager, d, unit.address) for d in UNIT_SENSORS]
        count = unit.cells or 16
        entities += [JkCellSensor(manager, unit.address, i, resistance=False) for i in range(count)]
        entities += [JkCellSensor(manager, unit.address, i, resistance=True) for i in range(count)]
        entities += [JkTempSensor(manager, unit.address, i) for i in range(5)]
    async_add_entities(entities)


class JkUnitSensor(JkEntity, SensorEntity):
    entity_description: UnitSensor
    # The card payload is large and changes every few seconds: keep it out of the history.
    _unrecorded_attributes = frozenset({"pack"})

    def __init__(self, manager: JkBmsManager, description: UnitSensor, address: int) -> None:
        super().__init__(manager, description.key, address)
        self.entity_description = description
        self._attr_entity_registry_enabled_default = description.enabled

    @property
    def native_value(self) -> Any:
        state = self.manager.state(self.address)
        return self.entity_description.value(state, self.manager) if state else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.key == "soc":
            return {"pack": self.manager.card_payload(self.address)}
        if self.key == "problems":
            state = self.manager.state(self.address)
            if state and state.cells:
                return {"problems": state.cells.problems, "info": [a for a in state.cells.alarms if a not in state.cells.problems]}
        if self.key == "weakest_cell":
            w = self.manager.health.weak_cell(self.address)
            return {"share_percent": w["weakest_share"], "first_full_cell": w["first_full"],
                    "first_full_share_percent": w["first_full_share"],
                    "minutes_lowest_per_cell": w["low_minutes"], "minutes_highest_per_cell": w["high_minutes"]}
        return None


class JkCellSensor(JkEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, manager: JkBmsManager, address: int, index: int, *, resistance: bool) -> None:
        key = f"cell_{'resistance' if resistance else 'voltage'}_{index + 1}"
        super().__init__(manager, key, address)
        self.index = index
        self.resistance = resistance
        self._attr_translation_key = "cell_resistance" if resistance else "cell_voltage"
        self._attr_translation_placeholders = {"cell": str(index + 1)}
        if resistance:
            self._attr_native_unit_of_measurement = MOHM
            self._attr_suggested_display_precision = 1
            self._attr_icon = "mdi:omega"
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
            self._attr_entity_registry_enabled_default = False
        else:
            self._attr_device_class = SensorDeviceClass.VOLTAGE
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
            self._attr_suggested_display_precision = 3

    @property
    def native_value(self) -> float | None:
        state = self.manager.state(self.address)
        if not state or not state.cells:
            return None
        values = state.cells.resistances if self.resistance else state.cells.cells
        if self.index >= len(values):
            return None
        return round(values[self.index] * 1000, 1) if self.resistance else values[self.index]


class JkTempSensor(JkEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, manager: JkBmsManager, address: int, index: int) -> None:
        super().__init__(manager, f"temperature_{index + 1}", address)
        self.index = index
        self._attr_translation_key = "temperature"
        self._attr_translation_placeholders = {"sensor": str(index + 1)}
        self._attr_entity_registry_enabled_default = index < 2

    @property
    def available(self) -> bool:
        state = self.manager.state(self.address)
        return super().available and bool(state and state.cells and state.cells.temps[self.index] is not None)

    @property
    def native_value(self) -> float | None:
        state = self.manager.state(self.address)
        return state.cells.temps[self.index] if state and state.cells else None


class JkBankSensor(JkEntity, SensorEntity):
    entity_description: BankSensor
    _unrecorded_attributes = frozenset({"bank"})

    def __init__(self, manager: JkBmsManager, description: BankSensor) -> None:
        super().__init__(manager, description.key, None)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        bank = self.manager.bank()
        if self.entity_description.field == "cell_delta_mv":
            return round(bank["cell_delta"] * 1000) if "cell_delta" in bank else None
        return bank.get(self.entity_description.field)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.key != "bank_soc":
            return None
        bank = self.manager.bank()
        bank["card_version"] = self.manager.version
        bank["mode"] = self.manager.bus.mode
        bank["packs"] = [
            {"address": u.address, "name": u.name, "entity": self.manager.own_entities.get(f"{u.address}:soc")}
            for u in self.manager.units
        ]
        bank["entities"] = {k.split(":", 1)[1]: v for k, v in self.manager.own_entities.items() if k.startswith("bank:")}
        bank["mismatch"] = list(self.manager.settings_mismatch())
        bank["allow_changes"] = self.manager.allow_changes
        return {"bank": bank}
