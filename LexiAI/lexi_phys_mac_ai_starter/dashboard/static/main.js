import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";
import { GLTFLoader } from "https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js";

const log = document.getElementById("log");
const input = document.getElementById("msg");
const send = document.getElementById("send");
const idea = document.getElementById("idea");
const depth = document.getElementById("depth");
const saveArtifacts = document.getElementById("save-artifacts");
const buildBlueprint = document.getElementById("build-blueprint");
const buildCashSystem = document.getElementById("build-cash-system");
const blueprintOutput = document.getElementById("blueprint-output");
const demoBtn = document.getElementById("demo-btn");
const primaryBlueprint = document.getElementById("primary-blueprint");
const waitlistForm = document.getElementById("waitlist-form");
const waitlistEmail = document.getElementById("waitlist-email");
const waitlistStatus = document.getElementById("waitlist-status");
const leadCount = document.getElementById("lead-count");
const leadTableBody = document.getElementById("lead-table-body");
const leadExportStatus = document.getElementById("lead-export-status");
const refreshLeads = document.getElementById("refresh-leads");
const companionLog = document.getElementById("companion-log");
const companionMsg = document.getElementById("companion-msg");
const companionSend = document.getElementById("companion-send");
const financeChimeLabel = document.getElementById("finance-chime-label");
const financeWalletLink = document.getElementById("finance-wallet-link");
const saveFinanceLinks = document.getElementById("save-finance-links");
const openWalletLink = document.getElementById("open-wallet-link");
const financeStatus = document.getElementById("finance-status");
const salesChart = document.getElementById("sales-chart");
const saleForm = document.getElementById("sale-form");
const saleProduct = document.getElementById("sale-product");
const saleChannel = document.getElementById("sale-channel");
const saleAmount = document.getElementById("sale-amount");
const saleStatus = document.getElementById("sale-status");
const saleDate = document.getElementById("sale-date");
const addSaleButton = document.getElementById("add-sale");
const salesTableBody = document.getElementById("sales-table-body");
const salesFormStatus = document.getElementById("sales-form-status");
const salesCount = document.getElementById("sales-count");
const metricRevenue = document.getElementById("metric-revenue");
const metricPaid = document.getElementById("metric-paid");
const metricPipeline = document.getElementById("metric-pipeline");
const metricAverage = document.getElementById("metric-average");
const growthGoal = document.getElementById("growth-goal");
const growthChannels = document.getElementById("growth-channels");
const generateGrowthPlan = document.getElementById("generate-growth-plan");
const growthOutput = document.getElementById("growth-output");
const contentKeywords = document.getElementById("content-keywords");
const targetAudience = document.getElementById("target-audience");
const contentHashtags = document.getElementById("content-hashtags");
const contentCta = document.getElementById("content-cta");
const contentTheme = document.getElementById("content-theme");
const contentObjective = document.getElementById("content-objective");
const toneButtons = [...document.querySelectorAll("[data-tone]")];
const detailButtons = [...document.querySelectorAll("[data-detail]")];
const executePostSynthesis = document.getElementById("execute-post-synthesis");
const fluxDescription = document.getElementById("flux-description");
const fluxResolution = document.getElementById("flux-resolution");
const fluxAspect = document.getElementById("flux-aspect");
const fluxStatus = document.getElementById("flux-status");
const executeKineticRender = document.getElementById("execute-kinetic-render");
const visualPrompt = document.getElementById("visual-prompt");
const visualStyle = document.getElementById("visual-style");
const generateArtifact = document.getElementById("generate-artifact");
const artifactCanvas = document.getElementById("artifact-canvas");
const artifactCaption = document.getElementById("artifact-caption");

let selectedTone = "Provocative";
let selectedDetail = "Advanced";

const demoIdea = [
  "Design a portable creator workstation that turns sketches, voice notes, and hardware parts into an engineered product blueprint.",
  "It should map subsystems, generate a prototype sprint plan, identify risky assumptions, and package the result as a futuristic technical presentation."
].join(" ");

const defaultSales = [
  {date: "2026-07-01", product: "Cash System Sprint", channel: "Facebook", amount: 750, status: "Paid"},
  {date: "2026-07-02", product: "Offer Page Buildout", channel: "Instagram", amount: 450, status: "Paid"},
  {date: "2026-07-03", product: "Lexi.AI Money Machine Kit", channel: "TikTok", amount: 149, status: "Offer Sent"}
];
const memoryStore = {};

