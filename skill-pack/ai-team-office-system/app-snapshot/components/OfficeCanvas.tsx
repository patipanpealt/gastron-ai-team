"use client";

import { useEffect, useRef } from "react";
import type { AgentId } from "@/lib/agents";
import type { Profile } from "@/lib/office/appearance";
import { type EditState, OfficeEngine } from "@/lib/office/engine";
import type { RoomLayout } from "@/lib/office/room";

export function OfficeCanvas({
  onReady,
  onSelect,
  selected,
  room,
  profiles,
  edit,
  onRoomChange,
  onEditSelect,
  onPlaceCancel,
}: {
  onReady: (engine: OfficeEngine) => void;
  onSelect: (id: AgentId | null) => void;
  selected: AgentId | null;
  room: RoomLayout;
  profiles: Record<AgentId, Profile>;
  edit: EditState;
  onRoomChange: (room: RoomLayout, selectId?: string | null) => void;
  onEditSelect: (id: string | null) => void;
  onPlaceCancel: () => void;
}) {
  const wrap = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const engine = useRef<OfficeEngine | null>(null);
  // the engine is created once with the first values; later changes are pushed in by the effects below
  const first = useRef({ room, profiles });

  useEffect(() => {
    const font = getComputedStyle(document.body).fontFamily;
    const pixelFont = getComputedStyle(document.documentElement).getPropertyValue("--font-pixel").trim() || "monospace";
    const e = new OfficeEngine(canvas.current!, font, pixelFont, first.current.room, first.current.profiles);
    engine.current = e;
    if (process.env.NODE_ENV !== "production") (window as unknown as { __office?: OfficeEngine }).__office = e;
    const ro = new ResizeObserver(([entry]) => e.resize(entry.contentRect.width));
    ro.observe(wrap.current!);
    e.start();
    onReady(e);
    return () => {
      ro.disconnect();
      e.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const e = engine.current;
    if (!e) return;
    e.onSelectAgent = onSelect;
    e.onRoomChange = onRoomChange;
    e.onEditSelect = onEditSelect;
    e.onPlaceCancel = onPlaceCancel;
  });

  useEffect(() => {
    if (engine.current) engine.current.selected = selected;
  }, [selected]);

  useEffect(() => {
    engine.current?.setRoom(room);
  }, [room]);

  useEffect(() => {
    engine.current?.setProfiles(profiles);
  }, [profiles]);

  useEffect(() => {
    engine.current?.setEdit(edit);
  }, [edit]);

  return (
    <div ref={wrap} className="office-wrap">
      <canvas ref={canvas} className="office-canvas" />
    </div>
  );
}
