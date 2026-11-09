"""Config flow: pick the USB-RS485 stick (or network gateway), we find the BMS units."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .bus import MODE_LISTEN, BusError, PortBusy, probe
from .const import (
    CONF_CONNECTION,
    CONF_DEVICE,
    CONF_HOST,
    CONF_PORT,
    CONF_UNITS,
    DEFAULT_DELTA_MV,
    DEFAULT_NOTIFY_EVENTS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SOC_LOW,
    DEFAULT_STALE_AFTER,
    DEFAULT_TEMP_HIGH,
    DEFAULT_TEMP_LOW,
    DOMAIN,
    NAME,
    NOTIFY_EVENTS,
    OPT_ALLOW_CHANGES,
    OPT_DELTA_MV,
    OPT_NOTIFY_EVENTS,
    OPT_NOTIFY_PERSISTENT,
    OPT_NOTIFY_RESOLVED,
    OPT_NOTIFY_TARGETS,
    OPT_SOC_LOW,
    OPT_TEMP_HIGH,
    OPT_TEMP_LOW,
    OPT_POLL_INTERVAL,
    OPT_STALE_AFTER,
    RS485_HINTS,
)

_LOGGER = logging.getLogger(__name__)

MANUAL = "__manual__"


def _list_ports() -> list[dict[str, str]]:
    """All serial ports, stable /dev/serial/by-id paths first, RS485-looking sticks on top."""
    import os

    from serial.tools import list_ports

    by_id: dict[str, str] = {}
    base = "/dev/serial/by-id"
    if os.path.isdir(base):
        for name in os.listdir(base):
            path = os.path.join(base, name)
            by_id[os.path.realpath(path)] = path
    ports = []
    for p in list_ports.comports():
        if not p.vid and not p.device.startswith(("/dev/ttyUSB", "/dev/ttyACM", "COM")):
            continue  # skip built-in UARTs without a device behind them
        label_bits = [p.product or p.description or "", p.manufacturer or ""]
        label = " · ".join(b for b in label_bits if b and b != "n/a") or p.device
        path = by_id.get(os.path.realpath(p.device), p.device)
        hint = any(h in f"{label} {path}".lower() for h in RS485_HINTS)
        ports.append({"path": path, "label": f"{label} — {p.device}", "hint": hint, "serial": p.serial_number or ""})
    ports.sort(key=lambda x: (not x["hint"], x["label"]))
    return ports


class JkBmsConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._conn: dict[str, Any] = {}
        self._result: dict[str, Any] | None = None
        self._error: str | None = None
        self._error_detail = ""
        self._task: asyncio.Task | None = None
        self._ports: list[dict[str, str]] = []

    # ---- start

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="user", menu_options=["usb", "network"])

    async def async_step_usb(self, user_input: dict[str, Any] | Any = None) -> ConfigFlowResult:
        # Home Assistant calls this step with a UsbServiceInfo when a known stick is plugged in.
        if user_input is not None and not isinstance(user_input, dict):
            return await self._async_usb_discovered(user_input)
        errors: dict[str, str] = {}
        if not self._ports:
            self._ports = await self.hass.async_add_executor_job(_list_ports)
        taken = {e.data.get(CONF_CONNECTION, {}).get(CONF_DEVICE) for e in self._async_current_entries()}
        options = [
            selector.SelectOptionDict(value=p["path"], label=p["label"]) for p in self._ports if p["path"] not in taken
        ]
        options.append(selector.SelectOptionDict(value=MANUAL, label="…"))
        if user_input is not None:
            path = user_input.get(CONF_DEVICE)
            if path == MANUAL:
                path = (user_input.get("manual_path") or "").strip()
            if not path:
                errors["base"] = "no_port"
            else:
                await self.async_set_unique_id(path)
                self._abort_if_unique_id_configured()
                self._conn = {"type": "serial", CONF_DEVICE: path}
                return await self.async_step_probe()
        default = options[0]["value"] if options else MANUAL
        return self.async_show_form(
            step_id="usb",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE, default=default): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options, mode=selector.SelectSelectorMode.LIST)
                    ),
                    vol.Optional("manual_path"): str,
                }
            ),
            errors=errors,
            description_placeholders={"count": str(len(self._ports))},
        )

    async def _async_usb_discovered(self, info: Any) -> ConfigFlowResult:
        from homeassistant.components import usb

        path = await self.hass.async_add_executor_job(usb.get_serial_by_id, info.device)
        await self.async_set_unique_id(path)
        self._abort_if_unique_id_configured()
        self._conn = {"type": "serial", CONF_DEVICE: path}
        self.context["title_placeholders"] = {"name": info.description or path}
        return await self.async_step_usb_confirm()

    async def async_step_usb_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return await self.async_step_probe()
        self._set_confirm_only()
        return self.async_show_form(step_id="usb_confirm", description_placeholders={"device": self._conn[CONF_DEVICE]})

    async def async_step_network(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            self._conn = {"type": "tcp", CONF_HOST: host, CONF_PORT: port}
            return await self.async_step_probe()
        return self.async_show_form(
            step_id="network",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=8899): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                }
            ),
        )

    # ---- probing the bus

    async def async_step_probe(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._task is None:
            self._result = None
            self._error = None
            self._task = self.hass.async_create_task(self._async_probe(), eager_start=False)
        if not self._task.done():
            return self.async_show_progress(step_id="probe", progress_action="probe", progress_task=self._task)
        self._task = None
        if self._error:
            return self.async_show_progress_done(next_step_id="failed")
        return self.async_show_progress_done(next_step_id="found")

    async def _async_probe(self) -> None:
        try:
            self._result = await probe(self.hass.loop, self._conn)
            if not self._result["units"]:
                self._error = "no_bms"
                self._error_detail = f"{self._result['bytes']} bytes, {self._result['frames']} frames"
        except PortBusy as err:
            self._error = "port_busy"
            self._error_detail = str(err)
        except BusError as err:
            self._error = "cannot_open"
            self._error_detail = str(err)
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Probing the RS485 bus failed")
            self._error = "unknown"
            self._error_detail = str(err)

    async def async_step_failed(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            if user_input.get("retry"):
                return await self.async_step_probe()
            self._ports = []
            return await self.async_step_user()
        return self.async_show_form(
            step_id="failed",
            data_schema=vol.Schema({vol.Required("retry", default=True): bool}),
            errors={"base": self._error or "unknown"},
            description_placeholders={"detail": self._error_detail},
        )

    async def async_step_found(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        assert self._result
        units = self._result["units"]
        if user_input is not None:
            data = {
                CONF_CONNECTION: self._conn,
                "mode": self._result["mode"],
                CONF_UNITS: [
                    {"address": u["address"], "name": user_input.get(f"name_{u['address']}") or f"JK BMS {i + 1}",
                     "cells": u.get("cells") or 16}
                    for i, u in enumerate(units)
                ],
            }
            return self.async_create_entry(title=user_input.get("title") or "JK BMS", data=data)
        lines = []
        for u in units:
            bits = [f"**#{u['address']}**"]
            if u.get("model"):
                bits.append(u["model"])
            if u.get("cells"):
                bits.append(f"{u['cells']}S")
            if u.get("voltage") is not None:
                bits.append(f"{u['voltage']:.2f} V")
            if u.get("soc") is not None:
                bits.append(f"{u['soc']} %")
            lines.append("- " + " · ".join(bits))
        schema: dict[Any, Any] = {vol.Required("title", default="JK BMS"): str}
        for i, u in enumerate(units):
            schema[vol.Required(f"name_{u['address']}", default=f"JK BMS {i + 1}")] = str
        return self.async_show_form(
            step_id="found",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "count": str(len(units)),
                "units": "\n".join(lines),
                "mode": "listen" if self._result["mode"] == MODE_LISTEN else "poll",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return JkBmsOptionsFlow()


class JkBmsOptionsFlow(OptionsFlow):
    """Configure: settings, names, search again, dashboard."""

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._result: dict[str, Any] | None = None
        self._error: str | None = None

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="init", menu_options=["dashboard", "names", "settings", "notifications", "rescan"])

    async def async_step_notifications(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        opts = self.config_entry.options
        if user_input is not None:
            test = user_input.pop("send_test", False)
            manager = getattr(self.config_entry, "runtime_data", None)
            if test and manager is not None:
                manager.alerts.test(user_input.get(OPT_NOTIFY_TARGETS) or [])
            return self.async_create_entry(data={**opts, **user_input})
        services = sorted(self.hass.services.async_services_for_domain("notify"))
        targets = [s for s in services if s not in ("notify", "persistent_notification", "send_message")]
        # mobile apps first: those are phones
        targets.sort(key=lambda s: (not s.startswith("mobile_app_"), s))
        current = [t for t in opts.get(OPT_NOTIFY_TARGETS, []) if t in targets]
        num = lambda lo, hi, step, unit: selector.NumberSelector(  # noqa: E731
            selector.NumberSelectorConfig(min=lo, max=hi, step=step, unit_of_measurement=unit, mode=selector.NumberSelectorMode.BOX))
        return self.async_show_form(
            step_id="notifications",
            data_schema=vol.Schema(
                {
                    vol.Optional(OPT_NOTIFY_TARGETS, default=current): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=targets, multiple=True, mode=selector.SelectSelectorMode.LIST)
                    ),
                    vol.Required(OPT_NOTIFY_PERSISTENT, default=opts.get(OPT_NOTIFY_PERSISTENT, True)): selector.BooleanSelector(),
                    vol.Required(OPT_NOTIFY_EVENTS, default=opts.get(OPT_NOTIFY_EVENTS, DEFAULT_NOTIFY_EVENTS)): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=list(NOTIFY_EVENTS), multiple=True, mode=selector.SelectSelectorMode.LIST,
                                                      translation_key="notify_events")
                    ),
                    vol.Required(OPT_DELTA_MV, default=opts.get(OPT_DELTA_MV, DEFAULT_DELTA_MV)): num(10, 500, 5, "mV"),
                    vol.Required(OPT_TEMP_HIGH, default=opts.get(OPT_TEMP_HIGH, DEFAULT_TEMP_HIGH)): num(30, 80, 1, "°C"),
                    vol.Required(OPT_TEMP_LOW, default=opts.get(OPT_TEMP_LOW, DEFAULT_TEMP_LOW)): num(-20, 20, 1, "°C"),
                    vol.Required(OPT_SOC_LOW, default=opts.get(OPT_SOC_LOW, DEFAULT_SOC_LOW)): num(0, 50, 1, "%"),
                    vol.Required(OPT_NOTIFY_RESOLVED, default=opts.get(OPT_NOTIFY_RESOLVED, True)): selector.BooleanSelector(),
                    vol.Optional("send_test", default=False): selector.BooleanSelector(),
                }
            ),
            description_placeholders={"count": str(len(targets))},
        )

    async def async_step_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data={**self.config_entry.options, **user_input})
        opts = self.config_entry.options
        return self.async_show_form(
            step_id="settings",
            data_schema=vol.Schema(
                {
                    vol.Required(OPT_POLL_INTERVAL, default=opts.get(OPT_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=2, max=60, step=1, unit_of_measurement="s", mode=selector.NumberSelectorMode.BOX)
                    ),
                    vol.Required(OPT_STALE_AFTER, default=opts.get(OPT_STALE_AFTER, DEFAULT_STALE_AFTER)): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=15, max=900, step=5, unit_of_measurement="s", mode=selector.NumberSelectorMode.BOX)
                    ),
                    vol.Required(OPT_ALLOW_CHANGES, default=opts.get(OPT_ALLOW_CHANGES, False)): selector.BooleanSelector(),
                }
            ),
        )

    async def async_step_names(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        units = list(self.config_entry.data.get(CONF_UNITS, []))
        if user_input is not None:
            new_units = [{**u, "name": user_input.get(f"name_{u['address']}") or u.get("name")} for u in units]
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, CONF_UNITS: new_units}
            )
            return self.async_create_entry(data=dict(self.config_entry.options))
        schema = {vol.Required(f"name_{u['address']}", default=u.get("name") or f"JK BMS {i + 1}"): str for i, u in enumerate(units)}
        return self.async_show_form(
            step_id="names",
            data_schema=vol.Schema(schema),
            description_placeholders={"units": ", ".join(f"#{u['address']}" for u in units)},
        )

    async def async_step_rescan(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None and self._task is None:
            return self.async_show_form(step_id="rescan", data_schema=vol.Schema({}))
        if self._task is None:
            self._task = self.hass.async_create_task(self._async_rescan(), eager_start=False)
        if not self._task.done():
            return self.async_show_progress(step_id="rescan", progress_action="probe", progress_task=self._task)
        self._task = None
        return self.async_show_progress_done(next_step_id="rescan_done")

    async def _async_rescan(self) -> None:
        entry = self.config_entry
        manager = getattr(entry, "runtime_data", None)
        try:
            if manager is not None:
                await manager.bus.release()  # free the port for a moment
            self._result = await probe(self.hass.loop, entry.data[CONF_CONNECTION])
        except BusError as err:
            self._error = str(err)
        finally:
            if manager is not None:
                manager.bus.resume()  # the run loop reopens the port

    async def async_step_rescan_done(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        entry = self.config_entry
        old = {u["address"]: u for u in entry.data.get(CONF_UNITS, [])}
        found = (self._result or {}).get("units", [])
        if user_input is not None:
            if found:
                units = [
                    {"address": u["address"], "name": old.get(u["address"], {}).get("name") or f"JK BMS {i + 1}",
                     "cells": u.get("cells") or old.get(u["address"], {}).get("cells") or 16}
                    for i, u in enumerate(found)
                ]
                # units that are not found now are kept: a pack may simply be switched off
                for addr, u in old.items():
                    if addr not in {x["address"] for x in units}:
                        units.append(u)
                units.sort(key=lambda x: x["address"])
                self.hass.config_entries.async_update_entry(
                    entry, data={**entry.data, CONF_UNITS: units, "mode": self._result.get("mode")}
                )
            return self.async_create_entry(data=dict(entry.options))
        new = [u for u in found if u["address"] not in old]
        return self.async_show_form(
            step_id="rescan_done",
            data_schema=vol.Schema({}),
            description_placeholders={
                "found": ", ".join(f"#{u['address']}" for u in found) or "—",
                "new": ", ".join(f"#{u['address']}" for u in new) or "—",
                "error": self._error or "",
            },
        )

    async def async_step_dashboard(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        from homeassistant.exceptions import HomeAssistantError

        from .dashboard import async_create_dashboard

        errors: dict[str, str] = {}
        placeholders = {"error": "", "url": ""}
        if user_input is not None:
            user = await self.hass.auth.async_get_user(self.context["user_id"]) if self.context.get("user_id") else None
            if user is not None and not user.is_admin:
                errors["base"] = "not_admin"
            else:
                try:
                    url = await async_create_dashboard(self.config_entry.runtime_data)
                except HomeAssistantError as err:
                    errors["base"] = "dashboard_failed"
                    placeholders["error"] = str(err)
                else:
                    return self.async_abort(reason="dashboard_created", description_placeholders={"url": f"/{url}"})
        return self.async_show_form(step_id="dashboard", data_schema=vol.Schema({}), errors=errors,
                                    description_placeholders=placeholders)


__all__ = ["JkBmsConfigFlow", "NAME"]