function readStore(key, fallback) {
  if (Object.prototype.hasOwnProperty.call(memoryStore, key)) return memoryStore[key];
  try {
    const raw = globalThis.localStorage?.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    memoryStore[key] = parsed;
    return parsed;
  } catch (_e) {
    return fallback;
  }
}

function writeStore(key, value) {
  memoryStore[key] = value;
  try {
    globalThis.localStorage?.setItem(key, JSON.stringify(value));
  } catch (_e) {
    // In-app browser storage can be unavailable; memoryStore keeps the UI live.
  }
}

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text) item.textContent = text;
  return item;
}

function appendList(parent, title, items) {
  const section = node("div", "blueprint-section");
  section.appendChild(node("h2", "", title));
  const list = document.createElement("ul");
  items.forEach(item => list.appendChild(node("li", "", item)));
  section.appendChild(list);
  parent.appendChild(section);
}

function money(value) {
  return `$${Number(value || 0).toLocaleString(undefined, {maximumFractionDigits: 0})}`;
}

function trimText(value, fallback = "") {
  const text = String(value || "").trim();
  return text || fallback;
}

async function requestJson(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      message = data.detail || data.error || message;
    } catch (_e) {
      // Keep the HTTP status message when the server did not return JSON.
    }
    throw new Error(message);
  }
  return res.json();
}

function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 3) {
  const words = text.split(/\s+/).filter(Boolean);
  let line = "";
  let lineCount = 0;

  words.forEach((word, index) => {
    if (lineCount >= maxLines) return;
    const testLine = line ? `${line} ${word}` : word;
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, y + lineCount * lineHeight);
      line = word;
      lineCount += 1;
      return;
    }
    line = testLine;
    if (index === words.length - 1 && lineCount < maxLines) {
      ctx.fillText(line, x, y + lineCount * lineHeight);
      lineCount += 1;
    }
  });
}

function composeContentIdea() {
  return [
    "Build a Lexi.PHYS inverse content engine cash-system pack.",
    `Keywords: ${trimText(contentKeywords.value, "0, vector, mass")}`,
    `Target audience: ${trimText(targetAudience.value, "physics grads and technical creators")}`,
    `Hashtags: ${trimText(contentHashtags.value, "#geometry #physicscore")}`,
    `CTA: ${trimText(contentCta.value, "Solve the equation")}`,
    `Geometric theme: ${trimText(contentTheme.value, "diamond lattice")}`,
    `Objective: ${trimText(contentObjective.value, "Viral reach")}`,
    `Resonance tone: ${selectedTone}`,
    "Package this as content hooks, products, services, proof assets, and validation checks."
  ].join("\n");
}

function setTone(button) {
  selectedTone = button.dataset.tone || selectedTone;
  toneButtons.forEach(item => item.classList.toggle("active", item === button));
}

function setDetail(button) {
  selectedDetail = button.dataset.detail || selectedDetail;
  detailButtons.forEach(item => item.classList.toggle("active", item === button));
}

