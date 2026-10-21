"""Overslag: økonomisk forsørgerbyrde 2026-2050 med konstante aldersspesifikke sysselsettingsrater (SSB 07984 bosted 2025 / 07459 1.1.2026) på SSB 14746."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
H = Path(__file__).parent
sys.path.insert(0, str(H))
from forsorg import post, celler, it, al, KODER  # noqa (bufret)

G = [(15, 19, "15-19"), (20, 24, "20-24"), (25, 39, "25-39"), (40, 54, "40-54"), (55, 66, "55-66"), (67, 74, "67-74")]
REG = KODER + ["0"]
SY = {}
for co, v in celler(post("07984", [it("Region", REG), it("NACE2007", ["00-99"]), it("Kjonn", ["0"]), it("Alder", [g[2] for g in G]), it("ContentsCode", ["Sysselsatte"]), it("Tid", ["2025"])], "f07984_alder")):
    SY[(co["Region"], co["Alder"])] = v or 0
P0 = {}
for co, v in celler(post("07459", [it("Region", REG), al("Kjonn"), al("Alder"), it("ContentsCode", ["Personer1"]), it("Tid", ["2026"])], "f07459_2026")):
    a = int(co["Alder"].replace("+", "")); P0[(co["Region"], a)] = P0.get((co["Region"], a), 0) + (v or 0)
F = json.loads((H / "eldre_ssb" / "f14746.json").read_text(encoding='utf-8'))
PF = {}
for co, v in celler(F):
    if v is None: continue
    a = int(co["Alder"].replace("+", "")); PF[(co["Region"], co["Tid"], a)] = PF.get((co["Region"], co["Tid"], a), 0) + v

for navn, regs in (("Nord-Norge", KODER), ("Landet", ["0"])):
    rad = []
    for t in ("2026", "2030", "2040", "2050"):
        tot = syss = a65 = a2064 = 0
        for r in regs:
            pop = lambda lo, hi: sum(PF.get((r, t, a), 0) for a in range(lo, hi + 1))
            tot += pop(0, 120); a65 += pop(65, 120); a2064 += pop(20, 64)
            for lo, hi, g in G:
                p0 = sum(P0.get((r, a), 0) for a in range(lo, hi + 1))
                if p0: syss += SY.get((r, g), 0) / p0 * pop(lo, hi)
        rad.append(f"{t}: demografisk {a65/a2064*100:.1f} | økonomisk {(tot-syss)/syss*100:.1f} (sysselsatte {syss:,.0f})")
    print(navn); [print("  ", x) for x in rad]
    rates = {g: sum(SY.get((r, g), 0) for r in regs) / sum(P0.get((r, a), 0) for r in regs for a in range(lo, hi + 1)) * 100 for lo, hi, g in G}
    print("   rater 2025:", {k: round(v, 1) for k, v in rates.items()})
