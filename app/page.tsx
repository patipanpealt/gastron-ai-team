"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { extractPalette, Markdown } from "@/components/Markdown";
import { CharacterEditor } from "@/components/CharacterEditor";
import { OfficeCanvas } from "@/components/OfficeCanvas";
import { RoomEditor } from "@/components/RoomEditor";
import { MemoryPanel, TeachBox } from "@/components/MemoryPanel";
import { downloadBriefPdf } from "@/lib/pdf";
import { MAX_REFERENCES, newReference, type Reference, referencesBlock } from "@/lib/references";
import { AGENT_BY_ID, AGENTS, type AgentId, type RunKind, TEAM_LABEL, type Team } from "@/lib/agents";
import type { EditState, OfficeEngine } from "@/lib/office/engine";
import { office, useOffice } from "@/lib/office/store";
import { loadHistory, Orchestrator, type Phase, type RunState, runToMarkdown, saveRun } from "@/lib/orchestrator";

const PRESETS: Record<RunKind, string[]> = {
  facebook: [
    "โพสต์ Facebook เปิดตัว G-Finder Multi เครื่องตรวจจับแก๊สแบบพกพา กลุ่มเป้าหมายวิศวกร Safety ในนิคม EEC อยากให้ทักมาขอใบเสนอราคา",
    "โพสต์ Facebook ชวนมาเยี่ยมชมบูธ Gastron ในงานแสดงสินค้าอุตสาหกรรม มี QR ดูแผนผังบูธ และของแจก",
    "โพสต์ให้ความรู้เรื่องมาตรฐาน ATEX กับ SIL2 แบบอ่านง่าย สร้างความน่าเชื่อถือให้แบรนด์ พร้อมแคมเปญต่อเนื่อง 3 โพสต์",
  ],
  graphic: [
    "โปสเตอร์ A3 ชวนมาบูธงานแสดงสินค้าอุตสาหกรรม โชว์เครื่องตรวจจับแก๊ส พร้อมส่วนลด 20% สำหรับผู้เข้าชมงาน มี QR ดูแผนผังบูธ",
    "โพสต์ Facebook + LinkedIn เปิดตัว G-Finder Multi เครื่องตรวจจับแก๊สแบบพกพาหลายชนิด สำหรับวิศวกร Safety ในนิคม EEC",
    "ใบปลิว A5 สองหน้า แนะนำ Flame Detector GTF-1100 สำหรับโรงงานปิโตรเคมี เน้นมาตรฐานกันระเบิด",
    "Banner เว็บไซต์ + cover Facebook ธีม 'ปลอดภัยทุกกะการทำงาน' สร้างภาพลักษณ์แบรนด์ Gastron Thailand",
  ],
  campaign: [
    "วางแคมเปญ 1 เดือนโปรโมทเครื่องตรวจจับแก๊สแบบพกพา G-Finder Multi สำหรับโรงงานในนิคม EEC งบโฆษณา 200,000 บาท",
    "ทำแผนคอนเทนต์ LinkedIn 4 สัปดาห์ เพื่อสร้างความน่าเชื่อถือของแบรนด์ Gastron ในกลุ่มวิศวกรความปลอดภัยไทย",
    "เตรียมแผนการตลาดก่อน-ระหว่าง-หลังงานแสดงสินค้าอุตสาหกรรมครั้งถัดไป",
    "เขียนบทความ SEO และโครง landing page สำหรับ Flame Detector GTF-1100 กลุ่มเป้าหมายโรงงานปิโตรเคมี",
  ],
};

const ARTWORKS = ["Poster", "Social Post", "Story / Reels cover", "Banner เว็บ", "Leaflet / Brochure", "Booth backdrop", "Roll-up", "Email header"];

const PHASE_LABEL: Record<Phase, string> = {
  discussing: "ทีมกำลังคุยงานกัน",
  planning: "ผู้อำนวยการกำลังวางแผน",
  kickoff: "ประชุมแจกงาน",
  working: "ทีมกำลังทำงาน",
  compiling: "ผู้อำนวยการกำลังรวมงาน",
  done: "งานเสร็จแล้ว",
  error: "เกิดข้อผิดพลาด",
  stopped: "หยุดงานแล้ว",
};

