import { NextResponse } from "next/server";
import { type Plan, type PlanTask, type RunKind, WORKER_IDS } from "@/lib/agents";
import { claude, DEMO_MODE, EFFORT, MODEL, PROVIDER, USE_FALLBACKS, errorMessage } from "@/lib/claude";
import { geminiJson } from "@/lib/gemini";
import { omniComplete } from "@/lib/omniroute";
import { demoPlan } from "@/lib/demo";
import { PLAN_SCHEMA, PLAN_SYSTEM, planPrompt } from "@/lib/prompts";

export const maxDuration = 300;

export async function POST(req: Request) {
  const { brief, kind = "graphic", names } = (await req.json()) as { brief?: string; kind?: RunKind; names?: Record<string, string> };
  if (!brief?.trim()) return NextResponse.json({ error: "กรุณาใส่ brief" }, { status: 400 });

  if (DEMO_MODE) {
    await new Promise((r) => setTimeout(r, 2500));
    return NextResponse.json({ plan: demoPlan(brief, kind), demo: true });
  }

  try {
    if (PROVIDER === "omniroute") {
      const raw = await omniComplete({
        system: PLAN_SYSTEM,
        user: `${planPrompt(brief, kind, names)}\n\nตอบเป็น JSON เท่านั้น ตาม schema นี้:\n${JSON.stringify(PLAN_SCHEMA)}`,
        maxTokens: 8000,
        json: true,
        signal: req.signal,
      });
      return NextResponse.json({ plan: sanitize(JSON.parse(raw.replace(/^```(?:json)?\s*|\s*```$/g, "")) as Plan) });
    }
    if (PROVIDER === "gemini") {
      const text = await geminiJson({
        system: PLAN_SYSTEM,
        user: `${planPrompt(brief, kind, names)}\n\nตอบเป็น JSON เท่านั้น ตาม schema นี้:\n${JSON.stringify(PLAN_SCHEMA)}`,
        maxTokens: 8000,
        signal: req.signal,
      });
      return NextResponse.json({ plan: sanitize(JSON.parse(text) as Plan) });
    }
    const res = await claude().beta.messages.create({
      model: MODEL,
      max_tokens: 16000,
      system: PLAN_SYSTEM,
      messages: [{ role: "user", content: planPrompt(brief, kind, names) }],
      output_config: { effort: EFFORT, format: { type: "json_schema", schema: PLAN_SCHEMA } },
      ...(USE_FALLBACKS ? { betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" as const } : {}),
    });
    if (res.stop_reason === "refusal") {
      return NextResponse.json({ error: "Claude ปฏิเสธ brief นี้ — ลองปรับถ้อยคำใหม่" }, { status: 422 });
    }
    const text = res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("");
    return NextResponse.json({ plan: sanitize(JSON.parse(text) as Plan) });
  } catch (err) {
    return NextResponse.json({ error: errorMessage(err) }, { status: 500 });
  }
}

/** Keep only valid agents and backward dependencies, and make sure QA closes the plan. */
function sanitize(plan: Plan): Plan {
  const seen = new Set<string>();
  const tasks: PlanTask[] = [];
  for (const t of plan.tasks) {
    if (!WORKER_IDS.includes(t.agent) || seen.has(t.id)) continue;
    tasks.push({ ...t, dependsOn: t.dependsOn.filter((d) => seen.has(d)) });
    seen.add(t.id);
  }
  const producers = tasks.filter((t) => t.agent !== "qa").map((t) => t.id);
  if (!tasks.some((t) => t.agent === "qa")) {
    tasks.push({
      id: `t${tasks.length + 1}`,
      agent: "qa",
      title: "ตรวจงานทั้งหมดก่อนส่ง",
      instructions: "ตรวจความถูกต้อง ความสอดคล้องกับแบรนด์ และความครบถ้วน แล้วสรุปสิ่งที่ต้องแก้",
      dependsOn: producers,
    });
  }
  return { summary: plan.summary, tasks };
}
