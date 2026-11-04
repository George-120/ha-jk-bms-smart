"""Charge / discharge / balance switches per BMS (only when changes are switched on)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JkBmsConfigEntry
from .entity import JkEntity
from .manager import JkBmsManager

SWITCHES = {
    "charge_switch": "mdi:battery-arrow-up",
    "discharge_switch": "mdi:battery-arrow-down",
    "balance_switch": "mdi:scale-balance",
}


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    manager = entry.runtime_data
    if not manager.allow_changes:
        return
    async_add_entities(JkSwitch(manager, unit.address, key, icon) for unit in manager.units for key, icon in SWITCHES.items())


class JkSwitch(JkEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager: JkBmsManager, address: int, key: str, icon: str) -> None:
        super().__init__(manager, key, address)
        self._attr_icon = icon

    @property
    def available(self) -> bool:
        state = self.manager.state(self.address)
        return super().available and bool(state and state.settings)

    @property
    def is_on(self) -> bool | None:
        state = self.manager.state(self.address)
        return getattr(state.settings, self.key) if state and state.settings else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.manager.async_write(self.address, self.key, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.manager.async_write(self.address, self.key, 0)
