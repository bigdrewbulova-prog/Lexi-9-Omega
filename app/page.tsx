"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { seedRuns, synthesizeRun, type RunResult } from "./lib/run-engine";

const STORAGE_KEY = "lexi-runs-v2";

export default function Home() {
  const [objective, setObjective] = useState(
    "Which industrial AI use case has the clearest measurable ROI for a 30-day pilot?",
  );
  const [runs, setRuns] = useState<RunResult[]>(seedRuns);
  const [activeRun, setActiveRun] = useState<RunResult>(seedRuns[0]);
  const [isRunning, setIsRunning] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as RunResult[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setRuns(parsed);
          setActiveRun(parsed[0]);
        }
      }
    } catch {
      // Ignore corrupt local storage and keep seeds.
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(runs));
  }, [runs, hydrated]);

  const metrics = useMemo(
    () => ({
      runs: runs.length,
      sources: runs.reduce((sum, run) => sum + run.sources, 0),
      actions: runs.reduce((sum, run) => sum + run.actions, 0),
      minutes: runs.reduce((sum, run) => sum + run.timeSaved, 0),
    }),
    [runs],
  );

  async function startRun(event: FormEvent) {
    event.preventDefault();
    if (!objective.trim() || isRunning) return;

    setIsRunning(true);
    setError(null);

    try {
      let run: RunResult | null = null;

      try {
        const response = await fetch("/api/runs", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            objective: objective.trim(),
            existingCount: runs.length,
          }),
        });
        const payload = (await response.json()) as { run?: RunResult; error?: string };
        if (response.ok && payload.run) {
          run = payload.run;
        }
      } catch {
        // Fall through to local live engine when API is offline.
      }

      // Local live fallback keeps the demo runnable without a server.
      if (!run) {
        run = synthesizeRun(objective.trim(), { existingCount: runs.length });
      }

      setRuns((previous) => [run!, ...previous]);
      setActiveRun(run);
      setShowEvidence(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed.");
    } finally {
      setIsRunning(false);
    }
  }

  function toggleApprove(actionId: string) {
    setActiveRun((current) => {
      const next: RunResult = {
        ...current,
        actionItems: current.actionItems.map((item) =>
          item.id === actionId ? { ...item, approved: !item.approved } : item,
        ),
      };
      setRuns((previous) => previous.map((run) => (run.id === current.id ? next : run)));
      return next;
    });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="LEXI-9-OMEGA home">
          <span className="brand-mark">
            <i />
            <i />
            <i />
          </span>
          <span>
            LEXI-9<span>/OMEGA</span>
          </span>
        </a>
        <div className="system-state">
          <span /> SYSTEM NOMINAL <b>v0.9</b>
        </div>
        <nav aria-label="Primary navigation">
          <a href="#mission">Mission</a>
          <a href="#evidence">Evidence</a>
          <a href="#impact">Impact</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">EVIDENCE-TO-ACTION INTELLIGENCE</p>
          <h1>
            Research that ends
            <br /> in a <em>decision.</em>
          </h1>
          <p className="lede">
            LEXI turns a real objective into current evidence, explicit uncertainty, prioritized
            actions, and a verifiable outcome trail.
          </p>
          <div className="truth-row">
            <span>LIVE DATA READY</span>
            <span>HUMAN APPROVAL</span>
            <span>AUDITABLE RUNS</span>
          </div>
        </div>
        <div className="core-stage" aria-label="Animated LEXI intelligence core">
          <div className="core-grid" />
          <div className="orbit orbit-one">
            <b />
            <b />
            <b />
          </div>
          <div className="orbit orbit-two">
            <b />
            <b />
          </div>
          <div className="core-glow">
            <span>LEXI</span>
            <strong>9Ω</strong>
            <small>ACTIVE CORE</small>
          </div>
          <div className="core-label label-a">01 / INGEST</div>
          <div className="core-label label-b">02 / VERIFY</div>
          <div className="core-label label-c">03 / DECIDE</div>
        </div>
      </section>

      <section className="mission-panel" id="mission">
        <div className="section-heading">
          <span>01</span>
          <div>
            <p>MISSION CONTROL</p>
            <h2>Give LEXI a decision to support.</h2>
          </div>
        </div>
        <form onSubmit={startRun}>
          <label htmlFor="objective">RESEARCH OBJECTIVE</label>
          <div className="objective-box">
            <textarea
              id="objective"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              maxLength={220}
            />
            <button type="submit" disabled={isRunning}>
              {isRunning ? "SYNTHESIZING…" : "EXECUTE RUN →"}
            </button>
          </div>
          <div className="run-settings">
            <span>
              MODE <b>Evidence-first</b>
            </span>
            <span>
              APPROVAL <b>Required</b>
            </span>
            <span>
              SOURCE POLICY <b>Primary preferred</b>
            </span>
            <span className="demo-label">
              {activeRun.mode === "bright-data-live"
                ? "BRIGHT DATA LIVE · SEARCH RESULTS ATTACHED"
                : "LOCAL FALLBACK · LIVE SEARCH UNAVAILABLE"}
            </span>
          </div>
          {error ? (
            <p role="alert" style={{ color: "#ff5c35", marginTop: 14, fontFamily: "var(--font-mono)", fontSize: 12 }}>
              {error}
            </p>
          ) : null}
        </form>
      </section>

      <section className="result-grid" id="evidence">
        <div className="result-main">
          <div className="panel-header">
            <span>RUN {activeRun.id}</span>
            <span className="complete">● COMPLETE</span>
            <span>{activeRun.createdAt}</span>
          </div>
          <div className="result-body">
            <p className="micro">DECISION BRIEF / GENERATED OUTPUT</p>
            <h2>{activeRun.headline}</h2>
            <p className="summary">{activeRun.summary}</p>
            <div className="confidence">
              <span>CONFIDENCE</span>
              <div>
                <i style={{ width: `${activeRun.confidence}%` }} />
              </div>
              <strong>{activeRun.confidence}%</strong>
              <small>{activeRun.confidenceLabel}</small>
            </div>
            <div className="actions">
              <p className="micro">RECOMMENDED ACTIONS</p>
              {activeRun.actionItems.map((item) => (
                <div className="action" key={item.id}>
                  <b>{item.id}</b>
                  <span>
                    {item.title}
                    <small>{item.meta}</small>
                  </span>
                  <button
                    type="button"
                    aria-label={`${item.approved ? "Revoke" : "Approve"} action ${item.id}`}
                    onClick={() => toggleApprove(item.id)}
                    style={item.approved ? { borderColor: "var(--acid)", color: "var(--acid)" } : undefined}
                  >
                    {item.approved ? "APPROVED" : "APPROVE"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <aside className="evidence-panel">
          <div className="panel-header">
            <span>EVIDENCE LEDGER</span>
            <button type="button" onClick={() => setShowEvidence(!showEvidence)}>
              {showEvidence ? "COLLAPSE" : "INSPECT ALL"}
            </button>
          </div>
          <div className="evidence-count">
            <strong>{activeRun.sources}</strong>
            <span>
              SOURCES
              <br />
              INGESTED
            </span>
            <b>
              {activeRun.mode === "bright-data-live"
                ? "BRIGHT DATA LIVE"
                : `${activeRun.primaryCount} PRIMARY`}
            </b>
          </div>
          <div className="sources">
            {(showEvidence ? activeRun.evidence : activeRun.evidence.slice(0, 3)).map((source) => (
              <article key={`${source.domain}-${source.title}`}>
                <div>
                  <span>{source.kind}</span>
                  <time>{source.age}</time>
                </div>
                <h3>{source.title}</h3>
                {source.snippet && <p>{source.snippet}</p>}
                {source.url ? (
                  <a href={source.url} target="_blank" rel="noreferrer">
                    {source.domain} ↗
                  </a>
                ) : (
                  <p>{source.domain}</p>
                )}
              </article>
            ))}
          </div>
          <div className="boundary">
            <b>TRUTH BOUNDARY</b>
            <p>{activeRun.truthBoundary}</p>
          </div>
        </aside>
      </section>

      <section className="impact" id="impact">
        <div className="section-heading">
          <span>02</span>
          <div>
            <p>PROOF OF USEFULNESS</p>
            <h2>Every useful event leaves evidence.</h2>
          </div>
        </div>
        <div className="metrics">
          <article>
            <p>COMPLETED RUNS</p>
            <strong>{metrics.runs}</strong>
            <span>on this device</span>
          </article>
          <article>
            <p>SOURCES PROCESSED</p>
            <strong>{metrics.sources}</strong>
            <span>live + fallback ledger</span>
          </article>
          <article>
            <p>ACTIONS PRODUCED</p>
            <strong>{metrics.actions}</strong>
            <span>approval-gated</span>
          </article>
          <article className="accent">
            <p>TIME SAVED</p>
            <strong>
              {metrics.minutes}
              <small> min</small>
            </strong>
            <span>user-reported estimate</span>
          </article>
        </div>
        <div className="run-log">
          <div className="run-log-head">
            <span>RECENT RUNS</span>
            <span>LOCAL PROOF LEDGER</span>
          </div>
          {runs.slice(0, 6).map((run) => (
            <button key={run.id} type="button" onClick={() => setActiveRun(run)}>
              <b>{run.id}</b>
              <span>{run.objective}</span>
              <small>
                {run.sources} sources · {run.actions} actions
              </small>
              <i>OPEN →</i>
            </button>
          ))}
        </div>
      </section>

      <footer>
        <div>
          <strong>LEXI-9/OMEGA</strong>
          <p>Observe → Interpret → Predict → Decide → Act → Verify → Learn</p>
        </div>
        <div>
          <span>#AI-AGENTS</span>
          <span>#DATA</span>
          <span>#AUTOMATION</span>
          <span>#PROOF-OF-USEFULNESS</span>
        </div>
        <p>Built for measurable utility. No fictional capabilities presented as fact.</p>
      </footer>
    </main>
  );
}
