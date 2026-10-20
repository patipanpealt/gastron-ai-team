# Gastron AI Office — skill pack

Two skills that together rebuild everything in this project:

| Skill | What it covers |
|---|---|
| `pixel-art-2d-office/` | 16x32 chibi characters (body, animations, hair, outfits, palette-swap dress-up), 3/4 top-down furniture, the canvas room engine (editor, partitions, doors, plaques, seating, pathing) |
| `ai-team-office-system/` | The product: 11 AI agents, plan→tasks briefs, the live Facebook-post meeting, providers (Claude/Gemini/OmniRoute), references, team memory, PDF, login, GitHub + Vercel deploy. Includes `app-snapshot/` (key source files, no secrets) |

## Install
- **Claude Code:** copy both folders into `~/.claude/skills/` (or `<project>/.claude/skills/`).
- **Other AI tools:** give the agent the `SKILL.md` of the skill you need first, then the files in its `references/`. Source code is in `ai-team-office-system/app-snapshot/` and the art generators in `pixel-art-2d-office/scripts/` (Python 3 + Pillow + numpy).

No API keys, passwords or password hashes are included. Create your own `.env.local` from `app-snapshot/.env.example`.
