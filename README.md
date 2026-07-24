# LEXI-9/OMEGA

LEXI-9/OMEGA is an evidence-to-action decision-support demo built for the
HackerNoon Proof of Usefulness hackathon. It converts a bounded research
objective into an explicit recommendation, confidence label, evidence ledger,
approval-gated actions, and a locally retained run history.

## What works

- Objective-specific synthesis for industrial maintenance, observability,
  defensive security, product-launch, and general decision workflows
- Server API with an offline browser fallback
- Evidence and uncertainty labels
- Human approval controls for proposed actions
- Device-local proof ledger and usefulness metrics
- Responsive judge-facing interface

## Truth boundary

The included engine is a deterministic local demonstration. Its evidence cards
are clearly labeled fixtures, not live web results. It does not claim to have
scraped, verified, or executed external actions. A production integration must
attach real source URLs and timestamps, enforce policy in code, and record
execution receipts separately from model proposals.

## Run locally

Requirements: Node.js 22.13 or newer.

```bash
npm install
npm test
npm run dev
```

The production build is Cloudflare Workers-compatible through vinext.

## API

Create a run:

```bash
curl -X POST http://localhost:3000/api/runs \
  -H 'content-type: application/json' \
  -d '{"objective":"Which industrial AI pilot has measurable 30-day ROI?"}'
```

The endpoint validates the objective and returns a decision brief, evidence
cards, confidence metadata, proposed actions, and a truth-boundary statement.

## Validation

```bash
npm test
```

This runs the engine and rendered-interface tests, followed by a production
build.

## Roadmap

1. Connect Bright Data for timestamped public-web evidence.
2. Persist consented run telemetry and outcome confirmations.
3. Separate proposal, approval, execution, and verification receipts.
4. Publish anonymized adoption metrics for the Proof of Usefulness report.

## Hackathon tags

`#proof-of-usefulness` `#ai` `#ai-agents` `#data` `#automation`
