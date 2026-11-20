#!/usr/bin/env python3
"""Skatt og kommuneøkonomi for de 80 kommunene (pakke A1 og A2 i analyse/PLAN-NARVIK-TEMAER.md).

A1 Skatteinngang per måned (SSB 07022, skatteregnskapet): «Ordinær skatt til primærkommunen»
   (skatteart 06), akkumulert i millioner kroner per måned, 2020 → siste måned. Fylker,
   Nord-Norge og landet er summen av kommunene (fylkesregionene i tabellen). Landet er summen av
   alle fylker, fordi tabellen ikke har en landsrad.
A2 Skatt og utjevning per innbygger (SSB 12137, KOSTRA, kommunekonsern), 2020–2025:
   skatt på inntekt og formue (AG12), rammetilskudd (A800), eiendomsskatt (AG10) og frie
   inntekter (AG11), i kroner per innbygger og i 1000 kr. Nord-Norge og fylkene regnes som sum av
   beløp delt på sum av innbyggere (innbyggere = beløp / beløp per innbygger). Landet og landet
   utenom Oslo er SSBs egne regioner (EAK, EAKUO).

Kommunekoder føres fram til dagens inndeling med kommunenøkkelen i fetch_nav.py (SSB Klass 131).
Fra 2020 har ingen av de 80 kommunene endret grenser, bare koder (Troms og Finnmark 2020–2023).

Skriver SKATT_DATA i assets/data.js og analyse/skatt/data/skatt.json.
Bruk: python fetch_skatt.py
"""
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
sys.path.insert(0, str(HER))
from fetch_nav import FRAM, KODER  # noqa: E402  (kommunenøkkel og de 80 kodene)

FYLKE = {"18": "Nordland", "55": "Troms", "56": "Finnmark"}
FRA_AAR = 2020


