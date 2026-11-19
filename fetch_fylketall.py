#!/usr/bin/env python3
"""«Fylket i tall»: 15 nøkkeltall for Nordland, Troms, Finnmark, Nord-Norge og landet → FYLKE_TALL i assets/data.js.

Alle tall hentes fra SSBs PxWebApi v2. Nord-Norge er summen av de tre fylkene; andeler, satser og priser regnes fra
summene (lønn veid med heltidsekvivalenter, kvadratmeterpris veid med antall omsetninger). Konjunkturbarometer for
Nord-Norge 2026 (s. 14–19) brukes bare som kontroll (KB under); avvik skrives ut og forklares i
analyse/konjunktur/notater/fylketall.md. Plan: analyse/konjunktur/PLAN-FYLKET-I-TALL.md.
Kjør:  python fetch_fylketall.py
"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
API = "https://data.ssb.no/api/pxwebapi/v2/tables/{}/data?"
FY = {"18": "Nordland", "55": "Troms", "56": "Finnmark"}
NN = lambda k: str(k)[:2] in FY and len(str(k)) == 4

# Konjunkturbarometerets fylkesfakta (s. 15, 17 og 19), bare til kontroll
KB = {"Nordland": {"syss": 67.7, "ledige": 1491, "lonn": 57580, "uh": 30.9, "vgs": 38.8, "stud": 8812, "boliger": 132814,
                   "fullf": 595, "areal": 38153, "bebygd": 1.0, "jordbruk": 1.9, "vernet": 19.8, "ndr": 1.0, "over175": 12},
      "Troms": {"syss": 70.2, "ledige": 1032, "lonn": 58180, "uh": 37.2, "vgs": 34.9, "stud": 12553, "boliger": 94660,
                "fullf": 517, "areal": 26189, "bebygd": 0.9, "jordbruk": 1.5, "vernet": 15.6, "ndr": -0.5, "over175": 3},
      "Finnmark": {"syss": 68.9, "ledige": 458, "lonn": 57310, "uh": 32.0, "vgs": 35.7, "stud": 2878, "boliger": 42158,
                   "fullf": 137, "areal": 48637, "bebygd": 0.3, "jordbruk": 0.3, "vernet": 9.4, "ndr": -0.1, "over175": 6}}


def hent(tab, filt, kodeliste=None):
    """Returnerer {(dim1, dim2, ...): verdi} i tabellens dimensjonsrekkefølge, og dimensjonsnavnene."""
    p = {"lang": "no", "outputFormat": "json-stat2", **{f"valueCodes[{k}]": v for k, v in filt.items()}}
    if kodeliste:
        p["codelist[Region]"] = kodeliste
    for forsok in range(6):   # SSB begrenser antall kall per minutt; vent og prøv igjen ved 429
        time.sleep(2)
        try:
            j = json.load(urllib.request.urlopen(API.format(tab) + urllib.parse.urlencode(p), timeout=300))
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or forsok == 5:
                raise
            time.sleep(30)
    dims, size = j["id"], j["size"]
    kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
    ut = {}
    for i, x in enumerate(j["value"]):
        idx, rest = [], i
        for d, n in zip(reversed(dims), reversed(size)):
            idx.append(kat[d][rest % n]); rest //= n
        ut[tuple(reversed(idx))] = x
    return ut, dims


def per_region(data, dims, regdim="Region", omkod=None, summer_over=None):
    """Summerer verdiene per region (eventuelt etter én ekstra dimensjon)."""
    ri = dims.index(regdim)
    si = dims.index(summer_over) if summer_over else None
    ut = defaultdict(float)
    for k, v in data.items():
        if v is None:
            continue
        r = k[ri]
        r = omkod.get(r, r) if omkod else r
        ut[(r, k[si]) if si is not None else r] += v
    return ut


def med_nn(d):
    d = dict(d)
    d["NN"] = sum(d[f] for f in FY)
    return d


def main():
    T = {}
    agg = lambda k: k.replace("F-", "")
    # 01 Sysselsettingsgrad 15–74 år (SSB 13563, bosted)
    d, dims = hent("13563", {"Region": "F-18,F-55,F-56", "HovArbStyrkStatus": "TOT,A.01", "Alder": "15-74", "InnvandrKat": "A-G", "ContentsCode": "Bosatte", "Tid": "2025"}, "agg_KommFylker")
    d2, _ = hent("13563", {"Region": "0", "HovArbStyrkStatus": "TOT,A.01", "Alder": "15-74", "InnvandrKat": "A-G", "ContentsCode": "Bosatte", "Tid": "2025"})
    s = per_region({**d, **d2}, dims, summer_over="HovArbStyrkStatus", omkod={f"F-{k}": k for k in FY})
    tot, sys_ = med_nn({r: s[(r, "TOT")] for r in [*FY, "0"]}), med_nn({r: s[(r, "A.01")] for r in [*FY, "0"]})
    T["syss"] = {r: round(100 * sys_[r] / tot[r], 1) for r in tot}
    # 02 Ledige stillinger, arbeidssted (SSB 14306)
    d, dims = hent("14306", {"Region": "18,55,56,0N", "NACE2007": "01-96", "ContentsCode": "LedigeStillinger", "Tid": "2026K3"})
    s = per_region(d, dims, omkod={"0N": "0"})
    T["ledige"] = {r: round(v) for r, v in med_nn(s).items()}
    # 03 Gjennomsnittlig månedslønn, arbeidssted (SSB 11422), NN veid med heltidsekvivalenter
    d, dims = hent("11422", {"Region": "18,55,56,0", "MaaleMetode": "02,11", "Yrke": "0-9", "Kjonn": "0", "ArbeidsTid": "0", "ContentsCode": "Manedslonn", "Tid": "2025"})
    s = per_region(d, dims, summer_over="MaaleMetode")
    lonn = {r: s[(r, "02")] for r in [*FY, "0"]}
    hte = {r: s[(r, "11")] for r in [*FY, "0"]}
    lonn["NN"] = sum(lonn[f] * hte[f] for f in FY) / sum(hte[f] for f in FY)
    T["lonn"] = {r: round(v) for r, v in lonn.items()}
    # 04–05 Utdanningsnivå 16 år og over (SSB 09429)
    d, dims = hent("09429", {"Region": "18,55,56", "Nivaa": "00,02a,03a,04a", "Kjonn": "0", "ContentsCode": "Personer", "Tid": "2025"}, "agg_FylkerGjeldende")
    d2, _ = hent("09429", {"Region": "0", "Nivaa": "00,02a,03a,04a", "Kjonn": "0", "ContentsCode": "Personer", "Tid": "2025"})
    s = per_region({**d, **d2}, dims, summer_over="Nivaa")
    niv = {n: med_nn({r: s[(r, n)] for r in [*FY, "0"]}) for n in ("00", "02a", "03a", "04a")}
    T["uh"] = {r: round(100 * (niv["03a"][r] + niv["04a"][r]) / niv["00"][r], 1) for r in niv["00"]}
    T["vgs"] = {r: round(100 * niv["02a"][r] / niv["00"][r], 1) for r in niv["00"]}
    # 06 Studenter etter studiested (SSB 03814)
    d, dims = hent("03814", {"Region": "18,55,56", "Kjonn": "0", "ContentsCode": "Studenter", "Tid": "2025"}, "agg_FylkerGjeldende")
    d2, _ = hent("03814", {"Region": "0", "Kjonn": "0", "ContentsCode": "Studenter", "Tid": "2025"})
    T["stud"] = {r: round(v) for r, v in med_nn(per_region({**d, **d2}, dims)).items()}
    # 07 Boliger i alt (SSB 06265) og 08 fullførte boliger (SSB 05940)
    om = {f"F-{k}": k for k in FY}
    d, dims = hent("06265", {"Region": "F-18,F-55,F-56", "BygnType": "*", "ContentsCode": "Boliger", "Tid": "2026"}, "agg_KommFylker")
    d2, _ = hent("06265", {"Region": "0", "BygnType": "*", "ContentsCode": "Boliger", "Tid": "2026"})
    T["boliger"] = {r: round(v) for r, v in med_nn(per_region({**d, **d2}, dims, omkod=om)).items()}
    d, dims = hent("05940", {"Region": "F-18,F-55,F-56", "Byggeareal": "*", "ContentsCode": "Fullforte", "Tid": "2025"}, "agg_KommFylker")
    d2, _ = hent("05940", {"Region": "0", "Byggeareal": "*", "ContentsCode": "Fullforte", "Tid": "2025"})
    T["fullf"] = {r: round(v) for r, v in med_nn(per_region({**d, **d2}, dims, omkod=om)).items()}
    # 09 Kvadratmeterpris brukte boliger, siste fire kvartaler veid med omsetninger (SSB 14310)
    kv = ["2025K4", "2026K1", "2026K2", "2026K3"]
    d, dims = hent("14310", {"Region": "18,55,56,0", "Boligtype": "00", "ContentsCode": "KvPris,Omsetninger", "Tid": ",".join(kv)})
    ri, ci = dims.index("Region"), dims.index("ContentsCode"); ti = dims.index("Tid")
    pris = defaultdict(float); oms = defaultdict(float)
    for k, v in d.items():
        if k[ci] == "KvPris" and v is not None:
            o = d[tuple(("Omsetninger" if j == ci else x) for j, x in enumerate(k))] or 0
            pris[k[ri]] += v * o; oms[k[ri]] += o
    pris = med_nn(pris); oms = med_nn(oms)
    T["kvpris"] = {r: round(pris[r] / oms[r]) for r in pris}
    T["omsetninger"] = {r: round(v) for r, v in oms.items()}
    # 10–11 Areal (SSB 09594): land og ferskvann = alle hovedklasser utenom sjø (23); bebygd = 01–14; jordbruk = 15–16
    klasser = ["01", "02", "03", "04", "05", "06", "07", "08-09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "24"]
    d, dims = hent("09594", {"Region": "F-18,F-55,F-56", "ArealKlasse": ",".join(klasser), "ContentsCode": "Areal", "Tid": "2026"}, "agg_KommFylker")
    d2, _ = hent("09594", {"Region": "0", "ArealKlasse": ",".join(klasser), "ContentsCode": "Areal", "Tid": "2026"})
    s = per_region({**d, **d2}, dims, omkod=om, summer_over="ArealKlasse")
    reg = [*FY, "0"]
    a_tot = med_nn({r: sum(s[(r, k)] for k in klasser) for r in reg})
    a_beb = med_nn({r: sum(s[(r, k)] for k in klasser[:13]) for r in reg})
    a_jb = med_nn({r: s[(r, "15")] + s[(r, "16")] for r in reg})
    T["areal"] = {r: round(v) for r, v in a_tot.items()}
    T["bebygd"] = {r: round(100 * a_beb[r] / a_tot[r], 1) for r in a_tot}
    T["jordbruk"] = {r: round(100 * a_jb[r] / a_tot[r], 1) for r in a_tot}
    # 12 Vernet areal på land i prosent av land og ferskvann (SSB 08936)
    d, dims = hent("08936", {"Region": "18,55,56", "VerneOmrader": "0", "ContentsCode": "VernetAreal", "Tid": "2025"}, "agg_FylkerGjeldende")
    d2, _ = hent("08936", {"Region": "0", "VerneOmrader": "0", "ContentsCode": "VernetAreal", "Tid": "2025"})
    d3, _ = hent("08936", {"Region": "21", "VerneOmrader": "0", "ContentsCode": "VernetAreal", "Tid": "2025"}, "agg_FylkerGjeldende")
    vern = med_nn(per_region({**d, **d2}, dims))
    vern["0"] -= sum(v for v in d3.values() if v)   # landstallet i 08936 omfatter Svalbard; arealet i 09594 gjør det ikke
    T["vernet"] = {r: round(100 * vern[r] / a_tot[r], 1) for r in vern}
    # 13–15 Kommuneøkonomi (SSB 13544, konsolidert kommuneregnskap 2025), summert over kommunene
    d, dims = hent("13544", {"KOKkommuneregion0000": "*", "KOKartkap0000": "AGD13,AGD23,AGI1", "KOKregnskapsomfa0000": "C", "ContentsCode": "KOSbelop0000", "Tid": "2025"})
    ki, ai = dims.index("KOKkommuneregion0000"), dims.index("KOKartkap0000")
    kom = defaultdict(dict)
    for k, v in d.items():
        if v is not None and k[ki].isdigit() and len(k[ki]) == 4 and k[ki] not in ("0000", "9999"):
            kom[k[ki]][k[ai]] = v
    kom = {k: v for k, v in kom.items() if "AGD13" in v and v["AGD13"]}
    sumr = lambda filt, art: sum(v.get(art, 0) for k, v in kom.items() if filt(k))
    flt = {**{f: (lambda f: lambda k: k[:2] == f)(f) for f in FY}, "NN": NN, "0": lambda k: True}
    # Netto driftsresultat for kommunekonsern (SSB 12134), slik TBU-normen måles; Nord-Norge veid med brutto driftsinntekter
    d, dims = hent("12134", {"KOKkommuneregion0000": "*", "ContentsCode": "KOSAGD230000", "Tid": "2025"})
    ndr_k = {k[dims.index("KOKkommuneregion0000")]: v for k, v in d.items() if v is not None}
    ndr = {f: ndr_k[f"EKA{f}"] for f in FY}
    ndr["0"] = ndr_k["EAK"]
    ndr["NN"] = sum(ndr[f] * sumr(flt[f], "AGD13") for f in FY) / sum(sumr(flt[f], "AGD13") for f in FY)
    T["ndr"] = {r: round(v, 1) for r, v in ndr.items()}
    T["inv"] = {r: round(sumr(fn, "AGI1") / 1e6, 1) for r, fn in flt.items()}   # milliarder kroner (beløp i 1 000 kr)
    T["inv_pst"] = {r: round(100 * sumr(fn, "AGI1") / sumr(fn, "AGD13"), 1) for r, fn in flt.items()}
    kk = {k: v for k, v in ndr_k.items() if k.isdigit() and len(k) == 4 and not k.startswith("21")}   # uten Svalbard
    over = lambda fn: [k for k, v in kk.items() if fn(k) and v >= 1.75]
    positiv = lambda fn: [k for k, v in kk.items() if fn(k) and v > 0]
    T["over175"] = {r: len(over(fn)) for r, fn in flt.items()}
    T["positiv"] = {r: len(positiv(fn)) for r, fn in flt.items()}
    T["antall_kommuner"] = {r: sum(1 for k in kk if fn(k)) for r, fn in flt.items()}
    # Kommuner uten konsolidert regnskap for 2025 hos SSB (per november 2026: Evenes og Gamvik) telles ikke med
    navn_k = dict(re.findall(r'"(\d{4})":\{"navn":"([^"]+)"', DATA_JS.read_text(encoding="utf-8")))
    T["mangler_regnskap"] = {"NN": sorted(navn_k[k].split(" - ")[0] for k in navn_k if NN(k) and k not in kom)}   # gjelder investeringsutgiftene (13544)
    print("Kommuner med regnskap 2025:", T["antall_kommuner"], "mangler i NN:", T["mangler_regnskap"]["NN"])

    # Kontroll mot konjunkturbarometeret
    navn = {v: k for k, v in FY.items()}
    print(f"{'indikator':12} {'fylke':9} {'SSB':>10} {'KB':>10}  avvik")
    for fy, kb in KB.items():
        for ind, kv in kb.items():
            v = T[ind][navn[fy]]
            av = v - kv
            flagg = "  <-- " if (abs(av) > 1 if isinstance(kv, float) and kv < 100 else abs(av) > 0.01 * abs(kv)) else ""
            print(f"{ind:12} {fy:9} {v:>10} {kv:>10}  {av:+.1f}{flagg}")

    mangler = T.pop("mangler_regnskap")["NN"]
    ut = {"hentet": "2026-11-19", "mangler_regnskap": mangler, "verdier": {k: {("landet" if r == "0" else ("nord-norge" if r == "NN" else FY[r])): v for r, v in d.items()} for k, d in T.items()},
          "aar": {"syss": "2025", "ledige": "3. kvartal 2026", "lonn": "2025", "uh": "2025", "vgs": "2025", "stud": "2025", "boliger": "1.1.2026",
                  "fullf": "2025", "kvpris": "4. kvartal 2025–3. kvartal 2026", "areal": "2026", "bebygd": "2026", "jordbruk": "2026", "vernet": "2025",
                  "ndr": "2025", "over175": "2025", "inv": "2025"},
          "kb": KB}
    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const FYLKE_TALL = " + json.dumps(ut, ensure_ascii=False, separators=(",", ":")) + ";"
    block = f"/* FYLKE_TALL BEGIN */\n{lit}\n/* FYLKE_TALL END */"
    if "/* FYLKE_TALL BEGIN */" in js:
        js = re.sub(r"/\* FYLKE_TALL BEGIN \*/.*?/\* FYLKE_TALL END \*/", lambda _m: block, js, flags=re.DOTALL)
    elif "/* KONJ_DATA END */" in js:
        js = js.replace("/* KONJ_DATA END */", "/* KONJ_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret KONJ_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injected FYLKE_TALL ({len(lit)} tegn)")


if __name__ == "__main__":
    main()
