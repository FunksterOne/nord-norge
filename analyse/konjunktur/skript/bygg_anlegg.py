#!/usr/bin/env python3
"""Sysselsatte i bygg og anlegg etter arbeidssted, SSB 13470 (4. kvartal, 15–74 år) → data/bygg_anlegg.json.

Kontroll av Konjunkturbarometer for Nord-Norge 2026, s. 46–47. Byggnæring = SN2007 41 og 43 utenom 43.1;
anlegg = 42 og 43.1 (riving og grunnarbeid). Med denne inndelingen treffer indeksene 2008–2025 rapportens figur
innenfor ett indekspoeng; med 43 i sin helhet under bygg gjør de det ikke.
Kjør fra repo-roten:  python analyse/konjunktur/skript/bygg_anlegg.py
"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
UT = Path(__file__).resolve().parents[1] / "data" / "bygg_anlegg.json"
# Fylkene hentes som SSBs sammenslåtte tidsserier (agg_KommFylker), fordi kodene 55 og 56 bare finnes fra 2024
REG = {"F-18": "Nordland", "F-55": "Troms", "F-56": "Finnmark", "0": "Landet"}
NACE = ["41", "42", "43", "43.1"]


def hent(koder, kodeliste=None):
    p = {"lang": "no", "outputFormat": "json-stat2", "valueCodes[Region]": ",".join(koder), "valueCodes[NACE2007]": ",".join(NACE),
         "valueCodes[ContentsCode]": "SysselsatteArb", "valueCodes[Tid]": "*"}
    if kodeliste:
        p["codelist[Region]"] = kodeliste
    url = "https://data.ssb.no/api/pxwebapi/v2/tables/13470/data?" + urllib.parse.urlencode(p)
    j = json.load(urllib.request.urlopen(url, timeout=300))
    dims = j["id"]; kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
    storr = j["size"]; ut = {}
    for i, x in enumerate(j["value"]):
        idx, rest = {}, i
        for d, n in zip(reversed(dims), reversed(storr)):
            idx[d] = kat[d][rest % n]; rest //= n
        ut[(idx["Region"], idx["NACE2007"], idx["Tid"])] = x
    return ut, kat["Tid"]


def main():
    v, aar = hent([k for k in REG if k.startswith("F-")], "agg_KommFylker")
    v2, _ = hent(["0"])
    v.update(v2)
    serie = {}
    for r, navn in REG.items():
        g = lambda n, a: v[(r, n, a)] or 0
        bygg = [g("41", a) + g("43", a) - g("43.1", a) for a in aar]
        anl = [g("42", a) + g("43.1", a) for a in aar]
        serie[navn] = {"bygg": bygg, "anlegg": anl}
    nn = {k: [sum(serie[f][k][i] for f in ("Nordland", "Troms", "Finnmark")) for i in range(len(aar))] for k in ("bygg", "anlegg")}
    serie["Nord-Norge"] = nn
    serie["Resten av landet"] = {k: [serie["Landet"][k][i] - nn[k][i] for i in range(len(aar))] for k in ("bygg", "anlegg")}
    ut = {"aar": [int(a) for a in aar], "serie": serie,
          "kilde": "SSB 13470, sysselsatte 15–74 år etter arbeidssted, 4. kvartal. Byggnæring = SN2007 41 og 43 utenom 43.1, anlegg = 42 og 43.1"}
    UT.parent.mkdir(parents=True, exist_ok=True)
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    i22, i25 = ut["aar"].index(2022), ut["aar"].index(2025)
    for navn, s in serie.items():
        tot = [b + a for b, a in zip(s["bygg"], s["anlegg"])]
        print(f"{navn:17} 2022 {tot[i22]:>7} 2025 {tot[i25]:>7} endring {tot[i25] - tot[i22]:>6} ({100 * (tot[i25] / tot[i22] - 1):.1f} %)",
              f"bygg {100 * (s['bygg'][i25] / s['bygg'][i22] - 1):.1f} % anlegg {100 * (s['anlegg'][i25] / s['anlegg'][i22] - 1):.1f} %")
    print("skrev", UT)


if __name__ == "__main__":
    main()
