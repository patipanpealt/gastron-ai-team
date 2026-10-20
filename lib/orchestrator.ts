import { AGENT_BY_ID, AGENTS, type AgentId, type Plan, type PlanTask, type RunKind } from "./agents";
import type { OfficeEngine } from "./office/engine";
import { memoryFor } from "./memory";
import { uid } from "./uid";
import { getSettings, nameOf } from "./office/store";
import type { AgentRequest, ChatLine, TaskInput } from "./prompts";

export type TaskStatus = "waiting" | "working" | "done" | "error";

export interface TaskState extends PlanTask {
  status: TaskStatus;
  thinking: string;
  output: string;
  error?: string;
  startedAt?: number;
  endedAt?: number;
}

export interface FeedItem {
  t: number;
  agent: AgentId;
  text: string;
  kind: "info" | "assign" | "start" | "done" | "handoff" | "error";
}

export type Phase = "planning" | "discussing" | "kickoff" | "working" | "compiling" | "done" | "error" | "stopped";

export interface RunState {
  id: string;
  kind: RunKind;
  brief: string;
  createdAt: number;
  phase: Phase;
  summary?: string;
  tasks: TaskState[];
  final: { status: "pending" | "working" | "done" | "error"; thinking: string; output: string };
  feed: FeedItem[];
  /** The team's conversation (Facebook post runs). */
  chat?: ChatLine[];
  error?: string;
  demo?: boolean;
}

/** The names the user gave the team, sent along so the AI calls everyone by them. */
const teamNames = () => Object.fromEntries(Object.entries(getSettings().profiles).map(([id, p]) => [id, p.name]));

/** The order of the conversation: who speaks, and what they are there to contribute. */
const FB_SCRIPT: { agent: AgentId; goal: string }[] = [
  { agent: "director", goal: "เปิดประชุม: สรุป brief 1–2 ประโยค บอกสิ่งที่ต้องได้ (header บนภาพ, เนื้อหา, layout ให้กราฟิก, แคปชัน, แคมเปญเล็ก ๆ) แล้วเชิญนักวางกลยุทธ์เริ่ม" },
  { agent: "strategist", goal: "เสนอวัตถุประสงค์ของโพสต์ กลุ่มเป้าหมาย และ key message 1 ประโยค แล้วส่งต่อให้ผู้จัดการโซเชียล" },
  { agent: "social", goal: "เสนอรูปแบบโพสต์ Facebook (ขนาดภาพ, อะไรควรอยู่บนภาพ อะไรควรอยู่ในแคปชัน, เวลาโพสต์) และไอเดียแคมเปญเล็ก ๆ ที่ต่อเนื่องจากโพสต์นี้" },
  { agent: "copywriter", goal: "เสนอ Header บนภาพ 3 แบบ (ข้อความจริง) พร้อมข้อความทุกบรรทัดที่จะขึ้นบนภาพ (sub-header, body, CTA, ข้อมูลบังคับ) เป็นคำต่อคำ ตอบสนองสิ่งที่เพื่อนเสนอมา" },
  { agent: "creative", goal: "เสนอ layout ของภาพ: วางอะไรตรงไหน ลำดับสายตา ภาพหลัก สี (HEX) ตอบรับ header ของนักเขียน และถามถ้าต้องการข้อมูลเพิ่ม" },
  { agent: "content", goal: "เสนอมุมเล่าเรื่องสำหรับแคปชัน (ประโยคเปิด, อารมณ์, ความยาว) ให้เข้ากับ header และภาพ" },
  { agent: "copywriter", goal: "ร่างแคปชัน Facebook พร้อมใช้ (ยาว 1 แบบ สั้น 1 แบบ) พร้อม hashtag และปรับ header ตามที่ทีมคุยกัน" },
  { agent: "creative", goal: "ยืนยัน/ปรับ layout ให้เข้ากับ header และแคปชันล่าสุด บอกว่าข้อความแต่ละบรรทัดวางที่โซนไหน ขนาดตัวอักษรหรือสัดส่วนที่กราฟิกควรใช้" },
  { agent: "qa", goal: "ตรวจ header, เนื้อหา, layout และแคปชัน: ข้อกล่าวอ้างเกินจริง, ข้อมูลที่ต้องเติม, ความสอดคล้องกัน ชี้ 2–3 ข้อที่ต้องแก้ พร้อมวิธีแก้" },
  { agent: "copywriter", goal: "รับข้อติของฝ่ายตรวจแล้วบอกว่าจะแก้ข้อความตรงไหน (ยกข้อความที่แก้แล้วมาเลย)" },
  { agent: "director", goal: "สรุปสิ่งที่ทีมตกลงกัน (header, แคปชัน, layout, แคมเปญเล็ก ๆ) และบอกว่าจะรวมเป็น brief ให้กราฟิก" },
];

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const tail = (s: string, n = 60) => s.replace(/\s+/g, " ").slice(-n);

