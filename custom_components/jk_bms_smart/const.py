"""Constants for JK BMS Smart."""

from __future__ import annotations

DOMAIN = "jk_bms_smart"
NAME = "JK BMS Smart"
VERSION = "1.2.0"

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

# notifications (1.2)
OPT_NOTIFY_TARGETS = "notify_targets"  # notify services, e.g. ["mobile_app_iphone"]
OPT_NOTIFY_PERSISTENT = "notify_persistent"  # also show in the HA notifications panel
OPT_NOTIFY_EVENTS = "notify_events"
OPT_NOTIFY_RESOLVED = "notify_resolved"
OPT_DELTA_MV = "alert_delta_mv"
OPT_TEMP_HIGH = "alert_temp_high"
OPT_TEMP_LOW = "alert_temp_low"
OPT_SOC_LOW = "alert_soc_low"
NOTIFY_EVENTS = ("offline", "alarm", "delta", "temp", "soc_low", "mismatch")
DEFAULT_NOTIFY_EVENTS = ["offline", "alarm", "delta", "temp", "mismatch"]
DEFAULT_DELTA_MV = 50
DEFAULT_TEMP_HIGH = 50
DEFAULT_TEMP_LOW = 3
DEFAULT_SOC_LOW = 10

BACKUP_DIR = "jk_bms_smart/backups"  # under the HA config folder

DEFAULT_POLL_INTERVAL = 5
DEFAULT_STALE_AFTER = 60

SIGNAL_UPDATE = f"{DOMAIN}_update_{{}}"

# USB-RS485 adapters people use with JK BMS units (shown first in the port list).
RS485_HINTS = ("rs485", "rs-485", "ft232", "ftdi", "ch340", "ch341", "cp210", "pl2303", "usb-serial", "usb serial", "uart")
