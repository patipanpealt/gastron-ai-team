import { AGENTS, AGENT_BY_ID, type AgentId, type RunKind, WORKER_IDS } from "./agents";
import { BRAND_CONTEXT } from "./brand";

export interface TaskInput {
  agentName: string;
  role: string;
  title: string;
  output: string;
}

/** One line of the team's conversation. */
export interface ChatLine {
  /** Who said it: an agent id, or "user" for the person running the office. */
  agent: AgentId | "user";
  name: string;
  role: string;
  text: string;
}

export interface AgentRequest {
  agentId: AgentId;
  kind: RunKind;
  mode: "task" | "compile" | "chat";
  /** The conversation so far (chat turns, and the final compile of a Facebook post). */
  transcript?: ChatLine[];
  /** What this speaker is supposed to do in this turn of the conversation. */
  turnGoal?: string;
  brief: string;
  task: { title: string; instructions: string };
  inputs: TaskInput[];
  /** Display names the user gave the team (agent id -> name). */
  names?: Record<string, string>;
  /** What the user has taught this agent (rules, good examples, feedback). */
  memory?: string;
}

const OFFICE_RULES = `คุณเป็นสมาชิกทีมการตลาด AI ใน Virtual Office ของ Gastron Thailand ทำงานร่วมกับเพื่อนร่วมทีมคนอื่น
- ตอบเป็นภาษาไทย ในรูปแบบ Markdown ที่อ่านง่าย (หัวข้อ, bullet, ตาราง เมื่อเหมาะสม)
- ส่งงานที่ใช้ได้จริงทันที ไม่ต้องเกริ่นหรือถามกลับ ถ้าข้อมูลไม่พอให้ตั้งสมมติฐานที่สมเหตุสมผลและระบุไว้สั้น ๆ
- ทำเฉพาะส่วนที่ได้รับมอบหมาย และต่อยอดจากงานของเพื่อนร่วมทีมที่แนบมา (ถ้ามี) ให้สอดคล้องกัน
- ห้ามแต่งข้อเท็จจริง ตัวเลข หรือใบรับรองที่ไม่มีในข้อมูลบริษัท ใช้ [ใส่ข้อมูล] แทน
- ถ้า brief มีหัวข้อ "Reference ที่หัวหน้าแนบมา" ให้ใช้เนื้อหานั้นเป็นข้อมูลอ้างอิง และเมื่อ brief บอกว่า "ตาม Reference ที่ N" ต้องทำตามรายการที่ N โดยตรง
- เมื่อระบุสี ให้เขียนรหัส HEX ใน inline code เสมอ เช่น \`#D70010\``;

/** How a layout wireframe must be written so the app can draw it. */
export const LAYOUT_SPEC = `## รูปแบบ Layout Wireframe (สำคัญ — แอปจะวาดเป็นภาพให้ดีไซเนอร์ดู)
สำหรับชิ้นงานหลักแต่ละชิ้น ให้ใส่ code block ภาษา \`layout\` ที่เป็น JSON ตามนี้ (ตำแหน่งเป็น % ของกรอบ 0–100):
\`\`\`layout
{"title":"Poster A3 แนวตั้ง","ratio":"3:4","background":"#FFFFFF","zones":[
  {"label":"โลโก้ GASTRON","x":6,"y":4,"w":30,"h":7,"color":"#009143"},
  {"label":"Headline","text":"ก๊าซรั่ว ไม่ต้องรอให้รู้สึก","x":6,"y":14,"w":88,"h":16,"color":"#D70010"},
  {"label":"ภาพสินค้า G-Finder Multi","x":10,"y":34,"w":80,"h":38,"color":"#93D0AF"},
  {"label":"CTA + QR","x":6,"y":80,"w":88,"h":14,"color":"#009143"}
]}
\`\`\`
- ratio ใช้รูปแบบ "กว้าง:สูง" เช่น "1:1", "4:5", "16:9", "3:4", "1.91:1"
- zones ไม่ควรเกิน 8 ช่อง label สั้น ๆ บอกว่าอะไรอยู่ตรงนั้น color คือสีหลักของโซนนั้น
- **ทุกโซนที่เป็นข้อความต้องมี "text" = ข้อความจริงที่จะขึ้นบน Artwork แบบคำต่อคำ** (ไม่ใช่คำอธิบาย) ส่วนโซนที่เป็นภาพ/โลโก้ไม่ต้องมี text
- JSON ต้องถูกต้อง (ใช้ " เท่านั้น ห้ามมี comment)`;

