"""Hent Nord-Norge-rader (Nordland, Troms, Finnmark, Troms og Finnmark, landet) fra fylketabeller
i monitor-tekstene. Skriver tabelltittel, flatet overskrift og rå tallrekker per rad.

Bruk: python nn_rader.py fil.txt linjenr [linjenr ...]
(linjenumre fra fylketabeller.py, 0-basert)
"""
import re, sys
from pathlib import Path

RADER = ["I alt", "Hele landet", "Alle", "Nordland", "Troms og Finnmark", "Troms", "Finnmark"]


def flat(s):
    return re.sub(r"\s+", " ", s).strip()


f = Path(sys.argv[1])
linjer = f.read_text(encoding="utf-8").splitlines()
for start in map(int, sys.argv[2:]):
    # til første "Kilde:" etter start (maks 400 linjer)
    slutt = start + 1
    while slutt < min(len(linjer), start + 400) and not linjer[slutt].strip().startswith("Kilde"):
        slutt += 1
    blokk = flat(" ".join(linjer[start:slutt]))
    blokk = re.sub(r"===== SIDE \d+ =====.*?Statistisk sentralbyrå \d+", " ", blokk)
    print("=" * 100)
    print(f"{f.name} L{start}–{slutt}")
    print("TOPP:", blokk[:520])
    for navn in RADER:
        # navn (evt. med fylkesnummer foran) etterfulgt av tall/skilletegn
        for m in re.finditer(r"(?:\b\d\d )?" + re.escape(navn) + r"(?![a-zæøå])\s*((?:[\d,:.\-–]+\s*){2,})", blokk):
            if navn == "Troms" and blokk[max(0, m.start() - 0):m.start() + 18].startswith("Troms og"):
                continue
            print(f"  {navn:18s}: {m.group(1).strip()}")
