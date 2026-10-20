// The models a user can pick. Only those whose provider has a key on the server are offered.
import { GEMINI_KEY, GEMINI_MODEL } from "./gemini";
import { GROQ_KEY, OMNI_KEY, OMNI_MODEL, OPENROUTER_KEY } from "./omniroute";
import { OPENAI_KEY } from "./openai";

export type Provider = "claude" | "gemini" | "omniroute" | "openai" | "groq" | "openrouter";

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
  if (GROQ_KEY) {
    out.push(opt("groq", "openai/gpt-oss-120b", "Groq · GPT-OSS 120B", "ฟรี · เร็วมาก (โมเดลเปิดของ OpenAI)"));
    out.push(opt("groq", "qwen/qwen3.8-27b", "Groq · Qwen 3.8 27B", "ฟรี · เร็ว ภาษาไทยดี"));
  }
  if (OPENROUTER_KEY) {
    out.push(opt("openrouter", "nvidia/nemotron-3.5-lightning:free", "OpenRouter · Nemotron 3.5 Lightning", "ฟรี · เร็ว"));
    out.push(opt("openrouter", "nvidia/nemotron-3-ultra-550b-a55b:free", "OpenRouter · Nemotron 3 Ultra", "ฟรี · ใหญ่ ช้ากว่า"));
    out.push(opt("openrouter", "minimax/minimax-m3.1-flash:free", "OpenRouter · MiniMax M3.1 Flash", "ฟรี · จำกัดครั้งต่อวัน"));
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
