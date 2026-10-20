"""Skriv tabellrader fra bestemte PDF-sider, gruppert etter y-posisjon (PyMuPDF-ord).

Bruk: python pdf_rader.py fil.pdf side[,side...] [filterord ...]
Uten filterord skrives alle rader.
"""
import sys
import fitz

pdf, sider = sys.argv[1], [int(s) for s in sys.argv[2].split(",")]
filt = sys.argv[3:]
doc = fitz.open(pdf)
for s in sider:
    side = doc[s - 1]
    rader = {}
    for w in side.get_text("words"):
        y = round((w[1] + w[3]) / 2 / 2.5)  # grupper ord på samme linje (toleranse ~2,5 pt)
        rader.setdefault(y, []).append((w[0], w[4]))
    print(f"===== {pdf} side {s}")
    for y in sorted(rader):
        tekst = " ".join(t for _, t in sorted(rader[y]))
        if not filt or any(f.lower() in tekst.lower() for f in filt):
            print("  ", tekst)