function drawArtifactPreview() {
  if (!artifactCanvas) return;

  const ctx = artifactCanvas.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const rect = artifactCanvas.getBoundingClientRect();
  const width = Math.max(320, Math.floor((rect.width || 620) * dpr));
  const height = Math.max(170, Math.floor((rect.height || 170) * dpr));
  artifactCanvas.width = width;
  artifactCanvas.height = height;
  ctx.scale(dpr, dpr);

  const displayWidth = width / dpr;
  const displayHeight = height / dpr;
  const style = trimText(visualStyle.value, "blueprint");
  const prompt = trimText(
    visualPrompt.value,
    trimText(fluxDescription.value, "Lexi deconstructing a diamond structure into light")
  );
  const palettes = {
    photorealistic: ["#10131d", "#52ead8", "#f4f7ff", "#f5b95a"],
    anime: ["#120d22", "#ff6f91", "#9587ff", "#52ead8"],
    blueprint: ["#071127", "#52ead8", "#f4f7ff", "#6757ff"],
    cyberpunk: ["#0a0718", "#9587ff", "#52ead8", "#ff6f91"],
    "art deco": ["#15100b", "#f5b95a", "#f4f7ff", "#52ead8"],
    surrealism: ["#100d1c", "#ff6f91", "#f5b95a", "#9587ff"]
  };
  const [bg, primary, text, accent] = palettes[style] || palettes.blueprint;

  const gradient = ctx.createLinearGradient(0, 0, displayWidth, displayHeight);
  gradient.addColorStop(0, bg);
  gradient.addColorStop(1, "#03050e");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, displayWidth, displayHeight);

  ctx.strokeStyle = "rgba(244, 247, 255, .08)";
  ctx.lineWidth = 1;
  for (let x = 0; x < displayWidth; x += 24) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, displayHeight);
    ctx.stroke();
  }
  for (let y = 0; y < displayHeight; y += 24) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(displayWidth, y);
    ctx.stroke();
  }

  const cx = displayWidth * .66;
  const cy = displayHeight * .5;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-0.35);
  ctx.strokeStyle = primary;
  ctx.lineWidth = 2;
  ctx.shadowColor = primary;
  ctx.shadowBlur = 18;
  ctx.strokeRect(-48, -48, 96, 96);
  ctx.rotate(0.78);
  ctx.strokeStyle = accent;
  ctx.strokeRect(-32, -32, 64, 64);
  ctx.restore();

  ctx.shadowBlur = 0;
  ctx.strokeStyle = "rgba(82, 234, 216, .55)";
  ctx.beginPath();
  ctx.arc(displayWidth * .66, displayHeight * .5, 64, 0, Math.PI * 2);
  ctx.stroke();

  [
    [displayWidth * .18, displayHeight * .25],
    [displayWidth * .33, displayHeight * .72],
    [displayWidth * .81, displayHeight * .27],
    [displayWidth * .9, displayHeight * .72]
  ].forEach(([x, y]) => {
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(244, 247, 255, .18)";
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(cx, cy);
    ctx.stroke();
  });

  ctx.fillStyle = text;
  ctx.font = "700 15px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
  ctx.fillText(style.toUpperCase(), 18, 28);
  ctx.fillStyle = "rgba(244, 247, 255, .7)";
  ctx.font = "12px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
  wrapCanvasText(ctx, prompt, 18, 54, displayWidth * .42, 17, 4);

  artifactCaption.textContent = `${style} artifact preview - ${prompt.slice(0, 96)}${prompt.length > 96 ? "..." : ""}`;
}

function loadSales() {
  const stored = readStore("lexiSales", []);
  return Array.isArray(stored) && stored.length ? stored : [...defaultSales];
}

function saveSales(rows) {
  writeStore("lexiSales", rows);
}

function loadFinanceLinks() {
  return readStore("lexiFinanceLinks", {});
}

function saveFinanceState() {
  const wallet = financeWalletLink.value.trim();
  const label = financeChimeLabel.value.trim();
  writeStore("lexiFinanceLinks", {wallet, label});
  renderFinanceLinks();
  financeStatus.textContent = "Saved locally. Open Chime or your wallet provider directly to approve money movement.";
}

function renderFinanceLinks() {
  const links = loadFinanceLinks();
  financeChimeLabel.value = links.label || "Business payout account";
  financeWalletLink.value = links.wallet || "";
  if (links.wallet && /^https?:\/\//i.test(links.wallet)) {
    openWalletLink.href = links.wallet;
    openWalletLink.removeAttribute("aria-disabled");
  } else {
    openWalletLink.href = "#operator-suite";
    openWalletLink.setAttribute("aria-disabled", "true");
  }
}

