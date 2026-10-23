"""Befolkningsregnskap per år 2006-2025 for Nord-Norge (SSB 01222, fylker 2024 sammenslåtte serier)."""
import json, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
KV = [f"{a}K{q}" for a in range(2006, 2026) for q in range(1, 5)]
K = ["Fodselsoverskudd4", "Innvandring5", "Utvandring6", "Tilflytting7", "Fraflytting8", "Folketilvekst10"]
p = {"lang": "no", "outputFormat": "json-stat2", "codelist[Region]": "agg_KommFylker",
     "valueCodes[Region]": "F-18,F-55,F-56", "valueCodes[Tid]": ",".join(KV), "valueCodes[ContentsCode]": ",".join(K)}
d = json.load(urllib.request.urlopen("https://data.ssb.no/api/pxwebapi/v2/tables/01222/data?" + urllib.parse.urlencode(p), timeout=120))
ids = d["id"]
keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
ut = {}
for n, v in enumerate(d["value"]):
    rest, co = n, {}
    for i in range(len(ids) - 1, -1, -1):
        co[ids[i]] = keys[i][rest % d["size"][i]]; rest //= d["size"][i]
    a = co["Tid"][:4]
    ut.setdefault(a, {k: 0 for k in K})[co["ContentsCode"]] += v or 0
json.dump(ut, open(sys.argv[1], "w"), indent=0)
print("år  fødselsoversk  netto innv  netto innenl  vekst")
s = {k: 0 for k in K}
for a in sorted(ut):
    u = ut[a]
    for k in K: s[k] += u[k]
    print(a, u["Fodselsoverskudd4"], u["Innvandring5"] - u["Utvandring6"], u["Tilflytting7"] - u["Fraflytting8"], u["Folketilvekst10"])
print("SUM", s["Fodselsoverskudd4"], s["Innvandring5"] - s["Utvandring6"], s["Tilflytting7"] - s["Fraflytting8"], s["Folketilvekst10"])