const GRAPHIC_FOCUS = `## โหมดงานนี้: Graphic Brief
ผลลัพธ์สุดท้ายของทีมคือ "Graphic Brief" ที่ส่งให้กราฟิกดีไซเนอร์ลงมือทำได้ทันที
ทุกคนจึงต้องโฟกัสสิ่งที่ใช้ในการออกแบบจริง: ข้อความที่อยู่บนชิ้นงาน, ลำดับความสำคัญ, ภาพ, สี, ขนาด, ข้อมูลบังคับ
หลีกเลี่ยงทฤษฎียาว ๆ ที่ดีไซเนอร์เอาไปใช้ไม่ได้`;

const FACEBOOK_FOCUS = `## โหมดงานนี้: โพสต์ Facebook
ทีมกำลังช่วยกันคิดโพสต์ Facebook 1 โพสต์ของ Gastron Thailand ให้ครบ: (1) Header / headline บนภาพ (2) เนื้อหาบนภาพ (3) layout สำหรับให้กราฟิกทำ (4) แคปชันที่ใช้โพสต์ (5) แคมเปญเล็ก ๆ ต่อเนื่อง (ถ้าเหมาะ)
ทุกอย่างต้องเอาไปใช้ได้จริง: เป็นข้อความตัวอย่างจริง ไม่ใช่คำแนะนำกว้าง ๆ`;

const CHAT_RULES = `## วิธีคุยในห้องประชุมนี้
- คุณกำลังคุยสดกับเพื่อนในทีมในห้องประชุม พูดภาษาไทยแบบเป็นกันเองแต่มืออาชีพ ยาว 2–5 ประโยค
- ห้ามใช้หัวข้อ ตาราง หรือ bullet ยาว ๆ — พูดเหมือนคนคุยกัน (ยกตัวอย่างข้อความจริงในเครื่องหมายคำพูดได้)
- เรียกชื่อเพื่อนที่คุณตอบหรือถาม ถ้าเห็นด้วยให้ต่อยอด ถ้าไม่เห็นด้วยให้ค้านพร้อมเหตุผลสั้น ๆ
- เสนอของจริงตามหน้าที่ของคุณ ไม่พูดวนซ้ำสิ่งที่เพื่อนพูดไปแล้ว
- ถ้ามีข้อความจาก "คุณ" (หัวหน้าที่มาร่วมคุย) ให้ตอบ/ทำตามก่อนเสมอ
- ห้ามแต่งข้อเท็จจริงหรือตัวเลข ใช้ [ใส่ข้อมูล] แทน`;

export function systemFor(agentId: AgentId, kind: RunKind, names?: Record<string, string>, chat = false, memory = "") {
  const a = AGENT_BY_ID[agentId];
  const role = [`## ตำแหน่งของคุณ: ${a.role} (${a.roleTh}) ชื่อ ${names?.[agentId] || a.name}`, a.persona, `ความเชี่ยวชาญ: ${a.skills}`];
  if (kind === "graphic") {
    role.push(GRAPHIC_FOCUS);
    if (agentId === "creative" || agentId === "director") role.push(LAYOUT_SPEC);
  }
  if (kind === "facebook") {
    role.push(FACEBOOK_FOCUS);
    if (chat) role.push(CHAT_RULES);
    else if (agentId === "creative" || agentId === "director") role.push(LAYOUT_SPEC);
  }
  if (memory.trim()) {
    role.push(`## สิ่งที่หัวหน้าสอนทีมไว้ (ต้องทำตามเสมอ เหนือกว่าแนวทางทั่วไป ยกเว้นขัดกับข้อเท็จจริง)\n${memory.trim()}`);
  }
  return [
    // Shared by every agent, so it can be cached across calls.
    { type: "text" as const, text: `${OFFICE_RULES}\n\n${BRAND_CONTEXT}`, cache_control: { type: "ephemeral" as const } },
    { type: "text" as const, text: role.join("\n") },
  ];
}

