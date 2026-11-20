#!/usr/bin/env python3
"""Pendling for de 80 kommunene (pakke B1 i analyse/PLAN-NARVIK-TEMAER.md).

Kilde: SSB 03321, sysselsatte 15–74 år per 4. kvartal etter bostedskommune og
arbeidsstedskommune, 2020 → siste år. To uttrekk per år:
  - bosted = en av de 80 kommunene, arbeidssted = alle  → utpendling og sysselsatte bosatte
  - arbeidssted = en av de 80, bosted = alle            → innpendling og arbeidsplasser
Kommunekoder føres fram til dagens inndeling med kommunenøkkelen i fetch_nav.py, slik at
Troms og Finnmark 2020–2023 (54xx) og 2024– (55xx/56xx) blir samme kommune. Pendling mellom
to koder som i dag er samme kommune, regnes som arbeid i egen kommune.

Skriver PENDLING_DATA i assets/data.js og analyse/pendling/data/pendling.json.
Bruk: python fetch_pendling.py
"""
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
sys.path.insert(0, str(HER))
from fetch_nav import FRAM, KODER  # noqa: E402
from fetch_skatt import post, meta, celler, it  # noqa: E402

FRA_AAR = 2020
TOPP = 6


def navn_rens(n):
    return re.sub(r"\s*\((?:\d{4})?-?(?:\d{4})?\)\s*$", "", n).strip()


