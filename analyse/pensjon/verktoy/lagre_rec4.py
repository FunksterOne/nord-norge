"""Validate a record JSON file (rec4/<nr>.json) against required keys. Usage: python -P verktoy/lagre_rec4.py rec4/<nr>.json"""
import sys, json
REQ = ["nr","navn","regnskapsaar","kilde_url","kilde_side","konsern_eller_kasse","leverandorer","brutto_pensjonsforpliktelse","pensjonsmidler","netto_forpliktelse","netto_inkl_aga","aarets_pensjonskostnad","innbetalt_premie","aarets_premieavvik","akkumulert_premieavvik","akkumulert_premieavvik_inkl_aga","amortisering_aar","reguleringspremie","egenkapitaltilskudd_klp","premiefond_bruk","forutsetninger","sykepleiere_separat","merknader"]
F = ["diskonteringsrente","avkastning","lonnsvekst","g_regulering","pensjonsregulering"]
r = json.load(open(sys.argv[1], encoding='utf-8'))
miss = [k for k in REQ if k not in r] + ['forutsetninger.'+k for k in F if k not in r.get('forutsetninger', {})]
extra = [k for k in r if k not in REQ]
print('OK' if not miss and not extra else f'MISSING {miss} EXTRA {extra}', r['nr'])
