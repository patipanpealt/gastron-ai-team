# Style guide

Benchmark: Gen-4/5 handheld-RPG trainer chibis (HGSS/BW overworld style). Learn principles, never copy a character.

## Proportions
Big head (~45–50% of height), 3/4 top-down so the crown shows, compact body, short legs. Silhouette must read at 1x.

## Shading & colour
- 3–4 tones per material + outline; ~12–16 colours per sprite.
- **Hue-shift**: shadows cooler/more saturated (purple/blue), highlights warmer/paler; never just a darker copy. Mid-tone is the most saturated.
- Tone bands follow the form (round, not stepped). Whole masses darken toward the lower-right.
- **Outline**: dark outside; inner separations use the material's darkest tone (selective outline), not black. Outline colour constant `#2b2230`.
- Furniture ramps are 4-step `[highlight, base, shade, deep]` (see `scripts/kit.py`): lit top face bright, front faces much darker; a cream lip highlights edges facing the light; long sheared cast shadow to the right.

## Hair (the hero)
- Volume beyond the skull, built from distinct clumps/locks, each with its own ramp (lit at root/upper-left, dark on underside/tip).
- Glossy streaks: short curved 1–2 px highlights following each lock, upper third of locks facing the light, broken between locks, absent on the shadow side.
- 1–2 px shadow on the forehead under the bangs.
- Keep to everyday office styles: neat short, side part, short lifted front (a normal male cut with slight lift), short layered, low ponytail, hime cut.

## Faces / clothes
- Tall dark eyes with a catch-light, tiny mouth, shaded skin under hair/head.
- Garments: strong colour blocks, contrasting trim (collar, cuffs, tie, buttons). Darker on the right/lower side. Smooth upper-left→lower-right gradient on the torso block.
