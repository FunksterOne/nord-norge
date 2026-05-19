#!/usr/bin/env python3
"""Henter Nord-Norges flyttetall fra SSB Statistikkbanken og injiserer som
inline `SSB_FLOWS` i index.html. Brukes til Modul A i Steg 04½.

Tabeller:
  09588 — flyttinger per fylke (innenlands netto, nettoinnvandring)
  11366 — statsborgerskap per fylke (filtrert til Ukraina = kode 148)

Fylkeskoder håndteres på tvers av kommunereformene:
  2002–2019: 18 Nordland, 19 Troms, 20 Finnmark
  2020–2023: 18 Nordland, 54 Troms og Finnmark
  2024–:     18 Nordland, 55 Troms, 56 Finnmark
"""
import json
import sys
import urllib.request
import datetime
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "assets" / "data.js"

YEARS_FLOW = [str(y) for y in range(2002, 2026)]
YEARS_UKR = [str(y) for y in range(2016, 2027)]
REGIONS = ["18", "19", "20", "54", "55", "56"]

REGION_LABEL = {
    "18": "Nordland",
    "19": "Troms (-2019)",
    "20": "Finnmark (-2019)",
    "54": "Troms og Finnmark (2020-23)",
    "55": "Troms",
    "56": "Finnmark",
}

