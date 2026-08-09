#!/usr/bin/env python3
"""Beregner boligbehov per kommune (BB-KVOTE-modellen) og injiserer BEHOV_DATA
i assets/data.js.

Modell (dokumentert i metode.html):
  behov(t) = husholdninger(1.1.t+1) - husholdninger(1.1.t) + erstatningsbehov
  husholdninger(t) = folketall(t) x andel i privathusholdning / husholdningsstorrelse(t)

  - Folketall: DATA.proj-banene (SSB 14746 MMMM/lav/hoey + TF-ATTR), 2026-2050.
  - Husholdningsstorrelse: SSB 09747 (personer per privathusholdning), skjotet
    til 2024-grenser. To kvotebaner: KONSTANT (2025-niva) og TREND (linear
    trend 2011-2025, dempet 50 %, gulv 1,70).
  - Andel i privathusholdning: kalibrert mot 1.1.2025 (09747 mot folketall).
  - Erstatningsbehov: gjennomsnittlig aarlig registrert avgang av boliger
    2016-2025 (BOLIG_DATA/SSB 10784). Ikke-registrert avgang kommer i tillegg;
    modellen er saann sett forsiktig.

Resultat per kommune: hoved-serien (MMMM x trend), lo/hi (spennet over
8 kombinasjoner: 4 baner x 2 kvoter) og vindussnitt 2026-2030 / 2031-2040 /
2041-2049. Fylker og landsdel beregnes paa aggregatniva (samme modell).
Kalibrering mot Prognosesenteret for kbnn (aarlig behov 2026-2030) lagres i meta.
"""
import json
import re
import datetime
from pathlib import Path

from fetch_bolig import get, post_ssb, celler, bygg_familier, CODES, fylke

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"

AAR_HH = [str(a) for a in range(2005, 2026)]
GULV, TAK = 1.70, 3.50
DEMPING = 0.5
TRENDAAR = list(range(2011, 2026))

# Prognosesenterets anslag (kbnn, aug. 2026): aarlig boligbehov 2026-2030
PS_REF = {"Nordland": 454, "Troms": 755, "Finnmark": 267,
          "5501": 431, "1804": 114, "5622": 12}


