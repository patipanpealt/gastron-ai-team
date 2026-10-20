import { NextResponse } from "next/server";
import { ACTIVE_MODEL, DEFAULT_MODEL, DEMO_MODE, PROVIDER } from "@/lib/claude";
import { availableModels } from "@/lib/models";

export function GET() {
  return NextResponse.json({
    demo: DEMO_MODE,
    model: ACTIVE_MODEL,
    provider: PROVIDER,
    defaultModel: DEFAULT_MODEL?.id ?? null,
    models: availableModels().map(({ id, label, note }) => ({ id, label, note })),
  });
}
