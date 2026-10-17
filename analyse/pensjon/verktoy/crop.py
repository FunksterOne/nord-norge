"""Render a page in horizontal bands: python -E -P verktoy/crop.py <pdf> <page> <outprefix> <zoom> <bands> [x0 x1 y0 y1 fractions]"""
import sys, os, fitz
pdf, page, pre, zoom, n = sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
x0, x1, y0, y1 = (map(float, sys.argv[6:10]) if len(sys.argv) > 9 else (0, 1, 0, 1))
os.makedirs(os.path.dirname(pre) or '.', exist_ok=True)
p = fitz.open(pdf)[page - 1]
r = p.rect
h = (y1 - y0) / n
for i in range(n):
    a = y0 + i * h - (0.01 if i else 0)
    b = y0 + (i + 1) * h + 0.01
    clip = fitz.Rect(r.x0 + r.width * x0, r.y0 + r.height * a, r.x0 + r.width * x1, r.y0 + r.height * min(b, 1))
    fn = f'{pre}_{page}_{i}.png'
    p.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip).save(fn)
    print(fn)
