import { NextResponse } from "next/server";
import { AUTH_COOKIE, authUsers, SESSION_DAYS, signSession } from "@/lib/auth";
import { checkPassword } from "@/lib/password";

export async function POST(req: Request) {
  if (!process.env.AUTH_SECRET) return NextResponse.json({ error: "เซิร์ฟเวอร์ยังไม่ได้ตั้ง AUTH_SECRET" }, { status: 500 });
  const { email, password } = (await req.json()) as { email?: string; password?: string };
  const user = authUsers().find((u) => u.email.toLowerCase() === (email ?? "").trim().toLowerCase());
  // always run one hash check, so an unknown email takes as long as a wrong password
  const ok = user ? await checkPassword(password ?? "", user.hash) : (await checkPassword(password ?? "", "scrypt:00:00"), false);
  if (!user || !ok) {
    await new Promise((r) => setTimeout(r, 700));
    return NextResponse.json({ error: "อีเมลหรือรหัสผ่านไม่ถูกต้อง" }, { status: 401 });
  }
  const res = NextResponse.json({ ok: true, role: user.role });
  res.cookies.set(AUTH_COOKIE, await signSession({ email: user.email, role: user.role === "admin" ? "admin" : "member" }), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * SESSION_DAYS,
    path: "/",
  });
  return res;
}
