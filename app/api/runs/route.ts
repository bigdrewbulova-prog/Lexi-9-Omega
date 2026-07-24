import { NextResponse } from "next/server";
import {
  BrightDataConfigurationError,
  brightDataConfigFromEnv,
  searchBrightData,
} from "../../lib/bright-data";
import { attachLiveEvidence, synthesizeRun } from "../../lib/run-engine";

export const dynamic = "force-dynamic";

type RunRequestBody = {
  objective?: string;
  existingCount?: number;
};

export async function POST(request: Request) {
  let body: RunRequestBody = {};
  try {
    body = (await request.json()) as RunRequestBody;
  } catch {
    return NextResponse.json(
      { error: "Request body must be JSON with an objective string." },
      { status: 400 },
    );
  }

  const objective = typeof body.objective === "string" ? body.objective : "";
  const existingCount =
    typeof body.existingCount === "number" && Number.isFinite(body.existingCount)
      ? Math.max(0, Math.floor(body.existingCount))
      : 0;

  try {
    const localRun = synthesizeRun(objective, { existingCount });
    let run = localRun;
    let liveStatus: "connected" | "not-configured" | "unavailable" = "not-configured";

    try {
      const evidence = await searchBrightData(objective, brightDataConfigFromEnv());
      run = attachLiveEvidence(localRun, evidence);
      liveStatus = run.mode === "bright-data-live" ? "connected" : "unavailable";
    } catch (error) {
      if (!(error instanceof BrightDataConfigurationError)) {
        liveStatus = "unavailable";
        console.error("Bright Data live search unavailable", error);
      }
    }

    return NextResponse.json({ run, liveStatus }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to create run.";
    return NextResponse.json({ error: message }, { status: 400 });
  }
}

export async function GET() {
  return NextResponse.json({
    service: "lexi-9-omega-runs",
    mode: process.env.BRIGHT_DATA_API_TOKEN ? "bright-data-live" : "local-live",
    methods: ["POST"],
    body: {
      objective: "string (required, max 220)",
      existingCount: "number (optional)",
    },
  });
}
