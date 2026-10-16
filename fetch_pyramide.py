#!/usr/bin/env python3
"""Henter befolkning etter kjønn og ettårig alder fra SSB og skriver befolkningspyramider
i femårsgrupper til data/pyramide/<id>.json (lastes ved behov av diagrammet «pyramide»).

  Faktisk 2000–siste år: SSB 07459 (1. januar), kodeliste agg_KommSummer = 2024-inndeling
  Framskrevet etterpå:   SSB 14746, hovedalternativet (MMMM)

Enheter: 80 kommuner, de tre fylkene, SØAs 13 regioner og hele landsdelen («nn»).
Format per fil: {"navn", "aar":[...], "faktiskTil", "grupper":[...], "m":[[...]], "k":[[...]]}
der m[i][g] og k[i][g] er menn og kvinner i aldersgruppe g i år aar[i].

Kjør:  python fetch_pyramide.py
"""
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"
UT = HERE / "data" / "pyramide"
START = 2000
SLUTT = 2050
GRUPPER = [f"{a}–{a + 4}" for a in range(0, 90, 5)] + ["90+"]
NG = len(GRUPPER)


def gruppe(alder):
    return min(alder // 5, NG - 1)


def hent_json(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode("utf-8"))


def jsonstat(d):
    """Gir (dimensjonskoder, iterator over (koordinater, verdi))."""
    dims, size = d["id"], d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"].keys()) for k in dims}
    vals = d["value"]
    if isinstance(vals, dict):
        vals = [vals.get(str(i)) for i in range(eval("*".join(map(str, size))))]
    for flat, v in enumerate(vals):
        rest, co = flat, {}
        for i in range(len(dims) - 1, -1, -1):
            co[dims[i]] = cats[dims[i]][rest % size[i]]
            rest //= size[i]
        yield co, v or 0


def alder_tall(kode):
    return int(re.sub(r"\D", "", kode) or 0)


def les_kommuner():
    js = DATA_JS.read_text(encoding="utf-8")
    linje = js.split("\n")[5]
    nr = [k for k in dict.fromkeys(re.findall(r'"(\d{4})":\{"navn":"([^"]+)"', linje))]
    kommuner = {}
    for k, navn in nr:
        if k[:2] in ("18", "55", "56") and k not in kommuner:
            kommuner[k] = navn
    assert len(kommuner) == 80, f"fant {len(kommuner)} kommuner"
    blokk = js[js.index("const REGIONS"):]
    regioner = dict(re.findall(r"\{id:'([\w-]+)',\s*navn:'([^']+)'", blokk[:blokk.index("];")]))
    kb = blokk[blokk.index("const KREGION"):]
    kregion = dict(re.findall(r'"(\d{4})":"([\w-]+)"', kb[:kb.index("};")]))
    assert len(regioner) == 13 and len(kregion) == 80, (len(regioner), len(kregion))
    return kommuner, kregion, regioner


def hent_historikk(koder, aar):
    """07459 via PxWebApi v2 med 2024-inndelingen."""
    ut = {}
    for i in range(0, len(koder), 10):
        bit = koder[i:i + 10]
        q = {
            "lang": "no",
            "valueCodes[Tid]": ",".join(aar),
            "codelist[Region]": "agg_KommSummer",
            "valueCodes[Region]": ",".join("K-" + k for k in bit),
            "valueCodes[ContentsCode]": "Personer1",
            "valueCodes[Kjonn]": "1,2",
            "valueCodes[Alder]": "*",
            "outputformat": "json-stat2",
        }
        url = "https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?" + urllib.parse.urlencode(q, safe="[],*")
        d = hent_json(url)
        for co, v in jsonstat(d):
            k = co["Region"].replace("K-", "")
            ut[(k, int(co["Tid"]), co["Kjonn"], alder_tall(co["Alder"]))] = v
        print(f"  07459: {i + len(bit)}/{len(koder)} kommuner", flush=True)
    return ut


def rekonstruer_2020(hist):
    """Kodelisten agg_KommSummer mangler Narvik (1806) og Hamarøy (1875) før 2020.
    Narvik 2020 = Narvik (1805) + Ballangen (1854) + østre Tysfjord; Hamarøy 2020 = Hamarøy (1849)
    + vestre Tysfjord. Tysfjord (1850) fordeles med andelen som faktisk gikk til Narvik i 2020,
    beregnet per kjønn og femårsgruppe og brukt likt for alle år før 2020."""
    aar = [str(a) for a in range(START, 2020)]
    q = {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": ["1805", "1854", "1849", "1850"]}},
        {"code": "Kjonn", "selection": {"filter": "item", "values": ["1", "2"]}},
        {"code": "Alder", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Personer1"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": aar}},
    ], "response": {"format": "json-stat2"}}
    d = hent_json("https://data.ssb.no/api/v0/no/table/07459", json.dumps(q).encode("utf-8"))
    gml = {}
    for co, v in jsonstat(d):
        key = (co["Region"], int(co["Tid"]), co["Kjonn"], gruppe(alder_tall(co["Alder"])))
        gml[key] = gml.get(key, 0) + v

    def g2020(k, kj, g):
        return sum(v for (kk, t, kjj, a), v in hist.items() if kk == k and t == 2020 and kjj == kj and gruppe(a) == g)

    for kj in ("1", "2"):
        for g in range(NG):
            tys19 = gml.get(("1850", 2019, kj, g), 0)
            rest = g2020("1806", kj, g) - gml.get(("1805", 2019, kj, g), 0) - gml.get(("1854", 2019, kj, g), 0)
            andel = min(1, max(0, rest / tys19)) if tys19 else 0.5
            for t in range(START, 2020):
                tys = gml.get(("1850", t, kj, g), 0)
                # Lagres på første alder i gruppen; pyramiden summerer uansett per femårsgruppe.
                hist[("1806", t, kj, g * 5)] = gml.get(("1805", t, kj, g), 0) + gml.get(("1854", t, kj, g), 0) + round(tys * andel)
                hist[("1875", t, kj, g * 5)] = gml.get(("1849", t, kj, g), 0) + round(tys * (1 - andel))
    print("  Narvik og Hamarøy rekonstruert for årene før 2020", flush=True)


