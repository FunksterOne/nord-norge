"""Henter figurdata fra SSB-artikkelen «Mest bruk av vikarbyrå ved sykehusene i Nord-Norge» (15.11.2024).
Ingen statistikkbanktabell finnes; tallene ligger som Highcharts-konfigurasjon i siden.
Kjør: python -X utf8 innleie_ssb_artikkel.py  -> data/innleie_ssb_2023.json"""
import json, os, re, html
from ssb import RAA, UT, hent
URL = "https://www.ssb.no/helse/helsetjenester/artikler/mest-bruk-av-vikarbyra-ved-sykehusene-i-nord-norge"
t = hent(URL, "ssb_artikkel_vikarbyra.html").decode("utf-8")
t = html.unescape(t)
fig = []
for m in re.finditer(r'"config":\{"categories":(\[[^\]]*\]),"series":\[', t):
    rest = t[m.end():m.end() + 20000]
    slutt = rest.find('],"accessibility"')
    ser = [{"navn": n, "data": json.loads(d)} for n, d in re.findall(r'"name":"([^"]*)","data":(\[[^\]]*\])', rest[:slutt])]
    fig.append({"kategorier": json.loads(m.group(1)), "serier": ser})
json.dump({"kilde": URL, "publisert": "2024-11-15", "hentet": "2026-10-29",
           "merknad": "Figurdata fra artikkelen; grunnlag er helseforetakenes resultatregnskap rapportert til SSB (artskontoer). Ikke i Statistikkbanken.",
           "figurer": fig}, open(os.path.join(UT, "innleie_ssb_2023.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in fig:
    print(f["kategorier"][:12], [(s["navn"][:80], s["data"]) for s in f["serier"]])