const COMPILE_CAMPAIGN = `# งานของคุณตอนนี้: รวมเป็น Deliverable สุดท้าย
รวมงานทั้งหมดข้างบนเป็นเอกสารส่งมอบฉบับเดียวที่พร้อมนำเสนอ:
1. Executive Summary (สั้น ๆ 3–5 bullet)
2. เนื้อหาหลักจัดเป็นหมวด โดยแก้ตามข้อเสนอของ QA แล้ว (ไม่ต้องคัดลอกทุกอย่างซ้ำ ให้เรียบเรียงใหม่ให้กระชับ)
3. Next Steps / สิ่งที่ต้องให้คนตัดสินใจหรือเติมข้อมูล`;

const COMPILE_GRAPHIC = `# งานของคุณตอนนี้: รวมเป็น Graphic Brief ฉบับสมบูรณ์สำหรับดีไซเนอร์
แก้ตามข้อเสนอของ QA แล้ว เขียนตามโครงนี้ทุกหัวข้อ (ใช้หัวข้อระดับ ## ตามนี้):
# Graphic Brief: <ชื่องาน>
ภาพรวมการเขียน: กระชับ ตรงประเด็น ใช้ตารางและ bullet สั้น ๆ ตัดคำอธิบายยืดยาว ดีไซเนอร์ต้องอ่านจบใน 2 นาที
## 1. ข้อมูลงาน — ตาราง: ชิ้นงาน, ช่องทาง, ผู้ดู, กำหนดส่ง ([ใส่ข้อมูล] ถ้าไม่รู้)
## 2. วัตถุประสงค์ — อยากให้คนดู "รู้ / รู้สึก / ทำ" อะไร
## 3. กลุ่มเป้าหมาย & Insight — 2–4 bullet
## 4. Key Message — 1 ประโยค
## 5. ข้อความบน Artwork (Copy Deck) — **หัวข้อที่สำคัญที่สุด** ดีไซเนอร์ต้องคัดลอกไปวางได้เลย ตาราง: # (ตรงกับเลขโซนใน layout) | ตำแหน่ง/องค์ประกอบ | **ข้อความจริงที่ขึ้นบนภาพ (คำต่อคำ ครบทุกบรรทัด)** | ขนาด/น้ำหนักตัวอักษรโดยสัมพัทธ์ (ใหญ่/กลาง/เล็ก, หนา/ปกติ) — ต้องครอบคลุมทุกข้อความที่มองเห็นบนชิ้นงาน ห้ามเขียนแค่คำอธิบาย เช่น "พาดหัวที่ดึงดูด" ต้องเขียนข้อความจริง ถ้าข้อมูลยังไม่มีให้ใส่ [ใส่ข้อมูล] เฉพาะตรงนั้น; ให้ headline สำรองอีก 2 แบบ
## 6. Visual Direction — Concept, Mood & Tone, ภาพ/องค์ประกอบหลัก, Typography
## 7. Color Palette — ตาราง: สี | HEX (inline code) | ใช้ตรงไหน
## 8. Layout — อธิบายลำดับสายตาสั้น ๆ แล้วใส่ \`layout\` block ของชิ้นงานหลัก (และชิ้นย่อยถ้าสัดส่วนต่างกันมาก) โดยทุกโซนข้อความมี "text" ตรงกับ Copy Deck ข้อ 5 ทุกตัวอักษร
## 9. ขนาด & Deliverables — ตาราง: ชิ้นงาน | ขนาด (px หรือ mm) | ไฟล์ส่งมอบ | หมายเหตุ
## 10. AI Image Prompts — prompt ภาษาอังกฤษใน code block สำหรับเจนภาพประกอบ 2–3 แบบ
## 11. Do & Don't
## 12. Checklist ก่อนส่งงาน — checkbox list (- [ ])`;

