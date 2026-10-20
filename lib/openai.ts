// OpenAI (ChatGPT models) over the Responses API, plain REST. Paid API key from platform.openai.com.
export const OPENAI_KEY = process.env.OPENAI_API_KEY || "";
export const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-6.1-sol";

interface Req {
  model?: string;
  system: string;
  user: string;
  maxTokens: number;
  json?: boolean;
  signal?: AbortSignal;
}

async function call(req: Req, stream: boolean) {
  const res = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${OPENAI_KEY}` },
    body: JSON.stringify({
      model: req.model || OPENAI_MODEL,
      instructions: req.system,
      input: req.user,
      max_output_tokens: req.maxTokens,
      stream,
      ...(req.json ? { text: { format: { type: "json_object" } } } : {}),
    }),
    signal: req.signal,
  });
  if (!res.ok) {
    const msg = ((await res.json().catch(() => ({}))) as { error?: { message?: string } }).error?.message ?? "";
    if (res.status === 401) throw new Error("OpenAI API key ไม่ถูกต้อง — ตรวจ OPENAI_API_KEY");
    if (res.status === 429) throw new Error("OpenAI: เกินโควต้าหรือเครดิตหมด (429)");
    throw new Error(`OpenAI API error ${res.status}: ${msg.slice(0, 200)}`);
  }
  return res;
}

export async function openaiStream(req: Req, onText: (t: string) => void) {
  const res = await call(req, true);
  const reader = res.body!.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let nl: number;
    while ((nl = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, nl).trim();
      buf = buf.slice(nl + 1);
      if (!line.startsWith("data:")) continue;
      let ev: { type?: string; delta?: string; error?: { message?: string } };
      try {
        ev = JSON.parse(line.slice(5));
      } catch {
        continue;
      }
      if (ev.type === "response.output_text.delta" && ev.delta) onText(ev.delta);
      else if (ev.type === "error" || ev.type === "response.failed") throw new Error(`OpenAI: ${ev.error?.message ?? "failed"}`);
    }
  }
}

export async function openaiComplete(req: Req): Promise<string> {
  const res = await call(req, false);
  const d = (await res.json()) as { output?: { content?: { type?: string; text?: string }[] }[] };
  return (d.output ?? []).flatMap((o) => o.content ?? []).filter((c) => c.type === "output_text").map((c) => c.text ?? "").join("");
}
