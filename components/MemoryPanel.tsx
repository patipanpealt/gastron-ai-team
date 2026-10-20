"use client";

import { useState } from "react";
import { AGENTS } from "@/lib/agents";
import { MEMORY_KIND_LABEL, memory, type MemoryKind, type MemoryScope, useMemory } from "@/lib/memory";
import { useOffice } from "@/lib/office/store";

const STARTERS: { kind: MemoryKind; text: string }[] = [
  { kind: "rule", text: "น้ำเสียงของแบรนด์: มืออาชีพ น่าเชื่อถือ ไม่ขู่ ไม่โอ้อวดเกินจริง" },
  { kind: "rule", text: "Header บนภาพต้องสั้น ไม่เกิน 8 คำ" },
  { kind: "rule", text: "แคปชัน Facebook เปิดด้วยประโยคเดียวที่ดึงความสนใจ ปิดด้วย CTA ชัดเจน" },
];

/** Teach the team: standing rules, good examples and feedback, remembered and sent with every request. */
export function MemoryPanel({ onClose }: { onClose: () => void }) {
  const items = useMemory();
  const { profiles } = useOffice();
  const [scope, setScope] = useState<MemoryScope>("team");
  const [kind, setKind] = useState<MemoryKind>("rule");
  const [text, setText] = useState("");
  const scopeName = (s: MemoryScope) => (s === "team" ? "ทั้งทีม" : `${profiles[s].name} (${AGENTS.find((a) => a.id === s)?.role})`);
  const add = () => {
    memory.add(scope, kind, text);
    setText("");
  };

  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal memory-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="ฝึก AI">
        <div className="drawer-head">
          <div>
            <h2>สอนทีม</h2>
            <p className="muted small">สิ่งที่สอนไว้จะใช้กับทุกงานต่อจากนี้ เก็บในเบราว์เซอร์เครื่องนี้ และแนบไปกับทุกคำขอ AI</p>
          </div>
          <button className="btn-x" onClick={onClose} aria-label="ปิด">
            ✕
          </button>
        </div>
        <div className="modal-body memory-body">
          <div className="memory-form">
            <div className="memory-row">
              <label>
                สอนใคร
                <select value={scope} onChange={(e) => setScope(e.target.value as MemoryScope)}>
                  <option value="team">ทั้งทีม</option>
                  {AGENTS.map((a) => (
                    <option key={a.id} value={a.id}>
                      {profiles[a.id].name} — {a.role}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                ประเภท
                <select value={kind} onChange={(e) => setKind(e.target.value as MemoryKind)}>
                  {(Object.keys(MEMORY_KIND_LABEL) as MemoryKind[]).map((k) => (
                    <option key={k} value={k}>
                      {MEMORY_KIND_LABEL[k]}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={3}
              maxLength={1200}
              placeholder="เช่น “อย่าใช้คำว่า ดีที่สุด” หรือวางแคปชันตัวอย่างที่ชอบ แล้วบอกว่าชอบตรงไหน…"
            />
            <div className="memory-actions">
              <button className="btn btn-green" onClick={add} disabled={!text.trim()}>
                + จำไว้
              </button>
              <span className="muted small">{text.length}/1200</span>
            </div>
            {items.length === 0 && (
              <div className="presets">
                <span className="mini-label">ตัวอย่างที่เพิ่มได้เลย:</span>
                {STARTERS.map((s) => (
                  <button key={s.text} className="preset" onClick={() => memory.add("team", s.kind, s.text)}>
                    {s.text.slice(0, 34)}…
                  </button>
                ))}
              </div>
            )}
          </div>

          <h3 className="appendix">สิ่งที่ทีมจำไว้ ({items.length})</h3>
          {items.length === 0 && <p className="muted">ยังไม่มี — ลองเพิ่มกฎหรือตัวอย่างด้านบน</p>}
          <ul className="memory-list">
            {items.map((m) => (
              <li key={m.id} className={m.on ? "" : "memory-off"}>
                <div className="memory-meta">
                  <span className="tag-wood">{MEMORY_KIND_LABEL[m.kind]}</span>
                  <span className="muted small">สอน: {scopeName(m.scope)}</span>
                  <label className="memory-toggle">
                    <input type="checkbox" checked={m.on} onChange={(e) => memory.update(m.id, { on: e.target.checked })} /> ใช้อยู่
                  </label>
                  <button className="btn-x" onClick={() => memory.remove(m.id)} aria-label="ลบ">
                    🗑
                  </button>
                </div>
                <textarea value={m.text} rows={2} maxLength={1200} onChange={(e) => memory.update(m.id, { text: e.target.value })} />
              </li>
            ))}
          </ul>
          {items.length > 0 && (
            <button
              className="btn btn-red"
              onClick={() => {
                if (confirm("ลบความจำทั้งหมด?")) memory.clear();
              }}
            >
              ลบทั้งหมด
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/** A small box in the finished-brief view: tell the team what to do differently (or what was good) next time. */
export function TeachBox() {
  const [kind, setKind] = useState<MemoryKind>("feedback");
  const [text, setText] = useState("");
  const [saved, setSaved] = useState(false);
  return (
    <div className="teach-box">
      <b>สอนทีมจากงานนี้</b>
      <div className="memory-row">
        <select value={kind} onChange={(e) => setKind(e.target.value as MemoryKind)}>
          <option value="feedback">ข้อติ / ครั้งหน้าอยากให้ทำต่าง</option>
          <option value="example">ตัวอย่างที่ดี (อยากให้ทำแบบนี้อีก)</option>
          <option value="rule">กฎถาวร</option>
        </select>
      </div>
      <textarea
        value={text}
        rows={2}
        maxLength={1200}
        onChange={(e) => {
          setText(e.target.value);
          setSaved(false);
        }}
        placeholder="เช่น header ยาวไป ครั้งหน้าให้สั้นกว่านี้ / แคปชันแบบนี้ชอบ…"
      />
      <button
        className="btn btn-green"
        disabled={!text.trim()}
        onClick={() => {
          memory.add("team", kind, text);
          setText("");
          setSaved(true);
        }}
      >
        จำไว้ให้ทั้งทีม
      </button>
      {saved && <span className="muted small"> ✓ บันทึกแล้ว แก้ได้ที่ปุ่ม “สอนทีม”</span>}
    </div>
  );
}
