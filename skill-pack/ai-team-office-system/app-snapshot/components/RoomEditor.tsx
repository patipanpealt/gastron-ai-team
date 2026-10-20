"use client";

import { useEffect, useMemo, useState } from "react";
import { AGENTS } from "@/lib/agents";
import {
  type Category,
  CATEGORY_LABEL,
  FLOORS,
  type FloorId,
  ITEM_BY_TYPE,
  ITEMS,
  PARTITION_COLORS,
  PARTITION_STYLES,
  PLAQUE_SIZES,
  PLAQUE_STYLES,
  SURFACE_TINTS,
} from "@/lib/office/catalog";
import type { EditState } from "@/lib/office/engine";
import {
  canPlace,
  defaultRoom,
  defOf,
  MAX_COLS,
  MAX_ROWS,
  MIN_COLS,
  MIN_ROWS,
  newId,
  nextRot,
  type PlacedItem,
  type RoomLayout,
  sanitizeRoom,
  withItemRemoved,
  withItemUpdated,
} from "@/lib/office/room";
import { office, useOffice } from "@/lib/office/store";

const CATS: Category[] = ["work", "furniture", "decor", "zone", "wall"];
const RUG_COLORS = ["#8c3b4a", "#2f8a84", "#5b6f8a", "#c2873a", "#6a4fa0", "#3f7a3a", "#b5503c", "#44485a"];

/** Fields a freshly picked catalog item starts with (the ones you can adjust before dropping it). */
function startProps(type: string): Partial<PlacedItem> {
  const def = ITEM_BY_TYPE[type];
  if (def.proc === "partition") return { len: 4, style: "solid", color: PARTITION_COLORS[0] };
  if (def.proc === "plaque") return { text: "ชื่อทีม", style: "wood", size: "s" };
  return {};
}

