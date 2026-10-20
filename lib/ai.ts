// A single plain-text completion, whichever AI provider is configured (used for small side jobs like summaries).
import { claude, DEMO_MODE, MODEL, PROVIDER } from "./claude";
import { geminiComplete } from "./gemini";

export async function completeText(system: string, user: string, maxTokens = 1500): Promise<string> {
  if (DEMO_MODE) return "";
  if (PROVIDER === "gemini") return (await geminiComplete({ system, user, maxTokens })).trim();
  const res = await claude().messages.create({ model: MODEL, max_tokens: maxTokens, system, messages: [{ role: "user", content: user }] });
  return res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("").trim();
}
