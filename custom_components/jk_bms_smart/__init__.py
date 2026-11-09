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
from .const import BACKUP_DIR, CARD_BASE, CARD_URL, DOMAIN, VERSION
from .manager import JkBmsManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.UPDATE]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type JkBmsConfigEntry = ConfigEntry[JkBmsManager]

SERVICE_CREATE_DASHBOARD = "create_dashboard"
SERVICE_SET_SETTING = "set_setting"
SERVICE_COPY = "copy_settings"
SERVICE_BACKUP = "backup_settings"
SERVICE_RESTORE = "restore_settings"
SERVICE_RESET_HEALTH = "reset_cell_statistics"
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

    def _resolve(entity_id: str) -> tuple[JkBmsManager, int | None]:
        """Entity of a pack → (manager, address); entity of the bank → (manager, None)."""
        from homeassistant.helpers import entity_registry as er

        ent = er.async_get(hass).async_get(entity_id)
        if ent is None or ent.platform != DOMAIN:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_bus")
        entry = hass.config_entries.async_get_entry(ent.config_entry_id)
        if entry is None or not hasattr(entry, "runtime_data"):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_bus")
        rest = ent.unique_id[len(entry.entry_id) + 1 :]
        return entry.runtime_data, None if rest.startswith("bank_") else int(rest.split("_", 1)[0])

    async def _set_setting(call: ServiceCall) -> ServiceResponse:
        """Used by the settings card: one setting on one pack, or on every pack of the bank."""
        from .protocol import WRITABLE

        manager, address = _resolve(call.data["entity_id"])
        key = call.data["key"]
        if key not in WRITABLE:
            raise ServiceValidationError(f"Unknown setting {key}")
        targets = [u.address for u in manager.units] if call.data.get("all_packs") or address is None else [address]
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

    async def _copy_settings(call: ServiceCall) -> ServiceResponse:
        """Make other packs equal to one pack (dry_run = only show what would change)."""
        manager, source = _resolve(call.data["source"])
        if source is None:
            raise ServiceValidationError("Choose an entity of the pack to copy from")
        wanted = manager.settings_of(source)
        if wanted is None:
            raise HomeAssistantError(f"{manager.unit_name(source)}: settings not received yet")
        targets = [u.address for u in manager.units if u.address != source]
        if call.data.get("targets"):
            targets = [a for a in (_resolve(e)[1] for e in call.data["targets"]) if a is not None and a != source]
        keys = call.data.get("keys") or None
        if keys is None:
            from .protocol import COMPARE_KEYS

            keys = list(COMPARE_KEYS) + (["design_capacity_ah"] if call.data.get("include_capacity") else [])
        results = [await manager.async_apply(a, wanted, keys, dry_run=call.data.get("dry_run", False)) for a in targets]
        return {"source": manager.unit_name(source), "results": results}

    async def _backup_settings(call: ServiceCall) -> ServiceResponse:
        manager, address = _resolve(call.data["entity_id"])
        targets = [u.address for u in manager.units] if address is None else [address]
        files, failed = [], {}
        for a in targets:
            try:
                files.append(await manager.async_backup(a))
            except HomeAssistantError as err:
                failed[manager.unit_name(a)] = str(err)
        if failed and not files:
            raise HomeAssistantError("; ".join(f"{k}: {v}" for k, v in failed.items()))
        return {"files": files, "failed": failed, "folder": BACKUP_DIR}

    async def _restore_settings(call: ServiceCall) -> ServiceResponse:
        manager, address = _resolve(call.data["entity_id"])
        doc = await manager.async_read_backup(call.data["file"])
        if address is None:
            address = doc.get("address")
            if address not in {u.address for u in manager.units}:
                raise ServiceValidationError("Choose the pack to restore to")
        keys = None if call.data.get("include_switches") else [k for k in doc["settings"] if not k.endswith("_switch")]
        return await manager.async_apply(address, doc["settings"], keys, dry_run=call.data.get("dry_run", False))

    async def _reset_health(call: ServiceCall) -> None:
        manager, address = _resolve(call.data["entity_id"])
        for a in [u.address for u in manager.units] if address is None else [address]:
            manager.health.reset(a)
        manager._flush()  # noqa: SLF001

    entity_schema = vol.Schema({vol.Required("entity_id"): cv.entity_id})
    for name, handler, schema, response in (
        (SERVICE_COPY, _copy_settings, vol.Schema({
            vol.Required("source"): cv.entity_id,
            vol.Optional("targets"): vol.All(cv.ensure_list, [cv.entity_id]),
            vol.Optional("keys"): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional("include_capacity", default=False): cv.boolean,
            vol.Optional("dry_run", default=False): cv.boolean,
        }), SupportsResponse.OPTIONAL),
        (SERVICE_BACKUP, _backup_settings, entity_schema, SupportsResponse.OPTIONAL),
        (SERVICE_RESTORE, _restore_settings, vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("file"): cv.string,
            vol.Optional("include_switches", default=False): cv.boolean,
            vol.Optional("dry_run", default=False): cv.boolean,
        }), SupportsResponse.OPTIONAL),
        (SERVICE_RESET_HEALTH, _reset_health, entity_schema, SupportsResponse.NONE),
    ):
        async_register_admin_service(hass, DOMAIN, name, handler, schema=schema, supports_response=response)

    from .websocket import async_register_websocket

    async_register_websocket(hass)

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
