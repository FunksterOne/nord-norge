"""Trekk ut figurdata (Highcharts-konfig) fra SSB-artikler (Enonic/react4xp).

Bruk: python ssb_figurdata.py fil.html [fil2.html ...]
Skriver figurtittel, kategorier og serier, og lagrer <fil>.figurer.json ved siden av.
"""
import json, re, sys
from pathlib import Path


def figurer(html):
    ut = []
    for m in re.finditer(r'<script data-react4xp-app-name="mimir"[^>]*type="application/json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        hc = d.get("props", {}).get("highcharts")
        if not hc:
            continue
        for h in hc:
            c = h.get("config", {})
            tittel = (c.get("title") or {}).get("text") or h.get("contentKey")
            kat = c.get("categories") or (c.get("xAxis") or {}).get("categories")
            if isinstance(c.get("xAxis"), list):
                kat = kat or c["xAxis"][0].get("categories")
            ser = [{"name": s.get("name"), "data": s.get("data")} for s in c.get("series", [])]
            ut.append({"tittel": tittel, "kategorier": kat, "serier": ser,
                       "kilde": (c.get("credits") or {}).get("text")})
    return ut


for f in sys.argv[1:]:
    p = Path(f)
    figs = figurer(p.read_text(encoding="utf-8"))
    p.with_suffix(".figurer.json").write_text(json.dumps(figs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"##### {p.name}: {len(figs)} figurer")
    for g in figs:
        print("\n#", g["tittel"])
        print("  kategorier:", g["kategorier"])
        for s in g["serier"]:
            print("  ", s["name"], ":", s["data"])
