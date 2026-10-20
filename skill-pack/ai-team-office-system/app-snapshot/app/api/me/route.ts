import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { AUTH_COOKIE, loginRequired, verifySession } from "@/lib/auth";

export async function GET() {
  if (!loginRequired()) return NextResponse.json({ loginRequired: false });
  const s = await verifySession((await cookies()).get(AUTH_COOKIE)?.value);
  return NextResponse.json(s ? { loginRequired: true, ...s } : { loginRequired: true }, { status: s ? 200 : 401 });
}
