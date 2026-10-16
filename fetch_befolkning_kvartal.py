#!/usr/bin/env python3
"""Henter ferskeste kvartalsvise folketall (SSB 01222) og injiserer BEFK_DATA
i assets/data.js.

Nyeste tilgjengelige kvartal brukes automatisk (per august 2026: 2026K1, dvs.
folketall per 1. april 2026). Vises som ferskeste maaling der folketall
presenteres. VIKTIG: alle modeller (framskriving, BB-KVOTE, TF-baner) forblir
forankret i 1.1.2026 — kvartalstallene har ingen aldersfordeling paa
kommuneniva og kan ikke brukes som modellanker.

Kontroll: 01222 "Befolkning ved inngangen av kvartalet" skal for K1 vaere lik
1.1-ankeret (sum av alder-arrayene), og for K2-K4 lik utgangen av forrige
kvartal, for hver kommune.
"""
import json
import re
import datetime
from pathlib import Path

from fetch_bolig import get, post_ssb, celler, CODES, fylke

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"


def main():
    meta = get("https://data.ssb.no/api/v0/no/table/01222")
    tid = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
    siste = tid[-1]
    aar, kv = int(siste[:4]), int(siste[-1])
    dato = {1: f"{aar}-04-01", 2: f"{aar}-07-01", 3: f"{aar}-10-01", 4: f"{aar+1}-01-01"}[kv]
    dato_norsk = {1: f"1. april {aar}", 2: f"1. juli {aar}", 3: f"1. oktober {aar}",
                  4: f"1. januar {aar+1}"}[kv]
    print(f"Henter 01222 for {siste} (folketall per {dato_norsk})...", flush=True)

    q = [{"code": "Region", "selection": {"filter": "item", "values": CODES + ["0"]}},
         {"code": "ContentsCode", "selection": {"filter": "item",
                                                "values": ["Folketallet1", "Folketallet11"]}},
         {"code": "Tid", "selection": {"filter": "item", "values": [siste]}}]
    d = post_ssb("01222", q)
    inng, utg = {}, {}
    for co, v in celler(d):
        (inng if co["ContentsCode"] == "Folketallet1" else utg)[co["Region"]] = v

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "tabell": "01222", "kvartal": siste, "dato": dato, "dato_norsk": dato_norsk,
        "kommuner": {k: utg.get(k) for k in CODES},
        "fylker": {f: sum(utg.get(k) or 0 for k in CODES if fylke(k) == f)
                   for f in ["Nordland", "Troms", "Finnmark"]},
        "landsdel": sum(utg.get(k) or 0 for k in CODES),
        "riket": utg.get("0"),
    }

    # Kontroll av kvartalsinngangen:
    #  - K1: inngangen (1.1) skal vaere lik 1.1-ankeret (sum av alder-arrayene).
    #  - K2-K4: inngangen skal vaere lik utgangen av forrige kvartal. Sammenlignes
    #    med BEFK_DATA som allerede ligger i data.js dersom den gjelder forrige
    #    kvartal; ellers hentes forrige kvartals utgang direkte fra 01222.
    js = DATA_JS.read_text(encoding="utf-8")
    linjer = js.split("\n")
    idx = next(i for i, l in enumerate(linjer) if l.startswith("const DATA = "))
    DATA = json.loads(linjer[idx][len("const DATA = "):].rstrip(";"))
    if kv == 1:
        ref = {k: sum(DATA["kommuner"][k]["alder"]) for k in CODES}
        ref_navn = "1.1-ankeret"
    else:
        forrige = f"{aar}K{kv - 1}"
        m = re.search(r"const BEFK_DATA = (\{.*?\});\n", js)
        gammel = json.loads(m.group(1)) if m else None
        if gammel and gammel.get("kvartal") == forrige:
            ref = {k: gammel["kommuner"].get(k) for k in CODES}
            ref_navn = f"utgangen av {forrige} (BEFK_DATA i data.js)"
        else:
            q2 = [q[0], {"code": "ContentsCode", "selection": {"filter": "item",
                                                                "values": ["Folketallet11"]}},
                  {"code": "Tid", "selection": {"filter": "item", "values": [forrige]}}]
            ref = {co["Region"]: v for co, v in celler(post_ssb("01222", q2))}
            ref_navn = f"utgangen av {forrige} (01222)"
    avvik = [(k, ref.get(k), inng.get(k)) for k in CODES if ref.get(k) != inng.get(k)]
    if avvik:
        print(f"ADVARSEL: {len(avvik)} kommuner der 01222-inngang != {ref_navn}:")
        for k, a, b in avvik[:5]:
            print(f"  {k}: referanse {a}, 01222-inngang {b}")
    else:
        print(f"Kontroll OK: 01222-inngangen er identisk med {ref_navn} for alle 80.")
    delta = payload["landsdel"] - sum(inng.get(k) or 0 for k in CODES)
    print(f"Landsdel per {dato_norsk}: {payload['landsdel']} "
          f"({'+' if delta >= 0 else ''}{delta} i kvartalet). Riket: {payload['riket']}.")

    lit = "const BEFK_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* BEFK_DATA BEGIN */\n" + lit + "\n/* BEFK_DATA END */"
    if "/* BEFK_DATA BEGIN */" in js:
        js = re.sub(r"/\* BEFK_DATA BEGIN \*/.*?/\* BEFK_DATA END \*/", lambda _m: block, js,
                    flags=re.DOTALL)
    else:
        js = js.replace("/* MARKED_DATA END */", "/* MARKED_DATA END */\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injisert BEFK_DATA ({len(lit)} tegn).")


if __name__ == "__main__":
    main()
