# The AI team

## Agents
director (Max), strategist, researcher, copywriter, content, creative, social, ads, seo, analyst, qa. User-given display names are sent as `names` and used in prompts. Persona + skills in `lib/agents.ts`; company facts in `lib/brand.ts` (edit there).

## Graphic Brief / Campaign (plan → tasks)
1. `/api/plan` returns `{summary, tasks[{id, agent, title, instructions, dependsOn}]}` (JSON schema for Claude; "JSON only + schema in prompt" for Gemini/OmniRoute). `sanitize()` drops unknown agents/forward deps and forces a final QA task.
2. Tasks run as dependencies finish, in parallel where possible; outputs of dependencies are passed as `inputs`.
3. Director compiles with `COMPILE_GRAPHIC` / `COMPILE_CAMPAIGN`.

## Facebook post (real conversation)
`FB_SCRIPT` in `lib/orchestrator.ts` = ordered turns with a goal each: director opens → strategist (objective, key message) → social (format, posting, mini-campaign) → copywriter (3 headers + every on-image line) → creative (layout, which line in which zone) → content (caption angle) → copywriter (captions + hashtags) → creative (confirm layout) → QA (2–3 fixes) → copywriter (apply fixes) → director (summary). Each turn sees the whole transcript; `CHAT_RULES` keep turns 2–5 conversational sentences that name colleagues. The user can type into the room (`Orchestrator.say`), included in the next turn. Then `COMPILE_FACEBOOK` writes the brief.

## Prompt rules that matter
- Copy Deck section: table `# | position | exact on-image text | relative size`, numbers match `layout` zones; layout JSON zones carry `"text"` with the exact words.
- `LAYOUT_SPEC`: ```layout``` JSON (ratio, background, zones with %, color, text) → rendered as a wireframe by `components/Markdown.tsx`.
- Never invent facts/numbers/certifications: use `[ใส่ข้อมูล]`. (Models still invent URLs/specs sometimes, so QA them.)
- Natural-writing rules (humanizer): no intros/recaps, no "ไม่ใช่แค่…แต่…", no hype words, no forced triads, no emoji headings, no long dashes.
- Memory (`สอนทีม`) is injected as "สิ่งที่หัวหน้าสอนทีมไว้ (ต้องทำตามเสมอ)".

## Demo mode
No provider key → `lib/demo.ts` scripted plan, chat lines and briefs, so the office can be shown without cost.
