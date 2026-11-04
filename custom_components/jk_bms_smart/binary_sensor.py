"""Binary sensors per BMS: online, MOS switches, balancing, heating, problems."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JkBmsConfigEntry
from .entity import JkEntity
from .manager import JkBmsManager


@dataclass(frozen=True, kw_only=True)
class JkBinary(BinarySensorEntityDescription):
    value: Callable[[Any], bool | None]
    always_available: bool = False


UNIT_BINARY: tuple[JkBinary, ...] = (
    JkBinary(key="online", device_class=BinarySensorDeviceClass.CONNECTIVITY, entity_category=EntityCategory.DIAGNOSTIC,
             value=lambda c: True, always_available=True),
    JkBinary(key="charging_enabled", icon="mdi:battery-arrow-up", value=lambda c: c.charging_enabled),
    JkBinary(key="discharging_enabled", icon="mdi:battery-arrow-down", value=lambda c: c.discharging_enabled),
    JkBinary(key="balancing", device_class=BinarySensorDeviceClass.RUNNING, icon="mdi:scale-balance",
             value=lambda c: c.balance_state != "off"),
    JkBinary(key="heating", device_class=BinarySensorDeviceClass.HEAT, value=lambda c: c.heating),
    JkBinary(key="charger_plugged", device_class=BinarySensorDeviceClass.PLUG, entity_registry_enabled_default=False,
             value=lambda c: c.charger_plugged),
    JkBinary(key="precharge", entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False,
             value=lambda c: c.precharge),
    JkBinary(key="problem", device_class=BinarySensorDeviceClass.PROBLEM, value=lambda c: bool(c.problems)),
)


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    manager = entry.runtime_data
    entities: list[BinarySensorEntity] = [JkBankProblem(manager)]
    for unit in manager.units:
        entities += [JkUnitBinary(manager, d, unit.address) for d in UNIT_BINARY]
    async_add_entities(entities)


class JkUnitBinary(JkEntity, BinarySensorEntity):
    entity_description: JkBinary

    def __init__(self, manager: JkBmsManager, description: JkBinary, address: int) -> None:
        super().__init__(manager, description.key, address)
        self.entity_description = description

    @property
    def available(self) -> bool:
        return True if self.entity_description.always_available else super().available

    @property
    def is_on(self) -> bool | None:
        if self.key == "online":
            return self.manager.online(self.address)
        state = self.manager.state(self.address)
        if not state or not state.cells:
            return None
        return self.entity_description.value(state.cells)


class JkBankProblem(JkEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, manager: JkBmsManager) -> None:
        super().__init__(manager, "bank_problem", None)

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        # a unit that went silent is a problem too
        bank = self.manager.bank()
        return bool(bank.get("problems")) or bank.get("online", 0) < bank.get("total", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        bank = self.manager.bank()
        return {
            "problems": bank.get("problems", []),
            "offline": [u.name for u in self.manager.units if not self.manager.online(u.address)],
        }
