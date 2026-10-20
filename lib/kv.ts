// Shared team storage on Upstash Redis (REST API, no SDK). Vercel's Upstash integration sets KV_REST_API_*;
// a database made on upstash.com directly gives UPSTASH_REDIS_REST_*. Either works. Unset = per-browser only.
const URL_ = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || "";
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || "";

export const kvEnabled = () => !!(URL_ && TOKEN);

export async function kv<T = unknown>(...cmd: (string | number)[]): Promise<T> {
  const res = await fetch(URL_, {
    method: "POST",
    headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify(cmd.map(String)),
    cache: "no-store",
  });
  const data = (await res.json()) as { result?: T; error?: string };
  if (!res.ok || data.error) throw new Error(`Upstash: ${data.error || res.status}`);
  return data.result as T;
}
