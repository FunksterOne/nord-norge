# usage: python -P verktoy3/bilde.py pdf outprefix dpi page [page...]
import fitz, sys
d = fitz.open(sys.argv[1]); dpi = int(sys.argv[3])
for s in sys.argv[4:]:
    d[int(s)-1].get_pixmap(dpi=dpi).save(f'{sys.argv[2]}_{s}.png')
