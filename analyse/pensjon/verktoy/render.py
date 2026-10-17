"""Render PDF pages to PNG. Usage: python -E -P verktoy/render.py <pdf> <outdir> <zoom> <pages like 1,3,5-7>"""
import sys, os, fitz
pdf, out, zoom, spec = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
os.makedirs(out, exist_ok=True)
doc = fitz.open(pdf)
pages = []
for part in spec.split(','):
    if '-' in part:
        a, b = map(int, part.split('-')); pages += range(a, b + 1)
    else:
        pages.append(int(part))
for p in pages:
    if 1 <= p <= len(doc):
        pix = doc[p - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        fn = os.path.join(out, f'p{p:03d}.png')
        pix.save(fn)
        print(fn, pix.width, pix.height)
