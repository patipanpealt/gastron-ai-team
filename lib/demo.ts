import { AGENT_BY_ID, type AgentId, type Plan, type RunKind } from "./agents";
import type { AgentRequest } from "./prompts";

// Scripted output used when no API key is configured, so the office can be
// demoed and tested without spending credits.

export function demoPlan(brief: string, kind: RunKind): Plan {
  const short = brief.slice(0, 60);
  if (kind === "graphic") {
    return {
      summary: `[DEMO] ทำ Graphic Brief จาก "${short}" — สรุป key message ก่อน แล้วให้ copy กับ visual ทำคู่กัน ระบุขนาดตามช่องทาง และให้ QA ตรวจ`,
      tasks: [
        { id: "t1", agent: "strategist", title: "วัตถุประสงค์ & Key Message", instructions: "สรุปวัตถุประสงค์ insight และ key message 1 ประโยค", dependsOn: [] },
        { id: "t2", agent: "copywriter", title: "Copy บนชิ้นงาน", instructions: "headline 3 แบบ, sub, body, CTA", dependsOn: ["t1"] },
        { id: "t3", agent: "creative", title: "Visual Direction & Layout", instructions: "concept, สี, typography, layout wireframe, AI prompts", dependsOn: ["t1"] },
        { id: "t4", agent: "social", title: "ขนาดตามช่องทาง", instructions: "ขนาดและข้อกำหนดของแต่ละช่องทาง", dependsOn: [] },
        { id: "t5", agent: "qa", title: "ตรวจ Brief ก่อนส่งดีไซเนอร์", instructions: "ตรวจความถูกต้องและความครบถ้วน", dependsOn: ["t2", "t3", "t4"] },
      ],
    };
  }
  return {
    summary: `[DEMO] วางแผนแคมเปญจาก brief "${short}" — เริ่มจากกลยุทธ์และข้อมูลตลาด แล้วแตกเป็นคอนเทนต์ โฆษณา และแผนวัดผล ก่อนให้ QA ตรวจ`,
    tasks: [
      { id: "t1", agent: "researcher", title: "สรุปตลาดและกลุ่มเป้าหมาย", instructions: "สรุปอุตสาหกรรมเป้าหมายและ pain point", dependsOn: [] },
      { id: "t2", agent: "strategist", title: "Positioning & Key Message", instructions: "กำหนด big idea และ key message", dependsOn: ["t1"] },
      { id: "t3", agent: "copywriter", title: "Headline และแคปชัน", instructions: "เขียน headline 5 แบบ และแคปชัน 3 โพสต์", dependsOn: ["t2"] },
      { id: "t4", agent: "creative", title: "Design brief โปสเตอร์", instructions: "กำหนด layout สี และ prompt ภาพ", dependsOn: ["t2"] },
      { id: "t5", agent: "social", title: "Content calendar 2 สัปดาห์", instructions: "ตารางโพสต์รายช่องทาง", dependsOn: ["t3"] },
      { id: "t6", agent: "ads", title: "แผนโฆษณา LinkedIn + Meta", instructions: "targeting และงบ", dependsOn: ["t2"] },
      { id: "t7", agent: "analyst", title: "KPI และแผนวัดผล", instructions: "กำหนด KPI และ tracking", dependsOn: ["t6"] },
      { id: "t8", agent: "qa", title: "ตรวจงานทั้งหมด", instructions: "ตรวจความถูกต้องและความสอดคล้องกับแบรนด์", dependsOn: ["t3", "t4", "t5", "t6", "t7"] },
    ],
  };
}

