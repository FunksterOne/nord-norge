"""Merge one municipality record into regnskap_gruppe2.json.
Usage: python -P verktoy2/lagre.py <record.json>   (record has 'nr'; fields are merged over template)
       python -P verktoy2/lagre.py --init
"""
import sys, json, os, copy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "regnskap_gruppe2.json")

TEMPLATE = {
    "nr": None, "navn": None, "regnskapsaar": None, "kilde_url": None, "kilde_side": None,
    "konsern_eller_kasse": None, "leverandorer": [],
    "brutto_pensjonsforpliktelse": None, "pensjonsmidler": None, "netto_forpliktelse": None,
    "netto_inkl_aga": None, "aarets_pensjonskostnad": None, "innbetalt_premie": None,
    "aarets_premieavvik": None, "akkumulert_premieavvik": None,
    "akkumulert_premieavvik_inkl_aga": None, "amortisering_aar": None,
    "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": None,
    "forutsetninger": {"diskonteringsrente": None, "avkastning": None, "lonnsvekst": None,
                        "g_regulering": None, "pensjonsregulering": None},
    "sykepleiere_separat": None, "merknader": "",
}
NAVN = [("1837", "Meløy"), ("1838", "Gildeskål"), ("1839", "Beiarn"), ("1840", "Saltdal"),
        ("1841", "Fauske"), ("1845", "Sørfold"), ("1848", "Steigen"), ("1851", "Lødingen"),
        ("1853", "Evenes"), ("1856", "Røst"), ("1857", "Værøy"), ("1859", "Flakstad"),
        ("1860", "Vestvågøy"), ("1865", "Vågan"), ("1866", "Hadsel"), ("1867", "Bø"),
        ("1868", "Øksnes"), ("1870", "Sortland"), ("1871", "Andøy"), ("1874", "Moskenes")]


def load():
    with open(OUT, encoding="utf-8") as f:
        return json.load(f)


def save(d):
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT)


if sys.argv[1] == "--init":
    if os.path.exists(OUT):
        print("exists, not overwriting")
    else:
        d = []
        for nr, navn in NAVN:
            r = copy.deepcopy(TEMPLATE)
            r["nr"], r["navn"] = nr, navn
            r["merknader"] = "Ikke undersøkt ennå."
            d.append(r)
        save(d)
        print("init ok")
    sys.exit()

with open(sys.argv[1], encoding="utf-8") as f:
    rec = json.load(f)
d = load()
for i, r in enumerate(d):
    if r["nr"] == rec["nr"]:
        new = copy.deepcopy(TEMPLATE)
        new.update({k: v for k, v in r.items() if k in TEMPLATE})
        for k, v in rec.items():
            if k == "forutsetninger":
                new["forutsetninger"] = {**TEMPLATE["forutsetninger"], **v}
            else:
                new[k] = v
        b, m = new["brutto_pensjonsforpliktelse"], new["pensjonsmidler"]
        if new["netto_forpliktelse"] is None and b is not None and m is not None:
            new["netto_forpliktelse"] = b - m
        d[i] = new
        save(d)
        print("saved", rec["nr"], new["navn"])
        break
else:
    print("nr not found", rec["nr"])
