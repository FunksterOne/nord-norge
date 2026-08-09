#!/usr/bin/env python3
"""Henter byggeaktivitet for bolig per kommune fra SSB og injiserer BOLIG_DATA
i assets/data.js.

Kilder:
  05889  Byggeareal: igangsettingstillatelser og fullforte boliger (K), kvartal 2000K1-
  10784  Byggeareal: avgang av boliger (K), kvartal 2009K1-

Kommunenummer skjotes automatisk via SSB KLASS (klassifikasjon 131) slik at
seriene folger dagens kommunegrenser (2024-inndelingen) hele veien tilbake:
  19xx/20xx (foer 2020) -> 54xx (2020-2023) -> 55xx/56xx (2024-), pluss eldre
  sammenslaainger (Skjerstad->Bodo 2005, Bjarkoy->Harstad 2013 osv.).
Kommuner som ble DELT (Tysfjord 1850 -> Narvik + Hamaroy i 2020) kan ikke
fordeles uten skjonn: de utelates fra kommuneseriene, men telles med i
fylkes- og landsdelssummene. Dielddanuorri-Tjeldsund (1852, Nordland) flyttet
til Troms i 2020 og regnes som Troms i hele serien.
"""
import json
import re
import datetime
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

CODES = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
"1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
"1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
"1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503",
"5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530",
"5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605",
"5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628",
"5630","5632","5634","5636"]


