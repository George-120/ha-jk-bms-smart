"""Newest known JK PB firmware per model.

JK has no public update API, so the integration keeps a small list (firmware.json) in its
GitHub repository and checks it once a day; the copy shipped with the integration is the
fallback. The BMS itself is flashed with JK's PC tool, never by Home Assistant.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

URL = "https://raw.githubusercontent.com/George-120/ha-jk-bms-smart/main/firmware.json"
BUNDLED = Path(__file__).parent / "firmware.json"


def model_key(model: str | None) -> str:
    """'JK_PB2A16S30P' / 'JK-PB2A16S-30P' -> 'JKPB2A16S30P'."""
    return re.sub(r"[^A-Z0-9]", "", (model or "").upper())


def parse(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {model_key(k): v for k, v in (doc.get("models") or {}).items() if isinstance(v, dict) and v.get("latest")}


async def async_load(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    try:
        session = async_get_clientsession(hass)
        async with session.get(URL, timeout=15) as resp:
            resp.raise_for_status()
            table = parse(json.loads(await resp.text()))
            if table:
                return table
    except Exception as err:  # noqa: BLE001 - offline is fine, use the bundled list
        _LOGGER.debug("Firmware list not reachable (%s), using the bundled one", err)
    text = await hass.async_add_executor_job(BUNDLED.read_text, "utf-8")
    return parse(json.loads(text))


def newer(installed: str | None, latest: str | None) -> bool:
    def nums(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in re.findall(r"\d+", v))

    if not installed or not latest:
        return False
    try:
        return nums(latest) > nums(installed)
    except ValueError:
        return False
