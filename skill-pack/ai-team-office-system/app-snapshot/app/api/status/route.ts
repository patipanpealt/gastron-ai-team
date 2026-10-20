import { NextResponse } from "next/server";
import { ACTIVE_MODEL, DEMO_MODE, PROVIDER } from "@/lib/claude";

export function GET() {
  return NextResponse.json({ demo: DEMO_MODE, model: ACTIVE_MODEL, provider: PROVIDER });
}
