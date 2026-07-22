/**
 * CHRONOS-VII spacetime sandbox
 * Cinematic simulation only — no physical time-travel model.
 */
(() => {
  const $ = (id) => document.getElementById(id);

  const state = {
    branches: 3,
    tilt: 18, // degrees of narrative light-cone tilt
    field: 35, // fictional "band intensity" 0-100
    pulse: 40, // fictional charge UI only
    lockout: false,
    ghosting: false,
    tick: 0,
    log: [],
  };

  const canvas = $("sandbox");
  const ctx = canvas.getContext("2d");

  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }

  function computeMeters() {
    const tiltFactor = state.tilt / 90;
    const branchFactor = (state.branches - 1) / 7;
    const fieldFactor = state.field / 100;

    // Narrative scores only — not physics measurements.
    let causality = Math.round(
      100 * clamp(0.15 + tiltFactor * 0.55 + branchFactor * 0.35 + fieldFactor * 0.15, 0, 1),
    );
    let entropy = Math.round(
      100 * clamp(0.1 + tiltFactor * 0.4 + branchFactor * 0.25 + (state.pulse / 100) * 0.2, 0, 1),
    );
    let shield = Math.round(
      100 * clamp(1 - tiltFactor * 0.35 - branchFactor * 0.2 - fieldFactor * 0.15, 0, 1),
    );
    let erosion = Math.round(
      100 * clamp(tiltFactor * 0.45 + branchFactor * 0.35 + (entropy / 100) * 0.25 - 0.05, 0, 1),
    );

    if (state.lockout) {
      causality = 100;
      erosion = Math.max(erosion, 92);
      shield = Math.min(shield, 12);
    }

    const ghosting = erosion >= 70 || state.ghosting;
    let simState = "NOMINAL";
    if (state.lockout) simState = "LOCKOUT";
    else if (ghosting || erosion >= 70) simState = "EROSION";
    else if (causality >= 45 || state.tilt >= 40) simState = "STRESSED";

    return { causality, entropy, shield, erosion, ghosting, simState };
  }

  function log(message) {
    const ts = new Date().toLocaleTimeString();
    state.log.unshift({ ts, message });
    state.log = state.log.slice(0, 12);
    renderLog();
  }

  function renderLog() {
    const el = $("event-log");
    el.innerHTML = state.log
      .map((row) => `<div><span class="ts">${row.ts}</span> · ${row.message}</div>`)
      .join("");
  }

  function setBar(id, value, opts = {}) {
    const fill = $(id);
    fill.style.width = `${value}%`;
    if (opts.critical && value >= 75) {
      fill.style.background = "linear-gradient(90deg, #ff5c35, #ff2a6d)";
    }
  }

  function updateUI() {
    const m = computeMeters();

    $("val-branches").textContent = String(state.branches);
    $("val-tilt").textContent = `${state.tilt.toFixed(0)}°`;
    $("val-field").textContent = `${state.field}%`;
    $("val-pulse").textContent = `${state.pulse}%`;

    $("meter-causality-val").textContent = `${m.causality}`;
    $("meter-entropy-val").textContent = `${m.entropy}`;
    $("meter-shield-val").textContent = `${m.shield}`;
    $("meter-erosion-val").textContent = `${m.erosion}`;

    setBar("bar-causality", m.causality, { critical: true });
    setBar("bar-entropy", m.entropy);
    setBar("bar-shield", m.shield);
    setBar("bar-erosion", m.erosion, { critical: true });

    const pill = $("sim-state");
    pill.dataset.state = m.simState;
    pill.querySelector("b").textContent = m.simState;

    $("risk-copy").textContent = riskCopy(m);
    // Recalibrate is useful whenever stressed/locked, not only after full lockout.
    $("btn-recalibrate").disabled = m.simState === "NOMINAL" && !state.lockout;

    if (m.simState === "EROSION" && !state.ghosting) {
      state.ghosting = true;
      log("Ghosting threshold reached — narrative erosion trails enabled (fiction UI).");
    }
    if (m.causality >= 90 && !state.lockout) {
      state.lockout = true;
      log("Chronology lockout — recalibration required before further cone tilt.");
    }

    $("tilt").disabled = state.lockout;
    $("branches").disabled = state.lockout;
    $("field").disabled = state.lockout;
    $("pulse").disabled = state.lockout;
    $("btn-stress").disabled = state.lockout;
  }

  function riskCopy(m) {
    if (m.simState === "LOCKOUT") {
      return "LOCKOUT: narrative causality ceiling hit. Recalibrate the Hafnium lattice (story beat only).";
    }
    if (m.simState === "EROSION") {
      return "EROSION: branch interference high. Ghost trails are cinematic, not medical guidance.";
    }
    if (m.simState === "STRESSED") {
      return "STRESSED: light-cone tilt and branch count elevate fictional paradox pressure.";
    }
    return "NOMINAL: cones near flat Minkowski-style baseline. Safe demonstration range.";
  }

  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    const m = computeMeters();
    state.tick += 1;

    ctx.clearRect(0, 0, w, h);

    // Grid
    ctx.save();
    ctx.strokeStyle = "rgba(232,230,220,0.05)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 32) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 32) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }
    ctx.restore();

    const cx = w * 0.5;
    const cy = h * 0.58;

    drawBranches(cx, cy, w, h, m);
    drawLightCones(cx, cy, m);
    drawWorldline(cx, cy, h, m);
    drawCirclet(cx, cy - 18, m);
    if (m.ghosting) drawGhosts(cx, cy, m);

    // Axis labels
    ctx.fillStyle = "rgba(139,148,140,0.9)";
    ctx.font = "11px IBM Plex Mono, monospace";
    ctx.fillText("space →", w - 72, cy + 4);
    ctx.fillText("time ↑", cx + 8, 24);
    ctx.fillText("t̂  (narrative geodesic)", 16, 24);
    ctx.fillText(`engine: cinematic · hash 0x882_TEMP_SHIFT`, 16, h - 16);

    requestAnimationFrame(draw);
  }

  function drawBranches(cx, cy, w, h, m) {
    const n = state.branches;
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0.5 : i / (n - 1);
      const angle = (-0.55 + t * 1.1) * (0.7 + state.tilt / 120);
      const len = Math.min(w, h) * 0.42;
      const jitter = m.simState === "STRESSED" || m.simState === "EROSION"
        ? Math.sin(state.tick * 0.08 + i) * 3
        : 0;

      const x2 = cx + Math.sin(angle) * len + jitter;
      const y2 = cy - Math.cos(angle) * len;

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.quadraticCurveTo(cx + Math.sin(angle) * len * 0.4, cy - len * 0.55, x2, y2);
      ctx.strokeStyle = `rgba(200,255,53,${0.25 + (1 - Math.abs(t - 0.5)) * 0.45})`;
      ctx.lineWidth = i === Math.floor(n / 2) ? 2.2 : 1.2;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(x2, y2, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(200,255,53,0.85)";
      ctx.fill();

      ctx.fillStyle = "rgba(200,255,53,0.7)";
      ctx.font = "10px IBM Plex Mono, monospace";
      ctx.fillText(`β${i + 1}`, x2 + 6, y2 - 6);
    }
  }

  function drawLightCones(cx, cy, m) {
    const tiltRad = (state.tilt * Math.PI) / 180;
    const open = Math.PI / 4 + tiltRad * 0.35;
    const lean = tiltRad * 0.85;
    const radius = 120 + state.field * 0.5;

    // Future cone
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius, -Math.PI / 2 - open + lean, -Math.PI / 2 + open + lean);
    ctx.closePath();
    ctx.fillStyle = "rgba(94,234,212,0.12)";
    ctx.fill();
    ctx.strokeStyle = "rgba(94,234,212,0.65)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Past cone
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius * 0.85, Math.PI / 2 - open - lean, Math.PI / 2 + open - lean);
    ctx.closePath();
    ctx.fillStyle = "rgba(255,176,32,0.08)";
    ctx.fill();
    ctx.strokeStyle = "rgba(255,176,32,0.45)";
    ctx.stroke();

    if (state.tilt > 45) {
      ctx.fillStyle = "rgba(255,92,53,0.85)";
      ctx.font = "11px IBM Plex Mono, monospace";
      ctx.fillText("cone tilt > 45° · paradox pressure (fiction)", cx - 110, cy + radius + 28);
    }
  }

  function drawWorldline(cx, cy, h, m) {
    ctx.beginPath();
    ctx.moveTo(cx, h - 20);
    ctx.lineTo(cx, 40);
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.setLineDash([4, 6]);
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#fff";
    ctx.fill();
  }

  function drawCirclet(cx, cy, m) {
    const pulse = 0.5 + 0.5 * Math.sin(state.tick * 0.05);
    const rOuter = 34 + state.field * 0.04;
    const rInner = 22;

    ctx.beginPath();
    ctx.arc(cx, cy, rOuter, 0, Math.PI * 2);
    ctx.strokeStyle = m.simState === "LOCKOUT" ? "rgba(255,92,53,0.7)" : "rgba(200,255,53,0.85)";
    ctx.lineWidth = 4;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, rInner, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(94,234,212,${0.35 + pulse * 0.4})`;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Fictional intensity ticks (not RPM hardware)
    const ticks = 16;
    for (let i = 0; i < ticks; i++) {
      const a = (i / ticks) * Math.PI * 2 + state.tick * 0.01 * (state.field / 50);
      const x1 = cx + Math.cos(a) * (rInner + 2);
      const y1 = cy + Math.sin(a) * (rInner + 2);
      const x2 = cx + Math.cos(a) * (rOuter - 3);
      const y2 = cy + Math.sin(a) * (rOuter - 3);
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = `rgba(200,255,53,${0.15 + (state.field / 100) * 0.5})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.fillStyle = "rgba(232,230,220,0.9)";
    ctx.font = "10px IBM Plex Mono, monospace";
    ctx.textAlign = "center";
    ctx.fillText("CIRCLET", cx, cy + 4);
    ctx.textAlign = "left";
  }

  function drawGhosts(cx, cy, m) {
    for (let g = 1; g <= 3; g++) {
      const ox = Math.sin(state.tick * 0.03 + g) * (8 * g);
      const oy = Math.cos(state.tick * 0.02 + g) * (5 * g);
      ctx.beginPath();
      ctx.arc(cx + ox, cy + oy - 18, 28, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255,92,53,${0.12 + g * 0.05})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  }

  function bindControls() {
    $("branches").addEventListener("input", (e) => {
      state.branches = Number(e.target.value);
      updateUI();
    });
    $("tilt").addEventListener("input", (e) => {
      state.tilt = Number(e.target.value);
      updateUI();
    });
    $("field").addEventListener("input", (e) => {
      state.field = Number(e.target.value);
      updateUI();
    });
    $("pulse").addEventListener("input", (e) => {
      state.pulse = Number(e.target.value);
      updateUI();
    });

    $("btn-reset").addEventListener("click", () => {
      state.branches = 3;
      state.tilt = 18;
      state.field = 35;
      state.pulse = 40;
      state.lockout = false;
      state.ghosting = false;
      $("branches").value = state.branches;
      $("tilt").value = state.tilt;
      $("field").value = state.field;
      $("pulse").value = state.pulse;
      log("Sandbox reset to calibration zero (flat narrative baseline).");
      updateUI();
    });

    $("btn-recalibrate").addEventListener("click", () => {
      state.lockout = false;
      state.ghosting = false;
      state.tilt = Math.min(state.tilt, 25);
      state.branches = Math.min(state.branches, 4);
      $("tilt").value = state.tilt;
      $("branches").value = state.branches;
      log("Recalibration narrative applied — lattice integrity restored (fiction).");
      updateUI();
    });

    $("btn-stress").addEventListener("click", () => {
      if (state.lockout) return;
      state.tilt = 72;
      state.branches = 7;
      state.field = 80;
      $("tilt").value = state.tilt;
      $("branches").value = state.branches;
      $("field").value = state.field;
      log("Stress scenario: high cone tilt + dense branch lattice.");
      updateUI();
    });
  }

  function init() {
    bindControls();
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    log("CHRONOS-VII sandbox online — cinematic simulation only.");
    log("Blocked: real CTC hardware, singularities, tritium power design, high-RPM rotors.");
    updateUI();
    requestAnimationFrame(draw);
  }

  init();
})();
