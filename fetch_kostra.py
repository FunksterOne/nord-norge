#!/usr/bin/env python3
"""Bygger KOSTRA-oeyeblikksbildet DATA.proj.kostra (per kommune) og
DATA.proj.kostra_bench (median Alle/Nordland/Troms/Finnmark) for nyeste
KOSTRA-aar, og oppdaterer DATA.proj.kostra_ts med gjeldende SSB-verdier.

Gjenskaper byggelogikken som manglet i repoet (verifisert mot 2024-blokken
som ble generert i mai 2026): hvert felt hentes fra en navngitt SSB-tabell
(kommunekonsern), med aarsprioritet per felt -- nyeste aar foerst, deretter
forrige aar dersom SSB mangler verdi. Benchmark = median av de 80 kommunenes
verdier (eksklusive manglende), rundet til 1 desimal.

Kjoering:
  python fetch_kostra.py --verify 2024   # sammenlign mot eksisterende blokk, skriver ikke
  python fetch_kostra.py                 # bygg nyeste aar og skriv til data.js
"""
import argparse
import datetime
import json
import statistics
import sys
import urllib.request

from datajs import load_data, save_data
from fetch_bolig import CODES, fylke

REG = "KOKkommuneregion0000"
PCT_BDI = "KOSbelopbrinv0000"  # andel av brutto driftsinntekter (12143)

