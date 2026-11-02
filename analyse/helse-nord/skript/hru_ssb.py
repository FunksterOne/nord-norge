#!/usr/bin/env python3
"""SSBs leveranse til Helsereformutvalget (2026) + SSB 07459 → data/hru_ssb.json (kompakt uttrekk til fetch_helse.py).

Kilder:
  - SSB for Helsereformutvalget: «aarsverk_p2003-p2025.xlsx» og «sykefravaer_p2015-p2025.xlsx», publisert på
    nettsteder.regjeringen.no/helsereformutvalget/rapporter/ (nr. 25 og 27), dokumentert i nr. 9. Filene ligger i
    kilder/helsereform/eksterne/ (ikke i git). Avtalte årsverk og legemeldt sykefravær, alle arbeidsforhold,
    geografi harmonisert til 2024-inndelingen. Brudd 2009 (SN2007) og 2015 (A-ordningen): serien brukes fra 2015.
  - SSB 07459: befolkning 1.1. etter alder (80 år og eldre) og kommunestørrelse 2026.

Nord-Norge = de 80 kommunene i Nordland, Troms og Finnmark (arbeidskommune 2024). Landet = alle rader.
Sykefravær: celler SSB har skjult er utelatt; prosenten vektes med mulige dagsverk.
Kjør fra repo-roten:  python analyse/helse-nord/skript/hru_ssb.py
"""
import collections, json, sys, urllib.request
from pathlib import Path
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
ROT = Path(__file__).resolve().parents[1]
KILDE = ROT / "kilder" / "helsereform" / "eksterne"
UT = ROT / "data" / "hru_ssb.json"
AAR = list(range(2015, 2026))
NN = lambda k: bool(k) and str(k)[:2] in ("18", "55", "56")
TJ = ["Kommunal helsetjeneste", "Kommunal omsorgstjeneste", "Spesialisthelsetjenesten"]
# Utdanningsgrupper i kommunal omsorg (SSBs gruppering, se dokumentasjonen avsnitt 6)
GRUPPER = {"syk": ("Sykepleier", "Sykepleier med videreutdanning"), "hfa": ("Helsefagarbeidere mv.",),
           "ufa": ("Ufaglært",)}


def ark(fil, navn):
    wb = openpyxl.load_workbook(KILDE / fil, read_only=True)
    rader = wb[navn].iter_rows(values_only=True)
    next(rader)
    return rader


def aarsverk():
    fil = "27.-SSB-Kopi-av-helsereformutvalget-aarsverk_p2003-p2025.xlsx"
    s = collections.defaultdict(float)
    for aar, tj, _sk, _sn, k, _kn, utd, av in ark(fil, "aarsverk_helsetj_komm_utd"):
        if aar not in AAR or tj not in TJ or not isinstance(av, (int, float)):
            continue
        for reg in (["nord"] if NN(k) else []) + ["landet"]:
            s[(reg, tj, aar)] += av
            if tj == "Kommunal omsorgstjeneste":
                for g, u in GRUPPER.items():
                    if utd in u:
                        s[(reg, g, aar)] += av
    # Kontroll: summen over kommuner skal stemme med SSBs landstall (eget ark)
    land = collections.defaultdict(float)
    for aar, tj, utd, av in ark(fil, "aarsverk_helsetj_utd"):
        if aar in AAR and tj in TJ and isinstance(av, (int, float)):
            land[(tj, aar)] += av
    for tj in TJ:
        for aar in (2015, 2025):
            a, b = s[("landet", tj, aar)], land[(tj, aar)]
            assert abs(a - b) / b < 0.01, (tj, aar, a, b)
    return {reg: {"total": {tj: [round(s[(reg, tj, a)]) for a in AAR] for tj in TJ},
                  "omsorg_utd": {g: [round(s[(reg, g, a)]) for a in AAR] for g in GRUPPER}}
            for reg in ("nord", "landet")}


def sykefravaer():
    fil = "25.-SSB-Kopi-av-helsereformutvalget-sykefravaer_p2015-p2025.xlsx"
    dv, fv, skjult = collections.defaultdict(float), collections.defaultdict(float), collections.Counter()
    for r in ark(fil, "sykefravaer_helsetj_opptak_utd"):
        aar, tj, rhf, _hf, _u, mulige, pst = r[:7]
        if tj not in TJ:
            continue
        if not isinstance(mulige, (int, float)) or not isinstance(pst, (int, float)):
            skjult[aar] += 1
            continue
        for reg in ([rhf] if rhf else []) + ["LANDET"]:
            dv[(reg, tj, aar)] += mulige
            fv[(reg, tj, aar)] += mulige * pst / 100
    navn = {"HELSE NORD RHF": "Helse Nord", "HELSE MIDT-NORGE RHF": "Helse Midt-Norge", "HELSE VEST RHF": "Helse Vest",
            "HELSE SØR-ØST RHF": "Helse Sør-Øst", "LANDET": "Landet"}
    return {"serie": {navn[reg]: {tj: [round(100 * fv[(reg, tj, a)] / dv[(reg, tj, a)], 2) for a in AAR] for tj in TJ}
                      for reg in navn},
            "skjulte_celler": {str(a): skjult[a] for a in AAR}}


