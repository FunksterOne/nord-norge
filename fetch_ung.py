#!/usr/bin/env python3
"""Unge voksne og eldre per kommune, og fødte og døde i landsdelen → UNG_DATA i assets/data.js.

  18–34 år og 67 år og over, 1. januar:
    faktisk 2020–siste år: SSB 07459 (2024-inndeling via kodelisten agg_KommSummer)
    framskrevet etterpå:   SSB 14746, hovedalternativet (MMMM)
  Krysningsår: første år 67+ er flere enn 18–34. «før 2020» når det allerede gjaldt i 2020, null når det ikke skjer innen 2050.
  Levendefødte og døde 1995–siste år: SSB 06913 (fylkessummer; fylkeskodene følger reformene 2020 og 2024).
  Barometer 2026X (Kunnskapsbanken, SpareBank 1 Nord-Norge / Sentio Research): tall lagt inn manuelt fra rapporten,
  med sidehenvisning, i barometer_ung.json.

Historikken starter i 2020 fordi kodelisten mangler Narvik og Hamarøy før kommunesammenslåingen det året.
Kjør:  python fetch_ung.py
"""
import json
import re
import sys
from pathlib import Path

import fetch_pyramide as FP

HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
BAROMETER = HER / "analyse" / "ung" / "barometer_ung.json"
START, SLUTT = 2020, 2050


def fylke(nr):
    return "Nordland" if nr.startswith("18") else ("Troms" if nr.startswith("55") else "Finnmark")


def hent_fodte():
    """Levendefødte og døde for landsdelen og hele landet, 1995–siste år (SSB 06913)."""
    meta = FP.hent_json("https://data.ssb.no/api/v0/no/table/06913")
    tid = [t for t in next(v for v in meta["variables"] if v["code"] == "Tid")["values"] if int(t) >= 1995]
    regioner = ["0", "18", "19", "20", "54", "55", "56"]
    q = {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": regioner}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Levende", "Dode"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": tid}},
    ], "response": {"format": "json-stat2"}}
    d = FP.hent_json("https://data.ssb.no/api/v0/no/table/06913", json.dumps(q).encode("utf-8"))
    v = {}
    for co, x in FP.jsonstat(d):
        v[(co["Region"], co["ContentsCode"], int(co["Tid"]))] = x
    ut = {"aar": [], "nn_fodte": [], "nn_dode": [], "land_fodte": [], "land_dode": []}
    for t in sorted({int(x) for x in tid}):
        # Fylkene i Nord-Norge etter inndelingen som gjaldt det året
        nn = ["18", "19", "20"] if t < 2020 else (["18", "54"] if t < 2024 else ["18", "55", "56"])
        f = sum(v.get((r, "Levende", t), 0) for r in nn)
        if not f:
            continue  # året er ikke publisert ennå
        ut["aar"].append(t)
        ut["nn_fodte"].append(f)
        ut["nn_dode"].append(sum(v.get((r, "Dode", t), 0) for r in nn))
        ut["land_fodte"].append(v.get(("0", "Levende", t), 0))
        ut["land_dode"].append(v.get(("0", "Dode", t), 0))
    return ut


