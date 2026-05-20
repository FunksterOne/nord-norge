#!/usr/bin/env python3
"""Henter husholdningsdata per kommune × husholdningstype × år fra SSB 06944
og injiserer som inline HUSH_DATA i assets/data.js.

SSB 06944: 'Inntekt for husholdninger, etter region, husholdningstype,
statistikkvariabel og år'

Husholdningstyper i 06944:
  0000  Alle husholdninger
  0001  Aleneboende
  0002  Par uten barn
  0003  Par med barn 0-17 år
  0004  Enslig mor/far med barn 0-17 år
  + beregnet 'andre' (flerfamilie/voksne hjemmeboende barn) = alle − sum(0001..0004)

Statistikkvariabler vi henter:
  AntallHushold     antall husholdninger
  InntSkatt         median inntekt etter skatt (kr)

Tidsserie: 2005-2024 (20 årganger). Brukes på nivå 2 (utvidbar visning).
Statisk 2024-snitt brukes på nivå 1.

Aggregat for fylke og landsdel:
  Antall: sum
  Median: vektet snitt av kommunemedianer (vekt = antall husholdninger).
          Dette er en praktisk approksimasjon — den matematiske medianen
          krever mikrodata vi ikke har. Markeres som 'vektet snitt' i UI.
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

# Mapping fra SSB-koder til våre korte nøkler
TYPE_KEYS = {
    "0000": "alle",
    "0001": "aleneboende",
    "0002": "par_uten_barn",
    "0003": "par_med_barn",
    "0004": "enslig_forelder",
}
TYPE_LABELS = {
    "alle":             "Alle husholdninger",
    "aleneboende":      "Aleneboende",
    "par_uten_barn":    "Par uten barn",
    "par_med_barn":     "Par med barn 0–17 år",
    "enslig_forelder":  "Enslig forelder",
    "andre":            "Andre (flerfamilie/voksne hjemmeboende barn)",
}
YEARS = [str(y) for y in range(2005, 2025)]
LATEST = "2024"


def post_ssb(body):
    url = "https://data.ssb.no/api/v0/no/table/06944"
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def parse(d):
    """jsonstat2 → {region: {type: {year: {contents: value}}}}"""
    dim = d["dimension"]
    ids = d.get("id") or list(dim.keys())
    sizes = d.get("size") or [len(dim[k]["category"]["index"]) for k in ids]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in ids}
    values = d["value"]
    strides = []; acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    out = {}
    for i in range(len(values)):
        v = values[i]
        if v is None:
            continue
        rem = i; coords = []
        for st, sz in zip(strides, sizes):
            coords.append(rem // st); rem %= st
        codes = {ids[j]: cats[ids[j]][coords[j]] for j in range(len(ids))}
        reg = codes.get("Region")
        ht = codes.get("HusholdType")
        cc = codes.get("ContentsCode")
        tid = codes.get("Tid")
        out.setdefault(reg, {}).setdefault(ht, {}).setdefault(tid, {})[cc] = v
    return out


def main():
    print(f"Henter SSB 06944 — {len(CODES)} kommuner × 5 typer × 20 år ...", flush=True)
    body = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": CODES}},
            {"code": "HusholdType", "selection": {"filter": "item",
                "values": ["0000","0001","0002","0003","0004"]}},
            {"code": "ContentsCode", "selection": {"filter": "item",
                "values": ["AntallHushold","InntSkatt"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": YEARS}},
        ],
        "response": {"format": "json-stat2"}
    }
    raw = post_ssb(body)
    parsed = parse(raw)
    print(f"  Mottok data for {len(parsed)} kommuner")

    # Bygg payload per kommune
    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source": "SSB tabell 06944",
        "year_latest": int(LATEST),
        "years": [int(y) for y in YEARS],
        "type_keys": list(TYPE_KEYS.values()) + ["andre"],
        "type_labels": TYPE_LABELS,
        "kommuner": {},
    }

    for kode in CODES:
        kdata = parsed.get(kode, {})
        # Bygg per-type aggregat
        latest = {}        # type → {n, median}
        tidsserie = {}     # år → type → {n, median}

        # Initialiser tidsserie-struktur
        for yr in YEARS:
            tidsserie[yr] = {}

        # For hver SSB-type, hent latest + tidsserie
        sum_n_4 = 0  # for å beregne 'andre' i siste år
        for ssb_type, key in TYPE_KEYS.items():
            type_data = kdata.get(ssb_type, {})
            # Siste år
            v = type_data.get(LATEST, {})
            n = v.get("AntallHushold")
            med = v.get("InntSkatt")
            latest[key] = {"n": n, "median": med}
            if key != "alle" and n is not None:
                sum_n_4 += n
            # Tidsserie
            for yr in YEARS:
                ty = type_data.get(yr, {})
                if ty.get("AntallHushold") is not None or ty.get("InntSkatt") is not None:
                    tidsserie[yr][key] = {
                        "n": ty.get("AntallHushold"),
                        "median": ty.get("InntSkatt"),
                    }

        # Beregn 'andre' for siste år: alle − sum av 4 typer
        alle_n = (latest.get("alle") or {}).get("n")
        if alle_n is not None:
            andre_n = alle_n - sum_n_4
            if andre_n < 0:
                andre_n = 0
            latest["andre"] = {"n": andre_n, "median": None}  # median for andre ikke direkte tilgjengelig
        else:
            latest["andre"] = {"n": None, "median": None}

        # Beregn 'andre' for hvert år i tidsserien
        for yr in YEARS:
            yr_data = tidsserie[yr]
            alle_y = (yr_data.get("alle") or {}).get("n")
            if alle_y is not None:
                sum4 = sum((yr_data.get(k) or {}).get("n", 0) or 0
                           for k in ["aleneboende","par_uten_barn","par_med_barn","enslig_forelder"])
                yr_data["andre"] = {"n": max(0, alle_y - sum4), "median": None}

        payload["kommuner"][kode] = {
            "latest": latest,
            "tidsserie": tidsserie,
        }

    # Aggreger per fylke og landsdel
    NL = [c for c in CODES if 1800 <= int(c) < 1900]
    TR = [c for c in CODES if 5500 <= int(c) < 5600]
    FI = [c for c in CODES if 5600 <= int(c) < 5700]

    def aggregate(kommune_koder):
        """Aggregerer husholdningsdata for et sett kommuner.
        Antall: sum. Median: vektet snitt av kommunemedianer."""
        # Latest aggregat
        latest = {}
        for key in list(TYPE_KEYS.values()) + ["andre"]:
            n_sum = 0
            weighted_median_sum = 0
            n_with_median = 0
            for k in kommune_koder:
                row = payload["kommuner"][k]["latest"].get(key, {})
                n_k = row.get("n")
                m_k = row.get("median")
                if n_k is not None:
                    n_sum += n_k
                if m_k is not None and n_k is not None:
                    weighted_median_sum += m_k * n_k
                    n_with_median += n_k
            median_w = (weighted_median_sum / n_with_median) if n_with_median > 0 else None
            latest[key] = {"n": n_sum if n_sum > 0 else None,
                           "median": round(median_w) if median_w else None}

        # Tidsserie aggregat
        tidsserie = {}
        for yr in YEARS:
            year_agg = {}
            for key in list(TYPE_KEYS.values()) + ["andre"]:
                n_sum = 0
                wms = 0
                n_med = 0
                for k in kommune_koder:
                    row = (payload["kommuner"][k]["tidsserie"].get(yr) or {}).get(key) or {}
                    n_k = row.get("n")
                    m_k = row.get("median")
                    if n_k is not None:
                        n_sum += n_k
                    if m_k is not None and n_k is not None:
                        wms += m_k * n_k
                        n_med += n_k
                m_w = round(wms / n_med) if n_med > 0 else None
                year_agg[key] = {"n": n_sum if n_sum > 0 else None, "median": m_w}
            tidsserie[yr] = year_agg

        return {"latest": latest, "tidsserie": tidsserie}

    payload["fylker"] = {
        "Nordland": aggregate(NL),
        "Troms": aggregate(TR),
        "Finnmark": aggregate(FI),
    }
    payload["landsdel"] = aggregate(CODES)

    # Print sammendrag
    print("\n=== Sammendrag latest (2024) ===")
    for navn, key_set in [("Bodø", ["1804"]), ("Hammerfest", ["5603"]),
                          ("Nordland", NL), ("Troms", TR), ("Finnmark", FI),
                          ("Nord-Norge", CODES)]:
        if len(key_set) == 1:
            data = payload["kommuner"][key_set[0]]["latest"]
        else:
            data = payload["fylker"].get(navn, payload["landsdel"])["latest"] if navn != "Nord-Norge" else payload["landsdel"]["latest"]
        alle = data.get("alle", {})
        alene = data.get("aleneboende", {})
        par_b = data.get("par_med_barn", {})
        alene_pct = (alene.get("n", 0) / alle.get("n", 1) * 100) if alle.get("n") else 0
        print(f"{navn:15s} alle={alle.get('n','?'):>8} median={alle.get('median','?'):>8}  alene={alene_pct:5.1f}%@{alene.get('median','?')}  parm.barn={par_b.get('median','?')}")

    # Inject
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const HUSH_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n","") + ";"
    marker_start = "/* HUSH_DATA BEGIN */"
    marker_end = "/* HUSH_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in html:
        pat = re.compile(r"/\* HUSH_DATA BEGIN \*/.*?/\* HUSH_DATA END \*/", re.DOTALL)
        new_html = pat.sub(block, html)
    else:
        for anchor in ("/* LEVEKAR_DATA END */", "/* GJELD_DATA END */", "/* RENTE_DATA END */"):
            if anchor in html:
                new_html = html.replace(anchor, anchor + "\n" + block, 1)
                break
        else:
            print("ERROR: ingen anchor funnet", file=sys.stderr); sys.exit(1)
    HTML.write_text(new_html, encoding="utf-8")
    print(f"\nInjected HUSH_DATA ({len(js_lit):,} chars)")


if __name__ == "__main__":
    main()
