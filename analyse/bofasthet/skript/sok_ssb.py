"""Søk i SSBs Statistikkbank (PxWebApi v0) etter tabeller om bofasthet/botid.

Bruk: python sok_ssb.py "ord1" "ord2" ...
Skriver treff (tabellnr, tittel, periode) til stdout og lagrer rå JSON i kilder/sok/.
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

UT = Path(__file__).resolve().parents[1] / "kilder" / "sok"
UT.mkdir(parents=True, exist_ok=True)


def hent(url):
    req = urllib.request.Request(url, headers={"User-Agent": "affectum-nord-norge/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


for q in sys.argv[1:]:
    url = "https://data.ssb.no/api/v0/no/table/?query=" + urllib.parse.quote(q)
    try:
        res = hent(url)
    except Exception as e:
        print(f"## {q}: FEIL {e}")
        continue
    (UT / (q.replace(" ", "_").replace("*", "") + ".json")).write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"## {q}: {len(res)} treff")
    for t in res:
        print(f"  {t.get('id')}  {t.get('title')}  [{t.get('published','')[:10]}]")
    time.sleep(0.5)
