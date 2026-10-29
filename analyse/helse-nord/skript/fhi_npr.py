"""Henter FHI/NPR nøkkeltall for somatikk (tabell 517) fra FHI Statistikk Open API.
Bostedsregion (landet + fire helseregioner), 2017–2026, perioder jan–apr, jan–aug og hele året.
API: https://statistikk-data.fhi.no/api/open/v1/npr/Table/517/data (POST, mal fra /query)
Kjør: python -X utf8 fhi_npr.py  -> data/npr_som_nokkeltall.csv
"""
import csv, json, os, urllib.request
from ssb import RAA, UT, UA, celler, etikett

B = "https://statistikk-data.fhi.no/api/open/v1/npr/Table/517/"
q = json.loads(urllib.request.urlopen(urllib.request.Request(B + "query", headers=UA), timeout=120).read())
q["response"] = {"format": "json-stat2", "maxRowCount": 50000}
req = urllib.request.Request(B + "data", data=json.dumps(q).encode(), headers={**UA, "Content-Type": "application/json"})
raw = urllib.request.urlopen(req, timeout=300).read()
open(os.path.join(RAA, "fhi_npr_517_data.json"), "wb").write(raw)
d = json.loads(raw)
rader = [{"aar": c["AAR"], "periode": etikett(d, "PERIODE", c["PERIODE"]), "aktor": etikett(d, "AKTOR", c["AKTOR"]),
          "bosted": etikett(d, "BOSTED", c["BOSTED"]), "mal_kode": c["MEASURE_TYPE"],
          "mal": etikett(d, "MEASURE_TYPE", c["MEASURE_TYPE"]), "verdi": v}
         for c, v in celler(d) if v not in (None, "..", ":")]
with open(os.path.join(UT, "npr_som_nokkeltall.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rader[0]))
    w.writeheader(); w.writerows(rader)
print(len(rader), "rader")
for r in rader:
    if r["bosted"].endswith("Nord") and r["aktor"] == "Alle aktører" and r["mal_kode"] in ("ANT_DOGNOPP", "ANT_KONT_POL"):
        print(r["aar"], r["periode"], r["mal"], r["verdi"])
