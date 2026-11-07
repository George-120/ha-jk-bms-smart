"""Constants for JK BMS Smart."""

from __future__ import annotations

DOMAIN = "jk_bms_smart"
NAME = "JK BMS Smart"
VERSION = "1.1.1"

CARD_BASE = f"/{DOMAIN}"
CARD_URL = f"{CARD_BASE}/jk-bms-smart-card.js"

CONF_CONNECTION = "connection"
CONF_DEVICE = "device"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_UNITS = "units"  # list of {"address": int, "name": str}
CONF_MODE = "mode"  # detected mode at setup (informational)

OPT_POLL_INTERVAL = "poll_interval"
OPT_STALE_AFTER = "stale_after"
OPT_LANGUAGE = "language"
OPT_CELL_RESISTANCE = "cell_resistance"
OPT_ALLOW_CHANGES = "allow_changes"

DEFAULT_POLL_INTERVAL = 5
DEFAULT_STALE_AFTER = 60

SIGNAL_UPDATE = f"{DOMAIN}_update_{{}}"

# USB-RS485 adapters people use with JK BMS units (shown first in the port list).
RS485_HINTS = ("rs485", "rs-485", "ft232", "ftdi", "ch340", "ch341", "cp210", "pl2303", "usb-serial", "usb serial", "uart")
