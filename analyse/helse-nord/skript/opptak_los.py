"""Kontroll av opptaksområder (somatikk) per kommune mot SSB 13982.

SSB 13982 gir befolkning per lokalsykehusområde (kodeliste vs_HelseOpptakSom, S01–S11 for Helse Nord),
men ikke hvilke kommuner som inngår. Skriptet finner alle fordelinger av de usikre kommunene som gir
nøyaktig SSBs folketall (07459, 1. januar) i hvert område og hvert år. Én entydig løsning over flere år
regnes som bekreftelse av fordelingen.

Kjør: python -X utf8 opptak_los.py   (krever kilder/data/ssb_13982_lokalsykehus_som.json og folketall_kommuner.json)
"""
import json, os, sys
from ssb import RAA, celler

d = json.load(open(os.path.join(RAA, "ssb_13982_lokalsykehus_som.json"), encoding="utf-8"))
MAAL = {}
for co, v in celler(d):
    MAAL.setdefault(co["Tid"], {}).setdefault(co["HelseReg"], 0)
    MAAL[co["Tid"]][co["HelseReg"]] += v or 0
P = json.load(open(os.path.join(RAA, "folketall_kommuner.json"), encoding="utf-8"))

# Lurøy (1834) er delt i SSB 13982. Delene bygges av grunnkretser (SSB 04317):
# fastlandet (Røytvik, Klevhals–Bratlandselv, Bratlandselv–Olvik, Kvinen, Konsvik, Aspdal–Rødøy) og øyene (resten).
_g = json.load(open(os.path.join(RAA, "ssb_04317_grunnkrets_utvalg.json"), encoding="utf-8"))
GK = {}
for co, v in celler(_g):
    GK.setdefault(co["Grunnkretser"], {})[co["Tid"]] = v or 0
LUROY_FAST = ["18340101", "18340102", "18340103", "18340105", "18340106", "18340107"]
P["1834f"] = {"navn": "Lurøy fastland", **{a: sum(GK[g][a] for g in LUROY_FAST) for a in ("2024", "2025", "2026")}}
P["1834o"] = {"navn": "Lurøy øyene", **{a: P["1834"][a] - P["1834f"][a] for a in ("2024", "2025", "2026")}}
# Restpost: innbyggere i UNN Harstads kommuner som SSB regner til Narvik (S04). Ikke stedfestet.
REST_S04 = {"2024": 735, "2025": 734, "2026": 835}

# Kandidater per kommune. Én kandidat = antatt sikker; flere = prøves.
# S25 Namsos tas med for Bindal; Trøndelag-kommunene i Namsos-området er listet som faste.
K = {
    # Finnmark
    "5601": "S01", "5603": "S01", "5612": "S01", "5616": "S01", "5618": "S01", "5620": "S01", "5622": "S01",
    "5614": "S01 S05", "5610": "S01 S02", "5624": "S01 S02", "5626": "S01 S02", "5628": "S01 S02",
    "5605": "S02", "5607": "S02", "5630": "S02", "5632": "S02", "5634": "S02", "5636": "S02",
    # Troms
    "5501": "S05", "5534": "S05", "5532": "S05", "5536": "S05", "5538": "S05", "5540": "S05", "5542": "S05",
    "5544": "S05", "5546": "S05 S01", "5524": "S05", "5530": "S05", "5526": "S05", "5528": "S05",
    "5520": "S05 S03", "5522": "S05 S03", "5518": "S05 S03", "5516": "S05 S03 S04", "5514": "S03 S04",
    "5512": "S03 S04", "5503": "S03", "5510": "S03",
    # Ofoten, Vesterålen, Lofoten, Salten
    "1806": "S04", "1853": "S04 S03", "1851": "S04 S03 S08", "1875": "S04 S06", "1871": "S08 S03",
    "1866": "S08", "1867": "S08", "1868": "S08", "1870": "S08",
    "1860": "S07", "1865": "S07", "1859": "S07", "1874": "S07", "1856": "S07 S06", "1857": "S07 S06",
    "1804": "S06", "1838": "S06", "1839": "S06", "1840": "S06", "1841": "S06", "1845": "S06", "1848": "S06",
    "1837": "S06 S09",
    # Helgeland
    "1836": "S06 S09", "1834f": "S09 S11", "1834o": "S09 S11", "1835": "S09 S11", "1828": "S09 S11", "1832": "S09 S10",
    "1833": "S09", "1824": "S10 S09 S11", "1825": "S10 S09 S11", "1826": "S10 S09 S11", "1822": "S10 S11 S09",
    "1818": "S11", "1827": "S11", "1820": "S11", "1816": "S11 S10 S09", "1813": "S11", "1812": "S11",
    "1815": "S11", "1811": "S11 S25",
    # Namsos-området (Trøndelag), faste
    "5007": "S25", "5060": "S25", "5052": "S25", "5049": "S25", "5047": "S25", "5046": "S25", "5045": "S25",
    "5044": "S25", "5043": "S25", "5042": "S25", "5020": "S25 X", "5041": "S25 X",
}
OMR = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S25"]


def los(aar):
    kand = {k: v.split() for k, v in K.items()}
    if aar == ["2026"]:
        kand = {k: [o for o in c if o != "S10"] or c for k, c in kand.items()}
    faste = {k: c[0] for k, c in kand.items() if len(c) == 1}
    usikre = sorted([k for k, c in kand.items() if len(c) > 1], key=lambda k: -P[k][aar[0]])
    base = {(a, o): 0 for a in aar for o in OMR}
    for k, o in faste.items():
        for a in aar:
            base[(a, o)] += P[k][a]
    for a in aar:
        base[(a, "S04")] += REST_S04[a]
        base[(a, "S03")] -= REST_S04[a]
    losn = []

    def dfs(i, s, valg):
        for a in aar:
            for o in OMR:
                if s[(a, o)] > MAAL[a][o]:
                    return
        if i == len(usikre):
            if all(s[(a, o)] == MAAL[a][o] for a in aar for o in OMR):
                losn.append(dict(valg))
            return
        # nedre grense: resten kan ikke nå målet
        k = usikre[i]
        for o in kand[k]:
            s2 = dict(s)
            if o != "X":
                for a in aar:
                    s2[(a, o)] += P[k][a]
            valg[k] = o
            dfs(i + 1, s2, valg)
        valg.pop(k, None)

    dfs(0, base, {})
    return faste, losn


if __name__ == "__main__":
    ut = {}
    for aar in (["2024", "2025"], ["2026"]):
        if aar == ["2026"]:  # S10 Mosjøen er tom i 2026: tillat Vefsn/Grane/Hattfjelldal/Hemnes/Vevelstad/Leirfjord andre steder
            pass
        faste, losn = los(aar)
        print(f"År {aar}: {len(losn)} løsning(er)")
        for l in losn[:5]:
            print("  ", {k + " " + P[k]["navn"]: v for k, v in sorted(l.items())})
        ut[",".join(aar)] = {"faste": faste, "losninger": losn}
    json.dump(ut, open(os.path.join(RAA, "opptak_losninger.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
