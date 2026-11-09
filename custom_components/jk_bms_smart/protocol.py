"""JK inverter BMS (PB series) RS485 protocol: framing, attribution and decoding.

Pure Python, no Home Assistant imports, so it can be unit tested.

Bus facts (JK "BMS RS485 Modbus V1.0/V1.1", firmware 15+/19.x):
- 115200 baud, 8N1, half duplex.
- A data request is a Modbus *write single register block* (function 0x10) to
  0x1620 (live data), 0x161E (settings) or 0x161C (device info) with value 0:
      AA 10 16 20 00 01 02 00 00 CRC
- The BMS answers with a 300 byte frame ``55 AA EB 90 <type> <counter> ... <sum>``
  (type 2 = live data, 1 = settings, 3 = device info) followed by the Modbus
  acknowledgement ``AA 10 16 20 00 01 CRC``.
- The 300 byte frame itself carries no address. The acknowledgement that follows
  it does (with a CRC), and the settings frame repeats the address at offset 264.
  Attributing frames this way is what keeps ghost devices out.
- A BMS with DIP address 0 is the bus master: it sends its own frames (followed
  by an acknowledgement with address 0) and polls addresses 1..15 itself. Another
  master on the same bus would collide, so in that case we only listen.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

HEADER = b"\x55\xaa\xeb\x90"
FRAME_LEN = 300

TYPE_SETTINGS = 1
TYPE_CELLS = 2
TYPE_INFO = 3

REG_INFO = 0x161C
REG_SETTINGS = 0x161E
REG_CELLS = 0x1620

REG_FOR_TYPE = {TYPE_CELLS: REG_CELLS, TYPE_SETTINGS: REG_SETTINGS, TYPE_INFO: REG_INFO}
TYPE_FOR_REG = {v: k for k, v in REG_FOR_TYPE.items()}

MAX_ADDRESS = 15  # DIP switches: 0..15

# Alarm bits of the live-data frame (offset 160). Bit 19 only asks to change the
# default Bluetooth password; it is not a battery problem.
ALARMS: list[str] = [
    "wire_resistance",  # 0
    "mos_overtemperature",  # 1
    "cell_quantity",  # 2
    "current_sensor",  # 3
    "cell_overvoltage",  # 4
    "battery_overvoltage",  # 5
    "charge_overcurrent",  # 6
    "charge_short_circuit",  # 7
    "charge_overtemperature",  # 8
    "charge_undertemperature",  # 9
    "internal_communication",  # 10
    "cell_undervoltage",  # 11
    "battery_undervoltage",  # 12
    "discharge_overcurrent",  # 13
    "discharge_short_circuit",  # 14
    "discharge_overtemperature",  # 15
    "charge_mos",  # 16
    "discharge_mos",  # 17
    "gps_disconnected",  # 18
    "change_password",  # 19
    "discharge_on_failed",  # 20
    "battery_overtemperature",  # 21
    "temperature_sensor",  # 22
    "parallel_module",  # 23
]
INFO_ONLY_ALARMS = {"change_password", "gps_disconnected"}

BALANCE_STATES = {0: "off", 1: "charging", 2: "discharging"}


def crc16(data: bytes) -> int:
    """Modbus CRC16 (poly 0xA001, init 0xFFFF)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def with_crc(data: bytes) -> bytes:
    return data + struct.pack("<H", crc16(data))


def build_request(address: int, register: int) -> bytes:
    """``AA 10 RR RR 00 01 02 00 00 CRC``: ask one BMS for one frame type."""
    return with_crc(struct.pack(">BBHHBH", address, 0x10, register, 1, 2, 0))


@dataclass(frozen=True, slots=True)
class Writable:
    """A setting that can be changed. The Modbus register is 0x1000 + the byte offset in the
    settings frame; the value is a 32-bit big-endian integer (JK Modbus V1.1, PB series)."""

    offset: int
    scale: float  # raw = value * scale
    minimum: float
    maximum: float
    signed: bool = False

    @property
    def register(self) -> int:
        return 0x1000 + self.offset


