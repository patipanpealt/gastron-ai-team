import { NextResponse } from "next/server";
import { kv, kvEnabled } from "@/lib/kv";

// Team-wide "สอนทีม" notes and finished runs, shared by everyone who is logged in.
const MEMORY = "gastron:memory";
const RUNS = "gastron:runs"; // hash: run id -> run JSON
const RUN_IDX = "gastron:runs:idx"; // sorted set: run id scored by createdAt
const MAX_RUNS = 30;
const MAX_MEMORY = 200;

export async function GET() {
  if (!kvEnabled()) return NextResponse.json({ shared: false });
  try {
    const memory = JSON.parse((await kv<string | null>("GET", MEMORY)) || "[]");
    const ids = await kv<string[]>("ZRANGE", RUN_IDX, 0, MAX_RUNS - 1, "REV");
    const runs = ids.length ? (await kv<(string | null)[]>("HMGET", RUNS, ...ids)).filter(Boolean).map((s) => JSON.parse(s!)) : [];
    return NextResponse.json({ shared: true, memory, runs });
  } catch (err) {
    return NextResponse.json({ shared: false, error: err instanceof Error ? err.message : String(err) }, { status: 502 });
  }
}

export async function PUT(req: Request) {
  if (!kvEnabled()) return NextResponse.json({ shared: false });
  const { memory } = (await req.json()) as { memory?: unknown };
  if (!Array.isArray(memory)) return NextResponse.json({ error: "memory must be a list" }, { status: 400 });
  await kv("SET", MEMORY, JSON.stringify(memory.slice(0, MAX_MEMORY)));
  return NextResponse.json({ ok: true });
}

export async function POST(req: Request) {
  if (!kvEnabled()) return NextResponse.json({ shared: false });
  const { run } = (await req.json()) as { run?: { id?: string; createdAt?: number } };
  if (!run?.id || typeof run.createdAt !== "number") return NextResponse.json({ error: "bad run" }, { status: 400 });
  await kv("HSET", RUNS, run.id, JSON.stringify(run));
  await kv("ZADD", RUN_IDX, run.createdAt, run.id);
  // keep the newest MAX_RUNS
  const old = await kv<string[]>("ZRANGE", RUN_IDX, 0, -(MAX_RUNS + 1));
  if (old.length) {
    await kv("HDEL", RUNS, ...old);
    await kv("ZREM", RUN_IDX, ...old);
  }
  return NextResponse.json({ ok: true });
}