def fylke(nykode):
    return "Nordland" if nykode.startswith("18") else (
        "Troms" if nykode.startswith("55") else "Finnmark")


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def post_ssb(table, query):
    body = {"query": query, "response": {"format": "json-stat2"}}
    req = urllib.request.Request(
        f"https://data.ssb.no/api/v0/no/table/{table}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def celler(d):
    dim = d["dimension"]; ids = d["id"]; sizes = d["size"]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in ids}
    strides = []; acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    for i, v in enumerate(d["value"]):
        rem = i; co = {}
        for k, st in zip(ids, strides):
            co[k] = cats[k][rem // st]; rem %= st
        yield co, v


def bygg_familier():
    """Skjotetabell fra KLASS: nykode -> mengde av alle forgjengerkoder."""
    d = get("https://data.ssb.no/api/klass/v1/classifications/131/changes"
            "?from=1999-01-01&to=2026-01-01&size=2000")
    changes = d.get("codeChanges", [])
    succ = {}
    for c in changes:
        o, n = c.get("oldCode"), c.get("newCode")
        if o and n and o != n:
            succ.setdefault(o, set()).add(n)
    splittet = {o for o, ns in succ.items() if len(ns) > 1}

    def preds(kode, sett):
        for o, ns in succ.items():
            if kode in ns and o not in splittet and o not in sett:
                sett.add(o)
                preds(o, sett)
        return sett

    familier = {k: sorted(preds(k, set()) | {k}) for k in CODES}
    # Splittede forgjengere som ender i vaare kommuner (for fylkessummene)
    split_i_nord = {}
    for o in splittet:
        ns = succ[o]
        mine = [n for n in ns if n in CODES or any(n in fam for fam in familier.values())]
        if mine:
            # fylke = fylket til (foerste) etterfolger i dagens inndeling
        # (Tysfjord -> Narvik/Hamaroy -> Nordland)
            def nykode_for(n):
                if n in CODES:
                    return n
                for k, fam in familier.items():
                    if n in fam:
                        return k
                return None
            nk = nykode_for(mine[0])
            if nk:
                split_i_nord[o] = fylke(nk)
    return familier, split_i_nord


def hent_serie(table, contents, region_koder, tid_koder, gyldige_regioner):
    koder = [k for k in region_koder if k in gyldige_regioner]
    q = [
        {"code": "Region", "selection": {"filter": "item", "values": koder}},
        {"code": "Byggeareal", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": [contents]}},
        {"code": "Tid", "selection": {"filter": "item", "values": tid_koder}},
    ]
    d = post_ssb(table, q)
    ut = {}
    for co, v in celler(d):
        if v is None:
            continue
        key = (co["Region"], co["Tid"])
        ut[key] = ut.get(key, 0) + v
    return ut


def main():
    print("Bygger skjotetabell fra KLASS...", flush=True)
    familier, split_i_nord = bygg_familier()
    alle_koder = sorted({k for fam in familier.values() for k in fam} | set(split_i_nord) | {"0"})
    print(f"  {len(familier)} kommuner, {len(alle_koder) - 1} koder totalt, "
          f"splittet (kun fylkessum): {sorted(split_i_nord)}")

    meta = get("https://data.ssb.no/api/v0/no/table/05889")
    tid = next(v for v in meta["variables"] if v["code"] == "Tid")["values"]
    reg_ok = set(next(v for v in meta["variables"] if v["code"] == "Region")["values"])
    meta_av = get("https://data.ssb.no/api/v0/no/table/10784")
    tid_av = next(v for v in meta_av["variables"] if v["code"] == "Tid")["values"]
    reg_ok_av = set(next(v for v in meta_av["variables"] if v["code"] == "Region")["values"])

    print(f"Henter 05889 Igangsatte ({tid[0]}-{tid[-1]})...", flush=True)
    ig = hent_serie("05889", "Igangsatte", alle_koder, tid, reg_ok)
    print("Henter 05889 Fullforte...", flush=True)
    fu = hent_serie("05889", "Fullforte", alle_koder, tid, reg_ok)
    print(f"Henter 10784 Avgang ({tid_av[0]}-{tid_av[-1]})...", flush=True)
    av = hent_serie("10784", "AvgangBoliger", alle_koder, tid_av, reg_ok_av)

    def spleis(kilde, fam, tider):
        return [int(sum(kilde.get((k, t), 0) for k in fam)) for t in tider]

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "tables": ["05889", "10784"],
        "quarters": tid,
        "av_quarters": tid_av,
        "kommuner": {},
        "fylker": {}, "landsdel": {}, "riket": {},
        "splits": {o: f"{f} (delt kommune, kun med i fylkes- og landsdelssum)"
                   for o, f in split_i_nord.items()},
    }
    for k in CODES:
        payload["kommuner"][k] = {
            "ig": spleis(ig, familier[k], tid),
            "fu": spleis(fu, familier[k], tid),
            "av": spleis(av, familier[k], tid_av),
        }
    for fnavn in ["Nordland", "Troms", "Finnmark"]:
        fam = [k for nk in CODES if fylke(nk) == fnavn for k in familier[nk]]
        fam += [o for o, f in split_i_nord.items() if f == fnavn]
        payload["fylker"][fnavn] = {
            "ig": spleis(ig, fam, tid), "fu": spleis(fu, fam, tid),
            "av": spleis(av, fam, tid_av)}
    alle_nord = [k for fam in familier.values() for k in fam] + list(split_i_nord)
    payload["landsdel"] = {"ig": spleis(ig, alle_nord, tid),
                           "fu": spleis(fu, alle_nord, tid),
                           "av": spleis(av, alle_nord, tid_av)}
    payload["riket"] = {"ig": spleis(ig, ["0"], tid), "fu": spleis(fu, ["0"], tid)}

    # --- kontroller ------------------------------------------------------
    siste4 = tid[-4:]
    i4 = [tid.index(t) for t in siste4]
    ld = payload["landsdel"]
    r12i = sum(ld["ig"][i] for i in i4); r12f = sum(ld["fu"][i] for i in i4)
    print(f"\nKontroll landsdel siste 12 mnd ({siste4[0]}-{siste4[-1]}): "
          f"igangsatt {r12i} (kbnn: 1239), fullfort {r12f} (kbnn: 1238)")
    tromso = payload["kommuner"]["5501"]
    i2015 = [i for i, t in enumerate(tid) if t.startswith("2015")]
    print(f"Tromso 2015 (spleiset): igangsatt {sum(tromso['ig'][i] for i in i2015)} (skal vaere > 0)")
    iaar = [i for i, t in enumerate(tid) if t.startswith(tid[-1][:4])]
    uten = [k for k in CODES if sum(payload['kommuner'][k]['ig'][i] for i in iaar) == 0]
    print(f"Kommuner uten igangsetting hittil i {tid[-1][:4]}: {len(uten)} (kbnn 1. halvaar 2026: 40)")
    rik12 = sum(payload["riket"]["ig"][i] for i in i4)
    print(f"Riket siste 12 mnd igangsatt: {rik12} (kbnn/PS-korrigert: 19043)")

    # --- injiser ---------------------------------------------------------
    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const BOLIG_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* BOLIG_DATA BEGIN */\n" + lit + "\n/* BOLIG_DATA END */"
    if "/* BOLIG_DATA BEGIN */" in js:
        js = re.sub(r"/\* BOLIG_DATA BEGIN \*/.*?/\* BOLIG_DATA END \*/", block, js, flags=re.DOTALL)
    else:
        anchor = "/* KJONN_DATA END */"
        if anchor not in js:
            raise SystemExit("KJONN_DATA END ikke funnet")
        js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injisert BOLIG_DATA ({len(lit)} tegn) i {DATA_JS}")


if __name__ == "__main__":
    main()