export class Orchestrator {
  run: RunState;
  private abort = new AbortController();

  constructor(
    brief: string,
    kind: RunKind,
    private office: OfficeEngine,
    private onChange: (run: RunState) => void,
  ) {
    this.run = {
      id: uid(),
      kind,
      brief,
      createdAt: Date.now(),
      phase: "planning",
      tasks: [],
      final: { status: "pending", thinking: "", output: "" },
      feed: [],
      chat: [],
    };
  }

  stop() {
    this.abort.abort();
    this.run.phase = "stopped";
    for (const a of AGENTS) {
      this.office.setWorking(a.id, false);
      this.office.setBusy(a.id, false);
      this.office.setBubble(a.id, null);
    }
    this.emit();
  }

  private emit() {
    this.onChange({ ...this.run, tasks: this.run.tasks.map((t) => ({ ...t })), feed: [...this.run.feed], chat: this.run.chat?.map((c) => ({ ...c })) });
  }

  private log(agent: AgentId, text: string, kind: FeedItem["kind"] = "info") {
    this.run.feed.push({ t: Date.now(), agent, text, kind });
    this.emit();
  }

  private get stopped() {
    return this.abort.signal.aborted;
  }

  /** The person running the office chips in: the team reads it on their next turn. */
  say(text: string) {
    const t = text.trim();
    if (!t || this.run.kind !== "facebook") return;
    this.run.chat!.push({ agent: "user", name: "คุณ", role: "ผู้สั่งงาน", text: t.slice(0, 1000) });
    this.emit();
  }

  async start() {
    try {
      if (this.run.kind === "facebook") {
        await this.discuss();
        if (this.stopped) return;
        await this.compileFacebook();
        return;
      }
      await this.kickoff();
      if (this.stopped) return;
      await this.work();
      if (this.stopped) return;
      await this.compile();
    } catch (err) {
      if (this.stopped) return;
      this.run.phase = "error";
      this.run.error = err instanceof Error ? err.message : String(err);
      this.office.setBubble("director", "😵 มีปัญหา: " + this.run.error, "error");
      this.log("director", `เกิดข้อผิดพลาด: ${this.run.error}`, "error");
    }
  }

  // Facebook post: the team talks it through, turn by turn, then the director writes it up.
  private async discuss() {
    const o = this.office;
    const cast = [...new Set(FB_SCRIPT.map((s) => s.agent))];
    this.run.phase = "discussing";
    for (const id of cast) o.setBusy(id, true);
    this.log("director", "เรียกทีมเข้าห้องประชุมคุยโพสต์ Facebook", "info");
    this.emit();
    void o.gather(cast);
    await sleep(3500);
    let prev: AgentId | null = null;
    for (const step of FB_SCRIPT) {
      if (this.stopped) return;
      const me = AGENT_BY_ID[step.agent];
      const msg: ChatLine = { agent: step.agent, name: nameOf(step.agent), role: me.role, text: "" };
      this.run.chat!.push(msg);
      if (prev && prev !== step.agent) o.link(prev, step.agent, "REPLY", 2200);
      o.setBubble(step.agent, "💭 …", "think");
      this.emit();
      await this.stream(
        {
          agentId: step.agent,
          kind: "facebook",
          mode: "chat",
          brief: this.run.brief,
          task: { title: "", instructions: "" },
          inputs: [],
          // everything said so far (including the person's own messages), but not this empty turn
          transcript: this.run.chat!.slice(0, -1).map((c) => ({ ...c })),
          turnGoal: step.goal,
        },
        (kind, text) => {
          if (kind !== "text") return;
          msg.text += text;
          o.setBubble(step.agent, "💬 " + tail(msg.text, 90), "talk");
        },
      );
      msg.text = msg.text.trim();
      o.setBubble(step.agent, "💬 " + tail(msg.text, 90), "talk", 4000);
      this.log(step.agent, msg.text.slice(0, 140) + (msg.text.length > 140 ? "…" : ""), "info");
      prev = step.agent;
      await sleep(900);
    }
  }

