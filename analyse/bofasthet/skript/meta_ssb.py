"""Hent metadata (variabler, verdier) for SSB-tabeller via PxWebApi v0.

Bruk: python meta_ssb.py 10598 08377 ...
Lagrer kilder/meta/<tabell>.json og skriver en kort oversikt.
"""
import json, sys, time, urllib.request
from pathlib import Path

UT = Path(__file__).resolve().parents[1] / "kilder" / "meta"
UT.mkdir(parents=True, exist_ok=True)


def hent(url):
    req = urllib.request.Request(url, headers={"User-Agent": "affectum-nord-norge/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


for t in sys.argv[1:]:
    try:
        m = hent(f"https://data.ssb.no/api/v0/no/table/{t}")
    except Exception as e:
        print(f"## {t}: FEIL {e}")
        continue
    (UT / f"{t}.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"## {t}: {m.get('title')}")
    for v in m["variables"]:
        vals, txt = v["values"], v["valueTexts"]
        vis = list(zip(vals, txt))
        if len(vis) > 14:
            vis = vis[:7] + [("…", f"({len(vals)} verdier)")] + vis[-5:]
        print(f"  {v['code']} [{v['text']}] elim={v.get('elimination', False)}: " +
              "; ".join(f"{a}={b}" for a, b in vis))
    time.sleep(0.4)
