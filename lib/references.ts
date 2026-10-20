import { uid } from "./uid";
// Reference links the user attaches to a brief. The brief can point at them: "ตาม Reference 1".
export interface Reference {
  id: string;
  url: string;
  /** What the user says this link is / what to take from it. */
  note: string;
  status: "idle" | "reading" | "ok" | "fail";
  /** The AI's summary of what the link contains (editable by the user). */
  summary: string;
  problem?: string;
}

export const MAX_REFERENCES = 6;

export const newReference = (): Reference => ({ id: uid(), url: "", note: "", status: "idle", summary: "" });

/** The block appended to the brief: numbered like the boxes in the UI, so "Reference 2" in the brief means entry 2. */
export function referencesBlock(refs: Reference[]): string {
  const used = refs.map((r, i) => ({ r, n: i + 1 })).filter(({ r }) => r.url.trim());
  if (!used.length) return "";
  const lines = used.map(({ r, n }) => {
    const parts = [`### Reference ${n}: ${r.url.trim()}`];
    if (r.note.trim()) parts.push(`หัวหน้าบอกว่า: ${r.note.trim()}`);
    if (r.summary.trim()) parts.push(`สรุปเนื้อหาในลิงก์:\n${r.summary.trim()}`);
    else parts.push("(ยังไม่ได้อ่านเนื้อหาลิงก์นี้ — ใช้เฉพาะคำอธิบายของหัวหน้า)");
    return parts.join("\n");
  });
  return `\n\n## Reference ที่หัวหน้าแนบมา\nเมื่อ brief อ้างถึง "Reference ที่ N" ให้ใช้เนื้อหาของรายการที่ N ด้านล่างนี้ และอย่าแต่งเนื้อหาที่ไม่มีใน Reference\n\n${lines.join("\n\n")}`;
}
