#!/usr/bin/env python3
"""Henter bruktbolig- og nyboligmarkedet og injiserer MARKED_DATA i assets/data.js.

Kilder:
  14545  Gjennomsnittlig kvadratmeterpris og antall omsetninger (K), aar (fra 2025)
  14310  Samme, kvartal (fylkesniva her; 2025K1-)
  06726  Omsetning av boligeiendommer med bygning i fritt salg (K), 1992-
         (GjSum er prikket paa kommuneniva; snittpris beregnes som Kjopesum/Oms)
  13500  Gjennomsnittlig kvadratmeterpris for nye eneboliger, landsdeler (2021-)

Personvern-prikking: 14545 publiserer kvadratmeterpris bare for kommuner med
tilstrekkelig antall omsetninger (46 av 80 i 2025). Kommuner uten pristall faar
fylkessnittet som referanse i grensesnittet, tydelig merket. Landsdels- og
rikssnitt beregnes som omsetningsvektet snitt av fylkene/landet.
06726-seriene skjotes til 2024-grensene via KLASS (som fetch_bolig.py).
"""
import json
import re
import datetime
from pathlib import Path

from fetch_bolig import get, post_ssb, celler, bygg_familier, CODES, fylke

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

FYLKE_KODE = {"Nordland": "18", "Troms": "55", "Finnmark": "56"}


def hent(table, query):
    d = post_ssb(table, query)
    ut = {}
    for co, v in celler(d):
        ut[tuple(co[k] for k in d["id"] if k != "ContentsCode") + (co.get("ContentsCode"),)] = v
    return d, ut


