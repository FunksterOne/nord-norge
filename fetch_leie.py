#!/usr/bin/env python3
"""Henter leiemarkedet og injiserer LEIE_DATA i assets/data.js.

Kilder:
  14891  Eierstatus, husholdninger (K), 2015-. EierStatus 0 = I alt, 3 = Leier.
         Erstatter 11084 (avviklet; v0-API gir 400). SSB reviderte hele
         boforholdsstatistikken 14. september 2026 for 2015-2025, saa nivaaene
         (saerlig antall leiere) er IKKE sammenlignbare med tidligere 11084-tall.
         14891 publiseres paa dagens kommunegrenser for hele perioden, saa
         KLASS-skjoeting er ikke lenger noedvendig.
  12008  Kommunalt disponerte boliger (K), KOSTRA — per 1 000 innbyggere.

Feltnavn: l15/a15 = 2015 (leiere/alle husholdninger). l24/a24 = SISTE aar
(`aar`, f.eks. 2025). Navnene beholdes av hensyn til eksisterende render-kode.

Avgrensning (dokumentert i metode.html): aldersfordelt leieandel og
utleieboliger etter eiertype finnes bare i Microdata/forskningsdata, ikke i
aapne tabeller. Slike tall gjengis som redaksjonelt innhold med kildehenvisning
(kbnn/KPB, juli 2026).
"""
import json
import re
import datetime
from pathlib import Path

from fetch_bolig import get, post_ssb, celler, CODES, fylke

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

TAB = "14891"
FYLKESKODE = {"Nordland": "18", "Troms": "55", "Finnmark": "56"}


def main():
    meta = get(f"https://data.ssb.no/api/v0/no/table/{TAB}")
    tid = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
    siste = tid[-1]
    print(f"Henter {TAB} (eierstatus husholdninger, 2015 og {siste})...", flush=True)
    q = [{"code": "Region", "selection": {"filter": "item",
                                          "values": CODES + list(FYLKESKODE.values()) + ["0"]}},
         {"code": "EierStatus", "selection": {"filter": "item", "values": ["0", "3"]}},
         {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Husholdning"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": ["2015", siste]}}]
    tall = {}
    for co, v in celler(post_ssb(TAB, q)):
        tall[(co["Region"], co["EierStatus"], co["Tid"])] = v

    def rec(kode):
        return {"l15": tall.get((kode, "3", "2015")), "l24": tall.get((kode, "3", siste)),
                "a15": tall.get((kode, "0", "2015")), "a24": tall.get((kode, "0", siste))}

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
        "tables": [TAB, "12008"],
        "aar": siste, "aar_komm": aar12,
        "felt_note": f"l15/a15 = 2015; l24/a24 = siste år ({siste}). Kilde {TAB} "
                     "(SSB-revisjon 14.9.2026, erstatter 11084; nivåene er ikke "
                     "sammenlignbare med tidligere publiserte tall).",
        "kommuner": {k: rec(k) for k in CODES},
        "fylker": {f: rec(c) for f, c in FYLKESKODE.items()},
        "landsdel": {}, "riket": rec("0"),
        "komm1000": komm,
    }
    payload["landsdel"] = {f: sum(payload["fylker"][fy][f] or 0 for fy in FYLKESKODE)
                           for f in ("l15", "l24", "a15", "a24")}

    # --- kontroller ---------------------------------------------------------
    for fy in FYLKESKODE:
        s = sum(payload["kommuner"][k]["a24"] or 0 for k in CODES if fylke(k) == fy)
        if s != payload["fylker"][fy]["a24"]:
            print(f"ADVARSEL: sum kommuner {fy} {s} != fylkestall {payload['fylker'][fy]['a24']}")
    L = payload["landsdel"]
    vl = (L["l24"] - L["l15"]) / L["l15"] * 100
    va = (L["a24"] - L["a15"]) / L["a15"] * 100
    print(f"\nLandsdel: {L['l24']} leiehusholdninger {siste} ({L['l24'] / L['a24'] * 100:.1f} %), "
          f"vekst 2015-{siste} {vl:.1f} %, alle husholdninger {va:.1f} %. "
          "(kbnn/KPB juli 2026 paa gammel 11084-serie: ~57 000, 12,6 %, 8,6 %)")
    R = payload["riket"]
    print(f"Riket: {R['l24']} leiehusholdninger {siste} (SSB-artikkel 2025: 713 623)")
    topp = sorted(((komm.get(k) or 0, k) for k in CODES), reverse=True)[:3]
    print("Kommunalt disponerte per 1 000 innb., topp 3:",
          [(t[1], t[0]) for t in topp], f"({aar12})")

    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const LEIE_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* LEIE_DATA BEGIN */\n" + lit + "\n/* LEIE_DATA END */"
    if "/* LEIE_DATA BEGIN */" in js:
        js = re.sub(r"/\* LEIE_DATA BEGIN \*/.*?/\* LEIE_DATA END \*/", lambda _m: block, js,
                    flags=re.DOTALL)
    else:
        anchor = "/* BEFK_DATA END */" if "/* BEFK_DATA END */" in js else "/* MARKED_DATA END */"
        js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injisert LEIE_DATA ({len(lit)} tegn).")


if __name__ == "__main__":
    main()
