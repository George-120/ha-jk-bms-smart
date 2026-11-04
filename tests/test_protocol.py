"""Protocol tests: framing, attribution (no ghost devices) and decoding."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "custom_components" / "jk_bms_smart"))

import protocol as p  # noqa: E402


def make_frame(ftype: int, fields: dict[int, tuple[str, int]], counter: int = 1) -> bytes:
    body = bytearray(p.FRAME_LEN)
    body[0:4] = p.HEADER
    body[4] = ftype
    body[5] = counter
    for offset, (fmt, value) in fields.items():
        struct.pack_into("<" + fmt, body, 6 + offset, value)
    body[-1] = sum(body[:-1]) & 0xFF
    return bytes(body)


def cells_frame(cells: list[int], **kw) -> bytes:
    fields: dict[int, tuple[str, int]] = {2 * i: ("H", v) for i, v in enumerate(cells)}
    fields[64] = ("I", (1 << len(cells)) - 1)
    fields[68] = ("H", sum(cells) // len(cells))
    fields[70] = ("H", max(cells) - min(cells))
    fields[138] = ("h", 215)
    fields[144] = ("I", kw.get("mv", 52336))
    fields[152] = ("i", kw.get("ma", -12500))
    fields[156] = ("h", 169)
    fields[158] = ("h", 173)
    fields[160] = ("I", kw.get("alarms", 1 << 19))
    fields[164] = ("h", kw.get("bal_ma", 0))
    fields[166] = ("B", kw.get("bal", 0))
    fields[167] = ("B", kw.get("soc", 65))
    fields[168] = ("i", 202859)
    fields[172] = ("I", 314000)
    fields[176] = ("I", 12)
    fields[184] = ("B", 100)
    fields[192] = ("B", 1)
    fields[193] = ("B", 1)
    fields[208] = ("B", 0b111)  # MOS + T1 + T2 present
    fields[248] = ("h", 189)
    return make_frame(2, fields)


def settings_frame(address: int) -> bytes:
    return make_frame(1, {4: ("I", 2580), 12: ("I", 3650), 108: ("I", 16), 112: ("I", 1), 124: ("I", 314000), 264: ("I", address)})


def ack(addr: int, reg: int = p.REG_CELLS) -> bytes:
    return p.with_crc(struct.pack(">BBHH", addr, 0x10, reg, 1))


def test_crc_matches_known_request():
    # from JK documentation captures: 01 10 16 20 00 01 02 00 00 D6 F1
    assert p.build_request(1, p.REG_CELLS).hex(" ") == "01 10 16 20 00 01 02 00 00 d6 f1"
    assert p.build_request(2, p.REG_CELLS).hex(" ") == "02 10 16 20 00 01 02 00 00 c2 01"
    assert ack(0).hex(" ") == "00 10 16 20 00 01 05 9a"


def test_decode_cells():
    cells = [3271] * 10 + [3272, 3271, 3272, 3268, 3272, 3290]
    c = p.decode_cells(cells_frame(cells))
    assert c.cell_count == 16
    assert c.cells[13] == 3.268 and c.cell_max == 3.290
    assert c.voltage == 52.336 and c.current == -12.5 and c.power == round(52.336 * -12.5, 1)
    assert c.soc == 65 and c.full_ah == 314.0 and c.cycles == 12
    assert c.temps[0] == 16.9 and c.temps[1] == 17.3 and c.temps[2] is None  # T3 not present
    assert c.mos_temp == 21.5
    assert c.alarms == ["change_password"] and c.problems == []


def test_ack_attributes_frames_and_master():
    r, a = p.FrameReader(), p.Attributor()
    stream = (
        cells_frame([3300] * 16) + ack(0)  # master's own data
        + p.build_request(1, p.REG_CELLS) + cells_frame([3200] * 16) + ack(1)
        + p.build_request(2, p.REG_CELLS) + cells_frame([3100] * 16) + ack(2)
    )
    got = []
    for chunk in (stream[i : i + 37] for i in range(0, len(stream), 37)):  # arrives in odd pieces
        for tok in r.feed(chunk):
            got += a.push(tok)
    assert [(addr, p.decode_cells(f.raw).cells[0]) for addr, f in got] == [(0, 3.3), (1, 3.2), (2, 3.1)]
    assert a.master_seen
    assert a.requests_seen == {1, 2}


def test_garbage_never_creates_addresses():
    r, a = p.FrameReader(), p.Attributor()
    noise = bytes([0x55, 0xE5, 0x10, 0x16, 0x20, 0xAA, 0x01, 0x10, 0x16, 0x20, 0x00, 0x01, 0x99, 0x99]) * 20
    broken = bytearray(cells_frame([3300] * 16))
    broken[100] ^= 0xFF  # checksum now wrong
    got = []
    for tok in r.feed(noise + bytes(broken) + ack(229) + noise):
        got += a.push(tok)
    got += a.flush()
    assert got == []
    assert r.bad_checksum >= 1


def test_lost_ack_falls_back_to_request():
    r, a = p.FrameReader(), p.Attributor()
    got = []
    for tok in r.feed(p.build_request(3, p.REG_CELLS) + cells_frame([3333] * 16)):
        got += a.push(tok)
    got += a.flush()
    assert [addr for addr, _ in got] == [3]


def test_settings_frame_carries_its_own_address():
    r, a = p.FrameReader(), p.Attributor()
    got = []
    for tok in r.feed(settings_frame(2)):
        got += a.push(tok)
    got += a.flush()
    assert [addr for addr, _ in got] == [2]
    s = p.decode_settings(got[0][1].raw)
    assert s.cell_ovp == 3.65 and s.cell_count == 16 and s.design_capacity_ah == 314 and s.charge_switch


def test_ack_with_wrong_register_does_not_steal_frame():
    r, a = p.FrameReader(), p.Attributor()
    got = []
    for tok in r.feed(cells_frame([3300] * 16) + ack(5, p.REG_SETTINGS)):
        got += a.push(tok)
    got += a.flush()
    assert got == []
