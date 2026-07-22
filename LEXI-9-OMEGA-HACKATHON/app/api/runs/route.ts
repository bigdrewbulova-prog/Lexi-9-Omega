import { NextResponse } from "next/server";
import { synthesizeRun } from "../../lib/run-engine";

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
    const run = synthesizeRun(objective, { existingCount });
    return NextResponse.json({ run }, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to create run.";
    return NextResponse.json({ error: message }, { status: 400 });
  }
}

export async function GET() {
  return NextResponse.json({
    service: "lexi-9-omega-runs",
    mode: "local-live",
    methods: ["POST"],
    body: {
      objective: "string (required, max 220)",
      existingCount: "number (optional)",
    },
  });
}
