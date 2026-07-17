"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Run = {
  id: string;
  objective: string;
  createdAt: string;
  status: "complete";
  sources: number;
  actions: number;
  timeSaved: number;
};

const seedRuns: Run[] = [
  { id: "LX-091", objective: "Map the strongest evidence for industrial predictive-maintenance demand", createdAt: "Jul 16, 10:42 AM", status: "complete", sources: 18, actions: 4, timeSaved: 47 },
  { id: "LX-090", objective: "Compare current agent observability tools for a pilot stack", createdAt: "Jul 15, 4:18 PM", status: "complete", sources: 12, actions: 3, timeSaved: 31 },
];

const sourceCards = [
  { domain: "energy.gov", age: "2h", title: "Predictive maintenance and operational resilience", kind: "PRIMARY" },
  { domain: "nist.gov", age: "1d", title: "AI risk controls for operational systems", kind: "PRIMARY" },
  { domain: "industry survey", age: "3d", title: "Downtime cost and adoption signals", kind: "SECONDARY" },
];

export default function Home() {
  const [objective, setObjective] = useState("Which industrial AI use case has the clearest measurable ROI for a 30-day pilot?");
  const [runs, setRuns] = useState<Run[]>(seedRuns);
  const [activeRun, setActiveRun] = useState<Run>(seedRuns[0]);
  const [isRunning, setIsRunning] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("lexi-runs");
    if (stored) {
      const parsed = JSON.parse(stored) as Run[];
      setRuns(parsed);
      setActiveRun(parsed[0] ?? seedRuns[0]);
    }
  }, []);

  const metrics = useMemo(() => ({
    runs: runs.length,
    sources: runs.reduce((sum, run) => sum + run.sources, 0),
    actions: runs.reduce((sum, run) => sum + run.actions, 0),
    minutes: runs.reduce((sum, run) => sum + run.timeSaved, 0),
  }), [runs]);

  function startRun(event: FormEvent) {
    event.preventDefault();
    if (!objective.trim() || isRunning) return;
    setIsRunning(true);
    window.setTimeout(() => {
      const run: Run = {
        id: `LX-${String(92 + runs.length).padStart(3, "0")}`,
        objective: objective.trim(),
        createdAt: "just now",
        status: "complete",
        sources: 16,
        actions: 4,
        timeSaved: 43,
      };
      const next = [run, ...runs];
      setRuns(next);
      setActiveRun(run);
      window.localStorage.setItem("lexi-runs", JSON.stringify(next));
      setIsRunning(false);
    }, 900);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="LEXI-9-OMEGA home">
          <span className="brand-mark"><i /><i /><i /></span>
          <span>LEXI-9<span>/OMEGA</span></span>
        </a>
        <div className="system-state"><span /> SYSTEM NOMINAL <b>v0.9</b></div>
        <nav aria-label="Primary navigation">
          <a href="#mission">Mission</a><a href="#evidence">Evidence</a><a href="#impact">Impact</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">EVIDENCE-TO-ACTION INTELLIGENCE</p>
          <h1>Research that ends<br />in a <em>decision.</em></h1>
          <p className="lede">LEXI turns a real objective into current evidence, explicit uncertainty, prioritized actions, and a verifiable outcome trail.</p>
          <div className="truth-row"><span>LIVE DATA READY</span><span>HUMAN APPROVAL</span><span>AUDITABLE RUNS</span></div>
        </div>
        <div className="core-stage" aria-label="Animated LEXI intelligence core">
          <div className="core-grid" />
          <div className="orbit orbit-one"><b /><b /><b /></div>
          <div className="orbit orbit-two"><b /><b /></div>
          <div className="core-glow"><span>LEXI</span><strong>9Ω</strong><small>ACTIVE CORE</small></div>
          <div className="core-label label-a">01 / INGEST</div><div className="core-label label-b">02 / VERIFY</div><div className="core-label label-c">03 / DECIDE</div>
        </div>
      </section>

      <section className="mission-panel" id="mission">
        <div className="section-heading"><span>01</span><div><p>MISSION CONTROL</p><h2>Give LEXI a decision to support.</h2></div></div>
        <form onSubmit={startRun}>
          <label htmlFor="objective">RESEARCH OBJECTIVE</label>
          <div className="objective-box">
            <textarea id="objective" value={objective} onChange={(e) => setObjective(e.target.value)} maxLength={220} />
            <button type="submit" disabled={isRunning}>{isRunning ? "SYNTHESIZING…" : "EXECUTE RUN →"}</button>
          </div>
          <div className="run-settings"><span>MODE <b>Evidence-first</b></span><span>APPROVAL <b>Required</b></span><span>SOURCE POLICY <b>Primary preferred</b></span><span className="demo-label">DEMO FIXTURE · CONNECT BRIGHT DATA FOR LIVE SOURCES</span></div>
        </form>
      </section>

      <section className="result-grid" id="evidence">
        <div className="result-main">
          <div className="panel-header"><span>RUN {activeRun.id}</span><span className="complete">● COMPLETE</span><span>{activeRun.createdAt}</span></div>
          <div className="result-body">
            <p className="micro">DECISION BRIEF / GENERATED OUTPUT</p>
            <h2>Predictive maintenance is the strongest 30-day wedge.</h2>
            <p className="summary">Start with a narrow anomaly-detection pilot on one high-cost rotating asset. The value is measurable through avoided unplanned downtime, earlier intervention, and maintenance-hour reduction—without requiring autonomous control.</p>
            <div className="confidence"><span>CONFIDENCE</span><div><i style={{width: "82%"}} /></div><strong>82%</strong><small>ENGINEERING ASSUMPTION</small></div>
            <div className="actions">
              <p className="micro">RECOMMENDED ACTIONS</p>
              {[
                ["01", "Select one asset with documented downtime cost", "Owner · Operations"],
                ["02", "Capture a 14-day vibration and temperature baseline", "Gate · Data quality ≥ 95%"],
                ["03", "Run alerts in shadow mode before operator review", "Safety · No autonomous actuation"],
              ].map(([n, title, meta]) => <div className="action" key={n}><b>{n}</b><span>{title}<small>{meta}</small></span><button aria-label={`Approve action ${n}`}>APPROVE</button></div>)}
            </div>
          </div>
        </div>

        <aside className="evidence-panel">
          <div className="panel-header"><span>EVIDENCE LEDGER</span><button onClick={() => setShowEvidence(!showEvidence)}>{showEvidence ? "COLLAPSE" : "INSPECT ALL"}</button></div>
          <div className="evidence-count"><strong>{activeRun.sources}</strong><span>SOURCES<br />INGESTED</span><b>3 PRIMARY</b></div>
          <div className="sources">
            {sourceCards.map((source) => <article key={source.domain}><div><span>{source.kind}</span><time>{source.age}</time></div><h3>{source.title}</h3><p>{source.domain} ↗</p></article>)}
            {showEvidence && <article><div><span>METHOD</span><time>run log</time></div><h3>Source selection, timestamps, and confidence labels retained</h3><p>Open audit trail ↗</p></article>}
          </div>
          <div className="boundary"><b>TRUTH BOUNDARY</b><p>Claims above are demo output, not verified industrial findings. Production runs must preserve source URLs and timestamps.</p></div>
        </aside>
      </section>

      <section className="impact" id="impact">
        <div className="section-heading"><span>02</span><div><p>PROOF OF USEFULNESS</p><h2>Every useful event leaves evidence.</h2></div></div>
        <div className="metrics">
          <article><p>COMPLETED RUNS</p><strong>{metrics.runs}</strong><span>on this device</span></article>
          <article><p>SOURCES PROCESSED</p><strong>{metrics.sources}</strong><span>demo + run ledger</span></article>
          <article><p>ACTIONS PRODUCED</p><strong>{metrics.actions}</strong><span>approval-gated</span></article>
          <article className="accent"><p>TIME SAVED</p><strong>{metrics.minutes}<small> min</small></strong><span>user-reported estimate</span></article>
        </div>
        <div className="run-log"><div className="run-log-head"><span>RECENT RUNS</span><span>LOCAL PROOF LEDGER</span></div>{runs.slice(0, 4).map(run => <button key={run.id} onClick={() => setActiveRun(run)}><b>{run.id}</b><span>{run.objective}</span><small>{run.sources} sources · {run.actions} actions</small><i>OPEN →</i></button>)}</div>
      </section>

      <footer><div><strong>LEXI-9/OMEGA</strong><p>Observe → Interpret → Predict → Decide → Act → Verify → Learn</p></div><div><span>#AI-AGENTS</span><span>#DATA</span><span>#AUTOMATION</span><span>#PROOF-OF-USEFULNESS</span></div><p>Built for measurable utility. No fictional capabilities presented as fact.</p></footer>
    </main>
  );
}