  private async compileFacebook() {
    const o = this.office;
    this.run.phase = "compiling";
    this.run.final.status = "working";
    this.emit();
    this.log("director", "สรุปบทสนทนาเป็น Facebook Post Brief", "start");
    o.setWorking("director", true);
    o.setBubble("director", "📝 สรุปเป็น brief ให้กราฟิก…", "think");
    const f = this.run.final;
    await this.stream(
      {
        agentId: "director",
        kind: "facebook",
        mode: "compile",
        brief: this.run.brief,
        task: { title: "Facebook Post Brief", instructions: "" },
        inputs: [],
        transcript: this.run.chat!.map((c) => ({ ...c })),
      },
      (kind, text) => {
        if (kind === "thinking") {
          f.thinking += text;
          o.setBubble("director", "💭 " + tail(f.thinking), "think");
        } else {
          f.output += text;
          o.setBubble("director", "⌨️ " + tail(f.output), "work");
        }
      },
    );
    f.status = "done";
    this.run.phase = "done";
    o.setWorking("director", false);
    this.log("director", "Facebook Post Brief เสร็จแล้ว 🎉", "done");
    const cast = new Set(FB_SCRIPT.map((s) => s.agent));
    for (const id of cast) {
      o.setBusy(id, false);
      void o.goToDesk(id);
      o.setBubble(id, id === "director" ? "🎉 เสร็จแล้ว! เยี่ยมมากทีม" : "🎉", id === "director" ? "done" : "talk", 5000);
    }
    this.emit();
  }

