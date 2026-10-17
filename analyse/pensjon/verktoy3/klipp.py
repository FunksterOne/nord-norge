# python -P verktoy3/klipp.py pdf page out.png dpi x0 y0 x1 y1  (fractions of page)
import fitz, sys
d = fitz.open(sys.argv[1]); p = d[int(sys.argv[2])-1]; r = p.rect
f = [float(v) for v in sys.argv[5:9]]
clip = fitz.Rect(r.x0+f[0]*r.width, r.y0+f[1]*r.height, r.x0+f[2]*r.width, r.y0+f[3]*r.height)
p.get_pixmap(dpi=int(sys.argv[4]), clip=clip).save(sys.argv[3])
