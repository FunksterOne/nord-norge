# usage: python -I verktoy3/tekst.py pdfpath [pattern]  -> writes .txt next to pdf, prints pages matching
import fitz, sys, re
p = sys.argv[1]
pat = sys.argv[2] if len(sys.argv) > 2 else r'(?i)premieavvik|pensjonsforpliktelse|pensjonsmidler'
d = fitz.open(p)
txt = []
hits = []
for i, pg in enumerate(d):
    t = pg.get_text()
    txt.append(f'\n=== SIDE {i+1} ===\n' + t)
    n = len(re.findall(pat, t))
    if n: hits.append((i+1, n))
open(p + '.txt', 'w', encoding='utf-8').write(''.join(txt))
tot = sum(len(x) for x in txt)
print('sider', len(d), 'tegn', tot, 'treff', hits)
