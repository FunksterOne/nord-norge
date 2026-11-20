#!/usr/bin/env python3
"""Sysselsetting 20–66 år for fylkene, Nord-Norge og landet (SSB 13563), 2020 → siste år.

Hovedstatus på arbeidsmarkedet (sysselsatte, registrerte ledige, under utdanning, AAP/uføretrygd,
AFP/alderspensjon, tiltak, andre) per 4. kvartal, alle og etter innvandrerkategori.

Troms (55) og Finnmark (56) finnes hver for seg i tabellen bare fra 2024. For 2020–2023 er de summen
av kommunene (kommunekodene føres fram med fetch_nav.FRAM), kontrollert mot SSBs tall for Troms og
Finnmark samlet (54). Nord-Norge er Nordland + Troms og Finnmark (SSBs fylkesrader).

Skriver SYSS_NIVAA i assets/data.js og analyse/sysselsetting/data/sysselsetting_nivaa.json.
Bruk: python fetch_sysselsetting_nivaa.py
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
STATUS = [("A.01", "Sysselsatte"), ("A.09", "Registrerte ledige"), ("U.01", "På arbeidsmarkedstiltak"),
          ("U.03", "Under utdanning"), ("U.04-U.05", "AAP eller uføretrygd"), ("U.06-U.07", "AFP eller alderspensjon"),
          ("U.90A", "Andre utenfor arbeidsstyrken")]
INNV = {"A-G": "alle", "A_C-G": "uten_innv", "B": "innv"}


def main():
    m = meta("13563")
    regvar = next(v for v in m["variables"] if v["code"] == "Region")
    gyldig = {}
    for kode, tekst in zip(regvar["values"], regvar["valueTexts"]):
        mm = re.search(r"\((\d{4})?-(\d{4})?\)\s*$", tekst)
        gyldig[kode] = (int(mm.group(1)) if mm and mm.group(1) else 0, int(mm.group(2)) if mm and mm.group(2) else 9999)
    aar = [t for t in next(v for v in m["variables"] if v["code"] == "Tid")["values"] if int(t) >= FRA_AAR]
    kom = [k for k in regvar["values"] if len(k) == 4 and k.isdigit() and (FRAM(k) or "")[:2] in ("55", "56")]
    statuskoder = ["TOT"] + [s for s, _ in STATUS]

    v = defaultdict(float)   # (nøkkel, innv, status, år) -> antall
    for regioner in (["0", "18", "54", "55", "56"], kom):
        d = post("13563", [it("Region", regioner), it("HovArbStyrkStatus", statuskoder), it("Alder", ["20-66"]),
                           it("InnvandrKat", list(INNV)), it("ContentsCode", ["Bosatte"]), it("Tid", aar)])
        for k, x in celler(d):
            r, t = k["Region"], k["Tid"]
            fra, til = gyldig.get(r, (0, 9999))
            if not fra <= int(t) <= til or x is None:
                continue
            nokkel = ("K" + FRAM(r)[:2]) if len(r) == 4 else {"0": "landet"}.get(r, r)
            v[(nokkel, INNV[k["InnvandrKat"]], k["HovArbStyrkStatus"], t)] += x
        time.sleep(1)

    # Troms og Finnmark 2020–2023 fra kommunene; kontroll mot SSBs tall for Troms og Finnmark samlet
    for t in aar:
        if int(t) >= 2024:
            continue
        for innv in INNV.values():
            for s in statuskoder:
                sum_k = v[("K55", innv, s, t)] + v[("K56", innv, s, t)]
                if abs(sum_k - v[("54", innv, s, t)]) > 0.5:
                    print(f"AVVIK {t} {innv} {s}: kommunene {sum_k} mot SSB 54 {v[('54', innv, s, t)]}")
                v[("55", innv, s, t)] = v[("K55", innv, s, t)]
                v[("56", innv, s, t)] = v[("K56", innv, s, t)]
    for t in aar:
        for innv in INNV.values():
            for s in statuskoder:
                v[("NN", innv, s, t)] = v[("18", innv, s, t)] + v[("55", innv, s, t)] + v[("56", innv, s, t)]

    siste = aar[-1]

    def pakk(n):
        ut = {"tot": [round(v[(n, "alle", "TOT", t)]) for t in aar],
              "syss": [round(v[(n, "alle", "A.01", t)]) for t in aar],
              "status": {s: round(v[(n, "alle", s, siste)]) for s, _ in STATUS}}
        for innv in ("uten_innv", "innv"):
            ut[innv] = {"tot": [round(v[(n, innv, "TOT", t)]) for t in aar],
                        "syss": [round(v[(n, innv, "A.01", t)]) for t in aar]}
        return ut

    D = {"hentet": time.strftime("%Y-%m-%d"),
         "kilde": "SSB 13563, befolkningen 20–66 år etter hovedstatus på arbeidsmarkedet, 4. kvartal",
         "aar": [int(t) for t in aar], "status": STATUS,
         "nivaa": {n: pakk(n) for n in ("18", "55", "56", "NN", "landet")}}
    mappe = HER / "analyse" / "sysselsetting" / "data"
    mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "sysselsetting_nivaa.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    djs = HER / "assets" / "data.js"
    js = djs.read_text(encoding="utf-8")
    blokk = "/* SYSS_NIVAA BEGIN */\nconst SYSS_NIVAA = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n/* SYSS_NIVAA END */"
    if "/* SYSS_NIVAA BEGIN */" in js:
        js = re.sub(r"/\* SYSS_NIVAA BEGIN \*/.*?/\* SYSS_NIVAA END \*/", lambda _m: blokk, js, flags=re.S)
    else:
        js = js.rstrip("\n") + "\n" + blokk + "\n"
    djs.write_text(js, encoding="utf-8")
    print(f"SYSS_NIVAA skrevet ({len(blokk) // 1024} KB), år {aar[0]}–{siste}.")
    return D


if __name__ == "__main__":
    D = main()
    for n, x in D["nivaa"].items():
        print(n, [f"{s / t * 100:.1f}" for s, t in zip(x["syss"], x["tot"])],
              "innv", f"{x['innv']['syss'][-1] / x['innv']['tot'][-1] * 100:.1f}",
              "uten", f"{x['uten_innv']['syss'][-1] / x['uten_innv']['tot'][-1] * 100:.1f}",
              "status-sum", sum(x["status"].values()), "tot", x["tot"][-1])
