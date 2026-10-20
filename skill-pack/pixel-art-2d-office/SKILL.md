---
name: pixel-art-2d-office
description: Design and build 2D pixel-art game assets in the Gastron "AI Office" style — native 16x32 chibi characters (animation sheets, hair, outfits, palette-swap dress-up), 3/4 top-down furniture on a 32px grid, and the Canvas/Next.js engine that runs them (room editor, partitions, doors, name plaques, pathing). Use when asked to draw, extend, recolour or integrate sprites/characters/furniture for this project or any office-style pixel-art scene.
---

# Pixel Art 2D — Gastron AI Office

A complete record of how the sprites and the office app were designed, so another AI can continue in the same style without re-deriving anything. Everything here was approved by the user; the **Rules** below are non-negotiable.

## Read first (pick what you need)
| Need | File |
|---|---|
| Colour, shading, outline rules | `references/style-guide.md` |
| Characters: body, animation, hair, outfits, recolouring | `references/character-kit.md` |
| Furniture / wall objects / floors, scale and anchors | `references/furniture-kit.md` |
| The app: engine, room layout, seats, partitions, doors, plaques | `references/app-integration.md` |
| What the user liked / rejected (history of corrections) | `references/user-preferences.md` |
| Working generator scripts (Python + PIL) | `scripts/` |

## Rules (hard-won)
1. **Characters are native 16x32 on the approved chibi body** (flat-topped wide head, no neck, stubby limbs). Never build on the rejected 32x64 body. Draw hair/outfits natively on the 16x32 grid; do not resample finished images.
2. **Show a front-view review image first** for any new design (hair, garment); the user replies with short corrections. Do not build full sheets before approval.
3. **Everyday office look**: tidy, ordinary hair and clothes — not flashy/anime. No shoes.
4. **Quality bar**: soft rounded gradients (never flat or blocky bands), selective outline, hue-shifted tones, glossy hair highlights (see style guide).
5. **The user wants systems, not generated images**: dress-up, naming, room decorating are things the user operates in the app. Never replace a requested feature with pre-rendered art.
6. Light always comes from the **upper-left**; outline colour `#2b2230` (never pure black); view is **3/4 top-down**, not isometric.
7. Furniture is drawn at 32px grid and shown at **OBJECT_SCALE = 1.5**; characters are shown at 2x (32x64 on screen). Do not change character scale when objects are rescaled.
8. Verify visually in the browser (zoom a region with a CSS transform on the canvas — screenshots are small). Test with a separate localStorage slot (`?slot=name`), never the user's real save.
9. The project lives on an external drive that creates `._*` AppleDouble files: delete them after writing (`find app lib components -name '._*' -delete`) and skip them in scripts.

## Workflow for a new asset
1. State the intent in one line; if a direction is ambiguous, ask once (AskUserQuestion) — otherwise proceed.
2. Draw it with a generator script in `pixel-art/sprites/` (one script per asset family; output PNGs + a preview image at 8x on the floor).
3. Show the preview; iterate with the user's short corrections (change only what they named).
4. When approved, add it to `export_assets.py` output (`public/assets/...`), register it in `lib/office/catalog.ts` (+ `furniture-meta.json` is generated), and test in the app.
5. Update memory/notes with the decision.

## Quick facts
- Tile 32 px; wall height 96 px (`WALL_H = 64 * 1.5`); room 18–40 × 12–30 tiles, default 32×21.
- Character cell 16x32, feet row 30; poses idle(2) walk(4) sit(1) talk(2) wave(2); views S N W (E = mirrored W).
- Layer order: hair_back → body → bottom → top → face → hair.
- Settings persist in `localStorage["gastron.office.v1"]` (room layout version `v: 3`).
