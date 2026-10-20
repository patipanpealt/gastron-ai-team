# Gastron AI Marketing Office

ออฟฟิศเสมือนแบบ pixel art ที่ทีมการตลาด AI 11 ตำแหน่งทำงานร่วมกันจริงผ่าน Claude API

## ทีม
| ทีม | สมาชิก |
|---|---|
| Strategy & Lead | Max (Marketing Director), Nina (Brand Strategist), Ken (Market Researcher) |
| Content & Creative | Ploy (Copywriter), Beam (Content Creator), Mook (Creative Director) |
| Social & Ads | Fah (Social Media), Tom (Performance Ads), Earth (SEO) |
| Data & Review | June (Data Analyst), Pim (QA & Brand Reviewer) |

## 2 โหมดงาน
- **🎨 Graphic Brief** (ค่าเริ่มต้น): ทีมช่วยกันคิด brief ส่งดีไซเนอร์ได้ทันที ได้ copy บนชิ้นงาน, visual direction,
  palette (มีแถบสีให้คลิกคัดลอก HEX), **layout wireframe** ที่แอปวาดให้ดู, ขนาดตามช่องทาง, AI image prompts และ checklist
  เลือกประเภทชิ้นงานได้ (Poster, Social Post, Banner, Leaflet, Booth backdrop…) และบันทึกเป็น PDF ได้
- **📣 แคมเปญ / คอนเทนต์**: วางแผนแคมเปญเต็มรูปแบบ (กลยุทธ์, คอนเทนต์, โฆษณา, SEO, KPI)

## ขั้นตอนการทำงาน
1. ส่ง brief แล้วทุกคนจะเดินเข้าห้องประชุม ระหว่างนั้น Max วางแผนและแจกงาน
2. แต่ละคนกลับไปทำงานที่โต๊ะ งานไหนรอผลงานคนอื่นได้ก็จะรอ ส่วนที่เหลือทำพร้อมกัน
3. ทำเสร็จก็ส่งเอกสารต่อให้เพื่อนที่ต้องใช้งานนั้น แล้วเดินไปส่งงานให้ Max
4. Pim ตรวจงานทั้งหมด แล้ว Max รวมเป็น Deliverable ฉบับเดียว ดาวน์โหลดเป็น .md ได้

คลิกที่ตัวละครเพื่อดูว่ากำลังคิดและเขียนอะไรอยู่

## รันบนเครื่อง
```bash
npm install
cp .env.example .env.local   # แล้วใส่ ANTHROPIC_API_KEY
npm run dev                  # http://localhost:3300
```
ถ้าไม่ใส่ API key จะทำงานในโหมด **DEMO** ใช้ข้อความจำลอง ไม่เสียค่าใช้จ่าย

## Deploy ขึ้น Vercel
1. Import โปรเจกต์นี้เข้า Vercel
2. ตั้ง Environment Variables:
   - `ANTHROPIC_API_KEY`: key ของ Anthropic
   - `TEAM_PASSWORD`: รหัสผ่านที่ทีมใช้เข้าออฟฟิศ (ถ้าไม่ตั้ง ใครมีลิงก์ก็เข้าได้)
3. Deploy


## แต่งตัว ตั้งชื่อ และแต่งห้อง (ทำเองได้ในแอป)
ปุ่มอยู่เหนือกรอบออฟฟิศ — ทุกอย่างบันทึกอัตโนมัติในเครื่อง (localStorage) และคงอยู่หลังรีเฟรช

- **🧑‍🎨 แต่งตัว & ตั้งชื่อ** (หรือดับเบิลคลิกชื่อในรายชื่อทีม / ปุ่ม "แต่งตัว/ชื่อ" ในหน้าโปรไฟล์): ตั้งชื่อ เลือกสีผิว ทรงผม 6 แบบ เสื้อ 5 แบบ กางเกง/กระโปรง 5 แบบ และเลือกสีผม/เสื้อ/กางเกงได้อิสระ
  มีปุ่มสุ่มลุค คืนค่าเริ่มต้น และส่งออก/นำเข้าไฟล์ตั้งค่า (.json) ชื่อที่ตั้งจะแสดงทั้งออฟฟิศ บอร์ดงาน และถูกส่งให้ AI ใช้เรียกตัวเองตอนทำงาน
- **🏠 แต่งห้อง**: เลือกของจากรายการแล้วคลิกในห้องเพื่อวาง คลิกของเพื่อเลือก ลากเพื่อย้าย
  `R` หมุน · `Delete` ลบ · `Esc` ยกเลิก · Shift ค้างตอนวางเพื่อวางต่อเนื่อง · ทำสำเนาได้ด้วย Ctrl/⌘+D
  เปลี่ยนลายพื้น สีพื้น สีผนัง ขนาดห้อง วางพรมเลือกสีได้ และเลือกว่า "โต๊ะทำงาน + เก้าอี้" ตัวไหนเป็นที่นั่งของใคร (คนที่ไม่มีที่นั่งจะยืนรอกลางห้อง)
  ตอนที่ทีมกำลังทำงานจะแต่งห้องไม่ได้ (ปุ่มจะถูกปิด)
  เฟอร์นิเจอร์และของตกแต่งผนังถูกวาดใหญ่ขึ้น 1.5 เท่าของภาพต้นฉบับ (ตัวละครขนาดเดิม) ปรับได้ที่ `OBJECT_SCALE` ใน `lib/office/catalog.ts` — ถ้าเปลี่ยนค่านี้ ผังห้องที่เคยบันทึกไว้จะถูกแทนด้วยห้องเริ่มต้นใหม่