# key -> where it lives. Limits are what the JK app allows for LiFePO4/NMC/LTO; the BMS checks too.
WRITABLE: dict[str, Writable] = {
    "charge_switch": Writable(112, 1, 0, 1),
    "discharge_switch": Writable(116, 1, 0, 1),
    "balance_switch": Writable(120, 1, 0, 1),
    "cell_ovp": Writable(12, 1000, 1.2, 4.35),
    "cell_ovpr": Writable(16, 1000, 1.2, 4.35),
    "cell_uvp": Writable(4, 1000, 1.2, 4.35),
    "cell_uvpr": Writable(8, 1000, 1.2, 4.35),
    "charge_voltage": Writable(32, 1000, 1.2, 4.35),
    "float_voltage": Writable(36, 1000, 1.2, 4.35),
    "soc100_voltage": Writable(24, 1000, 1.2, 4.35),
    "soc0_voltage": Writable(28, 1000, 1.2, 4.35),
    "power_off_voltage": Writable(40, 1000, 1.2, 4.35),
    "balance_trigger": Writable(20, 1000, 0.002, 1.0),
    "balance_start": Writable(132, 1000, 1.2, 4.35),
    "max_balance_current": Writable(72, 1000, 0.3, 2.0),
    "max_charge_current": Writable(44, 1000, 1, 300),
    "max_discharge_current": Writable(56, 1000, 1, 300),
    "design_capacity_ah": Writable(124, 1000, 1, 2000),
    "charge_ot": Writable(76, 10, 30, 80, signed=True),
    "discharge_ot": Writable(84, 10, 30, 80, signed=True),
    "charge_ut": Writable(92, 10, -30, 20, signed=True),
    "mos_ot": Writable(100, 10, 50, 100, signed=True),
    # 1.2: recovery temperatures, protection delays and the smart-sleep voltage
    # (same register scheme; offsets as in the settings frame, see decode_settings)
    "charge_otpr": Writable(80, 10, 20, 80, signed=True),
    "discharge_otpr": Writable(88, 10, 20, 80, signed=True),
    "charge_utpr": Writable(96, 10, -25, 25, signed=True),
    "mos_otpr": Writable(104, 10, 30, 100, signed=True),
    "charge_ocp_delay": Writable(48, 1, 2, 600),
    "charge_ocp_recovery": Writable(52, 1, 2, 600),
    "discharge_ocp_delay": Writable(60, 1, 2, 600),
    "discharge_ocp_recovery": Writable(64, 1, 2, 600),
    "scp_recovery": Writable(68, 1, 2, 600),
    "smart_sleep_voltage": Writable(0, 1000, 1.2, 4.35),
}

# Settings that should be the same on every pack of one bank (switches and the
# capacity can legitimately differ, so they are left out of the comparison).
COMPARE_KEYS: tuple[str, ...] = tuple(k for k in WRITABLE if not k.endswith("_switch") and k != "design_capacity_ah")

# Write order when several settings change at once (copy / restore): limits that
# open the window first, so every single write passes check_settings on the way.
APPLY_ORDER: tuple[str, ...] = (
    "cell_ovp", "cell_uvp", "cell_ovpr", "cell_uvpr", "charge_voltage", "float_voltage",
    "soc100_voltage", "soc0_voltage", "power_off_voltage", "balance_start", "balance_trigger",
    "max_balance_current", "max_charge_current", "max_discharge_current", "design_capacity_ah",
    "charge_ot", "discharge_ot", "mos_ot", "charge_ut", "charge_otpr", "discharge_otpr", "mos_otpr", "charge_utpr",
    "charge_ocp_delay", "charge_ocp_recovery", "discharge_ocp_delay", "discharge_ocp_recovery", "scp_recovery",
    "smart_sleep_voltage", "balance_switch", "charge_switch", "discharge_switch",
)


def build_write(address: int, key: str, value: float) -> bytes:
    """``AA 10 10 xx 00 02 04 <int32 BE> CRC``."""
    w = WRITABLE[key]
    if not w.minimum <= value <= w.maximum:
        raise ValueError(f"{key}={value} outside {w.minimum}..{w.maximum}")
    raw = round(value * w.scale)
    payload = struct.pack(">i" if w.signed else ">I", raw)
    return with_crc(struct.pack(">BBHHB", address, 0x10, w.register, 2, 4) + payload)


def check_settings(current: dict[str, Any], key: str, value: float) -> str | None:
    """Refuse combinations that would trip the pack immediately. Returns a reason or None."""
    s = {**current, key: value}
    order = [("cell_uvp", "cell_uvpr"), ("cell_uvpr", "cell_ovpr"), ("cell_ovpr", "cell_ovp"),
             ("soc0_voltage", "soc100_voltage"), ("charge_voltage", "cell_ovp"), ("power_off_voltage", "cell_uvp"),
             ("charge_otpr", "charge_ot"), ("discharge_otpr", "discharge_ot"), ("mos_otpr", "mos_ot"),
             ("charge_ut", "charge_utpr")]
    for low, high in order:
        if (low in OPTIONAL_KEYS or high in OPTIONAL_KEYS) and key not in (low, high):
            continue  # newer pairs: only checked when one of them is being written
        if low in s and high in s and s[low] is not None and s[high] is not None and not s[low] < s[high]:
            return f"{low} must be below {high}"
    return None


