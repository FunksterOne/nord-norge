#!/usr/bin/env python3
"""Spesialisthelsetjenesten i Nord-Norge (tema 12) → HELSE_DATA i assets/data.js.

Kilder (se analyse/helse-nord/notater/ for full dokumentasjon med sidetall):
  - Helse Nord RHF styresak 108-2026 (framskriving 2025–2045, SSB 2026 hovedalternativet): befolkning og
    somatiske liggedøgn og polikliniske kontakter per helseforetak, revidert modell og ren demografi.
  - analyse/helse-nord/data/: opptaksområder (utledet fra SSB 13982), sykehus med funksjonsnivå (RU42),
    reisetid fra kommunesenteret (OSRM, skript/reisetid.py), SSB 12764 (kjøretid til akuttmottak 2019),
    SSB 13953 (avtalte årsverk), SSB 13470 (sysselsatte i sykehustjenester), FHI ventetider, SKDE helseatlas,
    SSB-artikkel om innleie 2023.
  - NOU 2026: 12 Én helsetjeneste og SSBs leveranse til Helsereformutvalget (data/hru_ssb.json, skript/hru_ssb.py):
    kommunale omsorgsårsverk, sykefravær etter region og kommunestørrelser.
  - Regional utviklingsplan 2035 (2018) og 2023–2038 (2022): framskrivinger av liggedøgn (PLANER).
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
A = HER / "analyse" / "helse-nord" / "data"

# ── Styresak 108-2026: tabell 3 (PDF-s. 114), tabell 28 (PDF-s. 158) og tabell 44 (PDF-s. 171) ──
# bef: [2025, 2045, endring 0–17, 18–64, 65+ i prosent]; ligg/poli: [2025, 2045 revidert modell, 2045 ren demografi]
HF = [
    {"kode": "UNN", "navn": "Universitetssykehuset Nord-Norge", "kort": "UNN",
     "bef": [195499, 200131, -4.3, -4.5, 28.2], "ligg": [154249, 163188, 192625], "poli": [299429, 340114, 321573]},
    {"kode": "NLSH", "navn": "Nordlandssykehuset", "kort": "Nordlandssykehuset",
     "bef": [140608, 139962, -7.8, -7.0, 23.8], "ligg": [89827, 94863, 110374], "poli": [200720, 225261, 212752]},
    {"kode": "HSYK", "navn": "Helgelandssykehuset", "kort": "Helgelandssykehuset",
     "bef": [76580, 73013, -12.6, -12.4, 21.1], "ligg": [36937, 40107, 45092], "poli": [105089, 115014, 108377]},
    {"kode": "FIN", "navn": "Finnmarkssykehuset", "kort": "Finnmarkssykehuset",
     "bef": [75042, 76787, -3.3, -6.4, 34.1], "ligg": [33098, 38913, 43941], "poli": [90477, 104259, 98379]},
]
HN = {"kode": "HN", "navn": "Helse Nord", "bef": [487729, 489893, -6.5, -6.7, 26.5],
      "ligg": [314111, 337071, 392032], "poli": [695715, 784648, 741082]}
NORGE = {"kode": "NO", "navn": "Landet", "bef": [5594340, 6121519, -0.7, 2.5, 42.4],
         "ligg": [2931353, 3524036, 3877200], "poli": [7030703, 8742185, 8270913]}
HF_ORGNR = {"UNN": "983974899", "NLSH": "983974910", "HSYK": "983974929", "FIN": "983974880"}
HF_VENT = {"UNN": "Universitetssykehuset Nord-Norge HF", "NLSH": "Nordlandssykehuset HF",
           "HSYK": "Helgelandssykehuset HF", "FIN": "Finnmarkssykehuset HF"}
HF_ATLAS = {"UNN": "UNN", "NLSH": "Nordlandssykehuset", "HSYK": "Helgelandssykehuset", "FIN": "Finnmarkssykehuset"}
INNLEIE = {"aar": 2023, "andel": {"Nord": 3.88, "Sør-Øst": 1.53, "Vest": 1.32, "Midt-Norge": 0.87},
           "kilde": "SSB, «Mest bruk av vikarbyrå ved sykehusene i Nord-Norge» (15.11.2024): innleie i prosent av lønns- og personalkostnadene",
           "nou": {"innleie": 35, "aarsverk": 12, "aar": 2021, "kilde": "NOU 2023: 4 Tid for handling, s. 86"},
           "per_innb": {"pst": 28, "kilde": "Helse Nord RHF styresak 62-2026, vedlegg s. 2: årsverk per innbygger mot resten av landet"}}
# ── Tre generasjoner utviklingsplaner: liggedøgn med ren demografi mot planens anslag (analyse/helse-nord/VURDERING-HRU.md) ──
# demo/plan i prosent; abs = [startår, ren demografi, planens anslag] der planen oppgir liggedøgn. RU42 hentes fra HN over.
PLANER = [
    {"kort": "RU2035", "navn": "Regional utviklingsplan 2035", "vedtatt": "2018-12-19", "status": "Vedtatt 19.12.2018", "periode": "til 2035",
     "grunnlag": "Liggedøgn etter nasjonal framskrivingsmodell; startår og tjenesteområde ikke oppgitt", "demo": 37.0, "plan": 13.0,
     "kilde": "Regional utviklingsplan 2035 Helse Nord, kap. 10 (s. 13)"},
    {"kort": "RU2038", "navn": "Regional utviklingsplan 2023–2038", "vedtatt": "2022-12-14", "status": "Vedtatt 14.12.2022", "periode": "2019–2040",
     "grunnlag": "Somatiske liggedøgn per opptaksområde, nasjonal framskrivingsmodell", "abs": [330530, 471886, 372713],
     "hf": {"FIN": [56698, 82195, 64003], "UNN": [129073, 186113, 148506], "NLSH": [90172, 129921, 102522], "HSYK": [54587, 73656, 57683]},
     "kilde": "Regional utviklingsplan 2023–2038, del 2, figur 14 (s. 47)"},
    {"kort": "RU42", "navn": "Regional utviklingsplan 2027–2042 (høringsutkast)", "vedtatt": "2026-10-30", "status": "På høring fra 30.10.2026", "periode": "2025–2045",
     "grunnlag": "Somatiske liggedøgn per opptaksområde, revidert modell", "abs": HN["ligg"][:1] + HN["ligg"][2:] + HN["ligg"][1:2],
     "hf": {h["kode"]: [h["ligg"][0], h["ligg"][2], h["ligg"][1]] for h in HF},
     "kilde": "Helse Nord RHF styresak 108-2026, tabell 28 (lagt ut på høring 30.10.2026)"},
]
for p in PLANER:
    if "abs" in p:
        a, d, pl = p["abs"]
        p["demo"], p["plan"] = round((d / a - 1) * 100, 1), round((pl / a - 1) * 100, 1)
        assert abs(sum(v[0] for v in p["hf"].values()) - a) < 5, p["kort"]
    p["andel"] = round((p["demo"] - p["plan"]) / p["demo"] * 100, 1)


def les_csv(navn):
    return list(csv.DictReader((A / navn).open(encoding="utf-8")))


def kommuner():
    opp = json.loads((A / "opptak.json").read_text(encoding="utf-8"))["kommuner"]
    rt = json.loads((A / "reisetid.json").read_text(encoding="utf-8"))
    # SSB 12764 (2019), befolkningsvektet kjøretid til nærmeste akuttmottak; navnenøkkel fordi kodene er fra 2019
    norm = lambda s: re.sub(r"\s*\(.*?\)", "", s.split(" - ")[0]).strip().lower()
    ssb = {norm(r["region"]): r for r in les_csv("kjoretid_akuttmottak.csv") if len(r["region_kode"]) == 4}
    navn = {m.group(1): m.group(2) for m in re.finditer(r'"(\d{4})":\{"navn":"([^"]+)"', DATA_JS.read_text(encoding="utf-8"))}
    ut = {}
    for nr, r in rt["kommuner"].items():
        nøkler = [norm(d) for d in navn.get(nr, "").split(" - ")] + [norm(navn.get(nr, ""))]
        s19 = next((ssb[k] for k in nøkler if k in ssb), None)
        p50 = round(float(s19["min_P50"])) if s19 else None
        p90 = round(float(s19["min_P90"])) if s19 else None
        osrm = r["akutt"]["min"]
        # Fergeruter i OpenStreetMap gir urimelige tider for enkelte øykommuner. Der ruten går med ferge og
        # avviket mot SSBs befolkningsvektede 2019-tall er over én time, vises SSB-tallet.
        usikker = bool(r["akutt"]["ferge"] and p50 is not None and osrm - p50 > 60)
        ut[nr] = {"hf": opp[nr]["hf"], "lok": opp[nr]["sykehus"], "sted": r["sted"],
                  "akutt": r["akutt"]["navn"], "min": p50 if usikker else osrm, "osrm": osrm, "km": r["akutt"]["km"],
                  "ferge": r["akutt"]["ferge"], "grunnlag": "ssb2019" if usikker else "osrm",
                  "hn": [r["akutt_hn"]["navn"], r["akutt_hn"]["min"]], "reg": r["regionsykehus"]["min"],
                  "ssb2019": [p50, p90]}
    return ut, rt["sykehus"], rt["kilde"]


def aarsverk():
    rader = [r for r in les_csv("arsverk_hf.csv") if r["tjenesteomraade"] == "I alt" and r["yrke_kode"] == "TOT"]
    v = {(r["hf_kode"], int(r["aar"])): int(r["avtalte_arsverk"]) for r in rader}
    aar = sorted({k[1] for k in v})
    ut = {"aar": aar, "landet": [v[("H00", a)] for a in aar], "nord": [v[("H05", a)] for a in aar],
          "hf": {k: [v.get((o, a)) for a in aar] for k, o in HF_ORGNR.items()},
          "kilde": "SSB 13953, avtalte årsverk i spesialisthelsetjenesten"}
    # Yrker 2025 for Helseregion Nord
    yr = [r for r in les_csv("arsverk_hf.csv") if r["tjenesteomraade"] == "I alt" and r["hf_kode"] == "H05" and r["aar"] in (str(aar[0]), str(aar[-1]))]
    ut["yrker"] = {}
    for r in yr:
        ut["yrker"].setdefault(r["yrke"], {})[r["aar"]] = int(r["avtalte_arsverk"])
    return ut


def ventetid():
    rader = [r for r in les_csv("ventetid.csv") if r["fagomrade"] == "Alle sektorer"
             and r["indikator"] in ("ventetid_pabegynt_gjsn", "andel_fristbrudd_pabegynt")]
    siste = max(r["periode"] for r in rader)
    def v(enhet, ind, per=siste):
        r = next((x for x in rader if x["enhet"] == enhet and x["indikator"] == ind and x["periode"] == per), None)
        return round(float(r["verdi"]), 1) if r else None
    per = sorted({r["periode"] for r in rader})
    return {"periode": siste,
            "rhf": {n: [v(n, "ventetid_pabegynt_gjsn"), v(n, "andel_fristbrudd_pabegynt")] for n in
                    ("Helse Nord RHF", "Helse Midt-Norge RHF", "Helse Vest RHF", "Helse Sør-Øst RHF", "Landet")},
            "hf": {k: [v(n, "ventetid_pabegynt_gjsn"), v(n, "andel_fristbrudd_pabegynt")] for k, n in HF_VENT.items()},
            "serie": {"perioder": per, "nord": [v("Helse Nord RHF", "ventetid_pabegynt_gjsn", p) for p in per],
                      "landet": [v("Landet", "ventetid_pabegynt_gjsn", p) for p in per]},
            "kilde": "FHI/Helsedirektoratet, ventetider og fristbrudd per tertial (alle sektorer, påbegynte forløp)"}


def atlas():
    rader = [r for r in les_csv("skde_atlas_nord.csv") if r["status"] == "published"]
    nyeste = {}
    for r in rader:
        k = r["tittel"]
        if k not in nyeste or r["aar"] > nyeste[k]["aar"]:
            nyeste[k] = {"aar": r["aar"], "rader": []}
        if r["aar"] == nyeste[k]["aar"]:
            nyeste[k]["rader"].append(r)
    ut = []
    for tittel, o in nyeste.items():
        r0 = o["rader"][0]
        hn, no = float(r0["helse_nord_rate"]), float(r0["rate_norge"])
        ut.append({"tittel": tittel, "aar": int(o["aar"]), "hn": round(hn / no, 2),
                   "hf": {k: next((float(x["forhold_til_norge"]) for x in o["rader"] if x["hf"] == n), None) for k, n in HF_ATLAS.items()}})
    ut.sort(key=lambda x: -x["hn"])
    return {"analyser": ut, "kilde": "SKDE, Helseatlas (publiserte analyser), rater justert for alder og kjønn, forhold til landet"}


def main():
    K, H, rkilde = kommuner()
    ansatte = json.loads((A / "sykehusansatte.json").read_text(encoding="utf-8"))
    # SSBs leveranse til Helsereformutvalget, trukket ut av skript/hru_ssb.py
    hru = json.loads((A / "hru_ssb.json").read_text(encoding="utf-8"))
    payload = {
        "hentet": "2026-11-02",
        "hf": HF, "hn": HN, "norge": NORGE, "kommuner": K,
        "sykehus": [{k: h.get(k) for k in ("navn", "hf", "sted", "niva", "fodsel", "utenfor")} for h in H],
        "reisetid_kilde": rkilde, "aarsverk": aarsverk(), "ansatte": {"aar": ansatte["aar"], "serie": ansatte["serie"]},
        "innleie": INNLEIE, "ventetid": ventetid(), "atlas": atlas(),
        "kilde_framskriving": "Helse Nord RHF styresak 108-2026, tabell 3, 28 og 44 (SSB 2026, hovedalternativet)",
        "planer": PLANER, "hru": hru,
    }
    assert len(K) == 80, len(K)
    # Kontroll: befolkningen per helseforetak summerer til Helse Nord
    assert abs(sum(h["bef"][0] for h in HF) - HN["bef"][0]) < 5, "befolkning 2025"
    assert abs(sum(h["ligg"][1] for h in HF) - HN["ligg"][1]) < 5, "liggedøgn 2045"
    usikre = [v["sted"] for v in K.values() if v["grunnlag"] == "ssb2019"]
    print("Kommuner", len(K), "· SSB 2019 brukt for", usikre)
    print("Ventetid", payload["ventetid"]["periode"], payload["ventetid"]["rhf"]["Helse Nord RHF"], "landet", payload["ventetid"]["rhf"]["Landet"])
    print("Årsverk Nord", payload["aarsverk"]["aar"][0], payload["aarsverk"]["nord"][0], "→", payload["aarsverk"]["nord"][-1])

    html = DATA_JS.read_text(encoding="utf-8")
    js_lit = "const HELSE_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* HELSE_DATA BEGIN */", "/* HELSE_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in html:
        new = re.sub(r"/\* HELSE_DATA BEGIN \*/.*?/\* HELSE_DATA END \*/", lambda _m: block, html, flags=re.DOTALL)
    elif "/* NORD_DATA END */" in html:
        new = html.replace("/* NORD_DATA END */", "/* NORD_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret NORD_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    print(f"Injected HELSE_DATA ({len(js_lit)} tegn)")


if __name__ == "__main__":
    main()
