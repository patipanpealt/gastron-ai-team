# App integration (Next.js 16 + Canvas 2D)

Project: `AI Team/` (Next 16 Turbopack dev on :3300, React 19, strict TS). Run `npm run dev`; `rm -rf .next/cache/turbopack` before builds. Engine HMR does not patch a live `OfficeEngine` instance — reload the page after engine edits.

## Files
- `lib/office/catalog.ts` — item definitions (`ITEMS`), categories (work, furniture, decor, zone, wall), `OBJECT_SCALE`, `PARTITION_STYLES/COLORS`, `PLAQUE_STYLES/SIZES`, `proc: "partition" | "plaque" | "door"` for code-drawn items.
- `lib/office/room.ts` — all geometry: `footprint`, `stationGeo`, `seatOf`, `blockingCells`, `blockedGrid`, `floorOps`, `itemRect`, `canPlace`, `partitionGeo`, `wallSize`, `doorCell`, `withItemUpdated/Removed`, `defaultRoom`, `sanitizeRoom` (versioned: `v: 3`; v2 saves are migrated by swapping chair S/N).
- `lib/office/engine.ts` — `OfficeEngine`: actors, BFS pathing, seats, meetings (`gather` spreads people round the table), wandering, personal-space push (`keepApart`), pointer editing (place/drag/drop), door toggle, depth-sorted rendering.
- `lib/office/store.ts` — localStorage settings (`gastron.office.v1`, optional `:slot` via `?slot=name`).
- `lib/office/sprites.ts / palette.ts / appearance.ts` — asset loading, palette swap, appearance defaults.
- `components/RoomEditor.tsx`, `CharacterEditor.tsx`, `OfficeCanvas.tsx`, `app/page.tsx`.

## Rules baked into the engine
- Workstation = desk + chair composite; `stationGeo(rot)` where rot = direction the person faces. Seat feet (px, local): S `y 45` with chair_front dropped 14 px (`bottom 31*S+14`); N `y 102` with chair_back; E/W `y 46*S-12`. These were tuned so the person visibly sits on the chair (user complained twice that they looked seated on the floor).
- Chair cell is walkable; BFS is 4-connected on tiles. **If no route exists, an agent stays put — never a straight line through walls.**
- Partitions: `proc:"partition"`, horizontal (rot S) has a front face (84 px tall) that wall items can be hung on (`mount: <partition id>`); vertical is 14 px thick, no mount. Partition move/lengthen/shorten carries mounted children (drops those that no longer fit).
- Plaques: wall item with typed `text`, style (wood/brass/navy/green/red/white), size xs/s/m/l; text auto-fits.
- Doors: `proc:"door"`, `open` flag. On the back wall: sprite (closed) / doorway (open). In a partition: exactly one tile wide, 72 px tall, sitting on the floor; open = gap cut out of the partition (clip) and the cell becomes walkable, closed = blocks. Click to toggle when not editing; button in the room editor.
- Wall item picking: things mounted on a partition are hit-tested before the partition.
- Agents: custom names are sent to the API (`names` map) and used in prompts.

## Test recipe
Foreground a browser tab at `http://localhost:3300/?slot=qa`, inject layout into `localStorage["gastron.office.v1:qa"]`, reload, drive `window.__office` (dev only). Magnify with `canvas.style.transform = translate(...) scale(4)` and `pointerEvents='none'`. Node-test room logic by compiling `room.ts` with `tsc --module commonjs`.
