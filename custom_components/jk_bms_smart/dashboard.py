"""Ready-made dashboard, created with one button press (Configure → Create dashboard).

Same approach as Easee Smart Charging: Home Assistant has no public Python API to add a
storage dashboard, so we use the collection behind the lovelace/dashboards websocket commands.
A dashboard we did not create is never overwritten.
"""

from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CARD_BASE, DOMAIN

if TYPE_CHECKING:
    from .manager import JkBmsManager

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL = "jk-bms"
DASHBOARD_ICON = "mdi:battery-high"
STORE_KEY = f"{DOMAIN}.dashboards"

TEXT = {
    "nl": {"title": "Thuisaccu", "packs": "Accupakketten", "bank": "Accubank", "cells": "Cellen", "sub": "JK BMS via RS485",
           "settings": "Instellingen", "charts": "Grafieken", "b_soc": "Lading", "b_power": "Vermogen", "b_energy": "Opgeslagen", "b_delta": "Celverschil"},
    "en": {"title": "Home battery", "packs": "Battery packs", "bank": "Battery bank", "cells": "Cells", "sub": "JK BMS over RS485",
           "settings": "Settings", "charts": "Charts", "b_soc": "Charge", "b_power": "Power", "b_energy": "Stored", "b_delta": "Cell delta"},
    "de": {"title": "Heimspeicher", "packs": "Akkupacks", "bank": "Akkubank", "cells": "Zellen", "sub": "JK BMS über RS485",
           "settings": "Einstellungen", "charts": "Diagramme", "b_soc": "Ladung", "b_power": "Leistung", "b_energy": "Gespeichert", "b_delta": "Zelldifferenz"},
}


def _lang(hass: HomeAssistant) -> str:
    lang = (hass.config.language or "en").split("-")[0]
    return lang if lang in TEXT else "en"


def build_dashboard(manager: JkBmsManager) -> dict[str, Any]:
    t = TEXT[_lang(manager.hass)]
    own = manager.own_entities
    bank = own.get("bank:bank_soc")
    if not bank:
        raise HomeAssistantError("JK BMS Smart sensors are not ready yet")

    def heading(text: str, icon: str) -> dict[str, Any]:
        return {"type": "heading", "heading": text, "icon": icon, "heading_style": "title"}

    def badge(key: str, name: str) -> dict[str, Any] | None:
        eid = own.get(f"bank:{key}")
        return {"type": "entity", "entity": eid, "name": name, "show_name": True, "show_state": True, "show_icon": True} if eid else None

    badges = [b for b in (badge("bank_soc", t["b_soc"]), badge("bank_power", t["b_power"]),
                          badge("bank_stored_energy", t["b_energy"]), badge("bank_cell_delta", t["b_delta"])) if b]
    header = {
        "layout": "responsive",
        "badges_position": "bottom",
        "card": {"type": "markdown", "text_only": True,
                 "content": f'# <img src="{CARD_BASE}/logo.png" width="44" height="44" alt=""> JK BMS Smart\n{manager.entry.title} — {t["sub"]}'},
    }
    packs = []
    for unit in manager.units:
        eid = own.get(f"{unit.address}:soc")
        if eid:
            packs.append({"type": "grid", "cards": [heading(unit.name, "mdi:battery"), {"type": "custom:jk-bms-smart-pack-card", "entity": eid}]})
    return {
        "title": t["title"],
        "views": [
            {"title": t["packs"], "path": "accu", "icon": "mdi:battery-high", "type": "sections", "max_columns": 3,
             "dense_section_placement": True, "header": header, "badges": badges,
             "sections": [{"type": "grid", "column_span": 3, "cards": [heading(t["bank"], "mdi:home-battery"),
                                                                       {"type": "custom:jk-bms-smart-bank-card", "entity": bank}]},
                          *packs]},
            {"title": t["cells"], "path": "cellen", "icon": "mdi:view-grid-outline", "type": "sections", "max_columns": 3,
             "header": header,
             "sections": [{"type": "grid", "cards": [heading(s["cards"][0]["heading"], "mdi:battery"),
                                                     {**s["cards"][1], "tab": "cells", "size": "large"}]} for s in packs]},
            {"title": t["charts"], "path": "grafieken", "icon": "mdi:chart-line", "type": "sections", "max_columns": 3,
             "header": header,
             "sections": [{"type": "grid", "column_span": 3, "cards": [heading(t["bank"], "mdi:home-battery"),
                                                                       {"type": "custom:jk-bms-smart-chart-card", "entity": bank, "chart": "power"}]},
                          *[{"type": "grid", "cards": [heading(s["cards"][0]["heading"], "mdi:battery"),
                                                       {"type": "custom:jk-bms-smart-chart-card", "entity": s["cards"][1]["entity"], "chart": "cells"}]}
                            for s in packs]]},
            {"title": t["settings"], "path": "instellingen", "icon": "mdi:tune-variant", "type": "sections", "max_columns": 2,
             "header": header,
             "sections": [{"type": "grid", "cards": [heading(t["settings"], "mdi:tune-variant"),
                                                     {"type": "custom:jk-bms-smart-settings-card", "entity": bank}]}]},
        ],
    }


def _dashboards_collection(hass: HomeAssistant):
    from homeassistant.components import websocket_api

    handlers = hass.data.get(websocket_api.DOMAIN) or {}
    entry = handlers.get("lovelace/dashboards/create")
    if not entry:
        return None
    owner = getattr(inspect.unwrap(entry[0]), "__self__", None)
    return getattr(owner, "storage_collection", None)


async def async_create_dashboard(manager: JkBmsManager) -> str:
    """Create our dashboard, or refresh the one this integration made earlier."""
    from homeassistant.components.frontend import async_panel_exists
    from homeassistant.components.lovelace.const import LOVELACE_DATA
    from homeassistant.helpers.storage import Store

    hass = manager.hass
    data = hass.data.get(LOVELACE_DATA)
    if data is None:
        raise HomeAssistantError("Lovelace is not loaded")
    config = build_dashboard(manager)
    entry_id = manager.entry.entry_id
    store: Store = Store(hass, 1, STORE_KEY)
    owned: dict[str, str] = ((await store.async_load()) or {}).get("owned", {})

    url = owned.get(entry_id)
    if not (url and url in data.dashboards):
        base = DASHBOARD_URL if len(hass.config_entries.async_entries(DOMAIN)) <= 1 else f"{DASHBOARD_URL}-{entry_id[:6]}".lower()
        url, n = base, 2
        while url in data.dashboards or async_panel_exists(hass, url):
            url = f"{base}-{n}"
            n += 1
        coll = _dashboards_collection(hass)
        if coll is None:
            raise HomeAssistantError("Could not reach the dashboards collection")
        try:
            await coll.async_create_item({"url_path": url, "title": config["title"], "icon": DASHBOARD_ICON,
                                          "show_in_sidebar": True, "require_admin": False, "mode": "storage"})
        except HomeAssistantError:
            raise
        except Exception as err:  # vol.Invalid etc.
            raise HomeAssistantError(str(err)) from err
        owned[entry_id] = url
        await store.async_save({"owned": owned})
    target = data.dashboards.get(url)
    if target is None:
        raise HomeAssistantError("Dashboard was not registered")
    await target.async_save(config)
    _LOGGER.info("JK BMS Smart dashboard written to /%s", url)
    return url