def main():
    print("Henter 14545 (kvm-pris per kommune og fylke, 2025)...", flush=True)
    q = [{"code": "Region", "selection": {"filter": "item", "values": CODES + ["18", "55", "56", "0"]}},
         {"code": "Boligtype", "selection": {"filter": "item", "values": ["00", "01"]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["KvPris", "Omsetninger"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": ["2025"]}}]
    d = post_ssb("14545", q)
    kv = {}
    for co, v in celler(d):
        kv[(co["Region"], co["Boligtype"], co["ContentsCode"])] = v

    print("Henter 14310 (kvm-pris per fylke, kvartal)...", flush=True)
    meta310 = get("https://data.ssb.no/api/v0/no/table/14310")
    kvartaler = next(v for v in meta310["variables"] if v["code"] == "Tid")["values"]
    q = [{"code": "Region", "selection": {"filter": "item", "values": ["18", "55", "56"]}},
         {"code": "Boligtype", "selection": {"filter": "item", "values": ["00"]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["KvPris"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": kvartaler}}]
    d = post_ssb("14310", q)
    kvart = {}
    for co, v in celler(d):
        kvart.setdefault(co["Region"], {})[co["Tid"]] = v

    print("Henter 06726 (omsetninger og kjopesum, 1992-2025, skjotet)...", flush=True)
    familier, split_i_nord = bygg_familier()
    alle_koder = sorted({k for fam in familier.values() for k in fam} | set(split_i_nord) | {"0"})
    meta726 = get("https://data.ssb.no/api/v0/no/table/06726")
    aar = next(v for v in meta726["variables"] if v["code"] == "Tid")["values"]
    reg_ok = set(next(v for v in meta726["variables"] if v["code"] == "Region")["values"])
    q = [{"code": "Region", "selection": {"filter": "item", "values": [k for k in alle_koder if k in reg_ok]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Oms", "Kjopesum"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": aar}}]
    d = post_ssb("06726", q)
    o726 = {}
    for co, v in celler(d):
        o726[(co["Region"], co["Tid"], co["ContentsCode"])] = v

    def spleis(fam, felt):
        return [int(sum(o726.get((k, a, felt), 0) or 0 for k in fam)) for a in aar]

    print("Henter 13500 (nye eneboliger, kvm-pris landsdel)...", flush=True)
    meta135 = get("https://data.ssb.no/api/v0/no/table/13500")
    aar135 = next(v for v in meta135["variables"] if v["code"] == "Tid")["values"]
    q = [{"code": "Region", "selection": {"filter": "item", "values": ["0", "L06"]}},
         {"code": "Boligtype", "selection": {"filter": "item", "values": ["01"]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["KvPris", "Omsetninger"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": aar135}}]
    d = post_ssb("13500", q)
    ny = {}
    for co, v in celler(d):
        ny[(co["Region"], co["Tid"], co["ContentsCode"])] = v

    # --- bygg payload ----------------------------------------------------
    def vektet(par):
        """Omsetningsvektet snitt av (pris, omsetninger)-par; None-sikkert."""
        t = [(p, o) for p, o in par if p and o]
        if not t:
            return None
        return round(sum(p * o for p, o in t) / sum(o for _, o in t))

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "tables": ["14545", "14310", "06726", "13500"],
        "kvm_aar": "2025",
        "kvm2025": {},
        "kvm_fylker": {}, "kvm_landsdel": {}, "kvm_riket": {},
        "kvartal": {"labels": kvartaler, "fylker": {}},
        "oms_years": [int(a) for a in aar],
        "oms": {}, "kjs": {},
        "oms_fylker": {}, "oms_landsdel": {}, "oms_riket": {},
        "nybygg": {"years": [int(a) for a in aar135],
                   "nn_p": [ny.get(("L06", a, "KvPris")) for a in aar135],
                   "nn_o": [ny.get(("L06", a, "Omsetninger")) for a in aar135],
                   "riket_p": [ny.get(("0", a, "KvPris")) for a in aar135]},
    }
    for k in CODES:
        payload["kvm2025"][k] = {"p": kv.get((k, "00", "KvPris")),
                                 "o": kv.get((k, "00", "Omsetninger"))}
        payload["oms"][k] = spleis(familier[k], "Oms")
        payload["kjs"][k] = spleis(familier[k], "Kjopesum")
    for navn, kode in FYLKE_KODE.items():
        payload["kvm_fylker"][navn] = {
            "p": kv.get((kode, "00", "KvPris")), "o": kv.get((kode, "00", "Omsetninger")),
            "p01": kv.get((kode, "01", "KvPris")), "o01": kv.get((kode, "01", "Omsetninger"))}
        payload["kvartal"]["fylker"][navn] = [kvart.get(kode, {}).get(t) for t in kvartaler]
        fam = [c for k in CODES if fylke(k) == navn for c in familier[k]] + \
              [o for o, f in split_i_nord.items() if f == navn]
        payload["oms_fylker"][navn] = {"oms": spleis(fam, "Oms"), "kjs": spleis(fam, "Kjopesum")}
    payload["kvm_landsdel"] = {
        "p": vektet([(f["p"], f["o"]) for f in payload["kvm_fylker"].values()]),
        "p01": vektet([(f["p01"], f["o01"]) for f in payload["kvm_fylker"].values()])}
    payload["kvm_riket"] = {"p": kv.get(("0", "00", "KvPris")), "p01": kv.get(("0", "01", "KvPris"))}
    fam_alle = [c for k in CODES for c in familier[k]] + list(split_i_nord)
    payload["oms_landsdel"] = {"oms": spleis(fam_alle, "Oms"), "kjs": spleis(fam_alle, "Kjopesum")}
    payload["oms_riket"] = {"oms": spleis(["0"], "Oms"), "kjs": spleis(["0"], "Kjopesum")}

    # --- kontroller ------------------------------------------------------
    harP = [k for k in CODES if payload["kvm2025"][k]["p"]]
    print(f"\nKontroll: {len(harP)} av 80 kommuner har kvm-pris 2025 (ventet 46)")
    ol = payload["oms_landsdel"]["oms"]
    print(f"Omsetninger landsdel 2025: {ol[-1]} (til sammenligning: 1 238 fullforte nybygg siste 12 mnd)")
    bod = payload["kjs"]["1804"][-1] / payload["oms"]["1804"][-1]
    print(f"Bodo snittpris 2025 (Kjopesum/Oms): {bod:.0f} tusen kr (manuell kontroll: 4 919)")
    tromso15 = payload["oms"]["5501"][aar.index("2015")]
    print(f"Tromso omsetninger 2015 (spleiset): {tromso15} (skal vaere > 0)")
    nn_p = payload["nybygg"]["nn_p"][-1]; brukt01 = payload["kvm_landsdel"]["p01"]
    print(f"Pris-gap eneboliger: nybygg {nn_p} kr/m2 mot brukt {brukt01} kr/m2 "
          f"({(nn_p/brukt01-1)*100:.0f} % over)" if nn_p and brukt01 else "Pris-gap: mangler data")
    print(f"Kvm-pris landsdel (vektet): {payload['kvm_landsdel']['p']} kr/m2, riket: {payload['kvm_riket']['p']}")

    # --- injiser ---------------------------------------------------------
    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const MARKED_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* MARKED_DATA BEGIN */\n" + lit + "\n/* MARKED_DATA END */"
    if "/* MARKED_DATA BEGIN */" in js:
        js = re.sub(r"/\* MARKED_DATA BEGIN \*/.*?/\* MARKED_DATA END \*/", block, js, flags=re.DOTALL)
    else:
        anchor = "/* BEHOV_DATA END */"
        if anchor not in js:
            raise SystemExit("BEHOV_DATA END ikke funnet")
        js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"\nInjisert MARKED_DATA ({len(lit)} tegn) i {DATA_JS}")


if __name__ == "__main__":
    main()
