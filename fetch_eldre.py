#!/usr/bin/env python3
"""Eldre, demens og årsverk i omsorgstjenestene per kommune 2026–2050 → ELDRE_DATA i assets/data.js.

Bakgrunn: Riksrevisjonens Dokument 3:16 (2025–2026) om helse- og omsorgstjenester til eldre. Rapporten tallfester
ikke behov per kommune; tallene her er egne, mekaniske beregninger («alt annet likt»):

  80+, 90+, 20–64 år   SSB 14746, hovedalternativet MMMM (2026-årgangen)
  Forsørgerbrøk        SSB 14751 (65+ per 20–64), MMMM
  Demens (anslag)      Aldersspesifikke forekomstrater fra Demenskartet (Aldring og helse; HUNT4 70+, Gjøra mfl. 2021),
                       like for begge kjønn og hele landet, brukt på befolkningsbanen i 14746
  Årsverk 2025         SSB 14534, avtalte pasient- og brukerrettede årsverk (POB), i alt og sykepleiere (01)
  Behovsindeks 2050    Brukere av hjemme- og institusjonstjenester (SSB 12003, A+B) per innbygger i landet 2025
                       (07459) i aldersgruppene 0–66, 67–79 og 80+, brukt på kommunens befolkning 2026 og 2050.
                       Årsverksbehov 2050 = årsverk 2025 × indeks (bemanning per bruker holdes konstant).
  Sentralitet          SSB KLASS 128 (sentralitetsindeks 2024)

Riksrevisjonens tall i RR-blokken er kontrollert mot rapporten (PDF-sider i feltet «side»).
Kontrollert mot overleveringsfilen nn_kommuner_eldre_2026_2050.csv 20.10.2026: alle SSB-kolonner er like;
behovsindeksen avviker med inntil 0,01 (avrunding i mellomtrinn).
Kjør:  python fetch_eldre.py
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
API = "https://data.ssb.no/api/v0/no/table/"
AAR = ["2026", "2030", "2040", "2050"]
DEMENS = [(30, 64, 0.0008), (65, 69, 0.0057), (70, 74, 0.0639), (75, 79, 0.1003),
          (80, 84, 0.1780), (85, 89, 0.3045), (90, 200, 0.4147)]
FYLKER = {"18": "Nordland", "55": "Troms", "56": "Finnmark"}


def post(tab, q):
    req = urllib.request.Request(API + tab, data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
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


def alle(var):
    return {"code": var, "selection": {"filter": "all", "values": ["*"]}}


def item(var, verdier):
    return {"code": var, "selection": {"filter": "item", "values": verdier}}


def main():
    js = DATA_JS.read_text(encoding="utf-8")
    linje = next(l for l in js.split("\n") if l.startswith("const DATA = "))
    koder = sorted(json.loads(linje[len("const DATA = "):].rstrip(";"))["proj"]["kommuner"].keys())
    assert len(koder) == 80, len(koder)

    print("SSB 14746 ...", flush=True)
    P = {}
    for co, v in celler(post("14746", [item("Region", koder + ["0"]), alle("Kjonn"), alle("Alder"),
                                       item("ContentsCode", ["Personer"]), item("Tid", AAR)])):
        if v is None:
            continue
        a = int(co["Alder"].replace("+", ""))
        rad = P.setdefault(co["Region"], {}).setdefault(co["Tid"], {})
        rad[a] = rad.get(a, 0) + v
    grp = lambda r, t, lo, hi: sum(v for a, v in P[r][t].items() if lo <= a <= hi)
    dem = lambda r, t: sum(grp(r, t, lo, hi) * q for lo, hi, q in DEMENS)

    print("SSB 12003 + 07459 (bruksrater 2025) ...", flush=True)
    bruk = {}
    for co, v in celler(post("12003", [item("KOKkommuneregion0000", ["EAK"]), alle("KOKalder0000"), item("KOKTenesteGrp0000", ["A", "B"]),
                                       item("ContentsCode", ["KOSomsorgantbruk0000"]), item("Tid", ["2025"])])):
        bruk[co["KOKalder0000"]] = bruk.get(co["KOKalder0000"], 0) + (v or 0)
    bef = {}
    for co, v in celler(post("07459", [item("Region", ["0"]), alle("Kjonn"), alle("Alder"),
                                       item("ContentsCode", ["Personer1"]), item("Tid", ["2025"])])):
        a = int(co["Alder"].replace("+", ""))
        bef[a] = bef.get(a, 0) + (v or 0)
    b = lambda lo, hi: sum(v for a, v in bef.items() if lo <= a <= hi)
    rate = [bruk["F000-066"] / b(0, 66), bruk["F067-079"] / b(67, 79), bruk["F080-120"] / b(80, 200)]
    brukere = lambda r, t: grp(r, t, 0, 66) * rate[0] + grp(r, t, 67, 79) * rate[1] + grp(r, t, 80, 200) * rate[2]

    print("SSB 14534 (årsverk) ...", flush=True)
    AV = {}
    for co, v in celler(post("14534", [item("KOKkommuneregion0000", koder + ["EAK"]), item("KOKstillingkode0000", ["POB"]),
                                       item("KOKutdanningoms0000", ["TOT", "01"]), item("ContentsCode", ["KOSARBAARSVERKST0000"]),
                                       item("Tid", ["2015", "2025"])])):
        AV[(co["KOKkommuneregion0000"], co["KOKutdanningoms0000"], co["Tid"])] = v

    print("SSB 14751 (forsørgerbrøk) ...", flush=True)
    FB = {(co["Region"], co["Tid"]): v for co, v in celler(post("14751", [
        item("Region", ["0", "18", "55", "56"] + koder), item("Framskriv", ["MMMM"]),
        item("ContentsCode", ["ForsByrdeEldre"]), item("Tid", ["2026", "2050"])]))}

    print("KLASS sentralitet ...", flush=True)
    url = "https://data.ssb.no/api/klass/v1/classifications/131/correspondsAt.json?targetClassificationId=128&date=2024-06-01"
    with urllib.request.urlopen(url, timeout=60) as r:
        SENT = {m["sourceCode"]: int(m["targetCode"]) for m in json.loads(r.read().decode("utf-8"))["correspondenceItems"]}

    kom = {}
    for k in koder:
        av25 = AV.get((k, "TOT", "2025"))
        idx = brukere(k, "2050") / brukere(k, "2026")
        kom[k] = [SENT[k], grp(k, "2026", 80, 200), grp(k, "2050", 80, 200), grp(k, "2026", 90, 200), grp(k, "2050", 90, 200),
                  round(dem(k, "2026")), round(dem(k, "2050")), grp(k, "2026", 20, 64), grp(k, "2050", 20, 64),
                  round(av25) if av25 is not None else None, AV.get((k, "01", "2025")), round(idx, 3),
                  round(av25 * idx) if av25 is not None else None, FB.get((k, "2026")), FB.get((k, "2050"))]

    def agg(ks, navn, fb=None):
        s = lambda i: sum(kom[k][i] or 0 for k in ks)
        av, behov = sum(AV.get((k, "TOT", "2025")) or 0 for k in ks), sum((AV.get((k, "TOT", "2025")) or 0) * brukere(k, "2050") / brukere(k, "2026") for k in ks)
        return {"navn": navn, "n": len(ks),
                "a80": [sum(grp(k, t, 80, 200) for k in ks) for t in AAR], "a90": [sum(grp(k, t, 90, 200) for k in ks) for t in AAR],
                "demens": [round(sum(dem(k, t) for k in ks)) for t in AAR], "a2064": [sum(grp(k, t, 20, 64) for k in ks) for t in AAR],
                "aarsverk": round(av), "sykepleier": round(s(10)), "behov2050": round(behov), "fb": fb}

    fylker = {navn: agg([k for k in koder if k[:2] == nr], navn, [FB[(nr, "2026")], FB[(nr, "2050")]]) for nr, navn in FYLKER.items()}
    nn = agg(koder, "Nord-Norge")
    sent = {str(c): agg([k for k in koder if SENT[k] == c], f"Klasse {c}") for c in (3, 4, 5, 6)}
    av_l = AV[("EAK", "TOT", "2025")]
    landet = {"navn": "Hele landet", "a80": [grp("0", t, 80, 200) for t in AAR], "a90": [grp("0", t, 90, 200) for t in AAR],
              "demens": [round(dem("0", t)) for t in AAR], "a2064": [grp("0", t, 20, 64) for t in AAR],
              "aarsverk": round(av_l), "aarsverk2015": round(AV[("EAK", "TOT", "2015")]),
              "behov2050": round(av_l * brukere("0", "2050") / brukere("0", "2026")), "fb": [FB[("0", "2026")], FB[("0", "2050")]]}

    payload = {
        "hentet": "2026-10-20", "aar": [int(a) for a in AAR],
        "felt": ["sentralitet", "a80_2026", "a80_2050", "a90_2026", "a90_2050", "demens_2026", "demens_2050", "a2064_2026", "a2064_2050",
                 "aarsverk_2025", "sykepleier_2025", "behovsindeks", "behov_2050", "fb_2026", "fb_2050"],
        "kommuner": kom, "fylker": fylker, "nn": nn, "landet": landet, "sentralitet": sent,
        "bruksrater": [round(r * 100, 2) for r in rate], "demensrater": [[lo, min(hi, 90) if hi < 200 else None, q] for lo, hi, q in DEMENS],
        "fhi_demens": {"2025": 115000, "2030": 135000, "2040": 185000, "2050": 225000, "kilde": "FHI, Folkehelserapporten, oppdatert 27.5.2026"},
        "rr": {
            "tittel": "Riksrevisjonen si undersøking av kommunale helse- og omsorgstenester til eldre",
            "dok": "Dokument 3:16 (2025–2026)", "dato": "2026-06-09",
            "url": "https://www.stortinget.no/globalassets/pdf/dokumentserien/2025-2026/dok3-202526-016.pdf",
            "funn": [
                {"t": "Overordnet vurdering: kritikkverdig. Helse- og omsorgsdepartementet har ikke fulgt opp at kommunene er forberedt på at det blir flere eldre.", "side": 10},
                {"t": "33 av 60 tilfeldig valgte kommuner planlegger ikke å øke antallet sykehjemsplasser eller omsorgsboliger.", "side": 34},
                {"t": "31 % av kommunene har for få sykehjemsplasser, og om lag 43 % for få heldøgns omsorgsplasser.", "side": 16},
                {"t": "31 kommuner har ingen demensplasser; de er i sentralitetsklasse 4–6, og de fleste har under 5 000 innbyggere (s. 58 oppgir 28).", "side": 17},
                {"t": "Antallet institusjonsbrukere over 80 år falt med 16 % fra 2015 til 2025, mens årsverkene økte med 32 000 (28 %).", "side": "15 og 20"},
                {"t": "Mangelen på egnede boliger er størst i de nordligste fylkene.", "side": "18 og 65"},
                {"t": "Nordland, Troms og Finnmark har 2–3 allmennsykepleiere med avansert klinisk kompetanse per fylke, mot 9–18 i de andre fylkene.", "side": 75},
                {"t": "I Nordland søkte om lag 76 % av kommunene kompetanse- og tjenesteutviklingstilskudd i 2024 og 2025, færrest av alle embetene.", "side": 72},
                {"t": "Bindal, Vevelstad, Beiarn og Ibestad er blant seks kommuner med rundt 30 % innbyggere over 67 år i 2025.", "side": 49},
            ],
            "forsorg": {"2024": 0.32, "2050": 0.48, "side": 12, "merknad": "2024-årgangen av framskrivingen (SSB 14293)"},
            "demens_motsigelse": "Rapporten skriver «meir enn dobla fram mot 2040» (s. 16 og 54) og «nær dobla innan 2050» (s. 119). FHIs tall gir om lag en dobling fram mot 2050.",
        },
    }
    js_lit = "const ELDRE_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* ELDRE_DATA BEGIN */", "/* ELDRE_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in js:
        new = re.sub(r"/\* ELDRE_DATA BEGIN \*/.*?/\* ELDRE_DATA END \*/", lambda _m: block, js, flags=re.DOTALL)
    elif "/* BOFAST_DATA END */" in js:
        new = js.replace("/* BOFAST_DATA END */", "/* BOFAST_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret BOFAST_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    print(f"Injected ELDRE_DATA ({len(js_lit)} tegn). Bruksrater {payload['bruksrater']}.")
    print(f"Nord-Norge: 80+ {nn['a80'][0]} -> {nn['a80'][-1]}, demens {nn['demens'][0]} -> {nn['demens'][-1]}, "
          f"årsverk {nn['aarsverk']} -> {nn['behov2050']}; landet {landet['aarsverk']} -> {landet['behov2050']}")


if __name__ == "__main__":
    main()
