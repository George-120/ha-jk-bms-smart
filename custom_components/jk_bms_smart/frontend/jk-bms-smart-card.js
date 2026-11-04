/* JK BMS Smart cards — battery packs with their 16 prismatic cells, served by the jk_bms_smart integration. */
(() => {
  const VERSION = "1.0.0";
  const BASE = document.currentScript && document.currentScript.src
    ? new URL(".", document.currentScript.src).href
    : "/jk_bms_smart/";

  const I18N = {
    en: {
      tabs: { pack: "Pack", cells: "Cells", protect: "Protection", info: "Info" },
      charging: "Charging", discharging: "Discharging", idle: "Resting", offline: "Offline", noData: "Waiting for data from this BMS…",
      soc: "Charge", voltage: "Voltage", current: "Current", power: "Power", stored: "Stored", capacity: "Capacity",
      delta: "Cell delta", min: "Lowest", max: "Highest", avg: "Average", balance: "Balancer", cycles: "Cycles", soh: "Health",
      mos: "MOS", temp: "Temp", chg: "CHG", dsg: "DSG", bal: "BAL", heat: "Heat", on: "on", off: "off",
      balanceStates: { off: "idle", charging: "moving charge", discharging: "moving charge" },
      resistance: "Wire resistance", cell: "Cell", problemsTitle: "Needs attention", allGood: "No alarms", infoOnly: "Notice",
      model: "Model", firmware: "Firmware", hardware: "Hardware", serial: "Serial", made: "Made", address: "RS485 address", runtime: "Running",
      days: "days", mode: "Bus mode", listen: "listening (BMS is master)", poll: "polling", energyIn: "Charged", energyOut: "Discharged",
      settings: { cell_ovp: "Cell overvoltage", cell_ovpr: "… recovers at", cell_uvp: "Cell undervoltage", cell_uvpr: "… recovers at",
        charge_voltage: "Charge voltage (per cell)", float_voltage: "Float voltage (per cell)", soc100_voltage: "100 % at", soc0_voltage: "0 % at",
        balance_trigger: "Balance trigger", balance_start: "Balance from", max_balance_current: "Max balance current",
        max_charge_current: "Max charge current", max_discharge_current: "Max discharge current", design_capacity_ah: "Design capacity",
        charge_ot: "Charge over-temp", discharge_ot: "Discharge over-temp", charge_ut: "Charge under-temp", mos_ot: "MOS over-temp" },
      switches: "Switches", noSettings: "Settings arrive within a few minutes.",
      bankTitle: "Battery bank", packs: "packs", online: "online", lowest: "Lowest cell", highest: "Highest cell", warmest: "Warmest",
      stale: "JK BMS Smart was updated. Refresh the page to load the new cards.", reload: "Refresh",
      alarms: {
        wire_resistance: "Balance wire resistance too high", mos_overtemperature: "MOS over-temperature", cell_quantity: "Cell count does not match",
        current_sensor: "Current sensor fault", cell_overvoltage: "Cell overvoltage", battery_overvoltage: "Battery overvoltage",
        charge_overcurrent: "Charge overcurrent", charge_short_circuit: "Charge short circuit", charge_overtemperature: "Charge over-temperature",
        charge_undertemperature: "Too cold to charge", internal_communication: "Internal communication fault", cell_undervoltage: "Cell undervoltage",
        battery_undervoltage: "Battery undervoltage", discharge_overcurrent: "Discharge overcurrent", discharge_short_circuit: "Discharge short circuit",
        discharge_overtemperature: "Discharge over-temperature", charge_mos: "Charge MOSFET fault", discharge_mos: "Discharge MOSFET fault",
        gps_disconnected: "GPS module not connected", change_password: "Default Bluetooth password still set", discharge_on_failed: "Discharge could not switch on",
        battery_overtemperature: "Battery over-temperature", temperature_sensor: "Temperature sensor fault", parallel_module: "Parallel module fault",
      },
    },
    nl: {
      tabs: { pack: "Pakket", cells: "Cellen", protect: "Beveiliging", info: "Info" },
      charging: "Laden", discharging: "Ontladen", idle: "In rust", offline: "Offline", noData: "Wachten op gegevens van deze BMS…",
      soc: "Lading", voltage: "Spanning", current: "Stroom", power: "Vermogen", stored: "Opgeslagen", capacity: "Capaciteit",
      delta: "Celverschil", min: "Laagste", max: "Hoogste", avg: "Gemiddeld", balance: "Balancer", cycles: "Cycli", soh: "Gezondheid",
      mos: "MOS", temp: "Temp", chg: "LAD", dsg: "ONT", bal: "BAL", heat: "Verw.", on: "aan", off: "uit",
      balanceStates: { off: "rust", charging: "verplaatst lading", discharging: "verplaatst lading" },
      resistance: "Draadweerstand", cell: "Cel", problemsTitle: "Let op", allGood: "Geen alarmen", infoOnly: "Melding",
      model: "Model", firmware: "Firmware", hardware: "Hardware", serial: "Serienummer", made: "Productie", address: "RS485-adres", runtime: "Draaitijd",
      days: "dagen", mode: "Busmodus", listen: "luisteren (BMS is master)", poll: "uitvragen", energyIn: "Geladen", energyOut: "Ontladen",
      settings: { cell_ovp: "Cel overspanning", cell_ovpr: "… herstelt bij", cell_uvp: "Cel onderspanning", cell_uvpr: "… herstelt bij",
        charge_voltage: "Laadspanning (per cel)", float_voltage: "Druppelspanning (per cel)", soc100_voltage: "100 % bij", soc0_voltage: "0 % bij",
        balance_trigger: "Balanceren vanaf verschil", balance_start: "Balanceren vanaf", max_balance_current: "Max. balanceerstroom",
        max_charge_current: "Max. laadstroom", max_discharge_current: "Max. ontlaadstroom", design_capacity_ah: "Ontwerpcapaciteit",
        charge_ot: "Laden te warm", discharge_ot: "Ontladen te warm", charge_ut: "Laden te koud", mos_ot: "MOS te warm" },
      switches: "Schakelaars", noSettings: "De instellingen komen binnen een paar minuten binnen.",
      bankTitle: "Accubank", packs: "pakketten", online: "online", lowest: "Laagste cel", highest: "Hoogste cel", warmest: "Warmst",
      stale: "JK BMS Smart is bijgewerkt. Vernieuw de pagina om de nieuwe kaarten te laden.", reload: "Vernieuwen",
      alarms: {
        wire_resistance: "Weerstand balanceerdraad te hoog", mos_overtemperature: "MOS te warm", cell_quantity: "Aantal cellen klopt niet",
        current_sensor: "Stroomsensor defect", cell_overvoltage: "Cel overspanning", battery_overvoltage: "Accu overspanning",
        charge_overcurrent: "Laadstroom te hoog", charge_short_circuit: "Kortsluiting bij laden", charge_overtemperature: "Te warm om te laden",
        charge_undertemperature: "Te koud om te laden", internal_communication: "Interne communicatiefout", cell_undervoltage: "Cel onderspanning",
        battery_undervoltage: "Accu onderspanning", discharge_overcurrent: "Ontlaadstroom te hoog", discharge_short_circuit: "Kortsluiting bij ontladen",
        discharge_overtemperature: "Te warm om te ontladen", charge_mos: "Laad-MOSFET defect", discharge_mos: "Ontlaad-MOSFET defect",
        gps_disconnected: "GPS-module niet aangesloten", change_password: "Standaard Bluetooth-wachtwoord nog actief", discharge_on_failed: "Ontladen kon niet aan",
        battery_overtemperature: "Accu te warm", temperature_sensor: "Temperatuursensor defect", parallel_module: "Parallelmodule defect",
      },
    },
    de: {
      tabs: { pack: "Pack", cells: "Zellen", protect: "Schutz", info: "Info" },
      charging: "Laden", discharging: "Entladen", idle: "Ruhe", offline: "Offline", noData: "Warte auf Daten von diesem BMS…",
      soc: "Ladung", voltage: "Spannung", current: "Strom", power: "Leistung", stored: "Gespeichert", capacity: "Kapazität",
      delta: "Zelldifferenz", min: "Niedrigste", max: "Höchste", avg: "Mittel", balance: "Balancer", cycles: "Zyklen", soh: "Zustand",
      mos: "MOS", temp: "Temp", chg: "LAD", dsg: "ENT", bal: "BAL", heat: "Heiz.", on: "an", off: "aus",
      balanceStates: { off: "Ruhe", charging: "verschiebt Ladung", discharging: "verschiebt Ladung" },
      resistance: "Leitungswiderstand", cell: "Zelle", problemsTitle: "Achtung", allGood: "Keine Alarme", infoOnly: "Hinweis",
      model: "Modell", firmware: "Firmware", hardware: "Hardware", serial: "Seriennummer", made: "Produktion", address: "RS485-Adresse", runtime: "Laufzeit",
      days: "Tage", mode: "Busmodus", listen: "mithören (BMS ist Master)", poll: "abfragen", energyIn: "Geladen", energyOut: "Entladen",
      settings: { cell_ovp: "Zellüberspannung", cell_ovpr: "… zurück bei", cell_uvp: "Zellunterspannung", cell_uvpr: "… zurück bei",
        charge_voltage: "Ladespannung (je Zelle)", float_voltage: "Erhaltungsspannung (je Zelle)", soc100_voltage: "100 % bei", soc0_voltage: "0 % bei",
        balance_trigger: "Balancieren ab Differenz", balance_start: "Balancieren ab", max_balance_current: "Max. Balancierstrom",
        max_charge_current: "Max. Ladestrom", max_discharge_current: "Max. Entladestrom", design_capacity_ah: "Nennkapazität",
        charge_ot: "Laden zu warm", discharge_ot: "Entladen zu warm", charge_ut: "Laden zu kalt", mos_ot: "MOS zu warm" },
      switches: "Schalter", noSettings: "Die Einstellungen kommen in wenigen Minuten.",
      bankTitle: "Akkubank", packs: "Packs", online: "online", lowest: "Niedrigste Zelle", highest: "Höchste Zelle", warmest: "Wärmste",
      stale: "JK BMS Smart wurde aktualisiert. Lade die Seite neu, um die neuen Karten zu laden.", reload: "Neu laden",
      alarms: {
        wire_resistance: "Balancerleitung Widerstand zu hoch", mos_overtemperature: "MOS Übertemperatur", cell_quantity: "Zellenzahl stimmt nicht",
        current_sensor: "Stromsensor defekt", cell_overvoltage: "Zellüberspannung", battery_overvoltage: "Akku-Überspannung",
        charge_overcurrent: "Ladeüberstrom", charge_short_circuit: "Kurzschluss beim Laden", charge_overtemperature: "Zu warm zum Laden",
        charge_undertemperature: "Zu kalt zum Laden", internal_communication: "Interner Kommunikationsfehler", cell_undervoltage: "Zellunterspannung",
        battery_undervoltage: "Akku-Unterspannung", discharge_overcurrent: "Entladeüberstrom", discharge_short_circuit: "Kurzschluss beim Entladen",
        discharge_overtemperature: "Zu warm zum Entladen", charge_mos: "Lade-MOSFET defekt", discharge_mos: "Entlade-MOSFET defekt",
        gps_disconnected: "GPS-Modul nicht verbunden", change_password: "Standard-Bluetooth-Passwort noch aktiv", discharge_on_failed: "Entladen ließ sich nicht einschalten",
        battery_overtemperature: "Akku Übertemperatur", temperature_sensor: "Temperatursensor defekt", parallel_module: "Parallelmodul defekt",
      },
    },
  };

  const C = { green: "#45D69A", amber: "#F4B740", red: "#FF5C61", blue: "#5AA9FF", teal: "#3DD6C6", muted: "#59616D" };

  // Resting LiFePO4 voltage → state of charge (rough, only used to fill the cell drawings).
  const LFP = [[2.5, 0], [2.9, 3], [3.1, 8], [3.2, 15], [3.25, 28], [3.28, 45], [3.3, 62], [3.32, 75], [3.34, 86], [3.36, 93], [3.4, 97], [3.5, 100]];
  const lfpFill = (v) => {
    if (v == null) return 0;
    if (v <= LFP[0][0]) return 0;
    for (let i = 1; i < LFP.length; i++) {
      if (v <= LFP[i][0]) {
        const [v0, s0] = LFP[i - 1]; const [v1, s1] = LFP[i];
        return s0 + (s1 - s0) * (v - v0) / (v1 - v0);
      }
    }
    return 100;
  };

  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (v, d = 0) => (v == null || isNaN(v) ? "–" : Number(v).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d }));
  const deltaColor = (mv) => (mv == null ? C.muted : mv < 15 ? C.green : mv < 40 ? C.amber : C.red);
  const socColor = (soc) => (soc == null ? C.muted : soc < 15 ? C.red : soc < 35 ? C.amber : C.green);
  const tempColor = (t) => (t == null ? C.muted : t < 5 ? C.blue : t < 40 ? C.green : t < 55 ? C.amber : C.red);
  const fmtPower = (w) => (w == null ? "–" : Math.abs(w) >= 1000 ? `${num(w / 1000, 2)} kW` : `${num(w, 0)} W`);

  class JkBase extends HTMLElement {
    static getConfigElement() { return document.createElement("jk-bms-smart-card-editor"); }

    setConfig(config) {
      this._config = { theme: "auto", ...(config || {}) };
      this._tab = this._tab || this._config.tab || "pack";
      this._sig = null;
      if (!this.shadowRoot) {
        this.attachShadow({ mode: "open" });
        this.shadowRoot.addEventListener("click", (e) => this._onClick(e));
      }
    }

    set hass(hass) {
      this._hass = hass;
      const st = this._config && hass.states[this._config.entity];
      const sig = JSON.stringify([st && st.last_updated, st && st.attributes, this._tab, hass.themes && hass.themes.darkMode, hass.language]);
      if (sig === this._sig) return;
      this._sig = sig;
      this._render();
    }

    get _t() {
      const pick = (this._config.language && this._config.language !== "auto" ? this._config.language : (this._hass && this._hass.language)) || "en";
      return I18N[pick.split("-")[0]] || I18N.en;
    }

    _themeClass() {
      const theme = this._config.theme || "auto";
      if (theme === "dark" || theme === "light") return theme;
      return this._hass && this._hass.themes && this._hass.themes.darkMode === false ? "light" : "dark";
    }

    _staleBar(data, t) {
      if (!data || !data.card_version || data.card_version === VERSION) return "";
      return `<div class="stale"><span>${t.stale}</span><button data-act="reload">${t.reload}</button></div>`;
    }

    _onClick(e) {
      const el = e.target.closest("[data-act]");
      if (!el) return;
      const act = el.dataset.act;
      if (act === "tab") { this._tab = el.dataset.tab; this._sig = null; this._render(); }
      else if (act === "reload") { location.reload(); }
      else if (act === "more") {
        const ev = new Event("hass-more-info", { bubbles: true, composed: true });
        ev.detail = { entityId: el.dataset.entity };
        this.dispatchEvent(ev);
      }
    }

    _shell(inner, data, t) {
      this.shadowRoot.innerHTML = `<style>${CSS}</style><ha-card class="${this._themeClass()}">${this._staleBar(data, t)}${inner}</ha-card>`;
    }

    getCardSize() { return 8; }
  }

  // ------------------------------------------------------------------ pack card

  class JkPackCard extends JkBase {
    static getStubConfig(hass) {
      const e = Object.keys(hass.states).find((id) => hass.states[id].attributes && hass.states[id].attributes.pack);
      return { entity: e || "" };
    }

    _render() {
      if (!this._hass || !this._config) return;
      const t = this._t;
      const st = this._hass.states[this._config.entity];
      const p = st && st.attributes.pack;
      if (!p) {
        this._shell(`<div class="empty">${esc(this._config.entity || "")} — ${t.noData}</div>`, null, t);
        return;
      }
      const tabs = ["pack", "cells", "protect", "info"];
      if (!tabs.includes(this._tab)) this._tab = "pack";
      const body = !p.cells ? `<div class="empty">${t.noData}</div>`
        : this._tab === "cells" ? this._viewCells(p, t)
        : this._tab === "protect" ? this._viewProtect(p, t)
        : this._tab === "info" ? this._viewInfo(p, t)
        : this._viewPack(p, t);
      const nav = this._config.hide_tabs ? "" : `<nav class="tabs">${tabs.map((x) => `<button class="tab ${this._tab === x ? "sel" : ""}" data-act="tab" data-tab="${x}">${t.tabs[x]}</button>`).join("")}</nav>`;
      this._shell(`${this._header(p, t)}${this._problems(p, t)}${nav}<section class="body">${body}</section>`, p, t);
    }

    _flow(p) {
      if (!p.online) return "offline";
      if (p.current > 0.3) return "charging";
      if (p.current < -0.3) return "discharging";
      return "idle";
    }

    _header(p, t) {
      const flow = this._flow(p);
      const col = flow === "charging" ? C.green : flow === "discharging" ? C.amber : flow === "offline" ? C.muted : C.blue;
      const model = [p.info && p.info.model, p.info && p.info.software && `v${p.info.software}`, `#${p.address}`].filter(Boolean).join(" · ");
      return `
        <div class="head">
          <div class="htitle">
            <div class="name">${esc(this._config.name || p.name)}</div>
            <div class="sub">${esc(model)}</div>
          </div>
          <div class="flowchip" style="--fc:${col}"><span class="fdot ${flow}"></span>${t[flow]}${flow === "charging" || flow === "discharging" ? ` · ${fmtPower(Math.abs(p.power))}` : ""}</div>
        </div>`;
    }

    _problems(p, t) {
      const probs = p.problems || [];
      if (!probs.length) return "";
      return `<div class="alarm"><ha-icon icon="mdi:alert"></ha-icon><div><b>${t.problemsTitle}</b><br>${probs.map((a) => esc(t.alarms[a] || a)).join(" · ")}</div></div>`;
    }

    _viewPack(p, t) {
      const soc = p.soc;
      const R = 46; const circ = 2 * Math.PI * R;
      const ring = `
        <svg class="ring" viewBox="0 0 120 120" aria-hidden="true">
          <circle cx="60" cy="60" r="${R}" class="rtrack"/>
          <circle cx="60" cy="60" r="${R}" class="rval" style="stroke:${socColor(soc)};stroke-dasharray:${(circ * (soc || 0)) / 100} ${circ}"/>
        </svg>
        <div class="ringtxt"><b>${num(soc)}<small>%</small></b><span>${num(p.remaining_ah, 0)} / ${num(p.full_ah, 0)} Ah</span></div>`;
      const kwh = p.remaining_ah != null && p.voltage ? (p.remaining_ah * p.voltage) / 1000 : null;
      const deltaMv = p.cell_delta != null ? Math.round(p.cell_delta * 1000) : null;
      return `
        <div class="hero">
          <div class="ringwrap">${ring}</div>
          <div class="kv">
            <div><span>${t.voltage}</span><b>${num(p.voltage, 2)} V</b></div>
            <div><span>${t.current}</span><b>${num(p.current, 1)} A</b></div>
            <div><span>${t.power}</span><b>${fmtPower(p.power)}</b></div>
            <div><span>${t.stored}</span><b>${num(kwh, 2)} kWh</b></div>
          </div>
        </div>
        ${this._packSvg(p, t)}
        <div class="tiles">
          <div class="tile wide"><span>${t.delta}</span><b style="color:${deltaColor(deltaMv)}">${num(deltaMv)} mV</b>
            <i class="mini"><em style="width:${Math.min(100, (deltaMv || 0) / 0.8)}%;background:${deltaColor(deltaMv)}"></em></i></div>
          <div class="tile"><span>${t.min}</span><b class="cmin">${num(p.cells[p.cell_min_index], 3)}</b><small>${t.cell} ${p.cell_min_index + 1}</small></div>
          <div class="tile"><span>${t.max}</span><b class="cmax">${num(p.cells[p.cell_max_index], 3)}</b><small>${t.cell} ${p.cell_max_index + 1}</small></div>
          <div class="tile"><span>${t.avg}</span><b>${num(p.cell_avg, 3)}</b><small>V</small></div>
          <div class="tile"><span>${t.balance}</span><b style="color:${p.balance_state !== "off" ? C.teal : "inherit"}">${p.balance_state !== "off" ? `${num(Math.abs(p.balance_current), 2)} A` : t.off}</b><small>${t.balanceStates[p.balance_state] || ""}</small></div>
          <div class="tile"><span>${t.cycles}</span><b>${num(p.cycles)}</b></div>
          <div class="tile"><span>${t.soh}</span><b>${num(p.soh)} %</b></div>
          <div class="tile"><span>${t.energyIn}</span><b>${num(p.charged_kwh, 1)}</b><small>kWh</small></div>
          <div class="tile"><span>${t.energyOut}</span><b>${num(p.discharged_kwh, 1)}</b><small>kWh</small></div>
        </div>`;
    }

    // Top view of the pack: two rows of prismatic cells in series, busbars, BMS board with leads.
    _packSvg(p, t, opts = {}) {
      const cells = p.cells || [];
      const n = cells.length || 16;
      const perRow = Math.ceil(n / 2);
      const W = 640; const cw = 66; const gap = 8; const ch = 112;
      const left = (W - (perRow * cw + (perRow - 1) * gap)) / 2;
      const top1 = 96; const top2 = top1 + ch + 26;
      const avg = p.cell_avg || (cells.reduce((a, b) => a + b, 0) / (cells.length || 1));
      const minI = p.cell_min_index; const maxI = p.cell_max_index;
      const balancing = p.balance_state && p.balance_state !== "off";
      const flow = this._flow(p);
      // cell i: first row left→right (cells 1..8), second row right→left (cells 9..16): a real series snake
      const pos = (i) => {
        if (i < perRow) return { x: left + i * (cw + gap), y: top1, row: 0 };
        const j = i - perRow;
        return { x: left + (perRow - 1 - j) * (cw + gap), y: top2, row: 1 };
      };
      let defs = `<defs>
        <linearGradient id="can" x1="0" x2="1"><stop offset="0" stop-color="var(--can1)"/><stop offset=".5" stop-color="var(--can2)"/><stop offset="1" stop-color="var(--can1)"/></linearGradient>
        <linearGradient id="bus" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#E8C27A"/><stop offset="1" stop-color="#A97F35"/></linearGradient>
        <linearGradient id="pcb" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1F4D3A"/><stop offset="1" stop-color="#143628"/></linearGradient>`;
      let body = "";
      const term = (cx, cy, plus) => `<rect x="${cx - 9}" y="${cy - 6}" width="18" height="12" rx="3" class="term ${plus ? "tp" : "tn"}"/>`;
      const terms = [];
      for (let i = 0; i < n; i++) {
        const v = cells[i];
        const { x, y, row } = pos(i);
        const fill = lfpFill(v);
        const dev = v != null ? (v - avg) * 1000 : 0; // mV
        const tint = Math.abs(dev) < 3 ? C.green : dev > 0 ? (dev > 15 ? C.red : C.amber) : (dev < -15 ? "#4C7DFF" : C.blue);
        const fh = ((ch - 34) * fill) / 100;
        defs += `<linearGradient id="f${i}" x1="0" x2="0" y1="1" y2="0"><stop offset="0" stop-color="${tint}" stop-opacity=".95"/><stop offset="1" stop-color="${tint}" stop-opacity=".55"/></linearGradient>`;
        const cls = i === minI ? "cellmin" : i === maxI ? "cellmax" : "";
        // terminals: the second row is turned around, so the series string snakes back
        const flip = row === 1;
        const tl = { x: x + 17, y: y + 14 }; const tr = { x: x + cw - 17, y: y + 14 };
        const plusPt = flip ? tl : tr; const minusPt = flip ? tr : tl;
        terms.push({ plus: plusPt, minus: minusPt });
        body += `
          <g class="cell ${cls}" data-act="more" ${p.entities && p.entities[`cell_voltage_${i + 1}`] ? `data-entity="${p.entities[`cell_voltage_${i + 1}`]}"` : ""}>
            <rect x="${x}" y="${y}" width="${cw}" height="${ch}" rx="7" class="can" fill="url(#can)"/>
            <rect x="${x + 6}" y="${y + 28 + (ch - 34 - fh)}" width="${cw - 12}" height="${fh}" rx="4" fill="url(#f${i})" class="lvl"/>
            <rect x="${x + 4}" y="${y + 26}" width="${cw - 8}" height="${ch - 30}" rx="5" class="win"/>
            ${term(minusPt.x, minusPt.y, false)}${term(plusPt.x, plusPt.y, true)}
            <text x="${x + cw / 2}" y="${y + 18}" class="cn">${i + 1}</text>
            <rect x="${x + 7}" y="${y + 46}" width="${cw - 14}" height="38" rx="7" class="plate"/>
            <text x="${x + cw / 2}" y="${y + 63}" class="cv">${v != null ? v.toFixed(3) : "–"}</text>
            <text x="${x + cw / 2}" y="${y + 77}" class="cdev" fill="${tint}">${v != null ? `${dev >= 0 ? "+" : ""}${dev.toFixed(0)} mV` : ""}</text>
            ${i === minI ? `<text x="${x + cw / 2}" y="${y - 6}" class="tag tmin">MIN</text>` : ""}
            ${i === maxI ? `<text x="${x + cw / 2}" y="${y - 6}" class="tag tmax">MAX</text>` : ""}
          </g>`;
      }
      // busbars: + of cell i to - of cell i+1
      let bars = "";
      for (let i = 0; i < n - 1; i++) {
        const a = terms[i].plus; const b = terms[i + 1].minus;
        if (pos(i).row !== pos(i + 1).row) {
          // row change: run the link around the outside of the pack
          const ex = left + perRow * cw + (perRow - 1) * gap + 6;
          bars += `<path d="M ${a.x} ${a.y} L ${ex} ${a.y} L ${ex} ${b.y} L ${b.x} ${b.y}" class="bar link"/>`;
        } else {
          bars += `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="bar"/>`;
        }
      }
      // BMS board above the pack, leads B- (cell 1 minus) and B+ (last cell plus)
      const bx = W / 2 - 150; const by = 12; const bw = 300; const bh = 54;
      const bminus = terms[0].minus; const bplus = terms[n - 1].plus;
      const leadCls = flow === "charging" ? "lead chg" : flow === "discharging" ? "lead dsg" : "lead";
      const led = (x, on, label, color) => `<g><circle cx="${x}" cy="${by + 38}" r="5" fill="${on ? color : "#33403A"}" class="${on ? "ledon" : ""}" style="--lc:${color}"/><text x="${x}" y="${by + 22}" class="ledl">${label}</text></g>`;
      const board = `
        <rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="8" fill="url(#pcb)" class="pcb"/>
        <text x="${bx + 14}" y="${by + 22}" class="pcbt">JK BMS</text>
        <text x="${bx + 14}" y="${by + 40}" class="pcbs">${esc((p.info && p.info.model) || "")}</text>
        ${led(bx + 170, p.charging, t.chg, C.green)}${led(bx + 205, p.discharging, t.dsg, C.amber)}${led(bx + 240, balancing, t.bal, C.teal)}${led(bx + 272, p.heating, "🔥", C.red)}
        <path d="M ${bminus.x} ${bminus.y} L ${bminus.x} ${by + bh / 2} L ${bx} ${by + bh / 2}" class="${leadCls} neg"/>
        <path d="M ${bplus.x} ${bplus.y} L ${left - 26} ${bplus.y} L ${left - 26} ${by + 14} L ${bx} ${by + 14}" class="${leadCls} pos"/>
        <text x="${bminus.x + 22}" y="${by + bh / 2 + 18}" class="pol">B−</text>
        <text x="${left - 10}" y="${bplus.y + 22}" class="pol">B+</text>`;
      // active balancer: charge moves from the highest to the lowest cell
      let bal = "";
      if (balancing && minI != null && maxI != null && minI !== maxI) {
        const a = pos(maxI); const b = pos(minI);
        const ax = a.x + cw / 2; const ay = a.y + ch / 2; const bx2 = b.x + cw / 2; const by2 = b.y + ch / 2;
        const mx = (ax + bx2) / 2; const my = Math.min(ay, by2) - 40;
        bal = `<path d="M ${ax} ${ay} Q ${mx} ${my} ${bx2} ${by2}" class="balarc"/>
               <text x="${mx}" y="${my + 12}" class="baltxt">${num(Math.abs(p.balance_current || 0), 2)} A</text>`;
      }
      // temperature probes as chips under the tray (MOS on the board)
      const chips = [["MOS", p.mos_temp], ...(p.temps || []).map((v, i) => [`T${i + 1}`, v])].filter(([, v]) => v != null);
      const chipW = 78; const chipY = top2 + ch + 24;
      const chipX0 = W / 2 - (chips.length * (chipW + 8) - 8) / 2;
      const temps = chips.map(([label, v], i) => `
        <g><rect x="${chipX0 + i * (chipW + 8)}" y="${chipY}" width="${chipW}" height="22" rx="11" class="tbadge"/>
        <text x="${chipX0 + i * (chipW + 8) + chipW / 2}" y="${chipY + 15}" class="tbt" fill="${tempColor(v)}">${label} ${num(v, 1)}°</text></g>`).join("");
      const H = chips.length ? chipY + 28 : top2 + ch + 18;
      return `<div class="packwrap${opts.large ? " large" : ""}"><svg class="pack" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(p.name)}">${defs}</defs>
        <rect x="${left - 14}" y="${top1 - 14}" width="${perRow * cw + (perRow - 1) * gap + 28}" height="${top2 + ch - top1 + 28}" rx="14" class="tray"/>
        ${body}${bars}${board}${bal}${temps}</svg></div>`;
    }

    _viewCells(p, t) {
      const cells = p.cells || [];
      const lo = Math.min(...cells); const hi = Math.max(...cells);
      const span = Math.max(0.02, hi - lo);
      const base = lo - span * 0.6;
      const scale = (v) => Math.max(4, ((v - base) / (hi - base)) * 100);
      const res = p.resistances || [];
      const maxRes = Math.max(...res, 0.001);
      const bars = cells.map((v, i) => {
        const dev = (v - (p.cell_avg || v)) * 1000;
        const col = i === p.cell_min_index ? C.blue : i === p.cell_max_index ? C.red : Math.abs(dev) < 3 ? C.green : dev > 0 ? C.amber : "#7FB2FF";
        const ent = p.entities && p.entities[`cell_voltage_${i + 1}`];
        return `<button class="cbar" data-act="more" data-entity="${esc(ent || "")}" title="${t.cell} ${i + 1}: ${v.toFixed(3)} V">
          <span class="cbv">${v.toFixed(3)}</span>
          <span class="cbtrack"><i style="height:${scale(v)}%;background:${col}"></i></span>
          <span class="cbn">${i + 1}</span>
          <span class="cbr"><i style="width:${(100 * (res[i] || 0)) / maxRes}%"></i></span>
          <span class="cbrv">${res[i] != null ? (res[i] * 1000).toFixed(0) : ""}</span>
        </button>`;
      }).join("");
      const deltaMv = p.cell_delta != null ? Math.round(p.cell_delta * 1000) : null;
      return `
        ${this._packSvg(p, t, { large: true })}
        <div class="cellsum">
          <span>${t.min} <b class="cmin">${num(lo, 3)} V</b></span>
          <span>${t.max} <b class="cmax">${num(hi, 3)} V</b></span>
          <span>${t.delta} <b style="color:${deltaColor(deltaMv)}">${num(deltaMv)} mV</b></span>
        </div>
        <div class="cbars" style="grid-template-columns:repeat(${cells.length},1fr)">${bars}</div>
        <div class="legend"><span>${t.resistance} (mΩ)</span></div>`;
    }

    _viewProtect(p, t) {
      const s = p.settings;
      if (!s) return `<div class="empty">${t.noSettings}</div>`;
      const row = (k, v, unit, d = 3) => `<div class="srow"><span>${t.settings[k]}</span><b>${num(v, d)} ${unit}</b></div>`;
      const sw = (label, on) => `<span class="swc ${on ? "on" : ""}"><i></i>${label}</span>`;
      const ovp = s.cell_ovp; const uvp = s.cell_uvp;
      const lo = p.cells ? Math.min(...p.cells) : null; const hi = p.cells ? Math.max(...p.cells) : null;
      const pct = (v) => Math.max(0, Math.min(100, ((v - uvp) / (ovp - uvp)) * 100));
      const window = ovp > uvp && lo != null ? `
        <div class="window">
          <div class="wbar">
            <i class="wrange" style="left:${pct(lo)}%;width:${Math.max(1, pct(hi) - pct(lo))}%"></i>
            <em style="left:${pct(s.balance_start)}%" title="${t.settings.balance_start}"></em>
            <em class="chg" style="left:${pct(s.charge_voltage)}%" title="${t.settings.charge_voltage}"></em>
          </div>
          <div class="wlab"><span>${num(uvp, 2)} V</span><span>${t.cell}: ${num(lo, 3)}–${num(hi, 3)} V</span><span>${num(ovp, 2)} V</span></div>
        </div>` : "";
      return `
        ${window}
        <div class="switches">${t.switches}: ${sw(t.chg, s.charge_switch)}${sw(t.dsg, s.discharge_switch)}${sw(t.bal, s.balance_switch)}</div>
        <div class="slist">
          ${row("cell_ovp", s.cell_ovp, "V")}${row("cell_ovpr", s.cell_ovpr, "V")}
          ${row("cell_uvp", s.cell_uvp, "V")}${row("cell_uvpr", s.cell_uvpr, "V")}
          ${row("charge_voltage", s.charge_voltage, "V")}${row("float_voltage", s.float_voltage, "V")}
          ${row("soc100_voltage", s.soc100_voltage, "V")}${row("soc0_voltage", s.soc0_voltage, "V")}
          ${row("balance_start", s.balance_start, "V")}${row("balance_trigger", s.balance_trigger * 1000, "mV", 0)}
          ${row("max_balance_current", s.max_balance_current, "A", 1)}${row("max_charge_current", s.max_charge_current, "A", 0)}
          ${row("max_discharge_current", s.max_discharge_current, "A", 0)}${row("design_capacity_ah", s.design_capacity_ah, "Ah", 0)}
          ${row("charge_ot", s.charge_ot, "°C", 0)}${row("discharge_ot", s.discharge_ot, "°C", 0)}
          ${row("charge_ut", s.charge_ut, "°C", 0)}${row("mos_ot", s.mos_ot, "°C", 0)}
        </div>`;
    }

    _viewInfo(p, t) {
      const i = p.info || {};
      const row = (label, value) => (value ? `<div class="srow"><span>${label}</span><b>${esc(value)}</b></div>` : "");
      const alarms = p.alarms || [];
      const list = alarms.length
        ? alarms.map((a) => `<div class="arow ${(p.problems || []).includes(a) ? "bad" : ""}"><ha-icon icon="${(p.problems || []).includes(a) ? "mdi:alert" : "mdi:information-outline"}"></ha-icon>${esc(t.alarms[a] || a)}${(p.problems || []).includes(a) ? "" : ` <small>(${t.infoOnly})</small>`}</div>`).join("")
        : `<div class="arow ok"><ha-icon icon="mdi:check-circle"></ha-icon>${t.allGood}</div>`;
      return `
        <div class="alist">${list}</div>
        <div class="slist">
          ${row(t.model, i.model)}${row(t.firmware, i.software)}${row(t.hardware, i.hardware)}${row(t.serial, i.serial)}${row(t.made, i.manufacturing_date)}
          ${row(t.address, String(p.address))}${row(t.runtime, p.runtime_s ? `${num(p.runtime_s / 86400, 0)} ${t.days}` : "")}
          ${row(t.mode, p.mode === "listen" ? t.listen : p.mode === "poll" ? t.poll : "")}
          ${row(t.energyIn, `${num(p.charged_kwh, 2)} kWh`)}${row(t.energyOut, `${num(p.discharged_kwh, 2)} kWh`)}
        </div>`;
    }
  }

  // ------------------------------------------------------------------ bank card

  class JkBankCard extends JkBase {
    static getStubConfig(hass) {
      const e = Object.keys(hass.states).find((id) => hass.states[id].attributes && hass.states[id].attributes.bank);
      return { entity: e || "" };
    }

    _render() {
      if (!this._hass || !this._config) return;
      const t = this._t;
      const st = this._hass.states[this._config.entity];
      const b = st && st.attributes.bank;
      if (!b) { this._shell(`<div class="empty">${t.noData}</div>`, null, t); return; }
      const packs = (b.packs || []).map((x) => ({ ...x, p: x.entity && this._hass.states[x.entity] && this._hass.states[x.entity].attributes.pack }));
      const flow = b.current > 0.5 ? "charging" : b.current < -0.5 ? "discharging" : "idle";
      const col = flow === "charging" ? C.green : flow === "discharging" ? C.amber : C.blue;
      const deltaMv = b.cell_delta != null ? Math.round(b.cell_delta * 1000) : null;
      const R = 52; const circ = 2 * Math.PI * R;
      const mini = (x) => {
        const p = x.p;
        if (!p || !p.cells) {
          return `<button class="mpack off" data-act="more" data-entity="${esc(x.entity || "")}"><div class="mname">${esc(x.name)}</div><div class="mcells empty">${t.offline}</div></button>`;
        }
        const avg = p.cell_avg;
        const cells = p.cells.map((v, i) => {
          const dev = (v - avg) * 1000;
          const tint = i === p.cell_min_index ? C.blue : i === p.cell_max_index ? C.red : Math.abs(dev) < 3 ? C.green : dev > 0 ? C.amber : "#7FB2FF";
          return `<i style="--h:${Math.max(8, lfpFill(v))}%;--c:${tint}" title="${i + 1}: ${v.toFixed(3)} V"></i>`;
        });
        const half = Math.ceil(cells.length / 2);
        const pf = p.current > 0.3 ? "charging" : p.current < -0.3 ? "discharging" : "idle";
        const pd = Math.round((p.cell_delta || 0) * 1000);
        return `<button class="mpack ${p.online ? "" : "off"}" data-act="more" data-entity="${esc(x.entity)}">
          <div class="mtop"><span class="mname">${esc(x.name)}</span><span class="msoc" style="color:${socColor(p.soc)}">${num(p.soc)}%</span></div>
          <div class="mcells">${cells.slice(0, half).join("")}</div>
          <div class="mcells">${cells.slice(half).reverse().join("")}</div>
          <div class="mfoot"><span class="fdot ${pf}"></span>${fmtPower(p.power)}<span style="color:${deltaColor(pd)}">Δ ${pd} mV</span>${(p.problems || []).length ? `<ha-icon icon="mdi:alert" class="warn"></ha-icon>` : ""}</div>
        </button>`;
      };
      const probs = b.problems || [];
      this._shell(`
        <div class="head">
          <div class="htitle"><div class="name">${esc(this._config.name || t.bankTitle)}</div>
            <div class="sub">${b.online}/${b.total} ${t.packs} ${t.online}</div></div>
          <div class="flowchip" style="--fc:${col}"><span class="fdot ${flow}"></span>${t[flow]}${flow !== "idle" ? ` · ${fmtPower(Math.abs(b.power))}` : ""}</div>
        </div>
        ${probs.length ? `<div class="alarm"><ha-icon icon="mdi:alert"></ha-icon><div><b>${t.problemsTitle}</b><br>${probs.map((a) => esc(t.alarms[a] || a)).join(" · ")}</div></div>` : ""}
        <div class="bankhero">
          <div class="ringwrap big">
            <svg class="ring" viewBox="0 0 130 130"><circle cx="65" cy="65" r="${R}" class="rtrack"/>
              <circle cx="65" cy="65" r="${R}" class="rval" style="stroke:${socColor(b.soc)};stroke-dasharray:${(circ * (b.soc || 0)) / 100} ${circ}"/></svg>
            <div class="ringtxt"><b>${num(b.soc, 0)}<small>%</small></b><span>${num(b.remaining_kwh, 1)} / ${num(b.full_kwh, 1)} kWh</span></div>
          </div>
          <div class="kv">
            <div><span>${t.power}</span><b style="color:${col}">${fmtPower(b.power)}</b></div>
            <div><span>${t.current}</span><b>${num(b.current, 1)} A</b></div>
            <div><span>${t.voltage}</span><b>${num(b.voltage, 2)} V</b></div>
            <div><span>${t.delta}</span><b style="color:${deltaColor(deltaMv)}">${num(deltaMv)} mV</b></div>
          </div>
        </div>
        <div class="mpacks" style="grid-template-columns:repeat(${Math.min(packs.length, 3) || 1},1fr)">${packs.map(mini).join("")}</div>
        <div class="tiles">
          <div class="tile wide"><span>${t.lowest}</span><b class="cmin">${num(b.cell_min, 3)} V</b><small>${esc(b.cell_min_where || "")}</small></div>
          <div class="tile wide"><span>${t.highest}</span><b class="cmax">${num(b.cell_max, 3)} V</b><small>${esc(b.cell_max_where || "")}</small></div>
          <div class="tile"><span>${t.warmest}</span><b style="color:${tempColor(b.temp_max)}">${num(b.temp_max, 1)}°</b></div>
          <div class="tile"><span>${t.energyIn}</span><b>${num(b.charged_kwh, 1)}</b><small>kWh</small></div>
          <div class="tile"><span>${t.energyOut}</span><b>${num(b.discharged_kwh, 1)}</b><small>kWh</small></div>
        </div>`, b, t);
    }

    getCardSize() { return 7; }
  }

  // ------------------------------------------------------------------ editor

  class JkEditor extends HTMLElement {
    setConfig(config) { this._config = config; this._render(); }
    set hass(hass) { this._hass = hass; this._render(); }
    _render() {
      if (!this._hass || !this._config) return;
      if (!this._form) {
        this._form = document.createElement("ha-form");
        this._form.computeLabel = (s) => ({ entity: "JK BMS Smart", name: "Name", theme: "Theme / Thema", tab: "Start tab", language: "Language / Taal / Sprache", hide_tabs: "Hide tabs / Tabs verbergen" }[s.name] || s.name);
        this._form.addEventListener("value-changed", (ev) => {
          this._config = ev.detail.value;
          this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true }));
        });
        this.appendChild(this._form);
      }
      this._form.hass = this._hass;
      this._form.data = this._config;
      this._form.schema = [
        { name: "entity", selector: { entity: { integration: "jk_bms_smart", domain: "sensor", device_class: "battery" } } },
        { name: "name", selector: { text: {} } },
        { name: "tab", selector: { select: { mode: "dropdown", options: ["pack", "cells", "protect", "info"] } } },
        { name: "hide_tabs", selector: { boolean: {} } },
        { name: "theme", selector: { select: { mode: "dropdown", options: [{ value: "auto", label: "Auto" }, { value: "dark", label: "Dark / Donker" }, { value: "light", label: "Light / Licht" }] } } },
        { name: "language", selector: { select: { mode: "dropdown", options: [{ value: "auto", label: "Automatic" }, { value: "nl", label: "Nederlands" }, { value: "en", label: "English" }, { value: "de", label: "Deutsch" }] } } },
      ];
    }
  }

  const CSS = `
    :host { display:block; container-type:inline-size; }
    ha-card {
      display:block;
      --bg:#14181E; --panel:#1C2129; --line:#2A303A; --text:#EDF0F4; --muted:#8C95A2; --accent:#5AA9FF;
      --can1:#2B323D; --can2:#3A4350; --tray:#10141A; --win:rgba(255,255,255,.035);
      background:var(--bg); color:var(--text); border-radius:var(--ha-card-border-radius,16px);
      padding:18px 18px 16px; font-family:var(--ha-font-family-body, "Roboto", system-ui, sans-serif);
      overflow:hidden; border:1px solid var(--line);
    }
    ha-card.light { --bg:#FFFFFF; --panel:#F2F4F7; --line:#E3E7EC; --text:#14181E; --muted:#6B7480; --accent:#2F7FE0;
      --can1:#C9D0D9; --can2:#E4E8EE; --tray:#EEF1F5; --win:rgba(0,0,0,.03); box-shadow:0 2px 10px rgba(20,24,30,.06); }
    .empty { color:var(--muted); padding:24px 4px; text-align:center; }
    .stale { display:flex; align-items:center; gap:10px; background:rgba(90,169,255,.14); border:1px solid rgba(90,169,255,.4); border-radius:12px; padding:8px 10px; margin:0 0 12px; font-size:.8rem; }
    .stale span { flex:1; }
    .stale button { background:var(--accent); color:#06121F; border:0; border-radius:8px; padding:6px 12px; font:inherit; font-weight:600; cursor:pointer; }
    .head { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
    .htitle { flex:1; min-width:0; }
    .name { font-size:1.15rem; font-weight:600; letter-spacing:.01em; }
    .sub { color:var(--muted); font-size:.8rem; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .flowchip { display:flex; align-items:center; gap:7px; font-size:.8rem; font-weight:600; padding:6px 11px; border-radius:999px;
      background:color-mix(in srgb, var(--fc) 16%, transparent); color:var(--fc); white-space:nowrap; }
    .fdot { width:8px; height:8px; border-radius:50%; background:currentColor; display:inline-block; }
    .fdot.charging, .fdot.discharging { animation:pulse 1.6s ease-in-out infinite; }
    .fdot.offline { background:#59616D; }
    @keyframes pulse { 0%,100% { box-shadow:0 0 0 0 color-mix(in srgb, currentColor 55%, transparent); } 50% { box-shadow:0 0 0 5px transparent; } }
    .alarm { display:flex; gap:10px; align-items:flex-start; background:rgba(255,92,97,.12); border:1px solid rgba(255,92,97,.45); border-radius:12px; padding:9px 12px; margin:0 0 12px; font-size:.84rem; }
    .alarm ha-icon { color:#FF5C61; --mdc-icon-size:20px; }
    .tabs { display:flex; gap:18px; border-bottom:1px solid var(--line); margin:4px 0 14px; }
    .tab { background:none; border:0; color:var(--muted); font:inherit; font-size:.85rem; padding:6px 0 9px; cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-1px; }
    .tab.sel { color:var(--text); border-bottom-color:var(--accent); }
    .hero, .bankhero { display:flex; align-items:center; gap:18px; margin-bottom:6px; }
    .ringwrap { position:relative; width:118px; height:118px; flex:none; }
    .ringwrap.big { width:132px; height:132px; }
    .ring { width:100%; height:100%; transform:rotate(-90deg); }
    .rtrack { fill:none; stroke:var(--panel); stroke-width:10; }
    .rval { fill:none; stroke-width:10; stroke-linecap:round; transition:stroke-dasharray .8s ease; }
    .ringtxt { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
    .ringtxt b { font-size:1.9rem; font-weight:600; line-height:1; }
    .ringtxt b small { font-size:.9rem; font-weight:500; margin-left:1px; color:var(--muted); }
    .ringtxt span { font-size:.66rem; color:var(--muted); margin-top:4px; max-width:78%; text-align:center; line-height:1.2; }
    .kv { flex:1; display:grid; grid-template-columns:1fr 1fr; gap:8px; }
    .kv div { background:var(--panel); border-radius:12px; padding:8px 10px; display:flex; flex-direction:column; gap:2px; }
    .kv span { font-size:.72rem; color:var(--muted); }
    .kv b { font-size:1.02rem; font-weight:600; }
    .packwrap { margin:6px -6px 4px; }
    .pack { width:100%; height:auto; display:block; }
    .tray { fill:var(--tray); stroke:var(--line); stroke-width:1.5; }
    .can { stroke:rgba(0,0,0,.35); stroke-width:1; }
    .win { fill:var(--win); stroke:rgba(255,255,255,.06); }
    ha-card.light .win { stroke:rgba(0,0,0,.06); }
    .lvl { transition:height .6s ease, y .6s ease; }
    .plate { fill:rgba(10,13,18,.62); }
    ha-card.light .plate { fill:rgba(255,255,255,.78); }
    .term { stroke:rgba(0,0,0,.4); stroke-width:1; }
    .tp { fill:#C9A24A; } .tn { fill:#9AA3AF; }
    .bar { stroke:#C9A24A; stroke-width:7; stroke-linecap:round; stroke-linejoin:round; fill:none; opacity:.95; }
    .cell { cursor:pointer; }
    .cell:hover .can { stroke:var(--accent); stroke-width:2; }
    .cellmin .can { stroke:#5AA9FF; stroke-width:2.5; filter:drop-shadow(0 0 6px rgba(90,169,255,.6)); }
    .cellmax .can { stroke:#FF5C61; stroke-width:2.5; filter:drop-shadow(0 0 6px rgba(255,92,97,.55)); }
    .cv { font-size:13px; font-weight:600; text-anchor:middle; fill:var(--text); font-variant-numeric:tabular-nums; }
    .cdev { font-size:10px; text-anchor:middle; font-weight:600; }
    .cn { font-size:10px; text-anchor:middle; fill:var(--muted); }
    .tag { font-size:9.5px; font-weight:700; text-anchor:middle; letter-spacing:.06em; }
    .tmin { fill:#5AA9FF; } .tmax { fill:#FF5C61; }
    .pcb { stroke:#2E6B52; stroke-width:1.5; }
    .pcbt { fill:#E8F5EE; font-size:15px; font-weight:700; letter-spacing:.08em; }
    .pcbs { fill:#9FD3B9; font-size:10px; }
    .ledl { fill:#9FD3B9; font-size:9px; text-anchor:middle; font-weight:600; }
    .ledon { filter:drop-shadow(0 0 4px var(--lc)); }
    .lead { fill:none; stroke-width:5; stroke-linecap:round; }
    .lead.neg { stroke:#3B3F46; } .lead.pos { stroke:#C2413B; }
    .lead.chg, .lead.dsg { stroke-dasharray:2 12; }
    .lead.chg.pos, .lead.dsg.neg { animation:flowIn 1s linear infinite; }
    .lead.chg.neg, .lead.dsg.pos { animation:flowOut 1s linear infinite; }
    .lead.chg { stroke:#45D69A; } .lead.dsg { stroke:#F4B740; }
    @keyframes flowIn { to { stroke-dashoffset:-14; } }
    @keyframes flowOut { to { stroke-dashoffset:14; } }
    .pol { font-size:12px; font-weight:700; fill:var(--muted); text-anchor:middle; }
    .balarc { fill:none; stroke:#3DD6C6; stroke-width:3; stroke-dasharray:6 8; animation:flowIn .8s linear infinite; filter:drop-shadow(0 0 4px rgba(61,214,198,.7)); }
    .baltxt { fill:#3DD6C6; font-size:11px; font-weight:700; text-anchor:middle; }
    .tbadge { fill:var(--panel); stroke:var(--line); }
    .tbt { font-size:11px; font-weight:600; text-anchor:middle; }
    .tiles { display:grid; grid-template-columns:repeat(auto-fill, minmax(92px, 1fr)); gap:8px; margin-top:10px; }
    .tile { background:var(--panel); border-radius:12px; padding:9px 10px; display:flex; flex-direction:column; gap:2px; min-width:0; }
    .tile.wide { grid-column:span 2; }
    .tile span { font-size:.7rem; color:var(--muted); }
    .tile b { font-size:1rem; font-weight:600; font-variant-numeric:tabular-nums; }
    .tile small { font-size:.7rem; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .mini { display:block; height:5px; border-radius:3px; background:var(--line); margin-top:5px; overflow:hidden; }
    .mini em { display:block; height:100%; border-radius:3px; }
    .cmin { color:#5AA9FF; } .cmax { color:#FF5C61; }
    .cellsum { display:flex; flex-wrap:wrap; gap:14px; font-size:.82rem; color:var(--muted); margin:10px 2px; }
    .cellsum b { color:var(--text); margin-left:4px; }
    .cbars { display:grid; gap:4px; align-items:end; }
    .cbar { background:none; border:0; padding:0; color:var(--text); font:inherit; cursor:pointer; display:flex; flex-direction:column; align-items:center; gap:3px; min-width:0; }
    .cbv { font-size:.58rem; color:var(--muted); writing-mode:vertical-rl; transform:rotate(180deg); height:38px; font-variant-numeric:tabular-nums; }
    .cbtrack { width:100%; max-width:26px; height:110px; background:var(--panel); border-radius:6px; display:flex; align-items:flex-end; overflow:hidden; }
    .cbtrack i { display:block; width:100%; border-radius:6px 6px 3px 3px; transition:height .6s ease; }
    .cbn { font-size:.68rem; color:var(--muted); }
    .cbr { width:100%; max-width:26px; height:4px; background:var(--line); border-radius:2px; overflow:hidden; }
    .cbr i { display:block; height:100%; background:#8C95A2; }
    .cbrv { font-size:.58rem; color:var(--muted); }
    .legend { font-size:.7rem; color:var(--muted); text-align:right; margin-top:4px; }
    .window { background:var(--panel); border-radius:12px; padding:12px; margin-bottom:10px; }
    .wbar { position:relative; height:12px; border-radius:6px; background:linear-gradient(90deg,#FF5C61 0%,#F4B740 12%,#45D69A 30%,#45D69A 75%,#F4B740 90%,#FF5C61 100%); opacity:.85; }
    .wrange { position:absolute; top:-4px; bottom:-4px; border:2px solid var(--text); border-radius:6px; min-width:4px; }
    .wbar em { position:absolute; top:-6px; width:2px; height:24px; background:#3DD6C6; }
    .wbar em.chg { background:var(--accent); }
    .wlab { display:flex; justify-content:space-between; font-size:.72rem; color:var(--muted); margin-top:8px; }
    .switches { display:flex; align-items:center; flex-wrap:wrap; gap:8px; font-size:.8rem; color:var(--muted); margin-bottom:10px; }
    .swc { display:inline-flex; align-items:center; gap:6px; background:var(--panel); border-radius:999px; padding:4px 10px; color:var(--muted); font-weight:600; }
    .swc i { width:8px; height:8px; border-radius:50%; background:#59616D; }
    .swc.on { color:var(--text); } .swc.on i { background:#45D69A; }
    .slist { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:6px; }
    .srow { display:flex; justify-content:space-between; gap:8px; background:var(--panel); border-radius:10px; padding:8px 10px; font-size:.82rem; }
    .srow span { color:var(--muted); }
    .alist { display:flex; flex-direction:column; gap:6px; margin-bottom:12px; }
    .arow { display:flex; align-items:center; gap:8px; background:var(--panel); border-radius:10px; padding:8px 10px; font-size:.84rem; }
    .arow ha-icon { --mdc-icon-size:18px; color:var(--muted); }
    .arow.bad ha-icon { color:#FF5C61; } .arow.ok ha-icon { color:#45D69A; }
    .arow small { color:var(--muted); }
    .mpacks { display:grid; gap:10px; margin-top:12px; }
    .mpack { background:var(--panel); border:1px solid transparent; border-radius:14px; padding:10px; color:var(--text); font:inherit; text-align:left; cursor:pointer; display:flex; flex-direction:column; gap:6px; min-width:0; }
    .mpack:hover { border-color:var(--line); }
    .mpack.off { opacity:.5; }
    .mtop { display:flex; justify-content:space-between; align-items:baseline; gap:6px; }
    .mname { font-weight:600; font-size:.88rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .msoc { font-weight:700; font-size:.95rem; }
    .mcells { display:grid; grid-template-columns:repeat(8, 1fr); gap:3px; height:34px; }
    .mcells.empty { display:block; height:auto; color:var(--muted); font-size:.8rem; padding:20px 0; text-align:center; }
    .mcells i { position:relative; display:block; border-radius:3px; background:var(--can1); overflow:hidden; }
    .mcells i::after { content:""; position:absolute; left:0; right:0; bottom:0; height:var(--h); background:var(--c); opacity:.9; }
    .mfoot { display:flex; align-items:center; gap:7px; font-size:.75rem; color:var(--muted); flex-wrap:wrap; }
    .mfoot .fdot { width:7px; height:7px; }
    .mfoot .fdot.charging { color:#45D69A; } .mfoot .fdot.discharging { color:#F4B740; } .mfoot .fdot.idle { color:#5AA9FF; }
    .mfoot span:last-of-type { margin-left:auto; }
    .warn { color:#FF5C61; --mdc-icon-size:16px; }
    @container (max-width: 420px) { .hero, .bankhero { flex-direction:column; align-items:stretch; } .ringwrap { margin:0 auto; } }
  `;

  const DEFS = [
    ["jk-bms-smart-pack-card", JkPackCard],
    ["jk-bms-smart-bank-card", JkBankCard],
    ["jk-bms-smart-card-editor", JkEditor],
  ];
  const register = () => {
    for (const [tag, cls] of DEFS) {
      if (customElements.get(tag)) continue;
      try { customElements.define(tag, cls); } catch (_e) { try { customElements.define(tag, class extends cls {}); } catch (_e2) { /* known */ } }
    }
  };
  register();
  for (const ms of [0, 300, 1000, 2500, 5000, 10000]) setTimeout(register, ms);
  window.customCards = window.customCards || [];
  for (const [type, name, description] of [
    ["jk-bms-smart-pack-card", "JK BMS Smart – Accupakket / Battery pack", "One JK BMS with its prismatic cells, balancer, temperatures and protection settings."],
    ["jk-bms-smart-bank-card", "JK BMS Smart – Accubank / Battery bank", "All packs together: charge, power, lowest/highest cell."],
  ]) {
    if (!window.customCards.some((c) => c.type === type)) {
      window.customCards.push({ type, name, description, preview: true, documentationURL: "https://github.com/George-120/ha-jk-bms-smart" });
    }
  }
  console.info(`%c JK-BMS-SMART %c ${VERSION} `, "background:#45D69A;color:#06121F;font-weight:600", "background:#14181E;color:#EDF0F4");
  void BASE;
})();