  // 1. Everyone gathers while the director plans.
  private async kickoff() {
    const o = this.office;
    for (const a of AGENTS) o.setBusy(a.id, true);
    this.log("director", "ได้รับ brief ใหม่ — เรียกทุกคนเข้าห้องประชุม", "info");
    o.setBubble("director", "📣 ทุกคนเข้าประชุมด่วน!", "talk");
    void o.gather(AGENTS.map((a) => a.id));
    await sleep(1200);
    o.setBubble("director", "💭 กำลังอ่าน brief และวางแผน…", "think");

    const res = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief: this.run.brief, kind: this.run.kind, names: teamNames() }),
      signal: this.abort.signal,
    });
    const data = (await res.json()) as { plan?: Plan; error?: string; demo?: boolean };
    if (!res.ok || !data.plan) throw new Error(data.error || `วางแผนไม่สำเร็จ (${res.status})`);

    this.run.demo = data.demo;
    this.run.summary = data.plan.summary;
    this.run.tasks = data.plan.tasks.map((t) => ({ ...t, status: "waiting", thinking: "", output: "" }));
    this.run.phase = "kickoff";
    this.log("director", `แผนงาน: ${data.plan.summary}`, "info");
    o.setBubble("director", "🗂️ " + data.plan.summary, "talk");

    for (const t of this.run.tasks) {
      if (this.stopped) return;
      const a = AGENT_BY_ID[t.agent];
      o.setBubble("director", `👉 ${nameOf(a.id)}: ${t.title}`, "talk");
      o.link("director", t.agent, "ASSIGN TASK", 950);
      o.setBubble(t.agent, "🙋 รับทราบครับ/ค่ะ!", "talk", 1800);
      this.log(t.agent, `ได้รับมอบหมาย: ${t.title}`, "assign");
      await sleep(900);
    }
    o.setBubble("director", "💪 ลุยกันเลย!", "talk", 2500);
    await sleep(800);

    const assigned = new Set(this.run.tasks.map((t) => t.agent));
    for (const a of AGENTS) {
      void o.goToDesk(a.id);
      if (a.id !== "director" && !assigned.has(a.id)) {
        o.setBusy(a.id, false);
        o.setBubble(a.id, "☺️ รอบนี้ยังไม่มีงาน", "wait", 3000);
      }
    }
    await sleep(2500);
  }

  // 2. Run tasks as their dependencies finish, in parallel where possible.
  private async work() {
    this.run.phase = "working";
    this.emit();
    for (const t of this.run.tasks) {
      if (t.dependsOn.length) this.office.setBubble(t.agent, "⏳ รองานจากเพื่อน", "wait");
    }
    this.office.setBubble("director", "👀 ติดตามงานทีม", "talk", 4000);
    const running = new Map<string, Promise<void>>();
    while (!this.stopped) {
      const pending = this.run.tasks.filter((t) => t.status === "waiting");
      if (!pending.length && !running.size) break;
      for (const t of pending) {
        if (running.has(t.id)) continue;
        // one agent works on one task at a time
        const agentBusy = this.run.tasks.some((o) => o.agent === t.agent && o.status === "working");
        const ready = t.dependsOn.every((d) => {
          const dep = this.run.tasks.find((x) => x.id === d);
          return !dep || dep.status === "done" || dep.status === "error";
        });
        if (ready && !agentBusy) {
          t.status = "working";
          running.set(t.id, this.runTask(t).finally(() => running.delete(t.id)));
        }
      }
      if (running.size) await Promise.race(running.values());
      else await sleep(200);
    }
  }

  private async runTask(t: TaskState) {
    const o = this.office;
    const me = AGENT_BY_ID[t.agent];
    t.startedAt = Date.now();
    this.emit();

    const deps = t.dependsOn
      .map((d) => this.run.tasks.find((x) => x.id === d))
      .filter((x): x is TaskState => !!x);
    const senders = [...new Set(deps.map((d) => d.agent))].filter((id) => id !== t.agent);
    if (senders.length) {
      o.setBubble(t.agent, "📥 รับงานต่อจากเพื่อน", "talk");
      for (const s of senders) {
        this.log(s, `ส่งงานต่อให้ ${nameOf(me.id)}`, "handoff");
        o.link(s, t.agent, t.agent === "qa" ? "REVIEW" : "HANDOFF", 3000);
      }
      await Promise.all(senders.map((s, i) => sleep(i * 250).then(() => o.sendDoc(s, t.agent))));
    }
    await o.goToDesk(t.agent);
    this.log(t.agent, `เริ่มทำ: ${t.title}`, "start");
    o.setWorking(t.agent, true);
    o.setBubble(t.agent, "💭 กำลังคิด…", "think");

    const inputs: TaskInput[] = deps
      .filter((d) => d.status === "done")
      .map((d) => ({ agentName: nameOf(d.agent), role: AGENT_BY_ID[d.agent].role, title: d.title, output: d.output }));

    try {
      await this.stream(
        { agentId: t.agent, kind: this.run.kind, mode: "task", brief: this.run.brief, task: { title: t.title, instructions: t.instructions }, inputs },
        (kind, text) => {
          if (kind === "thinking") {
            t.thinking += text;
            o.setBubble(t.agent, "💭 " + tail(t.thinking), "think");
          } else {
            t.output += text;
            o.setBubble(t.agent, "⌨️ " + tail(t.output), "work");
          }
        },
      );
      t.status = "done";
      t.endedAt = Date.now();
      this.log(t.agent, `ส่งงานแล้ว: ${t.title}`, "done");
      o.setWorking(t.agent, false);
      o.setBubble(t.agent, "✅ เสร็จแล้ว!", "done", 3000);
      this.emit();
      // walk the result over to the director, then head back
      void (async () => {
        await o.visit(t.agent, "director");
        if (this.stopped) return;
        o.setBubble(t.agent, `📄 ส่ง "${t.title}"`, "talk", 2200);
        o.link(t.agent, "director", "SUBMIT", 2200);
        o.setBubble("director", "👍 ขอบคุณ!", "talk", 1800);
        await sleep(2200);
        await o.goToDesk(t.agent);
        const more = this.run.tasks.some((x) => x.agent === t.agent && x.status !== "done" && x.status !== "error");
        if (!more) o.setBusy(t.agent, false);
      })();
    } catch (err) {
      if (this.stopped) return;
      t.status = "error";
      t.error = err instanceof Error ? err.message : String(err);
      t.endedAt = Date.now();
      o.setWorking(t.agent, false);
      o.setBubble(t.agent, "😵 " + t.error, "error", 6000);
      this.log(t.agent, `งานผิดพลาด: ${t.error}`, "error");
    }
  }

  // 3. Director compiles everything into one deliverable.
  private async compile() {
    const o = this.office;
    this.run.phase = "compiling";
    this.run.final.status = "working";
    this.emit();
    const done = this.run.tasks.filter((t) => t.status === "done");
    await o.goToDesk("director");
    o.setBubble("director", "📚 รวบรวมงานทุกคน", "talk");
    await Promise.all(
      [...new Set(done.map((t) => t.agent))].map((id, i) =>
        sleep(i * 200).then(() => {
          o.link(id, "director", "COMPILE", 2400);
          return o.sendDoc(id, "director", 1300);
        }),
      ),
    );
    this.log("director", "เริ่มรวมงานเป็น Deliverable สุดท้าย", "start");
    o.setWorking("director", true);
    o.setBubble("director", "💭 เรียบเรียงทั้งหมด…", "think");
    const f = this.run.final;
    await this.stream(
      {
        agentId: "director",
        kind: this.run.kind,
        mode: "compile",
        brief: this.run.brief,
        task: { title: "Deliverable สุดท้าย", instructions: "" },
        inputs: done.map((d) => ({ agentName: nameOf(d.agent), role: AGENT_BY_ID[d.agent].role, title: d.title, output: d.output })),
      },
      (kind, text) => {
        if (kind === "thinking") {
          f.thinking += text;
          o.setBubble("director", "💭 " + tail(f.thinking), "think");
        } else {
          f.output += text;
          o.setBubble("director", "⌨️ " + tail(f.output), "work");
        }
      },
    );
    f.status = "done";
    this.run.phase = "done";
    o.setWorking("director", false);
    this.log("director", "งานเสร็จสมบูรณ์ 🎉 พร้อมส่งมอบ", "done");
    for (const a of AGENTS) {
      o.setBusy(a.id, false);
      o.setBubble(a.id, a.id === "director" ? "🎉 เสร็จแล้ว! เยี่ยมมากทีม" : "🎉", a.id === "director" ? "done" : "talk", 5000);
    }
    this.emit();
  }

  private async stream(req: AgentRequest, onDelta: (kind: "thinking" | "text", text: string) => void) {
    const res = await fetch("/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...req, names: teamNames(), memory: memoryFor(req.agentId) }),
      signal: this.abort.signal,
    });
    if (!res.ok || !res.body) {
      const msg = await res.text().catch(() => "");
      throw new Error(msg.slice(0, 200) || `HTTP ${res.status}`);
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    let lastEmit = 0;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let nl: number;
      while ((nl = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        const ev = JSON.parse(line) as { type: string; text?: string; message?: string };
        if (ev.type === "thinking" || ev.type === "text") onDelta(ev.type, ev.text ?? "");
        else if (ev.type === "error") throw new Error(ev.message);
      }
      if (performance.now() - lastEmit > 120) {
        lastEmit = performance.now();
        this.emit();
      }
    }
    this.emit();
  }
}