def main():
    m = meta("03321")
    bo_var = next(v for v in m["variables"] if v["code"] == "Bokommuen")
    alle = bo_var["values"]
    navn = {k: navn_rens(t) for k, t in zip(bo_var["values"], bo_var["valueTexts"])}
    aar = [t for t in next(v for v in m["variables"] if v["code"] == "Tid")["values"] if re.fullmatch(r"\d{4}", t) and int(t) >= FRA_AAR]
    nn = [k for k in alle if (FRAM(k) or "") in KODER]
    g = lambda k: FRAM(k) or k  # gjeldende kode (delte kommuner beholder gammel kode; ingen etter 2020)

    ut = {k: {"aar": [], "bosatte": [], "arbeid": [], "ut": [], "inn": [], "ut_nn": []} for k in KODER}
    topp = {}
    # Fylkene og Nord-Norge: ut = bor i området og jobber utenfor, inn = motsatt, mellom = pendler mellom
    # to kommuner i området. ut_nn (fylker) = jobber i en annen kommune i Nord-Norge utenfor fylket.
    NIV = {"18": None, "55": None, "56": None, "NN": None}
    medl = {n: {k for k in KODER if n == "NN" or k[:2] == n} for n in NIV}
    fut = {n: {"aar": [], "bosatte": [], "arbeid": [], "ut": [], "inn": [], "mellom": [], "ut_nn": []} for n in NIV}
    ftopp = {}
    for a in aar:
        print(f"SSB 03321 {a} ...", flush=True)
        bo = defaultdict(lambda: defaultdict(float))    # bosted -> arbeidssted -> n
        arb = defaultdict(lambda: defaultdict(float))   # arbeidssted -> bosted -> n
        for k, v in celler(post("03321", [it("Bokommuen", nn), it("ArbstedKomm", alle), it("ContentsCode", ["Sysselsatte"]), it("Tid", [a])])):
            bo[g(k["Bokommuen"])][g(k["ArbstedKomm"])] += v
        for k, v in celler(post("03321", [it("Bokommuen", alle), it("ArbstedKomm", nn), it("ContentsCode", ["Sysselsatte"]), it("Tid", [a])])):
            arb[g(k["ArbstedKomm"])][g(k["Bokommuen"])] += v
        for k in KODER:
            b, w = bo.get(k, {}), arb.get(k, {})
            tb, tw = sum(b.values()), sum(w.values())
            if not tb:
                continue
            hjemme = b.get(k, 0)
            ut[k]["aar"].append(int(a))
            ut[k]["bosatte"].append(round(tb))
            ut[k]["arbeid"].append(round(tw))
            ut[k]["ut"].append(round(tb - hjemme))
            ut[k]["inn"].append(round(tw - w.get(k, 0)))
            ut[k]["ut_nn"].append(round(sum(v for d, v in b.items() if d != k and d in KODER)))
            if a == aar[-1]:
                topp[k] = {
                    "topp_ut": [[navn.get(d, d), round(v)] for d, v in sorted(b.items(), key=lambda x: -x[1]) if d != k and v > 0][:TOPP],
                    "topp_inn": [[navn.get(d, d), round(v)] for d, v in sorted(w.items(), key=lambda x: -x[1]) if d != k and v > 0][:TOPP],
                }
        for n, M in medl.items():
            tb = sum(sum(bo.get(k, {}).values()) for k in M)
            tw = sum(sum(arb.get(k, {}).values()) for k in M)
            ut_f = sum(v for k in M for d, v in bo.get(k, {}).items() if d not in M)
            inn_f = sum(v for k in M for d, v in arb.get(k, {}).items() if d not in M)
            mellom = sum(v for k in M for d, v in bo.get(k, {}).items() if d in M and d != k)
            fut[n]["aar"].append(int(a)); fut[n]["bosatte"].append(round(tb)); fut[n]["arbeid"].append(round(tw))
            fut[n]["ut"].append(round(ut_f)); fut[n]["inn"].append(round(inn_f)); fut[n]["mellom"].append(round(mellom))
            fut[n]["ut_nn"].append(None if n == "NN" else round(sum(v for k in M for d, v in bo.get(k, {}).items() if d not in M and d in KODER)))
            if a == aar[-1]:
                til, fra = defaultdict(float), defaultdict(float)
                for k in M:
                    for d, v in bo.get(k, {}).items():
                        if d not in M: til[d] += v
                    for d, v in arb.get(k, {}).items():
                        if d not in M: fra[d] += v
                ftopp[n] = {"topp_ut": [[navn.get(d, d), round(v)] for d, v in sorted(til.items(), key=lambda x: -x[1]) if v > 0][:TOPP],
                            "topp_inn": [[navn.get(d, d), round(v)] for d, v in sorted(fra.items(), key=lambda x: -x[1]) if v > 0][:TOPP]}
        time.sleep(1)
    D = {"hentet": time.strftime("%Y-%m-%d"), "kilde": "SSB 03321, sysselsatte 15–74 år per 4. kvartal etter bosteds- og arbeidsstedskommune",
         "aar": [int(a) for a in aar], "kommuner": {k: {**ut[k], **topp.get(k, {})} for k in KODER},
         "fylker": {n: {**fut[n], **ftopp.get(n, {})} for n in NIV}}
    mangler = [k for k in KODER if not ut[k]["aar"]]
    if mangler:
        print("MANGLER:", mangler)
    mappe = HER / "analyse" / "pendling" / "data"
    mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "pendling.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    djs = HER / "assets" / "data.js"
    js = djs.read_text(encoding="utf-8")
    blokk = "/* PENDLING_DATA BEGIN */\nconst PENDLING_DATA = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n/* PENDLING_DATA END */"
    if "/* PENDLING_DATA BEGIN */" in js:
        js = re.sub(r"/\* PENDLING_DATA BEGIN \*/.*?/\* PENDLING_DATA END \*/", lambda _m: blokk, js, flags=re.S)
    else:
        js = js.rstrip("\n") + "\n" + blokk + "\n"
    djs.write_text(js, encoding="utf-8")
    print(f"PENDLING_DATA skrevet ({len(blokk) // 1024} KB), år {aar[0]}–{aar[-1]}.")
    return D


if __name__ == "__main__":
    D = main()
    n = D["kommuner"]["1806"]
    print("Narvik:", {f: n[f] for f in ("aar", "bosatte", "arbeid", "ut", "inn", "ut_nn")})
    print("  topp ut:", n["topp_ut"])
    print("  topp inn:", n["topp_inn"])
    for f, v in D["fylker"].items():
        print(f, {x: v[x][-1] for x in ("bosatte", "arbeid", "ut", "inn", "mellom", "ut_nn")}, v["topp_ut"][:3])
