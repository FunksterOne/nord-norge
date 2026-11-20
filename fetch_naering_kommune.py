#!/usr/bin/env python3
"""Sysselsatte etter næring per kommune, 2020 → siste år (SSB 07984).

Arbeidsplasser (sysselsatte etter arbeidssted) for 17 næringer og i alt, for de 80 kommunene,
Nord-Norge og landet, 4. kvartal, 15–74 år. For siste år også sysselsatte etter bosted.
SSB skjuler tall som kan føres tilbake til enkeltbedrifter; de lagres som null og listes under
«skjult», og regnes aldri som 0. Summen «Alle næringer» er SSBs egen og omfatter de skjulte.

Kommunekoder føres fram til dagens inndeling med kommunenøkkelen i fetch_nav.py (Troms og Finnmark
2020–2023). Nord-Norge = Nordland + Troms og Finnmark (2020–2023) eller Nordland + Troms + Finnmark.

Skriver NAERING_K i assets/data.js og analyse/naering/data/naering_kommune.json.
Bruk: python fetch_naering_kommune.py
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
from fetch_skatt import post, meta, it  # noqa: E402

FRA_AAR = 2020
KORT = {  # korte, norske navn til figurene
    "01-03": "Jordbruk, skogbruk og fiske", "05-09": "Bergverk og utvinning", "10-33": "Industri",
    "35-39": "Kraft, vann og renovasjon", "41-43": "Bygg og anlegg", "45-47": "Varehandel",
    "49-53": "Transport og lagring", "55-56": "Overnatting og servering", "58-63": "Informasjon og kommunikasjon",
    "64-66": "Finans og forsikring", "68-75": "Eiendom og teknisk tjenesteyting", "77-82": "Forretningsmessig tjenesteyting",
    "84": "Offentlig administrasjon og forsvar", "85": "Undervisning", "86-88": "Helse og sosialtjenester",
    "90-99": "Personlig tjenesteyting", "00": "Uoppgitt",
}


def celler_status(d):
    """json-stat2 → liste av ({dim: kode}, verdi, status)."""
    ids, storr = d["id"], d["size"]
    dims = []
    for i in ids:
        ix = d["dimension"][i]["category"]["index"]
        dims.append(sorted(ix, key=ix.get) if isinstance(ix, dict) else ix)
    status = d.get("status") or {}
    ut = []
    for n, v in enumerate(d["value"]):
        rest, koord = n, {}
        for i in range(len(ids) - 1, -1, -1):
            koord[ids[i]] = dims[i][rest % storr[i]]
            rest //= storr[i]
        ut.append((koord, v, status.get(str(n)) if isinstance(status, dict) else (status[n] if n < len(status) else None)))
    return ut


def main():
    m = meta("07984")
    regvar = next(v for v in m["variables"] if v["code"] == "Region")
    reg = regvar["values"]
    # Gyldighet fra teksten: «Narvik (-2019)», «Senja (2020-2023)». Koder utenfor perioden har nuller i
    # tabellen og må ikke legges sammen med dagens kode (de ville fylt hull der SSB har skjult tallet).
    gyldig = {}
    for kode, tekst in zip(regvar["values"], regvar["valueTexts"]):
        mm = re.search(r"\((\d{4})?-(\d{4})?\)\s*$", tekst)
        gyldig[kode] = (int(mm.group(1)) if mm and mm.group(1) else 0, int(mm.group(2)) if mm and mm.group(2) else 9999)
    aar = [t for t in next(v for v in m["variables"] if v["code"] == "Tid")["values"] if int(t) >= FRA_AAR]
    naer = [k for k in next(v for v in m["variables"] if v["code"] == "NACE2007")["values"] if k != "00-99"]
    kommuner = [k for k in reg if len(k) == 4 and k.isdigit() and FRAM(k) in KODER]
    regioner = kommuner + ["0", "18", "54", "55", "56"]
    print("SSB 07984 ...", flush=True)
    d = post("07984", [it("Region", regioner), it("NACE2007", ["00-99"] + naer), it("Kjonn", ["0"]), it("Alder", ["15-74"]),
                       it("ContentsCode", ["SysselsatteArb", "Sysselsatte"]), it("Tid", aar)])
    # verdi[(region, innhold, næring, år)] = tall eller None (skjult)
    arb = defaultdict(dict)    # nøkkel -> {(næring, år): v}
    bo = defaultdict(dict)
    skj = defaultdict(set)     # (nøkkel, år) -> næringer skjult (arbeidssted)
    for k, v, st in celler_status(d):
        r = k["Region"]
        fra, til = gyldig.get(r, (0, 9999))
        if not fra <= int(k["Tid"]) <= til:
            continue
        nokkel = FRAM(r) if len(r) == 4 else {"0": "landet"}.get(r, "F" + r)
        mål = arb if k["ContentsCode"] == "SysselsatteArb" else bo
        cell = (k["NACE2007"], k["Tid"])
        if v is None:
            if mål is arb and nokkel in KODER and k["NACE2007"] != "00-99":
                skj[(nokkel, k["Tid"])].add(k["NACE2007"])
            continue
        if cell in mål[nokkel] and nokkel in KODER:  # to koder samme kommune samme år: summer
            mål[nokkel][cell] += v
        else:
            mål[nokkel][cell] = v
    # Nord-Norge fra fylkene
    for t in aar:
        deler = ["F18", "F54"] if int(t) <= 2023 else ["F18", "F55", "F56"]
        for n in ["00-99"] + naer:
            vals = [arb[f].get((n, t)) for f in deler]
            if all(x is not None for x in vals):
                arb["NN"][(n, t)] = sum(vals)
            valsb = [bo[f].get((n, t)) for f in deler]
            if all(x is not None for x in valsb):
                bo["NN"][(n, t)] = sum(valsb)
    siste = aar[-1]

    def pakk(nokkel):
        return {"arb": {n: [arb[nokkel].get((n, t)) for t in aar] for n in ["00-99"] + naer},
                "bo": {n: bo[nokkel].get((n, siste)) for n in ["00-99"] + naer}}

    D = {"hentet": time.strftime("%Y-%m-%d"), "kilde": "SSB 07984, sysselsatte 15–74 år per 4. kvartal etter arbeidssted og bosted",
         "aar": [int(t) for t in aar], "naeringer": [[n, KORT.get(n, n)] for n in naer],
         "kommuner": {}, "NN": pakk("NN"), "landet": pakk("landet")}
    for kk in KODER:
        p = pakk(kk)
        p["skjult"] = {t: sorted(skj[(kk, t)]) for t in (aar[0], siste) if skj[(kk, t)]}
        D["kommuner"][kk] = p
    mangler = [kk for kk in KODER if D["kommuner"][kk]["arb"]["00-99"][-1] is None]
    if mangler:
        print("MANGLER totalen:", mangler)
    mappe = HER / "analyse" / "naering" / "data"
    mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "naering_kommune.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    djs = HER / "assets" / "data.js"
    js = djs.read_text(encoding="utf-8")
    blokk = "/* NAERING_K BEGIN */\nconst NAERING_K = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n/* NAERING_K END */"
    if "/* NAERING_K BEGIN */" in js:
        js = re.sub(r"/\* NAERING_K BEGIN \*/.*?/\* NAERING_K END \*/", lambda _m: blokk, js, flags=re.S)
    else:
        js = js.rstrip("\n") + "\n" + blokk + "\n"
    djs.write_text(js, encoding="utf-8")
    print(f"NAERING_K skrevet ({len(blokk) // 1024} KB), år {aar[0]}–{siste}.")
    return D


if __name__ == "__main__":
    D = main()
    n = D["kommuner"]["1806"]
    print("Narvik i alt:", n["arb"]["00-99"], " bosatte", n["bo"]["00-99"])
    print("  helse:", n["arb"]["86-88"], " overnatting:", n["arb"]["55-56"], " undervisning:", n["arb"]["85"])
    print("  skjult:", n["skjult"])
    print("Landet i alt:", D["landet"]["arb"]["00-99"], " NN:", D["NN"]["arb"]["00-99"])
