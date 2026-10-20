"use client";

import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        window.location.href = "/";
        return;
      }
      setError(((await res.json()) as { error?: string }).error || "เข้าสู่ระบบไม่สำเร็จ");
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
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="อีเมล" autoComplete="username" autoFocus required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="รหัสผ่าน" autoComplete="current-password" required />
        <button className="btn btn-green" disabled={!email || !password || loading}>
          {loading ? "กำลังตรวจสอบ…" : "▶ เข้าสู่ระบบ"}
        </button>
        {error && <p className="err">{error}</p>}
      </form>
    </div>
  );
}