def befolkning():
    """80+ i Nord-Norge og landet 2015 og 2025, og kommunestørrelser 1.1.2026 (SSB 07459)."""
    def hent(region, alder, tid):
        q = {"query": [{"code": "Region", "selection": {"filter": "item" if region != "*" else "all", "values": region if region != "*" else ["*"]}},
                       {"code": "Alder", "selection": {"filter": "item" if alder != "*" else "all", "values": alder if alder != "*" else ["*"]}},
                       {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Personer1"]}},
                       {"code": "Tid", "selection": {"filter": "item", "values": tid}}],
             "response": {"format": "json-stat2"}}
        req = urllib.request.Request("https://data.ssb.no/api/v0/no/table/07459", data=json.dumps(q).encode(),
                                     headers={"Content-Type": "application/json"})
        j = json.load(urllib.request.urlopen(req, timeout=300))
        dims, v = j["id"], j["value"]
        kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
        storr = [len(kat[d]) for d in dims]
        ut = collections.defaultdict(float)
        for i, x in enumerate(v):
            if not x:
                continue
            idx, rest = {}, i
            for d, n in zip(reversed(dims), reversed(storr)):
                idx[d] = kat[d][rest % n]
                rest //= n
            ut[(idx["Region"], idx.get("Alder"), idx["Tid"])] += x
        return ut
    alder80 = [f"{a:03d}" for a in range(80, 105)] + ["105+"]
    b = hent(["0", "18", "19", "20", "54", "55", "56"], alder80, ["2015", "2025"])
    a80 = {"nord": [sum(b[(r, al, "2015")] for r in ("18", "19", "20") for al in alder80),
                    sum(b[(r, al, "2025")] for r in ("18", "55", "56") for al in alder80)],
           "landet": [sum(b[("0", al, t)] for al in alder80) for t in ("2015", "2025")]}
    # Kommunestørrelse: summen over alder per kommune 2026
    q = hent("*", "*", ["2026"])
    pop = collections.defaultdict(float)
    for (reg, _al, _t), x in q.items():
        if len(reg) == 4 and reg.isdigit() and reg not in ("0000", "9999"):
            pop[reg] += x
    grenser = [5000, 10000, 15000, 20000]
    def tell(utvalg):
        tot = sum(utvalg.values())
        return {"antall": len(utvalg), "bef": round(tot),
                "under": {str(g): [sum(1 for x in utvalg.values() if x < g),
                                   round(100 * sum(x for x in utvalg.values() if x < g) / tot, 1)] for g in grenser}}
    nord = {k: x for k, x in pop.items() if NN(k)}
    assert len(nord) == 80 and len(pop) == 357, (len(nord), len(pop))
    return {"a80": {k: [round(x) for x in v] for k, v in a80.items()}, "a80_aar": [2015, 2025],
            "kommuner": {"aar": 2026, "nord": tell(nord), "landet": tell(pop)}}


def main():
    ut = {"aar": AAR, "aarsverk": aarsverk(), "sykefravaer": sykefravaer(), **befolkning(),
          "kilde": "SSB for Helsereformutvalget (2026): avtalte årsverk og legemeldt sykefravær; SSB 07459"}
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    o = ut["aarsverk"]
    for reg in ("nord", "landet"):
        t = o[reg]["total"]["Kommunal omsorgstjeneste"]
        print(reg, "omsorg", t[0], "->", t[-1], f"{100 * (t[-1] / t[0] - 1):.1f} %",
              "80+", ut["a80"][reg], "årsverk per 100 80+", round(100 * t[0] / ut["a80"][reg][0], 1), "->",
              round(100 * t[-1] / ut["a80"][reg][1], 1))
    print("sykefravær 2025", {r: v["Spesialisthelsetjenesten"][-1] for r, v in ut["sykefravaer"]["serie"].items()})
    print("kommuner", ut["kommuner"])
    print("skrev", UT)


if __name__ == "__main__":
    main()
