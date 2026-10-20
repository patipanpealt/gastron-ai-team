import { NextResponse } from "next/server";
import { AUTH_COOKIE, authUsers, SESSION_DAYS, signSession } from "@/lib/auth";
import { checkPassword, hashPassword } from "@/lib/password";
import { getMember, normEmail, saveMember } from "@/lib/members";

const MIN_PASSWORD = 8;

export async function POST(req: Request) {
  if (!process.env.AUTH_SECRET) return NextResponse.json({ error: "เซิร์ฟเวอร์ยังไม่ได้ตั้ง AUTH_SECRET" }, { status: 500 });
  const { email, password, setup } = (await req.json()) as { email?: string; password?: string; setup?: boolean };
  const e = normEmail(email);
  const pw = password ?? "";
  const envUser = authUsers().find((u) => u.email.toLowerCase() === e);
  const member = envUser ? null : await getMember(e);
  let user: { email: string; role: string } | null = envUser ?? member;

  // an admin-added member with no password yet: let them choose one
  if (member && !member.hash) {
    if (!setup) return NextResponse.json({ needSetup: true }, { status: 409 });
    if (pw.length < MIN_PASSWORD) return NextResponse.json({ error: `รหัสผ่านต้องยาวอย่างน้อย ${MIN_PASSWORD} ตัวอักษร` }, { status: 400 });
    const fresh = await getMember(e); // re-read so two people can't both claim it
    if (!fresh || fresh.hash) return NextResponse.json({ error: "ตั้งรหัสผ่านไปแล้ว กรุณาเข้าสู่ระบบ" }, { status: 409 });
    await saveMember({ ...fresh, hash: await hashPassword(pw) });
  } else {
    const hash = envUser?.hash ?? member?.hash;
    // always run one hash check, so an unknown email takes as long as a wrong password
    const ok = hash ? await checkPassword(pw, hash) : (await checkPassword(pw, "scrypt:00:00"), false);
    if (!user || !ok) {
      await new Promise((r) => setTimeout(r, 700));
      return NextResponse.json({ error: "อีเมลหรือรหัสผ่านไม่ถูกต้อง" }, { status: 401 });
    }
  }

  user = user!;
  const role = user.role === "admin" ? "admin" : "member";
  const res = NextResponse.json({ ok: true, role });
  res.cookies.set(AUTH_COOKIE, await signSession({ email: user.email, role }), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * SESSION_DAYS,
    path: "/",
  });
  return res;
}