def post_ssb(table_id: str, body: dict) -> dict:
    url = f"https://data.ssb.no/api/v0/no/table/{table_id}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_jsonstat2_3d(d, time_codes):
    """Parser response with dimensions Region, Tid, ContentsCode (in some order).
    Returns nested dict: {region: {year: {content: value}}}.
    """
    dim = d["dimension"]
    dim_ids = d.get("id") or list(dim.keys())
    sizes = d.get("size") or [len(dim[k]["category"]["index"]) for k in dim_ids]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in dim_ids}
    values = d["value"]
    # build out
    out = {}
    n = len(values)
    if n == 0:
        return out
    strides = []
    acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc)
        acc *= s
    for flat_idx in range(n):
        v = values[flat_idx]
        coords = []
        idx = flat_idx
        for s in sizes:
            sub = idx // (acc // s) if False else 0
        # Simpler: decode flat index to per-dim index
        coords = []
        rem = flat_idx
        for stride, size in zip(strides, sizes):
            coords.append(rem // stride)
            rem = rem % stride
        # Map to codes
        codes = {dim_ids[i]: cats[dim_ids[i]][coords[i]] for i in range(len(dim_ids))}
        region = codes.get("Region")
        tid = codes.get("Tid")
        content = codes.get("ContentsCode")
        out.setdefault(region, {}).setdefault(tid, {})[content] = v
    return out

def fetch_flytting():
    body = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
            {"code": "ContentsCode", "selection": {"filter": "item",
                "values": ["NettoInnland", "Nettoinnvandring", "Innvandring", "Utvandring"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": YEARS_FLOW}},
        ],
        "response": {"format": "json-stat2"},
    }
    return post_ssb("09588", body)

def fetch_ukraina():
    body = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": REGIONS}},
            {"code": "Statsborg", "selection": {"filter": "item", "values": ["148"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": YEARS_UKR}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Personer1"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return post_ssb("11366", body)

def build_series():
    print("Fetching 09588 (flyttinger)...", flush=True)
    flow = fetch_flytting()
    print("Fetching 11366 (statsborgerskap Ukraina)...", flush=True)
    ukr = fetch_ukraina()

    # Parse flow data: region -> tid -> content -> value
    flow_data = parse_jsonstat2_3d(flow, YEARS_FLOW)
    ukr_data = parse_jsonstat2_3d(ukr, YEARS_UKR)

    years = list(range(2002, 2026))

    def get_flow(region, year, content):
        v = flow_data.get(region, {}).get(str(year), {}).get(content)
        return v if v is not None else 0

    def get_ukr(region, year):
        v = ukr_data.get(region, {}).get(str(year), {}).get("Personer1")
        return v if v is not None else 0

    # Per-fylke series — Nord-Norge total, plus three fylker with reform-aware aggregation
    def nordland_yr(year, content):
        return get_flow("18", year, content)

    def troms_yr(year, content):
        # 2002-2019: code 19. 2020-2023: half of 54. 2024+: code 55.
        # Half-of-54 is rough; for visualization purposes we just use 54 as combined and
        # show Troms+Finnmark together for that period. So return 19 for ≤2019, 0 for
        # 2020-2023 (handled separately as TF combined), 55 for ≥2024.
        if year <= 2019:
            return get_flow("19", year, content)
        elif year <= 2023:
            return 0  # part of TF combined
        else:
            return get_flow("55", year, content)

    def finnmark_yr(year, content):
        if year <= 2019:
            return get_flow("20", year, content)
        elif year <= 2023:
            return 0
        else:
            return get_flow("56", year, content)

    def tf_combined_yr(year, content):
        if year <= 2019:
            return get_flow("19", year, content) + get_flow("20", year, content)
        elif year <= 2023:
            return get_flow("54", year, content)
        else:
            return get_flow("55", year, content) + get_flow("56", year, content)

    def nordnorge_yr(year, content):
        return get_flow("18", year, content) + tf_combined_yr(year, content)

    def ukr_nn_yr(year):
        # Ukrainians in Nord-Norge: sum 18 + (19+20 ≤2019, 54 2020-23, 55+56 ≥2024)
        n = get_ukr("18", year)
        if year <= 2019:
            n += get_ukr("19", year) + get_ukr("20", year)
        elif year <= 2023:
            n += get_ukr("54", year)
        else:
            n += get_ukr("55", year) + get_ukr("56", year)
        return n

    def series(fn_yr, content):
        return [fn_yr(y, content) for y in years]

    # Ukraine year-over-year delta = approximate net Ukrainian inflow
    ukr_stock = [ukr_nn_yr(y) for y in years]
    ukr_delta = [None] * len(years)
    for i, y in enumerate(years):
        prev = ukr_nn_yr(y - 1) if y - 1 >= 2016 else None
        cur = ukr_stock[i]
        if prev is not None:
            ukr_delta[i] = cur - prev
        else:
            ukr_delta[i] = None  # before 2017 we don't have prior-year baseline

    return {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_id": "SSB_STATBANK",
        "tables": ["09588", "11366"],
        "years": years,
        "nordNorge": {
            "nettoInnland": series(nordnorge_yr, "NettoInnland"),
            "nettoInnvandring": series(nordnorge_yr, "Nettoinnvandring"),
            "innvandring": series(nordnorge_yr, "Innvandring"),
            "utvandring": series(nordnorge_yr, "Utvandring"),
            "ukraineStock": ukr_stock,
            "ukraineDelta": ukr_delta,
        },
        "fylker": {
            "Nordland": {
                "nettoInnland": series(nordland_yr, "NettoInnland"),
                "nettoInnvandring": series(nordland_yr, "Nettoinnvandring"),
            },
            "Troms": {
                "nettoInnland": series(troms_yr, "NettoInnland"),
                "nettoInnvandring": series(troms_yr, "Nettoinnvandring"),
            },
            "Finnmark": {
                "nettoInnland": series(finnmark_yr, "NettoInnland"),
                "nettoInnvandring": series(finnmark_yr, "Nettoinnvandring"),
            },
            "TromsOgFinnmark": {
                "nettoInnland": series(tf_combined_yr, "NettoInnland"),
                "nettoInnvandring": series(tf_combined_yr, "Nettoinnvandring"),
            },
        },
    }

def inject_into_html(payload):
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const SSB_FLOWS = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n", "") + ";"

    marker_start = "/* SSB_FLOWS BEGIN */"
    marker_end = "/* SSB_FLOWS END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"

    if marker_start in html:
        # Replace existing block
        import re
        pattern = re.compile(r"/\* SSB_FLOWS BEGIN \*/.*?/\* SSB_FLOWS END \*/", re.DOTALL)
        new_html = pattern.sub(block, html)
    else:
        # Insert after SOURCES = {...}; (find end of SOURCES const)
        # We'll insert right before "const K =" line
        anchor = "const K = Object.entries(DATA.kommuner)"
        if anchor not in html:
            print(f"ERROR: anchor {anchor!r} not found", file=sys.stderr)
            sys.exit(1)
        new_html = html.replace(anchor, block + "\n" + anchor)

    HTML.write_text(new_html, encoding="utf-8")
    print(f"Injected SSB_FLOWS into index.html ({len(js_lit)} chars)")

def main():
    payload = build_series()
    print(f"Nord-Norge nettoinnvandring: {payload['nordNorge']['nettoInnvandring'][:5]}... {payload['nordNorge']['nettoInnvandring'][-3:]}")
    print(f"Nord-Norge nettoInnland: {payload['nordNorge']['nettoInnland'][:5]}... {payload['nordNorge']['nettoInnland'][-3:]}")
    print(f"Ukraine stock 2022-2025: {payload['nordNorge']['ukraineStock'][-4:]}")
    print(f"Ukraine delta 2022-2025: {payload['nordNorge']['ukraineDelta'][-4:]}")
    inject_into_html(payload)

if __name__ == "__main__":
    main()
