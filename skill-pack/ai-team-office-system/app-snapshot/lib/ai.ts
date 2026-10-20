// A single plain-text completion with the picked (or default) model, for small side jobs like summaries.
import { claude, DEFAULT_MODEL } from "./claude";
import { llmComplete } from "./llm";
import { resolveModel } from "./models";

export async function completeText(system: string, user: string, maxTokens = 1500, modelChoice?: string): Promise<string> {
  const m = resolveModel(modelChoice, DEFAULT_MODEL);
  if (!m) return "";
  if (m.provider !== "claude") return (await llmComplete(m, { system, user, maxTokens })).trim();
  const res = await claude().messages.create({ model: m.model, max_tokens: maxTokens, system, messages: [{ role: "user", content: user }] });
  return res.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("").trim();
}
