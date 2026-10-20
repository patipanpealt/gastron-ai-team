# Providers, keys, quotas

Selection (`lib/claude.ts`): `AI_PROVIDER=omniroute|gemini|claude` forces one; otherwise first key found in order OmniRoute → Claude → Gemini; no key → DEMO.

| Provider | Env | Notes |
|---|---|---|
| Gemini (REST, `lib/gemini.ts`) | `GEMINI_API_KEY`, `GEMINI_MODEL` (default `gemini-3.8-flash`; user uses `gemini-flash-latest`) | Free tier has a small **daily quota per model** (~1 Facebook run/day on flash). 429 "PerDay" → switch to `gemini-3.5-flash-lite` → `gemini-3.1-flash-lite` for 30 min; per-minute 429 → wait 6/15/30 s. Free-tier prompts may be used by Google: no confidential data. |
| Claude (`@anthropic-ai/sdk`) | `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `CLAUDE_EFFORT` | Streams thinking (bubbles show 💭). Prompt caching on the shared system block. Estimated cost per Facebook post (~12 calls, ~50k in / 16k out): Opus 5.5 ≈ $0.50, Sonnet 5.5 ≈ $0.26, Haiku 5.5 ≈ $0.013 (2026-10 prices; re-check). |
| OmniRoute (local router) | `OMNIROUTE_KEY`, `OMNIROUTE_MODEL` (provider/model or a combo name), `OMNIROUTE_URL` (default `http://localhost:20128/v1`) | `npm i -g --allow-scripts=omniroute,keytar,onnxruntime-node,@parcel/watcher,@swc/core,protobufjs,esbuild omniroute`, run `omniroute`, dashboard → Providers / API Keys / Combos. Bind to loopback (`OMNIROUTE_SERVER_HOST=127.0.0.1`). Not usable from Vercel. |

Model ids change: list them with the provider (`GET /v1beta/models` for Gemini) instead of guessing.
