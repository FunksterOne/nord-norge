#!/usr/bin/env python3
"""Nordområdepolitikken 2006–2026 → NORD_DATA i assets/data.js (tema 11).

Kilder:
  - Sju regjeringsdokumenter (2006–2025), registrert i analyse/nordomrade/notater/ (omtaler.json,
    lofter-samordnet.json, <år>.json) og analyse/nordomrade/data/temaord.json (ordtelling,
    analyse/nordomrade/skript/temaord.py; kildetekstene i kilder/ er ikke versjonert).
  - SSB 07459: folketall 1. januar 2006–siste år, fylker i 2024-inndeling (agg_KommFylker).
  - SSB 01222: befolkningsregnskap per kvartal, summert per år og over Nordland, Troms og Finnmark
    (flytting mellom de tre fylkene oppheves i summen).
  - SSB 07984: sysselsatte 15–74 år etter bosted og arbeidssted. Fylkeskodene følger inndelingen
    det enkelte år (18/19/20 → 18/54 → 18/55/56); kodelisten agg_FylkerGjeldende mangler Troms og
    Finnmark før 2024 og brukes derfor ikke.
"""
import json, re, sys, urllib.request, urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
NO = HER / "analyse" / "nordomrade"
V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/"
START = 2006


def get_v2(tab, params):
    url = V2 + tab + "/data?" + urllib.parse.urlencode({"lang": "no", "outputFormat": "json-stat2", **params})
    with urllib.request.urlopen(url, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def celler(d):
    ids = d["id"]
    keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
    for n, v in enumerate(d["value"]):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1):
            co[ids[i]] = keys[i][rest % d["size"][i]]
            rest //= d["size"][i]
        yield co, v


def siste_aar(tab):
    with urllib.request.urlopen(V2 + tab + "/metadata?lang=no", timeout=120) as r:
        m = json.loads(r.read().decode("utf-8"))
    return list(m["dimension"]["Tid"]["category"]["index"])[-1]


# ── Befolkning 1. januar (07459) ──
def befolkning():
    slutt = int(siste_aar("07459"))
    aar = [str(a) for a in range(START, slutt + 1)]
    alder = [f"{a:03d}" for a in range(105)] + ["105+"]
    felles = {"valueCodes[Tid]": ",".join(aar), "valueCodes[Alder]": ",".join(alder),
              "valueCodes[Kjonn]": "1,2", "valueCodes[ContentsCode]": "Personer1"}
    P = {}
    for reg, cl in (("F-18,F-55,F-56", "agg_KommFylker"), ("0", None)):
        par = {**felles, "valueCodes[Region]": reg}
        if cl:
            par["codelist[Region]"] = cl
        for co, v in celler(get_v2("07459", par)):
            r = "nn" if co["Region"].startswith("F-") else "landet"
            a = 105 if co["Alder"] == "105+" else int(co["Alder"])
            P.setdefault((r, co["Tid"]), [0] * 106)[a] += v or 0
    ut = {"aar": [int(a) for a in aar]}
    for r in ("nn", "landet"):
        ut[r] = {k: [sum(P[(r, a)][lo:hi]) for a in aar] for k, lo, hi in
                 (("tot", 0, 106), ("a2064", 20, 65), ("a65", 65, 106), ("a80", 80, 106), ("a2039", 20, 40))}
    return ut


# ── Befolkningsregnskap (01222) ──
def regnskap():
    sist = siste_aar("01222")
    kv = [f"{a}K{q}" for a in range(START, int(sist[:4]) + 1) for q in range(1, 5)]
    kv = kv[:kv.index(sist) + 1]
    K = ["Fodselsoverskudd4", "Innvandring5", "Utvandring6", "Tilflytting7", "Fraflytting8", "Folketilvekst10"]
    S, nkv = {}, {}
    for co, v in celler(get_v2("01222", {"codelist[Region]": "agg_KommFylker", "valueCodes[Region]": "F-18,F-55,F-56",
                                          "valueCodes[Tid]": ",".join(kv), "valueCodes[ContentsCode]": ",".join(K)})):
        a = int(co["Tid"][:4])
        S.setdefault(a, {k: 0 for k in K})[co["ContentsCode"]] += v or 0
        if v is not None and co["ContentsCode"] == K[0] and co["Region"] == "F-18":
            nkv[a] = nkv.get(a, 0) + 1
    aar = [a for a in sorted(S) if nkv.get(a) == 4]  # bare hele år
    return {"aar": aar,
            "fodsel": [S[a]["Fodselsoverskudd4"] for a in aar],
            "innvandring": [S[a]["Innvandring5"] - S[a]["Utvandring6"] for a in aar],
            "innenlands": [S[a]["Tilflytting7"] - S[a]["Fraflytting8"] for a in aar],
            "vekst": [S[a]["Folketilvekst10"] for a in aar]}


