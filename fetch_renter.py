#!/usr/bin/env python3
"""Henter rente-data fra SSB KOSTRA tabell 12143 og injiserer som inline
RENTE_DATA i index.html. Brukes til rentefølsomhets-drillen i Kapittel 3.1.

Felter per kommune:
  ndr_kr       Netto renter i 1000 kr (AGD97, KOSbelop0000)
  rxp_kr       Renteeksponert gjeld i 1000 kr (KG39)
  rxp_pct      Renteeksponert gjeld i % av BDI (KG39, KOSbelopbrinv0000)
  yr           Siste år tilgjengelig

For 8 kommuner uten KG39 brukes netto lånegjeld (KG31) som proxy, og
proxy-flag settes til true.
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

YEARS = ["2024", "2025"]
BEGREP = ["AGD97", "KG39", "KG31"]  # Netto renter, Renteeksp gjeld, Netto lånegjeld

def post_ssb(body):
    url = "https://data.ssb.no/api/v0/no/table/12143"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch(contents_code):
    body = {
        "query": [
            {"code": "KOKkommuneregion0000", "selection": {"filter": "item", "values": CODES}},
            {"code": "KOKartkap0000", "selection": {"filter": "item", "values": BEGREP}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [contents_code]}},
            {"code": "Tid", "selection": {"filter": "item", "values": YEARS}},
        ],
        "response": {"format": "json-stat2"},
    }
    return post_ssb(body)

def parse(d):
    """jsonstat2 → {region: {begrep: {year: value}}}"""
    dim = d["dimension"]
    dim_ids = d.get("id") or list(dim.keys())
    sizes = d.get("size") or [len(dim[k]["category"]["index"]) for k in dim_ids]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in dim_ids}
    values = d["value"]
    strides = []
    acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    out = {}
    for flat_idx in range(len(values)):
        rem = flat_idx
        coords = []
        for stride, size in zip(strides, sizes):
            coords.append(rem // stride); rem = rem % stride
        codes = {dim_ids[i]: cats[dim_ids[i]][coords[i]] for i in range(len(dim_ids))}
        region = codes.get("KOKkommuneregion0000")
        begrep = codes.get("KOKartkap0000")
        tid = codes.get("Tid")
        v = values[flat_idx]
        out.setdefault(region, {}).setdefault(begrep, {})[tid] = v
    return out

def main():
    print("Fetching 12143 beløp (1000 kr)...", flush=True)
    kr_data = parse(fetch("KOSbelop0000"))
    print("Fetching 12143 % av BDI...", flush=True)
    pct_data = parse(fetch("KOSbelopbrinv0000"))

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_id": "SSB_STATBANK",
        "table": "12143",
        "year_priority": YEARS[::-1],  # try newest first
        "kommuner": {}
    }

    for c in CODES:
        kr = kr_data.get(c, {})
        pct = pct_data.get(c, {})
        # pick latest year with values for AGD97 + (KG39 or KG31)
        rec = None
        for y in YEARS[::-1]:
            ndr = (kr.get("AGD97") or {}).get(y)
            rxp = (kr.get("KG39") or {}).get(y)
            lan = (kr.get("KG31") or {}).get(y)
            rxp_p = (pct.get("KG39") or {}).get(y)
            if ndr is not None and (rxp is not None or lan is not None):
                use_proxy = rxp is None
                rec = {
                    "yr": y,
                    "ndr_kr": ndr,           # netto renter, 1000 kr
                    "rxp_kr": rxp if rxp is not None else lan,  # renteeksp gjeld eller proxy
                    "rxp_pct": rxp_p,        # i % av BDI
                    "proxy": use_proxy
                }
                break
        if rec is None:
            rec = {"yr": None, "ndr_kr": None, "rxp_kr": None, "rxp_pct": None, "proxy": False}
        payload["kommuner"][c] = rec

    valid = sum(1 for k,v in payload["kommuner"].items() if v["ndr_kr"] is not None)
    proxied = sum(1 for k,v in payload["kommuner"].items() if v.get("proxy"))
    print(f"Got data for {valid}/{len(CODES)} kommuner ({proxied} with KG31-proxy)")

    # Inject into HTML
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const RENTE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n","") + ";"
    marker_start = "/* RENTE_DATA BEGIN */"
    marker_end = "/* RENTE_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in html:
        pat = re.compile(r"/\* RENTE_DATA BEGIN \*/.*?/\* RENTE_DATA END \*/", re.DOTALL)
        new_html = pat.sub(block, html)
    else:
        # Insert right after SSB_FLOWS END marker
        anchor = "/* SSB_FLOWS END */"
        if anchor not in html:
            print("ERROR: anchor not found", file=sys.stderr); sys.exit(1)
        new_html = html.replace(anchor, anchor + "\n" + block)
    HTML.write_text(new_html, encoding="utf-8")
    print(f"Injected RENTE_DATA ({len(js_lit)} chars)")

if __name__ == "__main__":
    main()