const THOUGHTS: Partial<Record<AgentId, string>> = {
  researcher: "ดูว่าโรงงานกลุ่มไหนในไทยต้องใช้ gas detector มากที่สุด... EEC, ปิโตรเคมี, เซมิคอนดักเตอร์",
  strategist: "จุดแข็งคือ ATEX + SIL2 รายแรกของเกาหลี ต้องแปลงเป็นความมั่นใจของวิศวกร",
  copywriter: "อยากได้ headline ที่สั้นแต่หนักแน่น พูดถึงความปลอดภัยโดยไม่ขู่",
  creative: "แดง Gastron สำหรับจุดเตือน เขียวสำหรับความมั่นใจ ภาพสินค้าใหญ่ตรงกลาง",
  social: "Facebook 1:1 กับ 4:5, LinkedIn 1.91:1, Story 9:16",
  ads: "แบ่งงบ awareness 30 / consideration 50 / conversion 20",
  analyst: "ต้องมี UTM ทุกลิงก์ และนับ lead จากฟอร์มขอใบเสนอราคา",
  qa: "เช็คว่าไม่มีตัวเลขที่แต่งขึ้น และชื่อรุ่นสินค้าถูกต้อง",
  director: "รวมทุกส่วนให้เป็นเรื่องเดียวกัน แล้วสรุปสิ่งที่ต้องตัดสินใจ",
};

const DEMO_LAYOUT = `\`\`\`layout
{"title":"Poster A3 แนวตั้ง","ratio":"3:4","background":"#FFFFFF","zones":[
 {"label":"โลโก้ GASTRON","x":6,"y":4,"w":32,"h":7,"color":"#009143"},
 {"label":"Badge ส่วนลด 20%","x":70,"y":3,"w":24,"h":12,"color":"#D70010"},
 {"label":"Headline: ตรวจจับก่อน ปลอดภัยก่อน","x":6,"y":16,"w":88,"h":14,"color":"#D70010"},
 {"label":"ภาพสินค้า G-Finder Multi","x":12,"y":33,"w":76,"h":36,"color":"#93D0AF"},
 {"label":"จุดเด่น 3 ข้อ (ATEX / SIL2 / 35 ปี)","x":6,"y":71,"w":88,"h":10,"color":"#2B3A55"},
 {"label":"CTA + QR + ข้อมูลติดต่อ","x":6,"y":84,"w":88,"h":12,"color":"#009143"}
]}
\`\`\``;

