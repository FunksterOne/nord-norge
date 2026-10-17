"""Contact sheet: python -E -P verktoy/ark.py <pdf> <out.png> <zoom> <cols> <pages a-b>"""
import sys, os, fitz
pdf, out, zoom, cols, spec = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
a, b = map(int, spec.split('-'))
doc = fitz.open(pdf)
pix = [doc[p - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom)) for p in range(a, min(b, len(doc)) + 1)]
w = max(p.width for p in pix); h = max(p.height for p in pix)
rows = (len(pix) + cols - 1) // cols
o = fitz.open(); pg = o.new_page(width=w * cols, height=h * rows)
for k, p in enumerate(pix):
    r = fitz.Rect((k % cols) * w, (k // cols) * h, (k % cols + 1) * w, (k // cols + 1) * h)
    pg.insert_image(r, pixmap=p)
    pg.insert_text((r.x0 + 5, r.y0 + 15), str(a + k), fontsize=14, color=(1, 0, 0))
pg.get_pixmap().save(out)
print(out)
