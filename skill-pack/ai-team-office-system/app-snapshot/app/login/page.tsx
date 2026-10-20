"use client";

import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [confirm, setConfirm] = useState("");
  const [setup, setSetup] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (setup && password !== confirm) return setError("รหัสผ่านทั้งสองช่องไม่ตรงกัน");
    setLoading(true);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, setup }),
      });
      if (res.ok) {
        window.location.href = "/";
        return;
      }
      const d = (await res.json()) as { error?: string; needSetup?: boolean };
      if (d.needSetup) {
        setSetup(true);
        setPassword("");
        setLoading(false);
        return;
      }
      setError(d.error || "เข้าสู่ระบบไม่สำเร็จ");
    } catch {
      setError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    }
    setLoading(false);
  }

  return (
    <div className="login">
      <form className="wood login-card" onSubmit={submit}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img className="login-logo" src="/brand/gastron-logo.svg" alt="GASTRON" />
        <p className="login-tagline">AI Marketing Creative Team</p>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="อีเมล" autoComplete="username" autoFocus required readOnly={setup} />
        {setup && <p className="login-tagline">เข้าครั้งแรก — ตั้งรหัสผ่านของคุณ (อย่างน้อย 8 ตัวอักษร)</p>}
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={setup ? "ตั้งรหัสผ่านใหม่" : "รหัสผ่าน"} autoComplete={setup ? "new-password" : "current-password"} minLength={setup ? 8 : undefined} required />
        {setup && <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="ยืนยันรหัสผ่าน" autoComplete="new-password" required />}
        <button className="btn btn-green" disabled={!email || !password || (setup && !confirm) || loading}>
          {loading ? "กำลังตรวจสอบ…" : setup ? "ตั้งรหัสผ่านและเข้าสู่ระบบ" : "เข้าสู่ระบบ"}
        </button>
        {error && <p className="err">{error}</p>}
      </form>
    </div>
  );
}
