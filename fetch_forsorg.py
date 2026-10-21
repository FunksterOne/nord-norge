#!/usr/bin/env python3
"""Forsørgerbyrde: demografisk og økonomisk, i dag og framskrevet → FORSORG_DATA i assets/data.js.

To mål, som ikke skal blandes:
  Forsørgerbrøk          Innbyggere 65+ per 100 i alderen 20–64 (SSB 14746, samme mål som SSB 14751 og OECD).
                         Teller alder, ikke arbeid.
  Ikke-sysselsatte per   Alle innbyggere som ikke er sysselsatt, per 100 sysselsatte (bosted). I dag: SSB 13563
  100 sysselsatte        (prioritert arbeidsstyrkestatus, 4. kvartal) og 07459 (barn 0–14, 1. januar året etter),
                         fordelt på hvorfor: barn, utdanning, AAP og uføretrygd, AFP og alderspensjon, ledige og tiltak, andre.

Framskriving 2026–2050 «alt annet likt»: sysselsettingsraten i seks aldersgrupper 15–74 (SSB 07984, bosted, snitt av
4. kvartal 2024 og 2025 delt på befolkningen 1. januar året etter) og for 75+ (SSB 13563, 2025) holdes fast og brukes på
befolkningsbanen i SSB 14746 (MMMM). To faste scenarioer:
  A  Andelen på arbeidsavklaringspenger og uføretrygd i alderen 20–66 senkes til landsnivået der den er høyere,
     og de som ikke lenger mottar ytelsen, er i arbeid.
  B  Sysselsettingsraten i alderen 55–74 er 5 prosentpoeng høyere.

Tidsserie 2015–2025 for status i alderen 20–66 hentes med SSBs kodeliste for sammenslåtte kommuner (agg_KommSummer);
Narvik og Hamarøy har tall fra 2020 (Tysfjord ble delt mellom dem).
Kjør:  python fetch_forsorg.py
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
V0 = "https://data.ssb.no/api/v0/no/table/"
V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/"
STATUS = [("syss", "A.01"), ("ledig", "A.09"), ("tiltak", "U.01"), ("utd", "U.03"), ("aapufo", "U.04-U.05"), ("pensjon", "U.06-U.07"), ("andre", "U.90A")]
G6 = [(15, 19, "15-19"), (20, 24, "20-24"), (25, 39, "25-39"), (40, 54, "40-54"), (55, 66, "55-66"), (67, 74, "67-74")]
AAR = list(range(2026, 2051))
TREND = [str(a) for a in range(2015, 2026)]
FYLKE = {"18": "Nordland", "55": "Troms", "56": "Finnmark"}


def post(tab, q):
    req = urllib.request.Request(V0 + tab, data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read().decode("utf-8"))


def get_v2(tab, params):
    with urllib.request.urlopen(V2 + tab + "/data?" + urllib.parse.urlencode({"lang": "no", "outputFormat": "json-stat2", **params}), timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def celler(d):
    ids = d["id"]
    keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
    for n, v in enumerate(d["value"]):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1):
            co[ids[i]] = keys[i][rest % d["size"][i]]
            rest //= d["size"][i]
        yield co, v


it = lambda c, v: {"code": c, "selection": {"filter": "item", "values": v}}
al = lambda c: {"code": c, "selection": {"filter": "all", "values": ["*"]}}


def alder(co):
    return int(co["Alder"].replace("+", ""))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    js = DATA_JS.read_text(encoding="utf-8")
    linje = next(l for l in js.split("\n") if l.startswith("const DATA = "))
    koder = sorted(json.loads(linje[len("const DATA = "):].rstrip(";"))["proj"]["kommuner"].keys())
    assert len(koder) == 80
    reg = koder + ["0"]

    print("SSB 13563 (status 2025) ...", flush=True)
    S = {}
    for co, v in celler(post("13563", [it("Region", reg), al("HovArbStyrkStatus"), it("Alder", ["15+", "15-74", "20-66", "62+"]),
                                       it("InnvandrKat", ["A-G"]), al("ContentsCode"), it("Tid", ["2025"])])):
        S[(co["Region"], co["HovArbStyrkStatus"], co["Alder"])] = v or 0

    print("SSB 07459 (befolkning 1.1.2025 og 2026) ...", flush=True)
    B = {}
    for co, v in celler(post("07459", [it("Region", reg), al("Kjonn"), al("Alder"), it("ContentsCode", ["Personer1"]), it("Tid", ["2025", "2026"])])):
        k = (co["Region"], co["Tid"], alder(co))
        B[k] = B.get(k, 0) + (v or 0)
    bef = lambda r, t, lo, hi: sum(B.get((r, t, a), 0) for a in range(lo, hi + 1))

    print("SSB 07984 (sysselsatte etter alder 2024–2025) ...", flush=True)
    SY = {}
    for co, v in celler(post("07984", [it("Region", reg), it("NACE2007", ["00-99"]), it("Kjonn", ["0"]), it("Alder", [g[2] for g in G6]),
                                       it("ContentsCode", ["Sysselsatte"]), it("Tid", ["2024", "2025"])])):
        SY[(co["Region"], co["Alder"], co["Tid"])] = v or 0

    print("SSB 14746 (befolkning 2026–2050, MMMM) ...", flush=True)
    P = {}
    for bit in (AAR[:9], AAR[9:17], AAR[17:]):
        for co, v in celler(post("14746", [it("Region", reg), al("Kjonn"), al("Alder"), it("ContentsCode", ["Personer"]), it("Tid", [str(a) for a in bit])])):
            if v is None:
                continue
            k = (co["Region"], int(co["Tid"]), alder(co))
            P[k] = P.get(k, 0) + v
    pp = lambda r, t, lo, hi: sum(P.get((r, t, a), 0) for a in range(lo, hi + 1))

    print("SSB 13563 v2 (trend 2015–2025, sammenslåtte kommuner) ...", flush=True)
    T = {}
    felles = {"valueCodes[HovArbStyrkStatus]": "TOT,A.01,U.04-U.05", "valueCodes[Alder]": "20-66", "valueCodes[InnvandrKat]": "A-G",
              "valueCodes[ContentsCode]": "Bosatte", "valueCodes[Tid]": ",".join(TREND)}
    par = dict(felles)
    par["codelist[Region]"] = "agg_KommSummer"
    par["valueCodes[Region]"] = ",".join("K-" + k for k in koder)
    for co, v in celler(get_v2("13563", par)):
        T[(co["Region"][2:], co["HovArbStyrkStatus"], co["Tid"])] = v
    for co, v in celler(get_v2("13563", {**felles, "valueCodes[Region]": "0"})):
        T[("0", co["HovArbStyrkStatus"], co["Tid"])] = v

    # ── Per kommune ──
    L_aapufo = S[("0", "U.04-U.05", "20-66")] / S[("0", "TOT", "20-66")]
    ut, komp = {}, {}

    def rater(r):
        rr = []
        for lo, hi, g in G6:
            n = bef(r, "2025", lo, hi) + bef(r, "2026", lo, hi)
            rr.append((lo, hi, (SY.get((r, g, "2024"), 0) + SY.get((r, g, "2025"), 0)) / n if n else 0))
        n75 = bef(r, "2026", 75, 120)
        s75 = max(0, S.get((r, "A.01", "15+"), 0) - S.get((r, "A.01", "15-74"), 0))
        rr.append((75, 120, s75 / n75 if n75 else 0))
        return rr

    def bane(r, rr, gap):
        syss, sA, sB, tot, a65, a2064 = [], [], [], [], [], []
        for t in AAR:
            s = sum(q * pp(r, t, lo, hi) for lo, hi, q in rr)
            syss.append(s)
            sA.append(s + gap * pp(r, t, 20, 66))
            sB.append(s + 0.05 * pp(r, t, 55, 74))
            tot.append(pp(r, t, 0, 120)); a65.append(pp(r, t, 65, 120)); a2064.append(pp(r, t, 20, 64))
        return {"syss": syss, "sA": sA, "sB": sB, "tot": tot, "a65": a65, "a2064": a2064}

    for r in reg:
        rr = rater(r)
        gap = 0.0 if r == "0" else max(0.0, S[(r, "U.04-U.05", "20-66")] / S[(r, "TOT", "20-66")] - L_aapufo)
        komp[r] = {
            "s2066": [S[(r, "TOT", "20-66")]] + [S[(r, c, "20-66")] for _, c in STATUS],
            "s15": [S[(r, "TOT", "15+")]] + [S[(r, c, "15+")] for _, c in STATUS],
            "syss62": S[(r, "A.01", "62+")],
            "bef": {"tot": bef(r, "2026", 0, 120), "u15": bef(r, "2026", 0, 14), "a2064": bef(r, "2026", 20, 64), "a65": bef(r, "2026", 65, 120),
                    "a2066": bef(r, "2026", 20, 66), "a67": bef(r, "2026", 67, 120)},
            "bane": bane(r, rr, gap), "gapA": gap,
        }

    def summer(rs):
        o = {"s2066": [sum(komp[r]["s2066"][i] for r in rs) for i in range(8)], "s15": [sum(komp[r]["s15"][i] for r in rs) for i in range(8)],
             "syss62": sum(komp[r]["syss62"] for r in rs), "bef": {k: sum(komp[r]["bef"][k] for r in rs) for k in komp[rs[0]]["bef"]},
             "bane": {k: [sum(komp[r]["bane"][k][i] for r in rs) for i in range(len(AAR))] for k in komp[rs[0]]["bane"]}}
        return o

    grupper = {nr: [k for k in koder if k[:2] == nr] for nr in FYLKE}
    for nr, navn in FYLKE.items():
        komp[navn] = summer(grupper[nr])
    komp["nn"] = summer(koder)
    komp["landet"] = komp.pop("0")

    def trend(r):
        """Andel sysselsatte og andel på AAP/uføretrygd, 20–66 år. Fylker og landsdel er summen av kommunene;
        år der en kommune mangler tall (Narvik og Hamarøy før 2020), står tomme."""
        rs = ["0"] if r == "landet" else koder if r == "nn" else grupper[{v: k for k, v in FYLKE.items()}[r]] if r in FYLKE.values() else [r]
        def sum_(c, a):
            vs = [T.get((x, c, a)) for x in rs]
            return None if any(not v for v in vs) else sum(vs)
        tot = [sum_("TOT", a) for a in TREND]
        f = lambda c: [round(100 * v / n, 1) if v and n else None for v, n in zip([sum_(c, a) for a in TREND], tot)]
        return {"syss": f("A.01"), "aapufo": f("U.04-U.05")}

    r1 = lambda xs: [round(x, 1) for x in xs]
    for r, c in komp.items():
        b = c["bane"]
        ok = lambda s: [(t - x) / x * 100 for t, x in zip(b["tot"], s)]
        ut[r] = {
            "s2066": c["s2066"], "s15": c["s15"], "syss62": c["syss62"], "bef": c["bef"],
            "demo": r1([100 * a / w for a, w in zip(b["a65"], b["a2064"])]),
            "okon": r1(ok(b["syss"])), "okonA": r1(ok(b["sA"])), "okonB": r1(ok(b["sB"])),
            "syss": [round(x) for x in b["syss"]], "syssA2050": round(b["sA"][-1]), "syssB2050": round(b["sB"][-1]),
            "trend": trend(r),
        }

    # ── Kontroller ──
    feil = []
    for r, c in komp.items():
        for nokkel in ("s2066", "s15"):
            if abs(sum(c[nokkel][1:]) - c[nokkel][0]) > 0:
                feil.append(f"{r} {nokkel}: statusene summerer til {sum(c[nokkel][1:])}, total {c[nokkel][0]}")
    m = re.search(r"const ELDRE_DATA = (\{.*?\});\n/\* ELDRE_DATA END", js, re.S)
    if m:
        E = json.loads(m.group(1))
        avvik = [(k, ut[k]["demo"][0], E["kommuner"][k][13], ut[k]["demo"][-1], E["kommuner"][k][14]) for k in koder
                 if abs(ut[k]["demo"][0] / 100 - E["kommuner"][k][13]) > 0.006 or abs(ut[k]["demo"][-1] / 100 - E["kommuner"][k][14]) > 0.006]
        if avvik:
            feil.append(f"forsørgerbrøk avviker fra SSB 14751 i {len(avvik)} kommuner: {avvik[:3]}")
    nn = ut["nn"]
    i_dag = (nn["bef"]["tot"] - nn["s15"][1]) / nn["s15"][1] * 100
    print(f"Kontroll: Nord-Norge i dag {i_dag:.1f} (13563), framskrevet 2026 {nn['okon'][0]} — avvik {nn['okon'][0] - i_dag:+.1f}")
    if feil:
        print("ADVARSEL:\n  " + "\n  ".join(feil))

    payload = {
        "hentet": "2026-10-21", "aar": AAR, "trend_aar": [int(a) for a in TREND], "status_aar": 2025, "bef_dato": "2026-01-01",
        "status": [s for s, _ in STATUS],
        "status_navn": {"syss": "I arbeid", "ledig": "Registrert ledig", "tiltak": "På arbeidsmarkedstiltak", "utd": "Under utdanning",
                        "aapufo": "Arbeidsavklaringspenger eller uføretrygd", "pensjon": "AFP eller alderspensjon", "andre": "Andre utenfor arbeid"},
        "landet_aapufo_pct": round(100 * L_aapufo, 3),
        "scenario": {"A": "Andelen på arbeidsavklaringspenger og uføretrygd (20–66 år) senkes til landsnivået der den er høyere, og de som ikke lenger mottar ytelsen, er i arbeid",
                     "B": "Sysselsettingsraten i alderen 55–74 år er 5 prosentpoeng høyere"},
        "regioner": ut,
    }
    js_lit = "const FORSORG_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* FORSORG_DATA BEGIN */", "/* FORSORG_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in js:
        new = re.sub(r"/\* FORSORG_DATA BEGIN \*/.*?/\* FORSORG_DATA END \*/", lambda _m: block, js, flags=re.DOTALL)
    elif "/* ELDRE_DATA END */" in js:
        new = js.replace("/* ELDRE_DATA END */", "/* ELDRE_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret ELDRE_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    L = ut["landet"]
    print(f"Injected FORSORG_DATA ({len(js_lit)} tegn). Nord-Norge: forsørgerbrøk {nn['demo'][0]} → {nn['demo'][-1]}, "
          f"ikke-sysselsatte per 100 sysselsatte {nn['okon'][0]} → {nn['okon'][-1]} (A {nn['okonA'][-1]}, B {nn['okonB'][-1]}); "
          f"landet {L['demo'][0]} → {L['demo'][-1]}, {L['okon'][0]} → {L['okon'][-1]}")


if __name__ == "__main__":
    main()