# Fields older firmware may not fill in (raw 0 = not reported): shown only when present.
OPTIONAL_KEYS = frozenset({
    "charge_otpr", "discharge_otpr", "mos_otpr", "charge_utpr", "charge_ocp_delay", "charge_ocp_recovery",
    "discharge_ocp_delay", "discharge_ocp_recovery", "scp_recovery", "smart_sleep_voltage",
})


def plan_changes(current: dict[str, Any], wanted: dict[str, Any], keys: list[str] | tuple[str, ...] | None = None) -> list[tuple[str, Any, Any]]:
    """What to write to go from ``current`` to ``wanted``: [(key, old, new)] in a safe order.

    Keys missing on either side, and values that are equal (within the BMS resolution), are skipped.
    """
    out = []
    for key in APPLY_ORDER:
        if keys is not None and key not in keys:
            continue
        if key not in WRITABLE or wanted.get(key) is None or current.get(key) is None:
            continue
        new, old = wanted[key], current[key]
        if key.endswith("_switch"):
            if bool(new) != bool(old):
                out.append((key, bool(old), bool(new)))
            continue
        w = WRITABLE[key]
        if round(float(new) * w.scale) != round(float(old) * w.scale):
            out.append((key, old, new))
    return order_changes(current, out)


def order_changes(current: dict[str, Any], changes: list[tuple[str, Any, Any]]) -> list[tuple[str, Any, Any]]:
    """Sort changes so that every single write is valid on its own (e.g. lower OVPR before OVP).

    Changes that can never pass stay at the end, so the BMS write reports why.
    """
    state = dict(current)
    todo = list(changes)
    out: list[tuple[str, Any, Any]] = []
    while todo:
        for i, (key, _old, new) in enumerate(todo):
            if check_settings(state, key, new) is None:
                out.append(todo.pop(i))
                state[key] = new
                break
        else:
            out.extend(todo)
            break
    return out


def _crc_ok(frame: bytes) -> bool:
    return len(frame) >= 4 and crc16(frame[:-2]) == struct.unpack_from("<H", frame, len(frame) - 2)[0]


# ---------------------------------------------------------------- tokens


@dataclass(slots=True)
class DataFrame:
    """A checksummed 300 byte frame (no address yet)."""

    type: int
    raw: bytes


@dataclass(slots=True)
class ModbusRequest:
    """``AA 10 16 xx 00 01 02 00 00 CRC`` — someone asks BMS ``address``."""

    address: int
    register: int


@dataclass(slots=True)
class ModbusAck:
    """``AA 10 16 xx 00 01 CRC`` — BMS ``address`` confirms it just answered."""

    address: int
    register: int


@dataclass(slots=True)
class ModbusWrite:
    """``AA 10 10 xx 00 02 04 <value> CRC`` — someone writes a setting of BMS ``address``."""

    address: int
    register: int
    data: bytes


@dataclass(slots=True)
class ModbusError:
    """``AA 90 <code> CRC`` — the BMS refused a request (3 = value not allowed)."""

    address: int
    code: int


Token = DataFrame | ModbusRequest | ModbusAck | ModbusWrite | ModbusError