def hent_hh(alle_koder):
    meta = get("https://data.ssb.no/api/v0/no/table/09747")
    reg_ok = set(next(v for v in meta["variables"] if v["code"] == "Region")["values"])
    q = [
        {"code": "Region", "selection": {"filter": "item",
                                         "values": [k for k in alle_koder if k in reg_ok]}},
        {"code": "ContentsCode", "selection": {"filter": "item",
                                               "values": ["Husholdniger", "Personer"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": AAR_HH}},
    ]
    d = post_ssb("09747", q)
    hush, pers = {}, {}
    for co, v in celler(d):
        if v is None:
            continue
        m = hush if co["ContentsCode"] == "Husholdniger" else pers
        key = (co["Region"], co["Tid"])
        m[key] = m.get(key, 0) + v
    return hush, pers


def trend_hhsize(serie):
    """Linear OLS paa 2011-2025, dempet; returnerer (siste, aarlig endring)."""
    pts = [(a, serie[str(a)]) for a in TRENDAAR if serie.get(str(a))]
    siste = serie.get("2025") or pts[-1][1]
    if len(pts) < 8:
        return siste, 0.0
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    return siste, (sxy / sxx) * DEMPING if sxx else 0.0


def behovsserie(pop, andel_priv, hh0, slope, ersta):
    """behov(t) for t=2026..2049 gitt folketallsbane pop[0..24] (2026..2050)."""
    hh = [max(GULV, min(TAK, hh0 + slope * i)) for i in range(len(pop))]
    hus = [pop[i] * andel_priv / hh[i] for i in range(len(pop))]
    return [round(hus[i + 1] - hus[i] + ersta) for i in range(len(pop) - 1)]


def main():
    js = DATA_JS.read_text(encoding="utf-8")
    linjer = js.split("\n")
    idx = next(i for i, l in enumerate(linjer) if l.startswith("const DATA = "))
    DATA = json.loads(linjer[idx][len("const DATA = "):].rstrip(";"))
    proj = DATA["proj"]
    assert proj["meta"]["tabell"] == "14746", "kjoer fetch_framskriving.py foerst"
    m = re.search(r"const BOLIG_DATA = (.*?);\n/\* BOLIG_DATA END", js, re.DOTALL)
    assert m, "kjoer fetch_bolig.py foerst"
    BOLIG = json.loads(m.group(1))

    print("Bygger skjotetabell...", flush=True)
    familier, split_i_nord = bygg_familier()
    alle_koder = sorted({k for fam in familier.values() for k in fam} | set(split_i_nord))
    print("Henter 09747 (husholdninger, personer) 2005-2025...", flush=True)
    hush, pers = hent_hh(alle_koder)

    def hh_serier(fam):
        h = {a: sum(hush.get((k, a), 0) for k in fam) for a in AAR_HH}
        p = {a: sum(pers.get((k, a), 0) for k in fam) for a in AAR_HH}
        return {a: (p[a] / h[a]) for a in AAR_HH if h[a]}, h, p

    def ersta_for(nk=None, niv=None):
        """Snitt aarlig avgang 2016-2025 fra BOLIG_DATA (kvartalsserie)."""
        rec = BOLIG["kommuner"][nk] if nk else BOLIG[niv[0]][niv[1]] if niv[0] == "fylker" else BOLIG["landsdel"]
        tq = BOLIG["av_quarters"]
        aar = {}
        for i, t in enumerate(tq):
            aar.setdefault(t[:4], []).append(rec["av"][i])
        vals = [sum(v) for a, v in aar.items() if "2016" <= a <= "2025" and len(v) == 4]
        return round(sum(vals) / len(vals)) if vals else 0

    BANER = ["main", "low", "high", "tfattr"]
    KVOTER = ["konst", "trend"]

    def beregn(pop_baner, fam, folketall_2025, nk=None, niv=None):
        hhs, h, p = hh_serier(fam)
        if not hhs:
            return None
        hh0, slope = trend_hhsize(hhs)
        pers2025 = p.get("2025", 0)
        andel = min(1.0, pers2025 / folketall_2025) if folketall_2025 else 0.97
        ersta = ersta_for(nk, niv)
        combos = {}
        for b in BANER:
            for kv in KVOTER:
                combos[f"{b[0]}_{kv[:2]}"] = behovsserie(
                    pop_baner[b], andel, hh0, slope if kv == "trend" else 0.0, ersta)
        hoved = combos["m_tr"]
        n = len(hoved)
        lo = [min(c[i] for c in combos.values()) for i in range(n)]
        hi = [max(c[i] for c in combos.values()) for i in range(n)]
        def vindu(serie):
            deler = [serie[0:5], serie[5:15], serie[15:]]
            return [round(sum(d) / len(d)) for d in deler]
        return {"hoved": hoved, "lo": lo, "hi": hi,
                "w": {k: vindu(c) for k, c in combos.items()},
                "ersta": ersta, "hh25": round(hh0, 2),
                "slope": round(slope, 4), "andel": round(andel, 3)}

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "years": list(range(2026, 2050)),
        "modell": "BB-KVOTE v1: behov = endring i husholdninger + registrert avgang. "
                  "Baner: SSB 14746 MMMM/lav/hoey + TF-ATTR; kvoter: konstant og "
                  "dempet trend (09747, 2011-2025).",
        "kommuner": {}, "fylker": {}, "landsdel": None, "kalibrering": {},
    }

    for k in CODES:
        o = proj["kommuner"][k]
        pop = {b: o[b] for b in BANER}
        f2025 = DATA["kommuner"][k]["hist"].get("2025")
        r = beregn(pop, familier[k], f2025, nk=k)
        payload["kommuner"][k] = r

    for fn in ["Nordland", "Troms", "Finnmark"]:
        mine = [k for k in CODES if fylke(k) == fn]
        fam = [c for k in mine for c in familier[k]] + \
              [o for o, f in split_i_nord.items() if f == fn]
        pop = {b: [sum(proj["kommuner"][k][b][i] for k in mine) for i in range(25)]
               for b in BANER}
        f2025 = sum(DATA["kommuner"][k]["hist"].get("2025", 0) for k in mine)
        payload["fylker"][fn] = beregn(pop, fam, f2025, niv=("fylker", fn))

    fam_alle = [c for k in CODES for c in familier[k]] + list(split_i_nord)
    pop = {b: [sum(proj["kommuner"][k][b][i] for k in CODES) for i in range(25)]
           for b in BANER}
    f2025 = sum(DATA["kommuner"][k]["hist"].get("2025", 0) for k in CODES)
    payload["landsdel"] = beregn(pop, fam_alle, f2025, niv=("landsdel", None))

    # --- kalibrering mot Prognosesenteret --------------------------------
    print("\nKalibrering mot Prognosesenteret (aarlig behov 2026-2030):")
    for navn, ps in PS_REF.items():
        r = payload["fylker"].get(navn) or payload["kommuner"].get(navn)
        vaar = r["w"]["m_tr"][0]
        lo5 = min(r["w"][c][0] for c in r["w"])
        hi5 = max(r["w"][c][0] for c in r["w"])
        label = navn if navn in payload["fylker"] else DATA["kommuner"][navn]["navn"]
        payload["kalibrering"][navn] = {"ps": ps, "bb": vaar, "lo": lo5, "hi": hi5}
        print(f"  {label}: BB-KVOTE {vaar} (spenn {lo5}-{hi5}) mot PS {ps}")
    ld = payload["landsdel"]
    print(f"  Nord-Norge: BB-KVOTE {ld['w']['m_tr'][0]} "
          f"(spenn {min(ld['w'][c][0] for c in ld['w'])}-{max(ld['w'][c][0] for c in ld['w'])}) mot PS 1476")
    payload["kalibrering"]["landsdel"] = {"ps": 1476, "bb": ld["w"]["m_tr"][0],
                                          "lo": min(ld["w"][c][0] for c in ld["w"]),
                                          "hi": max(ld["w"][c][0] for c in ld["w"])}

    # --- injiser ---------------------------------------------------------
    lit = "const BEHOV_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = "/* BEHOV_DATA BEGIN */\n" + lit + "\n/* BEHOV_DATA END */"
    if "/* BEHOV_DATA BEGIN */" in js:
        js = re.sub(r"/\* BEHOV_DATA BEGIN \*/.*?/\* BEHOV_DATA END \*/", block, js, flags=re.DOTALL)
    else:
        anchor = "/* BOLIG_DATA END */"
        js = js.replace(anchor, anchor + "\n" + block)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"\nInjisert BEHOV_DATA ({len(lit)} tegn) i {DATA_JS}")


if __name__ == "__main__":
    main()
