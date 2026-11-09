/* JK BMS Smart cards — battery packs with their 16 prismatic cells, served by the jk_bms_smart integration. */
(() => {
  const VERSION = "1.2.1";
  const BASE = document.currentScript && document.currentScript.src
    ? new URL(".", document.currentScript.src).href
    : "/jk_bms_smart/";

  const I18N = {
    en: {
      tabs: { pack: "Pack", cells: "Cells", charts: "Charts", protect: "Protection", info: "Info" },
      toFull: "Full in", toEmpty: "Empty in", weakCell: "Weakest cell", spread: "Charge difference", mismatchNote: "Settings differ between packs", hShort: "h", mShort: "min",
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
      tabs: { pack: "Pakket", cells: "Cellen", charts: "Grafieken", protect: "Beveiliging", info: "Info" },
      toFull: "Vol over", toEmpty: "Leeg over", weakCell: "Zwakste cel", spread: "Ladingsverschil", mismatchNote: "Instellingen verschillen per pakket", hShort: "u", mShort: "min",
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
      tabs: { pack: "Pack", cells: "Zellen", charts: "Diagramme", protect: "Schutz", info: "Info" },
      toFull: "Voll in", toEmpty: "Leer in", weakCell: "Schwächste Zelle", spread: "Ladungsdifferenz", mismatchNote: "Einstellungen je Pack unterschiedlich", hShort: "h", mShort: "min",
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
  const fmtDur = (min, t) => (min == null ? "–" : min < 90 ? `${Math.round(min)} ${t.mShort}` : `${num(min / 60, min < 600 ? 1 : 0)} ${t.hShort}`);
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
        // chart tooltips (mouse and touch)
        const mv = (e) => this._charts && this._charts.move && this._charts.move(e);
        this.shadowRoot.addEventListener("pointermove", mv);
        this.shadowRoot.addEventListener("pointerdown", mv);
        this.shadowRoot.addEventListener("pointerleave", (e) => this._charts && this._charts.leave && this._charts.leave(e), true);
      }
    }

    set hass(hass) {
      this._hass = hass;
      const st = this._config && hass.states[this._config.entity];
      // keep the last good data while an update is in flight: a short "unavailable" must not
      // collapse the card (that is what makes a phone jump to the top)
      if (st && st.attributes && (st.attributes.pack || st.attributes.bank)) this._lastAttrs = st.attributes;
      const sig = JSON.stringify([st && st.attributes, this._tab, hass.themes && hass.themes.darkMode, hass.language]);
      if (sig === this._sig) return;
      this._sig = sig;
      // at most one redraw per second
      if (this._pending) return;
      const wait = Math.max(0, 1000 - (Date.now() - (this._drawn || 0)));
      this._pending = setTimeout(() => { this._pending = null; this._drawn = Date.now(); this._render(); }, wait);
    }

    _stateAttrs(entity) {
      const st = this._hass.states[entity];
      if (st && st.attributes && (st.attributes.pack || st.attributes.bank)) return st.attributes;
      return entity === this._config.entity ? this._lastAttrs : null;
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

    // Update the card in place instead of rebuilding the whole shadow DOM on every state change.
    // On phones a full rebuild briefly removes the card's content; the page then shrinks for a
    // moment and the browser/app jumps back to the top. So: style and <ha-card> are created once,
    // nothing happens when the output did not change, the height is held during the swap and the
    // scroll position is put back if anything moved it anyway.
    _shell(inner, data, t) {
      const html = `${this._staleBar(data, t)}${inner}`;
      const cls = this._themeClass();
      const root = this.shadowRoot;
      let card = this._card;
      if (!card || !card.isConnected) {
        root.innerHTML = `<style>${CSS}</style><ha-card></ha-card>`;
        card = this._card = root.querySelector("ha-card");
        this._html = null;
      }
      if (card.className !== cls) card.className = cls;
      const lang = ((this._hass && this._hass.language) || "en").split("-")[0];
      if (card.getAttribute("lang") !== lang) card.setAttribute("lang", lang);
      if (html === this._html) return;
      this._html = html;
      const scrollers = this._scrollers();
      const positions = scrollers.map((el) => el.scrollTop);
      const height = card.offsetHeight;
      if (height) card.style.minHeight = `${height}px`;
      card.innerHTML = html;
      scrollers.forEach((el, i) => { if (Math.abs(el.scrollTop - positions[i]) > 1) el.scrollTop = positions[i]; });
      requestAnimationFrame(() => {
        card.style.minHeight = "";
        scrollers.forEach((el, i) => { if (positions[i] > 0 && el.scrollTop < positions[i] - 40) el.scrollTop = positions[i]; });
      });
    }

    // The page itself plus every scrolled container the card sits in (HA uses different
    // scroll containers on desktop, phone browsers and the companion app).
    _scrollers() {
      const out = [];
      const se = document.scrollingElement;
      if (se) out.push(se);
      let n = this;
      for (let i = 0; i < 40 && n; i++) {
        n = n.parentNode || (n instanceof ShadowRoot ? n.host : null) || (n.host || null);
        if (n && n.nodeType === 1 && n.scrollHeight > n.clientHeight + 1 && n.scrollTop > 0 && !out.includes(n)) out.push(n);
      }
      return out;
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
      const a = this._stateAttrs(this._config.entity);
      const p = a && a.pack;
      if (!p) {
        this._shell(`<div class="empty">${esc(this._config.entity || "")} — ${t.noData}</div>`, null, t);
        return;
      }
      const tabs = ["pack", "cells", "charts", "protect", "info"];
      if (!tabs.includes(this._tab)) this._tab = "pack";
      const body = !p.cells ? `<div class="empty">${t.noData}</div>`
        : this._tab === "cells" ? this._viewCells(p, t)
        : this._tab === "charts" ? this._viewCharts(p)
        : this._tab === "protect" ? this._viewProtect(p, t)
        : this._tab === "info" ? this._viewInfo(p, t)
        : this._viewPack(p, t);
      const nav = this._config.hide_tabs ? "" : `<nav class="tabs">${tabs.map((x) => `<button class="tab ${this._tab === x ? "sel" : ""}" data-act="tab" data-tab="${x}">${t.tabs[x]}</button>`).join("")}</nav>`;
      this._shell(`${this._header(p, t)}${this._problems(p, t)}${nav}<section class="body">${body}</section>`, p, t);
    }

    _chartCtx(p) {
      return { mode: "pack", entities: p.entities || {}, cells: (p.cells || []).length || 16, health: this._config.entity, name: p.name, allowChanges: p.allow_changes, data: p };
    }

    _viewCharts(p) {
      this._charts = this._charts || new Charts(this);
      return this._charts.html(this._chartCtx(p));
    }

    _onClick(e) {
      const el = e.target.closest("[data-act]");
      const a = this._stateAttrs(this._config.entity);
      if (el && this._charts && a && a.pack && this._charts.click(el, this._chartCtx(a.pack))) return;
      super._onClick(e);
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
      const hl = p.health || {};
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
          ${hl.time_to_full_min != null ? `<div class="tile"><span>${t.toFull}</span><b style="color:${C.green}">${fmtDur(hl.time_to_full_min, t)}</b></div>` : ""}
          ${hl.time_to_empty_min != null ? `<div class="tile"><span>${t.toEmpty}</span><b style="color:${C.amber}">${fmtDur(hl.time_to_empty_min, t)}</b></div>` : ""}
          ${hl.weakest ? `<div class="tile"><span>${t.weakCell}</span><b style="color:${C.amber}">${t.cell} ${hl.weakest}</b><small>${hl.weakest_share}%</small></div>` : ""}
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
      const weak = p.health && p.health.weakest && p.health.weakest_share >= 50 ? p.health.weakest - 1 : -1;
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
            ${weak === i ? `<g class="weak"><title>${esc(t.weakCell)}</title><circle cx="${x + cw - 9}" cy="${y + ch - 10}" r="6"/><text x="${x + cw - 9}" y="${y + ch - 6.5}">!</text></g>` : ""}
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
      const a = this._stateAttrs(this._config.entity);
      const b = a && a.bank;
      if (!b) { this._shell(`<div class="empty">${t.noData}</div>`, null, t); return; }
      this._packCache = this._packCache || {};
      const packs = (b.packs || []).map((x) => {
        const live = x.entity && this._hass.states[x.entity] && this._hass.states[x.entity].attributes.pack;
        if (live) this._packCache[x.entity] = live;
        return { ...x, p: live || this._packCache[x.entity] };
      });
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
          ${b.time_to_full_min != null ? `<div class="tile"><span>${t.toFull}</span><b style="color:${C.green}">${fmtDur(b.time_to_full_min, t)}</b></div>` : ""}
          ${b.time_to_empty_min != null ? `<div class="tile"><span>${t.toEmpty}</span><b style="color:${C.amber}">${fmtDur(b.time_to_empty_min, t)}</b></div>` : ""}
          ${packs.length > 1 ? `<div class="tile"><span>${t.spread}</span><b style="color:${(b.soc_spread || 0) > 10 ? C.amber : "inherit"}">${num(b.soc_spread, 0)} %</b></div>` : ""}
        </div>
        ${(b.mismatch || []).length ? `<div class="note"><ha-icon icon="mdi:file-compare"></ha-icon>${t.mismatchNote} (${b.mismatch.length})</div>` : ""}`, b, t);
    }

    getCardSize() { return 7; }
  }

  // ------------------------------------------------------------------ settings card

  const S_GROUPS = [
    ["switches", ["charge_switch", "discharge_switch", "balance_switch"]],
    ["voltages", ["cell_ovp", "cell_ovpr", "charge_voltage", "float_voltage", "soc100_voltage", "soc0_voltage", "cell_uvpr", "cell_uvp", "power_off_voltage", "smart_sleep_voltage"]],
    ["balancer", ["balance_start", "balance_trigger", "max_balance_current"]],
    ["currents", ["max_charge_current", "max_discharge_current", "design_capacity_ah"]],
    ["delays", ["charge_ocp_delay", "charge_ocp_recovery", "discharge_ocp_delay", "discharge_ocp_recovery", "scp_recovery"]],
    ["temps", ["charge_ot", "charge_otpr", "discharge_ot", "discharge_otpr", "charge_ut", "charge_utpr", "mos_ot", "mos_otpr"]],
  ];
  // unit, decimals, step, min, max (display units; balance_trigger is shown in mV)
  const VOLT = ["V", 3, 0.005, 1.2, 4.35]; const SEC = ["s", 0, 1, 2, 600];
  const S_META = {
    cell_ovp: VOLT, cell_ovpr: VOLT, cell_uvp: VOLT, cell_uvpr: VOLT, charge_voltage: VOLT, float_voltage: VOLT,
    soc100_voltage: VOLT, soc0_voltage: VOLT, power_off_voltage: VOLT, balance_start: VOLT, smart_sleep_voltage: VOLT,
    balance_trigger: ["mV", 0, 1, 2, 1000], max_balance_current: ["A", 1, 0.1, 0.3, 2],
    max_charge_current: ["A", 0, 1, 1, 300], max_discharge_current: ["A", 0, 1, 1, 300], design_capacity_ah: ["Ah", 0, 1, 1, 2000],
    charge_ot: ["°C", 0, 1, 30, 80], discharge_ot: ["°C", 0, 1, 30, 80], charge_ut: ["°C", 0, 1, -30, 20], mos_ot: ["°C", 0, 1, 50, 100],
    charge_otpr: ["°C", 0, 1, 20, 80], discharge_otpr: ["°C", 0, 1, 20, 80], charge_utpr: ["°C", 0, 1, -25, 25], mos_otpr: ["°C", 0, 1, 30, 100],
    charge_ocp_delay: SEC, charge_ocp_recovery: SEC, discharge_ocp_delay: SEC, discharge_ocp_recovery: SEC, scp_recovery: SEC,
  };
  const S_COMPARE = Object.keys(S_META).filter((k) => k !== "design_capacity_ah");
  const S_TEXT = {
    en: { title: "BMS settings", all: "All packs", groups: { switches: "Switches", voltages: "Cell voltages", balancer: "Balancer", currents: "Current & capacity", delays: "Delays & recovery", temps: "Temperature", readonly: "Other (read only)", sync: "Make packs equal", backups: "Backups" },
      save: "Save", saving: "Saving…", saved: "Saved", differs: "differs per pack", locked: "Changing settings is off. Switch it on under Configure → Update interval → Allow changing BMS settings.",
      confirm: "Change {name} from {old} to {new} on {where}?", confirmSwitch: "Turn {name} {state} on {where}?", on: "on", off: "off", failed: "Not saved", hint: "Changes go straight into the BMS. With a master BMS they are sent in a quiet moment on the bus and confirmed by the BMS. Before the first change of the hour a backup of the pack is made automatically.",
      mismatch: "{n} setting(s) differ between the packs", from: "Copy from", preview: "Show what changes", apply: "Apply", cancel: "Cancel", nothing: "Nothing to change: already equal.", applied: "Done", backupNow: "Make a backup now", restore: "Restore", noBackups: "No backups yet.", auto: "automatic", manual: "by hand", backupMade: "Backup saved", restoreTitle: "Restore {file} to {pack}",
      names: { charge_switch: "Charging", discharge_switch: "Discharging", balance_switch: "Balancer", charge_voltage: "Charge voltage", float_voltage: "Float voltage", soc100_voltage: "100 % at", soc0_voltage: "0 % at", power_off_voltage: "Power off at", smart_sleep_voltage: "Smart sleep voltage", balance_start: "Balance from", balance_trigger: "Balance trigger", max_balance_current: "Max balance current", max_charge_current: "Max charge current", max_discharge_current: "Max discharge current", design_capacity_ah: "Battery capacity", cell_ovp: "Overvoltage protection", cell_ovpr: "Overvoltage recovery", cell_uvp: "Undervoltage protection", cell_uvpr: "Undervoltage recovery", charge_ot: "Charge too hot", charge_otpr: "… recovers at", discharge_ot: "Discharge too hot", discharge_otpr: "… recovers at", charge_ut: "Charge too cold", charge_utpr: "… recovers at", mos_ot: "MOS too hot", mos_otpr: "… recovers at", charge_ocp_delay: "Charge overcurrent: delay", charge_ocp_recovery: "… recovery time", discharge_ocp_delay: "Discharge overcurrent: delay", discharge_ocp_recovery: "… recovery time", scp_recovery: "Short circuit: recovery time" },
      ro: { scp_delay_us: "Short-circuit reaction time", precharge_s: "Precharge time", smart_sleep_hours: "Sleep after", flags: { display_always_on: "Display always on", smart_sleep: "Smart sleep", special_charger: "Special charger", charging_float_mode: "Float charging", timed_stored_data: "Timed data logging", disable_temp_sensors: "Temperature sensors off" } } },
    nl: { title: "BMS-instellingen", all: "Alle pakketten", groups: { switches: "Schakelaars", voltages: "Celspanningen", balancer: "Balancer", currents: "Stroom & capaciteit", delays: "Vertragingen & herstel", temps: "Temperatuur", readonly: "Overig (alleen lezen)", sync: "Pakketten gelijk trekken", backups: "Back-ups" },
      save: "Opslaan", saving: "Opslaan…", saved: "Opgeslagen", differs: "verschilt per pakket", locked: "Instellingen wijzigen staat uit. Zet het aan via Configureren → Verversen → Instellingen van de BMS mogen wijzigen.",
      confirm: "{name} wijzigen van {old} naar {new} op {where}?", confirmSwitch: "{name} {state}zetten op {where}?", on: "aan", off: "uit", failed: "Niet opgeslagen", hint: "Wijzigingen gaan direct de BMS in. Met een master-BMS worden ze in een stil moment op de bus verstuurd en door de BMS bevestigd. Voor de eerste wijziging van het uur wordt automatisch een back-up van het pakket gemaakt.",
      mismatch: "{n} instelling(en) verschillen tussen de pakketten", from: "Kopiëren van", preview: "Bekijk wat er verandert", apply: "Toepassen", cancel: "Annuleren", nothing: "Niets te wijzigen: al gelijk.", applied: "Klaar", backupNow: "Nu een back-up maken", restore: "Terugzetten", noBackups: "Nog geen back-ups.", auto: "automatisch", manual: "met de hand", backupMade: "Back-up opgeslagen", restoreTitle: "{file} terugzetten in {pack}",
      names: { charge_switch: "Laden", discharge_switch: "Ontladen", balance_switch: "Balanceren", charge_voltage: "Laadspanning", float_voltage: "Druppelspanning", soc100_voltage: "100 % bij", soc0_voltage: "0 % bij", power_off_voltage: "Uitschakelen bij", smart_sleep_voltage: "Slaapspanning", balance_start: "Balanceren vanaf", balance_trigger: "Balanceren vanaf verschil", max_balance_current: "Max. balanceerstroom", max_charge_current: "Max. laadstroom", max_discharge_current: "Max. ontlaadstroom", design_capacity_ah: "Accucapaciteit", cell_ovp: "Overspanningsbeveiliging", cell_ovpr: "Overspanning herstel", cell_uvp: "Onderspanningsbeveiliging", cell_uvpr: "Onderspanning herstel", charge_ot: "Laden te warm", charge_otpr: "… herstelt bij", discharge_ot: "Ontladen te warm", discharge_otpr: "… herstelt bij", charge_ut: "Laden te koud", charge_utpr: "… herstelt bij", mos_ot: "MOS te warm", mos_otpr: "… herstelt bij", charge_ocp_delay: "Laadstroom te hoog: vertraging", charge_ocp_recovery: "… hersteltijd", discharge_ocp_delay: "Ontlaadstroom te hoog: vertraging", discharge_ocp_recovery: "… hersteltijd", scp_recovery: "Kortsluiting: hersteltijd" },
      ro: { scp_delay_us: "Reactietijd kortsluiting", precharge_s: "Voorlaadtijd", smart_sleep_hours: "Slapen na", flags: { display_always_on: "Display altijd aan", smart_sleep: "Slim slapen", special_charger: "Speciale lader", charging_float_mode: "Druppelladen", timed_stored_data: "Gegevens bewaren op tijd", disable_temp_sensors: "Temperatuursensoren uit" } } },
    de: { title: "BMS-Einstellungen", all: "Alle Packs", groups: { switches: "Schalter", voltages: "Zellspannungen", balancer: "Balancer", currents: "Strom & Kapazität", delays: "Verzögerungen & Rückkehr", temps: "Temperatur", readonly: "Sonstiges (nur lesen)", sync: "Packs angleichen", backups: "Sicherungen" },
      save: "Speichern", saving: "Speichert…", saved: "Gespeichert", differs: "unterschiedlich je Pack", locked: "Ändern ist aus. Unter Konfigurieren → Aktualisierung → Ändern der BMS-Einstellungen erlauben einschalten.",
      confirm: "{name} von {old} auf {new} ändern bei {where}?", confirmSwitch: "{name} {state} bei {where}?", on: "einschalten", off: "ausschalten", failed: "Nicht gespeichert", hint: "Änderungen gehen direkt ins BMS. Mit Master-BMS werden sie in einer ruhigen Busphase gesendet und vom BMS bestätigt. Vor der ersten Änderung der Stunde wird das Pack automatisch gesichert.",
      mismatch: "{n} Einstellung(en) unterscheiden sich zwischen den Packs", from: "Kopieren von", preview: "Änderungen anzeigen", apply: "Übernehmen", cancel: "Abbrechen", nothing: "Nichts zu ändern: schon gleich.", applied: "Fertig", backupNow: "Jetzt sichern", restore: "Wiederherstellen", noBackups: "Noch keine Sicherungen.", auto: "automatisch", manual: "von Hand", backupMade: "Sicherung gespeichert", restoreTitle: "{file} in {pack} wiederherstellen",
      names: { charge_switch: "Laden", discharge_switch: "Entladen", balance_switch: "Balancer", charge_voltage: "Ladespannung", float_voltage: "Erhaltungsspannung", soc100_voltage: "100 % bei", soc0_voltage: "0 % bei", power_off_voltage: "Abschalten bei", smart_sleep_voltage: "Ruhespannung", balance_start: "Balancieren ab", balance_trigger: "Balancieren ab Differenz", max_balance_current: "Max. Balancierstrom", max_charge_current: "Max. Ladestrom", max_discharge_current: "Max. Entladestrom", design_capacity_ah: "Akkukapazität", cell_ovp: "Überspannungsschutz", cell_ovpr: "Überspannung Rückkehr", cell_uvp: "Unterspannungsschutz", cell_uvpr: "Unterspannung Rückkehr", charge_ot: "Laden zu warm", charge_otpr: "… zurück bei", discharge_ot: "Entladen zu warm", discharge_otpr: "… zurück bei", charge_ut: "Laden zu kalt", charge_utpr: "… zurück bei", mos_ot: "MOS zu warm", mos_otpr: "… zurück bei", charge_ocp_delay: "Ladeüberstrom: Verzögerung", charge_ocp_recovery: "… Rückkehrzeit", discharge_ocp_delay: "Entladeüberstrom: Verzögerung", discharge_ocp_recovery: "… Rückkehrzeit", scp_recovery: "Kurzschluss: Rückkehrzeit" },
      ro: { scp_delay_us: "Kurzschluss-Reaktionszeit", precharge_s: "Vorladezeit", smart_sleep_hours: "Ruhe nach", flags: { display_always_on: "Display immer an", smart_sleep: "Smart Sleep", special_charger: "Spezielles Ladegerät", charging_float_mode: "Erhaltungsladung", timed_stored_data: "Zeitgesteuerte Datenspeicherung", disable_temp_sensors: "Temperatursensoren aus" } } },
  };

  class JkSettingsCard extends JkBase {
    static getStubConfig(hass) {
      const e = Object.keys(hass.states).find((id) => hass.states[id].attributes && hass.states[id].attributes.bank)
        || Object.keys(hass.states).find((id) => hass.states[id].attributes && hass.states[id].attributes.pack);
      return { entity: e || "" };
    }

    get _st() {
      const pick = (this._config.language && this._config.language !== "auto" ? this._config.language : (this._hass && this._hass.language)) || "en";
      return S_TEXT[pick.split("-")[0]] || S_TEXT.en;
    }

    _packs() {
      const st = this._hass.states[this._config.entity];
      if (!st) return [];
      if (st.attributes.pack) return [{ entity: this._config.entity, p: st.attributes.pack }];
      return ((st.attributes.bank && st.attributes.bank.packs) || [])
        .map((x) => ({ entity: x.entity, p: x.entity && this._hass.states[x.entity] && this._hass.states[x.entity].attributes.pack }))
        .filter((x) => x.p);
    }

    set hass(hass) {
      this._hass = hass;
      const packs = this._packs();
      const sig = JSON.stringify([packs.map((x) => [x.p.settings, x.p.allow_changes, x.p.name]), this._sel, this._busy, this._msg, this._preview, this._backups, this._src, hass.themes && hass.themes.darkMode, hass.language]);
      if (sig === this._sig) return;
      this._sig = sig;
      this._render();
      if (this._backups === undefined && hass.user && hass.user.is_admin) this._loadBackups();
    }

    async _loadBackups() {
      this._backups = null;
      try {
        const res = await this._hass.callWS({ type: "jk_bms_smart/backups", entity_id: this._config.entity });
        this._backups = res.backups || [];
      } catch (_e) { this._backups = false; }
      this._sig = null; this._render();
    }

    _fmt(key, v) {
      if (key.endsWith("_switch")) return v ? this._st.on : this._st.off;
      const [unit, dec] = S_META[key] || ["", 0];
      if (v == null) return "–";
      return `${num(key === "balance_trigger" ? v * 1000 : v, dec)} ${unit}`;
    }

    _mismatch(packs) {
      if (packs.length < 2) return [];
      return S_COMPARE.filter((k) => {
        const vals = packs.map((x) => x.p.settings && x.p.settings[k]);
        if (vals.some((v) => v == null)) return false;
        return new Set(vals.map((v) => Math.round(v * 1000))).size > 1;
      });
    }

    _render() {
      if (!this._hass || !this._config) return;
      const t = this._t; const s = this._st;
      const packs = this._packs();
      if (!packs.length) { this._shell(`<div class="empty">${t.noData}</div>`, null, t); return; }
      if (this._sel == null) this._sel = packs.length > 1 ? "all" : 0;
      const sel = this._sel === "all" ? packs : [packs[this._sel] || packs[0]];
      const allow = packs.every((x) => x.p.allow_changes);
      const ref = sel.find((x) => x.p.settings);
      const dis = allow && !this._busy ? "" : "disabled";
      const chips = packs.length > 1 ? `<div class="schips">${packs.map((x, i) => `<button class="schip ${this._sel === i ? "sel" : ""}" data-act="spick" data-i="${i}">${esc(x.p.name)}</button>`).join("")}<button class="schip ${this._sel === "all" ? "sel" : ""}" data-act="spick" data-i="all">${s.all}</button></div>` : "";
      const body = !ref ? `<div class="empty">${t.noSettings}</div>` : S_GROUPS.map(([g, keys]) => {
        const rows = keys.map((key) => {
          const vals = sel.map((x) => x.p.settings && x.p.settings[key]).filter((v) => v != null);
          if (!vals.length) return "";
          const v = vals[0];
          const differs = vals.some((x) => x !== v);
          if (key.endsWith("_switch")) {
            return `<div class="srow2"><span>${s.names[key]}${differs ? ` <em class="sdiff">${s.differs}</em>` : ""}</span>
              <button class="tog ${v ? "on" : ""}" data-act="stoggle" data-key="${key}" ${dis} aria-pressed="${v ? "true" : "false"}"><i></i></button></div>`;
          }
          const [unit, dec, step, min, max] = S_META[key];
          const shown = key === "balance_trigger" ? v * 1000 : v;
          return `<div class="srow2"><span>${s.names[key]}${differs ? ` <em class="sdiff">${s.differs}</em>` : ""}</span>
            <span class="sedit"><input type="number" inputmode="decimal" data-key="${key}" value="${shown != null ? Number(shown).toFixed(dec) : ""}" step="${step}" min="${min}" max="${max}" ${dis}>
            <small>${unit}</small><button class="sbtn" data-act="ssave" data-key="${key}" ${dis}>${s.save}</button></span></div>`;
        }).join("");
        return rows ? `<div class="sgroup"><div class="sgtitle">${s.groups[g]}</div>${rows}</div>` : "";
      }).join("") + (ref ? this._readOnly(ref.p.settings, s) : "");
      const msg = this._msg ? `<div class="smsg ${this._msg.ok ? "ok" : "bad"}">${esc(this._msg.text)}</div>` : "";
      this._shell(`
        <div class="head"><div class="htitle"><div class="name">${esc(this._config.name || s.title)}</div><div class="sub">${esc(sel.map((x) => x.p.name).join(" · "))}</div></div></div>
        ${chips}
        ${allow ? `<div class="shint">${s.hint}</div>` : `<div class="alarm"><ha-icon icon="mdi:lock"></ha-icon><div>${s.locked}</div></div>`}
        ${msg}${this._syncHtml(packs, s, allow)}${this._previewHtml(s, allow)}${body}${this._backupHtml(packs, s, allow)}`, packs[0].p, t);
    }

    _readOnly(st, s) {
      if (!st) return "";
      const rows = [];
      if (st.scp_delay_us) rows.push([s.ro.scp_delay_us, `${num(st.scp_delay_us)} µs`]);
      if (st.precharge_s) rows.push([s.ro.precharge_s, `${num(st.precharge_s)} s`]);
      if (st.smart_sleep_hours) rows.push([s.ro.smart_sleep_hours, `${num(st.smart_sleep_hours)} h`]);
      const flags = st.flags || {};
      const chips = Object.keys(s.ro.flags).filter((k) => k in flags).map((k) => `<span class="swc ${flags[k] ? "on" : ""}"><i></i>${s.ro.flags[k]}</span>`).join("");
      if (!rows.length && !chips) return "";
      return `<div class="sgroup"><div class="sgtitle">${s.groups.readonly}</div>
        ${rows.map(([a, b]) => `<div class="srow2"><span>${a}</span><b>${b}</b></div>`).join("")}
        ${chips ? `<div class="switches ro">${chips}</div>` : ""}</div>`;
    }

    _syncHtml(packs, s, allow) {
      const diff = this._mismatch(packs);
      if (!diff.length || this._preview) return "";
      if (this._src == null || !packs[this._src]) this._src = 0;
      return `<div class="sgroup sync"><div class="sgtitle">${s.groups.sync}</div>
        <div class="syncmsg"><ha-icon icon="mdi:file-compare"></ha-icon>${s.mismatch.replace("{n}", diff.length)}: ${diff.map((k) => esc(s.names[k])).join(", ")}</div>
        <div class="syncrow"><span>${s.from}</span>${packs.map((x, i) => `<button class="schip ${this._src === i ? "sel" : ""}" data-act="ssrc" data-i="${i}">${esc(x.p.name)}</button>`).join("")}</div>
        <button class="sbtn wide" data-act="spreview" ${this._busy ? "disabled" : ""}>${s.preview}</button></div>`;
    }

    _previewHtml(s, allow) {
      const pv = this._preview;
      if (!pv) return "";
      const results = pv.results || [];
      const total = results.reduce((n, r) => n + (r.changes || []).length, 0);
      const list = results.map((r) => `<div class="pvpack"><b>${esc(r.pack)}</b>${(r.changes || []).length ? (r.changes || []).map((c) => `<div class="pvrow"><span>${esc(s.names[c.key] || c.label || c.key)}</span><em>${esc(this._fmt(c.key, c.old))} → <b>${esc(this._fmt(c.key, c.new))}</b></em></div>`).join("") : `<div class="pvrow"><span>${s.nothing}</span></div>`}</div>`).join("");
      return `<div class="sgroup preview"><div class="sgtitle">${esc(pv.title)}</div>${list}
        <div class="pvbtns"><button class="sbtn ghost" data-act="pcancel">${s.cancel}</button>${total ? `<button class="sbtn" data-act="papply" ${allow && !this._busy ? "" : "disabled"}>${s.apply} (${total})</button>` : ""}</div></div>`;
    }

    _backupHtml(packs, s, allow) {
      if (this._backups === false || !(this._hass.user && this._hass.user.is_admin)) return "";
      const list = (this._backups || []).slice(0, 8);
      const lang = (this._hass.language || "en");
      const rows = list.map((b) => `<div class="srow2"><span>${esc(new Date(b.created).toLocaleString(lang, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }))} · ${esc(b.pack || "")} <em class="sdiff muted">${b.reason === "auto" ? s.auto : s.manual}</em></span>
        <button class="sbtn ghost" data-act="srestore" data-file="${esc(b.file)}" data-addr="${b.address}" ${this._busy ? "disabled" : ""}>${s.restore}</button></div>`).join("");
      return `<div class="sgroup"><div class="sgtitle">${s.groups.backups}</div>
        ${rows || `<div class="srow2"><span>${this._backups === null ? "…" : s.noBackups}</span></div>`}
        <button class="sbtn wide ghost" data-act="sbackup" ${this._busy ? "disabled" : ""}>${s.backupNow}</button></div>`;
    }

    async _call(service, data) {
      const res = await this._hass.connection.sendMessagePromise({ type: "call_service", domain: "jk_bms_smart", service, return_response: true, service_data: data });
      return (res && res.response) || {};
    }

    async _onClick(e) {
      const el = e.target.closest("[data-act]");
      if (!el) return;
      const act = el.dataset.act; const s = this._st;
      const packs = this._packs();
      const redraw = () => { this._sig = null; this._render(); };
      if (act === "spick") { this._sel = el.dataset.i === "all" ? "all" : Number(el.dataset.i); this._msg = null; redraw(); return; }
      if (act === "ssrc") { this._src = Number(el.dataset.i); redraw(); return; }
      if (act === "pcancel") { this._preview = null; redraw(); return; }
      if (act === "spreview") {
        const src = packs[this._src || 0];
        this._busy = true; redraw();
        try {
          const r = await this._call("copy_settings", { source: src.entity, dry_run: true });
          this._preview = { kind: "copy", title: `${s.groups.sync}: ${s.from.toLowerCase()} ${src.p.name}`, source: src.entity, results: r.results || [] };
          this._msg = null;
        } catch (err) { this._msg = { ok: false, text: `${s.failed}: ${(err && err.message) || err}` }; }
        this._busy = false; redraw(); return;
      }
      if (act === "srestore") {
        const addr = Number(el.dataset.addr);
        const target = packs.find((x) => x.p.address === addr) || (this._sel !== "all" ? packs[this._sel] : null);
        if (!target) return;
        this._busy = true; redraw();
        try {
          const r = await this._call("restore_settings", { entity_id: target.entity, file: el.dataset.file, dry_run: true });
          this._preview = { kind: "restore", title: s.restoreTitle.replace("{file}", el.dataset.file).replace("{pack}", target.p.name), entity: target.entity, file: el.dataset.file, results: [r] };
          this._msg = null;
        } catch (err) { this._msg = { ok: false, text: `${s.failed}: ${(err && err.message) || err}` }; }
        this._busy = false; redraw(); return;
      }
      if (act === "papply") {
        const pv = this._preview;
        this._busy = true; this._msg = { ok: true, text: s.saving }; redraw();
        try {
          const r = pv.kind === "copy"
            ? await this._call("copy_settings", { source: pv.source })
            : { results: [await this._call("restore_settings", { entity_id: pv.entity, file: pv.file })] };
          const failed = (r.results || []).flatMap((x) => Object.entries(x.failed || {}).map(([k, v]) => `${x.pack} ${s.names[k] || k}: ${v}`));
          const done = (r.results || []).reduce((n, x) => n + (x.done || []).length, 0);
          this._msg = failed.length ? { ok: false, text: `${s.applied}: ${done} · ${s.failed}: ${failed.join("; ")}` } : { ok: true, text: `${s.applied}: ${done} ${s.saved.toLowerCase()}` };
          this._preview = null;
        } catch (err) { this._msg = { ok: false, text: `${s.failed}: ${(err && err.message) || err}` }; }
        this._busy = false; redraw(); this._loadBackups(); return;
      }
      if (act === "sbackup") {
        this._busy = true; redraw();
        try {
          const entity = this._sel === "all" ? this._config.entity : (packs[this._sel] || packs[0]).entity;
          const r = await this._call("backup_settings", { entity_id: entity });
          this._msg = { ok: true, text: `${s.backupMade}: ${(r.files || []).join(", ")}` };
        } catch (err) { this._msg = { ok: false, text: `${s.failed}: ${(err && err.message) || err}` }; }
        this._busy = false; redraw(); this._loadBackups(); return;
      }
      if (act !== "ssave" && act !== "stoggle") return super._onClick(e);
      const sel = this._sel === "all" ? packs : [packs[this._sel] || packs[0]];
      const key = el.dataset.key;
      const where = sel.map((x) => x.p.name).join(", ");
      const cur = sel[0].p.settings ? sel[0].p.settings[key] : null;
      let value;
      if (act === "stoggle") {
        value = cur ? 0 : 1;
        if (!confirm(s.confirmSwitch.replace("{name}", s.names[key]).replace("{state}", value ? s.on : s.off).replace("{where}", where))) return;
      } else {
        const input = this.shadowRoot.querySelector(`input[data-key="${key}"]`);
        let v = parseFloat(String(input.value).replace(",", "."));
        if (isNaN(v)) return;
        const [, , , min, max] = S_META[key];
        if (v < min || v > max) { this._msg = { ok: false, text: `${s.failed}: ${min} – ${max}` }; redraw(); return; }
        if (key === "balance_trigger") v = v / 1000;
        value = v;
        if (!confirm(s.confirm.replace("{name}", s.names[key]).replace("{old}", this._fmt(key, cur)).replace("{new}", this._fmt(key, v)).replace("{where}", where))) return;
      }
      this._busy = true; this._msg = { ok: true, text: s.saving }; redraw();
      try {
        const r = await this._call("set_setting", { entity_id: sel[0].entity, key, value, all_packs: this._sel === "all" });
        const failed = Object.entries(r.failed || {});
        this._msg = failed.length
          ? { ok: false, text: `${s.saved}: ${(r.done || []).join(", ")} · ${s.failed}: ${failed.map(([k, v]) => `${k} (${v})`).join(", ")}` }
          : { ok: true, text: `${s.saved}: ${s.names[key]} → ${this._fmt(key, value)} (${(r.done || []).join(", ")})` };
      } catch (err) {
        this._msg = { ok: false, text: `${s.failed}: ${(err && err.message) || err}` };
      }
      this._busy = false; redraw();
    }

    getCardSize() { return 10; }
  }

  // ------------------------------------------------------------------ editor

  class JkEditor extends HTMLElement {
    setConfig(config) { this._config = config; this._render(); }
    set hass(hass) { this._hass = hass; this._render(); }
    _render() {
      if (!this._hass || !this._config) return;
      if (!this._form) {
        this._form = document.createElement("ha-form");
        this._form.computeLabel = (s) => ({ entity: "JK BMS Smart", name: "Name", theme: "Theme / Thema", tab: "Start tab", language: "Language / Taal / Sprache", hide_tabs: "Hide tabs / Tabs verbergen", chart: "Chart (chart card) / Grafiek", range: "Period / Periode" }[s.name] || s.name);
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
        { name: "tab", selector: { select: { mode: "dropdown", options: ["pack", "cells", "charts", "protect", "info"] } } },
        { name: "chart", selector: { select: { mode: "dropdown", options: ["soc", "power", "cells", "delta", "temp", "volt", "energy", "health"] } } },
        { name: "range", selector: { select: { mode: "dropdown", options: ["6h", "24h", "7d", "30d", "1y"] } } },
        { name: "hide_tabs", selector: { boolean: {} } },
        { name: "theme", selector: { select: { mode: "dropdown", options: [{ value: "auto", label: "Auto" }, { value: "dark", label: "Dark / Donker" }, { value: "light", label: "Light / Licht" }] } } },
        { name: "language", selector: { select: { mode: "dropdown", options: [{ value: "auto", label: "Automatic" }, { value: "nl", label: "Nederlands" }, { value: "en", label: "English" }, { value: "de", label: "Deutsch" }] } } },
      ];
    }
  }

  // ------------------------------------------------------------------ charts (1.2)
  //
  // Everything comes from Home Assistant's own long-term statistics (5-minute and hourly
  // mean/min/max per sensor), so the charts are light and also work for 30 days back.
  // Health (weakest cell, wire resistance per day) comes from the integration itself.

  const CH_TEXT = {
    en: { tabs: { soc: "Charge", power: "Power", cells: "Cells", delta: "Cell delta", temp: "Temperature", volt: "Voltage", energy: "Energy", health: "Health" },
      loading: "Loading…", none: "No history yet. Home Assistant builds it every 5 minutes.", failed: "Could not load the history",
      charged: "Charged", discharged: "Discharged", trigger: "balance trigger", weakest: "Weakest cell", firstFull: "Full first",
      weakTxt: "Cell {cell} was the lowest {share}% of the time when the pack was nearly empty.", fullTxt: "Cell {cell} was the highest {share}% of the time near full.",
      weakNone: "Not enough data yet: this becomes clear after the pack has been below 30 % a few times.",
      lowMinutes: "Minutes as lowest cell (below 30 %)", deltaDays: "Largest cell difference per day", resDays: "Balance-wire resistance per cell (connections)",
      packs: "packs", bank: "Bank", min: "min", max: "max", avg: "avg", tapCell: "Tap a cell to highlight it", reset: "Reset counting", resetConfirm: "Start counting the weakest cell again (e.g. after replacing cells)?" },
    nl: { tabs: { soc: "Lading", power: "Vermogen", cells: "Cellen", delta: "Celverschil", temp: "Temperatuur", volt: "Spanning", energy: "Energie", health: "Gezondheid" },
      loading: "Laden…", none: "Nog geen geschiedenis. Home Assistant bouwt die elke 5 minuten op.", failed: "Geschiedenis laden lukte niet",
      charged: "Geladen", discharged: "Ontladen", trigger: "balanceergrens", weakest: "Zwakste cel", firstFull: "Eerst vol",
      weakTxt: "Cel {cell} was {share}% van de tijd de laagste als het pakket bijna leeg was.", fullTxt: "Cel {cell} was {share}% van de tijd de hoogste bij bijna vol.",
      weakNone: "Nog te weinig gegevens: dit wordt duidelijk nadat het pakket een paar keer onder 30 % is geweest.",
      lowMinutes: "Minuten als laagste cel (onder 30 %)", deltaDays: "Grootste celverschil per dag", resDays: "Draadweerstand per cel (aansluitingen)",
      packs: "pakketten", bank: "Bank", min: "min", max: "max", avg: "gem", tapCell: "Tik op een cel om hem te markeren", reset: "Opnieuw tellen", resetConfirm: "Opnieuw beginnen met tellen welke cel de zwakste is (bijv. na het vervangen van cellen)?" },
    de: { tabs: { soc: "Ladung", power: "Leistung", cells: "Zellen", delta: "Zelldifferenz", temp: "Temperatur", volt: "Spannung", energy: "Energie", health: "Zustand" },
      loading: "Lädt…", none: "Noch kein Verlauf. Home Assistant erstellt ihn alle 5 Minuten.", failed: "Verlauf konnte nicht geladen werden",
      charged: "Geladen", discharged: "Entladen", trigger: "Balancier-Grenze", weakest: "Schwächste Zelle", firstFull: "Zuerst voll",
      weakTxt: "Zelle {cell} war {share}% der Zeit die niedrigste, wenn das Pack fast leer war.", fullTxt: "Zelle {cell} war {share}% der Zeit die höchste nahe voll.",
      weakNone: "Noch zu wenig Daten: das wird klar, nachdem das Pack einige Male unter 30 % war.",
      lowMinutes: "Minuten als niedrigste Zelle (unter 30 %)", deltaDays: "Größte Zelldifferenz pro Tag", resDays: "Leitungswiderstand je Zelle (Verbindungen)",
      packs: "Packs", bank: "Bank", min: "min", max: "max", avg: "Ø", tapCell: "Tippe auf eine Zelle, um sie hervorzuheben", reset: "Neu zählen", resetConfirm: "Neu zählen, welche Zelle die schwächste ist (z. B. nach Zellentausch)?" },
  };
  const PACK_COLORS = ["#5AA9FF", "#45D69A", "#F4B740", "#C792EA", "#FF8A65", "#3DD6C6", "#F06292", "#AED581"];
  const cellColor = (i, n) => `hsl(${Math.round((i * 300) / Math.max(1, n - 1))}, 72%, 62%)`;
  const RANGES = { "6h": 6 * 3600e3, "24h": 24 * 3600e3, "7d": 7 * 86400e3, "30d": 30 * 86400e3, "1y": 365 * 86400e3 };

  const niceTicks = (lo, hi, count = 4) => {
    if (!(hi > lo)) { hi = lo + 1; }
    const raw = (hi - lo) / count;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) || raw;
    const start = Math.floor(lo / step) * step; const end = Math.ceil(hi / step) * step;
    const out = [];
    for (let v = start; v <= end + step / 2; v += step) out.push(Number(v.toFixed(10)));
    return out;
  };
  const tsOf = (x) => (typeof x === "number" ? (x < 1e12 ? x * 1000 : x) : Date.parse(x));

  class Charts {
    constructor(host) { this.host = host; this.tab = null; this.range = "24h"; this.cache = {}; this.loading = null; this.err = null; this.hl = null; this.hover = null; }

    get t() {
      const h = this.host;
      const pick = (h._config.language && h._config.language !== "auto" ? h._config.language : (h._hass && h._hass.language)) || "en";
      return CH_TEXT[pick.split("-")[0]] || CH_TEXT.en;
    }

    tabsFor(mode) { return mode === "bank" ? ["soc", "power", "delta", "temp", "energy", "health"] : ["soc", "power", "cells", "delta", "temp", "volt", "energy", "health"]; }
    rangesFor(tab) { return tab === "energy" || tab === "health" ? ["7d", "30d", "1y"] : ["6h", "24h", "7d", "30d"]; }

    // ---- what to fetch for the current tab
    _plan(ctx) {
      const tab = this.tab; const e = ctx.entities || {}; const out = [];
      const add = (id, name, color, opts = {}) => { if (id) out.push({ id, name, color, ...opts }); };
      if (ctx.mode === "pack") {
        const n = ctx.cells || 16;
        if (tab === "soc") add(e.soc, this.host._t.soc, C.green, { unit: "%", min: 0, max: 100, area: true });
        if (tab === "power") add(e.power, this.host._t.power, C.blue, { unit: "W", split: true });
        if (tab === "cells") for (let i = 0; i < n; i++) add(e[`cell_voltage_${i + 1}`], `${this.host._t.cell} ${i + 1}`, cellColor(i, n), { unit: "V", cell: i, dec: 3 });
        if (tab === "delta") add(e.cell_delta, this.host._t.delta, C.amber, { unit: "mV", band: true, dec: 0 });
        if (tab === "temp") { add(e.mos_temperature, "MOS", C.red, { unit: "°C", dec: 1 }); for (let i = 0; i < 5; i++) add(e[`temperature_${i + 1}`], `T${i + 1}`, PACK_COLORS[i], { unit: "°C", dec: 1 }); }
        if (tab === "volt") { add(e.voltage, this.host._t.voltage, C.blue, { unit: "V", dec: 2 }); add(e.current, this.host._t.current, C.teal, { unit: "A", dec: 1, right: true }); }
        if (tab === "energy") { add(e.energy_charged, this.t.charged, C.green, { unit: "kWh", change: true }); add(e.energy_discharged, this.t.discharged, C.amber, { unit: "kWh", change: true, neg: true }); }
      } else {
        const packs = ctx.packs || [];
        if (tab === "soc") { add(e.bank_soc, this.t.bank, "#EDF0F4", { unit: "%", min: 0, max: 100, area: true, main: true }); packs.forEach((p, i) => add(p.entities.soc, p.name, PACK_COLORS[i % 8], { unit: "%", min: 0, max: 100 })); }
        if (tab === "power") { add(e.bank_power, this.t.bank, C.blue, { unit: "W", split: true, main: true }); packs.forEach((p, i) => add(p.entities.power, p.name, PACK_COLORS[(i + 1) % 8], { unit: "W" })); }
        if (tab === "delta") { add(e.bank_cell_delta, this.t.bank, "#EDF0F4", { unit: "mV", dec: 0, main: true }); packs.forEach((p, i) => add(p.entities.cell_delta, p.name, PACK_COLORS[i % 8], { unit: "mV", dec: 0 })); }
        if (tab === "temp") { add(e.bank_temperature_max, this.t.bank, C.red, { unit: "°C", dec: 1, main: true }); packs.forEach((p, i) => add(p.entities.mos_temperature, `${p.name} MOS`, PACK_COLORS[i % 8], { unit: "°C", dec: 1 })); }
        if (tab === "energy") { add(e.bank_energy_charged, this.t.charged, C.green, { unit: "kWh", change: true }); add(e.bank_energy_discharged, this.t.discharged, C.amber, { unit: "kWh", change: true, neg: true }); }
      }
      return out;
    }

    _key(ctx) { return `${ctx.mode}|${ctx.health || ""}|${this.tab}|${this.range}|${this._plan(ctx).map((s) => s.id).join(",")}`; }

    async _fetch(ctx, key) {
      const hass = this.host._hass;
      const now = Date.now();
      const span = RANGES[this.range];
      try {
        if (this.tab === "health") {
          const days = this.range === "7d" ? 7 : this.range === "30d" ? 30 : 365;
          const res = await hass.callWS({ type: "jk_bms_smart/health", entity_id: ctx.health, days });
          this.cache[key] = { at: now, health: res.packs || [] };
        } else {
          const plan = this._plan(ctx);
          if (!plan.length) { this.cache[key] = { at: now, series: [] }; return; }
          const change = plan.some((s) => s.change);
          const period = change ? (this.range === "1y" ? "month" : "day") : (span <= 24 * 3600e3 ? "5minute" : "hour");
          const res = await hass.callWS({
            type: "recorder/statistics_during_period",
            start_time: new Date(now - span).toISOString(), end_time: new Date(now).toISOString(),
            statistic_ids: plan.map((s) => s.id), period, types: change ? ["change"] : ["mean", "min", "max"],
          });
          const series = plan.map((s) => {
            const rows = (res && res[s.id]) || [];
            const pts = rows.map((r) => [tsOf(r.start), change ? r.change : r.mean, r.min, r.max]).filter((p) => p[1] != null && !isNaN(p[1]));
            if (!change) {
              const st = hass.states[s.id]; const v = st && parseFloat(st.state);
              if (st && !isNaN(v)) pts.push([now, v, v, v]); // live end point
            }
            return { ...s, pts, period };
          });
          this.cache[key] = { at: now, series, start: now - span, end: now, period };
        }
        this.err = null;
      } catch (err) {
        this.err = (err && err.message) || String(err);
        this.cache[key] = { at: now, series: [], failed: true };
      } finally {
        this.loading = null;
        this.host._sig = null; this.host._render();
      }
    }

    html(ctx) {
      const t = this.t;
      const tabs = this.tabsFor(ctx.mode);
      if (!tabs.includes(this.tab)) this.tab = tabs[0];
      if (!this.rangesFor(this.tab).includes(this.range)) this.range = this.rangesFor(this.tab)[1];
      this._charts = {};
      const key = this._key(ctx);
      const data = this.cache[key];
      const stale = !data || Date.now() - data.at > 5 * 60e3;
      if (stale && this.loading !== key) { this.loading = key; setTimeout(() => this._fetch(ctx, key), 0); }
      const nav = `<div class="ctabs">${tabs.map((x) => `<button class="ctab ${this.tab === x ? "sel" : ""}" data-act="ctab" data-v="${x}">${t.tabs[x]}</button>`).join("")}</div>
        <div class="cranges">${this.rangesFor(this.tab).map((r) => `<button class="crange ${this.range === r ? "sel" : ""}" data-act="crange" data-v="${r}">${r.replace("h", " u").replace("d", " d").replace("1y", "1 j")}</button>`).join("")}</div>`;
      let body;
      if (!data) body = `<div class="cempty">${t.loading}</div>`;
      else if (data.failed) body = `<div class="cempty">${t.failed}: ${esc(this.err || "")}</div>`;
      else if (this.tab === "health") body = this._healthHtml(ctx, data.health);
      else if (!data.series.some((s) => s.pts.length > 1)) body = `<div class="cempty">${t.none}</div>`;
      else if (this.tab === "energy") body = this._barsHtml(data);
      else body = this._lineHtml(ctx, data);
      this._last = data;
      return `<div class="charts">${nav}${body}</div>`;
    }

    // ---- line chart
    _lineHtml(ctx, data, opts = {}) {
      const series = data.series.filter((s) => s.pts.length);
      const left = series.filter((s) => !s.right); const right = series.filter((s) => s.right);
      const range = (list) => {
        let lo = Infinity; let hi = -Infinity;
        for (const s of list) for (const p of s.pts) {
          const a = s.band || s.cell != null ? Math.min(p[1], p[2] ?? p[1]) : p[1];
          const b = s.band || s.cell != null ? Math.max(p[1], p[3] ?? p[1]) : p[1];
          if (a < lo) lo = a; if (b > hi) hi = b;
        }
        const s0 = list[0] || {};
        if (s0.min != null) lo = Math.min(lo, s0.min);
        if (s0.max != null) hi = Math.max(hi, s0.max);
        if (s0.split) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
        if (s0.unit === "mV") lo = Math.min(lo, 0);
        if (s0.unit === "°C") { lo = Math.floor(lo - 2); hi = Math.ceil(hi + 2); }
        const pad = (hi - lo) * 0.06 || 0.01;
        return s0.min != null ? [s0.min, s0.max] : [lo - (s0.unit === "mV" && lo === 0 ? 0 : pad), hi + pad];
      };
      const [ylo0, yhi0] = range(left);
      const ticks = niceTicks(ylo0, yhi0, 4);
      const ylo = ticks[0]; const yhi = ticks[ticks.length - 1];
      let rticks = null; let rlo; let rhi;
      if (right.length) { const [a, b] = range(right); rticks = niceTicks(a, b, 4); rlo = rticks[0]; rhi = rticks[rticks.length - 1]; }
      const x0 = data.start; const x1 = data.end;
      const W = 1000; const H = 400;
      const X = (ts) => ((ts - x0) / (x1 - x0)) * W;
      const Y = (v, r) => (r ? H - ((v - rlo) / (rhi - rlo)) * H : H - ((v - ylo) / (yhi - ylo)) * H);
      const gapMs = ({ "5minute": 5 * 60e3, hour: 3600e3, day: 86400e3, month: 31 * 86400e3 }[data.period] || 3600e3) * 3.5;
      const path = (pts, idx, r) => {
        let d = ""; let prev = null;
        for (const p of pts) {
          if (p[idx] == null) continue;
          d += `${prev == null || p[0] - prev > gapMs ? "M" : "L"}${X(p[0]).toFixed(1)},${Y(p[idx], r).toFixed(1)}`;
          prev = p[0];
        }
        return d;
      };
      let svg = ticks.map((v) => `<line x1="0" x2="${W}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}" class="cgrid${v === 0 ? " zero" : ""}"/>`).join("");
      const hl = this.hl;
      for (const s of series) {
        const dim = hl != null && s.cell != null && s.cell !== hl;
        if (s.band && s.pts.length > 1) {
          const up = s.pts.map((p) => `${X(p[0]).toFixed(1)},${Y(p[3] ?? p[1]).toFixed(1)}`);
          const dn = s.pts.slice().reverse().map((p) => `${X(p[0]).toFixed(1)},${Y(p[2] ?? p[1]).toFixed(1)}`);
          svg += `<polygon points="${up.concat(dn).join(" ")}" fill="${s.color}" opacity=".16"/>`;
        }
        if (s.split) {
          const z = Y(0).toFixed(1);
          const pos = s.pts.map((p) => `${X(p[0]).toFixed(1)},${Y(Math.max(0, p[1])).toFixed(1)}`);
          const neg = s.pts.map((p) => `${X(p[0]).toFixed(1)},${Y(Math.min(0, p[1])).toFixed(1)}`);
          const first = X(s.pts[0][0]).toFixed(1); const last = X(s.pts[s.pts.length - 1][0]).toFixed(1);
          svg += `<polygon points="${first},${z} ${pos.join(" ")} ${last},${z}" fill="${C.green}" opacity=".28"/>`;
          svg += `<polygon points="${first},${z} ${neg.join(" ")} ${last},${z}" fill="${C.amber}" opacity=".28"/>`;
        } else if (s.area) {
          const d = path(s.pts, 1, s.right);
          if (d) svg += `<path d="${d} L${X(s.pts[s.pts.length - 1][0]).toFixed(1)},${H} L${X(s.pts[0][0]).toFixed(1)},${H} Z" fill="${s.color}" opacity=".12"/>`;
        }
        svg += `<path d="${path(s.pts, 1, s.right)}" fill="none" stroke="${s.split ? "var(--text)" : s.color}" stroke-width="${s.main || s.cell === hl ? 2.6 : s.cell != null ? 1.3 : 2}" vector-effect="non-scaling-stroke" opacity="${dim ? 0.18 : 1}" stroke-linejoin="round"/>`;
      }
      // reference lines
      if (opts.refs) for (const r of opts.refs) if (r.v > ylo && r.v < yhi) svg += `<line x1="0" x2="${W}" y1="${Y(r.v).toFixed(1)}" y2="${Y(r.v).toFixed(1)}" class="cref" stroke="${r.color}"/>`;
      const dec = left[0] && left[0].dec != null ? left[0].dec : (yhi - ylo) < 5 ? 2 : 0;
      const ylab = ticks.map((v) => `<span style="top:${((Y(v) / H) * 100).toFixed(2)}%">${num(v, Math.min(dec, (yhi - ylo) < 0.1 ? 3 : dec))}</span>`).join("");
      const rlab = rticks ? rticks.map((v) => `<span style="top:${((Y(v, true) / H) * 100).toFixed(2)}%">${num(v, 0)}</span>`).join("") : "";
      const xlab = this._xTicks(x0, x1).map(([ts, label], i) => `<span class="${i % 2 ? "odd" : ""}" style="left:${((X(ts) / W) * 100).toFixed(2)}%">${label}</span>`).join("");
      const id = `c${Math.random().toString(36).slice(2, 8)}`;
      this._charts = this._charts || {};
      this._charts[id] = { series, x0, x1, unitL: left[0] && left[0].unit, unitR: right[0] && right[0].unit };
      const legend = series.length > 1 ? `<div class="clegend">${series.map((s) => `<button class="lchip ${s.cell != null && hl === s.cell ? "sel" : ""}" ${s.cell != null ? `data-act="chl" data-v="${s.cell}"` : ""}><i style="background:${s.color}"></i>${esc(s.name)}</button>`).join("")}</div>` : "";
      const unit = `<div class="cunit"><span>${esc((left[0] && left[0].unit) || "")}</span><span>${esc((right[0] && right[0].unit) || "")}</span></div>`;
      const h = this.tab === "cells" ? 240 : 190;
      return `${unit}<div class="chart${rticks ? " dual" : ""}" style="height:${h}px">
          <div class="yax">${ylab}</div>
          <div class="plot" data-chart="${id}">
            <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${svg}</svg>
            <div class="hov"><i></i><div class="tip"></div></div>
          </div>
          ${rticks ? `<div class="yax r">${rlab}</div>` : ""}
          <div class="xax">${xlab}</div>
        </div>${legend}${this.tab === "cells" ? `<div class="chint">${this.t.tapCell}</div>` : ""}`;
    }

    _xTicks(x0, x1) {
      const span = x1 - x0; const out = [];
      const lang = (this.host._hass && this.host._hass.language) || "en";
      const d0 = new Date(x0);
      if (span <= 26 * 3600e3) {
        const step = span <= 7 * 3600e3 ? 1 : 3;
        const d = new Date(d0); d.setMinutes(0, 0, 0); d.setHours(d.getHours() + 1);
        while (d.getHours() % step) d.setHours(d.getHours() + 1);
        for (; d.getTime() < x1; d.setHours(d.getHours() + step)) out.push([d.getTime(), `${String(d.getHours()).padStart(2, "0")}:00`]);
      } else if (span <= 8 * 86400e3) {
        const d = new Date(d0); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + 1);
        for (; d.getTime() < x1; d.setDate(d.getDate() + 1)) out.push([d.getTime(), d.toLocaleDateString(lang, { weekday: "short" })]);
      } else if (span <= 40 * 86400e3) {
        const d = new Date(d0); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + 1);
        for (let i = 0; d.getTime() < x1; d.setDate(d.getDate() + 1), i++) if (d.getDay() === 1) out.push([d.getTime(), d.toLocaleDateString(lang, { day: "numeric", month: "short" })]);
      } else {
        const d = new Date(d0); d.setHours(0, 0, 0, 0); d.setDate(1); d.setMonth(d.getMonth() + 1);
        for (; d.getTime() < x1; d.setMonth(d.getMonth() + 1)) out.push([d.getTime(), d.toLocaleDateString(lang, { month: "short" })]);
      }
      return out;
    }

    // ---- bars: energy per day / month
    _barsHtml(data) {
      const pos = data.series.find((s) => !s.neg); const neg = data.series.find((s) => s.neg);
      const days = new Map();
      for (const s of [pos, neg]) if (s) for (const p of s.pts) { const k = p[0]; const r = days.get(k) || [0, 0]; r[s.neg ? 1 : 0] = Math.max(0, p[1] || 0); days.set(k, r); }
      const keys = [...days.keys()].sort((a, b) => a - b);
      if (!keys.length) return `<div class="cempty">${this.t.none}</div>`;
      const maxV = Math.max(...keys.map((k) => Math.max(...days.get(k))), 0.1);
      const ticks = niceTicks(0, maxV, 3); const top = ticks[ticks.length - 1];
      const lang = (this.host._hass && this.host._hass.language) || "en";
      const monthly = data.period === "month";
      const bw = 100 / keys.length;
      const bars = keys.map((k, i) => {
        const [a, b] = days.get(k);
        const d = new Date(k);
        const label = monthly ? d.toLocaleDateString(lang, { month: "short" }) : d.toLocaleDateString(lang, { day: "numeric", month: "short" });
        return `<div class="bcol" style="left:${(i * bw).toFixed(3)}%;width:${bw.toFixed(3)}%" data-tip="${esc(label)}: ↑ ${num(a, 1)} kWh · ↓ ${num(b, 1)} kWh">
          <i class="bup" style="height:${((a / top) * 50).toFixed(2)}%"></i><i class="bdn" style="height:${((b / top) * 50).toFixed(2)}%"></i></div>`;
      }).join("");
      const sumA = keys.reduce((s, k) => s + days.get(k)[0], 0); const sumB = keys.reduce((s, k) => s + days.get(k)[1], 0);
      const step = Math.ceil(keys.length / 7);
      const xlab = keys.map((k, i) => (i % step ? "" : `<span style="left:${((i + 0.5) * bw).toFixed(2)}%">${new Date(k).toLocaleDateString(lang, monthly ? { month: "short" } : { day: "numeric", month: "numeric" })}</span>`)).join("");
      return `<div class="csum"><span><i style="background:${C.green}"></i>${this.t.charged} <b>${num(sumA, 1)} kWh</b></span><span><i style="background:${C.amber}"></i>${this.t.discharged} <b>${num(sumB, 1)} kWh</b></span>${sumA > 0 ? `<span>η <b>${num((100 * sumB) / sumA, 0)}%</b></span>` : ""}</div>
        <div class="chart bars" style="height:190px">
          <div class="yax"><span style="top:0%">${num(top, 0)}</span><span style="top:50%">0</span><span style="top:100%">${num(top, 0)}</span></div>
          <div class="plot bplot"><i class="bmid"></i>${bars}<div class="btip"></div></div>
          <div class="xax">${xlab}</div>
        </div>`;
    }

    // ---- health
    _healthHtml(ctx, packs) {
      const t = this.t; const T = this.host._t;
      if (!packs.length) return `<div class="cempty">${t.none}</div>`;
      const blocks = packs.map((pk, pi) => {
        const w = pk.weak || {}; const days = pk.days || [];
        const n = (w.low_minutes || []).length || (days[days.length - 1] && days[days.length - 1].resistance_mohm.length) || 16;
        const summary = w.weakest
          ? `<div class="hsum bad"><ha-icon icon="mdi:battery-alert-variant-outline"></ha-icon><div><b>${t.weakest}: ${T.cell} ${w.weakest}</b><br>${t.weakTxt.replace("{cell}", w.weakest).replace("{share}", w.weakest_share)}${w.first_full ? `<br>${t.fullTxt.replace("{cell}", w.first_full).replace("{share}", w.first_full_share)}` : ""}</div></div>`
          : `<div class="hsum"><ha-icon icon="mdi:information-outline"></ha-icon><div>${t.weakNone}</div></div>`;
        const lows = w.low_minutes || [];
        const maxLow = Math.max(...lows, 1);
        const lowBars = lows.length && lows.some((x) => x > 0) ? `<div class="hlabel">${t.lowMinutes}</div><div class="hbars" style="grid-template-columns:repeat(${lows.length},1fr)">${lows.map((m, i) => `<div class="hbar ${w.weakest === i + 1 ? "weak" : ""}" title="${T.cell} ${i + 1}: ${m} min"><i style="height:${Math.max(2, (100 * m) / maxLow)}%"></i><span>${i + 1}</span></div>`).join("")}</div>` : "";
        const start = days.length ? Date.parse(days[0].day) : Date.now();
        const end = Date.now();
        const toPts = (fn) => days.map((d) => [Date.parse(d.day) + 12 * 3600e3, fn(d)]).filter((p) => p[1] != null);
        const deltaData = { start: start - 12 * 3600e3, end, period: "day", series: [{ name: T.delta, color: C.amber, unit: "mV", dec: 0, area: true, pts: toPts((d) => d.delta_max_mv) }] };
        const resSeries = []; for (let i = 0; i < n; i++) resSeries.push({ name: `${T.cell} ${i + 1}`, color: cellColor(i, n), unit: "mΩ", dec: 1, cell: i, pts: toPts((d) => (d.resistance_mohm && d.resistance_mohm.length > i ? d.resistance_mohm[i] : null)) });
        const resData = { start: start - 12 * 3600e3, end, period: "day", series: resSeries };
        const saveTab = this.tab; this.tab = "health-sub";
        const deltaChart = deltaData.series[0].pts.length > 1 ? `<div class="hlabel">${t.deltaDays}</div>${this._lineHtml(ctx, deltaData)}` : "";
        const resChart = resSeries.some((s) => s.pts.length > 1) ? `<div class="hlabel">${t.resDays}</div>${this._lineHtml(ctx, resData)}` : "";
        this.tab = saveTab;
        const allowReset = ctx.allowChanges;
        return `<div class="hpack">${packs.length > 1 ? `<div class="hname" style="color:${PACK_COLORS[pi % 8]}">${esc(pk.name)}</div>` : ""}${summary}${lowBars}${deltaChart}${resChart}
          ${allowReset && pk.entity ? `<div class="hfoot"><button class="lchip" data-act="hreset" data-entity="${esc(pk.entity)}">${t.reset}</button></div>` : ""}</div>`;
      });
      return blocks.join("");
    }

    // ---- interaction
    click(el, ctx) {
      const act = el.dataset.act;
      if (act === "ctab") { this.tab = el.dataset.v; this.hl = null; }
      else if (act === "crange") { this.range = el.dataset.v; }
      else if (act === "chl") { const v = Number(el.dataset.v); this.hl = this.hl === v ? null : v; }
      else if (act === "hreset") {
        if (!confirm(this.t.resetConfirm)) return true;
        this.host._hass.callService("jk_bms_smart", "reset_cell_statistics", { entity_id: el.dataset.entity })
          .then(() => { this.cache = {}; this.host._sig = null; this.host._render(); });
        return true;
      } else return false;
      this.host._sig = null; this.host._render();
      return true;
    }

    move(e) {
      const plot = e.target.closest && e.target.closest(".plot");
      if (!plot) return;
      if (plot.classList.contains("bplot")) {
        const col = e.target.closest(".bcol"); const tip = plot.querySelector(".btip");
        if (!tip) return;
        if (!col) { tip.style.display = "none"; return; }
        tip.textContent = col.dataset.tip; tip.style.display = "block";
        const r = plot.getBoundingClientRect(); const cr = col.getBoundingClientRect();
        tip.style.left = `${Math.min(r.width - 150, Math.max(0, cr.left - r.left - 60))}px`;
        return;
      }
      const c = this._charts && this._charts[plot.dataset.chart];
      if (!c) return;
      const r = plot.getBoundingClientRect();
      const fx = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
      const ts = c.x0 + fx * (c.x1 - c.x0);
      const hov = plot.querySelector(".hov"); const tip = plot.querySelector(".tip");
      const rows = []; let best = null;
      for (const s of c.series) {
        let p = null; let bd = Infinity;
        for (const q of s.pts) { const d = Math.abs(q[0] - ts); if (d < bd) { bd = d; p = q; } }
        if (!p || bd > (c.x1 - c.x0) / 20) continue;
        if (!best || Math.abs(p[0] - ts) < Math.abs(best - ts)) best = p[0];
        rows.push([s, p]);
      }
      if (!rows.length) { hov.style.display = "none"; return; }
      const lang = (this.host._hass && this.host._hass.language) || "en";
      const span = c.x1 - c.x0;
      const when = new Date(best).toLocaleString(lang, span > 26 * 3600e3 ? { weekday: "short", day: "numeric", month: "short", hour: span > 8 * 86400e3 ? undefined : "2-digit", minute: span > 8 * 86400e3 ? undefined : "2-digit" } : { hour: "2-digit", minute: "2-digit" });
      let list = rows;
      if (rows.length > 6) {
        const sorted = rows.slice().sort((a, b) => b[1][1] - a[1][1]);
        list = this.hl != null ? sorted.filter(([s]) => s.cell === this.hl).concat(sorted.slice(0, 2), sorted.slice(-2)) : sorted.slice(0, 3).concat(sorted.slice(-3));
        list = list.filter((x, i, arr) => arr.indexOf(x) === i);
      }
      tip.innerHTML = `<b>${esc(when)}</b>${list.map(([s, p]) => `<div><i style="background:${s.color}"></i>${esc(s.name)}<em>${num(p[1], s.dec != null ? s.dec : (s.unit === "W" ? 0 : 1))} ${esc(s.unit || "")}${s.band && p[2] != null ? ` <small>(${num(p[2], s.dec || 0)}–${num(p[3], s.dec || 0)})</small>` : ""}</em></div>`).join("")}`;
      hov.style.display = "block";
      const x = ((best - c.x0) / (c.x1 - c.x0)) * r.width;
      hov.querySelector("i").style.left = `${x}px`;
      const tw = tip.offsetWidth || 160;
      tip.style.left = `${x + 12 + tw > r.width ? Math.max(0, x - tw - 12) : x + 12}px`;
    }

    leave(e) {
      const root = this.host.shadowRoot; if (!root) return;
      if (e && e.relatedTarget && root.contains(e.relatedTarget) && e.relatedTarget.closest && e.relatedTarget.closest(".plot")) return;
      root.querySelectorAll(".hov, .btip").forEach((el) => { el.style.display = "none"; });
    }
  }

  // The stand-alone chart card: one pack or the whole bank.
  class JkChartCard extends JkBase {
    static getStubConfig(hass) {
      const e = Object.keys(hass.states).find((id) => hass.states[id].attributes && hass.states[id].attributes.bank);
      return { entity: e || "" };
    }

    setConfig(config) {
      super.setConfig(config);
      this._charts = this._charts || new Charts(this);
      if (config && config.chart) this._charts.tab = config.chart;
      if (config && config.range) this._charts.range = config.range;
    }

    set hass(hass) {
      this._hass = hass;
      const st = this._config && hass.states[this._config.entity];
      if (st && st.attributes && (st.attributes.pack || st.attributes.bank)) this._lastAttrs = st.attributes;
      if (this._card && this._card.isConnected && this._drawnOnce) return; // charts refresh on their own every 5 min
      this._render();
      this._drawnOnce = !!this._ctx();
    }

    _ctx() {
      const a = this._stateAttrs(this._config.entity);
      if (!a) return null;
      if (a.pack) return { mode: "pack", entities: a.pack.entities || {}, cells: (a.pack.cells || []).length || 16, health: this._config.entity, name: a.pack.name, allowChanges: a.pack.allow_changes, data: a.pack };
      const b = a.bank;
      const packs = (b.packs || []).map((x) => {
        const p = x.entity && this._hass.states[x.entity] && this._hass.states[x.entity].attributes.pack;
        return { name: x.name, entity: x.entity, entities: (p && p.entities) || {} };
      });
      return { mode: "bank", entities: b.entities || {}, packs, health: this._config.entity, allowChanges: b.allow_changes, data: b };
    }

    _render() {
      if (!this._hass || !this._config) return;
      const t = this._t;
      const ctx = this._ctx();
      if (!ctx) { this._shell(`<div class="empty">${t.noData}</div>`, null, t); return; }
      const title = this._config.name || (ctx.mode === "pack" ? ctx.name : t.bankTitle);
      this._shell(`<div class="head"><div class="htitle"><div class="name">${esc(title)}</div></div></div>${this._charts.html(ctx)}`, ctx.data, t);
      clearTimeout(this._refresh);
      this._refresh = setTimeout(() => { this._sig = null; this._render(); }, 5 * 60e3 + 500);
    }

    _onClick(e) {
      const el = e.target.closest("[data-act]");
      if (el && this._charts.click(el, this._ctx())) return;
      super._onClick(e);
    }

    disconnectedCallback() { clearTimeout(this._refresh); }
    getCardSize() { return 6; }
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
    .schips { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 12px; }
    .schip { background:var(--panel); border:1px solid transparent; color:var(--muted); border-radius:999px; padding:6px 12px; font:inherit; font-size:.82rem; cursor:pointer; }
    .schip.sel { color:var(--text); border-color:var(--accent); background:color-mix(in srgb, var(--accent) 14%, transparent); }
    .shint { font-size:.76rem; color:var(--muted); margin:0 0 12px; }
    .smsg { border-radius:10px; padding:8px 12px; margin:0 0 12px; font-size:.82rem; }
    .smsg.ok { background:rgba(69,214,154,.12); border:1px solid rgba(69,214,154,.4); }
    .smsg.bad { background:rgba(255,92,97,.12); border:1px solid rgba(255,92,97,.45); }
    .sgroup { background:var(--panel); border-radius:14px; padding:6px 12px; margin-bottom:10px; }
    .sgtitle { font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); padding:8px 0 4px; }
    .srow2 { display:grid; grid-template-columns:minmax(0,1fr) auto; align-items:center; column-gap:10px; padding:8px 0; border-top:1px solid var(--line); font-size:.86rem; }
    .srow2 > span:first-child { min-width:0; overflow-wrap:anywhere; hyphens:auto; -webkit-hyphens:auto; line-height:1.3; }
    .sgtitle + .srow2 { border-top:0; }
    .sdiff { font-style:normal; font-size:.68rem; color:#F4B740; margin-left:4px; }
    .sedit { display:grid; grid-template-columns:84px 28px 72px; align-items:center; gap:6px; justify-self:end; }
    .sedit input { width:100%; box-sizing:border-box; background:var(--bg); color:var(--text); border:1px solid var(--line); border-radius:8px; padding:6px 8px; font:inherit; text-align:right; font-variant-numeric:tabular-nums; }
    .sedit input:focus { outline:none; border-color:var(--accent); }
    .sedit small { color:var(--muted); font-size:.74rem; }
    .sbtn { width:100%; background:var(--accent); color:#06121F; border:0; border-radius:8px; padding:6px 4px; font:inherit; font-size:.78rem; font-weight:600; cursor:pointer; }
    .sbtn:disabled, .sedit input:disabled, .tog:disabled { opacity:.45; cursor:not-allowed; }
    .tog { width:44px; height:24px; border-radius:12px; border:0; background:#3A4250; position:relative; cursor:pointer; justify-self:end; }
    @container (max-width: 380px) { .sedit { grid-template-columns:72px 24px 64px; gap:4px; } .srow2 { font-size:.8rem; } }
    .tog i { position:absolute; top:3px; left:3px; width:18px; height:18px; border-radius:50%; background:#EDF0F4; transition:left .2s; }
    .tog.on { background:#45D69A; } .tog.on i { left:23px; }
    @container (max-width: 420px) { .hero, .bankhero { flex-direction:column; align-items:stretch; } .ringwrap { margin:0 auto; } }
    .tabs { overflow-x:auto; scrollbar-width:none; } .tabs::-webkit-scrollbar { display:none; } .tab { white-space:nowrap; }
    @container (max-width: 420px) { .tabs { gap:14px; } }
    .weak circle { fill:#F4B740; stroke:rgba(0,0,0,.4); } .weak text { font-size:10px; font-weight:800; text-anchor:middle; fill:#14181E; }
    .note { display:flex; align-items:center; gap:8px; margin-top:10px; font-size:.8rem; color:#F4B740; background:rgba(244,183,64,.1); border-radius:10px; padding:7px 10px; }
    .note ha-icon { --mdc-icon-size:18px; }
    /* charts */
    .charts { display:flex; flex-direction:column; gap:8px; }
    .ctabs { display:flex; gap:6px; overflow-x:auto; scrollbar-width:none; padding-bottom:2px; }
    .ctabs::-webkit-scrollbar { display:none; }
    .ctab, .crange, .lchip { background:var(--panel); border:1px solid transparent; color:var(--muted); border-radius:999px; padding:5px 11px; font:inherit; font-size:.78rem; cursor:pointer; white-space:nowrap; }
    .ctab.sel, .crange.sel, .lchip.sel { color:var(--text); border-color:var(--accent); background:color-mix(in srgb, var(--accent) 14%, transparent); }
    .cranges { display:flex; gap:6px; justify-content:flex-end; }
    .crange { padding:3px 9px; font-size:.72rem; }
    .cempty { color:var(--muted); text-align:center; padding:40px 8px; font-size:.85rem; }
    .cunit { display:flex; justify-content:space-between; font-size:.68rem; color:var(--muted); margin-bottom:-4px; }
    .chart { position:relative; display:grid; grid-template-columns:38px 1fr; grid-template-rows:1fr 18px; }
    .chart.dual { grid-template-columns:38px 1fr 34px; }
    .yax { position:relative; grid-row:1; font-size:.64rem; color:var(--muted); font-variant-numeric:tabular-nums; }
    .yax span { position:absolute; right:6px; transform:translateY(-50%); white-space:nowrap; }
    .yax.r span { right:auto; left:6px; }
    .plot { position:relative; grid-row:1; grid-column:2; border-left:1px solid var(--line); border-bottom:1px solid var(--line); touch-action:pan-y; cursor:crosshair; }
    .plot svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
    .cgrid { stroke:var(--line); stroke-width:1; vector-effect:non-scaling-stroke; } .cgrid.zero { stroke:var(--muted); stroke-dasharray:3 3; }
    .cref { stroke-width:1; stroke-dasharray:5 4; vector-effect:non-scaling-stroke; }
    .xax { position:relative; grid-row:2; grid-column:2; font-size:.64rem; color:var(--muted); }
    .xax span { position:absolute; top:3px; transform:translateX(-50%); white-space:nowrap; }
    @container (max-width: 420px) { .xax span.odd { display:none; } }
    .hov { display:none; position:absolute; inset:0; pointer-events:none; }
    .hov > i { position:absolute; top:0; bottom:0; width:1px; background:var(--muted); opacity:.7; }
    .tip, .btip { position:absolute; top:4px; background:color-mix(in srgb, var(--bg) 92%, transparent); border:1px solid var(--line); border-radius:10px; padding:7px 9px; font-size:.72rem; min-width:130px; max-width:220px; box-shadow:0 6px 18px rgba(0,0,0,.25); pointer-events:none; z-index:2; }
    .tip b { display:block; margin-bottom:3px; font-size:.72rem; }
    .tip div { display:flex; align-items:center; gap:6px; white-space:nowrap; }
    .tip div i { width:8px; height:8px; border-radius:50%; flex:none; }
    .tip em { font-style:normal; margin-left:auto; padding-left:8px; font-weight:600; font-variant-numeric:tabular-nums; }
    .tip small { color:var(--muted); font-weight:400; }
    .btip { display:none; white-space:nowrap; }
    .clegend { display:flex; flex-wrap:wrap; gap:5px; margin-top:4px; }
    .lchip { display:inline-flex; align-items:center; gap:5px; padding:3px 8px; font-size:.7rem; }
    .lchip i { width:8px; height:8px; border-radius:50%; }
    .chint { font-size:.68rem; color:var(--muted); text-align:right; }
    .bplot { cursor:default; }
    .bmid { position:absolute; left:0; right:0; top:50%; height:1px; background:var(--muted); opacity:.5; }
    .bcol { position:absolute; top:0; bottom:0; }
    .bcol:hover { background:color-mix(in srgb, var(--text) 6%, transparent); }
    .bcol i { position:absolute; left:18%; right:18%; border-radius:3px; }
    .bup { bottom:50%; background:#45D69A; } .bdn { top:50%; background:#F4B740; }
    .csum { display:flex; flex-wrap:wrap; gap:12px; font-size:.78rem; color:var(--muted); }
    .csum i { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; }
    .csum b { color:var(--text); }
    .hpack { display:flex; flex-direction:column; gap:8px; padding-bottom:6px; }
    .hpack + .hpack { border-top:1px solid var(--line); padding-top:12px; }
    .hname { font-weight:700; font-size:.9rem; }
    .hsum { display:flex; gap:10px; align-items:flex-start; background:var(--panel); border-radius:12px; padding:9px 12px; font-size:.82rem; line-height:1.35; }
    .hsum ha-icon { --mdc-icon-size:20px; color:var(--muted); flex:none; }
    .hsum.bad ha-icon { color:#F4B740; }
    .hlabel { font-size:.72rem; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); margin-top:4px; }
    .hbars { display:grid; gap:3px; height:90px; align-items:end; }
    .hbar { display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; gap:2px; }
    .hbar i { display:block; width:100%; max-width:22px; background:var(--muted); border-radius:4px 4px 2px 2px; opacity:.6; }
    .hbar.weak i { background:#F4B740; opacity:1; }
    .hbar span { font-size:.6rem; color:var(--muted); }
    .hfoot { display:flex; justify-content:flex-end; }
    /* settings card extras */
    .sgroup.sync { border:1px solid rgba(244,183,64,.45); }
    .syncmsg { display:flex; gap:8px; align-items:flex-start; font-size:.82rem; padding:4px 0 8px; }
    .syncmsg ha-icon { --mdc-icon-size:18px; color:#F4B740; flex:none; }
    .syncrow { display:flex; flex-wrap:wrap; align-items:center; gap:6px; font-size:.8rem; color:var(--muted); margin-bottom:10px; }
    .sbtn.wide { width:100%; padding:9px; margin:4px 0 8px; }
    .sbtn.ghost { background:transparent; color:var(--accent); border:1px solid var(--accent); }
    .srow2 > b { justify-self:end; font-variant-numeric:tabular-nums; }
    .sdiff.muted { color:var(--muted); }
    .switches.ro { padding:8px 0 6px; margin:0; border-top:1px solid var(--line); }
    .sgroup.preview { border:1px solid var(--accent); }
    .pvpack { padding:6px 0; border-top:1px solid var(--line); font-size:.84rem; }
    .pvpack > b { display:block; margin-bottom:4px; }
    .pvrow { display:flex; justify-content:space-between; gap:10px; padding:2px 0; color:var(--muted); }
    .pvrow em { font-style:normal; color:var(--text); white-space:nowrap; font-variant-numeric:tabular-nums; }
    .pvbtns { display:flex; justify-content:flex-end; gap:8px; padding:10px 0 6px; }
    .pvbtns .sbtn { width:auto; padding:7px 14px; }
  `;

  const DEFS = [
    ["jk-bms-smart-pack-card", JkPackCard],
    ["jk-bms-smart-bank-card", JkBankCard],
    ["jk-bms-smart-settings-card", JkSettingsCard],
    ["jk-bms-smart-chart-card", JkChartCard],
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
    ["jk-bms-smart-settings-card", "JK BMS Smart – Instellingen / Settings", "Change BMS settings per pack or for all packs at once, make packs equal, back up and restore."],
    ["jk-bms-smart-chart-card", "JK BMS Smart – Grafieken / Charts", "Charge, power, all cells, cell difference, temperature, energy per day and pack health over 6 hours to a year."],
  ]) {
    if (!window.customCards.some((c) => c.type === type)) {
      window.customCards.push({ type, name, description, preview: true, documentationURL: "https://github.com/George-120/ha-jk-bms-smart" });
    }
  }
  console.info(`%c JK-BMS-SMART %c ${VERSION} `, "background:#45D69A;color:#06121F;font-weight:600", "background:#14181E;color:#EDF0F4");
  void BASE;
})();