def post(tabell, query, forsok=5):
    body = json.dumps({"query": query, "response": {"format": "json-stat2"}}).encode()
    for i in range(forsok):
        try:
            req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{tabell}", data=body,
                                         headers={"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=120).read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (i + 1))
                continue
            raise
    raise RuntimeError(f"SSB {tabell}: for mange forsøk")


def meta(tabell):
    return json.loads(urllib.request.urlopen(f"https://data.ssb.no/api/v0/no/table/{tabell}", timeout=60).read().decode("utf-8"))


def celler(d):
    """json-stat2 → liste av ({dimensjon: kode}, verdi)."""
    ids = d["id"]
    dims = []
    for i in ids:
        ix = d["dimension"][i]["category"]["index"]
        dims.append(sorted(ix, key=ix.get) if isinstance(ix, dict) else ix)
    storr = d["size"]
    ut = []
    for n, v in enumerate(d["value"]):
        if v is None:
            continue
        rest, koord = n, {}
        for i in range(len(ids) - 1, -1, -1):
            koord[ids[i]] = dims[i][rest % storr[i]]
            rest //= storr[i]
        ut.append((koord, v))
    return ut


def it(kode, verdier):
    return {"code": kode, "selection": {"filter": "item", "values": verdier}}


# ------------------------------------------------------------------ A1 skatteinngang
def skatteinngang():
    m = meta("07022")
    reg = next(v for v in m["variables"] if v["code"] == "Region")
    tid = [t for t in next(v for v in m["variables"] if v["code"] == "Tid")["values"] if int(t[:4]) >= FRA_AAR]
    kommuner = [k for k in reg["values"] if len(k) == 4 and FRAM(k) in KODER]
    fylker = [k for k in reg["values"] if len(k) == 2 and k not in ("21", "23")]
    ut = {"kommuner": defaultdict(dict), "fylker": defaultdict(dict), "landet": {}}
    for bolk in (kommuner, fylker):
        d = post("07022", [it("Region", bolk), it("Skatteart", ["06"]), it("ContentsCode", ["Skatt"]), it("Tid", tid)])
        for k, v in celler(d):
            r, t = k["Region"], k["Tid"]
            if len(r) == 4:
                ut["kommuner"][FRAM(r)][t] = ut["kommuner"][FRAM(r)].get(t, 0) + v
            else:
                ut["landet"][t] = ut["landet"].get(t, 0) + v
    for k, s in ut["kommuner"].items():
        for t, v in s.items():
            fy = k[:2]
            ut["fylker"][fy][t] = ut["fylker"][fy].get(t, 0) + v
            ut["fylker"]["NN"][t] = ut["fylker"]["NN"].get(t, 0) + v
    siste = max(tid)
    return ut, siste


def til_serie(s):
    """{'2025M03': v} → {'2025': [12 akkumulerte verdier, None der måneden mangler]}"""
    aar = defaultdict(lambda: [None] * 12)
    for t, v in s.items():
        aar[t[:4]][int(t[5:]) - 1] = round(v, 2)
    return dict(sorted(aar.items()))


# ------------------------------------------------------------------ A2 KOSTRA per innbygger
ART = {"AG12": "skatt", "A800": "ramme", "AG10": "eiendom", "AG11": "frie"}


def kostra():
    m = meta("12137")
    reg = next(v for v in m["variables"] if v["code"] == "KOKkommuneregion0000")["values"]
    tid = [t for t in next(v for v in m["variables"] if v["code"] == "Tid")["values"] if int(t) >= FRA_AAR]
    kommuner = [k for k in reg if len(k) == 4 and k.isdigit() and FRAM(k) in KODER]
    ut = {"kommuner": defaultdict(lambda: defaultdict(dict)), "fylker": defaultdict(lambda: defaultdict(dict)),
          "landet": defaultdict(dict), "landet_uo": defaultdict(dict)}
    belop = defaultdict(dict)   # (gjeldende kode, år) -> {art: 1000 kr}
    innb = {}                   # (gjeldende kode, år) -> innbyggere
    d = post("12137", [it("KOKkommuneregion0000", kommuner + ["EAK", "EAKUO"]), it("KOKartkap0000", list(ART)),
                       it("ContentsCode", ["KOSbelopprinnb0000", "KOSbelop0000"]), it("Tid", tid)])
    per = defaultdict(dict)
    for k, v in celler(d):
        r, a, c, t = k["KOKkommuneregion0000"], ART[k["KOKartkap0000"]], k["ContentsCode"], k["Tid"]
        if r in ("EAK", "EAKUO"):
            if c == "KOSbelopprinnb0000":
                ut["landet" if r == "EAK" else "landet_uo"][a][t] = v
            continue
        g = FRAM(r)
        if c == "KOSbelop0000":
            belop[(g, t)][a] = belop[(g, t)].get(a, 0) + v
        else:
            per[(g, t)][a] = v
    for (g, t), arter in belop.items():
        # innbyggere fra skatt (alltid positiv); reserve: frie inntekter
        for a in ("skatt", "frie", "ramme"):
            if arter.get(a) and per[(g, t)].get(a):
                innb[(g, t)] = arter[a] * 1000 / per[(g, t)][a]
                break
        for a in ART.values():
            if (g, t) in per and a in per[(g, t)]:
                ut["kommuner"][g][a][t] = per[(g, t)][a]
    for nivaa in list(FYLKE) + ["NN"]:
        for t in tid:
            koder = [k for k in KODER if nivaa == "NN" or k[:2] == nivaa]
            if not all((k, t) in innb for k in koder):
                continue
            n = sum(innb[(k, t)] for k in koder)
            for a in ART.values():
                ut["fylker"][nivaa][a][t] = sum(belop[(k, t)].get(a, 0) for k in koder) * 1000 / n
            ut["fylker"][nivaa]["innbyggere"][t] = round(n)
    for k in KODER:
        for t in tid:
            if (k, t) in innb:
                ut["kommuner"][k]["innbyggere"][t] = round(innb[(k, t)])
    return ut, tid


def main():
    print("SSB 07022 (skatteinngang) ...", flush=True)
    s, siste = skatteinngang()
    print("SSB 12137 (KOSTRA per innbygger) ...", flush=True)
    k, kaar = kostra()
    r = lambda x: None if x is None else round(x)
    D = {
        "hentet": time.strftime("%Y-%m-%d"),
        "kilder": {"skatteinngang": "SSB 07022, ordinær skatt til primærkommunen, akkumulert (mill. kr)",
                   "kostra": "SSB 12137, kommunekonsern, kroner per innbygger"},
        "siste_mnd": siste, "kostra_aar": kaar,
        "inngang": {"kommuner": {kk: til_serie(v) for kk, v in s["kommuner"].items()},
                    "fylker": {kk: til_serie(v) for kk, v in s["fylker"].items()},
                    "landet": til_serie(s["landet"])},
        "kostra": {"kommuner": {kk: {a: {t: r(x) for t, x in v.items()} for a, v in arter.items()} for kk, arter in k["kommuner"].items()},
                   "fylker": {kk: {a: {t: r(x) for t, x in v.items()} for a, v in arter.items()} for kk, arter in k["fylker"].items()},
                   "landet": {a: {t: r(x) for t, x in v.items()} for a, v in k["landet"].items()},
                   "landet_uo": {a: {t: r(x) for t, x in v.items()} for a, v in k["landet_uo"].items()}},
    }
    mangler = [kk for kk in KODER if kk not in D["inngang"]["kommuner"] or kk not in D["kostra"]["kommuner"]]
    if mangler:
        print("MANGLER:", mangler)
    ut = HER / "analyse" / "skatt" / "data"
    ut.mkdir(parents=True, exist_ok=True)
    (ut / "skatt.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    djs = HER / "assets" / "data.js"
    js = djs.read_text(encoding="utf-8")
    blokk = "/* SKATT_DATA BEGIN */\nconst SKATT_DATA = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n/* SKATT_DATA END */"
    if "/* SKATT_DATA BEGIN */" in js:
        js = re.sub(r"/\* SKATT_DATA BEGIN \*/.*?/\* SKATT_DATA END \*/", lambda _m: blokk, js, flags=re.S)
    else:
        js = js.rstrip("\n") + "\n" + blokk + "\n"
    djs.write_text(js, encoding="utf-8")
    print(f"SKATT_DATA skrevet ({len(blokk) // 1024} KB). Siste måned {siste}, KOSTRA {kaar[0]}–{kaar[-1]}.")
    return D


if __name__ == "__main__":
    D = main()
    n = D["inngang"]["kommuner"]["1806"]
    print("Narvik skatteinngang 2025 (des):", n["2025"][11], " 2026 hittil:", [x for x in n["2026"] if x is not None][-1],
          " samme periode 2025:", n["2025"][len([x for x in n["2026"] if x is not None]) - 1])
    kk = D["kostra"]["kommuner"]["1806"]
    print("Narvik 2025 per innbygger:", {a: kk[a].get("2025") for a in kk}, " landet:", {a: D["kostra"]["landet"][a].get("2025") for a in D["kostra"]["landet"]},
          " landet u/Oslo skatt:", D["kostra"]["landet_uo"]["skatt"].get("2025"))
