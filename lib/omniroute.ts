// OpenAI-compatible chat providers: OmniRoute (local router), Groq and OpenRouter (free tiers).
// They all speak POST {base}/chat/completions with SSE streaming, so one client serves all three.
export const OMNI_KEY = process.env.OMNIROUTE_KEY || "";
export const OMNI_URL = (process.env.OMNIROUTE_URL || "http://localhost:20128/v1").replace(/\/$/, "");
export const OMNI_MODEL = process.env.OMNIROUTE_MODEL || "gemini/gemini-3.8-flash";
export const GROQ_KEY = process.env.GROQ_API_KEY || "";
export const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY || "";

export type CompatProvider = "omniroute" | "groq" | "openrouter";

interface Cfg {
  name: string;
  url: string;
  key: string;
  defaultModel: string;
  /** Not every OpenRouter model accepts response_format, so only send it where it is known to work. */
  jsonMode: boolean;
  headers?: Record<string, string>;
}

const CFG: Record<CompatProvider, Cfg> = {
  omniroute: { name: "OmniRoute", url: OMNI_URL, key: OMNI_KEY, defaultModel: OMNI_MODEL, jsonMode: true },
  groq: { name: "Groq", url: "https://api.groq.com/openai/v1", key: GROQ_KEY, defaultModel: "openai/gpt-oss-120b", jsonMode: true },
  openrouter: {
    name: "OpenRouter",
    url: "https://openrouter.ai/api/v1",
    key: OPENROUTER_KEY,
    defaultModel: "google/gemma-4-31b-it:free",
    jsonMode: false,
    headers: { "X-Title": "Gastron AI Office" },
  },
};

interface Req {
  model?: string;
  system: string;
  user: string;
  maxTokens: number;
  json?: boolean;
  signal?: AbortSignal;
}

async function call(p: CompatProvider, req: Req, stream: boolean) {
  const c = CFG[p];
  let res: Response;
  try {
    res = await fetch(`${c.url}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${c.key}`, ...c.headers },
      body: JSON.stringify({
        model: req.model || c.defaultModel,
        stream,
        max_tokens: req.maxTokens,
        messages: [
          { role: "system", content: req.system },
          { role: "user", content: req.user },
        ],
        ...(req.json && c.jsonMode ? { response_format: { type: "json_object" } } : {}),
      }),
      signal: req.signal,
    });
  } catch {
    throw new Error(p === "omniroute" ? "เชื่อมต่อ OmniRoute ไม่ได้ — เปิดโปรแกรม `omniroute` ไว้หรือยัง?" : `เชื่อมต่อ ${c.name} ไม่ได้`);
  }
  if (!res.ok) {
    const msg = ((await res.text().catch(() => "")) || "").slice(0, 200);
    if (res.status === 401) throw new Error(`${c.name} key ไม่ถูกต้อง`);
    if (res.status === 429) throw new Error(`${c.name}: โควต้าฟรีหมดชั่วคราว (429) — รอสักครู่ หรือเลือกโมเดลอื่น`);
    throw new Error(`${c.name} error ${res.status}: ${msg}`);
  }
  return res;
}

export async function compatStream(p: CompatProvider, req: Req, onText: (t: string) => void) {
  const res = await call(p, req, true);
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
        if (d.error) throw new Error(`${CFG[p].name}: ${d.error.message || "error"}`);
        const t = d.choices?.[0]?.delta?.content;
        if (t) onText(t);
      } catch (e) {
        if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
      }
    }
  }
}

export async function compatComplete(p: CompatProvider, req: Req): Promise<string> {
  const res = await call(p, req, false);
  const d = (await res.json()) as { choices?: { message?: { content?: string } }[] };
  return d.choices?.[0]?.message?.content ?? "";
}
