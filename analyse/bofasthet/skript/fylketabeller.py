"""Finn tabeller/figurer i monitor-tekstene som har fylkesrader (Nordland/Troms/Finnmark).

Bruk: python fylketabeller.py kilder/pdf/*.txt
Skriver: fil, side, tabelltittel (første to linjer).
"""
import re, sys
from pathlib import Path

for f in sys.argv[1:]:
    linjer = Path(f).read_text(encoding="utf-8").splitlines()
    side = 0
    blokker = []  # (side, startlinje, tittel)
    for i, l in enumerate(linjer):
        m = re.match(r"===== SIDE (\d+)", l)
        if m:
            side = int(m.group(1))
        if re.match(r"^\s*Tabell\s+\d+(\.\d+)?\s*[.:]?\s*$|^\s*Tabell\s+\d+(\.\d+)?\s*[.:]\s+\S", l) and "....." not in l:
            tittel = " ".join(x.strip() for x in linjer[i:i + 4])
            blokker.append((side, i, tittel[:230]))
    print(f"##### {Path(f).name}")
    for k, (s, i, t) in enumerate(blokker):
        slutt = blokker[k + 1][1] if k + 1 < len(blokker) else len(linjer)
        kropp = "\n".join(linjer[i:min(slutt, i + 260)])
        if re.search(r"Nordland", kropp) and re.search(r"Finnmark", kropp):
            print(f"  s.{s} L{i}: {t}")
