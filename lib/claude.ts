import Anthropic from "@anthropic-ai/sdk";
import { GEMINI_KEY, GEMINI_MODEL } from "./gemini";
import { OMNI_KEY, OMNI_MODEL } from "./omniroute";

export const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";
export const EFFORT = (process.env.CLAUDE_EFFORT || "medium") as "low" | "medium" | "high";
export const USE_FALLBACKS = process.env.CLAUDE_FALLBACKS !== "off";

const HAS_CLAUDE = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);

/** Which AI answers: AI_PROVIDER=omniroute|gemini|claude, otherwise the first key found: OmniRoute, Claude, Gemini. */
export type Provider = "claude" | "gemini" | "omniroute";
const FORCED = process.env.AI_PROVIDER as Provider | undefined;
export const PROVIDER: Provider =
  FORCED === "omniroute" || FORCED === "gemini" || FORCED === "claude" ? FORCED : OMNI_KEY ? "omniroute" : HAS_CLAUDE ? "claude" : GEMINI_KEY ? "gemini" : "claude";

/** No key for the chosen provider → the office runs on scripted demo output. */
export const DEMO_MODE = PROVIDER === "omniroute" ? !OMNI_KEY : PROVIDER === "gemini" ? !GEMINI_KEY : !HAS_CLAUDE;
export const ACTIVE_MODEL = PROVIDER === "omniroute" ? OMNI_MODEL : PROVIDER === "gemini" ? GEMINI_MODEL : MODEL;

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
