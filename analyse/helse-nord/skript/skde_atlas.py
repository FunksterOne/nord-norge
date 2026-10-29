"""Henter SKDEs helseatlas-analyser (åpent REST-API til analyser.skde.no, Payload CMS) og lager
data/skde_atlas_rater.csv (alle år, region- og opptaksområdenivå, «total»-visningen) og
data/skde_atlas_nord.csv (siste år, Helse Nord-HF-ene mot landet).

API: https://analyser.skde.no/api/analyser?limit=200&depth=0  (publiserte analyser, ingen innlogging)
Kjør: python -X utf8 skde_atlas.py
"""
import csv, json, os, re
from ssb import RAA, UT, hent

URL = "https://analyser.skde.no/api/analyser?limit=200&depth=0"
d = json.loads(hent(URL, "skde_analyser.json"))
NORD = {"UNN": "UNN", "Nordland": "Nordlandssykehuset", "Helgeland": "Helgelandssykehuset", "Finnmark": "Finnmarkssykehuset"}


def tekst(rt):
    """Flater ut Payload/Lexical-rikttekst til ren tekst."""
    ut = []

    def gå(n):
        if isinstance(n, dict):
            if n.get("type") == "text":
                ut.append(n.get("text", ""))
            for v in n.values():
                if isinstance(v, (dict, list)):
                    gå(v)
            if n.get("type") in ("paragraph", "heading", "listitem"):
                ut.append("\n")
        elif isinstance(n, list):
            for v in n:
                gå(v)
    gå(rt)
    return re.sub(r"\n+", " / ", "".join(ut)).strip(" /")


rader, nord, meta = [], [], []
for x in d["docs"]:
    D = x["data"]
    tot = D["data"]["total"]
    var = D["views"][0]["variables"][0]["name"]
    aggr = D["views"][0].get("aggregering", "")
    meta.append({"id": x["id"], "slug": x["slug"], "tittel": x["title"], "status": x.get("publiseringsStatus"),
                 "kjonn": D.get("kjonn"), "alder": D.get("age_range"), "aar": [min(tot), max(tot)],
                 "aggregering": aggr, "om": tekst(x.get("about"))[:1500], "oppsummering": tekst(x.get("summary"))[:1500]})
    for aar, niv in tot.items():
        for nivå, omr in niv.items():
            for o, vv in omr.items():
                v = vv.get(var, {})
                for mål, verdi in v.items():
                    rader.append({"slug": x["slug"], "tittel": x["title"], "status": x.get("publiseringsStatus"),
                                  "aar": aar, "niva": nivå, "omraade": o, "mal": mål, "verdi": verdi})
    siste = max(tot)
    sy = tot[siste]["sykehus"]
    rate = [k for k in sy.get("Norge", {}).get(var, {}) if k.endswith("_rate")]
    if not rate:
        continue
    r = rate[0]
    norge = sy["Norge"][var][r]
    alle = sorted((v[var][r], k) for k, v in sy.items() if k != "Norge" and r in v.get(var, {}))
    rang = {k: i + 1 for i, (_, k) in enumerate(sorted(alle, reverse=True))}
    for k, navn in NORD.items():
        if k in sy:
            nord.append({"slug": x["slug"], "tittel": x["title"], "status": x.get("publiseringsStatus"), "aar": siste,
                         "mal": r, "hf": navn, "rate": sy[k][var][r], "rate_norge": norge,
                         "forhold_til_norge": round(sy[k][var][r] / norge, 2) if norge else None,
                         "rang_av": f"{rang[k]} av {len(alle)}",
                         "helse_nord_rate": tot[siste]["region"].get("Helse_Nord", {}).get(var, {}).get(r)})

with open(os.path.join(UT, "skde_atlas_rater.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rader[0]))
    w.writeheader(); w.writerows(rader)
with open(os.path.join(UT, "skde_atlas_nord.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(nord[0]))
    w.writeheader(); w.writerows(nord)
json.dump(meta, open(os.path.join(RAA, "skde_analyser_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rader), "rader,", len(nord), "Nord-rader,", len(meta), "analyser")
# Største avvik for Helse Nord-regionen
reg = {}
for n in nord:
    reg.setdefault(n["slug"], n)
for slug, n in sorted(reg.items(), key=lambda kv: -abs((kv[1]["helse_nord_rate"] or 0) / kv[1]["rate_norge"] - 1)):
    hn = n["helse_nord_rate"]
    print(f'{n["tittel"][:45]:45s} {n["status"]:9s} {n["aar"]} HN/Norge {hn / n["rate_norge"]:.2f}  '
          + "  ".join(f'{m["hf"][:6]} {m["forhold_til_norge"]}' for m in nord if m["slug"] == slug))
