"use client";

import { useState } from "react";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    setLoading(false);
    if (res.ok) window.location.href = "/";
    else setError(((await res.json()) as { error?: string }).error || "เข้าสู่ระบบไม่สำเร็จ");
  }

  return (
    <div className="login">
      <form className="wood login-card" onSubmit={submit}>
        <h1>
          <span className="g-red">GAS</span>
          <span className="g-green">TRON</span>
        </h1>
        <p className="muted">ใส่รหัสผ่านของทีมเพื่อเข้า AI Office</p>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="รหัสผ่านทีม" autoFocus />
        <button className="btn btn-green" disabled={!password || loading}>
          {loading ? "กำลังตรวจสอบ…" : "▶ เข้าออฟฟิศ"}
        </button>
        {error && <p className="err">{error}</p>}
      </form>
    </div>
  );
}
