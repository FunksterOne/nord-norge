# contact sheet: python -P verktoy3/ark.py pdf out.png first last cols width
import fitz, sys
d = fitz.open(sys.argv[1]); a, b = int(sys.argv[3]), int(sys.argv[4]); cols = int(sys.argv[5]); W = int(sys.argv[6])
pages = list(range(a-1, min(b, len(d))))
r0 = d[pages[0]].rect; w = W; h = int(W * r0.height / r0.width)
rows = (len(pages)+cols-1)//cols
out = fitz.open(); pg = out.new_page(width=cols*w, height=rows*h)
for i, p in enumerate(pages):
    x, y = (i % cols)*w, (i//cols)*h
    pg.show_pdf_page(fitz.Rect(x, y, x+w, y+h), d, p)
    pg.insert_text((x+5, y+15), str(p+1), fontsize=14, color=(1,0,0))
pg.get_pixmap(dpi=72).save(sys.argv[2])
