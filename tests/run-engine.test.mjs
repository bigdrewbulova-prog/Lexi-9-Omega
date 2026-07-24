import assert from "node:assert/strict";
import test from "node:test";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Compile/import the TS engine via a tiny tsx-free approach: duplicate critical
// assertions against the built server route behavior when available, and unit
// test logic through a JS mirror executed by node --experimental-strip-types.

const enginePath = new URL("../app/lib/run-engine.ts", import.meta.url);

test("local live engine synthesizes objective-specific runs", async () => {
  // Node 22+ can strip types for direct import.
  const mod = await import(`${enginePath.href}?t=${Date.now()}`);
  const run = mod.synthesizeRun(
    "Which industrial AI use case has the clearest measurable ROI for a 30-day pilot?",
    { existingCount: 2 },
  );

  assert.equal(run.status, "complete");
  assert.equal(run.mode, "local-live");
  assert.match(run.id, /^LX-\d{3}$/);
  assert.match(run.headline.toLowerCase(), /maintenance|wedge|predictive/);
  assert.ok(run.actionItems.length >= 3);
  assert.ok(run.evidence.length >= 3);
  assert.ok(run.confidence >= 50 && run.confidence <= 100);
  assert.match(run.truthBoundary, /not a live web scrape/i);
});

test("engine rejects empty objectives", async () => {
  const mod = await import(`${enginePath.href}?t=${Date.now()}`);
  assert.throws(() => mod.synthesizeRun("   "), /required/i);
});

test("seed runs are available for the demo ledger", async () => {
  const mod = await import(`${enginePath.href}?t=${Date.now()}`);
  assert.ok(Array.isArray(mod.seedRuns));
  assert.ok(mod.seedRuns.length >= 2);
  assert.equal(mod.seedRuns[0].id, "LX-091");
});

test("live Bright Data evidence upgrades a local run without claiming verification", async () => {
  const mod = await import(`${enginePath.href}?t=${Date.now()}`);
  const local = mod.synthesizeRun("industrial maintenance evidence");
  const live = mod.attachLiveEvidence(local, [{
    domain: "nist.gov",
    age: "live",
    title: "A live search result",
    kind: "LIVE",
    url: "https://www.nist.gov/example",
    snippet: "Search-result snippet",
    rank: 1,
  }], new Date("2026-07-24T12:00:00Z"));

  assert.equal(live.mode, "bright-data-live");
  assert.equal(live.sources, 1);
  assert.match(live.engine, /bright-data/);
  assert.match(live.truthBoundary, /not independently verified/i);
});

test("Bright Data adapter sends server-side bearer auth and parses organic results", async () => {
  const adapterPath = new URL("../app/lib/bright-data.ts", import.meta.url);
  const mod = await import(`${adapterPath.href}?t=${Date.now()}`);
  let request;
  const fakeFetch = async (url, init) => {
    request = { url, init };
    return new Response(JSON.stringify({
      organic: [
        {
          link: "https://example.com/report",
          title: "Current report",
          description: "Fresh source description",
          global_rank: 1,
        },
      ],
    }), { status: 200, headers: { "content-type": "application/json" } });
  };

  const results = await mod.searchBrightData(
    "current industrial AI evidence",
    { token: "test-token", zone: "test-zone", country: "us", language: "en" },
    fakeFetch,
  );

  assert.equal(request.url, "https://api.brightdata.com/request");
  assert.equal(request.init.headers.authorization, "Bearer test-token");
  assert.match(request.init.body, /test-zone/);
  assert.equal(results[0].kind, "LIVE");
  assert.equal(results[0].url, "https://example.com/report");
});
