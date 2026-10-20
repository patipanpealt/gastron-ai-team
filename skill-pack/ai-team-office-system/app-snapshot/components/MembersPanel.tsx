"use client";

import { useCallback, useEffect, useState } from "react";

interface Row {
  email: string;
  role: string;
  source: "env" | "app";
  hasPassword: boolean;
}

/** Admin: add people by email. They choose their own password the first time they log in. */
export function MembersPanel({ onClose }: { onClose: () => void }) {
  const [rows, setRows] = useState<Row[]>([]);
  const [canEdit, setCanEdit] = useState(true);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    const res = await fetch("/api/members");
    if (!res.ok) return setMsg(((await res.json()) as { error?: string }).error || "โหลดไม่สำเร็จ");
    const d = (await res.json()) as { canEdit: boolean; users: Row[] };
    setRows(d.users);
    setCanEdit(d.canEdit);
  }, []);
  useEffect(() => {
    void load();
  }, [load]);

  async function call(method: string, body: object, ok?: string) {
    setMsg("");
    const res = await fetch("/api/members", { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const d = (await res.json()) as { error?: string };
    setMsg(res.ok ? ok ?? "" : d.error || "ไม่สำเร็จ");
    if (res.ok) await load();
    return res.ok;
  }

  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal memory-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="สมาชิก">
        <div className="drawer-head">
          <div>
            <h2>สมาชิกทีม</h2>
            <p className="muted small">เพิ่มอีเมลที่นี่ แล้วบอกให้เขาเข้าเว็บ กรอกอีเมล แล้วตั้งรหัสผ่านเองตอนเข้าครั้งแรก</p>
          </div>
          <button className="btn-x" onClick={onClose} aria-label="ปิด">
            ✕
          </button>
        </div>
        <div className="modal-body memory-body">
          {canEdit ? (
            <form
              className="memory-form"
              onSubmit={async (e) => {
                e.preventDefault();
                if (await call("POST", { email, role }, "เพิ่มแล้ว — ให้เขาเข้าสู่ระบบด้วยอีเมลนี้เพื่อตั้งรหัสผ่าน")) setEmail("");
              }}
            >
              <div className="memory-row">
                <label>
                  อีเมล
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@company.com" required />
                </label>
                <label>
                  สิทธิ์
                  <select value={role} onChange={(e) => setRole(e.target.value)}>
                    <option value="member">member</option>
                    <option value="admin">admin</option>
                  </select>
                </label>
              </div>
              <div className="memory-actions">
                <button className="btn btn-green" disabled={!email}>
                  + เพิ่มสมาชิก
                </button>
              </div>
            </form>
          ) : (
            <p className="err">ยังไม่ได้เชื่อม Upstash Redis จึงเพิ่มสมาชิกจากหน้านี้ไม่ได้</p>
          )}
          {msg && <p className="muted small">{msg}</p>}

          <h3 className="appendix">สมาชิกทั้งหมด ({rows.length})</h3>
          {rows.map((r) => (
            <div key={r.email} className="memory-row" style={{ alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 6 }}>
              <span>
                {r.role === "admin" ? "👑" : "👤"} {r.email}{" "}
                <small className="muted">{r.hasPassword ? "" : "· ยังไม่ได้ตั้งรหัสผ่าน"}</small>
              </span>
              {r.source === "app" && (
                <span>
                  {r.hasPassword && (
                    <button className="link-btn" onClick={() => confirm(`รีเซ็ตรหัสผ่านของ ${r.email}? เขาจะต้องตั้งรหัสใหม่`) && void call("PATCH", { email: r.email }, "รีเซ็ตแล้ว")}>
                      รีเซ็ตรหัส
                    </button>
                  )}{" "}
                  <button className="link-btn" onClick={() => confirm(`ลบ ${r.email} ออกจากระบบ?`) && void call("DELETE", { email: r.email }, "ลบแล้ว")}>
                    ลบ
                  </button>
                </span>
              )}
            </div>
          ))}
          <p className="muted small">คนที่ตั้งผ่าน AUTH_USERS (ใน Vercel) จะแสดงที่นี่ แต่แก้/ลบได้ที่ Vercel เท่านั้น</p>
        </div>
      </div>
    </div>
  );
}
