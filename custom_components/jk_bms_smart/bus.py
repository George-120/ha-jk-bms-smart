"""RS485 bus engine: serial or TCP transport, master detection, polling and listening.

Two ways a JK inverter-BMS bus can be wired:

* **Listen** - one BMS has DIP address 0 and is the bus master. It sends its own
  data and polls the others. We never transmit (that would collide) and only
  decode what passes by.
* **Poll** - no BMS has address 0. We are the master and ask every BMS in turn.

The mode is detected automatically: if requests or address-0 frames appear on the
bus while we stay silent, a master is present.
"""

from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .protocol import (
    MAX_ADDRESS,
    REG_CELLS,
    REG_INFO,
    REG_SETTINGS,
    TYPE_CELLS,
    TYPE_INFO,
    TYPE_SETTINGS,
    Attributor,
    CellData,
    DataFrame,
    DeviceInfo,
    FrameReader,
    WRITABLE,
    ModbusAck,
    ModbusError,
    ModbusRequest,
    Settings,
    build_request,
    build_write,
    check_settings,
    decode_cells,
    decode_info,
    decode_settings,
)

_LOGGER = logging.getLogger(__name__)

BAUDRATE = 115200
GAP_S = 0.03  # silence that ends a frame (115200 baud: 300 bytes take 26 ms)
ANSWER_TIMEOUT_S = 0.5
MODE_LISTEN = "listen"
MODE_POLL = "poll"


class BusError(Exception):
    """The port could not be opened or was lost."""


class PortBusy(BusError):
    """Another program (e.g. an add-on) holds the serial port."""


# ---------------------------------------------------------------- transports


class Transport:
    on_data: Callable[[bytes], None]
    on_lost: Callable[[Exception | None], None]

    async def open(self) -> None: ...
    async def write(self, data: bytes) -> None: ...
    async def close(self) -> None: ...


class SerialTransport(Transport):
    """pyserial in a reader thread (pyserial ships with Home Assistant)."""

    def __init__(self, loop: asyncio.AbstractEventLoop, port: str) -> None:
        self._loop = loop
        self._port = port
        self._ser: Any = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    async def open(self) -> None:
        await self._loop.run_in_executor(None, self._open)
        self._stop.clear()
        self._thread = threading.Thread(target=self._read_loop, name="jk_bms_smart reader", daemon=True)
        self._thread.start()

    def _open(self) -> None:
        import serial  # noqa: PLC0415 - imported in the executor, not in the event loop

        try:
            self._ser = serial.Serial(
                self._port, BAUDRATE, bytesize=8, parity="N", stopbits=1, timeout=0.02, exclusive=True
            )
        except (serial.SerialException, OSError) as err:
            text = str(err).lower()
            if "lock" in text or "busy" in text or "resource temporarily" in text or "errno 11" in text:
                raise PortBusy(str(err)) from err
            raise BusError(str(err)) from err
        with contextlib.suppress(Exception):
            self._ser.reset_input_buffer()

    def _read_loop(self) -> None:
        ser = self._ser
        while not self._stop.is_set():
            try:
                data = ser.read(512)
            except Exception as err:  # noqa: BLE001 - USB unplugged etc.
                if not self._stop.is_set():
                    self._loop.call_soon_threadsafe(self.on_lost, err)
                return
            if data:
                self._loop.call_soon_threadsafe(self.on_data, data)

    async def write(self, data: bytes) -> None:
        def _write() -> None:
            self._ser.write(data)
            self._ser.flush()

        await self._loop.run_in_executor(None, _write)

    async def close(self) -> None:
        self._stop.set()
        ser, self._ser = self._ser, None
        if ser is not None:
            await self._loop.run_in_executor(None, ser.close)
        if self._thread:
            await self._loop.run_in_executor(None, self._thread.join, 1)


