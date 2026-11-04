"""Bus engine against a simulated RS485 bus (TCP transport): listen mode and poll mode."""

from __future__ import annotations

import asyncio
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PKG = HERE.parent / "custom_components"
sys.path.insert(0, str(PKG))

import importlib  # noqa: E402
import types  # noqa: E402

from test_protocol import ack, cells_frame, settings_frame  # noqa: E402

# bus.py and protocol.py need no Home Assistant: load them as a bare package (skip __init__.py)
_pkg = types.ModuleType("jkbus_pkg")
_pkg.__path__ = [str(PKG / "jk_bms_smart")]
sys.modules["jkbus_pkg"] = _pkg
busmod = importlib.import_module("jkbus_pkg.bus")
p = importlib.import_module("jkbus_pkg.protocol")


async def _master_server(reader, writer):
    """A BMS at address 0 polls 1 and 2 every 0.4 s; the 'cable' also carries some noise."""
    try:
        while True:
            writer.write(cells_frame([3300] * 16) + ack(0))
            writer.write(b"\x00\xff\x13")  # line noise
            for addr, mv in ((1, 3200), (2, 3100)):
                writer.write(p.build_request(addr, p.REG_CELLS))
                writer.write(cells_frame([mv] * 16) + ack(addr))
            writer.write(p.build_request(1, p.REG_SETTINGS) + settings_frame(1) + ack(1, p.REG_SETTINGS))
            await writer.drain()
            await asyncio.sleep(0.4)
    except (ConnectionError, asyncio.CancelledError):
        pass


async def _slave_server(reader, writer):
    """Three slaves (1, 2, 3) that only answer requests."""
    buf = b""
    try:
        while True:
            data = await reader.read(64)
            if not data:
                return
            buf += data
            while len(buf) >= 11:
                addr, func, reg = buf[0], buf[1], struct.unpack(">H", buf[2:4])[0]
                req, buf = buf[:11], buf[11:]
                if func != 0x10 or addr not in (1, 2, 3) or req != p.build_request(addr, reg):
                    continue
                if reg == p.REG_CELLS:
                    writer.write(cells_frame([3000 + addr * 100] * 16) + ack(addr, reg))
                elif reg == p.REG_SETTINGS:
                    writer.write(settings_frame(addr) + ack(addr, reg))
                await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass


def _run(coro):
    return asyncio.run(coro)


def test_listen_mode_finds_master_and_slaves():
    async def main():
        server = await asyncio.start_server(_master_server, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        busmod.GAP_S = 0.01
        result = await asyncio.wait_for(busmod.probe(asyncio.get_running_loop(), {"type": "tcp", "host": "127.0.0.1", "port": port}), 60)
        server.close()
        return result

    result = _run(main())
    assert result["mode"] == busmod.MODE_LISTEN
    assert [u["address"] for u in result["units"]] == [0, 1, 2]
    assert [u["voltage"] for u in result["units"]] == [52.336] * 3


def test_poll_mode_scans_and_reads():
    async def main():
        server = await asyncio.start_server(_slave_server, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        loop = asyncio.get_running_loop()
        result = await busmod.probe(loop, {"type": "tcp", "host": "127.0.0.1", "port": port})
        bus = busmod.JkBus(loop, {"type": "tcp", "host": "127.0.0.1", "port": port}, poll_interval=0.5)
        await bus.open()
        bus.mode = busmod.MODE_POLL
        bus.start([1, 2, 3])
        await asyncio.sleep(1.5)
        states = {a: s.cells.cells[0] for a, s in bus.states.items() if s.cells}
        await bus.close()
        server.close()
        return result, states

    result, states = _run(main())
    assert result["mode"] == busmod.MODE_POLL
    assert [u["address"] for u in result["units"]] == [1, 2, 3]
    assert states == {1: 3.1, 2: 3.2, 3: 3.3}
