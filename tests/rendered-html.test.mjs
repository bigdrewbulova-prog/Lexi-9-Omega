import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const templateRoot = new URL("../", import.meta.url);

test("lexi home page is an evidence-to-action surface", async () => {
  const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  const layout = await readFile(new URL("../app/layout.tsx", import.meta.url), "utf8");
  const engine = await readFile(new URL("../app/lib/run-engine.ts", import.meta.url), "utf8");
  const route = await readFile(new URL("../app/api/runs/route.ts", import.meta.url), "utf8");
  const brightData = await readFile(new URL("../app/lib/bright-data.ts", import.meta.url), "utf8");
  const packageJson = await readFile(new URL("../package.json", import.meta.url), "utf8");

  assert.match(layout, /LEXI-9\/OMEGA/);
  assert.match(page, /EXECUTE RUN/);
  assert.match(page, /BRIGHT DATA LIVE/);
  assert.match(page, /fetch\("\/api\/runs"/);
  assert.match(page, /activeRun\.headline/);
  assert.match(page, /toggleApprove/);
  assert.match(engine, /export function synthesizeRun/);
  assert.match(engine, /mode: "local-live"/);
  assert.match(route, /export async function POST/);
  assert.match(route, /searchBrightData/);
  assert.match(brightData, /api\.brightdata\.com\/request/);
  assert.match(packageJson, /"vinext"/);
});

test("truth boundary and approval gates remain explicit", async () => {
  const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  const engine = await readFile(new URL("../app/lib/run-engine.ts", import.meta.url), "utf8");

  assert.match(page, /TRUTH BOUNDARY/);
  assert.match(page, /APPROVE/);
  assert.match(engine, /not a live web scrape/i);
  assert.match(engine, /Human approval required|approval/i);
});