class TcpTransport(Transport):
    """RS485-to-network converters (Elfin EW11, USR-TCP232, Waveshare) in transparent TCP mode."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._task: asyncio.Task | None = None

    async def open(self) -> None:
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=8
            )
        except (OSError, TimeoutError) as err:
            raise BusError(str(err)) from err
        self._task = asyncio.get_running_loop().create_task(self._read_loop())

    async def _read_loop(self) -> None:
        assert self._reader
        try:
            while True:
                data = await self._reader.read(1024)
                if not data:
                    raise ConnectionError("connection closed")
                self.on_data(data)
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            self.on_lost(err)

    async def write(self, data: bytes) -> None:
        assert self._writer
        self._writer.write(data)
        await self._writer.drain()

    async def close(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self._task
        if self._writer:
            self._writer.close()
            with contextlib.suppress(Exception):
                await self._writer.wait_closed()


def make_transport(loop: asyncio.AbstractEventLoop, conn: dict[str, Any]) -> Transport:
    if conn.get("type") == "tcp":
        return TcpTransport(conn["host"], int(conn["port"]))
    return SerialTransport(loop, conn["device"])


# ---------------------------------------------------------------- per BMS state


@dataclass
class BmsState:
    address: int
    cells: CellData | None = None
    settings: Settings | None = None
    info: DeviceInfo | None = None
    last_seen: float = 0.0
    frames: int = 0
    timeouts: int = 0
    last_frame_ts: dict[int, float] = field(default_factory=dict)

    def online(self, now: float, stale_after: float) -> bool:
        return self.cells is not None and now - self.last_seen < stale_after


# ---------------------------------------------------------------- engine


class JkBus:
    """Owns the transport and the protocol state for one RS485 bus."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        conn: dict[str, Any],
        *,
        poll_interval: float = 5.0,
        on_update: Callable[[int, int], None] | None = None,
    ) -> None:
        self._loop = loop
        self._conn = conn
        self.poll_interval = poll_interval
        self.on_update = on_update
        self.reader = FrameReader()
        self.attr = Attributor()
        self.states: dict[int, BmsState] = {}
        self.known: set[int] | None = None  # set after setup: other addresses never become devices
        self.unknown_seen: dict[int, int] = {}
        self.mode: str | None = None
        self.connected = False
        self.last_error: str | None = None
        self._transport: Transport | None = None
        self._gap_handle: asyncio.TimerHandle | None = None
        self._answer: asyncio.Future | None = None
        self._expect: tuple[int, int] | None = None
        self._own_requests: list[tuple[float, int, int]] = []
        self._foreign_requests = 0
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    # ---- life cycle

    async def open(self) -> None:
        transport = make_transport(self._loop, self._conn)
        transport.on_data = self._on_data
        transport.on_lost = self._on_lost
        await transport.open()
        self._transport = transport
        self.connected = True
        self.last_error = None

    async def close(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await self._task
            self._task = None
        if self._gap_handle:
            self._gap_handle.cancel()
        if self._transport:
            transport, self._transport = self._transport, None
            await transport.close()
        self.connected = False

    async def release(self) -> None:
        """Hand the port to someone else for a moment (rescan); the run loop waits."""
        self._paused = True
        async with self._lock:
            if self._transport:
                transport, self._transport = self._transport, None
                await transport.close()
            self.connected = False

    def resume(self) -> None:
        self._paused = False

    _paused = False

    def _on_lost(self, err: Exception | None) -> None:
        _LOGGER.warning("RS485 connection lost: %s", err)
        self.connected = False
        self.last_error = str(err)

    # ---- receiving

    def _on_data(self, data: bytes) -> None:
        self._last_rx = time.monotonic()
        for token in self.reader.feed(data):
            self._handle_token(token)
        if self._gap_handle:
            self._gap_handle.cancel()
        self._gap_handle = self._loop.call_later(GAP_S, self._on_gap)

    def _on_gap(self) -> None:
        self._gap_handle = None
        self.reader.flush()
        for addr, frame in self.attr.flush():
            self._accept(addr, frame)

    def _handle_token(self, token: Any) -> None:
        ours = False
        if isinstance(token, ModbusRequest):
            now = time.monotonic()
            self._own_requests = [r for r in self._own_requests if now - r[0] < 0.3]
            ours = any(r[1] == token.address and r[2] == token.register for r in self._own_requests)
            if not ours:
                self._foreign_requests += 1
        for addr, frame in self.attr.push(token, ours=ours):
            self._accept(addr, frame)
        if self._write_wait is not None and not self._write_wait.done() and self._write_expect:
            w_addr, w_reg = self._write_expect
            if isinstance(token, ModbusAck) and token.address == w_addr and token.register == w_reg:
                self._write_wait.set_result(None)
            elif isinstance(token, ModbusError) and token.address == w_addr:
                self._write_wait.set_result(f"refused (code {token.code})")
        if isinstance(token, ModbusAck) and self._expect and self._answer and not self._answer.done():
            if token.address == self._expect[0]:
                # the frame was accepted just before; make sure the waiter wakes up
                self._answer.set_result(True)

    def _accept(self, addr: int, frame: DataFrame) -> None:
        if addr > MAX_ADDRESS:
            return
        if self.known is not None and addr not in self.known:
            # Never auto-create devices from bus noise. Count it so the user can be told.
            self.unknown_seen[addr] = self.unknown_seen.get(addr, 0) + 1
            return
        state = self.states.setdefault(addr, BmsState(addr))
        try:
            if frame.type == TYPE_CELLS:
                state.cells = decode_cells(frame.raw)
            elif frame.type == TYPE_SETTINGS:
                settings = decode_settings(frame.raw)
                if settings.address != addr and settings.address <= MAX_ADDRESS:
                    _LOGGER.debug("Settings frame says address %s, ack said %s", settings.address, addr)
                    return
                state.settings = settings
            elif frame.type == TYPE_INFO:
                state.info = decode_info(frame.raw)
        except (IndexError, ValueError) as err:
            _LOGGER.debug("Could not decode frame type %s from %s: %s", frame.type, addr, err)
            return
        now = time.monotonic()
        state.last_seen = now
        state.frames += 1
        state.last_frame_ts[frame.type] = now
        if self._expect and self._expect[0] == addr and self._answer and not self._answer.done():
            self._answer.set_result(True)
        if self.on_update:
            self.on_update(addr, frame.type)

    # ---- master detection

    @property
    def master_present(self) -> bool:
        return self.attr.master_seen or self._foreign_requests > 2

    async def detect_mode(self, listen_s: float = 4.0) -> str:
        """Stay silent and listen. Any foreign master traffic means: listen only."""
        await asyncio.sleep(listen_s)
        self.mode = MODE_LISTEN if self.master_present or self.reader.frames > 0 else MODE_POLL
        return self.mode

    # ---- polling

    async def request(self, address: int, register: int, timeout: float = ANSWER_TIMEOUT_S) -> bool:
        if not self._transport or not self.connected:
            return False
        async with self._lock:
            self._expect = (address, register)
            self._answer = self._loop.create_future()
            self._own_requests.append((time.monotonic(), address, register))
            try:
                await self._transport.write(build_request(address, register))
                await asyncio.wait_for(self._answer, timeout)
                await asyncio.sleep(0.03)  # let the trailing ack pass before the next request
                return True
            except TimeoutError:
                if address in self.states:
                    self.states[address].timeouts += 1
                return False
            except Exception as err:  # noqa: BLE001 - write failed: port gone
                self._on_lost(err)
                return False
            finally:
                self._expect = None
                self._answer = None

    # ---- writing settings

    _last_rx = 0.0
    _write_wait: asyncio.Future | None = None
    _write_expect: tuple[int, int] | None = None

    async def _wait_quiet(self, quiet_s: float, timeout_s: float) -> bool:
        """With a master BMS on the bus, only transmit in a silent gap between its messages."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if time.monotonic() - self._last_rx >= quiet_s:
                return True
            await asyncio.sleep(0.01)
        return False

    async def write(self, address: int, key: str, value: float) -> None:
        """Change one setting. Raises ValueError / BusError with a readable reason."""
        w = WRITABLE[key]
        state = self.states.get(address)
        current = state.settings.as_dict() if state and state.settings else {}
        if reason := check_settings(current, key, value):
            raise ValueError(reason)
        frame = build_write(address, key, value)  # validates the range
        if not self._transport or not self.connected:
            raise BusError("RS485 port is not connected")
        listen = self.mode == MODE_LISTEN or self.master_present
        if await self._write_locked(address, key, value, w, frame, state, listen):
            if not listen:
                # poll mode: read the settings back right away so the card shows the real value
                await asyncio.sleep(0.05)
                await self.request(address, REG_SETTINGS)
            return

    async def _write_locked(self, address, key, value, w, frame, state, listen) -> bool:  # noqa: ANN001
        async with self._lock:
            last = "no answer"
            for _attempt in range(4):
                if listen and not await self._wait_quiet(0.12, 20):
                    last = "bus never went quiet"
                    continue
                self._write_expect = (address, w.register)
                self._write_wait = self._loop.create_future()
                try:
                    await self._transport.write(frame)
                    result = await asyncio.wait_for(self._write_wait, 0.6)
                except TimeoutError:
                    result = "no answer"
                finally:
                    self._write_expect = None
                    self._write_wait = None
                if result is None:
                    _LOGGER.info("BMS %s: %s set to %s", address, key, value)
                    if state and state.settings:
                        state.settings = dataclasses.replace(state.settings, **{key: bool(value) if key.endswith("_switch") else value})
                    if self.on_update:
                        self.on_update(address, TYPE_SETTINGS)
                    return True
                last = result
                if result.startswith("refused"):
                    break
                await asyncio.sleep(0.2)
        raise BusError(f"BMS {address} did not accept {key}: {last}")

    async def scan(self, addresses: range | list[int] = range(0, MAX_ADDRESS + 1)) -> list[int]:
        """Poll mode: find which addresses answer."""
        found = []
        for addr in addresses:
            if await self.request(addr, REG_INFO, timeout=0.35) or await self.request(addr, REG_CELLS, timeout=0.35):
                found.append(addr)
        for addr in found:
            await self.request(addr, REG_SETTINGS)
            await self.request(addr, REG_CELLS)
        return found

    async def fetch_info(self, force: bool = False) -> None:
        """Listen mode: ask every known BMS for its device info in a quiet moment on the bus."""
        for addr in sorted(self.known or []):
            state = self.states.get(addr)
            if state and state.info and not force:
                continue
            before = state.info if state else None
            for _attempt in range(3):
                if not await self._wait_quiet(0.12, 20):
                    return
                await self.request(addr, REG_INFO, timeout=0.6)
                state = self.states.get(addr)
                if state and state.info is not None and state.info is not before:
                    break
                await asyncio.sleep(0.3)

    _started = 0.0
    _info_rounds = 0

    def start(self, addresses: list[int]) -> None:
        self._started = time.monotonic()
        self.known = set(addresses)
        self._task = self._loop.create_task(self._run())

    async def _run(self) -> None:
        backoff = 5
        last_settings = 0.0
        last_info = 0.0
        while True:
            if self._paused:
                await asyncio.sleep(1)
                continue
            if not self.connected:
                try:
                    if self._transport:
                        await self._transport.close()
                        self._transport = None
                    await self.open()
                    backoff = 5
                except BusError as err:
                    self.last_error = str(err)
                    if self.on_update:
                        self.on_update(-1, 0)
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60)
                    continue
            if self.mode == MODE_LISTEN or self.master_present:
                # a master BMS does the asking; cells and settings pass by every few cycles.
                # The master never asks for device info (model, firmware, serial), so we ask
                # for it ourselves in a quiet gap: at start until we have it, then every 6 hours.
                self.mode = MODE_LISTEN
                await asyncio.sleep(self.poll_interval)
                now = time.monotonic()
                missing = any(not (self.states.get(a) and self.states[a].info) for a in (self.known or []))
                # a BMS that never answers (old firmware) is asked less often after 10 tries
                retry = 120 if self._info_rounds < 10 else 3600
                if now - self._started > 15 and now - last_info > (retry if missing else 6 * 3600):
                    last_info = now
                    self._info_rounds += 1 if missing else 0
                    await self.fetch_info(force=not missing)
                if self.on_update:
                    self.on_update(-1, 0)
                continue
            self.mode = MODE_POLL
            started = time.monotonic()
            for addr in sorted(self.known or []):
                await self.request(addr, REG_CELLS)
            if started - last_settings > 300:
                last_settings = started
                for addr in sorted(self.known or []):
                    await self.request(addr, REG_SETTINGS)
            if started - last_info > 3600:
                last_info = started
                for addr in sorted(self.known or []):
                    await self.request(addr, REG_INFO)
            if self.on_update:
                self.on_update(-1, 0)
            await asyncio.sleep(max(0.5, self.poll_interval - (time.monotonic() - started)))

    # ---- diagnostics

    def diagnostics(self) -> dict[str, Any]:
        now = time.monotonic()
        return {
            "mode": self.mode,
            "connected": self.connected,
            "last_error": self.last_error,
            "master_present": self.master_present,
            "foreign_requests": self._foreign_requests,
            "bytes_in": self.reader.bytes_in,
            "frames": self.reader.frames,
            "bad_checksum": self.reader.bad_checksum,
            "dropped_bytes": self.reader.dropped,
            "ignored_addresses": dict(self.unknown_seen),
            "bms": {
                addr: {
                    "frames": s.frames,
                    "timeouts": s.timeouts,
                    "seconds_since_seen": round(now - s.last_seen, 1) if s.last_seen else None,
                    "has_cells": s.cells is not None,
                    "has_settings": s.settings is not None,
                    "has_info": s.info is not None,
                }
                for addr, s in self.states.items()
            },
        }


async def probe(loop: asyncio.AbstractEventLoop, conn: dict[str, Any], listen_s: float = 6.0) -> dict[str, Any]:
    """Used by the config flow: open the port, find the mode and the BMS units, close again."""
    bus = JkBus(loop, conn)
    await bus.open()
    try:
        mode = await bus.detect_mode(4.0)
        if mode == MODE_LISTEN:
            # a master cycles every few seconds; wait until every unit was heard (max ~30 s)
            deadline = time.monotonic() + max(listen_s, 30)
            stable_since = time.monotonic()
            seen = set(bus.states)
            while time.monotonic() < deadline:
                await asyncio.sleep(1)
                if set(bus.states) != seen:
                    seen = set(bus.states)
                    stable_since = time.monotonic()
                have_all = all(s.cells is not None for s in bus.states.values())
                if seen and have_all and time.monotonic() - stable_since > 12:
                    break
            found = sorted(a for a, s in bus.states.items() if s.cells is not None or s.settings is not None)
        else:
            found = await bus.scan()
        units = []
        for addr in found:
            s = bus.states.get(addr)
            units.append(
                {
                    "address": addr,
                    "model": s.info.model if s and s.info else None,
                    "serial": s.info.serial if s and s.info else None,
                    "cells": s.cells.cell_count if s and s.cells else None,
                    "soc": s.cells.soc if s and s.cells else None,
                    "voltage": s.cells.voltage if s and s.cells else None,
                }
            )
        return {"mode": mode, "units": units, "frames": bus.reader.frames, "bytes": bus.reader.bytes_in}
    finally:
        await bus.close()
