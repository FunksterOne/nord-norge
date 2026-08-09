#!/usr/bin/env python3
"""Migrerer DATA.proj i assets/data.js til ny SSB-fremskriving.

Kilde: SSB tabell 14746 (regionale befolkningsframskrivinger 2026, publisert
12. juni 2026), 2026-2050. Erstatter tabell 14288 (2024-basert).

Hva scriptet gjor:
  1. Henter MMMM (Personer), LLML (Personer1) og HHMH (Personer2) for de 80
     kommunene, per ettaarsalder, og bygger main/low/high + aldersgrupper.
  2. Rebaserer TF-ATTR- og TF-MVP-seriene mekanisk til faktisk folketall
     1.1.2026 (= 14746-basisaaret): banene nivaajusteres (differanse mot
     kalenderaar 2026 i gammel bane), men rekjoeres IKKE.
     - Scenarioserier (ukraXX, uXX) og sensitivitet (s75/s125) rebaseres med
       "aar siden basisaar"-profil, slik at sjokket fortsatt inntreffer i
       foerste framskrivingsaar.
  3. Regenererer proj.landsdel som sum av kommunene.
  4. Oppdaterer proj.years (2026-2050) og proj.meta.
  5. Skriver ut forsoergerbyrde (65+/20-64) i 2050 per fylke for hele landet
     (til den hardkodede listen i tema-aldring.html).

Historikk-blokken (backtest, reg_nm, win_note, kostra*, robek) beroeres ikke.
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

FYLKE_KODER = ["03", "11", "15", "18", "31", "32", "33", "34", "39", "40",
               "42", "46", "50", "55", "56"]

NYE_AAR = list(range(2026, 2051))          # 25 aar
ANTALL_GAMLE = 27                          # 2024-2050
SKIFT = 2                                  # gammel indeks for 2026

# Aldersgrupper -> (fra, til) inklusiv, 106 ettaarsklasser 0..105+
GRUPPER = {
    "a019": (0, 19), "a2064": (20, 64), "a65": (65, 105),
    "a80": (80, 105), "a15": (1, 5), "a615": (6, 15), "a67": (67, 105),
}


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


def hent_alternativ(koder, contents_code):
    """Returnerer {kommune: {aar: {alder:int -> antall}}} summert over kjonn."""
    q = [
        {"code": "Region", "selection": {"filter": "item", "values": koder}},
        {"code": "Kjonn", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Alder", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": [contents_code]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [str(a) for a in NYE_AAR]}},
    ]
    d = post_ssb("14746", q)
    ut = {}
    for co, v in celler(d):
        if v is None:
            continue
        alder = int(co["Alder"].replace("+", ""))
        aar = ut.setdefault(co["Region"], {}).setdefault(co["Tid"], {})
        aar[alder] = aar.get(alder, 0) + v
    return ut


def serie_total(per_alder, kode):
    return [sum(per_alder[kode][str(a)].values()) for a in NYE_AAR]


def serie_gruppe(per_alder, kode, lo, hi):
    ut = []
    for a in NYE_AAR:
        rad = per_alder[kode][str(a)]
        ut.append(sum(v for alder, v in rad.items() if lo <= alder <= hi))
    return ut


def rebase_bane(gammel, anker):
    """Nivaajustering av basisbane: kalenderaar beholdes, nivaaet flyttes."""
    return [round(gammel[i + SKIFT] - gammel[SKIFT] + anker) for i in range(len(NYE_AAR))]


def rebase_sjokk(gammel_base, gammel_scenario, ny_base):
    """Scenarioserie: effektprofil per aar-siden-basisaar legges paa ny bane."""
    return [round(ny_base[i] - (gammel_base[i] - gammel_scenario[i]))
            for i in range(len(NYE_AAR))]


def rebase_ratio(gammel_base, gammel_scenario, ny_base):
    """Sensitivitetsserie: forholdet til egen bane per aar-siden-basisaar."""
    return [round(ny_base[i] * (gammel_scenario[i] / gammel_base[i])) if gammel_base[i] else ny_base[i]
            for i in range(len(NYE_AAR))]


def main():
    js = DATA_JS.read_text(encoding="utf-8")
    linjer = js.split("\n")
    idx = next(i for i, l in enumerate(linjer) if l.startswith("const DATA = "))
    DATA = json.loads(linjer[idx][len("const DATA = "):].rstrip(";"))
    proj = DATA["proj"]
    koder = list(proj["kommuner"].keys())
    assert len(koder) == 80, f"ventet 80 kommuner, fant {len(koder)}"
    if proj["meta"].get("tabell") == "14746":
        print("ADVARSEL: proj er allerede 14746-basert - kjoerer likevel (idempotent).")

    print("Henter 14746 MMMM (80 kommuner x alder x 2026-2050)...", flush=True)
    mmmm = hent_alternativ(koder, "Personer")
    print("Henter 14746 LLML...", flush=True)
    llml = hent_alternativ(koder, "Personer1")
    print("Henter 14746 HHMH...", flush=True)
    hhmh = hent_alternativ(koder, "Personer2")

    avvik_basis = []
    for kode in koder:
        o = proj["kommuner"][kode]
        alder = DATA["kommuner"][kode]["alder"]
        ny_main = serie_total(mmmm, kode)
        # Basisaarskontroll: 14746 sitt 2026-tall skal vaere lik registerdata
        # (alder-arrayen) som allerede ligger i dashbordet.
        if ny_main[0] != sum(alder):
            avvik_basis.append((kode, sum(alder), ny_main[0]))

        anker = {g: sum(alder[lo:hi + 1]) for g, (lo, hi) in GRUPPER.items()}
        anker_tot = ny_main[0]

        gammel = {f: list(o[f]) for f in
                  ["main", "low", "high", "a019", "a2064", "a65",
                   "tfattr", "tfattr_a019", "tfattr_a2064", "tfattr_a65",
                   "ukra50", "ukra75", "ukra100"]}

        o["main"] = ny_main
        o["low"] = serie_total(llml, kode)
        o["high"] = serie_total(hhmh, kode)
        for g in ["a019", "a2064", "a65"]:
            lo_, hi_ = GRUPPER[g]
            o[g] = serie_gruppe(mmmm, kode, lo_, hi_)

        o["tfattr"] = rebase_bane(gammel["tfattr"], anker_tot)
        for g in ["a019", "a2064", "a65"]:
            o[f"tfattr_{g}"] = rebase_bane(gammel[f"tfattr_{g}"], anker[g])
        for pct in ["50", "75", "100"]:
            o[f"ukra{pct}"] = rebase_sjokk(gammel["tfattr"], gammel[f"ukra{pct}"], o["tfattr"])

        for vindu, mw in o.get("mw", {}).items():
            g_pop = list(mw["pop"])
            mw["pop"] = rebase_bane(g_pop, anker_tot)
            for f in ["nat", "mig"]:
                gml = list(mw[f])
                mw[f] = [round(x - gml[SKIFT]) for x in gml[SKIFT:SKIFT + len(NYE_AAR)]]
            for g in ["a019", "a2064", "a65", "a80", "a15", "a615", "a67"]:
                mw[g] = rebase_bane(list(mw[g]), anker[g])
            for pct in ["50", "75", "100"]:
                mw[f"u{pct}"] = rebase_sjokk(g_pop, list(mw[f"u{pct}"]), mw["pop"])
            for s in ["s75", "s125"]:
                mw[s] = rebase_ratio(g_pop, list(mw[s]), mw["pop"])

    if avvik_basis:
        print(f"ADVARSEL: {len(avvik_basis)} kommuner der 14746-basis != alder-array:")
        for kode, a, b in avvik_basis[:10]:
            print(f"  {kode}: alder-sum {a}, 14746 {b}")

    # --- landsdel: sum av kommunene -------------------------------------
    L = proj["landsdel"]
    L["years"] = NYE_AAR
    n = len(NYE_AAR)
    for f in ["tfattr", "ukra50", "ukra75", "ukra100"]:
        L[f] = [sum(proj["kommuner"][k][f][i] for k in koder) for i in range(n)]
    L["ukr_total"] = sum(proj["kommuner"][k].get("ukr", 0) for k in koder)
    mwfelter = ["pop", "nat", "mig", "a019", "a2064", "a65", "a80", "a15",
                "a615", "a67", "u50", "u75", "u100", "s75", "s125"]
    for vindu in ["kons", "sentral", "opt"]:
        L["mw"][vindu] = {f: [sum(proj["kommuner"][k]["mw"][vindu][f][i] for k in koder)
                              for i in range(n)] for f in mwfelter}

    # --- years + meta ----------------------------------------------------
    proj["years"] = NYE_AAR
    proj["meta"]["tabell"] = "14746"
    proj["meta"]["basisaar"] = 2026
    for felt in ["tfmvp", "tfattr"]:
        if "rebasert" not in proj["meta"][felt]:
            proj["meta"][felt] += (
                " Rebasert mekanisk til 1.1.2026-basis ved 14746-migreringen "
                "(aug. 2026): nivaajustert til faktisk folketall, ikke rekjoert.")

    linjer[idx] = "const DATA = " + json.dumps(DATA, ensure_ascii=False, separators=(",", ":")) + ";"
    DATA_JS.write_text("\n".join(linjer), encoding="utf-8")

    # --- kontrollutskrift ------------------------------------------------
    def s2050(f):
        return sum(proj["kommuner"][k][f][-1] for k in koder)
    print("\nKontroll (2050, hele landsdelen):")
    print(f"  MMMM {s2050('main')}, lav {s2050('low')}, hoey {s2050('high')}, TF-ATTR {s2050('tfattr')}")
    b = proj["kommuner"]["1804"]
    print(f"  Bodoe: 2026 {b['main'][0]}, 2050 MMMM {b['main'][-1]}, TF-ATTR 2050 {b['tfattr'][-1]}")
    t = proj["kommuner"]["5501"]
    print(f"  Tromsoe: 2026 {t['main'][0]}, 2050 MMMM {t['main'][-1]}, TF-ATTR 2050 {t['tfattr'][-1]}")

    # --- forsoergerbyrde 2050 per fylke (til tema-aldring.html) ----------
    print("\nHenter fylkestall for forsoergerbyrde 2050 (alle fylker)...", flush=True)
    fylker = hent_alternativ(FYLKE_KODER, "Personer")
    navn_q = [{"code": "Region", "selection": {"filter": "item", "values": FYLKE_KODER}},
              {"code": "Kjonn", "selection": {"filter": "item", "values": ["1"]}},
              {"code": "Alder", "selection": {"filter": "item", "values": ["000"]}},
              {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Personer"]}},
              {"code": "Tid", "selection": {"filter": "item", "values": ["2026"]}}]
    dnavn = post_ssb("14746", navn_q)
    labels = dnavn["dimension"]["Region"]["category"]["label"]
    print("Forsoergerbyrde 65+/20-64 i 2050 (14746 MMMM):")
    for kode in FYLKE_KODER:
        rad = fylker[kode]["2050"]
        a2064 = sum(v for a, v in rad.items() if 20 <= a <= 64)
        a65 = sum(v for a, v in rad.items() if a >= 65)
        print(f"  {labels.get(kode, kode)}: {a65 / a2064 * 100:.1f}")


if __name__ == "__main__":
    main()
