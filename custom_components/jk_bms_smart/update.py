"""Firmware update entity per BMS: shows when JK has a newer firmware than the pack runs.

Home Assistant cannot install it (JK firmware is flashed with JK's PC tool), so the entity
only informs and links to the download page.
"""

from __future__ import annotations

from homeassistant.components.update import UpdateDeviceClass, UpdateEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JkBmsConfigEntry
from .entity import JkEntity
from .manager import JkBmsManager

SUMMARY = {
    "nl": "JK-firmware {latest} ({date}) is nieuwer dan {installed} in dit pakket. Bijwerken gaat met de JK PC-software en een USB-RS485-adapter, niet vanuit Home Assistant. Controleer eerst bij JK of deze versie bij hardware {hw} hoort, maak een back-up van de instellingen en haal tijdens het bijwerken de stroom of de kabel er niet af.",
    "de": "JK-Firmware {latest} ({date}) ist neuer als {installed} in diesem Pack. Das Update erfolgt mit der JK-PC-Software und einem USB-RS485-Adapter, nicht aus Home Assistant. Vorher bei JK prüfen, ob die Version zu Hardware {hw} passt, Einstellungen sichern und während des Updates Strom und Kabel nicht trennen.",
    "en": "JK firmware {latest} ({date}) is newer than {installed} in this pack. Updating is done with JK's PC software and a USB-RS485 adapter, not from Home Assistant. Check with JK first that this version fits hardware {hw}, back up the settings and do not cut power or the cable while updating.",
}


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    manager = entry.runtime_data
    async_add_entities(JkFirmwareUpdate(manager, unit.address) for unit in manager.units)


class JkFirmwareUpdate(JkEntity, UpdateEntity):
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, manager: JkBmsManager, address: int) -> None:
        super().__init__(manager, "firmware", address)

    @property
    def available(self) -> bool:
        state = self.manager.state(self.address)
        return bool(state and state.info and state.info.software)

    @property
    def installed_version(self) -> str | None:
        state = self.manager.state(self.address)
        return state.info.software if state and state.info else None

    @property
    def latest_version(self) -> str | None:
        fw = self.manager.firmware_for(self.address)
        return fw["latest"] if fw else None

    @property
    def title(self) -> str | None:
        state = self.manager.state(self.address)
        return f"{state.info.model} firmware" if state and state.info else "JK BMS firmware"

    @property
    def release_url(self) -> str | None:
        fw = self.manager.firmware_for(self.address)
        return fw.get("url") if fw else None

    @property
    def release_summary(self) -> str | None:
        fw = self.manager.firmware_for(self.address)
        state = self.manager.state(self.address)
        if not fw or not state or not state.info:
            return None
        lang = (self.hass.config.language or "en").split("-")[0]
        text = SUMMARY.get(lang, SUMMARY["en"])
        return text.format(latest=fw["latest"], date=fw.get("date", ""), installed=state.info.software, hw=state.info.hardware or "?")[:255]
