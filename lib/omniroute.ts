// OmniRoute: a local OpenAI-compatible router in front of many AI providers (and their free tiers).
// The model is a provider/model id like "gemini/gemini-3.8-flash", or the name of a combo you made in its dashboard.
export const OMNI_KEY = process.env.OMNIROUTE_KEY || "";
export const OMNI_URL = (process.env.OMNIROUTE_URL || "http://localhost:20128/v1").replace(/\/$/, "");
export const OMNI_MODEL = process.env.OMNIROUTE_MODEL || "gemini/gemini-3.8-flash";

interface Req {
  system: string;
  user: string;
  maxTokens: number;
  json?: boolean;
  signal?: AbortSignal;
}

async function call(req: Req, stream: boolean) {
  let res: Response;
  try {
    res = await fetch(`${OMNI_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${OMNI_KEY}` },
      body: JSON.stringify({
        model: OMNI_MODEL,
        stream,
        max_tokens: req.maxTokens,
        messages: [
          { role: "system", content: req.system },
          { role: "user", content: req.user },
        ],
        ...(req.json ? { response_format: { type: "json_object" } } : {}),
      }),
      signal: req.signal,
    });
  } catch {
    throw new Error("เชื่อมต่อ OmniRoute ไม่ได้ — เปิดโปรแกรม `omniroute` ไว้หรือยัง?");
  }
  if (!res.ok) {
    const msg = ((await res.text().catch(() => "")) || "").slice(0, 200);
    if (res.status === 401) throw new Error("OmniRoute key ไม่ถูกต้อง — ตรวจ OMNIROUTE_KEY");
    throw new Error(`OmniRoute error ${res.status}: ${msg}`);
  }
  return res;
}

export async function omniStream(req: Req, onText: (t: string) => void) {
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
      if (!line.startsWith("data:") || line.includes("[DONE]")) continue;
      try {
        const d = JSON.parse(line.slice(5)) as { choices?: { delta?: { content?: string } }[]; error?: { message?: string } };
        if (d.error) throw new Error(d.error.message || "OmniRoute error");
        const t = d.choices?.[0]?.delta?.content;
        if (t) onText(t);
      } catch (e) {
        if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
      }
    }
  }
}

export async function omniComplete(req: Req): Promise<string> {
  const res = await call(req, false);
  const d = (await res.json()) as { choices?: { message?: { content?: string } }[] };
  return d.choices?.[0]?.message?.content ?? "";
}
