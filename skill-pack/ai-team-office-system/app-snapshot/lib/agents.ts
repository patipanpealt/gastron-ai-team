export type AgentId =
  | "director"
  | "strategist"
  | "researcher"
  | "copywriter"
  | "content"
  | "creative"
  | "social"
  | "ads"
  | "seo"
  | "analyst"
  | "qa";

export type RunKind = "graphic" | "campaign" | "facebook";

export type Team = "lead" | "creative" | "growth" | "data";

export interface Agent {
  id: AgentId;
  name: string;
  role: string;
  roleTh: string;
  team: Team;
  /** Pixel palette for the sprite. */
  look: {
    hair: string;
    skin: string;
    shirt: string;
    pants: string;
    hairStyle: "short" | "long" | "bun" | "spiky" | "cap";
    outfit: "suit" | "shirt" | "hoodie" | "sweater" | "blouse";
    accessory?: "glasses" | "headphones" | "beret";
  };
  /** What this agent is for — shown in the roster and fed to the Director when planning. */
  skills: string;
  persona: string;
}

export const AGENTS: Agent[] = [
  {
    id: "director",
    name: "Max",
    role: "Marketing Director",
    roleTh: "ผู้อำนวยการการตลาด",
    team: "lead",
    look: { hair: "#2b1d16", skin: "#f1c27d", shirt: "#26324f", pants: "#1d2333", hairStyle: "short", outfit: "suit" },
    skills: "หัวหน้าทีม: รับ brief, แตกงาน, มอบหมาย, รวมงานเป็น deliverable สุดท้าย",
    persona:
      "คุณคือ Marketing Director ที่มีประสบการณ์การตลาด B2B อุตสาหกรรม 15 ปี คิดเป็นระบบ ตัดสินใจชัด สรุปเก่ง",
  },
  {
    id: "strategist",
    name: "Nina",
    role: "Brand Strategist",
    roleTh: "นักวางกลยุทธ์แบรนด์",
    team: "lead",
    look: { hair: "#8a3b1e", skin: "#f3c9a0", shirt: "#8e44ad", pants: "#2d2a3a", hairStyle: "long", outfit: "blouse" },
    skills: "positioning, key message, กลุ่มเป้าหมาย/persona, big idea ของแคมเปญ, objectives & KPI",
    persona:
      "คุณคือ Brand Strategist ถนัด positioning แบรนด์อุตสาหกรรม แปลงจุดแข็งทางเทคนิคเป็นคุณค่าที่ลูกค้าเข้าใจ",
  },
  {
    id: "researcher",
    name: "Ken",
    role: "Market Researcher",
    roleTh: "นักวิจัยตลาด",
    team: "lead",
    look: { hair: "#1d1d1d", skin: "#d9a066", shirt: "#16a085", pants: "#33302b", hairStyle: "spiky", outfit: "shirt", accessory: "glasses" },
    skills: "วิเคราะห์ตลาด/อุตสาหกรรมเป้าหมายในไทย, คู่แข่ง, pain point ลูกค้า, กฎหมาย/มาตรฐานความปลอดภัยที่เกี่ยวข้อง",
    persona:
      "คุณคือ Market Researcher ที่รู้จักอุตสาหกรรมไทย (ปิโตรเคมี, EEC, เซมิคอนดักเตอร์, โรงไฟฟ้า) ระบุสมมติฐานชัดเจนเมื่อไม่มีข้อมูลจริง",
  },
  {
    id: "copywriter",
    name: "Ploy",
    role: "Copywriter",
    roleTh: "นักเขียนคำโฆษณา",
    team: "creative",
    look: { hair: "#e0a526", skin: "#f3c9a0", shirt: "#e74c3c", pants: "#3a2f2f", hairStyle: "bun", outfit: "sweater" },
    skills: "headline, tagline, body copy, แคปชัน, CTA, ข้อความบนโปสเตอร์/ใบปลิว, อีเมล",
    persona:
      "คุณคือ Copywriter สายคมคาย เขียนภาษาไทยสั้น กระชับ จำง่าย แต่ยังน่าเชื่อถือสำหรับกลุ่มวิศวกร",
  },
  {
    id: "content",
    name: "Beam",
    role: "Content Creator",
    roleTh: "ครีเอเตอร์คอนเทนต์",
    team: "creative",
    look: { hair: "#5b3a29", skin: "#c68642", shirt: "#f39c12", pants: "#2b3a4a", hairStyle: "short", outfit: "hoodie", accessory: "headphones" },
    skills: "บทความ, สคริปต์วิดีโอสั้น/Reels/TikTok, คอนเทนต์ให้ความรู้, carousel, case study",
    persona:
      "คุณคือ Content Creator ที่ทำเรื่องเทคนิคให้สนุกและเข้าใจง่าย เล่าเรื่องเป็นฉาก ๆ เก่ง",
  },
  {
    id: "creative",
    name: "Mook",
    role: "Creative Director",
    roleTh: "ครีเอทีฟไดเรกเตอร์",
    team: "creative",
    look: { hair: "#ff6fb5", skin: "#f1c27d", shirt: "#1abc9c", pants: "#2c2c2c", hairStyle: "long", outfit: "sweater", accessory: "beret" },
    skills: "art direction, mood & tone, design brief สำหรับกราฟิก/โปสเตอร์/บูธ, prompt สำหรับ AI สร้างภาพ, storyboard",
    persona:
      "คุณคือ Creative Director คิดภาพเป็นฉาก ระบุ layout สี ตัวอักษร และองค์ประกอบได้ละเอียดพอให้ดีไซเนอร์ทำต่อได้ทันที",
  },
  {
    id: "social",
    name: "Fah",
    role: "Social Media Manager",
    roleTh: "ผู้จัดการโซเชียลมีเดีย",
    team: "growth",
    look: { hair: "#2c1b10", skin: "#e0ac69", shirt: "#3498db", pants: "#283040", hairStyle: "bun", outfit: "blouse" },
    skills: "content calendar, แผนโพสต์รายช่องทาง (Facebook, LinkedIn, LINE OA, TikTok, YouTube), community",
    persona:
      "คุณคือ Social Media Manager ที่วางแผนโพสต์เป็นตาราง ชัดเจนว่าโพสต์อะไร ช่องทางไหน วันไหน เพื่ออะไร",
  },
  {
    id: "ads",
    name: "Tom",
    role: "Performance Ads Specialist",
    roleTh: "ผู้เชี่ยวชาญโฆษณาออนไลน์",
    team: "growth",
    look: { hair: "#4a3020", skin: "#f5d0a9", shirt: "#27ae60", pants: "#2e2e38", hairStyle: "short", outfit: "shirt" },
    skills: "แผนโฆษณา Meta/Google/LinkedIn, targeting, งบประมาณ, ad copy variations, funnel, A/B test",
    persona:
      "คุณคือ Performance Marketer ที่คิดเป็นตัวเลข แบ่งงบตาม funnel และอธิบายเหตุผลการตั้งค่าแคมเปญได้",
  },
  {
    id: "seo",
    name: "Earth",
    role: "SEO Specialist",
    roleTh: "ผู้เชี่ยวชาญ SEO",
    team: "growth",
    look: { hair: "#111111", skin: "#c68642", shirt: "#7f8c8d", pants: "#2a2a2a", hairStyle: "spiky", outfit: "hoodie", accessory: "glasses" },
    skills: "keyword research (ไทย/อังกฤษ), โครงบทความ SEO, meta title/description, โครงสร้างเว็บ, landing page",
    persona:
      "คุณคือ SEO Specialist สาย B2B ที่รู้ว่าวิศวกรค้นหาอะไรใน Google และจัดโครงหน้าเว็บให้ทั้งคนและ search engine อ่านง่าย",
  },
  {
    id: "analyst",
    name: "June",
    role: "Data Analyst",
    roleTh: "นักวิเคราะห์ข้อมูล",
    team: "data",
    look: { hair: "#6d4c41", skin: "#f1c27d", shirt: "#34495e", pants: "#1f2630", hairStyle: "long", outfit: "sweater", accessory: "glasses" },
    skills: "กำหนด KPI, แผนวัดผล, tracking (UTM, pixel, conversion), dashboard, ตีความผลแคมเปญ",
    persona:
      "คุณคือ Data Analyst ที่ทำให้ทุกแคมเปญวัดผลได้ ระบุ metric, เป้าหมาย, วิธีเก็บข้อมูล และวิธีอ่านผล",
  },
  {
    id: "qa",
    name: "Pim",
    role: "QA & Brand Reviewer",
    roleTh: "ผู้ตรวจคุณภาพและแบรนด์",
    team: "data",
    look: { hair: "#3e2723", skin: "#e8b48a", shirt: "#d35400", pants: "#2b2b2b", hairStyle: "cap", outfit: "shirt", accessory: "headphones" },
    skills: "ตรวจความถูกต้อง ความสอดคล้องกับแบรนด์ ข้อกล่าวอ้างเกินจริง คำผิด และความครบถ้วนของงานก่อนส่ง",
    persona:
      "คุณคือ QA & Brand Reviewer ที่ละเอียดมาก ตรงไปตรงมา ชี้ปัญหาพร้อมข้อเสนอแก้ไขที่ทำได้ทันที",
  },
];

export const AGENT_BY_ID = Object.fromEntries(AGENTS.map((a) => [a.id, a])) as Record<AgentId, Agent>;

export const WORKER_IDS = AGENTS.filter((a) => a.id !== "director").map((a) => a.id);

export const TEAM_LABEL: Record<Team, string> = {
  lead: "Strategy & Lead",
  creative: "Content & Creative",
  growth: "Social & Ads",
  data: "Data & Review",
};

export interface PlanTask {
  id: string;
  agent: AgentId;
  title: string;
  instructions: string;
  dependsOn: string[];
}

export interface Plan {
  summary: string;
  tasks: PlanTask[];
}
