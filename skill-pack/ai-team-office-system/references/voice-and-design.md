# Voice and UI design (approved)

## UI copy (Thai)
- Friendly-professional, short. Headings without emoji ("สั่งงานทีม", "ห้องประชุม", "บอร์ดงาน", "ในออฟฟิศตอนนี้", "งานที่ผ่านมา", "สอนทีม").
- Hints are one sentence about the result ("ได้ brief พร้อมส่งดีไซเนอร์: ข้อความบนชิ้นงาน สี layout และขนาด"); how-to goes into placeholders.
- Emoji are fine inside character speech bubbles only.

## Humanizer rules (applied to UI copy and to the agents' prompts)
No staged contrasts ("ไม่ใช่แค่… แต่…"), no one-line dramatic closers or recaps, no "มาเริ่มกันเลย" run-ups, no hype ("ปฏิวัติ", "ยกระดับ", "ที่สุด"), no forced triads, no bold on every line, no emoji headings, no long dashes. Keep facts; never invent numbers.

## Visual system (Hallmark refine pass)
- Keep the cozy wood/parchment pixel look (Pixelify Sans for labels, IBM Plex Sans Thai body). Real GASTRON logo SVG in the header and login.
- Every colour is a token in `:root` (`app/globals.css`); no raw hex in rules.
- Buttons never wrap (`white-space: nowrap`); check 320/375/414/768 px.
- Stamp at the top of `globals.css`; `.hallmark/log.json` records runs.
