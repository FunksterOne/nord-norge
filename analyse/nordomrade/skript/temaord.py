"""Temaord per 10 000 ord i de sju nordområdedokumentene 2006-2025."""
import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
K = Path(r"C:\Users\HalvardNordang\Github\nord-norge\analyse\nordomrade\kilder")
DOK = [("2006", "2006_nordomradestrategi"), ("2009", "2009_nye_byggesteiner"), ("2011", "2011_meld_st_7"),
       ("2014", "2014_nordkloden"), ("2017", "2017_nordomradestrategi"), ("2020", "2020_meld_st_9"), ("2025", "2025_norge_i_nord")]
# Ordstammer (regex, ordstart). Bevisst snevre for å unngå falske treff.
TEMA = {
    "sikkerhet": r"\b(sikkerhetspolit\w*|forsvar\w*|militær\w*|nato|alliert\w*|avskrekk\w*|totalforsvar\w*|suverenitet\w*)",
    "russland": r"\b(russland\w*|russisk\w*|russer\w*)",
    "klima_miljo": r"\b(klima\w*|miljø\w*|forurens\w*|naturmangfold\w*)",
    "petroleum_energi": r"\b(petroleum\w*|olje\w*|gass\w*|energi\w*|havvind\w*|vannkraft\w*|vindkraft\w*|kraft(?:produksjon|forsyning|overskudd|intensiv|nett|linj|krevende|marked|system|behov|underskudd)\w*)",
    "fiskeri_havbruk": r"\b(fiske\w*|fisk|havbruk\w*|sjømat\w*|oppdrett\w*|torsk\w*)",
    "mineraler": r"\b(mineral\w*|gruve\w*|bergverk\w*)",
    "reiseliv": r"\b(reiseliv\w*|turis\w*)",
    "forskning": r"\b(forskning\w*|forsker\w*|kunnskap\w*|universitet\w*)",
    "utdanning": r"\b(utdanning\w*|kompetanse\w*|skole\w*|studie\w*|studen\w*)",
    "befolkning": r"\b(befolkning\w*|innbygger\w*|bosetting\w*|fraflytting\w*|tilflytting\w*|flytting\w*|demograf\w*|folketall\w*)",
    "arbeidskraft": r"\b(arbeidskraft\w*|sysselsetting\w*|sysselsatt\w*|rekrutter\w*|arbeidsplass\w*|arbeidsmarked\w*)",
    "helse_eldre": r"\b(helse\w*|sykehus\w*|eldre\w*|omsorg\w*)",
    "samferdsel": r"\b(samferdsel\w*|infrastruktur\w*|veinett\w*|vegnett\w*|veier|veger|riksvei\w*|riksveg\w*|europavei\w*|europaveg\w*|vegvesen\w*|jernbane\w*|\w*banen|havn\w*|\w*havner?|flyplass\w*|lufthavn\w*|\w*tunnel\w*|bredbånd\w*)",
    "samisk": r"\b(samisk\w*|samene|samer|sameting\w*|samelov\w*|samepolitikk\w*|samekonvensjon\w*|urfolk\w*|reindrift\w*)",
    "svalbard": r"\b(svalbard\w*|longyearbyen\w*)",
    "beredskap": r"\b(beredskap\w*|redning\w*|kystvakt\w*)",
    "ungdom_kvinner": r"\b(ungdom\w*|unge|kvinne\w*|likestilling\w*)",
}
ut = {}
for aar, f in DOK:
    t = (K / f"{f}.txt").read_text(encoding="utf-8").lower()
    t = re.sub(r"-\n", "", t)
    n = len(re.findall(r"\w+", t))
    rad = {"ord": n}
    for k, rx in TEMA.items():
        rad[k] = round(1e4 * len(re.findall(rx, t)) / n, 1)
    ut[aar] = rad
json.dump(ut, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{'tema':18s}" + "".join(f"{a:>7s}" for a, _ in DOK))
print(f"{'ord':18s}" + "".join(f"{ut[a]['ord']:7d}" for a, _ in DOK))
for k in TEMA:
    print(f"{k:18s}" + "".join(f"{ut[a][k]:7.1f}" for a, _ in DOK))
