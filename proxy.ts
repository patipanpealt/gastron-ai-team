import { NextResponse, type NextRequest } from "next/server";
import { AUTH_COOKIE, loginRequired, verifySession } from "@/lib/auth";

// Everything needs a login once AUTH_USERS is set.
export async function proxy(req: NextRequest) {
  if (!loginRequired()) return NextResponse.next();

  const { pathname } = req.nextUrl;
  if (pathname === "/login" || pathname === "/api/login" || pathname.startsWith("/brand/")) return NextResponse.next();

  if (await verifySession(req.cookies.get(AUTH_COOKIE)?.value)) return NextResponse.next();

  if (pathname.startsWith("/api/")) return NextResponse.json({ error: "กรุณาเข้าสู่ระบบ" }, { status: 401 });
  return NextResponse.redirect(new URL("/login", req.url));
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg).*)"],
};
