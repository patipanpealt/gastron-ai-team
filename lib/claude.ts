import Anthropic from "@anthropic-ai/sdk";
import { availableModels, type ModelOption, type Provider } from "./models";

export type { Provider };

export const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";
export const EFFORT = (process.env.CLAUDE_EFFORT || "medium") as "low" | "medium" | "high";
export const USE_FALLBACKS = process.env.CLAUDE_FALLBACKS !== "off";

/** The model used when the user hasn't picked one: AI_PROVIDER forces a provider, otherwise the first key found
 *  in the order OmniRoute, Claude, OpenAI, Gemini. null = no key at all → scripted demo output. */
export const DEFAULT_MODEL: ModelOption | null = (() => {
  const all = availableModels();
  const forced = process.env.AI_PROVIDER as Provider | undefined;
  for (const p of forced ? [forced] : (["omniroute", "claude", "openai", "gemini"] as Provider[])) {
    const first = all.find((m) => m.provider === p);
    if (first) return all.find((m) => m.provider === p && (m.model === MODEL || p !== "claude")) ?? first;
  }
  return null;
})();

export const PROVIDER: Provider = DEFAULT_MODEL?.provider ?? "claude";
export const DEMO_MODE = !DEFAULT_MODEL;
export const ACTIVE_MODEL = DEFAULT_MODEL?.model ?? MODEL;

let client: Anthropic | null = null;
export function claude() {
  client ??= new Anthropic();
  return client;
}

export function errorMessage(err: unknown) {
  if (err instanceof Anthropic.AuthenticationError) return "API key ไม่ถูกต้อง (401) — ตรวจ ANTHROPIC_API_KEY";
  if (err instanceof Anthropic.RateLimitError) return "ใช้งานเกิน rate limit (429) — รอสักครู่แล้วลองใหม่";
  if (err instanceof Anthropic.APIError && err.status) return `Claude API error ${err.status}: ${err.message}`;
  if (err instanceof Anthropic.APIConnectionError) return "เชื่อมต่อ Claude API ไม่ได้";
  return err instanceof Error ? err.message : String(err);
}
