"""Utfall 2006-2026 for Nord-Norge: befolkning 1.1., aldersgrupper (SSB 07459, fylker 2024 sammenslåtte serier)."""
import json, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

AAR = [str(a) for a in range(2006, 2027)]
ALDER = [f"{a:03d}" for a in range(0, 105)] + ["105+"]


def hent(region_codes, codelist=None):
    p = {"lang": "no", "outputFormat": "json-stat2",
         "valueCodes[Region]": ",".join(region_codes), "valueCodes[Tid]": ",".join(AAR),
         "valueCodes[Alder]": ",".join(ALDER), "valueCodes[Kjonn]": "1,2",
         "valueCodes[ContentsCode]": "Personer1"}
    if codelist:
        p["codelist[Region]"] = codelist
    url = "https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?" + urllib.parse.urlencode(p)
    d = json.load(urllib.request.urlopen(url, timeout=120))
    dims = d["id"]; size = d["size"]
    idx = {k: {c: i for c, i in d["dimension"][k]["category"]["index"].items()} for k in dims}
    ut = {}
    import itertools
    for combo in itertools.product(*[sorted(idx[k], key=idx[k].get) for k in dims]):
        pos = 0
        for k, c in zip(dims, combo):
            pos = pos * size[dims.index(k)] + idx[k][c]
        v = d["value"][pos] or 0
        co = dict(zip(dims, combo))
        a = 105 if co["Alder"] == "105+" else int(co["Alder"])
        key = (co["Region"], co["Tid"])
        ut.setdefault(key, [0] * 106)[a] += v
    return ut


nn = hent(["F-18", "F-55", "F-56"], "agg_KommFylker")
la = hent(["0"])
res = {}
for (r, t), v in list(nn.items()) + list(la.items()):
    res.setdefault(r, {})[t] = {"tot": sum(v), "u20": sum(v[:20]), "a2064": sum(v[20:65]), "a65": sum(v[65:]), "a80": sum(v[80:]), "a2039": sum(v[20:40])}
nnsum = {}
for t in AAR:
    nnsum[t] = {k: sum(res[f][t][k] for f in ["F-18", "F-55", "F-56"]) for k in res["F-18"][t]}
res["NN"] = nnsum
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
for t in ["2006", "2009", "2011", "2014", "2017", "2020", "2025", "2026"]:
    n, l = nnsum[t], res["0"][t]
    print(t, n["tot"], f"{100*n['tot']/l['tot']:.2f} %", "65+", f"{100*n['a65']/n['tot']:.1f}", "20-64", n["a2064"], "20-39", n["a2039"], "fb", f"{100*n['a65']/n['a2064']:.1f}", "landet fb", f"{100*l['a65']/l['a2064']:.1f}")
