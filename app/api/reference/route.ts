import { NextResponse } from "next/server";
import { completeText } from "@/lib/ai";
import { DEMO_MODE, errorMessage } from "@/lib/claude";
import { readUrl } from "@/lib/reference";

export const maxDuration = 60;

const SYSTEM = `คุณช่วยทีมการตลาดอ่านเอกสารอ้างอิงที่หัวหน้าแปะลิงก์มา สรุปเป็นภาษาไทย 120–250 คำ ให้ทีมนำไปใช้ทำ brief ได้ทันที:
- ใจความหลัก ข้อเท็จจริง ตัวเลข ชื่อสินค้า/รุ่น วันที่ ที่ปรากฏในเนื้อหา (ห้ามแต่งเพิ่ม)
- น้ำเสียง/สไตล์ ถ้าเป็นตัวอย่างงานหรือแนวทางแบรนด์
- ข้อห้ามหรือข้อกำหนดที่ต้องทำตาม
ถ้าเนื้อหาไม่เกี่ยวกับงานการตลาดหรือขาดข้อมูล ให้บอกตรง ๆ สั้น ๆ`;

export async function POST(req: Request) {
  const { url, note, modelChoice } = (await req.json()) as { url?: string; note?: string; modelChoice?: string };
  if (!url?.trim()) return NextResponse.json({ error: "กรุณาใส่ลิงก์" }, { status: 400 });
  const read = await readUrl(url);
  if (!read.ok) return NextResponse.json({ ok: false, problem: read.problem });
  if (DEMO_MODE) {
    return NextResponse.json({ ok: true, summary: `[DEMO] อ่านลิงก์ได้ ${read.text.length} ตัวอักษร — ใส่ API key เพื่อให้ AI สรุปจริง\n\n${read.text.slice(0, 300)}…` });
  }
  try {
    const summary = await completeText(SYSTEM, `ลิงก์: ${url}\nโน้ตของหัวหน้า: ${note?.trim() || "(ไม่มี)"}\n\nเนื้อหาที่อ่านได้:\n"""\n${read.text}\n"""`, 1500, modelChoice);
    return NextResponse.json({ ok: true, summary });
  } catch (err) {
    return NextResponse.json({ ok: false, problem: errorMessage(err) });
  }
}