// ---------- history (per browser) ----------

const KEY = "gastron-office-runs";

export function loadHistory(): RunState[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]") as RunState[];
  } catch {
    return [];
  }
}

export function saveRun(run: RunState) {
  try {
    const list = loadHistory().filter((r) => r.id !== run.id);
    list.unshift(run);
    localStorage.setItem(KEY, JSON.stringify(list.slice(0, 20)));
  } catch {
    // storage full or blocked — history is a convenience only
  }
}

export function runToMarkdown(run: RunState) {
  const parts = [run.final.output || "_(ยังไม่มี deliverable)_", "", `> Brief ต้นทาง: ${run.brief}`];
  if (run.chat?.length) {
    parts.push("", "---", "# ภาคผนวก: บทสนทนาของทีม");
    for (const c of run.chat) parts.push("", `**${c.name}** (${c.role}): ${c.text}`);
  }
  if (!run.tasks.length) return parts.join("\n");
  parts.push("", "---", "# ภาคผนวก: งานของแต่ละตำแหน่ง");
  for (const t of run.tasks) {
    const a = AGENT_BY_ID[t.agent];
    parts.push("", `## ${t.title} — ${nameOf(a.id)} (${a.role})`, t.output || `_(${t.status})_`);
  }
  return parts.join("\n");
}
