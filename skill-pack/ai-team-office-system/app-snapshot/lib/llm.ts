// One place that talks to the non-Claude providers (Claude keeps its own calls: thinking + JSON schema).
import { geminiComplete, geminiJson, geminiStream } from "./gemini";
import type { ModelOption } from "./models";
import { compatComplete, compatStream } from "./omniroute";
import { openaiComplete, openaiStream } from "./openai";

interface Req {
  system: string;
  user: string;
  maxTokens: number;
  json?: boolean;
  signal?: AbortSignal;
}

export function llmStream(m: ModelOption, req: Req, onText: (t: string) => void) {
  const r = { ...req, model: m.model };
  if (m.provider === "gemini") return geminiStream(r, onText);
  if (m.provider === "openai") return openaiStream(r, onText);
  if (m.provider === "claude") throw new Error("Claude is called directly");
  return compatStream(m.provider, r, onText);
}

export async function llmComplete(m: ModelOption, req: Req): Promise<string> {
  const r = { ...req, model: m.model };
  if (m.provider === "gemini") return req.json ? geminiJson(r) : geminiComplete(r);
  if (m.provider === "openai") return openaiComplete(r);
  if (m.provider === "claude") throw new Error("Claude is called directly");
  return compatComplete(m.provider, r);
}
