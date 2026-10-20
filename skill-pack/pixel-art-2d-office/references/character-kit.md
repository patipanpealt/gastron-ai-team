# Character kit (native 16x32)

## Body
`scripts/character16_anim.py` assembles the approved chibi per frame from labelled parts (legs, torso, hands, head), outline added automatically around the union silhouette; hands/legs overlapping the body are stamped with their own outline ring. `Frame.lab` holds per-pixel part labels used by outfits.

Animations (views S front, N back, W left, E = W mirrored): idle 2 frames (breathing, head+torso sink 1 px), walk 4 (step L · pass · step R · pass, body rises 1 px on lifted-leg frames), sit 1 still frame (no hand/feet movement — user request), talk 2, wave 2. Sheets: 20 rows (anim × dir) × 4 columns of 16x32 cells; per-frame head/body offsets are in `body16_anim.json` so hair/outfit layers follow the bob. Four skin tones: light, medium, tan, deep.

## Hair
Six styles × front + back layers (`hair_<style>.png`, `hair_<style>_back.png`; styles: neat, side part, lifted, layered, ponytail, hime). Designed in a 32x64 "design space" with a 3D hair rig (`hair32_rig.py`: a Shell ellipsoid with a hairline + 3D Lock curves; back/side views come from projecting the same description). `canvas16.py` re-points the rasteriser at design-space coordinates of the 16x32 canvas so each 16x32 pixel is evaluated natively (4x4 supersampling, per-pixel light/banding/outline). **Import canvas16 first, in its own process.**

## Outfits
`outfit16.py` paints garments from the body's part labels so they fit every pose. Torso block = 5 rows (0–3 garment neckline→hem, 4 waist). Template symbols: `.` nothing, `0-4` tone of main palette, letters for secondary palette (w, x, b button, r red tie, R red shade, d deep navy). Tops: tee, shirt, suit (red tie), dress, tank. Bottoms: slacks, jeans, shorts, pencil skirt, pleated skirt. Palettes are 6 tones (highlight, light, base, shade, deep, outline), hue-shifted.

## Build & export
`build16.py` → `character/sheets16/` (one transparent sheet per layer + `character16.json` + previews). `export_assets.py` copies to `public/assets/character` and writes `palettes.json` (default ramps).

## Dress-up in the browser
Palette swap, no extra art: `makeRamp(hex)` builds a ramp from a chosen colour and `remapColors` swaps the default ramp colours of a layer (`lib/office/palette.ts`). Garment ramps 6 tones, hair ramps 8 tones. Appearance options: 6 hair styles, 5 tops, 5 bottoms, 4 skins + colours (`lib/office/appearance.ts`). Draw order: hair back → body → bottom → top → face → hair.

## Seating
Characters are drawn at 2x with feet at row 30. A seated agent is drawn inside the workstation draw sequence (chair → person → desk for S/E/W; desk → person → chair for N).