class FrameReader:
    """Turns a raw byte stream into tokens. Anything that fails a checksum is dropped."""

    def __init__(self) -> None:
        self._buf = bytearray()
        self.bytes_in = 0
        self.dropped = 0
        self.frames = 0
        self.bad_checksum = 0

    def feed(self, data: bytes) -> list[Token]:
        self.bytes_in += len(data)
        self._buf.extend(data)
        out: list[Token] = []
        while True:
            token, consumed = self._next()
            if consumed == 0:
                break
            del self._buf[:consumed]
            if token is not None:
                out.append(token)
        # never let a stuck buffer grow without bound
        if len(self._buf) > 4 * FRAME_LEN:
            self.dropped += len(self._buf) - FRAME_LEN
            del self._buf[:-FRAME_LEN]
        return out

    def flush(self) -> None:
        """Called after a silent gap: whatever is left is an incomplete fragment."""
        self.dropped += len(self._buf)
        self._buf.clear()

    def _next(self) -> tuple[Token | None, int]:
        buf = self._buf
        n = len(buf)
        if n < 5:
            return None, 0
        if n < 8 and not (buf[1] in (0x90, 0x83) and _crc_ok(bytes(buf[:5]))):
            return None, 0
        if buf[0:4] == HEADER:
            if n < FRAME_LEN:
                return None, 0
            frame = bytes(buf[:FRAME_LEN])
            if sum(frame[:-1]) & 0xFF == frame[-1] and frame[4] in (1, 2, 3):
                self.frames += 1
                return DataFrame(frame[4], frame), FRAME_LEN
            self.bad_checksum += 1
            return None, 1
        addr, func = buf[0], buf[1]
        if addr <= 0xF7 and func in (0x90, 0x83) and _crc_ok(bytes(buf[:5])):
            return ModbusError(addr, buf[2]), 5
        if addr <= 0xF7 and func == 0x10 and buf[2] in (0x10, 0x11, 0x14, 0x15, 0x16):
            reg = (buf[2] << 8) | buf[3]
            # write request (9 + byte count) or acknowledgement (8 bytes)
            req_len = 9 + buf[6]
            if buf[6] in (2, 4) and n >= req_len and _crc_ok(bytes(buf[:req_len])):
                if buf[2] == 0x16:
                    return ModbusRequest(addr, reg), req_len
                return ModbusWrite(addr, reg, bytes(buf[7 : 7 + buf[6]])), req_len
            if _crc_ok(bytes(buf[:8])):
                return ModbusAck(addr, reg), 8
            if n < 13:
                return None, 0  # wait for the rest of a possible request
        # not the start of anything we know: skip to the next header or byte
        nxt = buf.find(HEADER, 1)
        skip = nxt if nxt > 0 and nxt < 8 else 1
        self.dropped += skip
        return None, skip


class Attributor:
    """Links data frames to BMS addresses.

    Order on the wire: [request AA ...] -> 300 byte frame -> ack AA. The ack (CRC
    checked) decides. If the ack is lost we fall back to the last request for the
    same frame type, and settings frames carry their own address as a check.
    """

    def __init__(self) -> None:
        self._pending: DataFrame | None = None
        self._last_request: ModbusRequest | None = None
        self.master_seen = False
        self.requests_seen: set[int] = set()

    def push(self, token: Token, *, ours: bool = False) -> list[tuple[int, DataFrame]]:
        out: list[tuple[int, DataFrame]] = []
        if isinstance(token, ModbusRequest):
            out.extend(self._resolve_pending_by_request())
            self._last_request = token
            if not ours:
                self.requests_seen.add(token.address)
        elif isinstance(token, DataFrame):
            out.extend(self._resolve_pending_by_request())
            self._pending = token
        elif isinstance(token, ModbusAck):
            if self._pending is not None and TYPE_FOR_REG.get(token.register) == self._pending.type:
                out.append((token.address, self._pending))
                self._pending = None
                if token.address == 0:
                    self.master_seen = True
            if self._last_request and self._last_request.address == token.address:
                self._last_request = None
        return out

    def flush(self) -> list[tuple[int, DataFrame]]:
        """Bus went quiet: resolve a frame whose ack never came."""
        return self._resolve_pending_by_request()

    def _resolve_pending_by_request(self) -> list[tuple[int, DataFrame]]:
        frame, self._pending = self._pending, None
        if frame is None:
            return []
        if frame.type == TYPE_SETTINGS:
            addr = struct.unpack_from("<I", frame.raw, 6 + 264)[0]
            if addr <= MAX_ADDRESS:
                return [(addr, frame)]
        req = self._last_request
        if req is not None and TYPE_FOR_REG.get(req.register) == frame.type:
            self._last_request = None
            return [(req.address, frame)]
        return []  # unknown sender: dropped, never a new device


# ---------------------------------------------------------------- decoding


def _u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, 6 + o)[0]


def _i16(b: bytes, o: int) -> int:
    return struct.unpack_from("<h", b, 6 + o)[0]


def _u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, 6 + o)[0]


def _i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, 6 + o)[0]


def _u8(b: bytes, o: int) -> int:
    return b[6 + o]


def _text(b: bytes, start: int, length: int) -> str:
    raw = b[start : start + length].split(b"\x00", 1)[0]
    return raw.decode("ascii", "ignore").strip()


