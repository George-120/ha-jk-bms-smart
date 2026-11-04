"""Diagnostics: bus health per BMS, without anything private."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import JkBmsConfigEntry


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: JkBmsConfigEntry) -> dict[str, Any]:
    manager = entry.runtime_data
    conn = dict(entry.data.get("connection", {}))
    if "host" in conn:
        conn["host"] = "**redacted**"
    return {
        "connection": conn,
        "units": entry.data.get("units"),
        "options": dict(entry.options),
        "bus": manager.bus.diagnostics(),
        "bank": manager.bank(),
        "packs": {u.address: {k: v for k, v in manager.card_payload(u.address).items() if k != "entities"} for u in manager.units},
    }