# felt -> (tabell, {dimensjon: kode})
FIELDS = {
    "ndr": ("12143", {"KOKartkap0000": "AGD23", "ContentsCode": PCT_BDI}),
    "bdr": ("12143", {"KOKartkap0000": "AGD18", "ContentsCode": PCT_BDI}),
    "fond": ("12143", {"KOKartkap0000": "56", "ContentsCode": PCT_BDI}),
    "gjeld": ("12143", {"KOKartkap0000": "KG31", "ContentsCode": PCT_BDI}),
    "lgjeld": ("12143", {"KOKartkap0000": "KG25", "ContentsCode": PCT_BDI}),
    "finutg": ("12143", {"KOKartkap0000": "AGD86", "ContentsCode": PCT_BDI}),
    "akap": ("12143", {"KOKartkap0000": "KG28", "ContentsCode": PCT_BDI}),
    "frieink": ("12134", {"ContentsCode": "KOSAG110000"}),
    "omsorg_pct": ("12209", {"ContentsCode": "KOSANDELNDUPLOM0000"}),
    "khelse_pct": ("12209", {"ContentsCode": "KOSANDELNDUkhels0000"}),
    "skole_pct": ("12255", {"ContentsCode": "KOSregnind10000"}),
    "bhg_pct": ("13502", {"ContentsCode": "KOSutg010000"}),
    "kultur_pct": ("13135", {"ContentsCode": "KOSdriftkultur0000"}),
    "kirke_pct": ("12025", {"ContentsCode": "KOSnedriftutkirk0000"}),
    "eiendom_pct": ("12051", {"ContentsCode": "KOSndueieforvtot0000"}),
    "omsorg_pi": ("12209", {"ContentsCode": "KOSbduFKG9innbyg0000"}),
    "skole_pi": ("12255", {"ContentsCode": "KOSregnind20000"}),
    "bhg_pi": ("13502", {"ContentsCode": "KOSutg020000"}),
    "kultur_pi": ("13135", {"ContentsCode": "KOSdriftinnb0000"}),
    "vei_pi": ("11816", {"ContentsCode": "KOSntodrutgveiin0000"}),
    "bvern_pi": ("12279", {"ContentsCode": "KOSndubvinnbygge0000"}),
    "eiendom_pi": ("12051", {"ContentsCode": "KOSndu421perinnb0000"}),
}
GRUPPER = {"Alle": CODES,
           "Nordland": [k for k in CODES if fylke(k) == "Nordland"],
           "Troms": [k for k in CODES if fylke(k) == "Troms"],
           "Finnmark": [k for k in CODES if fylke(k) == "Finnmark"]}


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def post(table, query):
    body = {"query": query, "response": {"format": "json-stat2"}}
    req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{table}",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def cells(d):
    ids, sizes = d["id"], d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"].keys()) for k in ids}
    st, acc = [], 1
    for s in reversed(sizes):
        st.insert(0, acc); acc *= s
    for i, v in enumerate(d["value"]):
        r, co = i, {}
        for k, s in zip(ids, st):
            co[k] = cats[k][r // s]; r %= s
        yield co, v


def hent_alle(years):
    """-> {felt: {(kommune, aar): verdi}} for alle felt, ett kall per tabell."""
    per_tab = {}
    for f, (t, sel) in FIELDS.items():
        per_tab.setdefault(t, []).append((f, sel))
    ut = {f: {} for f in FIELDS}
    for t, felt in per_tab.items():
        dims = {}
        for _, sel in felt:
            for k, v in sel.items():
                dims.setdefault(k, [])
                if v not in dims[k]:
                    dims[k].append(v)
        q = [{"code": REG, "selection": {"filter": "item", "values": CODES}}]
        q += [{"code": k, "selection": {"filter": "item", "values": v}} for k, v in dims.items()]
        q += [{"code": "Tid", "selection": {"filter": "item", "values": years}}]
        print(f"  henter {t} ({', '.join(f for f, _ in felt)})", flush=True)
        d = post(t, q)
        for co, v in cells(d):
            for f, sel in felt:
                if all(co[k] == val for k, val in sel.items()):
                    ut[f][(co[REG], co["Tid"])] = v
    return ut


def median1(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 1) if vals else None


def ts_median(raw, f, ks, y):
    """Median for tidsserie-benchmark (urundet, som i eksisterende kostra_ts)."""
    vals = [raw[f].get((k, y)) for k in ks if raw[f].get((k, y)) is not None]
    return round(statistics.median(vals), 4) if vals else None


def bygg_snapshot(raw, prioritet):
    snap, fallback = {}, {}
    for k in CODES:
        o = {}
        for f in FIELDS:
            v = None
            for y in prioritet:
                v = raw[f].get((k, y))
                if v is not None:
                    if y != prioritet[0]:
                        fallback.setdefault(k, {})[f] = y
                    break
            o[f] = v
        o["yr"] = prioritet[0]
        snap[k] = o
    bench = {}
    for g, ks in GRUPPER.items():
        b = {f: median1([snap[k][f] for k in ks]) for f in FIELDS}
        b["yr"] = prioritet[0]
        bench[g] = b
    return snap, bench, fallback


def lik(a, b):
    return a == b or (a is not None and b is not None and abs(a - b) < 1e-9)


def sammenlign(navn, ny, gammel):
    n = avv = 0
    for k in gammel:
        for f in FIELDS:
            n += 1
            if not lik(ny.get(k, {}).get(f), gammel[k].get(f)):
                avv += 1
                print(f"    {navn} {k} {f}: eksisterende {gammel[k].get(f)} | SSB naa {ny.get(k, {}).get(f)}")
    print(f"  {navn}: {n - avv}/{n} celler identiske")
    return avv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", metavar="AAR", help="bygg for AAR og sammenlign uten aa skrive")
    a = ap.parse_args()

    meta = get("https://data.ssb.no/api/v0/no/table/12143")
    years = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
    print(f"KOSTRA-aar tilgjengelig: {years[0]}-{years[-1]}", flush=True)
    raw = hent_alle(years)

    D = load_data()
    P = D["proj"]
    if a.verify:
        y = a.verify
        print(f"\nVerifikasjon {y} (kun aar {y}, ingen reserveaar):")
        snap, bench, _ = bygg_snapshot(raw, [y])
        sammenlign("kommune", snap, P["kostra"])
        # benchmark fra eksisterende snapshot (tester median-logikken isolert)
        b_old = {g: {f: median1([P["kostra"][k][f] for k in ks]) for f in FIELDS}
                 for g, ks in GRUPPER.items()}
        sammenlign("bench (median av eksisterende snapshot)", b_old, P["kostra_bench"])
        # tidsserien: celle for celle mot SSB naa, per aar
        ts = P["kostra_ts"]
        print("\nkostra_ts mot SSB naa (avvik per aar, kommuneceller):")
        for i, yy in enumerate(str(x) for x in ts["years"]):
            avv = [(k, f, s[i], raw[f].get((k, yy))) for k, ser in ts["kommuner"].items()
                   for f, s in ser.items() if not lik(s[i], raw[f].get((k, yy)))]
            bavv = [(g, f, s[i], ts_median(raw, f, GRUPPER[g], yy)) for g, ser in ts["bench"].items()
                    for f, s in ser.items() if not lik(s[i], ts_median(raw, f, GRUPPER[g], yy))]
            print(f"  {yy}: {len(avv)} kommuneavvik, {len(bavv)} bench-avvik"
                  + (f"  eks: {avv[:3]} {bavv[:2]}" if avv or bavv else ""))
        return

    ny = years[-1]
    forrige = str(int(ny) - 1)
    snap, bench, fallback = bygg_snapshot(raw, [ny, forrige])
    mangler = {f: [k for k in CODES if snap[k][f] is None] for f in FIELDS}
    print(f"\nSnapshot {ny}: {sum(len(v) for v in fallback.values())} felt fra {forrige} "
          f"(reserve) i {len(fallback)} kommuner; manglende verdier: "
          f"{ {f: v for f, v in mangler.items() if v} }")

    # --- tidsserien: oppdater med gjeldende SSB-verdier (revisjoner + endelig nyeste aar)
    ts = P["kostra_ts"]
    ts_years = [str(y) for y in ts["years"]]
    if ts_years != years:
        print(f"ADVARSEL: kostra_ts.years {ts_years[0]}-{ts_years[-1]} != SSB {years[0]}-{years[-1]}; "
              "utvider til SSB-aarene")
        ts["years"] = [int(y) for y in years]
        ts_years = years
    endret = 0
    for k, serier in ts["kommuner"].items():
        for f, arr in serier.items():
            nyarr = [raw[f].get((k, y)) for y in ts_years]
            endret += sum(1 for x, y2 in zip(arr, nyarr) if not lik(x, y2))
            serier[f] = nyarr
    for g, serier in ts["bench"].items():
        for f in serier:
            serier[f] = [ts_median(raw, f, GRUPPER[g], y) for y in ts_years]
    print(f"kostra_ts: {endret} kommuneceller endret mot SSB naa")

    P["kostra"] = snap
    P["kostra_bench"] = bench
    P["kostra_meta"] = {
        "retrieved_at": datetime.date.today().isoformat(),
        "yr": ny, "reserveaar": forrige,
        "tabeller": sorted({t for t, _ in FIELDS.values()}),
        "felt": {f: f"{t} {'/'.join(sel.values())}" for f, (t, sel) in FIELDS.items()},
        "reserve": fallback,
        "bench": "median av de 80 kommunene (Alle) og per fylke, rundet til 1 desimal",
    }
    P["meta"]["kostra"] = (
        "KOSTRA-konserntall fra SSB (tab. 12143 finansielle nøkkeltall i % av brutto "
        "driftsinntekter; 12134 frie inntekter; 12209 helse/omsorg; 12255 grunnskole; "
        "13502 barnehage; 13135 kultur; 12025 kirke; 12051 eiendomsforvaltning; 11816 "
        f"samferdsel; 12279 barnevern). Siste år: {ny} (endelige tall, publisert 15. juni "
        f"{int(ny) + 1}); felt som mangler for {ny} hentes fra {forrige}. Referanser: TBU-norm "
        "netto driftsresultat ≈ +1,75 %; landsdels-/fylkesmedian. Demografibroen er en "
        "illustrasjon (kun aldringseffekt, alt annet likt) — ikke en budsjettprognose.")
    save_data(D)
    print(f"Skrev DATA.proj.kostra/kostra_bench/kostra_meta ({ny}) og kostra_ts.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