function drawSalesChart(rows) {
  const ctx = salesChart.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const rect = salesChart.getBoundingClientRect();
  salesChart.width = Math.max(320, Math.floor(rect.width * dpr));
  salesChart.height = Math.floor(240 * dpr);
  ctx.scale(dpr, dpr);

  const width = salesChart.width / dpr;
  const height = salesChart.height / dpr;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "rgba(0,0,0,.22)";
  ctx.fillRect(0, 0, width, height);

  const paidRows = rows.filter(row => ["Paid", "Delivered"].includes(row.status));
  const byDate = new Map();
  paidRows.forEach(row => {
    byDate.set(row.date, (byDate.get(row.date) || 0) + Number(row.amount || 0));
  });
  const points = [...byDate.entries()].sort(([a], [b]) => a.localeCompare(b)).slice(-10);
  const chartPoints = points.length ? points : [["No sales", 0]];
  const maxValue = Math.max(100, ...chartPoints.map(([, value]) => value));
  const pad = 28;
  const barGap = 10;
  const barWidth = Math.max(18, (width - pad * 2 - barGap * (chartPoints.length - 1)) / chartPoints.length);

  ctx.strokeStyle = "rgba(247,244,236,.14)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i += 1) {
    const y = pad + ((height - pad * 2) / 3) * i;
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
  }

  chartPoints.forEach(([date, value], index) => {
    const x = pad + index * (barWidth + barGap);
    const barHeight = Math.max(3, (value / maxValue) * (height - pad * 2));
    const y = height - pad - barHeight;
    const gradient = ctx.createLinearGradient(0, y, 0, height - pad);
    gradient.addColorStop(0, "#71f4df");
    gradient.addColorStop(1, "#f2b84b");
    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, barWidth, barHeight);
    ctx.fillStyle = "rgba(247,244,236,.72)";
    ctx.font = "11px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
    ctx.fillText(value ? money(value) : "$0", x, Math.max(14, y - 6));
    ctx.fillStyle = "rgba(247,244,236,.46)";
    ctx.fillText(date.slice(5) || date, x, height - 8);
  });
}

function renderSales() {
  const rows = loadSales().sort((a, b) => b.date.localeCompare(a.date));
  const paidRows = rows.filter(row => ["Paid", "Delivered"].includes(row.status));
  const pipelineRows = rows.filter(row => ["Lead", "Offer Sent"].includes(row.status));
  const revenue = paidRows.reduce((sum, row) => sum + Number(row.amount || 0), 0);
  const pipeline = pipelineRows.reduce((sum, row) => sum + Number(row.amount || 0), 0);
  const average = paidRows.length ? revenue / paidRows.length : 0;

  metricRevenue.textContent = money(revenue);
  metricPaid.textContent = String(paidRows.length);
  metricPipeline.textContent = money(pipeline);
  metricAverage.textContent = money(average);
  salesCount.textContent = `${rows.length} records`;

  salesTableBody.textContent = "";
  rows.forEach(row => {
    const tr = document.createElement("tr");
    [row.date, row.product, row.channel, row.status, money(row.amount)].forEach(text => {
      tr.appendChild(node("td", "", text));
    });
    salesTableBody.appendChild(tr);
  });
  drawSalesChart(rows);
}

function addSale(event) {
  event?.preventDefault();
  try {
    const row = {
      date: saleDate.value,
      product: saleProduct.value.trim(),
      channel: saleChannel.value.trim(),
      amount: Number(saleAmount.value || 0),
      status: saleStatus.value
    };
    if (!row.date || !row.product || !row.channel) {
      salesFormStatus.textContent = "Add date, offer, channel, and amount before logging the sale.";
      return;
    }
    const rows = loadSales();
    rows.push(row);
    saveSales(rows);
    saleProduct.value = "";
    saleChannel.value = "";
    saleAmount.value = "";
    saleStatus.value = "Paid";
    renderSales();
    salesFormStatus.textContent = "Sale logged locally.";
  } catch (e) {
    salesFormStatus.textContent = `Could not log sale: ${e.message || e}`;
  }
}

function formatLeadDate(value) {
  if (!value) return "";
  return String(value).replace("T", " ").replace("Z", " UTC");
}

function renderLeads(data = {}) {
  if (!leadTableBody) return;
  const leads = Array.isArray(data.leads) ? data.leads : [];
  const summary = data.summary || {};

  if (leadCount) {
    const total = typeof summary.total === "number" ? summary.total : leads.length;
    leadCount.textContent = `${total} ${total === 1 ? "lead" : "leads"}`;
  }

  leadTableBody.textContent = "";
  if (!leads.length) {
    const tr = document.createElement("tr");
    const td = node("td", "", "No proof-page leads captured yet.");
    td.colSpan = 6;
    tr.appendChild(td);
    leadTableBody.appendChild(tr);
  } else {
    leads.forEach(lead => {
      const tr = document.createElement("tr");
      [
        lead.email,
        lead.stage || "Waitlist",
        lead.offer || "Lexi.AI early access",
        lead.source || "proof-page-waitlist",
        String(lead.touch_count || 1),
        formatLeadDate(lead.updated_at || lead.created_at)
      ].forEach(text => {
        tr.appendChild(node("td", "", text));
      });
      leadTableBody.appendChild(tr);
    });
  }

  if (leadExportStatus) {
    const paths = data.export_paths || {};
    leadExportStatus.textContent = paths.json && paths.csv
      ? "Server exports sync to workspace/leads/leads.json and workspace/leads/leads.csv."
      : "Server exports are available as JSON and CSV after the first lead is captured.";
  }
}

