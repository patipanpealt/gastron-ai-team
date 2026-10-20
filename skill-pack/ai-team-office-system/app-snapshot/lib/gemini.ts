// Google Gemini over plain REST (no SDK): streamed text for the agents, JSON for the plan.
export const GEMINI_KEY = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || "";
export const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-3.8-flash";

const BASE = "https://generativelanguage.googleapis.com/v1beta/models";

interface GeminiReq {
  system: string;
  user: string;
  maxTokens: number;
  json?: boolean;
  signal?: AbortSignal;
}

function body({ system, user, maxTokens, json }: GeminiReq) {
  return JSON.stringify({
    systemInstruction: { parts: [{ text: system }] },
    contents: [{ role: "user", parts: [{ text: user }] }],
    generationConfig: { maxOutputTokens: maxTokens, ...(json ? { responseMimeType: "application/json" } : {}) },
  });
}

async function fail(res: Response): Promise<never> {
  let msg = "";
  try {
    msg = ((await res.json()) as { error?: { message?: string } }).error?.message ?? "";
  } catch {
    /* not JSON */
  }
  if (res.status === 429) throw new Error("Gemini: โควต้าฟรีของวันนี้หมดทุกโมเดล (429) — รอพรุ่งนี้ หรือเปิด billing ใน Google AI Studio");
  if (res.status === 400 && /api key/i.test(msg)) throw new Error("Gemini API key ไม่ถูกต้อง — ตรวจ GEMINI_API_KEY");
  throw new Error(`Gemini API error ${res.status}: ${msg.slice(0, 200)}`);
}

/** Each model has its own free daily quota, so when one runs out we move on to the next one. */
const MODELS = [...new Set([GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"])];
const exhausted = new Map<string, number>(); // model -> when to try it again

/** Per-minute limits: wait and retry. Per-day limits: switch model. */
async function post(method: "streamGenerateContent?alt=sse" | "generateContent", req: GeminiReq, json: boolean): Promise<Response> {
  const waits = [6000, 15000, 30000];
  let last: Response | null = null;
  for (const model of MODELS) {
    if ((exhausted.get(model) ?? 0) > Date.now()) continue;
    for (let i = 0; ; i++) {
      const res = await fetch(`${BASE}/${model}:${method}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY },
        body: body({ ...req, json }),
        signal: req.signal,
      });
      if (res.status !== 429) return res;
      const text = await res.clone().text();
      last = res;
      if (/PerDay/i.test(text)) {
        exhausted.set(model, Date.now() + 30 * 60 * 1000);
        break;
      }
      if (i >= waits.length) return res;
      await new Promise((r) => setTimeout(r, waits[i]));
    }
  }
  return last ?? new Response(JSON.stringify({ error: { message: "quota" } }), { status: 429 });
}

/** Stream the answer; `onText` gets each piece as it arrives. */
export async function geminiStream(req: GeminiReq, onText: (t: string) => void) {
  const res = await post("streamGenerateContent?alt=sse", req, false);
  if (!res.ok || !res.body) return fail(res);
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  let blocked = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let nl: number;
    while ((nl = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, nl).trim();
      buf = buf.slice(nl + 1);
      if (!line.startsWith("data:")) continue;
      const data = JSON.parse(line.slice(5)) as {
        candidates?: { content?: { parts?: { text?: string; thought?: boolean }[] }; finishReason?: string }[];
        promptFeedback?: { blockReason?: string };
      };
      if (data.promptFeedback?.blockReason) blocked = data.promptFeedback.blockReason;
      for (const p of data.candidates?.[0]?.content?.parts ?? []) if (p.text && !p.thought) onText(p.text);
    }
  }
  if (blocked) throw new Error(`Gemini ปฏิเสธคำขอนี้ (${blocked})`);
}

/** One JSON answer (used for the plan). */
export async function geminiJson(req: Omit<GeminiReq, "json">): Promise<string> {
  const res = await post("generateContent", req, true);
  if (!res.ok) return fail(res);
  const data = (await res.json()) as { candidates?: { content?: { parts?: { text?: string }[] } }[] };
  return (data.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
}

/** One plain-text answer (used to summarise a reference). */
export async function geminiComplete(req: Omit<GeminiReq, "json">): Promise<string> {
  const res = await post("generateContent", req, false);
  if (!res.ok) return fail(res);
  const data = (await res.json()) as { candidates?: { content?: { parts?: { text?: string }[] } }[] };
  return (data.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
}