export function RoomEditor({ edit, setEdit, onDone }: { edit: EditState; setEdit: (patch: Partial<EditState>) => void; onDone: () => void }) {
  const { room, profiles } = useOffice();
  const [cat, setCat] = useState<Category>("work");
  const [note, setNote] = useState<string | null>(null);
  const selected = useMemo(() => room.items.find((i) => i.id === edit.selectedId) ?? null, [room, edit.selectedId]);

  const flash = (msg: string) => {
    setNote(msg);
    setTimeout(() => setNote((m) => (m === msg ? null : m)), 2600);
  };

  /** Change one item. A partition takes what is hung on it along; what no longer fits is taken off. */
  const update = (next: PlacedItem) => {
    const check = canPlace(room, next);
    if (!check.ok) return flash(`ทำไม่ได้: ${check.reason}`);
    const { room: r, dropped } = withItemUpdated(room, next);
    office.setRoom(r);
    if (dropped) flash(`ของที่แปะบนแผ่นนี้ ${dropped} ชิ้นวางไม่พอดี จึงถูกเอาออก`);
  };

  const rotate = () => {
    if (edit.placing) {
      const def = ITEM_BY_TYPE[edit.placing.type];
      setEdit({ placing: { ...edit.placing, rot: nextRot(def, edit.placing.rot) } });
    } else if (selected) {
      update({ ...selected, rot: nextRot(defOf(selected), selected.rot) });
    }
  };
  const remove = () => {
    if (!selected) return;
    office.setRoom(withItemRemoved(room, selected.id));
    setEdit({ selectedId: null });
  };
  const duplicate = () => {
    if (!selected) return;
    const def = defOf(selected);
    for (let d = 1; d < 8; d++) {
      const copy: PlacedItem = {
        ...selected,
        id: newId(),
        agent: undefined,
        col: selected.col + d,
        row: selected.row,
        x: def.kind === "wall" ? (selected.x ?? 0) + 20 * d : selected.x,
      };
      if (canPlace(room, copy).ok) {
        office.setRoom({ ...room, items: [...room.items, copy] });
        setEdit({ selectedId: copy.id });
        return;
      }
    }
    flash("ไม่มีที่ว่างข้างๆ สำหรับทำสำเนา");
  };

  // keyboard shortcuts while the editor is open
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "INPUT" || t.tagName === "SELECT" || t.tagName === "TEXTAREA")) return;
      if (e.key === "r" || e.key === "R") rotate();
      else if (e.key === "Delete" || e.key === "Backspace") remove();
      else if (e.key === "Escape") {
        if (edit.placing) setEdit({ placing: null });
        else if (edit.selectedId) setEdit({ selectedId: null });
        else onDone();
      } else if ((e.key === "d" || e.key === "D") && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        duplicate();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const assign = (agent: string) => {
    if (!selected) return;
    const id = agent || undefined;
    office.setRoom({
      ...room,
      items: room.items.map((i) => {
        if (i.id === selected.id) return { ...i, agent: id as PlacedItem["agent"] };
        if (id && i.agent === id) return { ...i, agent: undefined }; // an agent has only one seat
        return i;
      }),
    });
  };

  const setSize = (cols: number, rows: number) => {
    const next = sanitizeRoom({ ...room, cols, rows });
    if (next.items.length < room.items.length && !confirm(`ห้องเล็กลง ของ ${room.items.length - next.items.length} ชิ้นจะหลุดออกนอกห้อง ต้องการต่อไหม?`)) return;
    office.setRoom(next);
  };

  const set = (patch: Partial<RoomLayout>) => office.setRoom({ ...room, ...patch });
  const placingDef = edit.placing ? ITEM_BY_TYPE[edit.placing.type] : null;
  const def = selected ? defOf(selected) : null;
  const hungCount = selected && def?.proc === "partition" ? room.items.filter((i) => i.mount === selected.id).length : 0;

  /** Controls for the properties of a partition or plaque, used both for the item being placed and the selected one. */
  const props = (cur: Partial<PlacedItem> & { type: string }, change: (patch: Partial<PlacedItem>) => void) => {
    const d = ITEM_BY_TYPE[cur.type];
    if (d.proc === "partition") {
      return (
        <>
          <div className="field">
            <span>ความยาว {cur.len ?? 4} ช่อง</span>
            <div className="size-row">
              <button className="btn" onClick={() => change({ len: Math.max(1, (cur.len ?? 4) - 1) })} disabled={(cur.len ?? 4) <= 1}>
                − สั้นลง
              </button>
              <button className="btn" onClick={() => change({ len: Math.min(16, (cur.len ?? 4) + 1) })} disabled={(cur.len ?? 4) >= 16}>
                ยาวขึ้น +
              </button>
            </div>
          </div>
          <div className="field">
            <span>แบบ</span>
            <div className="seg seg-small">
              {PARTITION_STYLES.map((s) => (
                <button key={s.id} className={(cur.style ?? "solid") === s.id ? "on" : ""} onClick={() => change({ style: s.id })}>
                  {s.name}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>สีแผ่น</span>
            <div className="swatches">
              {PARTITION_COLORS.map((c) => (
                <button key={c} className={`swatch-btn ${cur.color === c ? "on" : ""}`} style={{ background: c }} onClick={() => change({ color: c })} aria-label={c} />
              ))}
              <label className="swatch-btn swatch-custom" title="เลือกสีเอง">
                <input type="color" value={cur.color ?? PARTITION_COLORS[0]} onChange={(e) => change({ color: e.target.value })} />＋
              </label>
            </div>
          </div>
        </>
      );
    }
    if (d.proc === "door" && cur.id) {
      return (
        <div className="field">
          <span>ประตู: {cur.open ? "เปิดอยู่ (เดินผ่านได้)" : "ปิดอยู่ (เดินผ่านไม่ได้)"}</span>
          <button className="btn" onClick={() => change({ open: !cur.open })}>
            {cur.open ? "🚪 ปิดประตู" : "🚪 เปิดประตู"}
          </button>
          <span className="muted small">ตอนไม่ได้แต่งห้อง คลิกที่ประตูในห้องเพื่อเปิด/ปิดได้เลย</span>
        </div>
      );
    }
    if (d.proc === "plaque") {
      return (
        <>
          <label className="field">
            <span>ข้อความบนป้าย</span>
            <input className="text-in" value={cur.text ?? ""} maxLength={40} placeholder="พิมพ์ชื่อทีม…" onChange={(e) => change({ text: e.target.value })} />
          </label>
          <div className="field">
            <span>สีป้าย</span>
            <div className="swatches">
              {PLAQUE_STYLES.map((s) => (
                <button key={s.id} className={`swatch-btn ${(cur.style ?? "wood") === s.id ? "on" : ""}`} style={{ background: s.fill }} title={s.name} aria-label={s.name} onClick={() => change({ style: s.id })} />
              ))}
            </div>
          </div>
          <div className="field">
            <span>ขนาดป้าย</span>
            <div className="seg seg-small">
              {PLAQUE_SIZES.map((s) => (
                <button key={s.id} className={(cur.size ?? "s") === s.id ? "on" : ""} onClick={() => change({ size: s.id })}>
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        </>
      );
    }
    return null;
  };

  return (
    <div className="wood room-editor" role="region" aria-label="แต่งห้อง">
      <div className="room-head">
        <h2>แต่งห้อง</h2>
        <p className="muted small">
          เลือกของจากรายการ แล้วคลิกในห้องเพื่อวาง · คลิกของในห้องเพื่อเลือก ลากเพื่อย้าย · <kbd>R</kbd> หมุน · <kbd>Delete</kbd> ลบ · <kbd>Esc</kbd> ยกเลิก · กด Shift ค้างตอนวางเพื่อวางต่อเนื่อง · ของติดผนัง/ป้าย/ประตูลากไปวางบนหน้าแผ่น partition แนวนอนได้
        </p>
        <button className="btn btn-green" onClick={onDone}>
          ✓ เสร็จแล้ว
        </button>
      </div>
      {note && <p className="err room-note">⚠️ {note}</p>}

      <div className="room-cols">
        <div className="room-col room-catalog">
          <div className="seg seg-small" role="tablist">
            {CATS.map((c) => (
              <button key={c} role="tab" aria-selected={cat === c} className={cat === c ? "on" : ""} onClick={() => setCat(c)}>
                {CATEGORY_LABEL[c]}
              </button>
            ))}
          </div>
          <div className="catalog">
            {ITEMS.filter((i) => i.cat === cat).map((i) => (
              <button
                key={i.type}
                className={`cat-item ${edit.placing?.type === i.type ? "on" : ""}`}
                onClick={() =>
                  setEdit({
                    placing:
                      edit.placing?.type === i.type
                        ? null
                        : { type: i.type, rot: i.rots[0], color: i.tint && !i.proc ? RUG_COLORS[0] : undefined, props: startProps(i.type) },
                    selectedId: null,
                  })
                }
                title={i.name}
              >
                <span className="cat-icon">{i.icon}</span>
                <span>{i.name}</span>
              </button>
            ))}
          </div>
          {placingDef && edit.placing && (
            <div className="placing-bar">
              <div className="placing-row">
                กำลังวาง: <b>{placingDef.name}</b>
                <button className="btn" onClick={rotate} disabled={placingDef.rots.length < 2}>
                  ↻ หมุน
                </button>
                {placingDef.tint && !placingDef.proc && (
                  <span className="swatches">
                    {RUG_COLORS.map((c) => (
                      <button key={c} className={`swatch-btn ${edit.placing!.color === c ? "on" : ""}`} style={{ background: c }} onClick={() => setEdit({ placing: { ...edit.placing!, color: c } })} aria-label={c} />
                    ))}
                  </span>
                )}
                <button className="btn" onClick={() => setEdit({ placing: null })}>
                  ยกเลิก
                </button>
              </div>
              {placingDef.proc && (
                <div className="placing-props">
                  {props({ type: edit.placing.type, ...edit.placing.props, color: edit.placing.props?.color }, (patch) =>
                    setEdit({ placing: { ...edit.placing!, props: { ...edit.placing!.props, ...patch } } }),
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="room-col room-inspector">
          <h3>ของที่เลือก</h3>
          {!selected && <p className="muted small">ยังไม่ได้เลือกอะไร — คลิกของในห้องเพื่อเลือก</p>}
          {selected && def && (
            <>
              <p className="sel-name">
                {def.icon} {def.name}
                {selected.mount && <small className="muted"> · แปะบน partition</small>}
              </p>
              <div className="row-btns">
                <button className="btn" onClick={rotate} disabled={def.rots.length < 2}>
                  ↻ หมุน
                </button>
                <button className="btn" onClick={duplicate}>
                  ⧉ ทำสำเนา
                </button>
                <button className="btn btn-red" onClick={remove}>
                  🗑 ลบ
                </button>
              </div>
              {def.proc && props({ ...selected }, (patch) => update({ ...selected, ...patch }))}
              {hungCount > 0 && <p className="hint">มีของแปะอยู่บนแผ่นนี้ {hungCount} ชิ้น ย้าย/ยืดแผ่นแล้วของจะตามไปด้วย (ถ้าลบแผ่น ของที่แปะจะถูกลบด้วย)</p>}
              {def.workstation && (
                <label className="field">
                  <span>ที่นั่งของ</span>
                  <select value={selected.agent ?? ""} onChange={(e) => assign(e.target.value)}>
                    <option value="">— ว่าง —</option>
                    {AGENTS.map((a) => (
                      <option key={a.id} value={a.id}>
                        {profiles[a.id].name} ({a.role})
                      </option>
                    ))}
                  </select>
                </label>
              )}
              {def.tint && !def.proc && (
                <div className="field">
                  <span>สีพรม</span>
                  <div className="swatches">
                    {RUG_COLORS.map((c) => (
                      <button key={c} className={`swatch-btn ${selected.color === c ? "on" : ""}`} style={{ background: c }} onClick={() => update({ ...selected, color: c })} aria-label={c} />
                    ))}
                    <label className="swatch-btn swatch-custom" title="เลือกสีเอง">
                      <input type="color" value={selected.color ?? "#8c3b4a"} onChange={(e) => update({ ...selected, color: e.target.value })} />＋
                    </label>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="room-col room-settings">
          <h3>พื้น &amp; ผนัง</h3>
          <div className="field">
            <span>ลายพื้น</span>
            <div className="seg seg-small seg-wrap">
              {FLOORS.map((f) => (
                <button key={f.id} className={room.floor === f.id ? "on" : ""} onClick={() => set({ floor: f.id as FloorId })}>
                  {f.name}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>สีพื้น</span>
            <div className="swatches">
              {SURFACE_TINTS.map((t) => (
                <button key={t.id} className={`swatch-btn ${room.floorTint === t.hex ? "on" : ""} ${t.hex ? "" : "swatch-default"}`} style={t.hex ? { background: t.hex } : undefined} title={t.name} onClick={() => set({ floorTint: t.hex })}>
                  {t.hex ? "" : "↺"}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>สีผนัง</span>
            <div className="swatches">
              {SURFACE_TINTS.map((t) => (
                <button key={t.id} className={`swatch-btn ${room.wallTint === t.hex ? "on" : ""} ${t.hex ? "" : "swatch-default"}`} style={t.hex ? { background: t.hex } : undefined} title={t.name} onClick={() => set({ wallTint: t.hex })}>
                  {t.hex ? "" : "↺"}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>
              ขนาดห้อง {room.cols}×{room.rows} ช่อง
            </span>
            <div className="size-row">
              <button className="btn" onClick={() => setSize(room.cols - 1, room.rows)} disabled={room.cols <= MIN_COLS}>
                ◀ แคบลง
              </button>
              <button className="btn" onClick={() => setSize(room.cols + 1, room.rows)} disabled={room.cols >= MAX_COLS}>
                กว้างขึ้น ▶
              </button>
              <button className="btn" onClick={() => setSize(room.cols, room.rows - 1)} disabled={room.rows <= MIN_ROWS}>
                ▲ เตี้ยลง
              </button>
              <button className="btn" onClick={() => setSize(room.cols, room.rows + 1)} disabled={room.rows >= MAX_ROWS}>
                สูงขึ้น ▼
              </button>
            </div>
          </div>
          <div className="row-btns">
            <button
              className="btn"
              onClick={() => {
                if (confirm("เอาของทั้งหมดออกจากห้อง (เหลือแต่พื้นและผนัง)?")) {
                  office.setRoom({ ...room, items: [] });
                  setEdit({ selectedId: null });
                }
              }}
            >
              🧹 เคลียร์ห้อง
            </button>
            <button
              className="btn"
              onClick={() => {
                if (confirm("คืนห้องเป็นแบบเริ่มต้น?")) {
                  office.setRoom(defaultRoom());
                  setEdit({ selectedId: null });
                }
              }}
            >
              ↺ คืนห้องเริ่มต้น
            </button>
          </div>
          <p className="hint">อย่าลืมวาง “โต๊ะทำงาน + เก้าอี้” แล้วเลือกว่าเป็นที่นั่งของใคร — คนที่ไม่มีที่นั่งจะยืนรอกลางห้อง</p>
        </div>
      </div>
    </div>
  );
}
