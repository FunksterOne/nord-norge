import json, os
k = json.load(open('kommuner.json', encoding='utf-8'))[2]
out = 'regnskap_gruppe3.json'
if os.path.exists(out):
    print('exists'); raise SystemExit
lst = []
for x in k:
    lst.append({
        "nr": x["nr"], "navn": x["navn"], "regnskapsaar": None, "kilde_url": None, "kilde_side": None,
        "konsern_eller_kasse": None, "leverandorer": [],
        "brutto_pensjonsforpliktelse": None, "pensjonsmidler": None, "netto_forpliktelse": None,
        "netto_inkl_aga": None, "aarets_pensjonskostnad": None, "innbetalt_premie": None,
        "aarets_premieavvik": None, "akkumulert_premieavvik": None, "akkumulert_premieavvik_inkl_aga": None,
        "amortisering_aar": None, "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": None,
        "forutsetninger": {"diskonteringsrente": None, "avkastning": None, "lonnsvekst": None, "g_regulering": None, "pensjonsregulering": None},
        "sykepleiere_separat": None, "merknader": "ikke behandlet ennå"})
json.dump(lst, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', len(lst))
