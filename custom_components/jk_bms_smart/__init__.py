"""JK BMS Smart: JK inverter BMS units over RS485 (USB or network), with battery-pack cards."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType

from .bus import BusError, PortBusy
from .const import CARD_BASE, CARD_URL, DOMAIN, VERSION
from .manager import JkBmsManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type JkBmsConfigEntry = ConfigEntry[JkBmsManager]

SERVICE_CREATE_DASHBOARD = "create_dashboard"
SERVICE_SET_SETTING = "set_setting"
ATTR_CONFIG_ENTRY = "config_entry_id"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the cards and register the admin action once."""
    folder = Path(__file__).parent / "frontend"
    try:
        await hass.http.async_register_static_paths([StaticPathConfig(CARD_BASE, str(folder), cache_headers=False)])
    except RuntimeError:
        pass  # already registered (reload)
    from homeassistant.components.frontend import add_extra_js_url

    add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")

    async def _create_dashboard(call: ServiceCall) -> ServiceResponse:
        from .dashboard import async_create_dashboard

        entry_id = call.data.get(ATTR_CONFIG_ENTRY)
        entries = [e for e in hass.config_entries.async_loaded_entries(DOMAIN) if entry_id in (None, e.entry_id)]
        if not entries:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_bus")
        try:
            url = await async_create_dashboard(entries[0].runtime_data)
        except HomeAssistantError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="dashboard_failed", translation_placeholders={"error": str(err)}
            ) from err
        return {"url_path": url}

    async def _set_setting(call: ServiceCall) -> ServiceResponse:
        """Used by the settings card: one setting on one pack, or on every pack of the bank."""
        from homeassistant.helpers import entity_registry as er

        from .protocol import WRITABLE

        reg = er.async_get(hass)
        ent = reg.async_get(call.data["entity_id"])
        if ent is None or ent.platform != DOMAIN:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_bus")
        entry = hass.config_entries.async_get_entry(ent.config_entry_id)
        if entry is None or not hasattr(entry, "runtime_data"):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_bus")
        manager = entry.runtime_data
        key = call.data["key"]
        if key not in WRITABLE:
            raise ServiceValidationError(f"Unknown setting {key}")
        rest = ent.unique_id[len(entry.entry_id) + 1 :]
        targets = [u.address for u in manager.units] if call.data.get("all_packs") or rest.startswith("bank_") else [int(rest.split("_", 1)[0])]
        done, failed = [], {}
        for address in targets:
            try:
                await manager.async_write(address, key, call.data["value"])
                done.append(manager.unit_name(address))
            except HomeAssistantError as err:
                failed[manager.unit_name(address)] = str(err)
        if failed and not done:
            raise HomeAssistantError("; ".join(f"{k}: {v}" for k, v in failed.items()))
        return {"done": done, "failed": failed}

    # Changes battery protection settings, so admins only.
    async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_SET_SETTING,
        _set_setting,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("key"): cv.string,
                vol.Required("value"): vol.Coerce(float),
                vol.Optional("all_packs", default=False): cv.boolean,
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )

    async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_CREATE_DASHBOARD,
        _create_dashboard,
        schema=vol.Schema({vol.Optional(ATTR_CONFIG_ENTRY): cv.string}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: JkBmsConfigEntry) -> bool:
    manager = JkBmsManager(hass, entry)
    try:
        await manager.async_setup()
    except PortBusy as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="port_busy", translation_placeholders={"error": str(err)}
        ) from err
    except BusError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="port_error", translation_placeholders={"error": str(err)}
        ) from err
    entry.runtime_data = manager
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: JkBmsConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: JkBmsConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_unload()
    return unloaded