def _temp(raw: int) -> float | None:
    # -2000 / 0x8000 style values mean "no sensor"
    if raw <= -1000 or raw >= 2000:
        return None
    return raw / 10


@dataclass
class CellData:
    cells: list[float]
    resistances: list[float]
    cell_count: int
    voltage: float
    current: float
    power: float
    soc: int
    soh: int
    remaining_ah: float
    full_ah: float
    cycles: int
    cycle_ah: float
    cell_avg: float
    cell_delta: float
    cell_max_index: int
    cell_min_index: int
    mos_temp: float | None
    temps: list[float | None]
    alarm_bits: int
    alarms: list[str]
    balance_current: float
    balance_state: str
    charging_enabled: bool
    discharging_enabled: bool
    precharge: bool
    heating: bool
    heater_current: float
    charger_plugged: bool
    runtime_s: int
    wire_alarm_bits: int
    raw_counter: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def cell_min(self) -> float:
        return min(self.cells) if self.cells else 0.0

    @property
    def cell_max(self) -> float:
        return max(self.cells) if self.cells else 0.0

    @property
    def problems(self) -> list[str]:
        return [a for a in self.alarms if a not in INFO_ONLY_ALARMS]


def decode_cells(b: bytes) -> CellData:
    mask = _u32(b, 64)
    count = bin(mask).count("1") or 16
    count = min(count, 32)
    cells = [_u16(b, 2 * i) / 1000 for i in range(count)]
    res = [_u16(b, 74 + 2 * i) / 1000 for i in range(count)]
    alarm_bits = _u32(b, 160)
    alarms = [name for bit, name in enumerate(ALARMS) if alarm_bits >> bit & 1]
    present = _u8(b, 208)  # bit0 MOS, bit1..5 battery sensors 1..5 (1 = present)
    raw_temps = [_i16(b, 156), _i16(b, 158), _i16(b, 248), _i16(b, 250), _i16(b, 252)]
    temps = [
        _temp(raw) if present == 0 or present >> (i + 1) & 1 else None
        for i, raw in enumerate(raw_temps)
    ]
    voltage = _u32(b, 144) / 1000
    current = _i32(b, 152) / 1000
    mos = _temp(_i16(b, 138)) if present == 0 or present & 1 else None
    return CellData(
        cells=cells,
        resistances=res,
        cell_count=count,
        voltage=voltage,
        current=current,
        power=round(voltage * current, 1),
        soc=_u8(b, 167),
        soh=_u8(b, 184),
        remaining_ah=_i32(b, 168) / 1000,
        full_ah=_u32(b, 172) / 1000,
        cycles=_u32(b, 176),
        cycle_ah=_u32(b, 180) / 1000,
        cell_avg=_u16(b, 68) / 1000,
        cell_delta=_u16(b, 70) / 1000,
        cell_max_index=_u8(b, 72),
        cell_min_index=_u8(b, 73),
        mos_temp=mos,
        temps=temps,
        alarm_bits=alarm_bits,
        alarms=alarms,
        balance_current=_i16(b, 164) / 1000,
        balance_state=BALANCE_STATES.get(_u8(b, 166), "off"),
        charging_enabled=bool(_u8(b, 192)),
        discharging_enabled=bool(_u8(b, 193)),
        precharge=bool(_u8(b, 185)),
        heating=bool(_u8(b, 209)),
        heater_current=_i16(b, 230) / 1000,
        charger_plugged=bool(_u8(b, 239)),
        runtime_s=_u32(b, 188),
        wire_alarm_bits=_u32(b, 140),
        raw_counter=b[5],
    )


@dataclass
class Settings:
    address: int
    cell_count: int
    cell_uvp: float
    cell_uvpr: float
    cell_ovp: float
    cell_ovpr: float
    balance_trigger: float
    balance_start: float
    soc100_voltage: float
    soc0_voltage: float
    charge_voltage: float
    float_voltage: float
    power_off_voltage: float
    max_charge_current: float
    max_discharge_current: float
    max_balance_current: float
    design_capacity_ah: float
    charge_switch: bool
    discharge_switch: bool
    balance_switch: bool
    charge_ot: float
    discharge_ot: float
    charge_ut: float
    mos_ot: float
    heating_enabled: bool
    # 1.2: writable (None = not reported by this firmware)
    charge_otpr: float | None = None
    discharge_otpr: float | None = None
    charge_utpr: float | None = None
    mos_otpr: float | None = None
    charge_ocp_delay: float | None = None
    charge_ocp_recovery: float | None = None
    discharge_ocp_delay: float | None = None
    discharge_ocp_recovery: float | None = None
    scp_recovery: float | None = None
    smart_sleep_voltage: float | None = None
    # 1.2: read only
    scp_delay_us: int | None = None
    precharge_s: int | None = None
    smart_sleep_hours: int | None = None
    discharge_ut: int | None = None
    discharge_utpr: int | None = None
    flags: dict[str, bool] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


