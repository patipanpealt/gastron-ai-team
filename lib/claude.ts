import Anthropic from "@anthropic-ai/sdk";
import { GEMINI_KEY, GEMINI_MODEL } from "./gemini";

export const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";
export const EFFORT = (process.env.CLAUDE_EFFORT || "medium") as "low" | "medium" | "high";
export const USE_FALLBACKS = process.env.CLAUDE_FALLBACKS !== "off";

const HAS_CLAUDE = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);

/** Which AI answers: AI_PROVIDER=gemini|claude, otherwise whichever key is set (Claude wins if both). */
export const PROVIDER: "claude" | "gemini" =
  process.env.AI_PROVIDER === "gemini" ? "gemini" : process.env.AI_PROVIDER === "claude" ? "claude" : HAS_CLAUDE || !GEMINI_KEY ? "claude" : "gemini";

/** No key for the chosen provider → the office runs on scripted demo output. */
export const DEMO_MODE = PROVIDER === "gemini" ? !GEMINI_KEY : !HAS_CLAUDE;
export const ACTIVE_MODEL = PROVIDER === "gemini" ? GEMINI_MODEL : MODEL;

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