const DEMO_GRAPHIC_BRIEF = `# Graphic Brief: โปสเตอร์ G-Finder Multi
*(DEMO output — ใส่ ANTHROPIC_API_KEY เพื่อให้ทีมคิดงานจริง)*

## 1. ข้อมูลงาน
| หัวข้อ | รายละเอียด |
|---|---|
| ชิ้นงาน | โปสเตอร์ A3 + โพสต์ Facebook 1:1 |
| ช่องทาง | บูธงานแสดงสินค้า, Facebook Page |
| ผู้ดู | วิศวกร Safety/HSE, ฝ่ายจัดซื้อโรงงาน |
| กำหนดส่ง | [ใส่ข้อมูล] |

## 2. วัตถุประสงค์
- **รู้:** G-Finder Multi ตรวจแก๊สได้หลายชนิดในเครื่องเดียว
- **รู้สึก:** มั่นใจในมาตรฐานระดับสากล
- **ทำ:** สแกน QR ขอใบเสนอราคา

## 3. กลุ่มเป้าหมาย & Insight
- วิศวกรต้องการอุปกรณ์ที่ "ผ่านมาตรฐาน" มากกว่าราคาถูก
- ฝ่ายจัดซื้อต้องการผู้ขายที่มีบริการหลังการขายในไทย

## 4. Key Message
ตรวจจับก่อน ปลอดภัยก่อน — มาตรฐาน ATEX & SIL2 ในเครื่องเดียว

## 5. Copy บนชิ้นงาน
| องค์ประกอบ | ข้อความ | หมายเหตุ |
|---|---|---|
| Headline | ตรวจจับก่อน ปลอดภัยก่อน | ตัวใหญ่สุด สีแดง |
| Sub-headline | เครื่องตรวจจับแก๊สแบบพกพา G-Finder Multi | |
| Body | ATEX · SIL2 · ประสบการณ์กว่า 30 ปี | ไอคอนนำหน้า |
| CTA | สแกนเพื่อขอใบเสนอราคา | คู่กับ QR |
| ข้อมูลบังคับ | โลโก้, www.gastronthailand.com, +66 89 497 3239 | |

Headline สำรอง: "ทุกลมหายใจในโรงงาน เราช่วยเฝ้าระวัง" / "แก๊สรั่ว รู้ก่อน 1 วินาที เปลี่ยนทุกอย่างได้"

## 6. Visual Direction
- **Concept:** "ผู้พิทักษ์ตัวเล็ก" — สินค้าใหญ่กลางภาพ แสงด้านหลังเหมือนเกราะป้องกัน
- **Mood & Tone:** สะอาด มั่นใจ เชิงวิศวกรรม
- **Typography:** หัวข้อ Kanit Bold / เนื้อหา IBM Plex Sans Thai

## 7. Color Palette
| สี | HEX | ใช้ตรงไหน |
|---|---|---|
| แดง Gastron | \`#D70010\` | Headline, badge |
| เขียว Gastron | \`#009143\` | CTA, โลโก้ |
| เขียวอ่อน | \`#93D0AF\` | พื้นหลังหลังสินค้า |
| กรมท่า | \`#2B3A55\` | ตัวอักษร body |

## 8. Layout
ลำดับสายตา: Headline → ภาพสินค้า → จุดเด่น → CTA/QR
${DEMO_LAYOUT}

## 9. ขนาด & Deliverables
| ชิ้นงาน | ขนาด | ไฟล์ส่งมอบ | หมายเหตุ |
|---|---|---|---|
| Poster A3 | 297 × 420 mm | PDF CMYK + bleed 3 mm | |
| Facebook Post | 1080 × 1080 px | PNG/JPG | |

## 10. AI Image Prompts
\`\`\`
Product hero shot of a yellow portable multi-gas detector on a clean white surface, soft green rim light, industrial plant blurred in background, photorealistic, studio lighting
\`\`\`

## 11. Do & Don't
- ✅ ใช้ภาพสินค้าจริง
- ❌ ห้ามใช้ภาพไฟไหม้/อุบัติเหตุรุนแรง

## 12. Checklist ก่อนส่งงาน
- [ ] โลโก้ถูกต้องตาม CI
- [ ] ชื่อรุ่นสะกดถูก
- [ ] QR สแกนได้
`;

const DEMO_CHAT: Partial<Record<AgentId, string[]>> = {
  director: [
    "ทุกคนครับ/ค่ะ วันนี้เราทำโพสต์ Facebook 1 โพสต์ ต้องได้ header บนภาพ เนื้อหา layout ให้กราฟิก แล้วก็แคปชัน คุณ Nina ช่วยเริ่มจากเป้าหมายและ key message ก่อนนะ",
    "โอเค ผมสรุปว่าเราจะใช้ header ที่สั้นและแคปชันที่เล่าต่อ เดี๋ยวผมรวมเป็น brief ให้กราฟิกเลย ใครมีอะไรค้างบอกได้",
  ],
  strategist: ["เป้าหมายคือให้วิศวกร Safety รู้ว่ามีเครื่องตรวจจับที่รับรอง ATEX และอยากทักมาถามราคา key message: \"ตรวจจับก่อน ปลอดภัยก่อน\" คุณ Fah ช่วยดูรูปแบบโพสต์หน่อยนะ"],
  social: ["Facebook แนะนำภาพ 4:5 จะกินพื้นที่ในฟีดมากกว่า 1:1 ข้อความบนภาพไม่ควรเกิน 20% ที่เหลือไปอยู่ในแคปชัน และถ้าโพสต์นี้ไปได้ดี เราทำเป็นซีรีส์ 3 โพสต์ต่อได้เลย คุณ Ploy ลองเสนอ header ได้เลย"],
  copywriter: [
    "header ที่ลองได้: \"ก๊าซรั่ว ไม่ต้องรอให้รู้สึก\" หรือ \"เห็นก่อน ปลอดภัยก่อน\" ส่วน CTA คือ \"ขอใบเสนอราคา\" คุณ Mook ช่วยดูว่าวางบนภาพได้ไหม",
    "แคปชันร่างแรก: \"ความปลอดภัยเริ่มก่อนสัญญาณเตือน — G-Finder Multi ตรวจจับได้หลายชนิดในเครื่องเดียว ทักมาขอข้อมูลได้เลย\" แล้วปิดด้วย hashtag #Gastron #GasDetection",
    "รับข้อติของคุณ Pim ค่ะ จะเปลี่ยนคำว่า \"ดีที่สุด\" เป็นข้อเท็จจริงที่ตรวจสอบได้ และใส่ [ใส่ข้อมูล] ตรงรุ่นสินค้า",
  ],
  creative: [
    "layout แนะนำ: โลโก้มุมซ้ายบน header ใหญ่สีแดง `#D70010` ใต้โลโก้ ภาพสินค้ากลางภาพ แล้ว CTA แถบเขียว `#009143` ด้านล่าง สายตาจะไหลจากบนลงล่างตามนี้",
    "ปรับตามคุณ Ploy: header ยาวขึ้นนิดเดียวก็ยังพอดี ถ้าทำเป็นสองบรรทัด ผมเพิ่มพื้นที่ header เป็น 20% ของภาพ",
  ],
  content: ["มุมแคปชันที่เล่าเรื่องน่าสนใจ: เปิดด้วยสถานการณ์หน้างานสั้น ๆ แล้วค่อยเฉลยว่าเครื่องช่วยอะไร คุณ Ploy เอาไปปรับกับ header ได้"],
  qa: ["ข้อสังเกต 3 ข้อ: 1) อย่าใช้คำว่า \"ดีที่สุด\" ถ้าไม่มีหลักฐาน 2) ชื่อรุ่นสินค้าต้องตรงกับแคตตาล็อก 3) header กับแคปชันต้องเล่าเรื่องเดียวกัน ตอนนี้ยังสอดคล้องดี"],
};

