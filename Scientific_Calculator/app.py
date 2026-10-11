"""
Scientific Calculator — Single-file Streamlit app
All HTML, CSS, and JavaScript are embedded in this file.
No external assets are required; deploys cleanly on Streamlit Community Cloud.
"""

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Scientific Calculator",
    page_icon="🧮",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Hide default Streamlit chrome so the calculator fills the viewport cleanly
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Remove top padding and default Streamlit footer */
        .block-container { padding-top: 1rem; padding-bottom: 0; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# The full self-contained calculator HTML / CSS / JS
# ---------------------------------------------------------------------------
CALCULATOR_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scientific Calculator</title>
  <style>
    :root {
      color-scheme: light;
      --paper: #f3f5f3;
      --surface: #ffffff;
      --ink: #222b29;
      --muted: #78817d;
      --line: #e7ebe8;
      --accent: #167d68;
      --accent-soft: #e5f2ed;
      --key: #f5f7f5;
      --shadow: 0 24px 70px rgba(38,57,49,.11), 0 3px 10px rgba(38,57,49,.05);
      font-family: "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 14px 30px;
      color: var(--ink);
      background: var(--paper);
      background-image: radial-gradient(#dbe4de 0.7px, transparent 0.7px);
      background-size: 18px 18px;
    }

    /* ── Calculator card ── */
    .calculator {
      width: min(100%, 660px);
      overflow: hidden;
      border: 1px solid rgba(255,255,255,.8);
      border-radius: 24px;
      background: var(--surface);
      box-shadow: var(--shadow);
      animation: arrive .4s ease-out both;
    }
    @keyframes arrive {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Top bar ── */
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 22px 14px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .3px;
    }
    .brand-mark {
      display: grid;
      width: 30px; height: 30px;
      place-items: center;
      border-radius: 9px;
      color: white;
      background: var(--accent);
      font-family: Georgia, serif;
      font-size: 18px;
      font-style: italic;
    }
    .brand small {
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-size: 9px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .6px;
    }

    /* ── DEG / RAD toggle ── */
    .mode-switch {
      display: flex;
      gap: 2px;
      padding: 3px;
      border: 1px solid var(--line);
      border-radius: 9px;
      background: #f8f9f8;
    }
    .mode-switch button {
      min-width: 42px; height: 27px;
      border: 0; border-radius: 6px;
      color: var(--muted);
      background: transparent;
      font: inherit; font-size: 10px; font-weight: 700;
      cursor: pointer; transition: all .15s;
    }
    .mode-switch button[aria-pressed="true"] {
      color: var(--accent);
      background: white;
      box-shadow: 0 1px 4px rgba(30,45,39,.13);
    }

    /* ── Tab nav ── */
    .view-nav {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 4px;
      margin: 0 18px 12px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 11px;
      background: #f7f9f7;
    }
    .view-nav button {
      min-height: 34px;
      border: 0; border-radius: 7px;
      color: var(--muted);
      background: transparent;
      font: inherit; font-size: 12px; font-weight: 650;
      cursor: pointer; transition: all .15s;
    }
    .view-nav button[aria-selected="true"] {
      color: var(--accent);
      background: white;
      box-shadow: 0 1px 4px rgba(30,45,39,.1);
    }

    /* ── Panels ── */
    .view[hidden] { display: none !important; }

    /* ── Display ── */
    .display {
      min-height: 118px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 12px 22px 18px;
      border-top: 1px solid #f2f4f2;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(145deg, #fbfcfb, #f5f8f6);
    }
    .display-label {
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: .6px;
    }
    #expression {
      width: 100%;
      min-height: 40px;
      border: 0; outline: 0; padding: 0;
      color: var(--ink);
      background: transparent;
      font: 400 28px/1.3 "Segoe UI", system-ui, sans-serif;
      text-align: right;
      caret-color: var(--accent);
    }
    .result-line {
      min-height: 22px;
      margin-top: 5px;
      color: var(--accent);
      font-size: 15px; font-weight: 600;
      text-align: right;
      overflow-wrap: anywhere;
    }
    .result-line.error { color: #bd5146; font-size: 12px; }

    /* ── Scientific function grid ── */
    .sci-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 6px;
      padding: 14px 18px 6px;
    }
    .sci-grid .key { height: 38px; font-size: 11px; }

    /* ── Main keypad ── */
    .keypad { padding: 10px 18px 18px; }
    .key-row {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 8px;
    }
    .key-row:last-child { margin-bottom: 0; }

    /* ── Keys ── */
    .key {
      min-width: 0; height: 50px;
      border: 1px solid transparent;
      border-radius: 12px;
      color: var(--ink);
      background: var(--key);
      font: 500 15px/1 "Segoe UI", system-ui, sans-serif;
      cursor: pointer;
      transition: transform .1s, background .1s, box-shadow .1s;
      touch-action: manipulation;
      -webkit-tap-highlight-color: transparent;
    }
    .key:hover { background: #eaf0ec; }
    .key:active { transform: scale(.94); }
    .key:focus-visible {
      outline: 3px solid rgba(22,125,104,.3);
      outline-offset: 2px;
    }
    .key.function {
      color: #2e6b5d; background: #eef5f1;
      font-size: 12px; font-weight: 650;
    }
    .key.operator {
      color: var(--accent); background: var(--accent-soft);
      font-size: 20px;
    }
    .key.utility {
      color: #6c7772; background: #eff1f0;
      font-size: 12px; font-weight: 700;
    }
    .key.equals {
      color: white; background: var(--accent);
      font-size: 22px;
      box-shadow: 0 4px 10px rgba(22,125,104,.22);
    }
    .key.equals:hover { background: #116d5b; }

    /* ── History ── */
    .history-wrap {
      padding: 0 18px 16px;
      border-top: 1px solid var(--line);
    }
    .history-wrap summary {
      padding: 12px 0 4px;
      color: var(--muted); font-size: 12px; font-weight: 650;
      cursor: pointer; user-select: none;
    }
    #history-list {
      display: grid; gap: 6px;
      margin: 8px 0 0; padding-left: 18px;
      color: var(--ink); font-size: 12px;
    }
    #history-list li { overflow-wrap: anywhere; }

    /* ── Trig / Calculus panel shared ── */
    .view-content { padding: 12px 22px 24px; }
    .view-title { margin: 8px 0 16px; font-size: 19px; font-weight: 700; }
    .section-label {
      margin: 20px 0 8px;
      color: var(--muted); font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: .5px;
    }

    .tool-row {
      display: flex; align-items: flex-end; gap: 12px; margin: 12px 0;
    }
    .tool-field { display: grid; flex: 1; gap: 5px; min-width: 0; }
    .tool-field label, .tool-label {
      color: var(--muted); font-size: 11px; font-weight: 650;
    }
    .tool-field input, .tool-field select {
      width: 100%; min-height: 40px; padding: 0 11px;
      border: 1px solid var(--line); border-radius: 8px;
      color: var(--ink); background: #fbfcfb;
      font: inherit; font-size: 14px;
    }
    .tool-field input:focus, .tool-field select:focus {
      outline: 2px solid rgba(22,125,104,.35); border-color: var(--accent);
    }

    .unit-switch {
      display: flex; gap: 3px; padding: 3px;
      border: 1px solid var(--line); border-radius: 9px; background: #f7f9f7;
    }
    .unit-switch button {
      min-height: 30px; padding: 0 10px;
      border: 0; border-radius: 6px;
      color: var(--muted); background: transparent;
      font: inherit; font-size: 11px; cursor: pointer; transition: all .15s;
    }
    .unit-switch button[aria-pressed="true"] {
      color: var(--accent); background: white;
      box-shadow: 0 1px 3px rgba(30,45,39,.1);
    }

    .angle-summary {
      margin: 10px 0 16px;
      color: var(--accent); font-size: 13px; font-weight: 600;
    }

    .value-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .value-table th, .value-table td {
      padding: 8px 8px; border-bottom: 1px solid var(--line); text-align: left;
    }
    .value-table th {
      color: var(--muted); font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: .4px;
    }
    .value-table td:last-child, .value-table th:last-child {
      text-align: right; font-variant-numeric: tabular-nums;
    }
    .value-table td:first-child { font-weight: 600; }

    .tool-button {
      min-height: 40px; padding: 0 20px; margin-top: 14px;
      border: 0; border-radius: 8px;
      color: white; background: var(--accent);
      font: inherit; font-size: 13px; font-weight: 700;
      cursor: pointer; transition: background .15s;
    }
    .tool-button:hover { background: #116d5b; }

    .tool-result {
      min-height: 44px; margin-top: 14px; padding: 12px 14px;
      border-left: 3px solid var(--accent);
      color: var(--accent); background: #f2f8f5;
      font-size: 13px; font-weight: 600;
      overflow-wrap: anywhere;
    }
    .tool-result.error { border-color: #bd5146; color: #a33f36; background: #fcf4f3; }

    .tool-hint { margin-top: 6px; color: var(--muted); font-size: 11px; line-height: 1.55; }

    /* ── Footer ── */
    .calc-footer {
      padding: 0 18px 15px;
      color: #9aa29e; font-size: 10px; text-align: center;
    }

    /* ── Responsive ── */
    @media (max-width: 380px) {
      body { padding: 10px 8px 20px; }
      .sci-grid { grid-template-columns: repeat(4, 1fr); padding: 10px 12px 4px; }
      .key-row { gap: 6px; }
      .keypad { padding: 8px 12px 14px; }
      .key { height: 46px; border-radius: 10px; }
      #expression { font-size: 24px; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }
  </style>
</head>
<body>
  <main class="calculator" aria-label="Scientific calculator">

    <!-- Top bar: brand + DEG/RAD -->
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">&#x192;</span>
        <span>SCIENTIFIC<small>Calculator</small></span>
      </div>
      <div class="mode-switch" role="group" aria-label="Angle mode">
        <button type="button" data-mode="DEG" aria-pressed="true">DEG</button>
        <button type="button" data-mode="RAD" aria-pressed="false">RAD</button>
      </div>
    </header>

    <!-- Tab navigation -->
    <nav class="view-nav" role="tablist" aria-label="Sections">
      <button type="button" role="tab" aria-selected="true"  data-view="calculator"   id="tab-calc">Calculator</button>
      <button type="button" role="tab" aria-selected="false" data-view="trigonometry" id="tab-trig">Trigonometry</button>
      <button type="button" role="tab" aria-selected="false" data-view="calculus"     id="tab-calc2">Calculus</button>
    </nav>

    <!-- ═══════════════════════ CALCULATOR TAB ═══════════════════════ -->
    <section class="view" id="view-calculator" role="tabpanel" aria-labelledby="tab-calc">

      <!-- Display -->
      <div class="display" aria-label="Calculator display">
        <div class="display-label">Expression</div>
        <input id="expression" type="text" inputmode="decimal"
               autocomplete="off" spellcheck="false" aria-label="Expression" autofocus>
        <output id="result" class="result-line" aria-live="polite"></output>
      </div>

      <!-- Scientific function grid (2 rows × 6) -->
      <div class="sci-grid" aria-label="Scientific functions">
        <button class="key function" data-insert="sin("  aria-label="Sine">sin</button>
        <button class="key function" data-insert="cos("  aria-label="Cosine">cos</button>
        <button class="key function" data-insert="tan("  aria-label="Tangent">tan</button>
        <button class="key function" data-insert="cot("  aria-label="Cotangent">cot</button>
        <button class="key function" data-insert="sec("  aria-label="Secant">sec</button>
        <button class="key function" data-insert="csc("  aria-label="Cosecant">csc</button>

        <button class="key function" data-insert="asin(" aria-label="Inverse sine">sin⁻¹</button>
        <button class="key function" data-insert="acos(" aria-label="Inverse cosine">cos⁻¹</button>
        <button class="key function" data-insert="atan(" aria-label="Inverse tangent">tan⁻¹</button>
        <button class="key function" data-insert="sinh(" aria-label="Hyperbolic sine">sinh</button>
        <button class="key function" data-insert="cosh(" aria-label="Hyperbolic cosine">cosh</button>
        <button class="key function" data-insert="tanh(" aria-label="Hyperbolic tangent">tanh</button>

        <button class="key function" data-insert="log("  aria-label="Base-10 log">log</button>
        <button class="key function" data-insert="ln("   aria-label="Natural log">ln</button>
        <button class="key function" data-insert="sqrt(" aria-label="Square root">&#x221A;</button>
        <button class="key function" data-insert="exp("  aria-label="Exponential">exp</button>
        <button class="key function" data-insert="fact(" aria-label="Factorial">n!</button>
        <button class="key function" data-insert="abs("  aria-label="Absolute value">|x|</button>

        <button class="key function" data-insert="floor(" aria-label="Floor">&#x230A;x&#x230B;</button>
        <button class="key function" data-insert="ceil("  aria-label="Ceiling">&#x2308;x&#x2309;</button>
        <button class="key function" data-insert="pow("   aria-label="Power function">pow</button>
        <button class="key function" data-insert="pi"     aria-label="Pi">&#x03C0;</button>
        <button class="key function" data-insert="e"      aria-label="Euler's number">e</button>
        <button class="key function" data-insert="^"      aria-label="Power">x&#x02B8;</button>
      </div>

      <!-- Main keypad (5 × 5) -->
      <section class="keypad" aria-label="Calculator keys">
        <div class="key-row">
          <button class="key utility" data-action="clear">AC</button>
          <button class="key utility" data-action="delete" aria-label="Delete">&#x232B;</button>
          <button class="key function" data-insert="(">(</button>
          <button class="key function" data-insert=")">)</button>
          <button class="key function" data-insert="%">%</button>
        </div>
        <div class="key-row">
          <button class="key" data-insert="7">7</button>
          <button class="key" data-insert="8">8</button>
          <button class="key" data-insert="9">9</button>
          <button class="key operator" data-insert="/" aria-label="Divide">&#xF7;</button>
          <button class="key operator" data-insert="*" aria-label="Multiply">&#xD7;</button>
        </div>
        <div class="key-row">
          <button class="key" data-insert="4">4</button>
          <button class="key" data-insert="5">5</button>
          <button class="key" data-insert="6">6</button>
          <button class="key operator" data-insert="-" aria-label="Subtract">&#x2212;</button>
          <button class="key operator" data-insert="+" aria-label="Add">+</button>
        </div>
        <div class="key-row">
          <button class="key" data-insert="1">1</button>
          <button class="key" data-insert="2">2</button>
          <button class="key" data-insert="3">3</button>
          <button class="key function" data-insert="ans">ANS</button>
          <button class="key equals" data-action="equals" aria-label="Calculate">=</button>
        </div>
        <div class="key-row">
          <button class="key" data-insert="0">0</button>
          <button class="key" data-insert=".">.</button>
          <button class="key function" data-insert="pi">&#x03C0;</button>
          <button class="key function" data-insert="e">e</button>
          <button class="key utility" data-action="clear-history">&#x1F5D1;</button>
        </div>
      </section>

      <!-- History -->
      <details class="history-wrap">
        <summary>&#x1F4CB; History</summary>
        <ol id="history-list"></ol>
      </details>
    </section>

    <!-- ════════════════════ TRIGONOMETRY TAB ════════════════════ -->
    <section class="view view-content" id="view-trigonometry" role="tabpanel"
             aria-labelledby="tab-trig" hidden>
      <h1 class="view-title">Trigonometric Ratios</h1>
      <div class="tool-row">
        <div class="tool-field">
          <label for="trig-angle">Angle &#x3B8;</label>
          <input id="trig-angle" type="number" value="30" step="any">
        </div>
        <div class="unit-switch" role="group" aria-label="Angle unit">
          <button type="button" data-trig-unit="DEG" aria-pressed="true">Degrees</button>
          <button type="button" data-trig-unit="RAD" aria-pressed="false">Radians</button>
        </div>
      </div>
      <div id="angle-summary" class="angle-summary"></div>
      <table class="value-table">
        <thead><tr><th>Function</th><th>Value</th></tr></thead>
        <tbody id="trig-values"></tbody>
      </table>

      <h2 class="section-label">Inverse Trigonometry</h2>
      <div class="tool-row">
        <div class="tool-field">
          <label for="inverse-value">Value v</label>
          <input id="inverse-value" type="number" value="0.5" step="any">
        </div>
      </div>
      <table class="value-table">
        <thead><tr><th>Function</th><th>Degrees</th><th>Radians</th></tr></thead>
        <tbody id="inverse-values"></tbody>
      </table>
    </section>

    <!-- ══════════════════════ CALCULUS TAB ══════════════════════ -->
    <section class="view view-content" id="view-calculus" role="tabpanel"
             aria-labelledby="tab-calc2" hidden>
      <h1 class="view-title">Numerical Calculus</h1>
      <div class="tool-field">
        <label for="calc-function">Function f(x)</label>
        <input id="calc-function" type="text" value="sin(x)"
               autocomplete="off" spellcheck="false">
      </div>
      <p class="tool-hint">Use <strong>x</strong> or <strong>theta</strong> as the variable.
         Trig functions use <strong>radians</strong> in calculus mode.</p>
      <div class="tool-row">
        <div class="tool-field">
          <label for="calc-op">Operation</label>
          <select id="calc-op">
            <option value="derivative">Derivative f'(x)</option>
            <option value="second">Second derivative f''(x)</option>
            <option value="integral">Definite integral</option>
          </select>
        </div>
      </div>
      <div id="calc-point-row" class="tool-row">
        <div class="tool-field">
          <label for="calc-point">Point x</label>
          <input id="calc-point" type="text" value="pi/4" autocomplete="off">
        </div>
      </div>
      <div id="calc-limits-row" class="tool-row" hidden>
        <div class="tool-field">
          <label for="calc-lower">Lower limit a</label>
          <input id="calc-lower" type="text" value="0" autocomplete="off">
        </div>
        <div class="tool-field">
          <label for="calc-upper">Upper limit b</label>
          <input id="calc-upper" type="text" value="pi" autocomplete="off">
        </div>
      </div>
      <button class="tool-button" id="calc-go" type="button">Calculate</button>
      <output class="tool-result" id="calc-result" aria-live="polite">
        Enter a function and press Calculate.
      </output>
    </section>

    <footer class="calc-footer">
      Type anywhere &middot; Enter&nbsp;/&nbsp;= to evaluate &middot; Esc to clear
    </footer>
  </main>

  <script>
  (function () {
    "use strict";

    /* ─── State ─── */
    const expr        = document.getElementById("expression");
    const resultEl    = document.getElementById("result");
    let   angleMode   = "DEG";   // calculator angle mode
    let   justCalced  = false;
    let   lastAnswer  = 0;

    /* ─── Helpers ─── */
    function clamp(v) {
      // Round tiny floating-point noise to clean integers / halves
      if (Math.abs(v) < 1e-12)          return 0;
      if (Math.abs(v - 1)  < 1e-12)     return 1;
      if (Math.abs(v + 1)  < 1e-12)     return -1;
      if (Math.abs(v - 0.5) < 1e-12)    return 0.5;
      if (Math.abs(v + 0.5) < 1e-12)    return -0.5;
      return v;
    }

    function fmt(v, digits = 12) {
      if (!Number.isFinite(v)) return String(v);
      v = clamp(v);
      if (v === 0) return "0";
      // Avoid scientific notation for numbers that display nicely
      const s = Number(v.toPrecision(digits)).toString();
      return s;
    }

    /* ─── Tokeniser ─── */
    function tokenize(src) {
      // Normalise input
      src = src
        .replace(/×/g, "*").replace(/÷/g, "/")
        .replace(/−/g, "-").replace(/–/g, "-")
        .replace(/π/g, "pi").replace(/θ/g, "theta")
        .replace(/√/g, "sqrt ");
      // Auto-close open parentheses
      let open = 0;
      for (const c of src) { if (c === "(") open++; else if (c === ")") open--; }
      if (open > 0) src += ")".repeat(open);

      const tokens = [];
      let i = 0;
      while (i < src.length) {
        if (/\s/.test(src[i])) { i++; continue; }
        const rest = src.slice(i);
        const num  = rest.match(/^(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?/i);
        const id   = rest.match(/^[a-z_][a-z0-9_]*/i);
        if (num) {
          tokens.push({ t: "num",  v: Number(num[0]) });
          i += num[0].length;
        } else if (id) {
          tokens.push({ t: "id",   v: id[0].toLowerCase() });
          i += id[0].length;
        } else if ("+-*/^%(),!".includes(src[i])) {
          tokens.push({ t: src[i], v: src[i] });
          i++;
        } else {
          throw new Error(`Unexpected character: "${src[i]}"`);
        }
      }
      return tokens;
    }

    /* ─── Recursive-descent parser / evaluator ─── */
    const FUNCS = new Set([
      "sin","cos","tan","cot","sec","csc",
      "asin","acos","atan","acot",
      "sinh","cosh","tanh","asinh","acosh","atanh",
      "sqrt","log","ln","exp","fact","abs","floor","ceil",
      "pow","radians","degrees"
    ]);

    function factorial(n) {
      if (!Number.isInteger(n) || n < 0 || n > 170)
        throw new Error("Factorial is only defined for integers 0 – 170.");
      let r = 1; for (let k = 2; k <= n; k++) r *= k; return r;
    }

    function applyFn(name, a, b, mode) {
      const toRad = mode === "DEG" ? a * Math.PI / 180 : a;
      const fromRad = v => mode === "DEG" ? v * 180 / Math.PI : v;
      const safe = (num, den) => {
        if (Math.abs(den) < 1e-12) throw new Error(`${name} is undefined here.`);
        return num / den;
      };
      switch (name) {
        case "sin":     return clamp(Math.sin(toRad));
        case "cos":     return clamp(Math.cos(toRad));
        case "tan":     return clamp(safe(Math.sin(toRad), Math.cos(toRad)));
        case "cot":     return clamp(safe(Math.cos(toRad), Math.sin(toRad)));
        case "sec":     return clamp(safe(1, Math.cos(toRad)));
        case "csc":     return clamp(safe(1, Math.sin(toRad)));
        case "asin":    return fromRad(Math.asin(a));
        case "acos":    return fromRad(Math.acos(a));
        case "atan":    return fromRad(Math.atan(a));
        case "acot":    return fromRad(Math.atan2(1, a));
        case "sinh":    return Math.sinh(a);
        case "cosh":    return Math.cosh(a);
        case "tanh":    return Math.tanh(a);
        case "asinh":   return Math.asinh(a);
        case "acosh":   return Math.acosh(a);
        case "atanh":   return Math.atanh(a);
        case "sqrt":    return Math.sqrt(a);
        case "log":     return Math.log10(a);
        case "ln":      return Math.log(a);
        case "exp":     return Math.exp(a);
        case "fact":    return factorial(a);
        case "abs":     return Math.abs(a);
        case "floor":   return Math.floor(a);
        case "ceil":    return Math.ceil(a);
        case "pow":
          if (b === undefined) throw new Error("pow(base, exponent) needs two arguments.");
          return Math.pow(a, b);
        case "radians": return a * Math.PI / 180;
        case "degrees": return a * 180 / Math.PI;
        default:        throw new Error(`Unknown function: ${name}`);
      }
    }

    function evaluate(src, vars = {}, mode = angleMode) {
      const tokens = tokenize(src);
      let pos = 0;
      const peek  = ()      => tokens[pos];
      const take  = (type)  => {
        if (peek()?.t !== type)
          throw new Error(`Expected "${type}" but got "${peek()?.v ?? "end of input"}".`);
        return tokens[pos++];
      };
      const startsVal = tk => tk && ["num", "id", "("].includes(tk.t);

      function parseExpr() {
        let v = parseTerm();
        while (peek()?.t === "+" || peek()?.t === "-") {
          const op = tokens[pos++].t;
          const r  = parseTerm();
          v = op === "+" ? v + r : v - r;
        }
        return v;
      }
      function parseTerm() {
        let v = parseUnary();
        while (["*", "/"].includes(peek()?.t) || startsVal(peek())) {
          const op = ["*", "/"].includes(peek()?.t) ? tokens[pos++].t : "*";
          const r  = parseUnary();
          if (op === "/" && r === 0) throw new Error("Division by zero.");
          v = op === "*" ? v * r : v / r;
        }
        return v;
      }
      function parseUnary() {
        if (peek()?.t === "+") { pos++; return parseUnary(); }
        if (peek()?.t === "-") { pos++; return -parseUnary(); }
        return parsePower();
      }
      function parsePower() {
        let v = parsePrimary();
        if (peek()?.t === "^") { pos++; v = Math.pow(v, parseUnary()); }
        while (peek()?.t === "%" || peek()?.t === "!") {
          const op = tokens[pos++].t;
          v = op === "%" ? v / 100 : factorial(v);
        }
        return v;
      }
      function parsePrimary() {
        const tk = peek();
        if (!tk) throw new Error("Unexpected end of expression.");
        if (tk.t === "num")  { pos++; return tk.v; }
        if (tk.t === "(")    {
          pos++;
          const v = parseExpr();
          take(")");
          return v;
        }
        if (tk.t === "id") {
          pos++;
          if (tk.v === "pi")    return Math.PI;
          if (tk.v === "e")     return Math.E;
          if (tk.v === "ans")   return lastAnswer;
          if (Object.hasOwn(vars, tk.v)) return vars[tk.v];
          if (!FUNCS.has(tk.v)) throw new Error(`Unknown name: "${tk.v}"`);
          // Function call — optional parentheses
          let a, b;
          if (peek()?.t === "(") {
            pos++;
            a = parseExpr();
            if (peek()?.t === ",") { pos++; b = parseExpr(); }
            take(")");
          } else {
            a = parseUnary();
          }
          return applyFn(tk.v, a, b, mode);
        }
        throw new Error(`Unexpected token "${tk.v}".`);
      }

      if (tokens.length === 0) throw new Error("Enter an expression.");
      const result = parseExpr();
      if (pos !== tokens.length)
        throw new Error("Check parentheses and operators.");
      if (!Number.isFinite(result))
        throw new Error("Result is out of range.");
      return result;
    }

    /* ─── Display logic ─── */
    function showResult() {
      const src = expr.value.trim();
      if (!src) { resultEl.textContent = ""; resultEl.className = "result-line"; return; }
      try {
        const v = evaluate(src);
        resultEl.textContent = `= ${fmt(v)}`;
        resultEl.className = "result-line";
      } catch (err) {
        resultEl.textContent = err.message;
        resultEl.className = "result-line error";
      }
    }

    function insert(val) {
      if (justCalced && /^[0-9.(a-z]/i.test(val)) expr.value = "";
      const s = expr.selectionStart ?? expr.value.length;
      const e = expr.selectionEnd   ?? s;
      expr.setRangeText(val, s, e, "end");
      justCalced = false;
      showResult();
      expr.focus({ preventScroll: true });
    }

    function calculate() {
      showResult();
      if (!resultEl.classList.contains("error") && resultEl.textContent) {
        const orig = expr.value;
        try {
          lastAnswer = evaluate(orig);
          expr.value = fmt(lastAnswer);
          resultEl.textContent = `= ${expr.value}`;
          const li = document.createElement("li");
          li.textContent = `${orig} = ${expr.value}`;
          const list = document.getElementById("history-list");
          list.prepend(li);
          while (list.children.length > 20) list.lastElementChild.remove();
          justCalced = true;
        } catch (_) { /* already shown */ }
      }
      expr.focus({ preventScroll: true });
    }

    function clearExpr() {
      expr.value = "";
      resultEl.textContent = "";
      resultEl.className = "result-line";
      justCalced = false;
      expr.focus({ preventScroll: true });
    }

    /* ─── Button wiring ─── */
    document.querySelectorAll("[data-insert]").forEach(btn => {
      btn.addEventListener("click", () => insert(btn.dataset.insert));
    });
    document.querySelectorAll('[data-action="clear"]').forEach(btn =>
      btn.addEventListener("click", clearExpr));
    document.querySelectorAll('[data-action="clear-history"]').forEach(btn =>
      btn.addEventListener("click", () => {
        document.getElementById("history-list").replaceChildren();
        expr.focus({ preventScroll: true });
      }));
    document.querySelector('[data-action="delete"]').addEventListener("click", () => {
      const s = expr.selectionStart ?? expr.value.length;
      const e = expr.selectionEnd   ?? s;
      if (s !== e) expr.setRangeText("", s, e, "end");
      else if (s > 0) expr.setRangeText("", s - 1, s, "end");
      justCalced = false;
      showResult();
      expr.focus({ preventScroll: true });
    });
    document.querySelector('[data-action="equals"]').addEventListener("click", calculate);

    /* ─── DEG / RAD mode ─── */
    document.querySelectorAll("[data-mode]").forEach(btn => {
      btn.addEventListener("click", () => {
        angleMode = btn.dataset.mode;
        document.querySelectorAll("[data-mode]").forEach(b =>
          b.setAttribute("aria-pressed", String(b === btn)));
        showResult();
        expr.focus({ preventScroll: true });
      });
    });

    expr.addEventListener("input", () => { justCalced = false; showResult(); });

    /* ─── Global keyboard support ─── */
    document.addEventListener("keydown", ev => {
      if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
      const active = document.activeElement;
      // If focus is in another input/select (not our expression field), ignore
      if (active && active !== expr &&
          active.matches("input, textarea, select")) return;
      // Only handle keypresses when Calculator tab is visible
      const calcPanel = document.getElementById("view-calculator");
      if (calcPanel.hidden && ev.key !== "Escape") return;

      if (ev.key === "Enter" || ev.key === "=") {
        ev.preventDefault(); calculate(); return;
      }
      if (ev.key === "Escape") {
        ev.preventDefault(); clearExpr(); return;
      }
      if (ev.key === "Backspace" && active !== expr) {
        ev.preventDefault();
        const s = expr.value.length;
        if (s > 0) expr.setRangeText("", s - 1, s, "end");
        showResult();
        expr.focus({ preventScroll: true }); return;
      }
      if (active !== expr && /^[0-9a-z.+\-*/%^()!,]$/i.test(ev.key)) {
        ev.preventDefault(); insert(ev.key);
      }
    });

    /* ─── Tab switching ─── */
    document.querySelectorAll("[data-view]").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll("[data-view]").forEach(t =>
          t.setAttribute("aria-selected", String(t === tab)));
        document.querySelectorAll(".view").forEach(panel =>
          panel.hidden = (panel.id !== `view-${tab.dataset.view}`));
        if (tab.dataset.view === "calculator")
          expr.focus({ preventScroll: true });
        if (tab.dataset.view === "trigonometry") updateTrig();
      });
    });

    /* ══════════════════════ TRIGONOMETRY TAB ════════════════════ */
    let trigUnit = "DEG";

    function trigClean(v) {
      // Same snap-to-clean-value logic used for calculator
      return clamp(v);
    }

    function updateTrig() {
      const raw   = Number(document.getElementById("trig-angle").value);
      const sumEl = document.getElementById("angle-summary");
      const tbody = document.getElementById("trig-values");
      if (!Number.isFinite(raw)) {
        sumEl.textContent = "Enter a valid angle."; tbody.replaceChildren(); return;
      }
      const rad = trigUnit === "DEG" ? raw * Math.PI / 180 : raw;
      const deg = rad * 180 / Math.PI;
      sumEl.textContent = `θ = ${fmt(deg, 8)}° = ${fmt(rad, 8)} rad`;
      tbody.replaceChildren();
      const pairs = [
        ["sin θ", trigClean(Math.sin(rad))],
        ["cos θ", trigClean(Math.cos(rad))],
      ];
      const sinv = pairs[0][1], cosv = pairs[1][1];
      const safe = (n, d) => Math.abs(d) < 1e-12 ? "undefined" : fmt(n / d, 8);
      pairs.push(
        ["tan θ", safe(sinv, cosv)],
        ["cot θ", safe(cosv, sinv)],
        ["sec θ", safe(1, cosv)],
        ["csc θ", safe(1, sinv)],
      );
      for (const [label, val] of pairs) {
        const tr = document.createElement("tr");
        const td1 = document.createElement("td"); td1.textContent = label;
        const td2 = document.createElement("td"); td2.textContent = typeof val === "number" ? fmt(val, 8) : val;
        tr.append(td1, td2); tbody.append(tr);
      }

      // Inverse trig
      const v2    = Number(document.getElementById("inverse-value").value);
      const ibody = document.getElementById("inverse-values");
      ibody.replaceChildren();
      if (!Number.isFinite(v2)) return;
      const inv = [];
      if (v2 >= -1 && v2 <= 1) {
        inv.push(["asin(v)", Math.asin(v2)], ["acos(v)", Math.acos(v2)]);
      }
      inv.push(["atan(v)", Math.atan(v2)], ["acot(v)", Math.atan2(1, v2)]);
      for (const [label, angle] of inv) {
        const tr = document.createElement("tr");
        for (const txt of [label, fmt(angle * 180 / Math.PI, 8), fmt(angle, 8)]) {
          const td = document.createElement("td"); td.textContent = txt; tr.append(td);
        }
        ibody.append(tr);
      }
    }

    document.querySelectorAll("[data-trig-unit]").forEach(btn => {
      btn.addEventListener("click", () => {
        trigUnit = btn.dataset.trigUnit;
        document.querySelectorAll("[data-trig-unit]").forEach(b =>
          b.setAttribute("aria-pressed", String(b === btn)));
        updateTrig();
      });
    });
    document.getElementById("trig-angle").addEventListener("input", updateTrig);
    document.getElementById("inverse-value").addEventListener("input", updateTrig);
    updateTrig();

    /* ══════════════════════ CALCULUS TAB ════════════════════════ */
    function numericalDerivative(fn, x, h = 1e-4) {
      return (-fn(x + 2*h) + 8*fn(x + h) - 8*fn(x - h) + fn(x - 2*h)) / (12 * h);
    }
    function secondDerivative(fn, x, h = 1e-4) {
      return (fn(x + h) - 2*fn(x) + fn(x - h)) / (h * h);
    }
    function simpsonsRule(fn, a, b, n = 2000) {
      const h = (b - a) / n;
      let total = fn(a) + fn(b);
      for (let i = 1; i < n; i++) total += (i % 2 ? 4 : 2) * fn(a + i * h);
      return total * h / 3;
    }

    document.getElementById("calc-op").addEventListener("change", ev => {
      const integral = ev.target.value === "integral";
      document.getElementById("calc-point-row").hidden  =  integral;
      document.getElementById("calc-limits-row").hidden = !integral;
    });

    document.getElementById("calc-go").addEventListener("click", () => {
      const out   = document.getElementById("calc-result");
      const src   = document.getElementById("calc-function").value.trim();
      const op    = document.getElementById("calc-op").value;
      try {
        const fn = v => evaluate(src, { x: v, theta: v }, "RAD");
        let answer;
        if (op === "integral") {
          const a = evaluate(document.getElementById("calc-lower").value, {}, "RAD");
          const b = evaluate(document.getElementById("calc-upper").value, {}, "RAD");
          answer = `Integral from ${document.getElementById("calc-lower").value} `
                 + `to ${document.getElementById("calc-upper").value} `
                 + `= ${fmt(simpsonsRule(fn, a, b), 8)}`;
        } else {
          const p   = evaluate(document.getElementById("calc-point").value, {}, "RAD");
          const val = op === "derivative" ? numericalDerivative(fn, p) : secondDerivative(fn, p);
          const lbl = op === "derivative" ? "f'" : "f''";
          answer = `${lbl}(${document.getElementById("calc-point").value}) = ${fmt(val, 8)}`;
        }
        out.textContent = answer;
        out.className = "tool-result";
      } catch (err) {
        out.textContent = err.message || "Check function and limits.";
        out.className = "tool-result error";
      }
    });

    /* ─── Auto-focus on load ─── */
    window.addEventListener("load", () => expr.focus({ preventScroll: true }));
  })();
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
components.html(CALCULATOR_HTML, height=1080, scrolling=True)
