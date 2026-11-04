"""Protection and balancer settings per BMS as number entities (only when changes are switched on)."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JkBmsConfigEntry
from .entity import JkEntity
from .manager import JkBmsManager
from .protocol import WRITABLE

V = (NumberDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 0.001)
A = (NumberDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 0.1)
T = (NumberDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 1)

NUMBERS: dict[str, tuple] = {
    "cell_ovp": V, "cell_ovpr": V, "cell_uvp": V, "cell_uvpr": V,
    "charge_voltage": V, "float_voltage": V, "soc100_voltage": V, "soc0_voltage": V,
    "power_off_voltage": V, "balance_start": V, "balance_trigger": V,
    "max_balance_current": A, "max_charge_current": A, "max_discharge_current": A,
    "design_capacity_ah": (None, "Ah", 1),
    "charge_ot": T, "discharge_ot": T, "charge_ut": T, "mos_ot": T,
}


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    manager = entry.runtime_data
    if not manager.allow_changes:
        return
    async_add_entities(JkNumber(manager, unit.address, key) for unit in manager.units for key in NUMBERS)


class JkNumber(JkEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX

    def __init__(self, manager: JkBmsManager, address: int, key: str) -> None:
        super().__init__(manager, f"set_{key}", address)
        self.setting = key
        device_class, unit, step = NUMBERS[key]
        w = WRITABLE[key]
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_native_step = step
        self._attr_native_min_value = w.minimum
        self._attr_native_max_value = w.maximum

    @property
    def available(self) -> bool:
        state = self.manager.state(self.address)
        return super().available and bool(state and state.settings)

    @property
    def native_value(self) -> float | None:
        state = self.manager.state(self.address)
        return getattr(state.settings, self.setting) if state and state.settings else None

    async def async_set_native_value(self, value: float) -> None:
        await self.manager.async_write(self.address, self.setting, value)