async function loadLeads() {
  if (!leadTableBody) return;
  try {
    const data = await requestJson("/leads?limit=50");
    renderLeads(data);
  } catch (e) {
    if (leadExportStatus) {
      leadExportStatus.textContent = `Lead pipeline unavailable: ${e.message || e}`;
    }
  }
}

async function captureWaitlistLead(event) {
  event.preventDefault();
  const email = waitlistEmail.value.trim();
  if (!email) return;

  waitlistStatus.textContent = "Capturing lead...";
  try {
    await requestJson("/leads", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        email,
        source: "proof-page-waitlist",
        offer: "Lexi.AI Cash System early access",
        interest: "cash-system generation, blueprint reports, prototype planning, creator tooling",
        stage: "Waitlist",
        notes: trimText(idea.value, "Captured from the Lexi.AI proof page waitlist.").slice(0, 320),
        tags: ["proof-page", "cash-system", "blueprint"]
      })
    });
    waitlistStatus.textContent = "Lead captured on the server. JSON and CSV exports are updated.";
    waitlistEmail.value = "";
    await loadLeads();
  } catch (e) {
    waitlistStatus.textContent = `Lead capture failed: ${e.message || e}`;
  }
}

function renderGrowthPlan(data) {
  const plan = data.plan;
  growthOutput.textContent = "";
  appendList(growthOutput, "Guardrails", plan.guardrails);
  appendList(
    growthOutput,
    "Company Stages",
    plan.company_stages.map(stage => `${stage.name}: ${stage.target} Metric: ${stage.metric}`)
  );
  appendList(
    growthOutput,
    "Social Sales Boosters",
    plan.social_sales_boosters.map(item => `${item.channel}: ${item.daily_action}`)
  );
  appendList(growthOutput, "Pipeline", plan.sales_pipeline);
  appendList(growthOutput, "Next Actions", plan.next_actions);
}

async function runGrowthAutomation() {
  generateGrowthPlan.disabled = true;
  generateGrowthPlan.textContent = "Planning...";
  growthOutput.textContent = "Building growth automation plan...";
  try {
    const channels = growthChannels.value.split(",").map(item => item.trim()).filter(Boolean);
    const res = await fetch("/growth-automation", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        goal: growthGoal.value.trim(),
        channels
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Growth automation failed.");
    renderGrowthPlan(data);
  } catch (e) {
    growthOutput.textContent = `error> ${e.message || e}`;
  } finally {
    generateGrowthPlan.disabled = false;
    generateGrowthPlan.textContent = "Generate Growth Automation";
  }
}

async function sendCompanionMessage() {
  const message = companionMsg.value.trim();
  if (!message) return;
  companionMsg.value = "";
  companionLog.textContent += `\n\nyou> ${message}\n`;
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message: [
          "Companion direct-neural-link dashboard mode.",
          "Treat direct-neural-link as a focused companion interface, not a medical device.",
          "Help me build Lexi.AI sales, content, products, services, and automation with practical next actions.",
          message
        ].join("\n")
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Companion chat failed.");
    companionLog.textContent += `\nlexi> ${data.reply}\n`;
    companionLog.scrollTop = companionLog.scrollHeight;
  } catch (e) {
    companionLog.textContent += `\nerror> ${e.message || e}\n`;
  }
}

