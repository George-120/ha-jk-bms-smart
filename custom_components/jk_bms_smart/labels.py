"""Names of the BMS settings in English, Dutch and German.

Used for messages, Repairs and backups, and by tools/gen_translations.py for the number entities.
"""

from __future__ import annotations

SETTING_LABELS: dict[str, tuple[str, str, str]] = {
    "cell_ovp": ("Cell overvoltage protection", "Cel-overspanningsbeveiliging", "Zellüberspannungsschutz"),
    "cell_ovpr": ("Cell overvoltage recovery", "Cel-overspanning herstel", "Zellüberspannung Rückkehr"),
    "cell_uvp": ("Cell undervoltage protection", "Cel-onderspanningsbeveiliging", "Zellunterspannungsschutz"),
    "cell_uvpr": ("Cell undervoltage recovery", "Cel-onderspanning herstel", "Zellunterspannung Rückkehr"),
    "charge_voltage": ("Charge voltage per cell", "Laadspanning per cel", "Ladespannung je Zelle"),
    "float_voltage": ("Float voltage per cell", "Druppelspanning per cel", "Erhaltungsspannung je Zelle"),
    "soc100_voltage": ("100 % at cell voltage", "100 % bij celspanning", "100 % bei Zellspannung"),
    "soc0_voltage": ("0 % at cell voltage", "0 % bij celspanning", "0 % bei Zellspannung"),
    "power_off_voltage": ("Power-off cell voltage", "Uitschakelspanning per cel", "Abschaltspannung je Zelle"),
    "balance_start": ("Balance from cell voltage", "Balanceren vanaf celspanning", "Balancieren ab Zellspannung"),
    "balance_trigger": ("Balance trigger difference", "Balanceren vanaf verschil", "Balancieren ab Differenz"),
    "max_balance_current": ("Max balance current", "Max. balanceerstroom", "Max. Balancierstrom"),
    "max_charge_current": ("Max charge current", "Max. laadstroom", "Max. Ladestrom"),
    "max_discharge_current": ("Max discharge current", "Max. ontlaadstroom", "Max. Entladestrom"),
    "design_capacity_ah": ("Battery capacity", "Accucapaciteit", "Akkukapazität"),
    "charge_ot": ("Charge over-temperature", "Laden te warm", "Laden zu warm"),
    "discharge_ot": ("Discharge over-temperature", "Ontladen te warm", "Entladen zu warm"),
    "charge_ut": ("Charge under-temperature", "Laden te koud", "Laden zu kalt"),
    "mos_ot": ("MOS over-temperature", "MOS te warm", "MOS zu warm"),
    "charge_otpr": ("Charge over-temperature recovery", "Laden te warm herstel", "Laden zu warm Rückkehr"),
    "discharge_otpr": ("Discharge over-temperature recovery", "Ontladen te warm herstel", "Entladen zu warm Rückkehr"),
    "charge_utpr": ("Charge under-temperature recovery", "Laden te koud herstel", "Laden zu kalt Rückkehr"),
    "mos_otpr": ("MOS over-temperature recovery", "MOS te warm herstel", "MOS zu warm Rückkehr"),
    "charge_ocp_delay": ("Charge overcurrent delay", "Laadstroom te hoog vertraging", "Ladeüberstrom Verzögerung"),
    "charge_ocp_recovery": ("Charge overcurrent recovery time", "Laadstroom te hoog hersteltijd", "Ladeüberstrom Rückkehrzeit"),
    "discharge_ocp_delay": ("Discharge overcurrent delay", "Ontlaadstroom te hoog vertraging", "Entladeüberstrom Verzögerung"),
    "discharge_ocp_recovery": ("Discharge overcurrent recovery time", "Ontlaadstroom te hoog hersteltijd", "Entladeüberstrom Rückkehrzeit"),
    "scp_recovery": ("Short-circuit recovery time", "Kortsluiting hersteltijd", "Kurzschluss Rückkehrzeit"),
    "smart_sleep_voltage": ("Smart sleep voltage", "Slaapspanning", "Ruhespannung (Smart Sleep)"),
    "charge_switch": ("Charging", "Laden", "Laden"),
    "discharge_switch": ("Discharging", "Ontladen", "Entladen"),
    "balance_switch": ("Balancer", "Balanceren", "Balancer"),
}

_IDX = {"en": 0, "nl": 1, "de": 2}


def label(key: str, lang: str) -> str:
    names = SETTING_LABELS.get(key)
    if not names:
        return key
    return names[_IDX.get(lang.split("-")[0], 0)]
