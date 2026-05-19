#!/usr/bin/env python3
"""Injiser historiske folketall (2000, 2005, 2010, 2015, 2020, 2025)
i DATA.kommuner i index.html. Henter dataene fra SSB tabell 07459 via
codelist agg_KommSummer (sammenslåtte tidsserier for kommuner 2024).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "index.html"

CODES = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
"1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
"1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
"1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503",
"5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530",
"5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605",
"5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628",
"5630","5632","5634","5636"]
YEARS = ["2000","2005","2010","2015","2020","2025"]

def fetch_ssb():
    url = "https://data.ssb.no/api/pxwebapi/v2-beta/tables/07459/data?lang=no&valueCodes[Tid]={tid}&codelist[Region]=agg_KommSummer&valueCodes[Region]={regs}&valueCodes[ContentsCode]=Personer1&outputformat=json-stat2"
    regs = ",".join("K-"+c for c in CODES)
    tid = ",".join(YEARS)
    url = url.format(tid=tid, regs=regs)
    req = urllib.request.Request(url, headers={"Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_jsonstat2(d):
    """Returns dict {kommune_code: {year: pop}}"""
    dim = d["dimension"]
    region_idx = dim["Region"]["category"]["index"]
    tid_idx = dim["Tid"]["category"]["index"]
    region_codes = list(region_idx.keys())
    tid_codes = list(tid_idx.keys())
    values = d["value"]
    n_tid = len(tid_codes)
    out = {}
    for ri, rcode in enumerate(region_codes):
        kcode = rcode.replace("K-","")
        out[kcode] = {}
        for ti, year in enumerate(tid_codes):
            v = values[ri*n_tid + ti]
            if v and v > 0:
                out[kcode][year] = v
    return out

def main():
    print("Fetcher SSB ...")
    d = fetch_ssb()
    hist = parse_jsonstat2(d)
    print(f"Got hist for {len(hist)} kommuner")
    missing = [c for c in CODES if c not in hist or not hist[c]]
    if missing:
        print("WARN: ingen data for:", missing)

    print("Reading index.html ...")
    html = HTML.read_text(encoding="utf-8")
    original_len = len(html)

    # For each kommune entry, find pattern: "NNNN":{"navn":"...","fylke":"...","alder":[ARRAY]}
    # and inject ,"hist":{...} before the closing brace.
    pat = re.compile(
        r'("(\d{4})":\{"navn":"[^"]+","fylke":"[^"]+","alder":\[[^\]]+\])'
        r'(\})'
    )

    count = 0
    skipped = 0
    def replacer(m):
        nonlocal count, skipped
        prefix = m.group(1)
        nr = m.group(2)
        close = m.group(3)
        h = hist.get(nr, {})
        if not h:
            skipped += 1
            return m.group(0)
        # Sort by year, only include years with data
        keys = sorted(h.keys())
        hist_json = "{" + ",".join(f'"{y}":{h[y]}' for y in keys) + "}"
        count += 1
        return f'{prefix},"hist":{hist_json}{close}'

    new_html = pat.sub(replacer, html)
    print(f"Injected hist into {count} kommuner. Skipped {skipped}.")

    if count == 0:
        print("ERROR: no matches found. Aborting.")
        sys.exit(1)

    # Sanity check: file should grow but not shrink
    if len(new_html) <= original_len:
        print(f"WARN: file did not grow (was {original_len}, now {len(new_html)})")

    HTML.write_text(new_html, encoding="utf-8")
    print(f"Wrote {HTML}. Size: {original_len} -> {len(new_html)} (+{len(new_html)-original_len})")

if __name__ == "__main__":
    main()