const COMPILE_FACEBOOK = `# งานของคุณตอนนี้: สรุปบทสนทนาเป็น Facebook Post Brief ฉบับสมบูรณ์
ใช้สิ่งที่ทีมตกลงกันในบทสนทนาข้างบน (ข้อความจาก "คุณ" มาก่อนเสมอ) เขียนตามโครงนี้ทุกหัวข้อ (หัวข้อระดับ ##):
# Facebook Post Brief: <ชื่อโพสต์>
## 1. ข้อมูลโพสต์ — ตาราง: ช่องทาง, รูปแบบ (ภาพเดี่ยว/คารูเซล), ขนาดภาพ, กำหนดโพสต์ ([ใส่ข้อมูล] ถ้าไม่รู้)
## 2. วัตถุประสงค์ & Key Message — รู้/รู้สึก/ทำ และ key message 1 ประโยค
## 3. ข้อความบน Artwork (Copy Deck) — **หัวข้อที่สำคัญที่สุด** ตาราง: # (ตรงกับเลขโซนใน layout) | ตำแหน่ง | **ข้อความจริงที่ขึ้นบนภาพ คำต่อคำ ครบทุกบรรทัด** (Header, Sub-header, Body, CTA, ข้อมูลบังคับ) | ขนาด/น้ำหนักตัวอักษรโดยสัมพัทธ์ — ห้ามเขียนแค่คำอธิบาย ต้องเป็นข้อความที่จะพิมพ์ลงบนภาพจริง; header สำรองอีก 2 แบบ
## 4. Layout สำหรับกราฟิก — อธิบายลำดับสายตาสั้น ๆ แล้วใส่ \`layout\` block (ratio ตรงกับขนาดภาพ) ทุกโซนข้อความมี "text" ตรงกับ Copy Deck ข้อ 3 ทุกตัวอักษร พร้อมสี HEX ใน inline code
## 5. Visual Direction — ภาพหลัก, mood & tone, typography, Color Palette (ตาราง สี | HEX | ใช้ตรงไหน)
## 6. แคปชัน Facebook — แคปชันหลัก (พร้อมใช้) + แบบสั้นอีก 1 แบบ + hashtag + ข้อความ CTA/ลิงก์ ([ใส่ลิงก์])
## 7. แคมเปญเล็ก ๆ ต่อเนื่อง — 3 โพสต์ถัดไปหรือไอเดียต่อยอด (หัวข้อ, มุม, ช่วงเวลา) ถ้าทีมไม่ได้คุยเรื่องนี้ให้เสนอสั้น ๆ
## 8. สิ่งที่ยังต้องตัดสินใจ / เติมข้อมูล
## 9. Checklist ก่อนส่งกราฟิก — checkbox list (- [ ])
ให้ข้อความ header และแคปชันตรงกับที่ตกลงกันในห้องประชุม ห้ามเปลี่ยนเงียบ ๆ
เขียนกระชับ ใช้ตารางและ bullet สั้น ๆ ดีไซเนอร์ต้องอ่านจบใน 2 นาที`;

function transcriptText(lines: ChatLine[]) {
  return lines.map((l) => `**${l.name}** (${l.agent === "user" ? "หัวหน้า/ผู้สั่งงาน" : l.role}): ${l.text}`).join("\n\n");
}