### ไฟล์ที่เกี่ยวข้อง
- `lib/office/` — `appearance.ts` (ตัวเลือกการแต่งตัว), `palette.ts` (ทำสีเสื้อ/ผมจากสีที่เลือก), `sprites.ts` (ประกอบตัวละครจาก layer), `catalog.ts` (รายการของตกแต่ง), `room.ts` (ผังห้อง + ห้องเริ่มต้น), `store.ts` (บันทึกการตั้งค่า), `engine.ts` (วาด/เดิน/แต่งห้อง)
- `components/CharacterEditor.tsx`, `components/RoomEditor.tsx`
- `public/assets/` — ภาพตัวละคร (layer) และเฟอร์นิเจอร์ที่สร้างจาก `pixel-art/` สร้างใหม่ได้ด้วย `python3 pixel-art/export_assets.py`

## ปรับแต่ง
- ข้อมูลบริษัทที่ AI ทุกตัวรู้: `lib/brand.ts`
- ตำแหน่งและบุคลิกการทำงานของตัวละคร: `lib/agents.ts` (ชื่อ/หน้าตา/ผังห้องแต่งเองได้ในแอป ดูหัวข้อด้านบน)
- ผังห้องเริ่มต้น: `defaultRoom()` ใน `lib/office/room.ts`
- โมเดลและระดับความคิด: `CLAUDE_MODEL`, `CLAUDE_EFFORT` ใน env

## หมายเหตุ: ไดรฟ์ภายนอก
โปรเจกต์อยู่บนไดรฟ์ภายนอก (ALT-04) ที่ macOS สร้างไฟล์ `._*` ปนเข้าไปใน cache ของ Next ถ้า `npm run build` ขึ้น error `Failed to open database` ให้ล้าง cache ก่อน:
```bash
rm -rf .next/cache/turbopack
```

## Partitions & name plaques

In the room editor, the **กั้นโซน & ป้าย** category has partition panels (solid / glass / slat, 1–16 tiles, any colour, horizontal or vertical) and a team-name plaque whose text you type. Wall-type objects (posters, clocks, plaques…) can be hung on the front face of a horizontal partition and move with it. `?slot=name` in the URL keeps a separate saved office for testing.

Doors: a door can be hung on the back wall or set into one tile of a horizontal partition. A door in a partition opens by itself when an agent walks up and closes after; click it (when not editing) to prop it open or shut. If an agent has no route (walled in), they stay put instead of walking through walls.

## Facebook post conversation

Pick **💬 โพสต์ Facebook** in the brief panel: the team sits at the meeting table and talks the post through turn by turn (director → strategist → social → copywriter → creative → content → copywriter → creative → QA → copywriter → director), each turn a real model call that reads the conversation so far (`mode: "chat"` in `/api/agent`). You can type into the room while they talk (`Orchestrator.say`). Then the director writes the **Facebook Post Brief** (header, on-image content, layout block, captions, mini-campaign). The turn order and what each person contributes is `FB_SCRIPT` in `lib/orchestrator.ts`. Without `ANTHROPIC_API_KEY` it runs scripted DEMO lines.

## Gemini instead of Claude

Set `GEMINI_API_KEY` (and no Anthropic key, or `AI_PROVIDER=gemini`) in `.env.local`; the agents and the plan then use Gemini (`lib/gemini.ts`, REST, default model `gemini-3.8-flash`). `/api/status` reports the provider. Extended thinking is a Claude-only feature, so with Gemini the "💭" bubbles show only the answer being typed.

## Teaching the team (memory) and PDF

- **🧠 ฝึก AI** (stage toolbar): rules, good examples and feedback, for the whole team or one person, stored in this browser (`lib/memory.ts`, key `gastron.office.memory.v1`) and sent with every AI request (`memory` in `/api/agent`, injected by `systemFor`). The finished-brief window also has a "สอนทีมจากงานนี้" box.
- **⬇ ดาวน์โหลด PDF**: opens the browser's print dialog with a designed A4 version (`PrintDoc` in `app/page.tsx`, styles under "the designed PDF version" in `globals.css`); choose "Save as PDF".
- Briefs now always contain a **Copy Deck**: the exact text that goes on the artwork, matching the numbered zones of the layout wireframe.
- Gemini free tier has a small daily quota *per model*; `lib/gemini.ts` falls back to `gemini-3.5-flash-lite` / `gemini-3.1-flash-lite` when one is used up.

## Reference links

Under the brief box, **🔗 Reference** takes up to 6 links, each with a note. The server (`/api/reference`, `lib/reference.ts`) opens the link, turns the page into text and has the AI summarise it; the summary is editable and is appended to the brief as "Reference ที่ N", so the brief can say "ตาม Reference 1". Google Docs/Sheets/Slides and Drive links work when shared as "anyone with the link"; private/internal addresses, PDFs and images are not read. With the Gemini free tier the page text is sent to Google.

## OmniRoute

Set `OMNIROUTE_KEY` (and optionally `OMNIROUTE_MODEL`, e.g. a combo name) and the app talks to a local OmniRoute (`lib/omniroute.ts`, OpenAI-compatible `/v1/chat/completions`). OmniRoute can fall back between providers/models when a free quota runs out. Never commit `.env.local`.
