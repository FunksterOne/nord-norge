#!/usr/bin/env python3
"""Henter levekårs- og inntektsdata fra SSB og injiserer som inline
LEVEKAR_DATA i index.html. Brukes til ny Akt 2.3 «Levekår og inntekt».

Kilder:
  06944  Inntekt husholdninger — per-kommune median + antall (kommune-spesifikke verdier)
  14780  Personinntekt etter komponenter (lønn, pensjon, uføretrygd)
  11084  Eierstatus husholdninger — antall + andel selveiere/leiere
  06265  Boliger etter bygningstype — antall boliger fordelt

OBS: 12558 (desiler) ble droppet — tabellen returnerer nasjonale desil-grenser
også for kommune-spørringer, så desil1/desil9 ble like for alle kommuner.
For spennvidde mellom 10 % laveste/høyeste finnes ikke per-kommune-data
hos SSB. 06944 har bare median (50-persentil) per kommune.
"""
import json
import re
import sys
import urllib.request
import datetime
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "assets" / "data.js"

CODES = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
"1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
"1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
"1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503",
"5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530",
"5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605",
"5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628",
"5630","5632","5634","5636"]

def post_ssb(table_id, body):
    url = f"https://data.ssb.no/api/v0/no/table/{table_id}"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def parse(d):
    dim = d["dimension"]
    dim_ids = d.get("id") or list(dim.keys())
    sizes = d.get("size") or [len(dim[k]["category"]["index"]) for k in dim_ids]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in dim_ids}
    values = d["value"]
    strides = []
    acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    out = []
    for flat_idx in range(len(values)):
        rem = flat_idx
        coords = []
        for stride, size in zip(strides, sizes):
            coords.append(rem // stride); rem = rem % stride
        codes = {dim_ids[i]: cats[dim_ids[i]][coords[i]] for i in range(len(dim_ids))}
        codes["_value"] = values[flat_idx]
        out.append(codes)
    return out

def fetch_inntekt_husholdninger():
    """06944 — per-kommune median husholdningsinntekt etter skatt + antall."""
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"HusholdType","selection":{"filter":"item","values":["0000"]}},  # alle husholdninger
            {"code":"ContentsCode","selection":{"filter":"item","values":["InntSkatt","AntallHushold"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("06944", body))

def fetch_personinntekt_komponenter():
    """14780 — personinntekt lønn, pensjon, uføretrygd. Begge kjønn, bosatte 17+."""
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"Inntekter225","selection":{"filter":"item","values":["11","12","124"]}},  # Lønn, Pensjon, Uføretrygd
            {"code":"Kjonn","selection":{"filter":"item","values":["0"]}},  # begge kjønn
            {"code":"Populasjon","selection":{"filter":"item","values":["03","04"]}},  # bosatte 17+, m/beløp
            {"code":"ContentsCode","selection":{"filter":"item","values":["GjSnitt","Median","AntPersoner","Belop"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2025"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("14780", body))

def fetch_eierstatus():
    """11084 — eierstatus husholdninger."""
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"EierStatus","selection":{"filter":"item","values":["1","2","3","4"]}},
            {"code":"ContentsCode","selection":{"filter":"item","values":["Husholdning","HusholdningProsent"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("11084", body))

def fetch_boliger():
    """06265 — boliger etter bygningstype."""
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"BygnType","selection":{"filter":"item","values":["01","02","03","04","05","999"]}},
            {"code":"ContentsCode","selection":{"filter":"item","values":["Boliger"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2026"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("06265", body))

INNT_LABEL = {"11":"lonn", "12":"pensjon", "124":"uforetrygd"}
EIER_LABEL = {"1":"total", "2":"selveier", "3":"andels", "4":"leier"}
BYGN_LABEL = {"01":"enebolig", "02":"tomannsbolig", "03":"rekkehus",
              "04":"boligblokk", "05":"bofellesskap", "999":"andre"}

def main():
    print("Fetching 06944 (husholdningsinntekt per kommune)...", flush=True)
    inntekt_rows = fetch_inntekt_husholdninger()
    print("Fetching 14780 (personinntekt komponenter)...", flush=True)
    pers_rows = fetch_personinntekt_komponenter()
    print("Fetching 11084 (eierstatus)...", flush=True)
    eier_rows = fetch_eierstatus()
    print("Fetching 06265 (boliger)...", flush=True)
    bolig_rows = fetch_boliger()

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_id": "SSB_STATBANK",
        "tables": ["06944", "14780", "11084", "06265"],
        "years": {"husholdningsinntekt": "2024", "personinntekt": "2025",
                  "eierstatus": "2024", "boliger": "2026"},
        "kommuner": {}
    }

    # Initialiser
    for c in CODES:
        payload["kommuner"][c] = {
            "antallHusholdninger": None,
            "medianInntektEtterSkatt": None,   # desil 5 verdi = median etter skatt
            "desil1": None, "desil9": None, "desil10": None,  # for spennvidde
            "personLonn_median": None, "personLonn_snitt": None, "personLonn_antall": None,
            "personPensjon_median": None, "personPensjon_snitt": None, "personPensjon_antall": None,
            "personUfore_median": None, "personUfore_snitt": None, "personUfore_antall": None,
            "personBosatte17plus": None,
            "totalLonn_mill": None, "totalPensjon_mill": None, "totalUfore_mill": None,
            "hush_total": None, "hush_selveier": None, "hush_andels": None, "hush_leier": None,
            "pct_selveier": None, "pct_andels": None, "pct_leier": None,
            "boliger_total": None,
            "boliger_enebolig": None, "boliger_tomannsbolig": None, "boliger_rekkehus": None,
            "boliger_boligblokk": None, "boliger_bofellesskap": None, "boliger_andre": None,
        }

    # 06944 — per-kommune median husholdningsinntekt etter skatt + antall husholdninger
    for r in inntekt_rows:
        nr = r["Region"]; cc = r["ContentsCode"]; v = r["_value"]
        if nr not in payload["kommuner"]: continue
        rec = payload["kommuner"][nr]
        if cc == "InntSkatt":
            rec["medianInntektEtterSkatt"] = v
        elif cc == "AntallHushold":
            rec["antallHusholdninger"] = v
        # desil1/9/10 finnes ikke per kommune i 06944 — beholdes som None.

    # 14780 — personinntekt komponenter (bosatte 17+ med beløp, populasjon=04)
    for r in pers_rows:
        nr = r["Region"]; cmp = r["Inntekter225"]; pop = r["Populasjon"]
        cc = r["ContentsCode"]; v = r["_value"]
        if nr not in payload["kommuner"]: continue
        rec = payload["kommuner"][nr]
        lab = INNT_LABEL.get(cmp)
        if not lab: continue
        # Bruk Populasjon=04 (bosatte 17+ med beløp) — det er denne som gir riktig median/gjennomsnitt
        if pop == "04":
            if cc == "Median": rec[f"person{lab.capitalize()}_median"] = v
            elif cc == "GjSnitt": rec[f"person{lab.capitalize()}_snitt"] = v
            elif cc == "AntPersoner": rec[f"person{lab.capitalize()}_antall"] = v
            elif cc == "Belop":
                # Belop er i millioner kr
                if lab == "lonn": rec["totalLonn_mill"] = v
                elif lab == "pensjon": rec["totalPensjon_mill"] = v
                elif lab == "uforetrygd": rec["totalUfore_mill"] = v
        elif pop == "03" and cc == "AntPersoner" and cmp == "11":
            # Antall bosatte 17+ totalt (uavhengig av om de har lønn) — bruk lønn-rad som proxy
            rec["personBosatte17plus"] = v

    # 11084 — eierstatus
    for r in eier_rows:
        nr = r["Region"]; eier = r["EierStatus"]; cc = r["ContentsCode"]; v = r["_value"]
        if nr not in payload["kommuner"]: continue
        rec = payload["kommuner"][nr]
        lab = EIER_LABEL.get(eier)
        if not lab: continue
        if cc == "Husholdning":
            rec[f"hush_{lab}"] = v
        elif cc == "HusholdningProsent" and lab != "total":
            rec[f"pct_{lab}"] = v

    # 06265 — boliger
    for r in bolig_rows:
        nr = r["Region"]; bt = r["BygnType"]; v = r["_value"]
        if nr not in payload["kommuner"]: continue
        rec = payload["kommuner"][nr]
        lab = BYGN_LABEL.get(bt)
        if not lab: continue
        rec[f"boliger_{lab}"] = v

    # Total antall boliger = sum av kategoriene
    for c in CODES:
        rec = payload["kommuner"][c]
        if rec["boliger_enebolig"] is not None:
            rec["boliger_total"] = (
                (rec.get("boliger_enebolig") or 0) +
                (rec.get("boliger_tomannsbolig") or 0) +
                (rec.get("boliger_rekkehus") or 0) +
                (rec.get("boliger_boligblokk") or 0) +
                (rec.get("boliger_bofellesskap") or 0) +
                (rec.get("boliger_andre") or 0)
            )

    # Sanity-print
    b = payload["kommuner"]["1804"]
    print()
    print("Bodø (1804) sample:")
    print(f"  Median inntekt etter skatt: {b['medianInntektEtterSkatt']} kr")
    print(f"  Antall husholdninger (approks): {b['antallHusholdninger']}")
    print(f"  Hush total (fra 11084): {b['hush_total']}")
    print(f"  Andel selveiere: {b['pct_selveier']}%")
    print(f"  Lønn median: {b['personLonn_median']} kr · snitt: {b['personLonn_snitt']} kr")
    print(f"  Pensjon median: {b['personPensjon_median']} kr")
    print(f"  Boliger total: {b['boliger_total']}")
    print(f"  Eneboliger: {b['boliger_enebolig']}")

    # Tell hvor mange kommuner som har data
    has_inntekt = sum(1 for c in CODES if payload["kommuner"][c]["medianInntektEtterSkatt"])
    has_pers = sum(1 for c in CODES if payload["kommuner"][c]["personLonn_median"])
    has_eier = sum(1 for c in CODES if payload["kommuner"][c]["hush_total"])
    has_bolig = sum(1 for c in CODES if payload["kommuner"][c]["boliger_total"])
    print(f"\nData-dekning: inntekt {has_inntekt}/80, person {has_pers}/80, eier {has_eier}/80, bolig {has_bolig}/80")

    # Inject
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const LEVEKAR_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n","") + ";"
    marker_start = "/* LEVEKAR_DATA BEGIN */"
    marker_end = "/* LEVEKAR_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in html:
        pat = re.compile(r"/\* LEVEKAR_DATA BEGIN \*/.*?/\* LEVEKAR_DATA END \*/", re.DOTALL)
        new_html = pat.sub(block, html)
    else:
        anchor = "/* ARBEID_DATA END */"
        if anchor not in html:
            anchor = "/* RENTE_DATA END */"
        new_html = html.replace(anchor, anchor + "\n" + block)
    HTML.write_text(new_html, encoding="utf-8")
    print(f"\nInjected LEVEKAR_DATA ({len(js_lit)} chars)")

if __name__ == "__main__":
    main()
