"""Regresjonstest: Lødingen (1851) fra fetch_nav.py mot den kontrollerte Lødingen-leveransen.
Bruk: python analyse/nav/skript/regresjon_lodingen.py   (kode 0 = likt, 1 = avvik)
"""
import json, statistics, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
N = json.loads((R / "data/nav_kommuner.json").read_text(encoding="utf-8"))
L = json.loads((R / "kilder/lodingen_kontrollert.json").read_text(encoding="utf-8"))
k = N["kommuner"]["1851"]
avvik = []


def tall(d):
    return {int(m): v for m, v in (d or {}).items() if isinstance(v, (int, float))}


def sml(navn, ny, gml):
    a, b = tall(ny), tall(gml)
    if a != b:
        avvik.append(f"{navn}: ny {a} | kontrollert {b}")


for aar, r in L["helt_ledige"].items():
    n = k["helt_ledige"].get(aar, {}).get("mnd", {})
    sml(f"helt ledige {aar} antall", {m: v[0] for m, v in n.items()}, r.get("antall"))
    sml(f"helt ledige {aar} pst", {m: v[1] for m, v in n.items()}, r.get("pst"))
    l = N["landet"]["helt_ledige"].get(aar, {}).get("mnd", {})
    sml(f"helt ledige {aar} landet pst", {m: v[1] for m, v in l.items()}, r.get("landet_pst"))

for kat in ("aap", "nedsatt"):
    for aar, r in L[kat].items():
        if "antall" not in r:
            continue
        n = k[kat].get(aar, {}).get("mnd", {})
        sml(f"{kat} {aar} antall", {m: v[0] for m, v in n.items()}, r.get("antall"))
        sml(f"{kat} {aar} pst", {m: v[1] for m, v in n.items()}, r.get("pst"))
    for aar, r in L[kat].items():
        if "aarssnitt_antall" in r:
            n = k[kat][aar]
            if (n["antall"], n["pst"]) != (float(r["aarssnitt_antall"]), float(r["aarssnitt_pst"])):
                avvik.append(f"{kat} {aar} årssnitt: ny {n['antall'], n['pst']} | kontrollert {r['aarssnitt_antall'], r['aarssnitt_pst']}")

# Uføre: den kuraterte serien (UF i nav_leveranse.py): dato, antall, andel (2 des.), aldersstandardisert
UF = [("2010-12", 210, None, None), ("2011-12", 201, None, None), ("2012-12", 200, 15.2, None),
      ("2013-12", 192, 14.20, None), ("2014-12", 186, 14.44, None), ("2015-12", 193, 15.18, 12.8),
      ("2016-12", 214, 17.04, 13.8), ("2017-12", 213, 17.25, 14.0), ("2018-12", 210, 16.96, None),
      ("2019-12", 219, 18.29, None), ("2020-12", 219, 18.84, None), ("2021-12", 205, 18.49, None),
      ("2022-12", 197, 17.63, None), ("2023-12", 204, 17.80, None), ("2024-12", 195, 16.91, None),
      ("2025-09", 193, 17.89, None), ("2026-09", 191, 17.48, None)]
for d, a, p, s in UF:
    n = k["ufore"].get(d)
    if not n:
        avvik.append(f"uføre {d}: mangler i ny")
        continue
    ny = (n["antall"], None if n["pst"] is None else round(n["pst"] + 1e-9, 2), n.get("aldersstandardisert"))
    if ny != (a, p, s):
        avvik.append(f"uføre {d}: ny {ny} | kontrollert {(a, p, s)}")

for kat in ("alderspensjon", "minstepensjon"):
    for aar, r in L[kat].items():
        if k["pensjon"][aar][kat] != float(r["lodingen"]):
            avvik.append(f"{kat} {aar}: ny {k['pensjon'][aar][kat]} | kontrollert {r['lodingen']}")

print("\n".join(avvik) if avvik else "Lødingen: identisk med kontrollert leveranse")
sys.exit(1 if avvik else 0)