# ── Sysselsetting (07984) ──
def sysselsetting():
    d = get_v2("07984", {"valueCodes[Region]": "0,18,19,20,54,55,56", "valueCodes[NACE2007]": "*", "valueCodes[Kjonn]": "0",
                         "valueCodes[Alder]": "15-74", "valueCodes[ContentsCode]": "Sysselsatte,SysselsatteArb", "valueCodes[Tid]": "*"})
    navn = d["dimension"]["NACE2007"]["category"]["label"]
    V = {(co["Region"], co["NACE2007"], co["ContentsCode"], int(co["Tid"])): v for co, v in celler(d)}
    aar = sorted({k[3] for k in V})

    def nn(nace, c, t):
        regs = ["18", "19", "20"] if t < 2020 else (["18", "54"] if t < 2024 else ["18", "55", "56"])
        return sum(V.get((r, nace, c, t)) or 0 for r in regs)

    ut = {"aar": aar,
          "nn_bosted": [nn("00-99", "Sysselsatte", t) for t in aar], "landet_bosted": [V[("0", "00-99", "Sysselsatte", t)] for t in aar],
          "nn_arb": [nn("00-99", "SysselsatteArb", t) for t in aar], "landet_arb": [V[("0", "00-99", "SysselsatteArb", t)] for t in aar],
          "naering": []}
    a0, a1 = aar[0], aar[-1]
    for k, l in navn.items():
        if k in ("00-99", "00"):
            continue
        ut["naering"].append({"kode": k, "navn": l, "nn0": nn(k, "SysselsatteArb", a0), "nn1": nn(k, "SysselsatteArb", a1),
                              "la0": V[("0", k, "SysselsatteArb", a0)], "la1": V[("0", k, "SysselsatteArb", a1)]})
    return ut


