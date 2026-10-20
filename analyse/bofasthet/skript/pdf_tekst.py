"""Trekk ut tekst fra PDF-er med PyMuPDF; én .txt per PDF med sidemarkører.

Bruk: python pdf_tekst.py kilder/pdf/*.pdf
"""
import sys
from pathlib import Path
import fitz  # PyMuPDF

for f in sys.argv[1:]:
    p = Path(f)
    doc = fitz.open(p)
    deler = []
    for i, side in enumerate(doc, start=1):
        deler.append(f"\n===== SIDE {i} =====\n" + side.get_text("text"))
    p.with_suffix(".txt").write_text("".join(deler), encoding="utf-8")
    print(p.name, len(doc), "sider")
