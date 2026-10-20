// What the user has taught the team: standing rules, good examples and feedback. Kept in this browser (localStorage)
// and sent along with every request so the AI follows it next time.
import { useEffect, useSyncExternalStore } from "react";
import type { AgentId } from "./agents";
import { uid } from "./uid";

export type MemoryKind = "rule" | "example" | "feedback";
export type MemoryScope = "team" | AgentId;

export interface MemoryItem {
  id: string;
  scope: MemoryScope;
  kind: MemoryKind;
  text: string;
  on: boolean;
  createdAt: number;
}

export const MEMORY_KIND_LABEL: Record<MemoryKind, string> = {
  rule: "กฎ / สไตล์ที่ต้องทำตาม",
  example: "ตัวอย่างที่ดี",
  feedback: "ข้อติจากงานที่ผ่านมา",
};

const KEY = "gastron.office.memory.v1";
const MAX_ITEM = 1200;
const MAX_TOTAL = 5000; // characters sent per request, so prompts stay small
const SERVER: MemoryItem[] = [];
let items: MemoryItem[] = SERVER;
let loaded = false;
const listeners = new Set<() => void>();

function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    /* private mode / quota: memory still works until reload */
  }
}

function set(next: MemoryItem[]) {
  items = next;
  persist();
  listeners.forEach((l) => l());
}

export function loadMemory() {
  if (loaded || typeof window === "undefined") return;
  loaded = true;
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "[]") as unknown;
    if (Array.isArray(raw)) {
      items = raw
        .filter((m): m is MemoryItem => !!m && typeof m === "object" && typeof (m as MemoryItem).text === "string")
        .map((m) => ({ ...m, text: m.text.slice(0, MAX_ITEM), on: m.on !== false }));
    }
  } catch {
    /* corrupt save: start empty */
  }
  listeners.forEach((l) => l());
}

export const memory = {
  all: () => items,
  add(scope: MemoryScope, kind: MemoryKind, text: string) {
    const t = text.trim().slice(0, MAX_ITEM);
    if (!t) return;
    set([{ id: uid(), scope, kind, text: t, on: true, createdAt: Date.now() }, ...items]);
  },
  update(id: string, patch: Partial<Pick<MemoryItem, "text" | "on" | "scope" | "kind">>) {
    set(items.map((m) => (m.id === id ? { ...m, ...patch, text: (patch.text ?? m.text).slice(0, MAX_ITEM) } : m)));
  },
  remove(id: string) {
    set(items.filter((m) => m.id !== id));
  },
  clear() {
    set([]);
  },
};

/** The text sent to the AI for one agent: team-wide notes plus that agent's own, newest first, capped. */
export function memoryFor(agent: AgentId): string {
  loadMemory(); // the teaching panel may never have been opened on this page
  const out: string[] = [];
  let used = 0;
  for (const m of items) {
    if (!m.on || (m.scope !== "team" && m.scope !== agent)) continue;
    const line = `- [${MEMORY_KIND_LABEL[m.kind]}] ${m.text.replace(/\s+/g, " ")}`;
    if (used + line.length > MAX_TOTAL) break;
    out.push(line);
    used += line.length;
  }
  return out.join("\n");
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

export function useMemory(): MemoryItem[] {
  useEffect(() => loadMemory(), []);
  return useSyncExternalStore(subscribe, () => items, () => SERVER);
}
