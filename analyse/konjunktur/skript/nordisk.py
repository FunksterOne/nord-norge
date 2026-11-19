#!/usr/bin/env python3
"""Befolkningsframskriving 2026–2035 for nordlige regioner i Norge, Sverige og Finland → data/nordisk_framskriving.json.

Kontroll og utvidelse av Konjunkturbarometer for Nord-Norge 2026, s. 31–32 (figuren «Befolkningsframskriving
(hovedalternativet), 2026–2035»). Rapporten viser bare figuren; tallene her er hentet fra byråene:
  - SSB 14746, hovedalternativet (MMMM), folkemengde 1. januar 2026 og 2035.
  - SCB BefProgRegFakN (Befolkningsframskrivning 2025, län), folkmängd 31. december 2025 og 2034.
  - Statistics Finland 14wx (Väestöennuste 2024, kommuner summert til maakunta), population 31 Dec 2025 and 2034.
31. desember år t regnes som 1. januar år t + 1, slik at alle tre dekker 2026–2035.
Kjør fra repo-roten:  python analyse/konjunktur/skript/nordisk.py
"""
import json, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
UT = Path(__file__).resolve().parents[1] / "data" / "nordisk_framskriving.json"
GRUPPER = {"0–19": (0, 19), "20–66": (20, 66), "67+": (67, 200)}


def gruppe(alder):
    for g, (a, b) in GRUPPER.items():
        if a <= alder <= b:
            return g


def post(url, q):
    time.sleep(1)
    req = urllib.request.Request(url, data=json.dumps(q).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def jsonstat(j, regdim, alderdim, tiddim, alder_til_int):
    dims, size = j["id"], j["size"]
    kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
    ut = defaultdict(float)
    for i, x in enumerate(j["value"]):
        if not x:
            continue
        idx, rest = {}, i
        for d, n in zip(reversed(dims), reversed(size)):
            idx[d] = kat[d][rest % n]; rest //= n
        a = alder_til_int(idx[alderdim])
        if a is None:
            continue
        ut[(idx[regdim], gruppe(a), idx[tiddim])] += x
    return ut


def norge():
    p = {"lang": "no", "outputFormat": "json-stat2", "valueCodes[Region]": "18,55,56,0",
         "valueCodes[Kjonn]": "*", "valueCodes[Alder]": "*", "valueCodes[ContentsCode]": "Personer", "valueCodes[Tid]": "2026,2035"}
    j = json.load(urllib.request.urlopen("https://data.ssb.no/api/pxwebapi/v2/tables/14746/data?" + urllib.parse.urlencode(p), timeout=300))
    v = jsonstat(j, "Region", "Alder", "Tid", lambda a: int(a.rstrip("+")))
    navn = {"18": "Nordland", "55": "Troms", "56": "Finnmark", "0": "Norge"}
    return {navn[r]: {g: [v[(r, g, "2026")], v[(r, g, "2035")]] for g in GRUPPER} for r in navn}


def sverige():
    q = {"query": [{"code": "Region", "selection": {"filter": "item", "values": ["01", "03", "04", "05", "06", "07", "08", "09", "10", "12", "13", "14", "17", "18", "19", "20", "21", "22", "23", "24", "25"]}},
                   {"code": "InrikesUtrikes", "selection": {"filter": "item", "values": ["83"]}},
                   {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                   {"code": "Alder", "selection": {"filter": "all", "values": ["*"]}},
                   {"code": "Tid", "selection": {"filter": "item", "values": ["2025", "2034"]}}],
         "response": {"format": "json-stat2"}}
    j = post("https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0401/BE0401A/BefProgRegFakN", q)
    v = jsonstat(j, "Region", "Alder", "Tid", lambda a: int(a.rstrip("+")))
    ut = {"Västerbotten": "24", "Norrbotten": "25"}
    res = {n: {g: [v[(k, g, "2025")], v[(k, g, "2034")]] for g in GRUPPER} for n, k in ut.items()}
    res["Sverige"] = {g: [sum(x for (r, gg, t), x in v.items() if gg == g and t == "2025"),
                          sum(x for (r, gg, t), x in v.items() if gg == g and t == "2034")] for g in GRUPPER}
    return res


def finland():
    # Tabellen har bare kommuner og hele landet; kommunene summeres til maakunta med Statistics Finlands klassifikasjonsnøkkel
    u = "https://data.stat.fi/api/classifications/v2/correspondenceTables/kunta_1_20240101%23maakunta_1_20240101/maps?content=data&meta=max&lang=fi"
    nokkel = json.load(urllib.request.urlopen(u, timeout=120))
    mk = {"KU" + x["sourceItem"]["code"]: x["targetItem"]["code"] for x in nokkel}
    navn = {"17": "Nord-Österbotten", "18": "Kainuu", "19": "Lappland"}
    koder = [k for k, m in mk.items() if m in navn]
    q = {"query": [{"code": "alue_23_20240101", "selection": {"filter": "item", "values": ["SSS"] + koder}},
                   {"code": "sukupuoli_9_20180101", "selection": {"filter": "item", "values": ["SSS"]}},
                   {"code": "ikaryhma_10_20180101", "selection": {"filter": "all", "values": ["*"]}},
                   {"code": "timeperiod_y", "selection": {"filter": "item", "values": ["2025", "2034"]}}],
         "response": {"format": "json-stat2"}}
    j = post("https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/vaenn/14wx.px", q)
    v = jsonstat(j, "alue_23_20240101", "ikaryhma_10_20180101", "timeperiod_y", lambda a: None if a == "SSS" else int(a.rstrip("-+")))
    res = {}
    for m, n in navn.items():
        res[n] = {g: [sum(x for (r, gg, t), x in v.items() if mk.get(r) == m and gg == g and t == aar) for aar in ("2025", "2034")] for g in GRUPPER}
    res["Finland"] = {g: [v[("SSS", g, "2025")], v[("SSS", g, "2034")]] for g in GRUPPER}
    return res


def main():
    land = {"Norge": norge(), "Sverige": sverige(), "Finland": finland()}
    rader = []
    for l, regioner in land.items():
        for navn, g in regioner.items():
            tot = [sum(g[x][i] for x in GRUPPER) for i in (0, 1)]
            rader.append({"land": l, "region": navn, "nasjon": navn == l,
                          "endring": {**{x: round(100 * (g[x][1] / g[x][0] - 1), 1) for x in GRUPPER}, "Totalt": round(100 * (tot[1] / tot[0] - 1), 1)},
                          "start": {x: round(g[x][0]) for x in GRUPPER}})
    ut = {"periode": "2026–2035", "rader": rader,
          "kilde": "SSB 14746 (hovedalternativet, 1.1.2026–1.1.2035), SCB BefProgRegFakN (31.12.2025–31.12.2034) og Statistics Finland 14wx (projeksjon 2024, 31.12.2025–31.12.2034)"}
    UT.parent.mkdir(parents=True, exist_ok=True)
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rader:
        print(f"{r['region']:18} " + "  ".join(f"{k} {v:+.1f}" for k, v in r["endring"].items()))
    print("skrev", UT)


if __name__ == "__main__":
    main()