const TEAMS: Team[] = ["lead", "creative", "growth", "data"];

export default function OfficePage() {
  const engine = useRef<OfficeEngine | null>(null);
  const orch = useRef<Orchestrator | null>(null);
  const [run, setRun] = useState<RunState | null>(null);
  const [kind, setKind] = useState<RunKind>("graphic");
  const [brief, setBrief] = useState("");
  const [artworks, setArtworks] = useState<string[]>([]);
  const [refs, setRefs] = useState<Reference[]>([]);
  const patchRef = (id: string, patch: Partial<Reference>) => setRefs((cur) => cur.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  /** Ask the server to open the link, read it and summarise it. */
  const readRef = useCallback(async (r: Reference) => {
    if (!r.url.trim()) return;
    patchRef(r.id, { status: "reading", problem: undefined });
    try {
      const res = await fetch("/api/reference", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: r.url, note: r.note }) });
      const data = (await res.json()) as { ok?: boolean; summary?: string; problem?: string; error?: string };
      if (data.ok) patchRef(r.id, { status: "ok", summary: data.summary ?? "", problem: undefined });
      else patchRef(r.id, { status: "fail", problem: data.problem || data.error || "อ่านลิงก์ไม่สำเร็จ" });
    } catch {
      patchRef(r.id, { status: "fail", problem: "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้" });
    }
  }, []);
  const [selected, setSelected] = useState<AgentId | null>(null);
  const [showFinal, setShowFinal] = useState(false);
  const [history, setHistory] = useState<RunState[]>([]);
  const [status, setStatus] = useState<{ demo: boolean; model: string } | null>(null);
  const { profiles, room } = useOffice();
  const [edit, setEditState] = useState<EditState>({ active: false, placing: null, selectedId: null });
  const [charEditor, setCharEditor] = useState<AgentId | null>(null);
  const [showMemory, setShowMemory] = useState(false);
  const [me, setMe] = useState<{ email: string; role: string } | null>(null);
  useEffect(() => {
    void fetch("/api/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((d: { email?: string; role?: string } | null) => d?.email && setMe({ email: d.email, role: d.role ?? "member" }))
      .catch(() => undefined);
  }, []);
  const setEdit = useCallback((patch: Partial<EditState>) => setEditState((e) => ({ ...e, ...patch })), []);
  const phaseLabel = (p: Phase) =>
    p === "planning" ? `${profiles.director.name} กำลังวางแผน` : p === "compiling" ? `${profiles.director.name} กำลังรวมงาน` : PHASE_LABEL[p];

  useEffect(() => {
    setHistory(loadHistory());
    fetch("/api/status")
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => {});
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      setShowFinal(false);
      setSelected(null);
      setCharEditor(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const active = !!run && ["planning", "discussing", "kickoff", "working", "compiling"].includes(run.phase);

  const start = useCallback(() => {
    if (!engine.current || !brief.trim() || active) return;
    const base =
      kind === "graphic" && artworks.length ? `${brief.trim()}\n\nชิ้นงานที่ต้องการ: ${artworks.join(", ")}` : brief.trim();
    const full = base + referencesBlock(refs);
    const o = new Orchestrator(full, kind, engine.current, (r) => {
      setRun(r);
      if (r.phase === "done") {
        saveRun(r);
        setHistory(loadHistory());
      }
    });
    orch.current = o;
    setRun(o.run);
    setShowFinal(false);
    void o.start();
  }, [brief, active, kind, artworks, refs]);

  const feedRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const [chatText, setChatText] = useState("");
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [run?.chat]);
  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }, [run?.feed.length]);

  const agentStatus = (id: AgentId) => {
    if (!run || !active) return "idle";
    if (id === "director") return run.phase === "compiling" || run.phase === "planning" ? "working" : "lead";
    const ts = run.tasks.filter((t) => t.agent === id);
    if (!ts.length) return "free";
    if (ts.some((t) => t.status === "working")) return "working";
    if (ts.some((t) => t.status === "waiting")) return "waiting";
    return "done";
  };

  const total = run ? run.tasks.length + 1 : 0;
  const finished = run
    ? run.tasks.filter((t) => t.status === "done" || t.status === "error").length + (run.final.status === "done" ? 1 : 0)
    : 0;
  const progress = !run ? 0 : run.phase === "done" ? 100 : total > 1 ? Math.round((finished / total) * 100) : 4;

  return (
    <div className="app">
      <header className="topbar">
        <div className="sign">
          <span className="sign-post" aria-hidden />
          <div className="sign-board">
            <h1>
              <span className="g-red">GAS</span>
              <span className="g-green">TRON</span> <span className="sign-sub">AI OFFICE</span>
            </h1>
            <p>ทีมการตลาด AI 11 ตำแหน่ง · คิด Graphic Brief และแคมเปญร่วมกันแบบเรียลไทม์</p>
          </div>
        </div>
        <div className="topbar-right">
          {status?.demo && (
            <span className="tag-wood tag-demo" title="ยังไม่ได้ใส่ ANTHROPIC_API_KEY — ใช้ผลลัพธ์จำลอง">
              DEMO MODE
            </span>
          )}
          {status && !status.demo && <span className="tag-wood">{status.model}</span>}
          {run && <span className={`tag-wood phase-${run.phase}`}>{phaseLabel(run.phase)}</span>}
          {me && (
            <span className="tag-wood account" title={`ล็อกอินเป็น ${me.email}`}>
              <b>{me.role === "admin" ? "👑" : "👤"}</b> {me.email}
              <button
                className="link-btn"
                onClick={() => void fetch("/api/logout", { method: "POST" }).then(() => (window.location.href = "/login"))}
              >
                ออกจากระบบ
              </button>
            </span>
          )}
        </div>
      </header>

      <main className="layout">
        <section className="stage">
          <div className="stage-tools">
            <button className="btn" onClick={() => setCharEditor(selected ?? "director")}>
              🧑‍🎨 แต่งตัว &amp; ตั้งชื่อ
            </button>
            <button
              className={`btn ${edit.active ? "btn-green" : ""}`}
              onClick={() => {
                setEdit({ active: !edit.active, placing: null, selectedId: null });
                if (!edit.active) setSelected(null);
              }}
              disabled={active}
              title={active ? "รอทีมทำงานเสร็จก่อนจึงจะแต่งห้องได้" : undefined}
            >
              🏠 {edit.active ? "กำลังแต่งห้อง" : "แต่งห้อง"}
            </button>
            <button className="btn" onClick={() => setShowMemory(true)}>
              🧠 ฝึก AI
            </button>
          </div>
          <div className="frame">
            <i className="post tl" />
            <i className="post tr" />
            <i className="post bl" />
            <i className="post br" />
            <OfficeCanvas
              onReady={(e) => (engine.current = e)}
              onSelect={setSelected}
              selected={selected}
              room={room}
              profiles={profiles}
              edit={edit}
              onRoomChange={(r, selectId) => {
                office.setRoom(r);
                if (selectId !== undefined) setEdit({ selectedId: selectId });
              }}
              onEditSelect={(id) => setEdit({ selectedId: id })}
              onPlaceCancel={() => setEdit({ placing: null })}
            />
          </div>

          {edit.active && <RoomEditor edit={edit} setEdit={setEdit} onDone={() => setEdit({ active: false, placing: null, selectedId: null })} />}

          {run && (
            <div className="wood progress-wood">
              <span className="progress-label">{phaseLabel(run.phase)}</span>
              <div className="bar" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
                <div className="bar-fill" style={{ width: `${progress}%` }} />
              </div>
              <span className="progress-num">{progress}%</span>
            </div>
          )}

          <div className="roster">
            {TEAMS.map((team) => (
              <div key={team} className={`wood roster-team team-${team}`}>
                <h3>{TEAM_LABEL[team]}</h3>
                <div className="roster-list">
                  {AGENTS.filter((a) => a.team === team).map((a) => {
                    const st = agentStatus(a.id);
                    return (
                      <button
                        key={a.id}
                        className={`chip ${selected === a.id ? "chip-on" : ""}`}
                        onClick={() => setSelected(selected === a.id ? null : a.id)}
                        onDoubleClick={() => setCharEditor(a.id)}
                        title="คลิกเพื่อดูงาน · ดับเบิลคลิกเพื่อแต่งตัว/เปลี่ยนชื่อ"
                      >
                        <span className={`dot dot-${st}`} />
                        <span className="chip-name">{profiles[a.id].name}</span>
                        <span className="chip-role">{a.role}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>

        <aside className="side">
          <div className="wood brief-panel">
            <h2>📜 สั่งงานทีม</h2>
            <div className="seg" role="tablist" aria-label="ประเภทงาน">
              <button role="tab" aria-selected={kind === "graphic"} className={kind === "graphic" ? "on" : ""} onClick={() => setKind("graphic")} disabled={active}>
                🎨 Graphic Brief
              </button>
              <button role="tab" aria-selected={kind === "facebook"} className={kind === "facebook" ? "on" : ""} onClick={() => setKind("facebook")} disabled={active}>
                💬 โพสต์ Facebook
              </button>
              <button role="tab" aria-selected={kind === "campaign"} className={kind === "campaign" ? "on" : ""} onClick={() => setKind("campaign")} disabled={active}>
                📣 แคมเปญ / คอนเทนต์
              </button>
            </div>
            <p className="hint">
              {kind === "graphic"
                ? "ทีมจะช่วยกันคิด brief ส่งดีไซเนอร์: copy บนชิ้นงาน, visual direction, สี, layout wireframe, ขนาด และ AI prompt"
                : kind === "facebook"
                  ? "ทีมจะนั่งคุยกันจริง ๆ ในห้องประชุม: header, เนื้อหา, layout ให้กราฟิก, แคปชัน และแคมเปญเล็ก ๆ — คุณพิมพ์แทรกได้ระหว่างคุย"
                  : "ทีมจะวางแผนแคมเปญครบ: กลยุทธ์, คอนเทนต์, โฆษณา, SEO และแผนวัดผล"}
            </p>
            <textarea
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
              placeholder={
                kind === "facebook"
                  ? "โพสต์นี้เกี่ยวกับอะไร สินค้า/เรื่องอะไร กลุ่มเป้าหมาย อยากให้คนทำอะไรหลังเห็นโพสต์…"
                  : kind === "graphic"
                  ? "งานกราฟิกชิ้นนี้คืออะไร ใช้ที่ไหน อยากสื่ออะไร มีข้อมูลบังคับอะไรบ้าง (วันที่ สถานที่ โปรโมชัน QR)…"
                  : "เล่าว่าอยากให้ทีมทำอะไร เช่น สินค้า กลุ่มเป้าหมาย งบ ระยะเวลา ช่องทาง…"
              }
              rows={4}
              disabled={active}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) start();
              }}
            />
            {!active && (
              <div className="refs">
                <span className="mini-label">🔗 Reference (แปะลิงก์ แล้วพิมพ์ในช่องบรีฟว่า “ตาม Reference 1” ได้):</span>
                {refs.map((r, i) => (
                  <div key={r.id} className={`ref ref-${r.status}`}>
                    <div className="ref-top">
                      <b className="ref-n">{i + 1}</b>
                      <input
                        value={r.url}
                        placeholder="วางลิงก์ เช่น Google Docs / หน้าเว็บ"
                        onChange={(e) => patchRef(r.id, { url: e.target.value, status: "idle", summary: "", problem: undefined })}
                        onBlur={() => r.status === "idle" && r.url.trim() && void readRef(r)}
                      />
                      <button className="btn-x" title="ลบ Reference นี้" onClick={() => setRefs((cur) => cur.filter((x) => x.id !== r.id))}>
                        🗑
                      </button>
                    </div>
                    <input value={r.note} placeholder={`รายละเอียด: Reference ${i + 1} คืออะไร ให้ดูอะไรจากมัน…`} maxLength={400} onChange={(e) => patchRef(r.id, { note: e.target.value })} />
                    {r.status === "reading" && <p className="muted small">⏳ กำลังอ่านลิงก์และสรุป…</p>}
                    {r.status === "fail" && (
                      <p className="err small">
                        ⚠️ {r.problem}{" "}
                        <button className="link-btn" onClick={() => void readRef(r)}>
                          ลองอ่านอีกครั้ง
                        </button>
                      </p>
                    )}
                    {r.status === "ok" && (
                      <details className="ref-sum">
                        <summary>✅ AI อ่านแล้ว — ดู/แก้สรุป</summary>
                        <textarea value={r.summary} rows={5} onChange={(e) => patchRef(r.id, { summary: e.target.value })} />
                        <button className="link-btn" onClick={() => void readRef(r)}>
                          อ่านใหม่
                        </button>
                      </details>
                    )}
                  </div>
                ))}
                {refs.length < MAX_REFERENCES && (
                  <button className="btn" onClick={() => setRefs((cur) => [...cur, newReference()])}>
                    + เพิ่ม Reference {refs.length + 1}
                  </button>
                )}
              </div>
            )}
            {kind === "graphic" && !active && (
              <div className="artworks">
                <span className="mini-label">ชิ้นงาน:</span>
                {ARTWORKS.map((w) => (
                  <button
                    key={w}
                    className={`toggle ${artworks.includes(w) ? "on" : ""}`}
                    onClick={() => setArtworks((cur) => (cur.includes(w) ? cur.filter((x) => x !== w) : [...cur, w]))}
                  >
                    {w}
                  </button>
                ))}
              </div>
            )}
            {!active && (
              <div className="presets">
                <span className="mini-label">ตัวอย่าง:</span>
                {PRESETS[kind].map((p) => (
                  <button key={p} className="preset" onClick={() => setBrief(p)} title={p}>
                    {p.slice(0, 30)}…
                  </button>
                ))}
              </div>
            )}
            <div className="brief-actions">
              {active ? (
                <button className="btn btn-red" onClick={() => orch.current?.stop()}>
                  ■ หยุดงาน
                </button>
              ) : (
                <button className="btn btn-green" onClick={start} disabled={!brief.trim() || refs.some((r) => r.status === "reading")}>
                  ▶ ส่งให้ทีม
                </button>
              )}
              {run?.final.output && (
                <button className="btn" onClick={() => setShowFinal(true)}>
                  {run.kind === "graphic" ? "🎨 ดู Graphic Brief" : run.kind === "facebook" ? "📘 ดู Facebook Post Brief" : "📦 ดู Deliverable"}
                </button>
              )}
            </div>
            {run?.error && <p className="err">⚠️ {run.error}</p>}
          </div>

          {run && run.kind === "facebook" && (
            <div className="wood chat-panel">
              <h2>💬 ห้องประชุม</h2>
              <div className="chat" ref={chatRef}>
                {(run.chat ?? []).map((c, i) => {
                  const a = c.agent === "user" ? null : AGENT_BY_ID[c.agent];
                  return (
                    <div key={i} className={`chat-msg ${a ? "" : "chat-user"}`}>
                      <b className={a ? `team-text-${a.team}` : ""}>{a ? profiles[a.id].name : "คุณ"}</b>
                      <span className="chat-role">{a ? a.role : "ผู้สั่งงาน"}</span>
                      <p>{c.text || "…"}</p>
                    </div>
                  );
                })}
              </div>
              {active && run.phase === "discussing" && (
                <form
                  className="chat-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!chatText.trim()) return;
                    orch.current?.say(chatText);
                    setChatText("");
                  }}
                >
                  <input value={chatText} onChange={(e) => setChatText(e.target.value)} placeholder="พิมพ์แทรกวงสนทนา เช่น อยากให้ header สั้นกว่านี้…" maxLength={500} />
                  <button className="btn btn-green" disabled={!chatText.trim()}>
                    ส่ง
                  </button>
                </form>
              )}
            </div>
          )}

          {run && run.tasks.length > 0 && (
            <div className="wood tasks-panel">
              <h2>🗂️ บอร์ดงาน</h2>
              {run.summary && <p className="summary">{run.summary}</p>}
              <ol className="tasks">
                {run.tasks.map((t) => {
                  const a = AGENT_BY_ID[t.agent];
                  return (
                    <li key={t.id} className={`task task-${t.status}`} onClick={() => setSelected(t.agent)}>
                      <span className="task-status">
                        {t.status === "done" ? "✓" : t.status === "working" ? "●" : t.status === "error" ? "!" : "○"}
                      </span>
                      <div>
                        <div className="task-title">{t.title}</div>
                        <div className="task-meta">
                          {profiles[a.id].name} · {a.role}
                          {t.dependsOn.length > 0 && ` · รอ ${t.dependsOn.join(", ")}`}
                        </div>
                      </div>
                      <span className="task-id">{t.id}</span>
                    </li>
                  );
                })}
                <li
                  className={`task task-${run.final.status === "pending" ? "waiting" : run.final.status}`}
                  onClick={() => run.final.output && setShowFinal(true)}
                >
                  <span className="task-status">{run.final.status === "done" ? "✓" : run.final.status === "working" ? "●" : "○"}</span>
                  <div>
                    <div className="task-title">{run.kind === "graphic" ? "รวมเป็น Graphic Brief ฉบับสมบูรณ์" : "รวมเป็น Deliverable สุดท้าย"}</div>
                    <div className="task-meta">{profiles.director.name} · Marketing Director</div>
                  </div>
                  <span className="task-id">★</span>
                </li>
              </ol>
            </div>
          )}

          <div className="wood feed-panel">
            <h2>📡 ความเคลื่อนไหวในออฟฟิศ</h2>
            <div className="feed" ref={feedRef}>
              {!run && <p className="muted">ยังเงียบอยู่… ส่ง brief ให้ทีมเพื่อเริ่มงาน หรือคลิกที่ตัวละครเพื่อดูโปรไฟล์</p>}
              {run?.feed.map((f, i) => {
                const a = AGENT_BY_ID[f.agent];
                return (
                  <div key={i} className={`feed-item feed-${f.kind}`}>
                    <span className="feed-time">
                      {new Date(f.t).toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </span>
                    <b className={`team-text-${a.team}`}>{profiles[a.id].name}</b> {f.text}
                  </div>
                );
              })}
            </div>
          </div>

          {history.length > 0 && !active && (
            <div className="wood history-panel">
              <h2>🗄️ งานที่ผ่านมา (เครื่องนี้)</h2>
              <ul className="history">
                {history.map((h) => (
                  <li key={h.id}>
                    <button
                      onClick={() => {
                        setRun(h);
                        setShowFinal(true);
                      }}
                    >
                      <span>
                        {h.kind === "graphic" ? "🎨" : h.kind === "facebook" ? "💬" : "📣"} {h.brief.slice(0, 60)}
                      </span>
                      <small>{new Date(h.createdAt).toLocaleString("th-TH")}</small>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>
      </main>

      {selected && <AgentDrawer id={selected} run={run} onClose={() => setSelected(null)} onEdit={() => setCharEditor(selected)} />}
      {showMemory && <MemoryPanel onClose={() => setShowMemory(false)} />}
      {charEditor && <CharacterEditor initial={charEditor} onClose={() => setCharEditor(null)} />}
      {showFinal && run && <FinalModal run={run} onClose={() => setShowFinal(false)} />}
    </div>
  );
}

function AgentDrawer({ id, run, onClose, onEdit }: { id: AgentId; run: RunState | null; onClose: () => void; onEdit: () => void }) {
  const a = AGENT_BY_ID[id];
  const { profiles } = useOffice();
  const tasks = run?.tasks.filter((t) => t.agent === id) ?? [];
  const isDirector = id === "director";
  const body = useRef<HTMLDivElement>(null);
  const latest = isDirector ? run?.final.output : tasks.at(-1)?.output;
  useEffect(() => {
    const el = body.current;
    if (el && el.scrollHeight - el.scrollTop - el.clientHeight < 120) el.scrollTop = el.scrollHeight;
  }, [latest]);

  return (
    <div className="drawer" role="dialog" aria-label={`${profiles[id].name} — ${a.role}`}>
      <div className="drawer-head">
        <div>
          <h2>
            {profiles[id].name} <small>· {a.role}</small>
          </h2>
          <p className="muted">
            {a.roleTh} — {a.skills}
          </p>
        </div>
        <div className="modal-actions">
          <button className="btn" onClick={onEdit}>
            ✏️ แต่งตัว / ชื่อ
          </button>
          <button className="btn-x" onClick={onClose} aria-label="ปิด">
            ✕
          </button>
        </div>
      </div>
      <div className="drawer-body" ref={body}>
        {isDirector && run && (
          <>
            {run.summary && (
              <section>
                <h4>แผนงาน</h4>
                <p>{run.summary}</p>
              </section>
            )}
            {(run.final.thinking || run.final.output) && (
              <section>
                <h4>{run.kind === "graphic" ? "Graphic Brief" : run.kind === "facebook" ? "Facebook Post Brief" : "Deliverable สุดท้าย"}</h4>
                {run.final.thinking && <Thinking text={run.final.thinking} />}
                <Markdown text={run.final.output} />
              </section>
            )}
          </>
        )}
        {!isDirector && tasks.length === 0 && <p className="muted">ตอนนี้ยังไม่มีงานที่ได้รับมอบหมาย</p>}
        {tasks.map((t) => (
          <section key={t.id}>
            <h4>
              {t.title} <span className={`tag tag-${t.status}`}>{t.status}</span>
            </h4>
            <p className="muted small">{t.instructions}</p>
            {t.thinking && <Thinking text={t.thinking} />}
            {t.output ? <Markdown text={t.output} /> : t.status === "waiting" && <p className="muted">⏳ รองานจากเพื่อนร่วมทีม…</p>}
            {t.error && <p className="err">{t.error}</p>}
          </section>
        ))}
      </div>
    </div>
  );
}

function Thinking({ text }: { text: string }) {
  return (
    <details className="thinking">
      <summary>💭 ความคิดระหว่างทำงาน</summary>
      <p>{text}</p>
    </details>
  );
}

function FinalModal({ run, onClose }: { run: RunState; onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  const { profiles } = useOffice();
  const md = runToMarkdown(run);
  const palette = run.kind !== "campaign" ? extractPalette(run.final.output) : [];
  const [pdfBusy, setPdfBusy] = useState(false);
  const savePdf = async () => {
    const el = document.querySelector<HTMLElement>(".modal .print-doc");
    if (!el) return;
    setPdfBusy(true);
    try {
      await downloadBriefPdf(el, `gastron-${run.kind === "graphic" ? "graphic-brief" : run.kind === "facebook" ? "facebook-post" : "deliverable"}-${new Date(run.createdAt).toISOString().slice(0, 10)}.pdf`);
    } catch (err) {
      console.error("PDF failed, falling back to print", err);
      window.print(); // fall back to the browser's own print-to-PDF
    } finally {
      setPdfBusy(false);
    }
  };
  const download = () => {
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const el = document.createElement("a");
    el.href = url;
    el.download = `gastron-${run.kind === "graphic" ? "graphic-brief" : run.kind === "facebook" ? "facebook-post" : "deliverable"}-${new Date(run.createdAt).toISOString().slice(0, 10)}.md`;
    el.click();
    URL.revokeObjectURL(url);
  };
  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Deliverable">
        <div className="drawer-head">
          <div>
            <h2>{run.kind === "graphic" ? "🎨 Graphic Brief" : run.kind === "facebook" ? "📘 Facebook Post Brief" : "📦 Deliverable"}</h2>
            <p className="muted small">Brief: {run.brief}</p>
          </div>
          <div className="modal-actions">
            <button
              className="btn"
              onClick={() => {
                void navigator.clipboard.writeText(md).then(() => {
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                });
              }}
            >
              {copied ? "✓ คัดลอกแล้ว" : "คัดลอก"}
            </button>
            <button className="btn" onClick={download}>
              ⬇ .md
            </button>
            <button className="btn btn-green" onClick={() => void savePdf()} disabled={pdfBusy}>
              {pdfBusy ? "⏳ กำลังสร้าง PDF…" : "⬇ ดาวน์โหลด PDF"}
            </button>
            <button className="btn-x" onClick={onClose} aria-label="ปิด">
              ✕
            </button>
          </div>
        </div>
        <PrintDoc run={run} palette={palette} />
        <div className="modal-body">
          {palette.length > 0 && (
            <div className="palette-strip" aria-label="Color palette">
              {palette.map((c) => (
                <button
                  key={c}
                  className="swatch"
                  style={{ background: c }}
                  title={`คัดลอก ${c}`}
                  onClick={() => void navigator.clipboard.writeText(c)}
                >
                  <span>{c}</span>
                </button>
              ))}
            </div>
          )}
          <Markdown text={run.final.output || "_(ยังไม่เสร็จ)_"} />
          {run.final.output && <TeachBox />}
          {(run.chat?.length ?? 0) > 0 && (
            <details className="appendix-item">
              <summary>บทสนทนาของทีม ({run.chat!.length} ข้อความ)</summary>
              {run.chat!.map((c, i) => (
                <p key={i}>
                  <b>{c.name}</b>: {c.text}
                </p>
              ))}
            </details>
          )}
          {run.tasks.length > 0 && <h3 className="appendix">งานของแต่ละตำแหน่ง</h3>}
          {run.tasks.map((t) => (
            <details key={t.id} className="appendix-item">
              <summary>
                {t.title} — {profiles[t.agent].name} ({AGENT_BY_ID[t.agent].role})
              </summary>
              <Markdown text={t.output || `_(${t.status})_`} />
            </details>
          ))}
        </div>
      </div>
    </div>
  );
}

/** The designed A4 version of the brief. Hidden on screen; the print stylesheet shows it (and nothing else). */
function PrintDoc({ run, palette }: { run: RunState; palette: string[] }) {
  const out = run.final.output || "";
  const title = out.match(/^#\s+(.+)$/m)?.[1]?.replace(/^(Graphic Brief|Facebook Post Brief):\s*/i, "") || "Brief";
  const body = out.replace(/^#\s+.+\n?/m, "");
  const label = run.kind === "facebook" ? "Facebook Post Brief" : run.kind === "graphic" ? "Graphic Brief" : "Deliverable";
  return (
    <div className="print-doc">
      <header className="pd-head">
        <div>
          <div className="pd-kicker">GASTRON THAILAND · {label.toUpperCase()}</div>
          <h1>{title}</h1>
        </div>
        <div className="pd-date">{new Date(run.createdAt).toLocaleDateString("th-TH", { year: "numeric", month: "long", day: "numeric" })}</div>
      </header>
      {palette.length > 0 && (
        <div className="pd-palette">
          {palette.map((c) => (
            <span key={c} style={{ background: c, color: lum(c) > 0.6 ? "#1f2430" : "#fff", textShadow: lum(c) > 0.6 ? "none" : undefined }}>
              {c}
            </span>
          ))}
        </div>
      )}
      <Markdown text={body} />
      <footer className="pd-foot">
        <b>Brief ต้นทาง:</b> {run.brief}
      </footer>
    </div>
  );
}

/** Rough brightness of a #RRGGBB colour (0 dark – 1 light), to pick readable text over it. */
function lum(hex: string) {
  const n = parseInt(hex.slice(1), 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
}
