"""Write strings.json and translations/{en,nl,de}.json from one table (run from the repo root)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "jk_bms_smart"

L = ("en", "nl", "de")


def t(en: str, nl: str, de: str) -> dict[str, str]:
    return {"en": en, "nl": nl, "de": de}


CONFIG = {
    "flow_title": t("{name}", "{name}", "{name}"),
    "step": {
        "user": {
            "title": t("Connect your JK BMS units", "Je JK BMS'en koppelen", "JK BMS verbinden"),
            "description": t(
                "How are the BMS units connected?\n\n**What you need:** a USB-RS485 adapter (preferably FTDI FT232R) or an RS485 network gateway, and a CAT5/6 cable cut open at one end: RJ45 **pin 1 = B (D−)**, **pin 2 = A (D+)**, **pin 3 = GND** (white-orange, orange, white-green).\n\n**Where:** the free **RS485-2** (parallel) socket on the communication board of the first or last pack — not CAN / RS485-1, that one goes to the inverter. Every pack needs its own DIP address.",
                "Hoe zitten de BMS'en aan Home Assistant?\n\n**Wat je nodig hebt:** een USB-RS485-adapter (liefst met FTDI FT232R-chip) of een RS485-netwerkgateway, en een netwerkkabel (CAT5/6) die je aan één kant doorknipt: RJ45 **pin 1 = B (D−)**, **pin 2 = A (D+)**, **pin 3 = GND** (wit-oranje, oranje, wit-groen).\n\n**Waar:** in de vrije **RS485-2**-bus (parallel) op de communicatieprint van het eerste of laatste pakket — niet in CAN / RS485-1, die gaat naar de omvormer. Elk pakket heeft een eigen DIP-adres.",
                "Wie sind die BMS verbunden?\n\n**Was du brauchst:** einen USB-RS485-Adapter (am besten FTDI FT232R) oder ein RS485-Netzwerk-Gateway und ein CAT5/6-Kabel, an einem Ende abgeschnitten: RJ45 **Pin 1 = B (D−)**, **Pin 2 = A (D+)**, **Pin 3 = GND** (weiß-orange, orange, weiß-grün).\n\n**Wo:** die freie **RS485-2**-Buchse (Parallel) auf der Kommunikationsplatine des ersten oder letzten Packs — nicht CAN / RS485-1, die geht zum Wechselrichter. Jedes Pack braucht eine eigene DIP-Adresse.",
            ),
            "menu_options": {
                "usb": t("USB-RS485 stick", "USB-RS485-stick", "USB-RS485-Stick"),
                "network": t("RS485 network gateway (Wi-Fi/Ethernet)", "RS485-netwerkgateway (wifi/ethernet)", "RS485-Netzwerk-Gateway (WLAN/Ethernet)"),
            },
        },
        "usb": {
            "title": t("Choose the USB stick", "Kies de USB-stick", "USB-Stick wählen"),
            "description": t(
                "Found {count} serial port(s); the most likely RS485 stick is on top. Not in the list? Choose … and type the path.\n\nThe port must be free: stop any add-on that uses it (e.g. a JK BMS add-on) first.",
                "{count} seriële poort(en) gevonden; de meest waarschijnlijke RS485-stick staat bovenaan. Staat hij er niet bij? Kies … en typ het pad.\n\nDe poort moet vrij zijn: zet een add-on die hem gebruikt (bijv. een JK BMS-add-on) eerst uit.",
                "{count} serielle(r) Port(s) gefunden; der wahrscheinlichste RS485-Stick steht oben. Nicht dabei? Wähle … und gib den Pfad ein.\n\nDer Port muss frei sein: stoppe zuerst ein Add-on, das ihn nutzt (z. B. ein JK-BMS-Add-on).",
            ),
            "data": {"device": t("Serial port", "Seriële poort", "Serieller Port"), "manual_path": t("Path (only for …)", "Pad (alleen bij …)", "Pfad (nur bei …)")},
        },
        "usb_confirm": {
            "title": t("RS485 stick found", "RS485-stick gevonden", "RS485-Stick gefunden"),
            "description": t(
                "A USB-RS485 stick was plugged in ({device}). Search it for JK BMS units?",
                "Er is een USB-RS485-stick aangesloten ({device}). Daarop zoeken naar JK BMS'en?",
                "Ein USB-RS485-Stick wurde angeschlossen ({device}). Darauf nach JK BMS suchen?",
            ),
        },
        "network": {
            "title": t("RS485 network gateway", "RS485-netwerkgateway", "RS485-Netzwerk-Gateway"),
            "description": t(
                "For converters such as Elfin EW11 or USR-TCP232 in transparent TCP server mode at 115200 baud, 8N1.",
                "Voor omzetters zoals Elfin EW11 of USR-TCP232 in transparante TCP-servermodus op 115200 baud, 8N1.",
                "Für Wandler wie Elfin EW11 oder USR-TCP232 im transparenten TCP-Server-Modus mit 115200 Baud, 8N1.",
            ),
            "data": {"host": t("IP address", "IP-adres", "IP-Adresse"), "port": t("TCP port", "TCP-poort", "TCP-Port")},
        },
        "found": {
            "title": t("{count} BMS unit(s) found", "{count} BMS('en) gevonden", "{count} BMS gefunden"),
            "description": t(
                "{units}\n\nBus mode: **{mode}** — *listen* means one BMS (address 0) is the master and Home Assistant only listens; *poll* means Home Assistant asks every BMS itself.\n\nGive the bank and each pack a name.",
                "{units}\n\nBusmodus: **{mode}** — *listen* betekent dat één BMS (adres 0) de master is en Home Assistant alleen meeluistert; *poll* betekent dat Home Assistant zelf elke BMS uitvraagt.\n\nGeef de accubank en elk pakket een naam.",
                "{units}\n\nBusmodus: **{mode}** — *listen* heißt, ein BMS (Adresse 0) ist Master und Home Assistant hört nur mit; *poll* heißt, Home Assistant fragt jedes BMS selbst ab.\n\nGib der Akkubank und jedem Pack einen Namen.",
            ),
            "data": {"title": t("Name of the battery bank", "Naam van de accubank", "Name der Akkubank")},
        },
        "failed": {
            "title": t("No JK BMS found yet", "Nog geen JK BMS gevonden", "Noch kein JK BMS gefunden"),
            "description": t(
                "Details: {detail}\n\nCheck: the adapter is in the **RS485-2** socket (not CAN / RS485-1), RJ45 pin 1 = B, 2 = A, 3 = GND (swap A and B if nothing comes in), and that no add-on uses the port. Tick the box to search again, untick to choose another port.",
                "Details: {detail}\n\nControleer: zit de adapter in de **RS485-2**-bus (niet CAN / RS485-1), RJ45 pin 1 = B, 2 = A, 3 = GND (A en B omwisselen als er niets binnenkomt) en of geen add-on de poort gebruikt. Vinkje aan = opnieuw zoeken, uit = andere poort kiezen.",
                "Details: {detail}\n\nPrüfe: steckt der Adapter in der **RS485-2**-Buchse (nicht CAN / RS485-1), RJ45 Pin 1 = B, 2 = A, 3 = GND (A und B tauschen, wenn nichts ankommt) und ob kein Add-on den Port nutzt. Haken = erneut suchen, ohne Haken = anderen Port wählen.",
            ),
            "data": {"retry": t("Search again on this port", "Opnieuw zoeken op deze poort", "Auf diesem Port erneut suchen")},
        },
    },
    "progress": {
        "probe": t(
            "Listening on the RS485 bus and looking for JK BMS units. This takes up to 40 seconds.",
            "Luisteren op de RS485-bus en zoeken naar JK BMS'en. Dit duurt tot 40 seconden.",
            "Höre am RS485-Bus mit und suche JK BMS. Das dauert bis zu 40 Sekunden.",
        )
    },
    "error": {
        "no_port": t("Choose a port or type a path.", "Kies een poort of typ een pad.", "Wähle einen Port oder gib einen Pfad ein."),
        "port_busy": t(
            "The port is in use by another program. Stop the add-on that uses it and try again.",
            "De poort is in gebruik door een ander programma. Zet de add-on die hem gebruikt uit en probeer opnieuw.",
            "Der Port wird von einem anderen Programm benutzt. Stoppe das Add-on und versuche es erneut.",
        ),
        "cannot_open": t("The port could not be opened.", "De poort kon niet worden geopend.", "Der Port konnte nicht geöffnet werden."),
        "no_bms": t(
            "No JK BMS answered on this port.", "Er antwoordde geen JK BMS op deze poort.", "Auf diesem Port hat kein JK BMS geantwortet."
        ),
        "unknown": t("Unexpected error, see the log.", "Onverwachte fout, zie het logboek.", "Unerwarteter Fehler, siehe Protokoll."),
    },
    "abort": {
        "already_configured": t("This port is already set up.", "Deze poort is al ingesteld.", "Dieser Port ist bereits eingerichtet."),
    },
}

OPTIONS = {
    "step": {
        "init": {
            "title": t("JK BMS Smart", "JK BMS Smart", "JK BMS Smart"),
            "menu_options": {
                "dashboard": t("Create dashboard", "Dashboard aanmaken", "Dashboard erstellen"),
                "names": t("Names of the packs", "Namen van de pakketten", "Namen der Packs"),
                "settings": t("Update interval", "Verversen", "Aktualisierung"),
                "rescan": t("Search for BMS units again", "Opnieuw zoeken naar BMS'en", "Erneut nach BMS suchen"),
            },
        },
        "settings": {
            "title": t("Update interval", "Verversen", "Aktualisierung"),
            "description": t(
                "The interval is only used when Home Assistant polls the BMS units itself; with a master BMS (address 0) the master sets the pace.\n\n**Allow changing BMS settings** adds switches (charge, discharge, balance) and the protection settings, and makes the settings card editable. Changes go straight into the BMS: only change what you understand. With a master BMS the integration sends a change in a quiet moment on the bus and checks that the BMS confirms it.",
                "Het interval geldt alleen als Home Assistant de BMS'en zelf uitvraagt; met een master-BMS (adres 0) bepaalt die het tempo.\n\n**Instellingen van de BMS mogen wijzigen** voegt schakelaars toe (laden, ontladen, balanceren) en de beveiligingsinstellingen, en maakt de instellingenkaart bewerkbaar. Wijzigingen gaan direct de BMS in: verander alleen wat je begrijpt. Met een master-BMS stuurt de integratie een wijziging in een stil moment op de bus en controleert dat de BMS hem bevestigt.",
                "Das Intervall gilt nur, wenn Home Assistant die BMS selbst abfragt; mit einem Master-BMS (Adresse 0) gibt dieses den Takt vor.\n\n**Ändern der BMS-Einstellungen erlauben** fügt Schalter (Laden, Entladen, Balancieren) und die Schutzeinstellungen hinzu und macht die Einstellungskarte bearbeitbar. Änderungen gehen direkt ins BMS: nur ändern, was du verstehst. Mit Master-BMS sendet die Integration eine Änderung in einer ruhigen Busphase und prüft die Bestätigung.",
            ),
            "data": {
                "poll_interval": t("Ask every … seconds", "Elke … seconden uitvragen", "Alle … Sekunden abfragen"),
                "stale_after": t("Show as offline after … seconds without data", "Offline tonen na … seconden zonder gegevens", "Nach … Sekunden ohne Daten als offline zeigen"),
                "allow_changes": t("Allow changing BMS settings", "Instellingen van de BMS mogen wijzigen", "Ändern der BMS-Einstellungen erlauben"),
            },
        },
        "names": {
            "title": t("Names of the packs", "Namen van de pakketten", "Namen der Packs"),
            "description": t("Packs on RS485 addresses {units}.", "Pakketten op RS485-adres {units}.", "Packs auf RS485-Adresse {units}."),
        },
        "rescan": {
            "title": t("Search again", "Opnieuw zoeken", "Erneut suchen"),
            "description": t(
                "Pauses reading for up to 40 seconds and searches the bus. Use this after adding a pack or changing a DIP address. Packs that are not found stay, so a pack that is switched off is not lost.",
                "Pauzeert het uitlezen tot 40 seconden en doorzoekt de bus. Gebruik dit na het toevoegen van een pakket of het wijzigen van een DIP-adres. Niet gevonden pakketten blijven staan, zodat een uitgeschakeld pakket niet verdwijnt.",
                "Pausiert das Auslesen bis zu 40 Sekunden und durchsucht den Bus. Nach dem Hinzufügen eines Packs oder Ändern einer DIP-Adresse nutzen. Nicht gefundene Packs bleiben erhalten.",
            ),
        },
        "rescan_done": {
            "title": t("Search finished", "Zoeken klaar", "Suche beendet"),
            "description": t(
                "Found: {found}\nNew: {new}\n{error}\n\nSubmit to save.",
                "Gevonden: {found}\nNieuw: {new}\n{error}\n\nOpslaan om over te nemen.",
                "Gefunden: {found}\nNeu: {new}\n{error}\n\nZum Übernehmen absenden.",
            ),
        },
        "dashboard": {
            "title": t("Create dashboard", "Dashboard aanmaken", "Dashboard erstellen"),
            "description": t(
                "Adds a dashboard \"Home battery\" to the sidebar with the battery bank and every pack with its cells. Your own dashboards are never changed. Press again later to refresh it. {error}",
                "Voegt een dashboard \"Thuisaccu\" toe aan de zijbalk met de accubank en elk pakket met zijn cellen. Je eigen dashboards worden nooit aangepast. Later nog eens drukken ververst het. {error}",
                "Fügt der Seitenleiste ein Dashboard \"Heimspeicher\" mit der Akkubank und jedem Pack mit seinen Zellen hinzu. Eigene Dashboards werden nie geändert. Später erneut drücken aktualisiert es. {error}",
            ),
        },
    },
    "progress": CONFIG["progress"],
    "error": {
        "not_admin": t("Only administrators can do this.", "Alleen beheerders kunnen dit.", "Nur Administratoren können das."),
        "dashboard_failed": t("Could not create the dashboard.", "Dashboard aanmaken lukte niet.", "Dashboard konnte nicht erstellt werden."),
    },
    "abort": {
        "dashboard_created": t(
            "Dashboard ready: open {url} or find \"Home battery\" in the sidebar.",
            "Dashboard klaar: open {url} of kies \"Thuisaccu\" in de zijbalk.",
            "Dashboard fertig: öffne {url} oder wähle \"Heimspeicher\" in der Seitenleiste.",
        )
    },
}

SENSORS = {
    "soc": t("State of charge", "Laadtoestand", "Ladezustand"),
    "voltage": t("Voltage", "Spanning", "Spannung"),
    "current": t("Current", "Stroom", "Strom"),
    "power": t("Power", "Vermogen", "Leistung"),
    "remaining_capacity": t("Remaining capacity", "Resterende capaciteit", "Restkapazität"),
    "full_capacity": t("Full capacity", "Volle capaciteit", "Volle Kapazität"),
    "stored_energy": t("Stored energy", "Opgeslagen energie", "Gespeicherte Energie"),
    "soh": t("State of health", "Gezondheid", "Gesundheitszustand"),
    "cycles": t("Cycles", "Cycli", "Zyklen"),
    "cycle_capacity": t("Total cycled capacity", "Totaal gecycleerde capaciteit", "Gesamte Zykluskapazität"),
    "cell_min": t("Lowest cell voltage", "Laagste celspanning", "Niedrigste Zellspannung"),
    "cell_max": t("Highest cell voltage", "Hoogste celspanning", "Höchste Zellspannung"),
    "cell_avg": t("Average cell voltage", "Gemiddelde celspanning", "Mittlere Zellspannung"),
    "cell_delta": t("Cell voltage difference", "Celspanningsverschil", "Zellspannungsdifferenz"),
    "cell_min_number": t("Lowest cell", "Laagste cel", "Niedrigste Zelle"),
    "cell_max_number": t("Highest cell", "Hoogste cel", "Höchste Zelle"),
    "mos_temperature": t("MOS temperature", "MOS-temperatuur", "MOS-Temperatur"),
    "balance_current": t("Balance current", "Balanceerstroom", "Balancierstrom"),
    "balance_state": t("Balancer", "Balancer", "Balancer"),
    "problems": t("Active alarms", "Actieve alarmen", "Aktive Alarme"),
    "energy_charged": t("Energy charged", "Energie geladen", "Energie geladen"),
    "energy_discharged": t("Energy discharged", "Energie ontladen", "Energie entladen"),
    "runtime": t("Running time", "Draaitijd", "Laufzeit"),
    "heater_current": t("Heater current", "Verwarmingsstroom", "Heizstrom"),
    "design_capacity": t("Design capacity", "Ontwerpcapaciteit", "Nennkapazität"),
    "cell_ovp": t("Cell overvoltage protection", "Cel-overspanningsbeveiliging", "Zellüberspannungsschutz"),
    "cell_uvp": t("Cell undervoltage protection", "Cel-onderspanningsbeveiliging", "Zellunterspannungsschutz"),
    "charge_voltage_setting": t("Charge voltage per cell", "Laadspanning per cel", "Ladespannung je Zelle"),
    "balance_trigger": t("Balance trigger difference", "Balanceren vanaf verschil", "Balancieren ab Differenz"),
    "max_charge_current": t("Max charge current", "Max. laadstroom", "Max. Ladestrom"),
    "max_discharge_current": t("Max discharge current", "Max. ontlaadstroom", "Max. Entladestrom"),
    "cell_voltage": t("Cell {cell}", "Cel {cell}", "Zelle {cell}"),
    "cell_resistance": t("Cell {cell} wire resistance", "Cel {cell} draadweerstand", "Zelle {cell} Leitungswiderstand"),
    "temperature": t("Temperature {sensor}", "Temperatuur {sensor}", "Temperatur {sensor}"),
    "bank_soc": t("State of charge", "Laadtoestand", "Ladezustand"),
    "bank_power": t("Power", "Vermogen", "Leistung"),
    "bank_current": t("Current", "Stroom", "Strom"),
    "bank_voltage": t("Voltage", "Spanning", "Spannung"),
    "bank_stored_energy": t("Stored energy", "Opgeslagen energie", "Gespeicherte Energie"),
    "bank_capacity_energy": t("Capacity", "Capaciteit", "Kapazität"),
    "bank_remaining_capacity": t("Remaining capacity", "Resterende capaciteit", "Restkapazität"),
    "bank_cell_min": t("Lowest cell voltage", "Laagste celspanning", "Niedrigste Zellspannung"),
    "bank_cell_max": t("Highest cell voltage", "Hoogste celspanning", "Höchste Zellspannung"),
    "bank_cell_delta": t("Cell voltage difference", "Celspanningsverschil", "Zellspannungsdifferenz"),
    "bank_temperature_max": t("Highest temperature", "Hoogste temperatuur", "Höchste Temperatur"),
    "bank_energy_charged": t("Energy charged", "Energie geladen", "Energie geladen"),
    "bank_energy_discharged": t("Energy discharged", "Energie ontladen", "Energie entladen"),
    "bank_units_online": t("Packs online", "Pakketten online", "Packs online"),
}
BALANCE_STATES = {
    "off": t("Idle", "Rust", "Ruhe"),
    "charging": t("Moving charge (charging)", "Verplaatst lading (laden)", "Verschiebt Ladung (Laden)"),
    "discharging": t("Moving charge (discharging)", "Verplaatst lading (ontladen)", "Verschiebt Ladung (Entladen)"),
}
BINARY = {
    "online": t("Connected", "Verbonden", "Verbunden"),
    "charging_enabled": t("Charging allowed", "Laden toegestaan", "Laden erlaubt"),
    "discharging_enabled": t("Discharging allowed", "Ontladen toegestaan", "Entladen erlaubt"),
    "balancing": t("Balancing", "Balanceren", "Balancieren"),
    "heating": t("Heating", "Verwarming", "Heizung"),
    "charger_plugged": t("Charger connected", "Lader aangesloten", "Ladegerät angeschlossen"),
    "precharge": t("Precharge", "Voorladen", "Vorladung"),
    "problem": t("Problem", "Probleem", "Problem"),
    "bank_problem": t("Problem", "Probleem", "Problem"),
}
SWITCHES = {
    "charge_switch": t("Charging", "Laden", "Laden"),
    "discharge_switch": t("Discharging", "Ontladen", "Entladen"),
    "balance_switch": t("Balancer", "Balanceren", "Balancer"),
}
NUMBERS = {
    "set_cell_ovp": t("Cell overvoltage protection", "Cel-overspanningsbeveiliging", "Zellüberspannungsschutz"),
    "set_cell_ovpr": t("Cell overvoltage recovery", "Cel-overspanning herstel", "Zellüberspannung Rückkehr"),
    "set_cell_uvp": t("Cell undervoltage protection", "Cel-onderspanningsbeveiliging", "Zellunterspannungsschutz"),
    "set_cell_uvpr": t("Cell undervoltage recovery", "Cel-onderspanning herstel", "Zellunterspannung Rückkehr"),
    "set_charge_voltage": t("Charge voltage per cell", "Laadspanning per cel", "Ladespannung je Zelle"),
    "set_float_voltage": t("Float voltage per cell", "Druppelspanning per cel", "Erhaltungsspannung je Zelle"),
    "set_soc100_voltage": t("100 % at cell voltage", "100 % bij celspanning", "100 % bei Zellspannung"),
    "set_soc0_voltage": t("0 % at cell voltage", "0 % bij celspanning", "0 % bei Zellspannung"),
    "set_power_off_voltage": t("Power-off cell voltage", "Uitschakelspanning per cel", "Abschaltspannung je Zelle"),
    "set_balance_start": t("Balance from cell voltage", "Balanceren vanaf celspanning", "Balancieren ab Zellspannung"),
    "set_balance_trigger": t("Balance trigger difference", "Balanceren vanaf verschil", "Balancieren ab Differenz"),
    "set_max_balance_current": t("Max balance current", "Max. balanceerstroom", "Max. Balancierstrom"),
    "set_max_charge_current": t("Max charge current", "Max. laadstroom", "Max. Ladestrom"),
    "set_max_discharge_current": t("Max discharge current", "Max. ontlaadstroom", "Max. Entladestrom"),
    "set_design_capacity_ah": t("Battery capacity", "Accucapaciteit", "Akkukapazität"),
    "set_charge_ot": t("Charge over-temperature", "Laden te warm", "Laden zu warm"),
    "set_discharge_ot": t("Discharge over-temperature", "Ontladen te warm", "Entladen zu warm"),
    "set_charge_ut": t("Charge under-temperature", "Laden te koud", "Laden zu kalt"),
    "set_mos_ot": t("MOS over-temperature", "MOS te warm", "MOS zu warm"),
}
EXCEPTIONS = {
    "port_busy": t(
        "The RS485 port is in use ({error}). Stop the add-on or program that uses it.",
        "De RS485-poort is in gebruik ({error}). Zet de add-on of het programma dat hem gebruikt uit.",
        "Der RS485-Port ist belegt ({error}). Stoppe das Add-on oder Programm, das ihn nutzt.",
    ),
    "port_error": t("The RS485 port could not be opened: {error}", "De RS485-poort kon niet worden geopend: {error}", "Der RS485-Port konnte nicht geöffnet werden: {error}"),
    "no_bus": t("JK BMS Smart is not set up.", "JK BMS Smart is niet ingesteld.", "JK BMS Smart ist nicht eingerichtet."),
    "dashboard_failed": t("Could not create the dashboard: {error}", "Dashboard aanmaken lukte niet: {error}", "Dashboard konnte nicht erstellt werden: {error}"),
}
SERVICES = {
    "set_setting": {
        "name": t("Change BMS setting", "BMS-instelling wijzigen", "BMS-Einstellung ändern"),
        "description": t(
            "Writes one setting into one JK BMS, or into every pack of the bank (administrators only; 'Allow changing BMS settings' must be on).",
            "Schrijft één instelling in één JK BMS, of in alle pakketten van de bank (alleen beheerders; 'Instellingen van de BMS mogen wijzigen' moet aan staan).",
            "Schreibt eine Einstellung in ein JK BMS oder in alle Packs der Bank (nur Administratoren; 'Ändern der BMS-Einstellungen erlauben' muss an sein).",
        ),
        "fields": {
            "entity_id": {"name": t("Pack", "Pakket", "Pack"), "description": t("Any JK BMS Smart entity of the pack.", "Een willekeurige JK BMS Smart-entiteit van het pakket.", "Eine beliebige JK-BMS-Smart-Entität des Packs.")},
            "key": {"name": t("Setting", "Instelling", "Einstellung"), "description": t("Which setting.", "Welke instelling.", "Welche Einstellung.")},
            "value": {"name": t("Value", "Waarde", "Wert"), "description": t("Volts, amps, Ah or °C; switches 1 = on, 0 = off.", "Volt, ampère, Ah of °C; schakelaars 1 = aan, 0 = uit.", "Volt, Ampere, Ah oder °C; Schalter 1 = an, 0 = aus.")},
            "all_packs": {"name": t("All packs", "Alle pakketten", "Alle Packs"), "description": t("Apply to every pack of the bank.", "Toepassen op alle pakketten van de bank.", "Auf alle Packs der Bank anwenden.")},
        },
    },
    "create_dashboard": {
        "name": t("Create dashboard", "Dashboard aanmaken", "Dashboard erstellen"),
        "description": t(
            "Adds or refreshes the JK BMS Smart dashboard (administrators only).",
            "Maakt of ververst het JK BMS Smart-dashboard (alleen beheerders).",
            "Erstellt oder aktualisiert das JK-BMS-Smart-Dashboard (nur Administratoren).",
        ),
        "fields": {
            "config_entry_id": {
                "name": t("Battery bank", "Accubank", "Akkubank"),
                "description": t("Only needed with more than one bus.", "Alleen nodig bij meer dan één bus.", "Nur bei mehr als einem Bus nötig."),
            }
        },
    }
}


def pick(node, lang):
    if isinstance(node, dict):
        if set(node) == set(L):
            return node[lang]
        return {k: pick(v, lang) for k, v in node.items()}
    return node


NAME_FIELDS = {
    f"name_{a}": t(f"Name of the pack on address {a}", f"Naam van het pakket op adres {a}", f"Name des Packs auf Adresse {a}")
    for a in range(16)
}
CONFIG["step"]["found"]["data"].update(NAME_FIELDS)
OPTIONS["step"]["names"]["data"] = dict(NAME_FIELDS)


def build(lang: str) -> dict:
    sensor = {k: {"name": v} for k, v in SENSORS.items()}
    sensor["balance_state"]["state"] = BALANCE_STATES
    out = {
        "config": CONFIG,
        "options": OPTIONS,
        "entity": {"sensor": sensor, "binary_sensor": {k: {"name": v} for k, v in BINARY.items()},
                   "switch": {k: {"name": v} for k, v in SWITCHES.items()},
                   "number": {k: {"name": v} for k, v in NUMBERS.items()}},
        "exceptions": {k: {"message": v} for k, v in EXCEPTIONS.items()},
        "services": SERVICES,
    }
    return pick(out, lang)


def main() -> None:
    (ROOT / "translations").mkdir(exist_ok=True)
    for lang in L:
        (ROOT / "translations" / f"{lang}.json").write_text(json.dumps(build(lang), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "strings.json").write_text(json.dumps(build("en"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
