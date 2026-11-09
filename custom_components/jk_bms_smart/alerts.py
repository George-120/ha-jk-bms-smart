"""Notifications (phone / HA panel) and Repairs issues.

Every condition has a hold time (it must last that long before anyone is told) and a
hysteresis (it must clearly be gone before "resolved" is sent), so a short balancing
spike or one missed frame never wakes anybody up.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import (
    DEFAULT_DELTA_MV,
    DEFAULT_NOTIFY_EVENTS,
    DEFAULT_SOC_LOW,
    DEFAULT_TEMP_HIGH,
    DEFAULT_TEMP_LOW,
    DOMAIN,
    OPT_DELTA_MV,
    OPT_NOTIFY_EVENTS,
    OPT_NOTIFY_PERSISTENT,
    OPT_NOTIFY_RESOLVED,
    OPT_NOTIFY_TARGETS,
    OPT_SOC_LOW,
    OPT_TEMP_HIGH,
    OPT_TEMP_LOW,
)

if TYPE_CHECKING:
    from .manager import JkBmsManager

_LOGGER = logging.getLogger(__name__)

STARTUP_GRACE_S = 120
EVAL_EVERY_S = 10
OFFLINE_REPAIR_S = 600
PORT_REPAIR_S = 120

TEXT = {
    "en": {
        "offline": ("{pack} is offline", "No data from {pack} for a while. Check the RS485 cable and that the pack is switched on."),
        "offline_ok": ("{pack} is back online", "{pack} sends data again."),
        "port": ("RS485 connection lost", "The USB-RS485 adapter or gateway does not answer: {error}"),
        "port_ok": ("RS485 connection restored", "JK BMS Smart reads the BMS units again."),
        "alarm": ("{pack}: {alarm}", "The BMS reports “{alarm}”. It may have switched charging or discharging off."),
        "alarm_ok": ("{pack}: alarm gone", "“{alarm}” is no longer reported."),
        "delta": ("{pack}: cells drift apart", "Cell difference {value} mV (limit {limit} mV) for more than 5 minutes. Lowest cell {low}, highest {high}."),
        "delta_ok": ("{pack}: cells back in line", "Cell difference is {value} mV again."),
        "temp_high": ("{pack} is warm", "Temperature {value} °C (limit {limit} °C)."),
        "temp_high_ok": ("{pack}: temperature normal", "Temperature {value} °C."),
        "temp_low": ("{pack} is cold", "Temperature {value} °C (limit {limit} °C). Charging may be blocked."),
        "temp_low_ok": ("{pack}: temperature normal", "Temperature {value} °C."),
        "soc_low": ("Battery almost empty", "Battery bank at {value} % (limit {limit} %)."),
        "soc_low_ok": ("Battery charging again", "Battery bank at {value} %."),
        "mismatch": ("Packs have different settings", "These settings differ between the packs: {keys}. Use the settings card to make them equal."),
        "mismatch_ok": ("Pack settings equal again", "All packs have the same settings."),
    },
    "nl": {
        "offline": ("{pack} is offline", "Al een tijd geen gegevens van {pack}. Controleer de RS485-kabel en of het pakket aan staat."),
        "offline_ok": ("{pack} is weer online", "{pack} stuurt weer gegevens."),
        "port": ("RS485-verbinding weg", "De USB-RS485-adapter of gateway antwoordt niet: {error}"),
        "port_ok": ("RS485-verbinding hersteld", "JK BMS Smart leest de BMS'en weer uit."),
        "alarm": ("{pack}: {alarm}", "De BMS meldt “{alarm}”. Mogelijk is laden of ontladen uitgeschakeld."),
        "alarm_ok": ("{pack}: alarm voorbij", "“{alarm}” wordt niet meer gemeld."),
        "delta": ("{pack}: cellen lopen uit elkaar", "Celverschil {value} mV (grens {limit} mV), al langer dan 5 minuten. Laagste cel {low}, hoogste {high}."),
        "delta_ok": ("{pack}: cellen weer gelijk", "Celverschil is weer {value} mV."),
        "temp_high": ("{pack} is warm", "Temperatuur {value} °C (grens {limit} °C)."),
        "temp_high_ok": ("{pack}: temperatuur normaal", "Temperatuur {value} °C."),
        "temp_low": ("{pack} is koud", "Temperatuur {value} °C (grens {limit} °C). Laden kan geblokkeerd zijn."),
        "temp_low_ok": ("{pack}: temperatuur normaal", "Temperatuur {value} °C."),
        "soc_low": ("Accu bijna leeg", "Accubank op {value} % (grens {limit} %)."),
        "soc_low_ok": ("Accu laadt weer", "Accubank op {value} %."),
        "mismatch": ("Pakketten hebben andere instellingen", "Deze instellingen verschillen tussen de pakketten: {keys}. Trek ze gelijk via de instellingenkaart."),
        "mismatch_ok": ("Instellingen weer gelijk", "Alle pakketten hebben weer dezelfde instellingen."),
    },
    "de": {
        "offline": ("{pack} ist offline", "Seit einiger Zeit keine Daten von {pack}. Prüfe das RS485-Kabel und ob das Pack eingeschaltet ist."),
        "offline_ok": ("{pack} ist wieder online", "{pack} sendet wieder Daten."),
        "port": ("RS485-Verbindung verloren", "Der USB-RS485-Adapter oder das Gateway antwortet nicht: {error}"),
        "port_ok": ("RS485-Verbindung wiederhergestellt", "JK BMS Smart liest die BMS wieder aus."),
        "alarm": ("{pack}: {alarm}", "Das BMS meldet „{alarm}“. Laden oder Entladen ist eventuell abgeschaltet."),
        "alarm_ok": ("{pack}: Alarm vorbei", "„{alarm}“ wird nicht mehr gemeldet."),
        "delta": ("{pack}: Zellen driften auseinander", "Zelldifferenz {value} mV (Grenze {limit} mV) seit über 5 Minuten. Niedrigste Zelle {low}, höchste {high}."),
        "delta_ok": ("{pack}: Zellen wieder gleich", "Zelldifferenz wieder {value} mV."),
        "temp_high": ("{pack} ist warm", "Temperatur {value} °C (Grenze {limit} °C)."),
        "temp_high_ok": ("{pack}: Temperatur normal", "Temperatur {value} °C."),
        "temp_low": ("{pack} ist kalt", "Temperatur {value} °C (Grenze {limit} °C). Laden kann gesperrt sein."),
        "temp_low_ok": ("{pack}: Temperatur normal", "Temperatur {value} °C."),
        "soc_low": ("Akku fast leer", "Akkubank bei {value} % (Grenze {limit} %)."),
        "soc_low_ok": ("Akku lädt wieder", "Akkubank bei {value} %."),
        "mismatch": ("Packs haben unterschiedliche Einstellungen", "Diese Einstellungen unterscheiden sich: {keys}. Mit der Einstellungskarte angleichen."),
        "mismatch_ok": ("Einstellungen wieder gleich", "Alle Packs haben wieder dieselben Einstellungen."),
    },
}

ALARM_NAMES = {
    "nl": {"cell_overvoltage": "cel overspanning", "cell_undervoltage": "cel onderspanning", "charge_overcurrent": "laadstroom te hoog",
           "discharge_overcurrent": "ontlaadstroom te hoog", "charge_overtemperature": "te warm om te laden", "charge_undertemperature": "te koud om te laden",
           "discharge_overtemperature": "te warm om te ontladen", "mos_overtemperature": "MOS te warm", "battery_overvoltage": "accu overspanning",
           "battery_undervoltage": "accu onderspanning", "charge_short_circuit": "kortsluiting bij laden", "discharge_short_circuit": "kortsluiting bij ontladen",
           "wire_resistance": "weerstand balanceerdraad te hoog", "temperature_sensor": "temperatuursensor defect", "current_sensor": "stroomsensor defect",
           "cell_quantity": "aantal cellen klopt niet", "charge_mos": "laad-MOSFET defect", "discharge_mos": "ontlaad-MOSFET defect",
           "internal_communication": "interne communicatiefout", "discharge_on_failed": "ontladen kon niet aan", "battery_overtemperature": "accu te warm",
           "parallel_module": "parallelmodule defect"},
    "de": {"cell_overvoltage": "Zellüberspannung", "cell_undervoltage": "Zellunterspannung", "charge_overcurrent": "Ladeüberstrom",
           "discharge_overcurrent": "Entladeüberstrom", "charge_overtemperature": "zu warm zum Laden", "charge_undertemperature": "zu kalt zum Laden",
           "discharge_overtemperature": "zu warm zum Entladen", "mos_overtemperature": "MOS Übertemperatur"},
}


@dataclass
class _Cond:
    since: float | None = None
    active: bool = False


class Alerts:
    def __init__(self, manager: JkBmsManager) -> None:
        self.manager = manager
        self.hass: HomeAssistant = manager.hass
        self._conds: dict[str, _Cond] = {}
        self._started = time.monotonic()
        self._last_eval = 0.0
        self._issues: set[str] = set()

    # ---- options

    def _opt(self, key: str, default: Any) -> Any:
        return self.manager.entry.options.get(key, default)

    @property
    def lang(self) -> str:
        lang = (self.hass.config.language or "en").split("-")[0]
        return lang if lang in TEXT else "en"

    def _alarm_name(self, alarm: str) -> str:
        names = ALARM_NAMES.get(self.lang, {})
        return names.get(alarm, alarm.replace("_", " "))

    # ---- evaluation

    @callback
    def evaluate(self) -> None:
        now = time.monotonic()
        if now - self._last_eval < EVAL_EVERY_S:
            return
        self._last_eval = now
        try:
            self._evaluate(now)
        except Exception:  # noqa: BLE001 - alerts must never break the integration
            _LOGGER.exception("JK BMS Smart alert check failed")

    def _evaluate(self, now: float) -> None:
        m = self.manager
        events = set(self._opt(OPT_NOTIFY_EVENTS, DEFAULT_NOTIFY_EVENTS))
        grace = now - self._started < STARTUP_GRACE_S
        delta_lim = float(self._opt(OPT_DELTA_MV, DEFAULT_DELTA_MV))
        t_high = float(self._opt(OPT_TEMP_HIGH, DEFAULT_TEMP_HIGH))
        t_low = float(self._opt(OPT_TEMP_LOW, DEFAULT_TEMP_LOW))
        soc_low = float(self._opt(OPT_SOC_LOW, DEFAULT_SOC_LOW))
        seen: set[str] = set()

        def cond(key: str, on: bool, hold: float, event: str, args: dict[str, Any]) -> None:
            seen.add(key)
            c = self._conds.setdefault(key, _Cond())
            if on:
                c.since = c.since or now
                if not c.active and now - c.since >= hold and not grace:
                    c.active = True
                    if event in events:
                        self._send(key, event, args, resolved=False)
            else:
                c.since = None
                if c.active:
                    c.active = False
                    if event in events and self._opt(OPT_NOTIFY_RESOLVED, True):
                        self._send(key, event, args, resolved=True)

        # bus
        cond("port", not m.bus.connected, PORT_REPAIR_S, "offline", {"error": m.bus.last_error or "—"})
        self._issue("port_lost", not m.bus.connected and self._held("port", now, PORT_REPAIR_S),
                    {"error": m.bus.last_error or "—"})

        for unit in m.units:
            a = unit.address
            pack = unit.name
            online = m.online(a)
            cond(f"offline:{a}", not online and m.bus.connected, 60, "offline", {"pack": pack})
            self._issue(f"pack_offline_{a}", not online and m.bus.connected and self._held(f"offline:{a}", now, OFFLINE_REPAIR_S),
                        {"pack": pack}, key="pack_offline")
            s = m.state(a)
            c = s.cells if s and online else None
            if c is None:
                continue
            for alarm in c.problems:
                cond(f"alarm:{a}:{alarm}", True, 5, "alarm", {"pack": pack, "alarm": self._alarm_name(alarm)})
            for key in [k for k in self._conds if k.startswith(f"alarm:{a}:")]:
                if key.split(":", 2)[2] not in c.problems:
                    cond(key, False, 5, "alarm", {"pack": pack, "alarm": self._alarm_name(key.split(":", 2)[2])})
            delta = round((c.cell_max - c.cell_min) * 1000)
            dc = self._conds.get(f"delta:{a}")
            on = delta >= (delta_lim - 10 if dc and dc.active else delta_lim)
            cond(f"delta:{a}", on, 300, "delta", {"pack": pack, "value": delta, "limit": int(delta_lim),
                                                  "low": c.cells.index(c.cell_min) + 1, "high": c.cells.index(c.cell_max) + 1})
            temps = [t for t in [c.mos_temp, *c.temps] if t is not None]
            if temps:
                hi, lo = max(temps), min(temps)
                hc = self._conds.get(f"temp_high:{a}")
                cond(f"temp_high:{a}", hi >= (t_high - 3 if hc and hc.active else t_high), 60, "temp",
                     {"pack": pack, "value": round(hi, 1), "limit": int(t_high)})
                lc = self._conds.get(f"temp_low:{a}")
                cond(f"temp_low:{a}", lo <= (t_low + 2 if lc and lc.active else t_low), 300, "temp",
                     {"pack": pack, "value": round(lo, 1), "limit": int(t_low)})

        bank = m.bank()
        if bank.get("soc") is not None and soc_low > 0:
            sc = self._conds.get("soc_low")
            cond("soc_low", bank["soc"] <= (soc_low + 5 if sc and sc.active else soc_low), 60, "soc_low",
                 {"value": round(bank["soc"]), "limit": int(soc_low)})

        diff = m.settings_mismatch()
        names = ", ".join(m.setting_label(k) for k in diff)
        cond("mismatch", bool(diff), 600, "mismatch", {"keys": names})
        self._issue("settings_mismatch", bool(diff) and self._held("mismatch", now, 600), {"keys": names or "—"})

        # conditions that no longer exist (pack removed): forget silently
        for key in [k for k in self._conds if k not in seen and not k.startswith("alarm:")]:
            del self._conds[key]

    def _held(self, key: str, now: float, hold: float) -> bool:
        c = self._conds.get(key)
        return bool(c and c.since and now - c.since >= hold)

    # ---- output

    def _send(self, key: str, event: str, args: dict[str, Any], *, resolved: bool) -> None:
        text_key = {"offline": "port" if key == "port" else "offline", "temp": key.split(":")[0]}.get(event, event)
        if resolved:
            text_key += "_ok"
        title_t, body_t = TEXT[self.lang].get(text_key) or TEXT["en"][text_key]
        safe = _SafeDict(args)
        title = title_t.format_map(safe)
        body = body_t.format_map(safe)
        tag = f"jk_bms_smart_{self.manager.entry.entry_id[:6]}_{key}".replace(":", "_")
        _LOGGER.info("JK BMS Smart: %s — %s", title, body)
        if self._opt(OPT_NOTIFY_PERSISTENT, True):
            from homeassistant.components import persistent_notification

            if resolved:
                persistent_notification.async_dismiss(self.hass, tag)
            else:
                persistent_notification.async_create(self.hass, body, title=f"🔋 {title}", notification_id=tag)
        for target in self._opt(OPT_NOTIFY_TARGETS, []) or []:
            service = target.split(".", 1)[-1]
            if not self.hass.services.has_service("notify", service):
                continue
            data = {"title": title, "message": body,
                    "data": {"tag": tag, "group": "jk-bms-smart", "push": {"interruption-level": "passive" if resolved else "time-sensitive"}}}
            self.hass.async_create_task(self._call(service, data))

    async def _call(self, service: str, data: dict[str, Any]) -> None:
        try:
            await self.hass.services.async_call("notify", service, data, blocking=True)
        except Exception as err:  # noqa: BLE001 - a broken notifier must not stop the rest
            _LOGGER.warning("JK BMS Smart could not send a notification via notify.%s: %s", service, err)

    def _issue(self, issue_id: str, on: bool, placeholders: dict[str, Any], key: str | None = None) -> None:
        full = f"{self.manager.entry.entry_id}_{issue_id}"
        if on and full not in self._issues:
            self._issues.add(full)
            ir.async_create_issue(
                self.hass, DOMAIN, full, is_fixable=False, is_persistent=False,
                severity=ir.IssueSeverity.ERROR if issue_id == "port_lost" else ir.IssueSeverity.WARNING,
                translation_key=key or issue_id, translation_placeholders={k: str(v) for k, v in placeholders.items()},
            )
        elif not on and full in self._issues:
            self._issues.discard(full)
            ir.async_delete_issue(self.hass, DOMAIN, full)

    def clear(self) -> None:
        for full in list(self._issues):
            ir.async_delete_issue(self.hass, DOMAIN, full)
        self._issues.clear()

    def test(self, targets: list[str]) -> None:
        """Send one test message to the given notify services (from the options flow)."""
        lang = self.lang
        title = {"nl": "Testmelding", "de": "Testnachricht"}.get(lang, "Test notification")
        body = {"nl": "JK BMS Smart kan je bereiken. 🔋", "de": "JK BMS Smart kann dich erreichen. 🔋"}.get(lang, "JK BMS Smart can reach you. 🔋")
        for target in targets:
            service = target.split(".", 1)[-1]
            if self.hass.services.has_service("notify", service):
                self.hass.async_create_task(self._call(service, {"title": title, "message": body, "data": {"group": "jk-bms-smart"}}))


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "?"
