# Architecture

```
app/page.tsx            office UI: canvas, brief panel, meeting chat, task board, feed, history, final modal + PDF
app/login/page.tsx      email + password login (logo /public/brand/gastron-logo.svg, "AI Marketing Creative Team")
app/api/plan            director plans tasks (JSON)            → Claude | Gemini | OmniRoute
app/api/agent           one agent turn, streamed as NDJSON     → modes: task | compile | chat
app/api/reference       read a URL + summarise it
app/api/login|logout|me session cookie
app/api/status          {demo, model, provider}
proxy.ts                gate: everything needs a session once AUTH_USERS is set
lib/orchestrator.ts     client-side conductor: kickoff/work/compile, Facebook discuss(), say(), history
lib/prompts.ts          OFFICE_RULES (incl. natural-writing rules), focus blocks, LAYOUT_SPEC, compile templates, chat rules
lib/agents.ts           11 agents: id, name, role, persona, skills
lib/brand.ts            company context every agent reads (cached system block)
lib/claude.ts           provider selection (PROVIDER, DEMO_MODE, ACTIVE_MODEL)
lib/gemini.ts           REST client, SSE stream, per-minute retry, per-day model fallback
lib/omniroute.ts        OpenAI-compatible client for a local OmniRoute
lib/ai.ts               completeText() for side jobs (summaries) on any provider
lib/reference.ts        safe URL reader (blocks private IPs, follows redirects manually, Google Docs export)
lib/references.ts       client Reference type + block appended to the brief
lib/memory.ts           "สอนทีม" store (localStorage) → memoryFor(agent) sent with each request
lib/pdf.ts              html2canvas-pro + jsPDF, section-aware A4 pagination
lib/auth.ts, lib/password.ts   signed session cookie (HMAC, Web Crypto) + scrypt hashes (node:crypto)
lib/uid.ts              randomUUID fallback for http:// on phones
lib/office/*            room engine (see pixel-art-2d-office skill)
components/*            Markdown (layout block → wireframe), editors, MemoryPanel/TeachBox, OfficeCanvas
```

Request flow (Facebook post): page → `Orchestrator.discuss()` → for each step in `FB_SCRIPT` POST `/api/agent` `{mode:"chat", transcript, turnGoal, memory, names}` → stream text into the speaker's bubble and the chat panel → `compileFacebook()` → `/api/agent {mode:"compile", kind:"facebook", transcript}` → final markdown → modal (+ PDF).