# ── Dokumentene ──
URL = {
    "2006": "https://www.regjeringen.no/no/dokumenter/regjeringens-nordomradestrategi/id448697/",
    "2009": "https://www.regjeringen.no/no/dokumenter/nye-byggesteiner-i-nord/id548803/",
    "2011": "https://www.regjeringen.no/contentassets/a0140460a8d04e4ba9c4af449b5fa06d/no/pdfs/stm201120120007000dddpdfs.pdf",
    "2014": "https://www.regjeringen.no/en/dokumenter/nordkloden/id2076193/",
    "2017": "https://www.regjeringen.no/no/dokumenter/nordomradestrategi/id2550081/",
    "2020": "https://www.regjeringen.no/no/dokumenter/meld.-st.-9-20202021/id2787429/",
    "2025": "https://www.regjeringen.no/contentassets/ce4ca6a943494c1da569f45ae2d8dfb9/no/pdfs/h-2569-b-nordomradestrategi.pdf",
}
# Vurdering etter samme fire kriterier for alle dokumentene (SAMMENSTILLING.md, punkt 5).
# problem: 0–4 (Harvey-ball) for hvor godt befolkning, aldring og arbeidskraft beskrives med tall.
VURDERING = {
    "2006": {"problem": 1, "problem_t": "ett avsnitt, uten tall", "mal": "nei", "penger": "lite (199,5 mill. kr i 2007)", "evaluering": "nei", "vekt": "utenriks"},
    "2009": {"problem": 1, "problem_t": "ingen befolkningstall", "mal": "nei", "penger": "lite", "evaluering": "nei", "vekt": "utenriks"},
    "2011": {"problem": 1, "problem_t": "ett folketall i en tabell", "mal": "nei", "penger": "uklart («over en milliard årlig»)", "evaluering": "nei", "vekt": "utenriks"},
    "2014": {"problem": 1, "problem_t": "bare Hammerfest", "mal": "nei", "penger": "lite", "evaluering": "nei", "vekt": "blandet"},
    "2017": {"problem": 2, "problem_t": "SSB-tall", "mal": "nei", "penger": "lite (mest NTP)", "evaluering": "nei", "vekt": "innenriks"},
    "2020": {"problem": 4, "problem_t": "grundig", "mal": "nei", "penger": "små beløp, innenfor gjeldende rammer", "evaluering": "nei", "vekt": "innenriks"},
    "2025": {"problem": 1, "problem_t": "uten tall", "mal": "delvis (forsvarsarbeidsplasser)", "penger": "ingen egen ramme", "evaluering": "nei", "vekt": "innenriks, sikkerhetsbegrunnet"},
}
ANSLAG = [
    {"dok": "2017", "hva": "Befolkningsvekst i Nord-Norge 2017–2030", "fra": 2017, "til": 2030, "pst": 4.7, "side": 11,
     "kilde": "Nordområdestrategien 2017, s. 11 (SSBs framskriving)"},
    {"dok": "2020", "hva": "Sysselsatte per pensjonist i Nord-Norge", "i_dag": 3.1, "aar": 2040, "verdi": 1.9, "side": 54,
     "kilde": "Meld. St. 9 (2020–2021), s. 54"},
]
# Oppgitte samlebeløp (notater/etter-2025-og-hull.md). Definisjonene skifter, så rekken er ikke sammenlignbar.
PENGER = [
    {"aar": "Før 2011", "belop": "over 1 milliard kroner per år", "hva": "Regjeringens samlede forslag til nordområdetiltak", "kilde": "Meld. St. 7 (2011–2012), s. 43"},
    {"aar": "2011", "belop": "om lag 1,2 milliarder kroner", "hva": "Foreslått bevilgning til nordområdetiltak", "kilde": "Nordområdesatsingen – status oktober 2010"},
    {"aar": "2012", "belop": "om lag 1,5 milliarder kroner", "hva": "Nordområdetiltak samlet", "kilde": "Flertallsregjeringens statusrapport (2011)"},
    {"aar": "2016", "belop": "om lag 3 milliarder kroner", "hva": "Tiltak innen fem prioriterte områder (sekundærkilde)", "kilde": "High North News, 7. oktober 2015"},
    {"aar": "2016", "belop": "320,1 millioner kroner", "hva": "UDs kap. 118 post 70, nordområdetiltak og prosjektsamarbeid med Russland", "kilde": "Innst. 7 S (2015–2016)"},
    {"aar": "2025", "belop": "54,6 millioner kroner", "hva": "UDs kap. 118 post 70, nordområdetiltak, Russland og atomsikkerhet", "kilde": "Innst. 7 S (2024–2025)"},
    {"aar": "2026", "belop": "posten lagt ned", "hva": "Arktis 2030 flyttet til KDD (67,1 millioner kroner via Troms fylkeskommune og 20 millioner kroner fordelt på tre fylker)", "kilde": "Prop. 1 S (2025–2026) UD, s. 53"},
]
TEMANAVN = {
    "sikkerhet": "Sikkerhet og forsvar", "russland": "Russland", "klima_miljo": "Klima og miljø", "petroleum_energi": "Petroleum og energi",
    "fiskeri_havbruk": "Fiskeri og havbruk", "mineraler": "Mineraler", "reiseliv": "Reiseliv", "forskning": "Forskning og kunnskap",
    "utdanning": "Utdanning og kompetanse", "befolkning": "Befolkning og bosetting", "arbeidskraft": "Arbeidskraft",
    "helse_eldre": "Helse og eldre", "samferdsel": "Samferdsel", "samisk": "Samiske forhold", "svalbard": "Svalbard",
    "beredskap": "Beredskap", "ungdom_kvinner": "Ungdom og kvinner",
}


