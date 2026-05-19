#!/usr/bin/env python3
"""Henter kjønnsbalansen i unge aldersgrupper per kommune fra SSB tabell 07459
og injiserer som inline KJONN_DATA i assets/data.js.

Brukes til Temaserie 03 — Kvinneflukten.

Henter alder 18-44 år per kjønn per kommune (1.1.2026) og summerer til
aldersgrupper 18-24, 25-29, 30-34, 35-39, 40-44.
"""
import json
import re
import urllib.request
import datetime
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

CODES = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
"1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
"1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
"1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503",
"5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530",
"5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605",
"5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628",
"5630","5632","5634","5636"]

# Alder 18-44, formatert som tresifrede koder
ALDER_KODER = [f"{a:03d}" for a in range(18, 45)]

# Aldersgrupper for aggregering
GRUPPER = [
    ("a18_24", 18, 24),
    ("a25_29", 25, 29),
    ("a30_34", 30, 34),
    ("a35_39", 35, 39),
    ("a40_44", 40, 44),
]

def post_ssb(body):
    url = "https://data.ssb.no/api/v0/no/table/07459"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
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

def main():
    print("Henter SSB 07459: kjønn × alder 18-44 × kommune × 2026...", flush=True)
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"Kjonn","selection":{"filter":"item","values":["1","2"]}},
            {"code":"Alder","selection":{"filter":"item","values":ALDER_KODER}},
            {"code":"ContentsCode","selection":{"filter":"item","values":["Personer1"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2026"]}},
        ],
        "response":{"format":"json-stat2"}}
    rows = parse(post_ssb(body))
    print(f"Mottok {len(rows)} verdier", flush=True)

    # Aggreger: per (kommune, kjønn, gruppe)
    agg = {}
    for r in rows:
        nr = r["Region"]; k = r["Kjonn"]; a = int(r["Alder"]); v = r["_value"] or 0
        for gnavn, lo, hi in GRUPPER:
            if lo <= a <= hi:
                key = (nr, k, gnavn)
                agg[key] = agg.get(key, 0) + v
                break

    # Bygg payload
    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_id": "SSB_STATBANK",
        "table": "07459",
        "year": "2026",
        "alder_range": "18-44",
        "grupper": [g[0] for g in GRUPPER],
        "kommuner": {}
    }
    for c in CODES:
        rec = {"menn": {}, "kvinner": {}, "total": {}}
        for gnavn, lo, hi in GRUPPER:
            menn = agg.get((c, "1", gnavn), 0)
            kvinner = agg.get((c, "2", gnavn), 0)
            rec["menn"][gnavn] = menn
            rec["kvinner"][gnavn] = kvinner
            rec["total"][gnavn] = menn + kvinner
        # Sum 18-44
        rec["menn"]["sum_18_44"] = sum(rec["menn"][g] for g, _, _ in [(g[0], 0, 0) for g in GRUPPER])
        rec["kvinner"]["sum_18_44"] = sum(rec["kvinner"][g] for g, _, _ in [(g[0], 0, 0) for g in GRUPPER])
        # Kjønnsbalanse: menn per 100 kvinner
        if rec["kvinner"]["sum_18_44"] > 0:
            rec["mpr100k_18_44"] = round(rec["menn"]["sum_18_44"] / rec["kvinner"]["sum_18_44"] * 100, 1)
        else:
            rec["mpr100k_18_44"] = None
        # Per gruppe
        rec["mpr100k_per_gruppe"] = {}
        for gnavn, _, _ in GRUPPER:
            k = rec["kvinner"][gnavn]
            m = rec["menn"][gnavn]
            rec["mpr100k_per_gruppe"][gnavn] = round(m / k * 100, 1) if k > 0 else None
        payload["kommuner"][c] = rec

    # Sanity
    bod = payload["kommuner"].get("1804", {})
    print(f"Bodø sample: menn 18-44 = {bod['menn'].get('sum_18_44')}, kvinner = {bod['kvinner'].get('sum_18_44')}, "
          f"M/100K = {bod['mpr100k_18_44']}")

    # Inject i data.js
    js = DATA_JS.read_text(encoding="utf-8")
    js_lit = "const KJONN_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n", "") + ";"
    marker_start = "/* KJONN_DATA BEGIN */"
    marker_end = "/* KJONN_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in js:
        pat = re.compile(r"/\* KJONN_DATA BEGIN \*/.*?/\* KJONN_DATA END \*/", re.DOTALL)
        new_js = pat.sub(block, js)
    else:
        # Sett inn etter LEVEKAR_DATA END
        anchor = "/* LEVEKAR_DATA END */"
        if anchor not in js:
            raise SystemExit("LEVEKAR_DATA END ikke funnet i data.js — kan ikke injisere")
        new_js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(new_js, encoding="utf-8")
    print(f"Injisert KJONN_DATA ({len(js_lit)} chars) i {DATA_JS}")

if __name__ == "__main__":
    main()
