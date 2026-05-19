#!/usr/bin/env python3
"""Henter arbeidsstyrkedata fra SSB og injiserer som inline ARBEID_DATA i
index.html. Brukes for ærlig forsørgerbyrde-beregning og uføre-indikator.

Kilder:
  11715  Uføretrygdede etter alder per kommune (2024)
  13563  Prioritert arbeidsstyrkestatus per kommune (2024)
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

def fetch_uforetrygdede():
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"Alder","selection":{"filter":"item","values":["18-67"]}},
            {"code":"ContentsCode","selection":{"filter":"item","values":["UforetygdPers","UforetrygdPros"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("11715", body))

def fetch_arbeidsstyrke():
    """Hent sysselsatte 20-66 og utenfor arbeidsstyrken-kategorier."""
    body = {
        "query": [
            {"code":"Region","selection":{"filter":"item","values":CODES}},
            {"code":"HovArbStyrkStatus","selection":{"filter":"item","values":[
                "TOT", "A.01", "A.09", "U.03", "U.04-U.05", "U.06-U.07", "U.90A", "NEET2"
            ]}},
            {"code":"Alder","selection":{"filter":"item","values":["20-66"]}},
            {"code":"InnvandrKat","selection":{"filter":"item","values":["A-G"]}},
            {"code":"ContentsCode","selection":{"filter":"item","values":["Bosatte"]}},
            {"code":"Tid","selection":{"filter":"item","values":["2024"]}},
        ],
        "response":{"format":"json-stat2"}}
    return parse(post_ssb("13563", body))

def main():
    print("Fetching 11715 (uføretrygdede)...", flush=True)
    ufo_rows = fetch_uforetrygdede()
    print("Fetching 13563 (arbeidsstyrkestatus)...", flush=True)
    arb_rows = fetch_arbeidsstyrke()

    # Pivot uføre per kommune (alder 18-67)
    ufo = {}
    for r in ufo_rows:
        nr = r["Region"]; cc = r["ContentsCode"]; v = r["_value"]
        ufo.setdefault(nr, {})[cc] = v

    # Pivot arbeid per kommune × kategori
    arb = {}
    for r in arb_rows:
        nr = r["Region"]; cat = r["HovArbStyrkStatus"]; v = r["_value"]
        arb.setdefault(nr, {})[cat] = v

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_ids": ["SSB_STATBANK"],
        "tables": ["11715", "13563"],
        "year": "2024",
        "alder_arb": "20-66",
        "alder_ufo": "18-67",
        "kommuner": {}
    }

    missing = []
    for c in CODES:
        u = ufo.get(c, {})
        a = arb.get(c, {})
        rec = {
            "uforePers": u.get("UforetygdPers"),       # absolutt antall 18-67
            "uforePct18_67": u.get("UforetrygdPros"),  # andel av befolkningen 18-67 (%)
            "tot20_66": a.get("TOT"),                  # hele 20-66 (kontroll)
            "sysselsatte20_66": a.get("A.01"),         # antall sysselsatte 20-66
            "ledige20_66": a.get("A.09"),              # registrerte arbeidsledige
            "utdanning20_66": a.get("U.03"),           # under utdanning
            "aap_ufore20_66": a.get("U.04-U.05"),      # AAP + uføre i alderen 20-66
            "afp_pensjon20_66": a.get("U.06-U.07"),    # tidlig pensjon
            "andre20_66": a.get("U.90A"),              # andre utenfor
        }
        # Beregn avledede tall
        if rec["sysselsatte20_66"] is not None and rec["tot20_66"]:
            rec["sysselsRate"] = rec["sysselsatte20_66"] / rec["tot20_66"] * 100
        else:
            rec["sysselsRate"] = None
        if rec["sysselsatte20_66"] is None and rec["tot20_66"] is None:
            missing.append(c)
        payload["kommuner"][c] = rec

    print(f"Got data for {len(CODES)-len(missing)}/{len(CODES)} kommuner")
    if missing:
        print(f"Missing: {missing}")
    # Sanity-print
    bodø = payload["kommuner"].get("1804", {})
    print(f"Bodø sample: tot={bodø.get('tot20_66')}, sysselsatte={bodø.get('sysselsatte20_66')}, "
          f"sysselsRate={bodø.get('sysselsRate'):.1f}% if not None else '–', "
          f"uføre18-67={bodø.get('uforePers')} ({bodø.get('uforePct18_67')}%)")

    # Inject
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const ARBEID_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n","") + ";"
    marker_start = "/* ARBEID_DATA BEGIN */"
    marker_end = "/* ARBEID_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in html:
        pat = re.compile(r"/\* ARBEID_DATA BEGIN \*/.*?/\* ARBEID_DATA END \*/", re.DOTALL)
        new_html = pat.sub(block, html)
    else:
        anchor = "/* RENTE_DATA END */"
        if anchor not in html:
            anchor = "/* SSB_FLOWS END */"
        new_html = html.replace(anchor, anchor + "\n" + block)
    HTML.write_text(new_html, encoding="utf-8")
    print(f"Injected ARBEID_DATA ({len(js_lit)} chars)")

if __name__ == "__main__":
    main()
