import { claude, DEMO_MODE, EFFORT, MODEL, PROVIDER, USE_FALLBACKS, errorMessage } from "@/lib/claude";
import { geminiStream } from "@/lib/gemini";
import { demoOutput } from "@/lib/demo";
import { type AgentRequest, systemFor, userMessageFor } from "@/lib/prompts";

export const maxDuration = 300;

// Streams one agent's work as NDJSON lines: {type:"thinking"|"text", text} …
// then {type:"done"} or {type:"error", message}.
export async function POST(req: Request) {
  const body = (await req.json()) as AgentRequest;
  const enc = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const send = (obj: object) => controller.enqueue(enc.encode(JSON.stringify(obj) + "\n"));
      try {
        if (DEMO_MODE) await runDemo(body, send);
        else if (PROVIDER === "gemini") await runGemini(body, send, req.signal);
        else await runClaude(body, send, req.signal);
        send({ type: "done" });
      } catch (err) {
        send({ type: "error", message: errorMessage(err) });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: { "Content-Type": "application/x-ndjson; charset=utf-8", "Cache-Control": "no-store" },
  });
}

async function runGemini(body: AgentRequest, send: (o: object) => void, signal: AbortSignal) {
  const system = systemFor(body.mode === "compile" ? "director" : body.agentId, body.kind, body.names, body.mode === "chat", body.memory)
    .map((b) => b.text)
    .join("\n\n");
  await geminiStream(
    { system, user: userMessageFor(body), maxTokens: body.mode === "chat" ? 1500 : 16000, signal },
    (text) => send({ type: "text", text }),
  );
}

async function runClaude(body: AgentRequest, send: (o: object) => void, signal: AbortSignal) {
  const stream = claude().beta.messages.stream(
    {
      model: MODEL,
      max_tokens: body.mode === "chat" ? 1500 : 32000,
      system: systemFor(body.mode === "compile" ? "director" : body.agentId, body.kind, body.names, body.mode === "chat", body.memory),
      messages: [{ role: "user", content: userMessageFor(body) }],
      // a turn of conversation is short and quick: no extended thinking
      ...(body.mode === "chat" ? {} : { thinking: { type: "adaptive" as const, display: "summarized" as const } }),
      output_config: { effort: body.mode === "compile" ? "high" : body.mode === "chat" ? "low" : EFFORT },
      ...(USE_FALLBACKS ? { betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" as const } : {}),
    },
    { signal },
  );
  for await (const event of stream) {
    if (event.type !== "content_block_delta") continue;
    if (event.delta.type === "thinking_delta") send({ type: "thinking", text: event.delta.thinking });
    else if (event.delta.type === "text_delta") send({ type: "text", text: event.delta.text });
  }
  const final = await stream.finalMessage();
  if (final.stop_reason === "refusal") throw new Error("Claude ปฏิเสธงานชิ้นนี้ (refusal)");
  if (final.stop_reason === "max_tokens") send({ type: "text", text: "\n\n_(ข้อความถูกตัดเพราะยาวเกินกำหนด)_" });
}

async function runDemo(body: AgentRequest, send: (o: object) => void) {
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
  const { thought, text } = demoOutput(body);
  for (const word of thought.split(" ")) {
    send({ type: "thinking", text: word + " " });
    await sleep(180);
  }
  for (let i = 0; i < text.length; i += 6) {
    send({ type: "text", text: text.slice(i, i + 6) });
    await sleep(35 + Math.random() * 40);
  }
}
