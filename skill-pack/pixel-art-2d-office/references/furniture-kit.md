# Furniture, wall objects, floors

Contract (`scripts/kit.py`): 32px grid, 3/4 top-down (lit TOP face + darker FRONT face), light top-left, 1px outline `#2b2230` (on the shade side, v2), sheared cast shadow right, 4-step ramps. Gastron CI colours: red `#D70010`, green `#009143`.

Anchor sprites by bottom-centre (feet). Each generator writes PNGs + an 8x preview with the grid. Sprite families: desk (front/back/left/right; direction = way the SCREEN faces; the user sits opposite), chair (front/back/left/right = way the person faces), meeting table, sofa, shelf/bookshelf, filing, fridge, water cooler, whiteboard, plush, trash bins, plants, rugs (procedural), tiles/floors (2 floor patterns + wall), wall items (windows, blinds, door, pillar, whiteboard, calendar, clocks, posters).

`export_assets.py` flattens everything to `public/assets/furniture/<name>.png` and writes `lib/office/furniture-meta.json` ({w,h,body:[x0,y0,x1,y1]}); `body` (solid bounds) is used to centre a sprite in its footprint and rest it on the lower edge.

Display scale: `OBJECT_SCALE = 1.5` (user asked — desks felt small). Footprints use `ceil(size × 1.5)`. Wall height `WALL_H = round(64 × 1.5) = 96`.

Chair art: `chair_front` shows the backrest on top with the seat cushion below it (used for people facing S); `chair_back` is its rear view (people facing N); `chair_left/right` have a tall backrest on the side the person leans against. Desk sprites are named by the way the screen faces, so the person sits on the opposite side.
