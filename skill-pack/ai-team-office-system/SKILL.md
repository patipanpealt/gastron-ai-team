---
name: ai-team-office-system
description: Build or extend the Gastron "AI Office" web app — a Next.js app where 11 AI marketing agents (pixel-art characters) plan, talk through and write Graphic Briefs, Facebook-post briefs and campaigns. Covers the agent orchestration and live meeting conversation, AI providers (Claude / Gemini / OmniRoute), reference links, team memory ("สอนทีม"), the PDF brief, email+password login, and GitHub + Vercel deployment. Use when building a multi-agent "AI team" product, adding a feature to this app, or deploying/operating it.
---

# AI Team Office — the system

Companion to the `pixel-art-2d-office` skill (art + room engine). This one is the product around it.

## Read first
| Need | File |
|---|---|
| Architecture, files, request flow | `references/architecture.md` |
| How the AI team works (plan → tasks, Facebook meeting, prompts) | `references/ai-team.md` |
| Providers, keys, free quotas, costs | `references/providers.md` |
| Features: references, memory, PDF, history | `references/features.md` |
| Login, secrets, GitHub, Vercel, ops gotchas | `references/deploy-and-security.md` |
| Writing + UI rules the user approved (humanizer, Hallmark) | `references/voice-and-design.md` |
| Source snapshot of the key files | `app-snapshot/` |

## Rules
1. The user wants **systems they operate** (forms, panels, editors), never one-off generated output.
2. Every brief must contain a **Copy Deck**: the exact words that go on the artwork, numbered to the layout zones. Briefs are short (designer reads in 2 minutes).
3. Secrets never go into git, chat replies or browser form fields typed by the agent. Keys live in `.env.local` (local) and Vercel env vars (set by the user). Passwords are stored only as scrypt hashes.
4. Free first: Gemini free tier (per-model daily quota) with automatic fallback to lighter models; Claude optional; OmniRoute optional.
5. Verify in the browser with a separate localStorage slot (`?slot=qa`) and never touch the user's real saved office.
6. Thai UI copy, friendly-professional, no emoji in headings, no AI-writing tells.
7. The project sits on an external drive: delete `._*` files after writes; if `next dev` dies with "Failed to open database … invalid digit", delete `.next` and restart.

## Quick facts
- Stack: Next.js 16 (Turbopack, port 3300), React 19, TypeScript strict, Canvas 2D engine, no DB (browser localStorage for settings, history, memory).
- Repo: github.com/patipanpealt/gastron-ai-team (public) → Vercel project `gastron-ai-team` (auto-deploy on push to `main`).
- Run kinds: `graphic` (Graphic Brief), `facebook` (meeting conversation), `campaign`.