const DEMO_FB_BRIEF = `# Facebook Post Brief: ตรวจจับก่อน ปลอดภัยก่อน
*(DEMO output — ใส่ ANTHROPIC_API_KEY เพื่อให้ทีมคุยและเขียนงานจริง)*

## 1. ข้อมูลโพสต์
| หัวข้อ | รายละเอียด |
|---|---|
| ช่องทาง | Facebook Page Gastron Thailand |
| รูปแบบ | ภาพเดี่ยว |
| ขนาดภาพ | 1080 x 1350 px (4:5) |
| กำหนดโพสต์ | [ใส่ข้อมูล] |

## 2. วัตถุประสงค์ & Key Message
- รู้: Gastron มีเครื่องตรวจจับแก๊สที่รับรองมาตรฐาน
- ทำ: ทักมาขอใบเสนอราคา
- Key message: "ตรวจจับก่อน ปลอดภัยก่อน"

## 3. ข้อความบน Artwork (Copy Deck)
| # | ตำแหน่ง | ข้อความที่ขึ้นบนภาพ (คำต่อคำ) | ขนาด |
|---|---|---|---|
| 2 | Header | ก๊าซรั่ว ไม่ต้องรอให้รู้สึก | ใหญ่สุด หนา |
| 4 | Sub-header | G-Finder Multi ตรวจจับหลายชนิดในเครื่องเดียว | กลาง |
| 5 | CTA | ขอใบเสนอราคา | กลาง หนา |

Header สำรอง: "เห็นก่อน ปลอดภัยก่อน", "ทุกกะ ปลอดภัยทุกคน"

## 4. Layout สำหรับกราฟิก
สายตาไหลจากโลโก้ → header → ภาพสินค้า → CTA

\`\`\`layout
{"title":"Facebook Post 4:5","ratio":"4:5","background":"#FFFFFF","zones":[
 {"label":"โลโก้ GASTRON","x":6,"y":4,"w":30,"h":6,"color":"#009143"},
 {"label":"Header","text":"ก๊าซรั่ว ไม่ต้องรอให้รู้สึก","x":6,"y":13,"w":88,"h":20,"color":"#D70010"},
 {"label":"ภาพสินค้า G-Finder Multi","x":10,"y":36,"w":80,"h":40,"color":"#93D0AF"},
 {"label":"Sub-header","text":"G-Finder Multi ตรวจจับหลายชนิดในเครื่องเดียว","x":6,"y":78,"w":88,"h":7,"color":"#26324f"},
 {"label":"CTA","text":"ขอใบเสนอราคา","x":6,"y":87,"w":88,"h":9,"color":"#009143"}
]}
\`\`\`

## 5. Visual Direction
ภาพสินค้าคมชัดบนพื้นสว่าง โทนมืออาชีพ | สีหลัก \`#D70010\` \`#009143\` \`#26324F\`

## 6. แคปชัน Facebook
**หลัก:** ความปลอดภัยเริ่มก่อนสัญญาณเตือน — G-Finder Multi ตรวจจับได้หลายชนิดในเครื่องเดียว ทักมาขอข้อมูลได้เลย [ใส่ลิงก์]

**สั้น:** ตรวจจับก่อน ปลอดภัยก่อน ทักมาคุยกับเรา

#Gastron #GasDetection

## 7. แคมเปญเล็ก ๆ ต่อเนื่อง
1. โพสต์ที่ 2: ตัวอย่างสถานการณ์หน้างาน
2. โพสต์ที่ 3: มาตรฐาน ATEX อธิบายง่าย ๆ
3. โพสต์ที่ 4: ถาม-ตอบกับวิศวกร

## 8. สิ่งที่ยังต้องตัดสินใจ / เติมข้อมูล
- วันที่โพสต์, ลิงก์, รุ่นสินค้าที่ใช้ในภาพ

## 9. Checklist ก่อนส่งกราฟิก
- [ ] ขนาด 1080x1350
- [ ] โลโก้ถูกต้อง
- [ ] ข้อความบนภาพไม่เกิน 20%
`;

