"""1.2: extra settings, copy planning and the health tracker."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "custom_components" / "jk_bms_smart"))

import health as h  # noqa: E402
import protocol as p  # noqa: E402
from test_protocol import cells_frame, make_frame  # noqa: E402


def full_settings_frame() -> bytes:
    fields = {
        0: ("I", 3300), 4: ("I", 2600), 8: ("I", 2800), 12: ("I", 3650), 16: ("I", 3550), 48: ("I", 30), 52: ("I", 60),
        60: ("I", 300), 64: ("I", 60), 68: ("I", 5), 76: ("i", 550), 80: ("i", 500), 92: ("i", 20), 96: ("i", 50),
        100: ("i", 800), 104: ("i", 700), 108: ("I", 16), 128: ("I", 1500), 264: ("I", 1),
        276: ("H", 0b1_0001_0000),  # display always on + charging float mode
    }
    raw = bytearray(make_frame(1, fields))
    raw[6 + 268] = 5  # precharge seconds
    raw[-1] = sum(raw[:-1]) & 0xFF
    return bytes(raw)


def test_decode_extra_settings():
    s = p.decode_settings(full_settings_frame())
    assert s.smart_sleep_voltage == 3.3
    assert s.charge_ocp_delay == 30 and s.discharge_ocp_delay == 300 and s.scp_recovery == 5
    assert s.charge_otpr == 50 and s.charge_utpr == 5 and s.mos_otpr == 70
    assert s.discharge_otpr is None  # not reported -> hidden, not 0 °C
    assert s.scp_delay_us == 1500 and s.precharge_s == 5
    assert s.flags["display_always_on"] and s.flags["timed_stored_data"] and not s.flags["heating"]


def test_write_new_registers():
    assert p.build_write(1, "charge_ocp_delay", 30)[2:4] == b"\x10\x30"
    assert p.build_write(1, "smart_sleep_voltage", 3.3)[2:4] == b"\x10\x00"
    assert p.build_write(1, "charge_utpr", -2)[7:11] == struct.pack(">i", -20)
    assert p.check_settings({"charge_ot": 55, "charge_otpr": 50}, "charge_otpr", 56) is not None
    # an unrelated write is never blocked by a newer pair the firmware may report oddly
    assert p.check_settings({"charge_ut": 5, "charge_utpr": 2}, "cell_ovp", 3.6) is None


def test_plan_orders_writes_safely():
    current = {"cell_ovp": 3.65, "cell_ovpr": 3.55, "cell_uvp": 2.6, "cell_uvpr": 2.8, "charge_voltage": 3.5}
    wanted = {"cell_ovp": 3.50, "cell_ovpr": 3.40, "charge_voltage": 3.45, "cell_uvp": 2.6}
    plan = p.plan_changes(current, wanted)
    keys = [k for k, _, _ in plan]
    assert set(keys) == {"cell_ovp", "cell_ovpr", "charge_voltage"}
    # lowering: recovery and charge voltage must go down before the protection itself
    assert keys.index("cell_ovpr") < keys.index("cell_ovp")
    assert keys.index("charge_voltage") < keys.index("cell_ovp")
    # equal within the BMS resolution -> nothing to do
    assert p.plan_changes({"cell_ovp": 3.65}, {"cell_ovp": 3.6500001}) == []


def test_weak_cell_and_days():
    t = h.HealthTracker()
    low = [3200] * 16
    low[6] = 3150  # cell 7 is low at the bottom
    frame = p.decode_cells(cells_frame(low, ma=-20000, soc=20))
    for _ in range(200):
        t.sample(0, frame, "2026-11-09", 5)
    w = t.weak_cell(0)
    assert w["weakest"] == 7 and w["weakest_share"] == 100
    day = t.today(0, "2026-11-09")
    assert day["delta_max_mv"] == 50 and day["lowest_cell"] == 7 and day["ah_out"] > 5
    t2 = h.HealthTracker(t.as_store())
    assert t2.weak_cell(0)["weakest"] == 7
    t2.reset(0)
    assert t2.weak_cell(0)["weakest"] is None