def main():
    kommuner, _, _ = FP.les_kommuner()
    koder = list(kommuner)
    meta = FP.hent_json("https://data.ssb.no/api/v0/no/table/07459")
    siste = int(next(v for v in meta["variables"] if v["code"] == "Tid")["values"][-1])
    hist = FP.hent_historikk(koder, [str(a) for a in range(START, siste + 1)])
    fram, _ = FP.hent_framskriving(koder, [str(a) for a in range(siste + 1, SLUTT + 1)])
    aar = list(range(START, SLUTT + 1))

    def tom():
        return {"u": [0] * len(aar), "e": [0] * len(aar), "pop": [0] * len(aar)}

    per = {k: tom() for k in koder}
    for (k, t, _kj, a), v in {**hist, **fram}.items():
        if k not in per or not START <= t <= SLUTT:
            continue
        i = t - START
        per[k]["pop"][i] += v
        if 18 <= a <= 34:
            per[k]["u"][i] += v
        if a >= 67:
            per[k]["e"][i] += v

    def kryss(o):
        for i, t in enumerate(aar):
            if o["e"][i] > o["u"][i]:
                return "før 2020" if i == 0 else t
        return None

    def summer(ks):
        o = tom()
        for k in ks:
            for f in ("u", "e", "pop"):
                o[f] = [a + b for a, b in zip(o[f], per[k][f])]
        return o

    i0 = siste - START
    ut_k = {}
    for k in koder:
        o = per[k]
        ut_k[k] = {"u": o["u"], "e": o["e"], "kryss": kryss(o), "pop": o["pop"][i0]}
    fylker = {f: summer([k for k in koder if fylke(k) == f]) for f in ("Nordland", "Troms", "Finnmark")}
    nn = summer(koder)
    for o in list(fylker.values()) + [nn]:
        o["kryss"] = kryss(o)
        o["pop"] = o["pop"][i0]

    # Kontrolltall mot rapportens påstander
    idx = lambda t: t - START
    sma = [k for k in koder if ut_k[k]["pop"] < 2000]
    sma_kryss = [k for k in sma if per[k]["e"][i0] > per[k]["u"][i0]]
    kontroll = {
        "basisaar": siste,
        "u_endring_2035_pct": round((nn["u"][idx(2035)] / nn["u"][i0] - 1) * 100, 1),
        "u_endring_2050_pct": round((nn["u"][idx(2050)] / nn["u"][i0] - 1) * 100, 1),
        "u_endring_2050_antall": nn["u"][idx(2050)] - nn["u"][i0],
        "e_endring_2050_pct": round((nn["e"][idx(2050)] / nn["e"][i0] - 1) * 100, 1),
        "nn_kryss": nn["kryss"],
        "n_sma": len(sma), "n_sma_kryss": len(sma_kryss),
        "bodo_kryss": ut_k["1804"]["kryss"], "tromso_kryss": ut_k["5501"]["kryss"],
        "n_kryss_innen_2030": sum(1 for k in koder if ut_k[k]["kryss"] == "før 2020" or (isinstance(ut_k[k]["kryss"], int) and ut_k[k]["kryss"] <= 2030)),
        "n_kryss_for_2020": sum(1 for k in koder if ut_k[k]["kryss"] == "før 2020"),
        "n_aldri": sum(1 for k in koder if ut_k[k]["kryss"] is None),
    }
    fodte = hent_fodte()
    payload = {
        "aar": aar, "faktiskTil": siste,
        "kommuner": ut_k, "fylker": fylker, "landsdel": nn,
        "fodte": fodte, "kontroll": kontroll,
        "barometer": json.loads(BAROMETER.read_text(encoding="utf-8")),
        "kilde": f"SSB 07459 (1. januar {START}–{siste}), 14746 hovedalternativet ({siste + 1}–{SLUTT}) og 06913 (fødte og døde)",
    }
    print(json.dumps(kontroll, ensure_ascii=False, indent=1))
    fa = fodte["aar"]
    for t in (1995, 2015, 2024, fa[-1]):
        if t in fa:
            i = fa.index(t)
            print(t, "NN fødte", fodte["nn_fodte"][i], "døde", fodte["nn_dode"][i], "| landet fødte", fodte["land_fodte"][i], "døde", fodte["land_dode"][i])

    html = DATA_JS.read_text(encoding="utf-8")
    js_lit = "const UNG_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* UNG_DATA BEGIN */", "/* UNG_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in html:
        new = re.sub(r"/\* UNG_DATA BEGIN \*/.*?/\* UNG_DATA END \*/", lambda _m: block, html, flags=re.DOTALL)
    elif "/* PENSJON_DATA END */" in html:
        new = html.replace("/* PENSJON_DATA END */", "/* PENSJON_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret PENSJON_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    print(f"Injected UNG_DATA ({len(js_lit)} tegn)")


if __name__ == "__main__":
    main()
