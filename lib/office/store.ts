// The user's office settings — each agent's display name and look, and the room layout — kept in localStorage.
import { useEffect, useSyncExternalStore } from "react";
import { AGENTS, type AgentId } from "../agents";
import { type Appearance, defaultAppearance, defaultProfiles, type Profile, sanitizeAppearance } from "./appearance";
import { defaultRoom, type RoomLayout, sanitizeRoom } from "./room";

export interface OfficeSettings {
  profiles: Record<AgentId, Profile>;
  room: RoomLayout;
}

// `?slot=name` keeps a separate set of settings (handy for trying things without touching your real office)
const slot = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("slot")?.replace(/\W/g, "").slice(0, 24) : "";
const KEY = slot ? `gastron.office.v1:${slot}` : "gastron.office.v1";
export const MAX_NAME = 24;

const SERVER: OfficeSettings = { profiles: defaultProfiles(), room: defaultRoom() };
let state: OfficeSettings = SERVER;
let loaded = false;
const listeners = new Set<() => void>();

const emit = () => listeners.forEach((l) => l());

function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* private mode / quota — the office still works, it just won't be remembered */
  }
}

export function cleanName(raw: unknown, fallback: string) {
  const s = typeof raw === "string" ? raw.replace(/\s+/g, " ").trim().slice(0, MAX_NAME) : "";
  return s || fallback;
}

/** Merge whatever is saved with the defaults, so an old or hand-edited file never breaks the office. */
export function sanitizeSettings(raw: unknown): OfficeSettings {
  const d = defaultProfiles();
  const o = (raw && typeof raw === "object" ? raw : {}) as { profiles?: Record<string, Partial<Profile>>; room?: unknown };
  const profiles = Object.fromEntries(
    AGENTS.map((a) => {
      const p = o.profiles?.[a.id];
      return [a.id, { name: cleanName(p?.name, d[a.id].name), appearance: sanitizeAppearance(p?.appearance, d[a.id].appearance) }];
    }),
  ) as Record<AgentId, Profile>;
  return { profiles, room: sanitizeRoom(o.room) };
}

export function loadSettings() {
  if (loaded || typeof window === "undefined") return;
  loaded = true;
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) state = sanitizeSettings(JSON.parse(raw));
  } catch {
    /* ignore a corrupt save */
  }
  emit();
}

function set(next: OfficeSettings) {
  state = next;
  persist();
  emit();
}

export const getSettings = () => state;
export const nameOf = (id: AgentId) => state.profiles[id]?.name ?? id;

export const office = {
  setName(id: AgentId, name: string) {
    const fallback = AGENTS.find((a) => a.id === id)!.name;
    set({ ...state, profiles: { ...state.profiles, [id]: { ...state.profiles[id], name: cleanName(name, fallback) } } });
  },
  setAppearance(id: AgentId, patch: Partial<Appearance>) {
    const cur = state.profiles[id];
    set({ ...state, profiles: { ...state.profiles, [id]: { ...cur, appearance: { ...cur.appearance, ...patch } } } });
  },
  setProfile(id: AgentId, profile: Profile) {
    set({ ...state, profiles: { ...state.profiles, [id]: profile } });
  },
  resetProfile(id: AgentId) {
    set({ ...state, profiles: { ...state.profiles, [id]: { name: AGENTS.find((a) => a.id === id)!.name, appearance: defaultAppearance(id) } } });
  },
  setRoom(room: RoomLayout) {
    set({ ...state, room });
  },
  resetRoom() {
    set({ ...state, room: defaultRoom() });
  },
  resetAll() {
    set({ profiles: defaultProfiles(), room: defaultRoom() });
  },
  exportJson() {
    return JSON.stringify({ app: "gastron-ai-office", ...state }, null, 2);
  },
  importJson(text: string) {
    set(sanitizeSettings(JSON.parse(text)));
  },
};

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

/** React hook: the current settings (defaults during SSR, the saved ones after mount). */
export function useOffice(): OfficeSettings {
  useEffect(() => loadSettings(), []);
  return useSyncExternalStore(subscribe, getSettings, () => SERVER);
}
