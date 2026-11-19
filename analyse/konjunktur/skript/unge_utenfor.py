#!/usr/bin/env python3
"""Unge utenfor arbeid, utdanning og arbeidsmarkedstiltak (NEET), SSB 13556 → data/unge_utenfor.json.

Kontroll og oppdatering av Konjunkturbarometer for Nord-Norge 2026, s. 79–81 (15–24 år, 2015–2024).
Nord-Norge er summen av fylkeskodene som gjaldt hvert år (18, 19, 20 til 2019; 18, 54 i 2020–2023; 18, 55, 56 fra
2024). Fylkesgrensene inne i landsdelen har endret seg, men landsdelen samlet har samme kommuner hele perioden.
Kjør fra repo-roten:  python analyse/konjunktur/skript/unge_utenfor.py
"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
UT = Path(__file__).resolve().parents[1] / "data" / "unge_utenfor.json"
NN = ("18", "19", "20", "54", "55", "56")
STATUS = {"TOT": "i alt", "NEET": "utenfor", "U.03": "under utdanning", "A.01": "sysselsatte",
          "A.09": "registrerte ledige", "U.04-U.05": "AAP eller uføretrygd", "U.90B": "andre, ikke på tiltak"}
ALDER = {"15-24": ("15-19", "20-24"), "15-29": ("15-19", "20-24", "25-29")}


def main():
    p = {"lang": "no", "outputFormat": "json-stat2", "valueCodes[Region]": "0," + ",".join(NN),
         "valueCodes[Kjonn]": "0", "valueCodes[Alder]": "15-19,20-24,25-29", "valueCodes[HovArbStyrkStatus]": ",".join(STATUS),
         "valueCodes[ContentsCode]": "Bosatte", "valueCodes[Tid]": "*"}
    j = json.load(urllib.request.urlopen("https://data.ssb.no/api/pxwebapi/v2/tables/13556/data?" + urllib.parse.urlencode(p), timeout=300))
    dims, size = j["id"], j["size"]
    kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
    v = {}
    for i, x in enumerate(j["value"]):
        idx, rest = {}, i
        for d, n in zip(reversed(dims), reversed(size)):
            idx[d] = kat[d][rest % n]; rest //= n
        v[(idx["Region"], idx["Alder"], idx["HovArbStyrkStatus"], idx["Tid"])] = x or 0
    aar = kat["Tid"]
    ut = {"aar": [int(a) for a in aar], "status": STATUS, "kilde": "SSB 13556, prioritert arbeidsstyrkestatus for bosatte 15–29 år, 4. kvartal"}
    for reg, koder in (("nord-norge", NN), ("landet", ("0",))):
        ut[reg] = {al: {st: [sum(v.get((r, a, st, t), 0) for r in koder for a in ag) for t in aar] for st in STATUS} for al, ag in ALDER.items()}
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    n = ut["nord-norge"]["15-24"]
    for i, t in enumerate(aar):
        if t in ("2015", "2021", "2024", "2025"):
            print(t, "NN 15–24:", n["NEET"][i], f"{100 * n['NEET'][i] / n['TOT'][i]:.1f} %",
                  "landet", f"{100 * ut['landet']['15-24']['NEET'][i] / ut['landet']['15-24']['TOT'][i]:.1f} %")
    print("skrev", UT)


if __name__ == "__main__":
    main()