export function demoChat(req: AgentRequest) {
  const lines = DEMO_CHAT[req.agentId] ?? ["ขอเสริมนิดนึง ตามที่คุยกันมาถือว่าไปในทางเดียวกันแล้ว"];
  const n = (req.transcript ?? []).filter((l) => l.agent === req.agentId).length;
  return lines[Math.min(n, lines.length - 1)];
}

export function demoOutput(req: AgentRequest) {
  if (req.mode === "chat") return { thought: "", text: demoChat(req) };
  if (req.kind === "facebook" && req.mode === "compile") return { thought: THOUGHTS.director ?? "", text: DEMO_FB_BRIEF };
  const a = { ...AGENT_BY_ID[req.agentId], name: req.names?.[req.agentId] || AGENT_BY_ID[req.agentId].name };
  const thought = THOUGHTS[req.agentId] ?? "กำลังคิดว่าจะเริ่มจากตรงไหน";
  if (req.kind === "graphic" && req.mode === "compile") return { thought, text: DEMO_GRAPHIC_BRIEF };
  const title = req.mode === "compile" ? "Deliverable สุดท้าย" : req.task.title;
  const extra = req.kind === "graphic" && req.agentId === "creative" ? `\n### Layout\n${DEMO_LAYOUT}\n` : "";
  const text = `## ${title}
*(DEMO output — ใส่ ANTHROPIC_API_KEY เพื่อให้ ${a.name} คิดงานจริง)*

**${a.name} — ${a.role}**

- ประเด็นที่ 1: ต่อยอดจาก brief "${req.brief.slice(0, 40)}…"
- ประเด็นที่ 2: เชื่อมกับงานของเพื่อน ${req.inputs.map((i) => i.agentName).join(", ") || "(ไม่มี)"}
- ประเด็นที่ 3: ปรับให้เข้ากับโทนแบรนด์ Gastron — สีหลัก \`#D70010\` และ \`#009143\`

| หัวข้อ | รายละเอียด |
|---|---|
| กลุ่มเป้าหมาย | วิศวกร Safety/HSE โรงงานอุตสาหกรรม |
| ช่องทาง | LinkedIn, Facebook, LINE OA |
| ข้อความหลัก | "ตรวจจับก่อน ปลอดภัยก่อน" |
${extra}`;
  return { thought, text };
}
