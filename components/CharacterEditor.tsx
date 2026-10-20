"use client";

import { useEffect, useRef, useState } from "react";
import { AGENT_BY_ID, AGENTS, type AgentId, TEAM_LABEL } from "@/lib/agents";
import {
  type Appearance,
  BOTTOMS,
  type BottomId,
  HAIR_STYLES,
  type HairStyleId,
  randomAppearance,
  SKINS,
  TOPS,
  type TopId,
} from "@/lib/office/appearance";
import { GARMENT_COLORS, HAIR_COLORS } from "@/lib/office/palette";
import { type Anim, animInfo, CELL_H, CELL_W, characterFrame, type Dir, useAssetsVersion } from "@/lib/office/sprites";
import { MAX_NAME, office, useOffice } from "@/lib/office/store";

/** A (possibly animated) character drawn from the sprite layers. `crop` = [sx, sy, sw, sh] in the 16x32 cell. */
function CharCanvas({ ap, anim = "idle", dir = "S", scale, crop, className }: { ap: Appearance; anim?: Anim; dir?: Dir; scale: number; crop?: [number, number, number, number]; className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const ver = useAssetsVersion();
  const [sx, sy, sw, sh] = crop ?? [0, 0, CELL_W, CELL_H];
  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d")!;
    let raf = 0;
    const t0 = performance.now();
    const draw = (t: number) => {
      const info = animInfo(anim);
      const idx = info && info.frames > 1 ? Math.floor(Math.max(0, t - t0) / info.msPerFrame) % info.frames : 0;
      const f = characterFrame(ap, anim, dir, idx);
      ctx.clearRect(0, 0, c.width, c.height);
      ctx.imageSmoothingEnabled = false;
      if (f) ctx.drawImage(f, sx, sy, sw, sh, 0, 0, sw * scale, sh * scale);
      if (info && info.frames > 1) raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [ap, anim, dir, scale, sx, sy, sw, sh, ver]);
  return <canvas ref={ref} className={className} width={sw * scale} height={sh * scale} style={{ imageRendering: "pixelated" }} />;
}

function Swatches({
  colors,
  value,
  onPick,
  defaultLabel,
  disabled,
}: {
  colors: { id: string; name: string; hex: string }[];
  value: string | null;
  onPick: (hex: string | null) => void;
  defaultLabel: string;
  disabled?: boolean;
}) {
  const custom = value && !colors.some((c) => c.hex.toLowerCase() === value.toLowerCase()) ? value : null;
  return (
    <div className="swatches">
      <button className={`swatch-btn swatch-default ${value === null ? "on" : ""}`} title={defaultLabel} onClick={() => onPick(null)} disabled={disabled}>
        ↺
      </button>
      {colors.map((c) => (
        <button
          key={c.id}
          className={`swatch-btn ${value?.toLowerCase() === c.hex.toLowerCase() ? "on" : ""}`}
          style={{ background: c.hex }}
          title={c.name}
          aria-label={c.name}
          onClick={() => onPick(c.hex)}
          disabled={disabled}
        />
      ))}
      <label className={`swatch-btn swatch-custom ${custom ? "on" : ""}`} title="เลือกสีเอง" style={custom ? { background: custom } : undefined}>
        <input type="color" value={value ?? "#888888"} onChange={(e) => onPick(e.target.value)} disabled={disabled} />
        {!custom && "＋"}
      </label>
    </div>
  );
}

function OptionGrid<T extends string>({
  options,
  value,
  onPick,
  render,
  disabled,
}: {
  options: { id: T; name: string }[];
  value: T | "none";
  onPick: (id: T) => void;
  render: (id: T) => React.ReactNode;
  disabled?: boolean;
}) {
  return (
    <div className="opt-grid">
      {options.map((o) => (
        <button key={o.id} className={`opt ${value === o.id ? "on" : ""}`} onClick={() => onPick(o.id)} title={o.name} disabled={disabled}>
          <span className="opt-art">{render(o.id)}</span>
          <span className="opt-name">{o.name}</span>
        </button>
      ))}
    </div>
  );
}

const ANIMS: { id: Anim; name: string }[] = [
  { id: "idle", name: "ยืน" },
  { id: "walk", name: "เดิน" },
  { id: "talk", name: "พูด" },
  { id: "wave", name: "โบกมือ" },
  { id: "sit", name: "นั่ง" },
];
const DIRS: { id: Dir; name: string }[] = [
  { id: "S", name: "หน้า" },
  { id: "E", name: "ขวา" },
  { id: "N", name: "หลัง" },
  { id: "W", name: "ซ้าย" },
];

export function CharacterEditor({ initial, onClose }: { initial: AgentId; onClose: () => void }) {
  const { profiles } = useOffice();
  const [id, setId] = useState<AgentId>(initial);
  const [anim, setAnim] = useState<Anim>("idle");
  const [dir, setDir] = useState<Dir>("S");
  const agent = AGENT_BY_ID[id];
  const profile = profiles[id];
  const ap = profile.appearance;
  const set = (patch: Partial<Appearance>) => office.setAppearance(id, patch);
  const dress = ap.top === "dress";

  // the name box edits freely and saves as you type
  const [draft, setDraft] = useState(profile.name);
  useEffect(() => setDraft(profiles[id].name), [id, profiles]);

  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal editor" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="แต่งตัวและตั้งชื่อตัวละคร">
        <div className="drawer-head">
          <div>
            <h2>🧑‍🎨 แต่งตัว &amp; ตั้งชื่อ</h2>
            <p className="muted small">ตั้งชื่อและเลือกหน้าตา ผม เสื้อ กางเกง/กระโปรง ของทีมแต่ละคน — บันทึกในเครื่องนี้อัตโนมัติ</p>
          </div>
          <button className="btn-x" onClick={onClose} aria-label="ปิด">
            ✕
          </button>
        </div>

        <div className="editor-body">
          <nav className="editor-list" aria-label="เลือกตัวละคร">
            {AGENTS.map((a) => (
              <button key={a.id} className={`editor-pick ${a.id === id ? "on" : ""}`} onClick={() => setId(a.id)}>
                <CharCanvas ap={profiles[a.id].appearance} scale={2} crop={[0, 8, 16, 18]} className="editor-thumb" />
                <span>
                  <b className={`team-text-${a.team}`}>{profiles[a.id].name}</b>
                  <small>{a.role}</small>
                </span>
              </button>
            ))}
          </nav>

          <div className="editor-stage">
            <div className="editor-preview">
              <CharCanvas ap={ap} anim={anim} dir={dir} scale={9} className="preview-canvas" />
            </div>
            <div className="seg seg-small" role="group" aria-label="ท่าทาง">
              {ANIMS.map((a) => (
                <button key={a.id} className={anim === a.id ? "on" : ""} onClick={() => setAnim(a.id)}>
                  {a.name}
                </button>
              ))}
            </div>
            <div className="seg seg-small" role="group" aria-label="ทิศทาง">
              {DIRS.map((d) => (
                <button key={d.id} className={dir === d.id ? "on" : ""} onClick={() => setDir(d.id)}>
                  {d.name}
                </button>
              ))}
            </div>
            <div className="editor-actions">
              <button className="btn" onClick={() => office.setAppearance(id, randomAppearance())}>
                🎲 สุ่มลุค
              </button>
              <button className="btn" onClick={() => office.resetProfile(id)}>
                ↺ คืนค่าเริ่มต้น
              </button>
            </div>
          </div>

          <div className="editor-form">
            <section>
              <h4>ชื่อ</h4>
              <div className="name-row">
                <input
                  className="text-in"
                  value={draft}
                  maxLength={MAX_NAME}
                  onChange={(e) => {
                    setDraft(e.target.value);
                    office.setName(id, e.target.value);
                  }}
                  placeholder={agent.name}
                  aria-label="ชื่อตัวละคร"
                />
                <span className="muted small">
                  {agent.role} · {TEAM_LABEL[agent.team]}
                </span>
              </div>
              <p className="hint">ชื่อนี้จะแสดงในออฟฟิศ บอร์ดงาน และถูกส่งให้ AI ใช้เรียกตัวเองตอนทำงาน (ว่างไว้ = ใช้ชื่อเดิม: {agent.name})</p>
            </section>

            <section>
              <h4>สีผิว</h4>
              <div className="swatches">
                {SKINS.map((s) => (
                  <button key={s.id} className={`swatch-btn ${ap.skin === s.id ? "on" : ""}`} style={{ background: s.hex }} title={s.name} aria-label={s.name} onClick={() => set({ skin: s.id })} />
                ))}
              </div>
            </section>

            <section>
              <h4>ทรงผม</h4>
              <OptionGrid<HairStyleId>
                options={HAIR_STYLES}
                value={ap.hairStyle}
                onPick={(h) => set({ hairStyle: h })}
                render={(h) => <CharCanvas ap={{ ...ap, hairStyle: h }} scale={3} crop={[0, 6, 16, 17]} />}
              />
              <button className={`opt opt-none ${ap.hairStyle === "none" ? "on" : ""}`} onClick={() => set({ hairStyle: "none" })}>
                ไม่มีผม
              </button>
              <h5>สีผม</h5>
              <Swatches colors={HAIR_COLORS.slice(1)} value={ap.hairColor} onPick={(hex) => set({ hairColor: hex })} defaultLabel="ดำ (สีเดิม)" disabled={ap.hairStyle === "none"} />
            </section>

            <section>
              <h4>เสื้อ</h4>
              <OptionGrid<TopId>
                options={TOPS}
                value={ap.top}
                onPick={(t) => set({ top: t })}
                render={(t) => <CharCanvas ap={{ ...ap, top: t }} scale={3} crop={[0, 20, 16, 11]} />}
              />
              <h5>สีเสื้อ</h5>
              <Swatches colors={GARMENT_COLORS} value={ap.topColor} onPick={(hex) => set({ topColor: hex })} defaultLabel="สีเดิมของเสื้อ" />
            </section>

            <section>
              <h4>กางเกง / กระโปรง</h4>
              {dress && <p className="hint">เดรสมีกระโปรงในตัว จึงไม่ต้องเลือกกางเกง/กระโปรงเพิ่ม</p>}
              <OptionGrid<BottomId>
                options={BOTTOMS}
                value={ap.bottom}
                onPick={(b) => set({ bottom: b })}
                disabled={dress}
                render={(b) => <CharCanvas ap={{ ...ap, bottom: b, top: dress ? "tee" : ap.top }} scale={3} crop={[0, 23, 16, 8]} />}
              />
              <h5>สีกางเกง / กระโปรง</h5>
              <Swatches colors={GARMENT_COLORS} value={ap.bottomColor} onPick={(hex) => set({ bottomColor: hex })} defaultLabel="สีเดิม" disabled={dress} />
            </section>

            <section className="editor-foot">
              <button
                className="btn"
                onClick={() => {
                  if (confirm("คืนชื่อและหน้าตาของทุกคนเป็นค่าเริ่มต้น?")) office.resetAll();
                }}
              >
                ↺ คืนค่าเริ่มต้นทั้งทีม (รวมห้อง)
              </button>
              <button
                className="btn"
                onClick={() => {
                  const blob = new Blob([office.exportJson()], { type: "application/json" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "gastron-office-settings.json";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                ⬇ ส่งออกการตั้งค่า
              </button>
              <label className="btn">
                ⬆ นำเข้า
                <input
                  type="file"
                  accept="application/json"
                  hidden
                  onChange={async (e) => {
                    const f = e.target.files?.[0];
                    if (!f) return;
                    try {
                      office.importJson(await f.text());
                    } catch {
                      alert("ไฟล์ตั้งค่าไม่ถูกต้อง");
                    }
                    e.target.value = "";
                  }}
                />
              </label>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
