"""Forsørgerbyrde: demografisk (65+/20-64) mot økonomisk (ikke-sysselsatte per sysselsatt), Nord-Norge og landet, 2025.
Kilder: SSB 13563 (status 15+, 4. kv. 2025), 07459 (1.1.2026, 0-14 og aldersgrupper), 06445 (sysselsettingsrater etter alder, kommune).
"""
import json, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
UT = Path(sys.argv[1]); UT.mkdir(exist_ok=True)
KODER = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822","1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837","1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859","1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503","5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530","5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605","5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628","5630","5632","5634","5636"]


def post(tab, q, navn):
    f = UT / f"{navn}.json"
    if f.exists(): return json.loads(f.read_text(encoding='utf-8'))
    req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{tab}", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(), headers={"Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=600).read().decode('utf-8')); f.write_text(json.dumps(d), encoding='utf-8'); return d


def celler(d):
    ids = d["id"]; keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
    for n, v in enumerate(d["value"]):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1): co[ids[i]] = keys[i][rest % d["size"][i]]; rest //= d["size"][i]
        yield co, v


it = lambda c, v: {"code": c, "selection": {"filter": "item", "values": v}}
al = lambda c: {"code": c, "selection": {"filter": "all", "values": ["*"]}}
REG = KODER + ["0"]
S = {}
for co, v in celler(post("13563", [it("Region", REG), al("HovArbStyrkStatus"), al("Alder"), it("InnvandrKat", ["A-G"]), al("ContentsCode"), it("Tid", ["2025"])], "f13563")):
    S[(co["Region"], co["HovArbStyrkStatus"], co["Alder"])] = v or 0
P = {}
for co, v in celler(post("07459", [it("Region", REG), al("Kjonn"), al("Alder"), it("ContentsCode", ["Personer1"]), it("Tid", ["2026"])], "f07459_2026")):
    a = int(co["Alder"].replace("+", "")); P[(co["Region"], a)] = P.get((co["Region"], a), 0) + (v or 0)
pop = lambda regs, lo, hi: sum(P.get((r, a), 0) for r in regs for a in range(lo, hi + 1))
st = lambda regs, s, alder: sum(S.get((r, s, alder), 0) for r in regs)

STAT = [("A.01", "Sysselsatte"), ("A.09", "Registrerte ledige"), ("U.01", "Tiltak"), ("U.03", "Utdanning"), ("U.04-U.05", "AAP og uføretrygd"), ("U.06-U.07", "AFP og alderspensjon"), ("U.90A", "Andre")]
for navn, regs in (("Nord-Norge", KODER), ("Landet", ["0"])):
    print(f"\n=== {navn}")
    tot = pop(regs, 0, 120)
    a2064, a65, a2066, a67, u20, u15 = pop(regs, 20, 64), pop(regs, 65, 120), pop(regs, 20, 66), pop(regs, 67, 120), pop(regs, 0, 19), pop(regs, 0, 14)
    syss15 = st(regs, "A.01", "15+"); syss2066 = st(regs, "A.01", "20-66")
    print(f"Befolkning 1.1.2026 {tot}; 0-14 {u15}; 0-19 {u20}; 20-64 {a2064}; 65+ {a65}; 20-66 {a2066}; 67+ {a67}")
    print(f"1 Demografisk 65+/20-64: {a65/a2064*100:.1f}   67+/20-66: {a67/a2066*100:.1f}   total (0-19 + 65+)/20-64: {(u20+a65)/a2064*100:.1f}")
    print(f"2 Dagens justerte: 65+/(20-64 x syssrate20-66) = {a65/(a2064*syss2066/st(regs,'TOT','20-66'))*100:.1f}  (syssrate 20-66 {syss2066/st(regs,'TOT','20-66')*100:.1f} %)")
    print(f"3 Økonomisk: ikke-sysselsatte per 100 sysselsatte (alle aldre) = {(tot-syss15)/syss15*100:.1f}  (sysselsatte 15+ {syss15}, befolkning 15+ i 13563 {st(regs,'TOT','15+')})")
    print("  Fordeling per 100 sysselsatte: barn 0-14", round(u15 / syss15 * 100, 1),
          *[f"| {t} {st(regs, s, '15+')/syss15*100:.1f}" for s, t in STAT[1:]])
    print("  20-66 status (antall og %):", *[f"{t} {st(regs, s, '20-66')} ({st(regs, s, '20-66')/st(regs,'TOT','20-66')*100:.1f} %)" for s, t in STAT])
    print("  62+ sysselsatte", st(regs, "A.01", "62+"), "av", st(regs, "TOT", "62+"))
