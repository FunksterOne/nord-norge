#!/usr/bin/env python3
"""Henter leiemarkedet og injiserer LEIE_DATA i assets/data.js.

Kilder:
  11084  Eierstatus, husholdninger (K), 2015-2024. EierStatus 4 = Leier.
         Kommuneserier skjotes til 2024-grensene via KLASS (som fetch_bolig.py).
  12008  Kommunalt disponerte boliger (K), KOSTRA — per 1 000 innbyggere.

Avgrensning (dokumentert i metode.html): aldersfordelt leieandel og
utleieboliger etter eiertype finnes bare i Microdata/forskningsdata, ikke i
aapne tabeller. Slike tall gjengis som redaksjonelt innhold med kildehenvisning
(kbnn/KPB, juli 2026).
"""
import json
import re
import datetime
from pathlib import Path

from fetch_bolig import get, post_ssb, celler, bygg_familier, CODES, fylke

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

AAR = [str(a) for a in range(2015, 2025)]


def main():
    print("Bygger skjotetabell...", flush=True)
    familier, split_i_nord = bygg_familier()
    alle_koder = sorted({k for fam in familier.values() for k in fam} | set(split_i_nord) | {"0"})

    print("Henter 11084 (eierstatus husholdninger, 2015-2024)...", flush=True)
    meta = get("https://data.ssb.no/api/v0/no/table/11084")
    reg_ok = set(next(v for v in meta["variables"] if v["code"] == "Region")["values"])
    q = [{"code": "Region", "selection": {"filter": "item",
                                          "values": [k for k in alle_koder if k in reg_ok]}},
         {"code": "EierStatus", "selection": {"filter": "item", "values": ["1", "4"]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Husholdning"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": AAR}}]
    d = post_ssb("11084", q)
    tall = {}
    for co, v in celler(d):
        tall[(co["Region"], co["EierStatus"], co["Tid"])] = v

    def spleis(fam, status, aar):
        return int(sum(tall.get((k, status, aar), 0) or 0 for k in fam))

    print("Henter 12008 (kommunalt disponerte boliger)...", flush=True)
    meta12 = get("https://data.ssb.no/api/v0/no/table/12008")
    innh = next(v for v in meta12["variables"] if v["code"] == "ContentsCode")
    per1000_kode = next(c for c, t in zip(innh["values"], innh["valueTexts"])
                        if "1000" in t or "1 000" in t)
    aar12 = next(v for v in meta12["variables"] if v["code"] == "Tid")["values"][-1]
    regvar = next(v for v in meta12["variables"] if "region" in v["code"].lower())
    reg12 = set(regvar["values"])
    q = [{"code": regvar["code"], "selection": {"filter": "item",
                                                "values": [k for k in CODES if k in reg12]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": [per1000_kode]}},
         {"code": "Tid", "selection": {"filter": "item", "values": [aar12]}}]
    d = post_ssb("12008", q)
    komm = {}
    for co, v in celler(d):
        komm[co[regvar["code"]]] = v

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "tables": ["11084", "12008"],
        "aar": "2024", "aar_komm": aar12,
        "kommuner": {}, "fylker": {}, "landsdel": {}, "riket": {},
        "komm1000": komm,
    }
    for k in CODES:
        fam = familier[k]
        payload["kommuner"][k] = {
            "l15": spleis(fam, "4", "2015"), "l24": spleis(fam, "4", "2024"),
            "a15": spleis(fam, "1", "2015"), "a24": spleis(fam, "1", "2024")}
    for f in ["Nordland", "Troms", "Finnmark"]:
        fam = [c for k in CODES if fylke(k) == f for c in familier[k]] + \
              [o for o, fy in split_i_nord.items() if fy == f]
        payload["fylker"][f] = {
            "l15": spleis(fam, "4", "2015"), "l24": spleis(fam, "4", "2024"),
            "a15": spleis(fam, "1", "2015"), "a24": spleis(fam, "1", "2024")}
    fam_alle = [c for k in CODES for c in familier[k]] + list(split_i_nord)
    payload["landsdel"] = {
        "l15": spleis(fam_alle, "4", "2015"), "l24": spleis(fam_alle, "4", "2024"),
        "a15": spleis(fam_alle, "1", "2015"), "a24": spleis(fam_alle, "1", "2024")}
    payload["riket"] = {
        "l15": spleis(["0"], "4", "2015"), "l24": spleis(["0"], "4", "2024"),
        "a15": spleis(["0"], "1", "2015"), "a24": spleis(["0"], "1", "2024")}

    # --- kontroller mot kbnn-artikkelen (KPB, juli 2026) -----------------
    L = payload["landsdel"]
    vl = (L["l24"] - L["l15"]) / L["l15"] * 100
    va = (L["a24"] - L["a15"]) / L["a15"] * 100
    print(f"\nKontroll landsdel: {L['l24']} leiehusholdninger 2024 (kbnn: ~57 000), "
          f"vekst 2015-2024 {vl:.1f} % (kbnn: 12,6 %), alle husholdninger {va:.1f} % (kbnn: 8,6 %)")
    topp = sorted(((komm.get(k) or 0, k) for k in CODES), reverse=True)[:3]
    print("Kommunalt disponerte per 1 000 innb., topp 3:",
          [(t[1], t[0]) for t in topp], f"({aar12})")

    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const LEIE_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* LEIE_DATA BEGIN */\n" + lit + "\n/* LEIE_DATA END */"
    if "/* LEIE_DATA BEGIN */" in js:
        js = re.sub(r"/\* LEIE_DATA BEGIN \*/.*?/\* LEIE_DATA END \*/", block, js, flags=re.DOTALL)
    else:
        anchor = "/* BEFK_DATA END */" if "/* BEFK_DATA END */" in js else "/* MARKED_DATA END */"
        js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injisert LEIE_DATA ({len(lit)} tegn).")


if __name__ == "__main__":
    main()
