"use client";

import { marked } from "marked";
import { useMemo } from "react";

interface LayoutSpec {
  title?: string;
  ratio?: string;
  background?: string;
  zones?: { label: string; text?: string; x: number; y: number; w: number; h: number; color?: string }[];
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const HEX = /^#[0-9a-fA-F]{6}$/;
const color = (c: string | undefined, fallback: string) => (c && HEX.test(c) ? c : fallback);
const num = (v: unknown) => Math.max(0, Math.min(100, Number(v) || 0));

/** Draw a `layout` JSON block as a wireframe the designer can read at a glance. */
function renderLayout(src: string) {
  let spec: LayoutSpec;
  try {
    spec = JSON.parse(src) as LayoutSpec;
  } catch {
    // still streaming, or malformed — show it as code
    return `<pre class="layout-pending"><code>${esc(src)}</code></pre>`;
  }
  const [rw, rh] = (spec.ratio || "3:4").split(":").map(Number);
  const ratio = rw > 0 && rh > 0 ? `${rw} / ${rh}` : "3 / 4";
  const portrait = !(rw > rh);
  const zones = (spec.zones || [])
    .map((z, i) => {
      const c = color(z.color, "#8b5a3c");
      return `<div class="lz" style="left:${num(z.x)}%;top:${num(z.y)}%;width:${num(z.w)}%;height:${num(z.h)}%;--zc:${c}">
        <span class="lz-n">${i + 1}</span><span class="lz-l">${z.text ? `<b>${esc(String(z.text))}</b>` : esc(String(z.label ?? ""))}</span></div>`;
    })
    .join("");
  return `<figure class="layout-card">
    <figcaption><b>📐 ${esc(spec.title || "Layout")}</b> <span>${esc(spec.ratio || "")}</span></figcaption>
    <div class="layout-canvas ${portrait ? "is-portrait" : ""}" style="aspect-ratio:${ratio};background:${color(spec.background, "#ffffff")}">${zones}</div>
  </figure>`;
}

const renderer = new marked.Renderer();
// Raw HTML from the model is escaped, never rendered.
renderer.html = ({ text }) => esc(text);
renderer.code = ({ text, lang }) =>
  lang === "layout" ? renderLayout(text) : `<pre><code>${esc(text)}</code></pre>`;
renderer.codespan = ({ text }) => {
  const raw = text.replace(/&#35;/g, "#").trim();
  return HEX.test(raw)
    ? `<code class="hex"><i style="background:${raw}"></i>${raw.toUpperCase()}</code>`
    : `<code>${text}</code>`;
};

export function Markdown({ text }: { text: string }) {
  const html = useMemo(() => marked.parse(text, { renderer, gfm: true, breaks: false, async: false }) as string, [text]);
  return <div className="md" dangerouslySetInnerHTML={{ __html: html }} />;
}

/** Pull the brand palette used in a brief (HEX codes in inline code). */
export function extractPalette(text: string) {
  const seen = new Set<string>();
  for (const m of text.matchAll(/`(#[0-9a-fA-F]{6})`/g)) seen.add(m[1].toUpperCase());
  return [...seen].slice(0, 10);
}
