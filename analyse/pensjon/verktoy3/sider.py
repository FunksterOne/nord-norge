# usage: python -I verktoy3/sider.py pdfpath 40 41 ...
import fitz, sys
d = fitz.open(sys.argv[1])
for s in sys.argv[2:]:
    print(f'=== SIDE {s} ===')
    print(d[int(s)-1].get_text())