def hent_framskriving(koder, aar):
    """14746 hovedalternativet (MMMM) via PxWebApi v0."""
    meta = hent_json("https://data.ssb.no/api/v0/no/table/14746")
    var = {v["code"]: v for v in meta["variables"]}
    innhold = var["ContentsCode"]["values"][0]
    alder = var["Alder"]["values"]
    ut = {}
    for i in range(0, len(koder), 10):
        bit = koder[i:i + 10]
        q = {"query": [
            {"code": "Region", "selection": {"filter": "item", "values": bit}},
            {"code": "Kjonn", "selection": {"filter": "item", "values": ["1", "2"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": alder}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [innhold]}},
            {"code": "Tid", "selection": {"filter": "item", "values": aar}},
        ], "response": {"format": "json-stat2"}}
        d = hent_json("https://data.ssb.no/api/v0/no/table/14746", json.dumps(q).encode("utf-8"))
        for co, v in jsonstat(d):
            ut[(co["Region"], int(co["Tid"]), co["Kjonn"], alder_tall(co["Alder"]))] = v
        print(f"  14746: {i + len(bit)}/{len(koder)} kommuner", flush=True)
    return ut, innhold


def main():
    kommuner, kregion, regioner = les_kommuner()
    koder = list(kommuner)

    meta = hent_json("https://data.ssb.no/api/v0/no/table/07459")
    siste = int(next(v for v in meta["variables"] if v["code"] == "Tid")["values"][-1])
    hist_aar = [str(a) for a in range(START, siste + 1)]
    fram_aar = [str(a) for a in range(siste + 1, SLUTT + 1)]
    print(f"Faktisk {START}–{siste}, framskrevet {siste + 1}–{SLUTT}", flush=True)

    hist = hent_historikk(koder, hist_aar)
    rekonstruer_2020(hist)
    fram, innhold = hent_framskriving(koder, fram_aar)
    alle = {**hist, **fram}

    aar = list(range(START, SLUTT + 1))
    per_kommune = {}
    for k in koder:
        m = [[0] * NG for _ in aar]
        kv = [[0] * NG for _ in aar]
        for (kk, t, kj, a), v in alle.items():
            if kk != k:
                continue
            arr = m if kj == "1" else kv
            arr[t - START][gruppe(a)] += v
        per_kommune[k] = (m, kv)

    # Kontroll mot DATA: folketall 1.1. siste år skal stemme med summen av pyramiden
    tot = sum(sum(per_kommune[k][0][siste - START]) + sum(per_kommune[k][1][siste - START]) for k in koder)
    print(f"Kontroll: sum 80 kommuner 1.1.{siste} = {tot}", flush=True)

    def summer(ks):
        m = [[sum(per_kommune[k][0][i][g] for k in ks) for g in range(NG)] for i in range(len(aar))]
        kv = [[sum(per_kommune[k][1][i][g] for k in ks) for g in range(NG)] for i in range(len(aar))]
        return m, kv

    enheter = {k: (kommuner[k], per_kommune[k]) for k in koder}
    enheter["nn"] = ("Nord-Norge", summer(koder))
    for f, pre in (("Nordland", "18"), ("Troms", "55"), ("Finnmark", "56")):
        enheter[f.lower()] = (f, summer([k for k in koder if k.startswith(pre)]))
    for rid, navn in regioner.items():
        ks = [k for k in koder if kregion.get(k) == rid]
        enheter[f"r-{rid}"] = (navn, summer(ks))

    UT.mkdir(parents=True, exist_ok=True)
    felles = {"aar": aar, "faktiskTil": siste, "grupper": GRUPPER,
              "kilde": f"SSB 07459 (1. januar, {START}–{siste}) og 14746 hovedalternativet ({siste + 1}–{SLUTT})",
              "hentet": datetime.date.today().isoformat()}
    for eid, (navn, (m, kv)) in enheter.items():
        (UT / f"{eid}.json").write_text(json.dumps({"navn": navn, **felles, "m": m, "k": kv}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Skrev {len(enheter)} filer til {UT}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
