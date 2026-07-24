export type SourceKind = "PRIMARY" | "SECONDARY" | "METHOD" | "LIVE";

export type SourceCard = {
  domain: string;
  age: string;
  title: string;
  kind: SourceKind;
  url?: string;
  snippet?: string;
  rank?: number;
};

export type ActionItem = {
  id: string;
  title: string;
  meta: string;
  approved: boolean;
};

export type RunResult = {
  id: string;
  objective: string;
  createdAt: string;
  status: "complete";
  sources: number;
  actions: number;
  timeSaved: number;
  headline: string;
  summary: string;
  confidence: number;
  confidenceLabel: string;
  actionItems: ActionItem[];
  evidence: SourceCard[];
  primaryCount: number;
  mode: "local-live" | "bright-data-live";
  engine: string;
  truthBoundary: string;
  fetchedAt?: string;
};

type Theme = {
  key: string;
  match: RegExp;
  headline: string;
  summary: (objective: string) => string;
  confidence: number;
  confidenceLabel: string;
  actions: Array<[string, string]>;
  evidence: SourceCard[];
  timeSaved: number;
};

const themes: Theme[] = [
  {
    key: "predictive-maintenance",
    match: /maintenance|downtime|industrial|asset|vibration|factory|plant|rotat/i,
    headline: "Predictive maintenance is the strongest 30-day wedge.",
    summary: (objective) =>
      `For “${trimObjective(objective)}”, start with a narrow anomaly-detection pilot on one high-cost rotating asset. Value is measurable through avoided unplanned downtime, earlier intervention, and maintenance-hour reduction—without autonomous control.`,
    confidence: 82,
    confidenceLabel: "ENGINEERING ASSUMPTION",
    actions: [
      ["Select one asset with documented downtime cost", "Owner · Operations"],
      ["Capture a 14-day vibration and temperature baseline", "Gate · Data quality ≥ 95%"],
      ["Run alerts in shadow mode before operator review", "Safety · No autonomous actuation"],
      ["Define a weekly decision review with ops + reliability", "Cadence · 30-day pilot"],
    ],
    evidence: [
      { domain: "energy.gov", age: "2h", title: "Predictive maintenance and operational resilience", kind: "PRIMARY" },
      { domain: "nist.gov", age: "1d", title: "AI risk controls for operational systems", kind: "PRIMARY" },
      { domain: "industry survey", age: "3d", title: "Downtime cost and adoption signals", kind: "SECONDARY" },
    ],
    timeSaved: 43,
  },
  {
    key: "observability",
    match: /observab|monitor|tracing|telemetry|agent stack|llm ops|eval/i,
    headline: "Ship an agent observability pilot before multi-agent expansion.",
    summary: (objective) =>
      `For “${trimObjective(objective)}”, prioritize run-level traces, tool-call logs, cost counters, and human approval events. The decision edge is auditability and failure localization, not more agents.`,
    confidence: 78,
    confidenceLabel: "STACK ASSUMPTION",
    actions: [
      ["Instrument one critical agent path end-to-end", "Owner · Platform"],
      ["Store prompts, tool calls, and outcomes with retention policy", "Gate · Privacy review"],
      ["Add a weekly failure-class review from the ledger", "Cadence · Ops"],
      ["Block autonomous write actions until approval metrics exist", "Safety · Human gate"],
    ],
    evidence: [
      { domain: "opentelemetry.io", age: "5h", title: "Tracing patterns for multi-step workflows", kind: "PRIMARY" },
      { domain: "nist.gov", age: "2d", title: "AI system logging and accountability guidance", kind: "PRIMARY" },
      { domain: "vendor landscape", age: "4d", title: "Agent observability tooling comparison notes", kind: "SECONDARY" },
    ],
    timeSaved: 36,
  },
  {
    key: "security",
    match: /secur|vulnerab|openvas|threat|risk|compliance|audit/i,
    headline: "Treat security as an approval-gated evidence loop, not a one-shot scan.",
    summary: (objective) =>
      `For “${trimObjective(objective)}”, define ownership, authorized targets, and a remediation queue before expanding scan coverage. Proof of usefulness is closed findings with timestamps, not raw alert volume.`,
    confidence: 80,
    confidenceLabel: "CONTROL ASSUMPTION",
    actions: [
      ["Confirm target ownership and authorization in writing", "Owner · Security"],
      ["Run a bounded discovery scan on one approved host class", "Gate · Scope freeze"],
      ["Triage critical/high findings into a 7-day remediation board", "Cadence · Weekly"],
      ["Keep Lexi as planner/logger; execute scanners outside auto-mode", "Safety · No auto-exploit"],
    ],
    evidence: [
      { domain: "cisa.gov", age: "6h", title: "Vulnerability management prioritization guidance", kind: "PRIMARY" },
      { domain: "nist.gov", age: "1d", title: "Risk assessment and continuous monitoring", kind: "PRIMARY" },
      { domain: "internal policy", age: "2d", title: "Owner-approval requirements for active scanning", kind: "SECONDARY" },
    ],
    timeSaved: 39,
  },
  {
    key: "product-launch",
    match: /launch|market|showcase|pricing|gtm|customer|pilot offer/i,
    headline: "Run a bounded public showcase with explicit claim boundaries.",
    summary: (objective) =>
      `For “${trimObjective(objective)}”, convert the demo into a measurable pilot offer: one audience, one outcome, one proof metric, and a hard claim boundary. Avoid AGI language; sell governed usefulness.`,
    confidence: 74,
    confidenceLabel: "GO-TO-MARKET ASSUMPTION",
    actions: [
      ["Pick one buyer segment and one painful decision", "Owner · Founder"],
      ["Publish a 3-minute demo with truth-boundary copy", "Gate · Legal/claims review"],
      ["Collect 10 structured feedback responses", "Metric · Insight quality"],
      ["Convert feedback into a paid pilot checklist", "Cadence · 14 days"],
    ],
    evidence: [
      { domain: "product brief", age: "1h", title: "Showcase packet and claim-boundary notes", kind: "PRIMARY" },
      { domain: "market signals", age: "1d", title: "Demand for multimodal governed assistants", kind: "SECONDARY" },
      { domain: "pilot template", age: "2d", title: "30-day proof-of-usefulness checklist", kind: "SECONDARY" },
    ],
    timeSaved: 41,
  },
];

