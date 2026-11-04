<h1><img src="https://raw.githubusercontent.com/George-120/ha-jk-bms-smart/main/custom_components/jk_bms_smart/brand/icon.png" alt="" width="56" height="56" align="absmiddle"> JK BMS Smart</h1>

JK inverter-BMS'en (PB-serie, bijv. JK-PB2A16S20P / 30P) rechtstreeks in Home Assistant via RS485 — met een USB-RS485-stick of een RS485-netwerkgateway. Geen add-on, geen MQTT, geen ESP32. Elke BMS wordt een eigen apparaat, samen vormen ze één accubank, en de kaarten tekenen je pakketten met alle prismatische cellen.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=George-120&repository=ha-jk-bms-smart&category=integration)
[![Integratie toevoegen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=jk_bms_smart)

**Taal / Language / Sprache:** [Nederlands](#nederlands) · [English](#english) · [Deutsch](#deutsch)

## Nederlands

### Wat het doet

- **Plug and play.** Kies je USB-RS485-stick (de meest waarschijnlijke staat bovenaan) en de integratie zoekt zelf alle BMS'en op de bus, met model, aantal cellen, spanning en lading.
- **Werkt met en zonder master-BMS.** Heeft één BMS DIP-adres 0, dan is die de master en vraagt die de andere uit; Home Assistant luistert dan alleen mee en zendt nooit iets (geen botsingen op de bus). Hebben alle BMS'en een adres vanaf 1, dan vraagt Home Assistant ze zelf uit. Dat wordt automatisch herkend.
- **Geen spook-apparaten.** Elk 300-byte JK-frame wordt met checksum gecontroleerd en aan een adres gekoppeld via de Modbus-bevestiging (met CRC) die erna komt. Het instellingenframe bevat het adres nog een keer als controle. Verminkte frames worden weggegooid in plaats van als "nieuwe BMS" te verschijnen, en adressen die niet bij het instellen zijn gevonden worden nooit automatisch toegevoegd.
- **Alles per BMS:** lading, spanning, stroom, vermogen, resterende/volle capaciteit, opgeslagen kWh, gezondheid, cycli, alle celspanningen, laagste/hoogste/gemiddelde cel en het verschil, balanceerstroom en -status, MOS-temperatuur en tot vijf accutemperaturen, laad-/ontlaad-MOSFET, verwarming, alarmen (in gewone taal), geladen/ontladen kWh voor het Energie-dashboard, en de beveiligingsinstellingen (alleen lezen). Draadweerstand per cel staat als diagnostiek klaar.
- **Accubank:** totale lading (gewogen naar capaciteit), vermogen, stroom, opgeslagen energie, laagste en hoogste cel van de hele bank (met pakket en celnummer), warmste punt, en een probleemmelding als een pakket alarm geeft of stil valt.
- **Kaarten** in dezelfde donkere stijl als Easee Smart Charging:
  - *Accupakket*: het pakket van bovenaf met alle prismatische cellen in serie (polen, busbars, B−/B+ naar de BMS-print), vulniveau en afwijking per cel, MIN/MAX gemarkeerd, de actieve balancer als bewegende boog van de hoogste naar de laagste cel, stroom die zichtbaar in- of uitloopt, LED's voor laden/ontladen/balanceren. Tabbladen Cellen (staafjes + draadweerstand), Beveiliging (spanningsvenster en grenzen) en Info (model, firmware, serienummer, alarmen).
  - *Accubank*: alle pakketten naast elkaar met hun cellen in miniatuur, totale lading en vermogen.
- **Dashboard met één druk:** *Configureren → Dashboard aanmaken*.
- Nederlands, Engels en Duits.

Deze integratie leest alleen; ze verandert geen instellingen in de BMS.

### Installatie

1. Installeer **JK BMS Smart** via HACS (knop hierboven) en herstart Home Assistant.
2. **Gebruikt een add-on de RS485-stick al (bijvoorbeeld een JK BMS-add-on), zet die dan uit.** Twee programma's tegelijk op één seriële poort gaat niet goed.
3. *Instellingen → Apparaten & diensten → Integratie toevoegen → JK BMS Smart*, kies *USB-RS485-stick* en de stick. Na maximaal 40 seconden zie je de gevonden BMS'en; geef ze een naam.
4. *Configureren → Dashboard aanmaken*, of zet de kaarten zelf op een dashboard (*JK BMS Smart – Accupakket* en *– Accubank* in de kaartkiezer).

### Aansluiten

- Stick op de **RS485-poort** van de BMS (de RJ45 waarop ook de JK-pc-software werkt), A op A, B op B; komt er niets binnen, wissel A en B dan om. Bij meerdere BMS'en zit de RS485 doorgelust tussen de pakketten.
- 115200 baud, 8N1 (dat regelt de integratie zelf).
- Netwerkgateway (Elfin EW11, USR-TCP232, Waveshare): transparante TCP-server, 115200 8N1.

### Problemen oplossen

- *Poort in gebruik*: een add-on of ander programma heeft de stick nog open.
- *Geen BMS gevonden*: A/B omwisselen, kabel controleren, of het DIP-adres. Downloaddiagnostiek op de integratie laat zien hoeveel bytes en geldige frames er binnenkomen.
- Pakket toegevoegd of DIP-adres gewijzigd: *Configureren → Opnieuw zoeken*.

## English

Read JK inverter BMS units (PB series) straight into Home Assistant over RS485 — USB-RS485 stick or RS485 network gateway, no add-on, no MQTT. The flow finds every BMS on the bus, detects whether a master BMS (DIP address 0) is present (then Home Assistant only listens) or polls the units itself. Frames are checksummed and attributed to an address through the CRC-checked Modbus acknowledgement, so line noise never turns into ghost devices. Every pack gets all cell voltages, balancer, temperatures, MOSFET states, alarms, energy counters and its protection settings (read only); the battery bank gets totals. Two cards draw the packs with their prismatic cells (balancer animation, min/max cells, current flow) and the whole bank. *Configure → Create dashboard* adds a ready-made dashboard.

Install via HACS, restart, **stop any add-on that uses the stick**, then add *JK BMS Smart*.

## Deutsch

Liest JK-Inverter-BMS (PB-Serie) direkt per RS485 in Home Assistant — USB-RS485-Stick oder RS485-Netzwerk-Gateway, ohne Add-on und ohne MQTT. Die Einrichtung findet alle BMS am Bus und erkennt, ob ein Master-BMS (DIP-Adresse 0) vorhanden ist (dann hört Home Assistant nur mit) oder ob Home Assistant selbst abfragt. Frames werden per Prüfsumme und CRC-geprüfter Modbus-Bestätigung einer Adresse zugeordnet — keine Geistergeräte mehr. Pro Pack: alle Zellspannungen, Balancer, Temperaturen, MOSFETs, Alarme, Energiezähler und Schutzeinstellungen (nur lesen); für die Akkubank Summen. Zwei Karten zeigen die Packs mit ihren prismatischen Zellen und die ganze Bank. *Konfigurieren → Dashboard erstellen* legt ein fertiges Dashboard an.

Über HACS installieren, neu starten, **ein Add-on, das den Stick nutzt, stoppen**, dann *JK BMS Smart* hinzufügen.

---

Not affiliated with JK BMS / Jikong. Protocol: JK "BMS RS485 Modbus V1.0/V1.1".
