"""Copy the game-ready art into the Next.js app (public/assets) and write the palette file the app needs for
recolouring.

  public/assets/character/   layer sheets from sprites/character/sheets16 (body / face / hair / top / bottom),
                             character16.json (cell layout, timings), palettes.json (default colour ramps)
  public/assets/furniture/   every furniture / wall / floor sprite, flat file names (e.g. desk_front.png)

Run:  python3 export_assets.py   (from this folder)
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
SPR = HERE / "sprites"
OUT = HERE.parent / "public" / "assets"
sys.path.insert(0, str(SPR))

import outfit16  # noqa: E402  (default garment ramps)

SKIP = ("preview", "pairs", "closeup", "_v1")


def main():
    char_out = OUT / "character"
    furn_out = OUT / "furniture"
    for d in (char_out, furn_out):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)

    src = SPR / "character" / "sheets16"
    for f in sorted(src.glob("*.png")):
        if not f.name.startswith("._"):
            shutil.copy(f, char_out / f.name)
    shutil.copy(src / "character16.json", char_out / "character16.json")

    # default ramps: the colours the sheets were drawn with (the app swaps them for any chosen colour)
    import hair32_front as H0
    pal = {"hair": {"black": H0.COLORS["black"]}, "garments": outfit16.PAL}
    (char_out / "palettes.json").write_text(json.dumps(pal, indent=2))

    n = 0
    for f in sorted(SPR.glob("*/*.png")):
        rel = str(f.relative_to(SPR))
        if f.name.startswith("._") or any(s in rel for s in SKIP) or rel.startswith(("character", "_v1")):
            continue
        shutil.copy(f, furn_out / f.name)
        n += 1
    # sprite sizes + solid-body boxes (the soft shadow is excluded) so the app can align every sprite to the tile grid
    import numpy as np
    from PIL import Image
    meta = {}
    for f in sorted(furn_out.glob("*.png")):
        if f.name.startswith("._"):
            continue
        a = np.array(Image.open(f).convert("RGBA"))[..., 3]
        ys, xs = np.where(a >= 250)
        meta[f.stem] = {"w": int(a.shape[1]), "h": int(a.shape[0]),
                        "body": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}
    (HERE.parent / "lib" / "office" / "furniture-meta.json").write_text(json.dumps(meta, indent=1))
    for junk in OUT.rglob("._*"):   # the external drive litters AppleDouble files next to every copy
        junk.unlink()
    print("character layers:", len(list(char_out.glob('*.png'))), "| furniture sprites:", n)


if __name__ == "__main__":
    main()
