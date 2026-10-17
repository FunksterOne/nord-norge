# python -P verktoy3/rot.py pdf page out dpi rot x0 y0 x1 y1   (clip fractions in unrotated page coords)
import fitz, sys
d = fitz.open(sys.argv[1]); p = d[int(sys.argv[2])-1]; r = p.rect
f = [float(v) for v in sys.argv[6:10]]
clip = fitz.Rect(r.x0+f[0]*r.width, r.y0+f[1]*r.height, r.x0+f[2]*r.width, r.y0+f[3]*r.height)
z = int(sys.argv[4])/72
p.get_pixmap(matrix=fitz.Matrix(z, z).prerotate(int(sys.argv[5])), clip=clip).save(sys.argv[3])
