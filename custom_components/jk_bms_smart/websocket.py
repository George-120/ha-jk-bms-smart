"""Websocket commands for the cards: pack health history and the list of settings backups."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN


def _resolve(hass: HomeAssistant, entity_id: str):  # noqa: ANN202
    ent = er.async_get(hass).async_get(entity_id)
    if ent is None or ent.platform != DOMAIN:
        return None, None
    entry = hass.config_entries.async_get_entry(ent.config_entry_id)
    manager = getattr(entry, "runtime_data", None) if entry else None
    if manager is None:
        return None, None
    rest = ent.unique_id[len(entry.entry_id) + 1 :]
    return manager, None if rest.startswith("bank_") else int(rest.split("_", 1)[0])


@callback
def async_register_websocket(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_health)
    websocket_api.async_register_command(hass, ws_backups)


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/health", vol.Required("entity_id"): str, vol.Optional("days", default=90): vol.All(int, vol.Range(1, 400))}
)
@callback
def ws_health(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    manager, address = _resolve(hass, msg["entity_id"])
    if manager is None:
        connection.send_error(msg["id"], "not_found", "Not a JK BMS Smart entity")
        return
    units = [u for u in manager.units if address is None or u.address == address]
    connection.send_result(msg["id"], {"packs": [
        {"address": u.address, "name": u.name, "entity": manager.own_entities.get(f"{u.address}:soc"),
         "weak": manager.health.weak_cell(u.address), "days": manager.health.history(u.address, msg["days"])}
        for u in units
    ]})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/backups", vol.Required("entity_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backups(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    manager, _address = _resolve(hass, msg["entity_id"])
    if manager is None:
        connection.send_error(msg["id"], "not_found", "Not a JK BMS Smart entity")
        return
    connection.send_result(msg["id"], {"backups": await manager.async_list_backups()})
