"""Render PDF pages to PNG.
Usage: python -P verktoy2/render.py <pdf> <outdir> <pages e.g. 34-49> [zoom] [sheet]
 sheet: if given 'sheet', make a 4-col contact sheet of the pages instead of individual pngs.
"""
import sys, os
import fitz

pdf, out, rng = sys.argv[1:4]
zoom = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
sheet = len(sys.argv) > 5 and sys.argv[5] == "sheet"
os.makedirs(out, exist_ok=True)
a, b = (map(int, rng.split("-")) if "-" in rng else (int(rng), int(rng)))
doc = fitz.open(pdf)
pages = list(range(a, b + 1))
if not sheet:
    for n in pages:
        pix = doc[n - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        p = os.path.join(out, f"p{n:03d}.png")
        pix.save(p)
        print(p)
else:
    cols = 4
    w0, h0 = doc[pages[0] - 1].rect.width * zoom, doc[pages[0] - 1].rect.height * zoom
    rows = (len(pages) + cols - 1) // cols
    sheetdoc = fitz.open()
    pg = sheetdoc.new_page(width=w0 * cols, height=h0 * rows)
    for i, n in enumerate(pages):
        r = fitz.Rect((i % cols) * w0, (i // cols) * h0, (i % cols + 1) * w0, (i // cols + 1) * h0)
        pg.show_pdf_page(r, doc, n - 1)
        pg.insert_text((r.x0 + 5, r.y0 + 20), str(n), fontsize=24, color=(1, 0, 0))
    pix = pg.get_pixmap(matrix=fitz.Matrix(1, 1))
    p = os.path.join(out, f"sheet_{a}_{b}.png")
    pix.save(p)
    print(p, pix.width, pix.height)