function renderBlueprint(data) {
  const result = data.result;
  const blueprint = result.blueprint;
  blueprintOutput.textContent = "";

  const head = node("div", "blueprint-head");
  const titleBlock = document.createElement("div");
  titleBlock.appendChild(node("strong", "", blueprint.title));
  titleBlock.appendChild(node("span", "", `${data.status} / ${data.depth} / run ${data.run_id}`));
  head.appendChild(titleBlock);
  head.appendChild(node("span", "", result.artifacts.markdown ? "Saved" : "Unsaved"));
  blueprintOutput.appendChild(head);

  const mission = node("div", "blueprint-section");
  mission.appendChild(node("h2", "", "Mission"));
  mission.appendChild(node("div", "", blueprint.mission));
  blueprintOutput.appendChild(mission);

  appendList(
    blueprintOutput,
    "Automation Ladder",
    blueprint.automation_ladder.map(item => `${item.stage}: ${item.action}`)
  );
  appendList(
    blueprintOutput,
    "Build Queue",
    blueprint.build_queue.map(item => `${item.rank}. ${item.action}`)
  );
  appendList(
    blueprintOutput,
    "Prototype Sprints",
    blueprint.prototype_sprints.map(item => `${item.window}: ${item.outcome}`)
  );
  appendList(blueprintOutput, "Validation", blueprint.validation_checks);

  if (result.artifacts.markdown || result.artifacts.json) {
    const paths = node("div", "blueprint-section");
    paths.appendChild(node("h2", "", "Artifacts"));
    if (result.artifacts.markdown) paths.appendChild(node("div", "pathline", result.artifacts.markdown));
    if (result.artifacts.json) paths.appendChild(node("div", "pathline", result.artifacts.json));
    blueprintOutput.appendChild(paths);
  }
}

function renderCashSystem(data) {
  const result = data.result;
  const cash = result.cash_system;
  const artifacts = result.artifacts || {};
  blueprintOutput.textContent = "";

  const head = node("div", "blueprint-head");
  const titleBlock = document.createElement("div");
  titleBlock.appendChild(node("strong", "", cash.title));
  titleBlock.appendChild(node("span", "", `${data.status} / ${cash.offer_type} / run ${data.run_id}`));
  head.appendChild(titleBlock);
  head.appendChild(node("span", "", artifacts.markdown ? "Saved" : "Unsaved"));
  blueprintOutput.appendChild(head);

  const mission = node("div", "blueprint-section");
  mission.appendChild(node("h2", "", "Mission"));
  mission.appendChild(node("div", "", cash.mission));
  blueprintOutput.appendChild(mission);

  appendList(
    blueprintOutput,
    "Content Hooks",
    cash.content_engine.hooks.map(item => `${item.format}: ${item.hook} CTA: ${item.cta}`)
  );
  appendList(
    blueprintOutput,
    "Products",
    cash.products.map(item => `${item.name}: ${item.deliverable} (${item.price_test})`)
  );
  appendList(
    blueprintOutput,
    "Services",
    cash.services.map(item => `${item.name}: ${item.promise} (${item.price_test})`)
  );
  appendList(
    blueprintOutput,
    "Build Queue",
    cash.build_queue.map(item => `${item.rank}. ${item.action}`)
  );
  appendList(blueprintOutput, "Validation", cash.validation_checks);

  const offer = node("div", "blueprint-section");
  offer.appendChild(node("h2", "", "One-Page Offer"));
  offer.appendChild(node("div", "", cash.launch_assets.one_page_offer.headline));
  offer.appendChild(node("div", "", cash.launch_assets.one_page_offer.subheadline));
  offer.appendChild(node("div", "", `CTA: ${cash.launch_assets.one_page_offer.cta}`));
  blueprintOutput.appendChild(offer);

  if (artifacts.markdown || artifacts.json) {
    const paths = node("div", "blueprint-section");
    paths.appendChild(node("h2", "", "Artifacts"));
    if (artifacts.markdown) paths.appendChild(node("div", "pathline", artifacts.markdown));
    if (artifacts.json) paths.appendChild(node("div", "pathline", artifacts.json));
    blueprintOutput.appendChild(paths);
  }
}

function focusBlueprintLab() {
  document.getElementById("blueprint-lab").scrollIntoView({behavior: "smooth", block: "start"});
  window.setTimeout(() => idea.focus(), 450);
}

async function runPostSynthesis() {
  idea.value = composeContentIdea();
  depth.value = "product";
  await runCashSystem();
}

async function runKineticRender() {
  const description = trimText(fluxDescription.value);
  if (!description) {
    fluxStatus.textContent = "Add a kinetic vector description first.";
    return;
  }

  idea.value = [
    "Create a Lexi.PHYS temporal flux render blueprint.",
    `Kinetic vector: ${description}`,
    `Resolution: ${fluxResolution.value}`,
    `Aspect ratio: ${fluxAspect.value}`,
    `Schematic detail: ${selectedDetail}`,
    "Return concept anatomy, visual staging, prototype steps, and validation checks."
  ].join("\n");
  visualPrompt.value = description;
  depth.value = "prototype";
  drawArtifactPreview();
  fluxStatus.textContent = "Temporal coordinates locked. Building render blueprint...";
  await runBlueprint();
  fluxStatus.textContent = "Render blueprint synthesized.";
}

