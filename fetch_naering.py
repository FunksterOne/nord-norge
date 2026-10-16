#!/usr/bin/env python3
"""Henter sysselsatte etter arbeidssted og naering (SSB 13470) og injiserer NAERING_DATA
i assets/data.js. Naeringsgruppene folger Samfunnsokonomisk Analyses inndeling i
«Nord-Norge 2040» (rapport 33-2026) saa langt SN2007-kodene tillater det.

Innhold:
  - kommuner[nr][gruppe] = sysselsatte (arbeidssted) siste aar, 80 kommuner (2024-inndeling)
  - landet[gruppe]        = sysselsatte i hele landet, siste aar og 2015
  - nn[gruppe]            = Nord-Norge (fylke 18+55+56 siste aar; 18+19+20 i 2015)

Kjoer:  python fetch_naering.py
"""
import json
import re
import sys
import datetime
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"
TABELL = "13470"

GRUPPER = {
    "fiske":      ("Fiske og fangst", ["03.1"]),
    "havbruk":    ("Havbruk", ["03.2"]),
    "fiskeind":   ("Fiskeindustri", ["10.2"]),
    "reiseliv":   ("Reiseliv", ["55", "56", "79"]),
    "kraftind":   ("Kraftforedlende industri", ["17", "20", "23", "24"]),
    "energi":     ("Energiproduksjon", ["35.1"]),
    "petroleum":  ("Petroleum", ["06", "09.1", "49.5"]),
    "bergverk":   ("Bergverk", ["07", "08"]),
    "anlegg":     ("Anlegg", ["42"]),
    "bygg":       ("Byggenæring", ["41", "43"]),
    "ikt":        ("IKT-tjenester", ["58.2", "61", "62", "63.1"]),
    "kunnskap":   ("Kunnskapsbaserte tjenester", ["69", "70", "71", "72", "73", "74"]),
    "finans":     ("Finansielle tjenester", ["64-66"]),
    "luft":       ("Lufttransport", ["51"]),
    "forsvar":    ("Forsvar", ["84.22"]),
    "helse":      ("Helse og omsorg", ["86", "87", "88"]),
    "undervisning": ("Undervisning", ["85"]),
    "handel":     ("Varehandel", ["45-47"]),
}
ALLE = "00-99"


def get(url):
    with urllib.request.urlopen(url, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def post(query):
    req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{TABELL}",
                                 data=json.dumps(query).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def hent(regioner, aar, koder):
    q = {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": regioner}},
        {"code": "NACE2007", "selection": {"filter": "item", "values": koder}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["SysselsatteArb"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [aar]}},
    ], "response": {"format": "json-stat2"}}
    d = post(q)
    dims = d["id"]; size = d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"].keys()) for k in dims}
    ut = {}
    for flat, v in enumerate(d["value"]):
        rest, co = flat, {}
        for i in range(len(dims) - 1, -1, -1):
            co[dims[i]] = cats[dims[i]][rest % size[i]]
            rest //= size[i]
        ut[(co["Region"], co["NACE2007"])] = v or 0
    return ut


def grupper(rad_fn):
    return {g: sum(rad_fn(k) for k in koder) for g, (_, koder) in GRUPPER.items()}


def main():
    meta = get(f"https://data.ssb.no/api/v0/no/table/{TABELL}")
    tid = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
    siste = tid[-1]
    js = DATA_JS.read_text(encoding="utf-8")
    kommuner = re.findall(r'"(\d{4})":\{"navn":', js.split("\n")[5])[:200]
    kommuner = [k for k in dict.fromkeys(kommuner) if k[:2] in ("18", "55", "56")]
    assert len(kommuner) == 80, f"fant {len(kommuner)} kommuner"
    koder = [ALLE] + [k for _, (_, ks) in GRUPPER.items() for k in ks]

    print(f"Henter {TABELL} {siste} for 80 kommuner + landet ...", flush=True)
    nyt = hent(kommuner + ["0", "18", "55", "56"], siste, koder)
    print(f"Henter {TABELL} 2015 for landet og fylkene 18/19/20 ...", flush=True)
    gml = hent(["0", "18", "19", "20"], "2015", koder)

    def sumreg(data, regs, k):
        return sum(data.get((r, k), 0) for r in regs)

    out = {
        "retrieved_at": datetime.date.today().isoformat(),
        "tabell": TABELL, "aar": siste, "basisaar": "2015",
        "maal": "Sysselsatte personer etter arbeidssted, 4. kvartal",
        "grupper": {g: {"navn": n, "sn2007": ks} for g, (n, ks) in GRUPPER.items()},
        "kommuner": {},
        "landet": {"alle": nyt.get(("0", ALLE), 0), **grupper(lambda k: nyt.get(("0", k), 0))},
        "landet_2015": {"alle": gml.get(("0", ALLE), 0), **grupper(lambda k: gml.get(("0", k), 0))},
        "nn": {"alle": sumreg(nyt, ["18", "55", "56"], ALLE), **grupper(lambda k: sumreg(nyt, ["18", "55", "56"], k))},
        "nn_2015": {"alle": sumreg(gml, ["18", "19", "20"], ALLE), **grupper(lambda k: sumreg(gml, ["18", "19", "20"], k))},
    }
    for nr in kommuner:
        out["kommuner"][nr] = {"alle": nyt.get((nr, ALLE), 0), **grupper(lambda k, nr=nr: nyt.get((nr, k), 0))}

    sum80 = sum(v["alle"] for v in out["kommuner"].values())
    print(f"Kontroll: sum 80 kommuner = {sum80}, fylkessum = {out['nn']['alle']}", flush=True)
    if abs(sum80 - out["nn"]["alle"]) > 50:
        print("ADVARSEL: kommunesum avviker fra fylkessum", flush=True)
    for g in ("fiske", "havbruk", "fiskeind", "reiseliv", "ikt"):
        print(f"  {GRUPPER[g][0]:<28} NN {out['nn'][g]:>7}  (2015: {out['nn_2015'][g]:>7})  landet {out['landet'][g]:>8}", flush=True)

    blokk = "/* NAERING_DATA BEGIN */\nconst NAERING_DATA = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n/* NAERING_DATA END */"
    if "/* NAERING_DATA BEGIN */" in js:
        js = re.sub(r"/\* NAERING_DATA BEGIN \*/.*?/\* NAERING_DATA END \*/", lambda m: blokk, js, flags=re.S)
    else:
        js = js.replace("/* REGIONER:", blokk + "\n\n/* REGIONER:", 1) if "/* REGIONER:" in js else js + "\n" + blokk + "\n"
    DATA_JS.write_text(js, encoding="utf-8")
    print("Skrev NAERING_DATA til assets/data.js", flush=True)


if __name__ == "__main__":
    sys.exit(main())
