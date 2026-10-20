# Features

- **Reference links** (brief panel, up to 6): URL + note; server reads the page (Google Docs/Sheets/Slides export links, Drive download links; refuses private IPs/localhost, PDFs, images, login walls), AI summarises it, user can edit the summary; appended to the brief as "Reference ที่ N" so the brief can say "ตาม Reference 1". Not persisted across reloads.
- **สอนทีม (memory)**: rules / good examples / feedback, team-wide or per agent, toggle/edit/delete; localStorage `gastron.office.memory.v1`; max ~5,000 chars sent per request; also a "สอนทีมจากงานนี้" box under each finished brief. Call `loadMemory()` before reading (panel may never have been opened).
- **PDF**: `lib/pdf.ts` renders the hidden `.print-doc` (navy header with logo text, palette strip, section bars, tables, layout wireframe, source brief) with **html2canvas-pro** (plain html2canvas crashes on CSS `color()`), splits per `##` section so sections aren't cut, A4 via jsPDF, falls back to `window.print()`. Text in the PDF is an image.
- **History**: last 20 runs in localStorage `gastron-office-runs`; markdown export; chat transcript appended.
- **Mobile**: `allowedDevOrigins` for LAN IPs in `next.config.ts`; `uid()` instead of `crypto.randomUUID` (missing on http://192.168.x.x).