function generateVisualArtifact() {
  const prompt = trimText(visualPrompt.value, trimText(fluxDescription.value));
  if (!prompt) {
    artifactCaption.textContent = "Add a visual prompt first.";
    return;
  }

  visualPrompt.value = prompt;
  drawArtifactPreview();
  idea.value = [
    "Prepare a Lexi.PHYS visual synthesis brief.",
    `Prompt: ${prompt}`,
    `Aesthetic style: ${visualStyle.value}`,
    `Resolution: ${fluxResolution.value}`,
    `Aspect ratio: ${fluxAspect.value}`,
    `Schematic detail: ${selectedDetail}`,
    "Include the intended artifact, visual system map, production notes, and validation checks."
  ].join("\n");
  blueprintOutput.textContent = "Visual artifact rendered locally. Use Deconstruct to generate the full artifact brief.";
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  log.textContent += `\n\nyou> ${message}\n`;
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message})
    });
    const data = await res.json();
    log.textContent += `\nlexi> ${data.reply}\n`;
    if (data.sources && data.sources.length) {
      log.textContent += `\nSources:\n${data.sources.map(s => "- " + s.path).join("\n")}\n`;
    }
    log.scrollTop = log.scrollHeight;
  } catch (e) {
    log.textContent += `\nerror> ${e}\n`;
  }
}

async function runBlueprint() {
  const text = idea.value.trim();
  if (!text) {
    blueprintOutput.textContent = "Add an idea first.";
    return;
  }

  buildBlueprint.disabled = true;
  buildBlueprint.textContent = "Building...";
  blueprintOutput.textContent = "Building blueprint...";
  try {
    const res = await fetch("/blueprint", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        idea: text,
        depth: depth.value,
        write_artifacts: saveArtifacts.checked
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Blueprint build failed.");
    renderBlueprint(data);
    log.textContent += `\n\nblueprint> ${data.result.summary}\n`;
    if (data.result.artifacts.markdown) {
      log.textContent += `artifact> ${data.result.artifacts.markdown}\n`;
    }
    log.scrollTop = log.scrollHeight;
  } catch (e) {
    blueprintOutput.textContent = `error> ${e.message || e}`;
  } finally {
    buildBlueprint.disabled = false;
    buildBlueprint.textContent = "Deconstruct";
  }
}

async function runCashSystem() {
  const text = idea.value.trim();
  if (!text) {
    blueprintOutput.textContent = "Add an idea first.";
    return;
  }

  buildCashSystem.disabled = true;
  buildCashSystem.textContent = "Packaging...";
  blueprintOutput.textContent = "Packaging Cash System...";
  try {
    const res = await fetch("/cash-system", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        idea: text,
        write_artifacts: saveArtifacts.checked
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Cash System build failed.");
    renderCashSystem(data);
    log.textContent += `\n\ncash-system> ${data.result.summary}\n`;
    if (data.result.artifacts.markdown) {
      log.textContent += `artifact> ${data.result.artifacts.markdown}\n`;
    }
    log.scrollTop = log.scrollHeight;
  } catch (e) {
    blueprintOutput.textContent = `error> ${e.message || e}`;
  } finally {
    buildCashSystem.disabled = false;
    buildCashSystem.textContent = "Package Cash System";
  }
}

send.onclick = sendMessage;
buildBlueprint.onclick = runBlueprint;
buildCashSystem.onclick = runCashSystem;
companionSend.onclick = sendCompanionMessage;
saveFinanceLinks.onclick = saveFinanceState;
saleForm.addEventListener("submit", addSale);
globalThis.lexiAddSale = addSale;
generateGrowthPlan.onclick = runGrowthAutomation;
executePostSynthesis.onclick = runPostSynthesis;
executeKineticRender.onclick = runKineticRender;
generateArtifact.onclick = generateVisualArtifact;
toneButtons.forEach(button => {
  button.addEventListener("click", () => setTone(button));
});
detailButtons.forEach(button => {
  button.addEventListener("click", () => setDetail(button));
});
visualStyle.addEventListener("change", drawArtifactPreview);
visualPrompt.addEventListener("input", drawArtifactPreview);
fluxDescription.addEventListener("input", () => {
  if (!visualPrompt.value.trim()) drawArtifactPreview();
});
primaryBlueprint.addEventListener("click", () => {
  focusBlueprintLab();
});
demoBtn.addEventListener("click", () => {
  idea.value = demoIdea;
  depth.value = "product";
  focusBlueprintLab();
  blueprintOutput.textContent = "Demo concept loaded. Building a sample blueprint...";
  window.setTimeout(runBlueprint, 550);
});
waitlistForm.addEventListener("submit", event => {
  captureWaitlistLead(event);
});
refreshLeads?.addEventListener("click", loadLeads);
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});
companionMsg.addEventListener("keydown", e => {
  if (e.key === "Enter") sendCompanionMessage();
});
saleDate.value = new Date().toISOString().slice(0, 10);
saleStatus.value = "Paid";
renderFinanceLinks();
renderSales();
loadLeads();
drawArtifactPreview();
window.addEventListener("resize", () => {
  renderSales();
  drawArtifactPreview();
});