FLAG_BITS = {
    "heating": 0, "disable_temp_sensors": 1, "gps_heartbeat": 2, "port_rs485": 3, "display_always_on": 4,
    "special_charger": 5, "smart_sleep": 6, "disable_pcl_module": 7, "timed_stored_data": 8, "charging_float_mode": 9,
}


def _opt(raw: int, scale: float) -> float | None:
    return None if raw == 0 else raw / scale


def decode_settings(b: bytes) -> Settings:
    bits = _u16(b, 276)
    extra = dict(
        charge_otpr=_opt(_i32(b, 80), 10),
        discharge_otpr=_opt(_i32(b, 88), 10),
        charge_utpr=_opt(_i32(b, 96), 10),
        mos_otpr=_opt(_i32(b, 104), 10),
        charge_ocp_delay=_opt(_u32(b, 48), 1),
        charge_ocp_recovery=_opt(_u32(b, 52), 1),
        discharge_ocp_delay=_opt(_u32(b, 60), 1),
        discharge_ocp_recovery=_opt(_u32(b, 64), 1),
        scp_recovery=_opt(_u32(b, 68), 1),
        smart_sleep_voltage=_opt(_u32(b, 0), 1000),
        scp_delay_us=_u32(b, 128) or None,
        precharge_s=_u8(b, 268) or None,
        smart_sleep_hours=_u8(b, 280) or None,
        discharge_ut=struct.unpack_from("<b", b, 6 + 290)[0] or None,
        discharge_utpr=struct.unpack_from("<b", b, 6 + 291)[0] or None,
        flags={name: bool(bits >> bit & 1) for name, bit in FLAG_BITS.items()},
    )
    return Settings(
        **extra,
        address=_u32(b, 264),
        cell_count=_u32(b, 108),
        cell_uvp=_u32(b, 4) / 1000,
        cell_uvpr=_u32(b, 8) / 1000,
        cell_ovp=_u32(b, 12) / 1000,
        cell_ovpr=_u32(b, 16) / 1000,
        balance_trigger=_u32(b, 20) / 1000,
        balance_start=_u32(b, 132) / 1000,
        soc100_voltage=_u32(b, 24) / 1000,
        soc0_voltage=_u32(b, 28) / 1000,
        charge_voltage=_u32(b, 32) / 1000,
        float_voltage=_u32(b, 36) / 1000,
        power_off_voltage=_u32(b, 40) / 1000,
        max_charge_current=_u32(b, 44) / 1000,
        max_discharge_current=_u32(b, 56) / 1000,
        max_balance_current=_u32(b, 72) / 1000,
        design_capacity_ah=_u32(b, 124) / 1000,
        charge_switch=bool(_u32(b, 112)),
        discharge_switch=bool(_u32(b, 116)),
        balance_switch=bool(_u32(b, 120)),
        charge_ot=_i32(b, 76) / 10,
        discharge_ot=_i32(b, 84) / 10,
        charge_ut=_i32(b, 92) / 10,
        mos_ot=_i32(b, 100) / 10,
        heating_enabled=bool(bits & 1),
    )


@dataclass
class DeviceInfo:
    model: str
    hardware: str
    software: str
    uptime_s: int
    power_on_count: int
    name: str
    manufacturing_date: str
    serial: str

    def as_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def decode_info(b: bytes) -> DeviceInfo:
    # Offsets 62.. and 97.. 118.. hold passcodes: deliberately never read.
    date = _text(b, 78, 6)
    return DeviceInfo(
        model=_text(b, 6, 16),
        hardware=_text(b, 22, 8),
        software=_text(b, 30, 8),
        uptime_s=struct.unpack_from("<I", b, 38)[0],
        power_on_count=struct.unpack_from("<I", b, 42)[0],
        name=_text(b, 46, 16),
        manufacturing_date=f"20{date[:2]}-{date[2:4]}-{date[4:6]}" if len(date) == 6 and date.isdigit() else "",
        serial=_text(b, 86, 11),
    )
