#!/usr/bin/env python3
"""Fetch SSB 09588 (innland + innvandring flyttinger) for all 80 Nord-Norge
kommuner, aggregate to fylke + landsdel. Also extract Fafo 2025:14 PDF text."""
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "refugee_data.json"

# Kommune-koder, gruppert per fylke
NORDLAND = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
    "1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
    "1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
    "1860","1865","1866","1867","1868","1870","1871","1874","1875"]
TROMS = ["5501","5503","5510","5512","5514","5516","5518","5520","5522","5524",
    "5526","5528","5530","5532","5534","5536","5538","5540","5542","5544","5546"]
FINNMARK = ["5601","5603","5605","5607","5610","5612","5614","5616","5618","5620",
    "5622","5624","5626","5628","5630","5632","5634","5636"]

ALL_CODES = NORDLAND + TROMS + FINNMARK
YEARS = list(range(2002, 2026))

def fetch_09588():
    """Fetch via the v2-beta endpoint. URL-based GET works fine for moderate-sized
    queries. ~3840 cells expected."""
    regs = ",".join("K-"+c for c in ALL_CODES)
    tid = ",".join(str(y) for y in YEARS)
    url = (
        "https://data.ssb.no/api/pxwebapi/v2-beta/tables/09588/data"
        f"?lang=no&codelist[Region]=agg_KommGjeldende"
        f"&valueCodes[Region]={regs}"
        f"&valueCodes[ContentsCode]=NettoInnland,Nettoinnvandring"
        f"&valueCodes[Tid]={tid}"
        f"&outputformat=json-stat2"
    )
    print(f"Fetching SSB 09588 (URL length {len(url)})...")
    req = urllib.request.Request(url, headers={"Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_09588(d):
    """Returns {kommune: {year: {metric: value}}}"""
    dim = d["dimension"]
    region_codes = list(dim["Region"]["category"]["index"].keys())
    content_codes = list(dim["ContentsCode"]["category"]["index"].keys())
    tid_codes = list(dim["Tid"]["category"]["index"].keys())
    values = d["value"]
    n_c = len(content_codes)
    n_t = len(tid_codes)
    out = {}
    for ri, rcode in enumerate(region_codes):
        kcode = rcode.replace("K-","")
        out[kcode] = {}
        for ci, c in enumerate(content_codes):
            for ti, y in enumerate(tid_codes):
                idx = ri*n_c*n_t + ci*n_t + ti
                v = values[idx]
                if v is None: continue
                out[kcode].setdefault(int(y), {})[c] = v
    return out

def aggregate(perK):
    """Sum per fylke and landsdel."""
    def sum_group(codes):
        out = {y: {"NettoInnland":0, "Nettoinnvandring":0} for y in YEARS}
        for c in codes:
            kd = perK.get(c, {})
            for y, vals in kd.items():
                for k,v in vals.items():
                    out[y][k] = out[y].get(k,0) + (v or 0)
        return out
    return {
        "nordland": sum_group(NORDLAND),
        "troms":    sum_group(TROMS),
        "finnmark": sum_group(FINNMARK),
        "nordnorge":sum_group(ALL_CODES),
    }

def flatten_for_chart(agg):
    """Transform to series-arrays per region for chart."""
    out = {"years": YEARS}
    for region, byyear in agg.items():
        innland = [byyear[y]["NettoInnland"] for y in YEARS]
        innvandring = [byyear[y]["Nettoinnvandring"] for y in YEARS]
        out[region] = {"innland": innland, "innvandring": innvandring}
    return out

def try_pdf():
    pdf_path = HERE / "fafo_20927.pdf"
    if not pdf_path.exists():
        # Try downloading
        try:
            print("Downloading Fafo PDF...")
            urllib.request.urlretrieve("https://www.fafo.no/images/pub/2025/20927.pdf", pdf_path)
            print(f"Saved to {pdf_path}")
        except Exception as e:
            print(f"PDF fetch failed: {e}")
            return None
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            text_parts.append(f"\n=== PAGE {i+1} ===\n{t}")
        full = "\n".join(text_parts)
        outtxt = HERE / "fafo_extracted.txt"
        outtxt.write_text(full, encoding="utf-8")
        print(f"Extracted {len(reader.pages)} pages to {outtxt}")
        return outtxt
    except Exception as e:
        print(f"PDF extract failed: {e}")
        return None

def main():
    data = fetch_09588()
    perK = parse_09588(data)
    agg = aggregate(perK)
    flat = flatten_for_chart(agg)
    print(f"\nSample (Nord-Norge):")
    print(f"  years: {flat['years'][:3]} ... {flat['years'][-3:]}")
    print(f"  innland sum 2002-2025: {sum(flat['nordnorge']['innland'])}")
    print(f"  innvandring sum 2002-2025: {sum(flat['nordnorge']['innvandring'])}")
    OUT.write_text(json.dumps(flat, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to {OUT}")
    try_pdf()

if __name__ == "__main__":
    main()