const stage = document.getElementById("avatar");
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, stage.clientWidth / stage.clientHeight, 0.1, 100);
camera.position.set(0, 1.4, 4);

const renderer = new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(stage.clientWidth, stage.clientHeight);
stage.appendChild(renderer.domElement);

const light = new THREE.DirectionalLight(0xffffff, 2.2);
light.position.set(3, 4, 5);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 1.1));

const blueprintGrid = new THREE.GridHelper(18, 36, 0x71f4df, 0x38564f);
blueprintGrid.position.set(0, -1.45, 0);
blueprintGrid.material.transparent = true;
blueprintGrid.material.opacity = 0.22;
scene.add(blueprintGrid);

let avatar;
const loader = new GLTFLoader();

function mountFallbackAvatar() {
  if (avatar) return;
  avatar = new THREE.Group();

  const core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.92, 1),
    new THREE.MeshStandardMaterial({
      color: 0x71f4df,
      emissive: 0x123c37,
      metalness: 0.78,
      roughness: 0.18,
      wireframe: true
    })
  );
  avatar.add(core);

  const ringMaterial = new THREE.MeshStandardMaterial({
    color: 0xf2b84b,
    emissive: 0x3a2105,
    metalness: 0.65,
    roughness: 0.22,
    transparent: true,
    opacity: 0.72
  });

  const ringOne = new THREE.Mesh(new THREE.TorusGeometry(1.42, 0.012, 8, 140), ringMaterial);
  ringOne.rotation.x = Math.PI / 2;
  avatar.add(ringOne);

  const ringTwo = new THREE.Mesh(new THREE.TorusGeometry(1.08, 0.01, 8, 120), ringMaterial.clone());
  ringTwo.rotation.y = Math.PI / 2.7;
  avatar.add(ringTwo);

  const nodeMaterial = new THREE.MeshStandardMaterial({
    color: 0xdb6441,
    emissive: 0x401105,
    metalness: 0.35,
    roughness: 0.3
  });

  [
    [-1.85, .58, -.12],
    [1.6, .2, .3],
    [.38, 1.46, -.3],
    [-.42, -.98, .28],
    [1.08, -.78, -.1]
  ].forEach(([x, y, z]) => {
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.055, 18, 18), nodeMaterial);
    dot.position.set(x, y, z);
    avatar.add(dot);
  });

  avatar.position.set(1.4, .15, 0);
  scene.add(avatar);
}

function mountLoadedAvatar(gltf) {
  avatar = gltf.scene;
  avatar.scale.set(1.4, 1.4, 1.4);
  scene.add(avatar);
}

fetch("/avatar-model")
  .then(res => res.json())
  .then(data => {
    if (data.url) {
      loader.load(data.url, mountLoadedAvatar, undefined, mountFallbackAvatar);
      return;
    }
    mountFallbackAvatar();
  })
  .catch(mountFallbackAvatar);

function animate() {
  requestAnimationFrame(animate);
  if (avatar) {
    avatar.rotation.y += 0.006;
    avatar.rotation.x = Math.sin(Date.now() * 0.001) * 0.08;
  }
  blueprintGrid.position.z = (Date.now() * 0.00035) % 1;
  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = stage.clientWidth / stage.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(stage.clientWidth, stage.clientHeight);
});