def dokumenter():
    om = json.loads((NO / "notater" / "omtaler.json").read_text(encoding="utf-8"))
    lo = json.loads((NO / "notater" / "lofter-samordnet.json").read_text(encoding="utf-8")) if (NO / "notater" / "lofter-samordnet.json").exists() else None
    tw = json.loads((NO / "data" / "temaord.json").read_text(encoding="utf-8"))
    dok = []
    for o in om["dokumenter"]:
        i = o["id"]
        reg = json.loads((NO / "notater" / f"{i}.json").read_text(encoding="utf-8"))
        L = lo["dokumenter"][i] if lo else None
        dok.append({**{k: o.get(k) for k in ("id", "kort", "tittel", "regjering", "dato", "type", "sider", "kjerne", "avsnitt", "sitat", "sitat_side", "storting")},
                    "url": URL[i], "ord": tw[i]["ord"], "vurdering": VURDERING[i],
                    "innsatsomrader": reg.get("innsatsomrader", []),
                    "lofter": {k: L[k] for k in ("n", "konkret", "vagt", "belop_nytt", "belop_eksisterende")} if L else None})
    kol = [d["id"] for d in dok]
    temaord = {"kolonner": kol, "rader": [{"key": k, "l": TEMANAVN[k], "v": [tw[c][k] for c in kol]} for k in TEMANAVN]}
    tekster = {k: om.get(k) for k in ("forhistorie", "innovasjonsloft", "etter2025", "statusrapport2010")}
    regel = lo["regel"] if lo else None
    return dok, temaord, tekster, regel


def main():
    print("Dokumenter og ordtelling ...", flush=True)
    dok, temaord, tekster, regel = dokumenter()
    print("SSB 07459 ...", flush=True)
    B = befolkning()
    print("SSB 01222 ...", flush=True)
    R = regnskap()
    print("SSB 07984 ...", flush=True)
    S = sysselsetting()

    # Kontroller: regnskapet skal gå opp mot endringen i folketall.
    i0, i1 = B["aar"].index(R["aar"][0]), B["aar"].index(R["aar"][-1] + 1) if R["aar"][-1] + 1 in B["aar"] else None
    kontroll = {"sum_vekst": sum(R["vekst"]), "sum_komp": sum(R["fodsel"]) + sum(R["innvandring"]) + sum(R["innenlands"]),
                "endring_folketall": B["nn"]["tot"][i1] - B["nn"]["tot"][i0] if i1 is not None else None,
                "syss_arb_kommunesum_2008": 231037}
    assert abs(kontroll["sum_vekst"] - kontroll["sum_komp"]) < 150, kontroll  # differansen er registerkorreksjoner
    if kontroll["endring_folketall"] is not None:
        assert abs(kontroll["sum_vekst"] - kontroll["endring_folketall"]) < 100, kontroll
    assert S["aar"][0] != 2008 or S["nn_arb"][0] == 231037, S["nn_arb"][0]
    print(json.dumps(kontroll, ensure_ascii=False))

    payload = {
        "dokumenter": dok,
        "merker": [{"aar": 2010, "tekst": "Statusrapport (oktober 2010)", "lite": True}, {"aar": 2025, "tekst": "Plan for Norge (desember 2025)", "lite": True}],
        "temaord": temaord, "tekster": tekster, "kodingsregel": regel,
        "befolkning": B, "regnskap": R, "sysselsetting": S, "anslag": ANSLAG, "penger": PENGER, "kontroll": kontroll,
        "kilde": "Regjeringens nordområdedokumenter 2006–2025; SSB 07459, 01222 og 07984",
    }
    nn = B["nn"]
    print("Folketall", B["aar"][0], nn["tot"][0], B["aar"][-1], nn["tot"][-1],
          "andel", round(100 * nn["tot"][0] / B["landet"]["tot"][0], 2), round(100 * nn["tot"][-1] / B["landet"]["tot"][-1], 2))
    print("Regnskap", R["aar"][0], "–", R["aar"][-1], "fødsel", sum(R["fodsel"]), "innv", sum(R["innvandring"]), "innenl", sum(R["innenlands"]))
    print("Syss bosted", S["aar"][0], S["nn_bosted"][0], S["aar"][-1], S["nn_bosted"][-1])

    html = DATA_JS.read_text(encoding="utf-8")
    js_lit = "const NORD_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* NORD_DATA BEGIN */", "/* NORD_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in html:
        new = re.sub(r"/\* NORD_DATA BEGIN \*/.*?/\* NORD_DATA END \*/", lambda _m: block, html, flags=re.DOTALL)
    elif "/* UNG_DATA END */" in html:
        new = html.replace("/* UNG_DATA END */", "/* UNG_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret UNG_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    print(f"Injected NORD_DATA ({len(js_lit)} tegn)")


if __name__ == "__main__":
    main()
