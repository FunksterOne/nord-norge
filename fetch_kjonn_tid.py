#!/usr/bin/env python3
"""Kjønnsbalansen over tid, flytting etter kjønn og alder, og framskrevne unge kvinner → KJONN_TID i assets/data.js.

Til tema 03 (Kvinneflukten), pakke B i analyse/PLAN-FIGURER-08.md:
  - SSB 07459: menn og kvinner 18–44 år, 1.1.1986–2026, Nord-Norge (sum av fylkene, kodelisten agg_KommFylker gir
    sammenlignbare serier bakover) og landet.
  - SSB 05539: inn-, ut- og nettoflytting etter kjønn og aldersgruppe, 2011–2025. Tabellen omfatter ALL flytting over
    fylkesgrensen, også til og fra utlandet, og kan ikke deles. Nord-Norge = summen av fylkene som fantes hvert år
    (18, 19, 20, 54, 55, 56); flytting mellom fylkene i landsdelen går da ut mot hverandre.
  - SSB 14746: framskrevne kvinner og menn 20–39 år, 2026–2050, lav (LLML), hoved (MMMM) og høy (HHMH) alternativ.
Kjør:  python fetch_kjonn_tid.py
"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
API = "https://data.ssb.no/api/pxwebapi/v2/tables/{}/data?"


def hent(tab, filt, kodeliste=None):
    """Returnerer {(dim1, dim2, ...): verdi} i tabellens dimensjonsrekkefølge, dimensjonsnavnene og kategorietikettene."""
    p = {"lang": "no", "outputFormat": "json-stat2", **{f"valueCodes[{k}]": v for k, v in filt.items()}}
    if kodeliste:
        p["codelist[Region]"] = kodeliste
    for forsok in range(6):   # SSB begrenser antall kall per minutt; vent og prøv igjen ved 429
        time.sleep(2)
        try:
            j = json.load(urllib.request.urlopen(API.format(tab) + urllib.parse.urlencode(p), timeout=300))
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or forsok == 5:
                raise
            time.sleep(30)
    dims, size = j["id"], j["size"]
    kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
    lab = {d: j["dimension"][d]["category"]["label"] for d in dims}
    ut = {}
    for i, x in enumerate(j["value"]):
        idx, rest = [], i
        for d, n in zip(reversed(dims), reversed(size)):
            idx.append(kat[d][rest % n]); rest //= n
        ut[tuple(reversed(idx))] = x
    return ut, dims, lab


def main():
    alder_18_44 = ",".join(f"{a:03d}" for a in range(18, 45))
    alder_20_39 = ",".join(f"{a:03d}" for a in range(20, 40))
    aar = [str(y) for y in range(1986, 2027)]

    # 1. Kjønnsbalansen 18–44 år over tid (07459)
    def bestand(region, kodeliste=None):
        d, dims, _ = hent("07459", {"Region": region, "Kjonn": "1,2", "Alder": alder_18_44, "ContentsCode": "Personer1",
                                    "Tid": ",".join(aar)}, kodeliste)
        ki, ai, ti = dims.index("Kjonn"), dims.index("Alder"), dims.index("Tid")
        m, k, k2039 = defaultdict(int), defaultdict(int), defaultdict(int)
        for key, v in d.items():
            if v is None:
                continue
            t, a = key[ti], int(key[ai])
            if key[ki] == "1":
                m[t] += v
            else:
                k[t] += v
                if 20 <= a <= 39:
                    k2039[t] += v
        return {"menn": [m[t] for t in aar], "kvinner": [k[t] for t in aar], "kvinner_20_39": [k2039[t] for t in aar]}

    nn = bestand("F-18,F-55,F-56", "agg_KommFylker")
    landet = bestand("0")

    # 2. Flytting etter kjønn og aldersgruppe (05539), Nord-Norge
    d, dims, lab = hent("05539", {"Region": "18,19,20,54,55,56", "Kjonn": "1,2", "Alder": "*",
                                  "ContentsCode": "Innflyttinger,Utflyttinger,Nettoflyttinger", "Tid": "*"})
    ki, ai, ci, ti = dims.index("Kjonn"), dims.index("Alder"), dims.index("ContentsCode"), dims.index("Tid")
    grupper = list(lab["Alder"])
    flytt_aar = sorted({k[ti] for k in d})
    fl = defaultdict(int)
    for key, v in d.items():
        if v is not None:
            fl[(key[ki], key[ai], key[ci], key[ti])] += v
    flytting = {
        "aar": [int(t) for t in flytt_aar],
        "grupper": [lab["Alder"][g] for g in grupper],
        **{kj: {c: [[fl[(kode, g, c, t)] for t in flytt_aar] for g in grupper]
                for c in ("Innflyttinger", "Utflyttinger", "Nettoflyttinger")}
           for kj, kode in (("menn", "1"), ("kvinner", "2"))},
    }

    # 3. Framskrevne kvinner og menn 20–39 år (14746)
    d, dims, _ = hent("14746", {"Region": "18,55,56", "Kjonn": "1,2", "Alder": alder_20_39,
                                "ContentsCode": "Personer,Personer1,Personer2", "Tid": "*"})
    ki, ci, ti = dims.index("Kjonn"), dims.index("ContentsCode"), dims.index("Tid")
    fr_aar = sorted({k[ti] for k in d})
    fr = defaultdict(int)
    for key, v in d.items():
        if v is not None:
            fr[(key[ki], key[ci], key[ti])] += v
    navn = {"Personer": "hoved", "Personer1": "lav", "Personer2": "hoy"}
    framskr = {"aar": [int(t) for t in fr_aar],
               **{kj: {navn[c]: [fr[(kode, c, t)] for t in fr_aar] for c in navn} for kj, kode in (("menn", "1"), ("kvinner", "2"))}}

    ut = {"hentet": date.today().isoformat(), "tabeller": ["07459", "05539", "14746"],
          "aar": [int(t) for t in aar], "nn": nn, "landet": landet, "flytting": flytting, "framskriving": framskr}

    # Kontroll mot KJONN_DATA (07459 per kommune, 1.1.2026)
    js = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"/\* KJONN_DATA BEGIN \*/\s*(?:const|var|let)\s+KJONN_DATA\s*=\s*(\{.*?\});?\s*/\* KJONN_DATA END \*/", js, re.S)
    if m:
        kd = json.loads(m.group(1))
        sm = sum(r["menn"]["sum_18_44"] for r in kd["kommuner"].values())
        sk = sum(r["kvinner"]["sum_18_44"] for r in kd["kommuner"].values())
        print(f"Kontroll 2026: menn {nn['menn'][-1]} mot {sm}, kvinner {nn['kvinner'][-1]} mot {sk}")
    i86, i26 = 0, -1
    print("Menn per 100 kvinner 18–44, Nord-Norge:", round(nn["menn"][i86] / nn["kvinner"][i86] * 100, 1), "(1986) →",
          round(nn["menn"][i26] / nn["kvinner"][i26] * 100, 1), "(2026); landet:",
          round(landet["menn"][i86] / landet["kvinner"][i86] * 100, 1), "→", round(landet["menn"][i26] / landet["kvinner"][i26] * 100, 1))
    for kj in ("menn", "kvinner"):
        print(kj, "netto 2011–2025 per gruppe:", dict(zip(flytting["grupper"], [sum(r) for r in flytting[kj]["Nettoflyttinger"]])))
    print("Kvinner 20–39 hoved:", framskr["kvinner"]["hoved"][0], "→", framskr["kvinner"]["hoved"][-1])

    lit = "const KJONN_TID = " + json.dumps(ut, ensure_ascii=False, separators=(",", ":")) + ";"
    block = f"/* KJONN_TID BEGIN */\n{lit}\n/* KJONN_TID END */"
    if "/* KJONN_TID BEGIN */" in js:
        js = re.sub(r"/\* KJONN_TID BEGIN \*/.*?/\* KJONN_TID END \*/", lambda _m: block, js, flags=re.DOTALL)
    elif "/* FYLKE_TALL END */" in js:
        js = js.replace("/* FYLKE_TALL END */", "/* FYLKE_TALL END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret FYLKE_TALL END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(js, encoding="utf-8")
    print("KJONN_TID skrevet til", DATA_JS)


if __name__ == "__main__":
    main()