export function userMessageFor(req: AgentRequest) {
  if (req.mode === "chat") {
    const t = req.transcript?.length ? `# บทสนทนาในห้องประชุมจนถึงตอนนี้\n${transcriptText(req.transcript)}` : "# บทสนทนา\n(ยังไม่มีใครพูด คุณเป็นคนเริ่ม)";
    return [`# Brief\n${req.brief}`, t, `# ตาของคุณ\n${req.turnGoal ?? "พูดต่อจากเพื่อน"}\n\nพูดเฉพาะข้อความของคุณ ไม่ต้องใส่ชื่อนำหน้า`].join("\n\n");
  }
  const parts = [`# Brief จากลูกค้า/หัวหน้า\n${req.brief}`];
  if (req.transcript?.length) parts.push(`# บทสนทนาของทีม\n${transcriptText(req.transcript)}`);
  if (req.inputs.length) {
    parts.push(
      "# งานจากเพื่อนร่วมทีมที่เกี่ยวข้อง\n" +
        req.inputs
          .map((i) => `## ${i.title} — โดย ${i.agentName} (${i.role})\n${i.output}`)
          .join("\n\n---\n\n"),
    );
  }
  if (req.mode === "compile") parts.push(req.kind === "facebook" ? COMPILE_FACEBOOK : req.kind === "graphic" ? COMPILE_GRAPHIC : COMPILE_CAMPAIGN);
  else parts.push(`# งานที่ได้รับมอบหมาย: ${req.task.title}\n${req.task.instructions}`);
  return parts.join("\n\n");
}

export const PLAN_SYSTEM = `${OFFICE_RULES}\n\n${BRAND_CONTEXT}`;

const PLAN_RULES: Record<RunKind, string> = {
  facebook: `- งานนี้คือโพสต์ Facebook: ใช้ copywriter, creative, social และ qa`,
  campaign: `- เลือกเฉพาะคนที่จำเป็นต่อ brief นี้ (ปกติ 4–8 task) ไม่ต้องใช้ทุกคน`,
  graphic: `- งานนี้คือ Graphic Brief: เป้าหมายคือ brief ให้ดีไซเนอร์ ใช้ 4–6 task
- ต้องมี task ของ copywriter (ข้อความจริงที่จะขึ้นบนชิ้นงานทุกส่วน คำต่อคำ + headline หลายแบบ) และ creative (visual concept, สี, typography, layout wireframe แบบ \`layout\` block, AI image prompts) เสมอ
- ใช้ strategist เพื่อสรุปวัตถุประสงค์/key message/insight ก่อน (ให้ copywriter และ creative รอ)
- ถ้าชิ้นงานลงหลายช่องทาง ให้ social หรือ ads ระบุขนาดและข้อกำหนดของแต่ละช่องทาง
- researcher ใช้เฉพาะเมื่อต้องหา insight ที่ไม่มีใน brief`,
};

export function planPrompt(brief: string, kind: RunKind, names?: Record<string, string>) {
  const nm = (id: string, d: string) => names?.[id] || d;
  const roster = AGENTS.filter((a) => a.id !== "director")
    .map((a) => `- ${a.id}: ${nm(a.id, a.name)} — ${a.role} | ${a.skills}`)
    .join("\n");
  return `คุณคือ ${nm("director", "Max")}, Marketing Director ของทีม ได้รับ brief นี้:

"""
${brief}
"""

ทีมของคุณ:
${roster}

วางแผนงานโดยแตกเป็น task แล้วมอบหมายให้สมาชิกทีม:
${PLAN_RULES[kind]}
- ห้ามมอบหมายให้ตัวเอง (director)
- task ที่ต้องใช้ผลงานของคนอื่นให้ใส่ id ของ task นั้นใน dependsOn แต่ให้ทำงานคู่ขนานได้มากที่สุด
- task สุดท้ายต้องเป็นของ qa เพื่อตรวจงานทั้งหมด โดย dependsOn ทุก task ที่ผลิตงาน
- instructions เขียนเป็นภาษาไทย ระบุให้ชัดว่าต้องส่งมอบอะไร รูปแบบไหน ปริมาณเท่าไร
- id ใช้รูปแบบ t1, t2, t3 ...
- summary: สรุปแนวทางของแผนเป็นภาษาไทย 1–2 ประโยค`;
}

export const PLAN_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "tasks"],
  properties: {
    summary: { type: "string" },
    tasks: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "agent", "title", "instructions", "dependsOn"],
        properties: {
          id: { type: "string" },
          agent: { type: "string", enum: WORKER_IDS },
          title: { type: "string" },
          instructions: { type: "string" },
          dependsOn: { type: "array", items: { type: "string" } },
        },
      },
    },
  },
} as const;
