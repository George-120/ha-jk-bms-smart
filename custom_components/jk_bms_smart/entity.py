"""Base entities: one device per BMS plus one 'battery bank' device."""

from __future__ import annotations

import inspect

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, VERSION
from .manager import JkBmsManager

# Home Assistant 2026.8+ links devices with via_device_id; older versions use via_device.
_VIA_DEVICE_ID = "via_device_id" in inspect.signature(dr.DeviceRegistry.async_get_or_create).parameters


def bank_identifier(manager: JkBmsManager) -> tuple[str, str]:
    return (DOMAIN, f"{manager.entry.entry_id}_bank")


def unit_identifier(manager: JkBmsManager, address: int) -> tuple[str, str]:
    return (DOMAIN, f"{manager.entry.entry_id}_{address}")


def bank_device(manager: JkBmsManager) -> DeviceInfo:
    return DeviceInfo(
        identifiers={bank_identifier(manager)},
        name=manager.entry.title,
        manufacturer="JK BMS Smart (community)",
        model=f"Battery bank · {len(manager.units)} × JK BMS",
        sw_version=VERSION,
    )


def unit_device(manager: JkBmsManager, address: int) -> DeviceInfo:
    info = DeviceInfo(
        identifiers={unit_identifier(manager, address)},
        name=manager.unit_name(address),
        manufacturer="JK BMS (Jikong)",
        model="JK inverter BMS",
        hw_version=f"RS485 address {address}",
    )
    if not _VIA_DEVICE_ID:
        info["via_device"] = bank_identifier(manager)
    return info


class JkEntity(Entity):
    """Common bits: naming, availability, update signal."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager: JkBmsManager, key: str, address: int | None) -> None:
        self.manager = manager
        self.key = key
        self.address = address
        self._attr_translation_key = key.rstrip("0123456789_") if key.startswith(("cell_voltage_", "cell_resistance_", "temperature_")) else key
        if address is None:
            self._attr_unique_id = f"{manager.entry.entry_id}_bank_{key}"
            self._attr_device_info = bank_device(manager)
        else:
            self._attr_unique_id = f"{manager.entry.entry_id}_{address}_{key}"
            self._attr_device_info = unit_device(manager, address)

    @property
    def own_key(self) -> str:
        return f"{'bank' if self.address is None else self.address}:{self.key}"

    @property
    def available(self) -> bool:
        if self.address is None:
            return any(self.manager.online(u.address) for u in self.manager.units)
        return self.manager.online(self.address)

    async def async_added_to_hass(self) -> None:
        self.manager.own_entities[self.own_key] = self.entity_id
        self.async_on_remove(async_dispatcher_connect(self.hass, self.manager.signal, self._handle_update))
        if _VIA_DEVICE_ID and self.address is not None and self.registry_entry and self.registry_entry.device_id:
            reg = dr.async_get(self.hass)
            parent = reg.async_get_device(identifiers={bank_identifier(self.manager)})
            dev = reg.async_get(self.registry_entry.device_id)
            if parent and dev and dev.via_device_id != parent.id:
                reg.async_update_device(dev.id, via_device_id=parent.id)

    @callback
    def _handle_update(self) -> None:
        self._sync_device_info()
        self.async_write_ha_state()

    _info_applied = False

    @callback
    def _sync_device_info(self) -> None:
        """Once the BMS told us its model/firmware/serial, put it on the device."""
        if self._info_applied or self.address is None or not self.registry_entry or not self.registry_entry.device_id:
            return
        state = self.manager.state(self.address)
        if not state or not state.info:
            return
        self._info_applied = True
        info = state.info
        reg = dr.async_get(self.hass)
        dev = reg.async_get(self.registry_entry.device_id)
        if dev is None:
            return
        changes = {}
        if info.model and dev.model != info.model:
            changes["model"] = info.model
        if info.software and dev.sw_version != info.software:
            changes["sw_version"] = info.software
        if info.hardware and dev.hw_version != f"{info.hardware} · RS485 {self.address}":
            changes["hw_version"] = f"{info.hardware} · RS485 {self.address}"
        if info.serial and getattr(dev, "serial_number", None) != info.serial:
            changes["serial_number"] = info.serial
        if changes:
            reg.async_update_device(dev.id, **changes)