const fallback: Theme = {
  key: "general-decision",
  match: /.*/,
  headline: "Frame the objective as a 30-day decision with proof criteria.",
  summary: (objective) =>
    `For “${trimObjective(objective)}”, convert the question into: decision, evidence needed, uncertainty, next actions, and verification. Prefer primary sources, keep human approval on consequential steps, and log every useful event.`,
  confidence: 70,
  confidenceLabel: "METHOD ASSUMPTION",
  actions: [
    ["Restate the decision and success metric in one sentence", "Owner · Decision maker"],
    ["Collect 3 primary and 2 secondary evidence items", "Gate · Source quality"],
    ["List uncertainties that would reverse the recommendation", "Method · Red team"],
    ["Define a 7-day verification checkpoint", "Cadence · Review"],
  ],
  evidence: [
    { domain: "objective ledger", age: "now", title: "User-supplied research objective retained", kind: "PRIMARY" },
    { domain: "method card", age: "now", title: "Evidence → uncertainty → action → verify loop", kind: "METHOD" },
    { domain: "policy", age: "static", title: "Human approval required for consequential actions", kind: "SECONDARY" },
  ],
  timeSaved: 28,
};

function trimObjective(objective: string, max = 140): string {
  const cleaned = objective.replace(/\s+/g, " ").trim();
  if (cleaned.length <= max) return cleaned;
  return `${cleaned.slice(0, max - 1)}…`;
}

function pickTheme(objective: string): Theme {
  return themes.find((theme) => theme.match.test(objective)) ?? fallback;
}

function nextRunId(existingCount: number): string {
  const n = 92 + Math.max(0, existingCount);
  return `LX-${String(n).padStart(3, "0")}`;
}

function formatCreatedAt(date = new Date()): string {
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function synthesizeRun(
  objective: string,
  options?: { existingCount?: number; now?: Date },
): RunResult {
  const cleaned = objective.replace(/\s+/g, " ").trim();
  if (!cleaned) {
    throw new Error("Objective is required.");
  }
  if (cleaned.length > 220) {
    throw new Error("Objective must be 220 characters or fewer.");
  }

  const theme = pickTheme(cleaned);
  const actionItems: ActionItem[] = theme.actions.map(([title, meta], index) => ({
    id: String(index + 1).padStart(2, "0"),
    title,
    meta,
    approved: false,
  }));

  const methodCard: SourceCard = {
    domain: "run log",
    age: "now",
    title: "Source selection, timestamps, and confidence labels retained",
    kind: "METHOD",
  };

  const evidence = [...theme.evidence, methodCard];
  const primaryCount = evidence.filter((item) => item.kind === "PRIMARY").length;

  return {
    id: nextRunId(options?.existingCount ?? 0),
    objective: cleaned,
    createdAt: formatCreatedAt(options?.now),
    status: "complete",
    sources: evidence.length,
    actions: actionItems.length,
    timeSaved: theme.timeSaved,
    headline: theme.headline,
    summary: theme.summary(cleaned),
    confidence: theme.confidence,
    confidenceLabel: theme.confidenceLabel,
    actionItems,
    evidence,
    primaryCount,
    mode: "local-live",
    engine: `local-theme:${theme.key}`,
    truthBoundary:
      "This is a local live synthesis from the objective text and theme library. It is not a live web scrape. Production runs must attach real source URLs and timestamps.",
  };
}

export function attachLiveEvidence(
  run: RunResult,
  evidence: SourceCard[],
  fetchedAt = new Date(),
): RunResult {
  const liveEvidence = evidence.filter(
    (source) => source.kind === "LIVE" && source.url?.startsWith("https://"),
  );
  if (liveEvidence.length === 0) return run;

  return {
    ...run,
    evidence: liveEvidence,
    sources: liveEvidence.length,
    primaryCount: 0,
    mode: "bright-data-live",
    engine: "bright-data:serp-api:parsed-light",
    fetchedAt: fetchedAt.toISOString(),
    truthBoundary:
      "These are live search-result records returned by Bright Data SERP API. Titles and snippets are discovery evidence, not independently verified facts. Open the source URL before relying on a claim.",
  };
}

export const seedRuns: RunResult[] = [
  {
    ...synthesizeRun(
      "Map the strongest evidence for industrial predictive-maintenance demand",
      { existingCount: 0, now: new Date("2026-07-16T10:42:00") },
    ),
    id: "LX-091",
    createdAt: "Jul 16, 10:42 AM",
  },
  {
    ...synthesizeRun(
      "Compare current agent observability tools for a pilot stack",
      { existingCount: 0, now: new Date("2026-07-15T16:18:00") },
    ),
    id: "LX-090",
    createdAt: "Jul 15, 4:18 PM",
  },
];
