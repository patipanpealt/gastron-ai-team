// Turn the designed brief (the hidden `.print-doc` element) into a real A4 PDF file and download it.
// Each section is rendered on its own and placed so a section is never cut in half unless it is longer than a page.

const PAGE_W = 210;
const PAGE_H = 297;
const MARGIN = 11;
const GAP = 2.5;
const CAPTURE_PX = 700;

export async function downloadBriefPdf(source: HTMLElement, filename: string) {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([import("html2canvas-pro"), import("jspdf")]);

  const stage = document.createElement("div");
  stage.style.cssText = `position:fixed;left:-10000px;top:0;width:${CAPTURE_PX}px;background:#fff;`;
  document.body.appendChild(stage);

  // split into chunks: header (+ palette), one per `##` section, footer
  const groups: Node[][] = [];
  let head: Node[] = [];
  const md = source.querySelector(".md");
  for (const el of Array.from(source.children)) {
    if (el === md) break;
    head.push(el);
  }
  groups.push(head);
  const tail: Node[] = [];
  let seenMd = false;
  for (const el of Array.from(source.children)) {
    if (el === md) {
      seenMd = true;
      let cur: Node[] = [];
      for (const node of Array.from(el.children)) {
        if (node.tagName === "H2" && cur.length) {
          groups.push([wrapMd(cur)]);
          cur = [];
        }
        cur.push(node);
      }
      if (cur.length) groups.push([wrapMd(cur)]);
    } else if (seenMd) tail.push(el);
  }
  if (tail.length) groups.push(tail);

  const pdf = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
  const usableW = PAGE_W - 2 * MARGIN;
  const usableH = PAGE_H - 2 * MARGIN;
  let y = MARGIN;

  try {
    for (const group of groups) {
      if (!group.length) continue;
      const box = document.createElement("div");
      box.className = "print-doc pdf-capture";
      box.style.cssText = `display:block;width:${CAPTURE_PX}px;background:#fff;padding:0;`;
      for (const n of group) box.appendChild(n.cloneNode(true));
      stage.replaceChildren(box);
      const canvas = await html2canvas(box, { scale: 2, backgroundColor: "#ffffff", useCORS: true, logging: false });
      const hMm = (canvas.height / canvas.width) * usableW;

      if (hMm <= usableH) {
        if (y + hMm > PAGE_H - MARGIN) {
          pdf.addPage();
          y = MARGIN;
        }
        pdf.addImage(canvas.toDataURL("image/jpeg", 0.92), "JPEG", MARGIN, y, usableW, hMm);
        y += hMm + GAP;
      } else {
        // longer than a page: cut it into page-sized slices
        const pxPerMm = canvas.width / usableW;
        let sy = 0;
        if (y > MARGIN) {
          pdf.addPage();
          y = MARGIN;
        }
        while (sy < canvas.height) {
          const slicePx = Math.min(canvas.height - sy, Math.floor(usableH * pxPerMm));
          const part = document.createElement("canvas");
          part.width = canvas.width;
          part.height = slicePx;
          part.getContext("2d")!.drawImage(canvas, 0, sy, canvas.width, slicePx, 0, 0, canvas.width, slicePx);
          pdf.addImage(part.toDataURL("image/jpeg", 0.92), "JPEG", MARGIN, MARGIN, usableW, slicePx / pxPerMm);
          sy += slicePx;
          if (sy < canvas.height) pdf.addPage();
          y = MARGIN + slicePx / pxPerMm + GAP;
        }
      }
    }
  } finally {
    stage.remove();
  }
  pdf.save(filename);
}

function wrapMd(nodes: Node[]): Node {
  const d = document.createElement("div");
  d.className = "md";
  for (const n of nodes) d.appendChild(n.cloneNode(true));
  return d;
}
