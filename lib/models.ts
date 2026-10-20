// The models a user can pick. Only those whose provider has a key on the server are offered.
import { GEMINI_KEY, GEMINI_MODEL } from "./gemini";
import { OMNI_KEY, OMNI_MODEL } from "./omniroute";
import { OPENAI_KEY } from "./openai";

export type Provider = "claude" | "gemini" | "omniroute" | "openai";

export interface ModelOption {
  /** "provider:model" — what the browser sends back. */
  id: string;
  provider: Provider;
  model: string;
  label: string;
  /** Short Thai note shown next to the name. */
  note: string;
}

const HAS_CLAUDE = () => !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);

const opt = (provider: Provider, model: string, label: string, note: string): ModelOption => ({ id: `${provider}:${model}`, provider, model, label, note });

export function availableModels(): ModelOption[] {
  const out: ModelOption[] = [];
  if (GEMINI_KEY) {
    out.push(opt("gemini", GEMINI_MODEL, "Gemini Flash", "ฟรี · ค่าเริ่มต้น"));
    out.push(opt("gemini", "gemini-3.5-flash-lite", "Gemini Flash-Lite", "ฟรี · เร็ว โควต้าเยอะกว่า"));
    out.push(opt("gemini", "gemini-2.5-pro", "Gemini 2.5 Pro", "ฟรี · คิดลึก โควต้าน้อย"));
  }
  if (OPENAI_KEY) {
    out.push(opt("openai", "gpt-6.1-sol", "ChatGPT · GPT-6.1 Sol", "เสียเงิน · สมดุล"));
    out.push(opt("openai", "gpt-6-luna", "ChatGPT · GPT-6 Luna", "เสียเงิน · ถูกสุด"));
    out.push(opt("openai", "gpt-6-astra", "ChatGPT · GPT-6 Astra", "เสียเงิน · เก่งสุด แพง"));
  }
  if (HAS_CLAUDE()) {
    out.push(opt("claude", "claude-sonnet-5-5", "Claude Sonnet 5.5", "เสียเงิน · สมดุล"));
    out.push(opt("claude", "claude-haiku-5-5", "Claude Haiku 5.5", "เสียเงิน · ถูกและเร็ว"));
    out.push(opt("claude", "claude-opus-5-5", "Claude Opus 5.5", "เสียเงิน · เก่งสุด"));
  }
  if (OMNI_KEY) out.push(opt("omniroute", OMNI_MODEL, `OmniRoute · ${OMNI_MODEL}`, "ผ่านเครื่องนี้เท่านั้น"));
  return out;
}

/** The pick the browser sent, if the server can serve it; otherwise the default (or null = demo). */
export function resolveModel(id: unknown, fallback: ModelOption | null): ModelOption | null {
  return availableModels().find((m) => m.id === id) ?? fallback;
}
