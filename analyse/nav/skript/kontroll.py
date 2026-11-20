"""Fase 2: kontroll av analyse/nav/data/nav_kommuner.json. Skriver analyse/nav/KONTROLL.md.

1. Sumkontroll: summen av kommunene mot NAVs publiserte fylkestall i de samme filene.
   Sammenlignes bare der inndelingen er lik: Nord-Norge samlet alle år, Finnmark alle år,
   Nordland fra 2020, Troms fra 2024 og Troms og Finnmark 2020–2023.
2. Dekning: kommune × kategori × periode (tall, prikket, brudd, beregnet).
3. Prikking: hvor mye årssnittet for helt ledige endres om de skjulte månedene (0–3 personer)
   settes til 0 eller 3.
4. Hopp: endring i kommunens andel fra år til år, utover fylkets endring.
5. Uføre: NAV september 2025 mot SSB 11715 (2025) som dashbordet bruker i dag.

Bruk: python analyse/nav/skript/kontroll.py   (kode 0 = ingen avvik i sumkontrollen)
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROT))
import fetch_nav as F  # noqa: E402

D = json.loads((ROT / "analyse/nav/data/nav_kommuner.json").read_text(encoding="utf-8"))
KOM, FYL = D["kommuner"], D["fylker"]
NAVN = D["navn"]
t = F.t
FYRE = [("54", r"troms og finnmark"), ("18", r"nordland"), ("55", r"troms"), ("56", r"finnmark")]
linjer = []
P = linjer.append


def fylke_av(r):
    if F.kode(r)[0]:
        return None
    lab = " ".join(t(x) for x in r[:4] if t(x) and F.tall(x) is None).lower()
    lab = re.sub(r"^(i alt|sum)\s+", "", lab)
    lab = re.sub(r"^\d\d\s+", "", lab)
    for k, n in FYRE:
        if re.match(rf"^{n}\b", lab) and not (k in ("55", "56") and "og" in lab.split()[:3]):
            return k
    return None


def publiserte(fil, ant_re, pst_re):
    """{(fylke, felt): {mnd: verdi}} fra fylkesrader i en månedsfil (fylke- og kommuneark)."""
    ut = {}
    for an, rader in F.ark(fil):
        al = an.lower()
        felt = "antall" if re.search(ant_re, al) else "pst" if re.search(pst_re, al) else None
        if not felt:
            continue
        hode = None
        for i, r in enumerate(rader):
            m = {j: F.MND.index(t(x).lower()) + 1 for j, x in enumerate(r) if t(x).lower() in F.MND}
            m.update({j: int(re.fullmatch(r"20\d\d(\d\d)(\.0)?", t(x)).group(1)) for j, x in enumerate(r)
                      if re.fullmatch(r"20\d\d(0[1-9]|1[0-2])(\.0)?", t(x))})
            if len(m) >= 2:
                hode = m
                continue
            fy = fylke_av(r) if hode else None
            if not fy:
                continue
            rad = r
            if sum(F.tall(x) is not None for x in r) < 2 and i + 1 < len(rader):  # overskrift + «I alt»
                nr = rader[i + 1]
                if re.fullmatch(r"i alt", " ".join(t(x) for x in nr[:4] if t(x) and F.tall(x) is None).lower()):
                    rad = nr
            v = {mn: F.tall(rad[c]) for c, mn in hode.items() if c < len(rad) and F.tall(rad[c]) is not None}
            if v and (fy, felt) not in ut:
                ut[(fy, felt)] = v
    return ut


def sammenlign(navn, aar, pub, egen_fylke):
    """Teller avvik i antall (må være likt) og største avvik i prosent (avrunding)."""
    avvik, maks_pp, n = [], 0.0, 0
    global ANSLAG_MAKS, ANSLAG_N
    sett = [("18",), ("54",), ("55",), ("56",)]
    for (fy,) in sett:
        if aar < 2020 and fy != "56":
            continue
        if fy == "55" and aar < 2024:
            continue
        if fy == "54" and not (2020 <= aar <= 2023):
            continue
        if fy == "18" and aar < 2020:
            continue
        mine = egen_fylke(fy)
        for felt in ("antall", "pst"):
            for m, v in pub.get((fy, felt), {}).items():
                e = mine.get(felt, {}).get(m)
                if e is None:
                    continue
                n += 1
                if m in mine.get("anslatt", set()):
                    if felt == "antall":
                        ANSLAG_MAKS = max(ANSLAG_MAKS, abs(e - v))
                        ANSLAG_N += 1
                    else:
                        ANSLAG_PP[0] = max(ANSLAG_PP[0], abs(e - v))
                    continue
                if felt == "antall" and abs(e - v) > 0.5:
                    avvik.append(f"{navn} {aar}/{m} fylke {fy} antall: sum {e:g} | NAV {v:g}")
                if felt == "pst":
                    maks_pp = max(maks_pp, abs(e - v))
    # Nord-Norge samlet (lik inndeling alle år)
    nn = egen_fylke("NN")
    for m, e in nn.get("antall", {}).items():
        deler = [pub.get((fy, "antall"), {}).get(m) for fy in (("18", "55", "56") if aar >= 2024 else ("18", "54") if aar >= 2020 else ("18", "55", "56"))]
        if aar < 2020:  # gamle Troms (19) heter «Troms» i filene
            deler = [pub.get((fy, "antall"), {}).get(m) for fy in ("18", "55", "56")]
        if e is None or any(d is None for d in deler):
            continue
        n += 1
        if m in nn.get("anslatt", set()):
            ANSLAG_MAKS = max(ANSLAG_MAKS, abs(sum(deler) - e))
            ANSLAG_N += 1
            continue
        if abs(sum(deler) - e) > 0.5:
            avvik.append(f"{navn} {aar}/{m} Nord-Norge antall: sum {e:g} | NAV {sum(deler):g}")
    return avvik, maks_pp, n


def slaa_54(a, b):
    """Troms og Finnmark = 55 + 56 (antall summeres, andel via nevner = antall/andel)."""
    ut = {"antall": {}, "pst": {}, "anslatt": a.get("anslatt", set()) | b.get("anslatt", set())}
    for m in set(a["antall"]) & set(b["antall"]):
        ut["antall"][m] = a["antall"][m] + b["antall"][m]
        if a["pst"].get(m) and b["pst"].get(m):
            ut["pst"][m] = ut["antall"][m] / (a["antall"][m] / a["pst"][m] + b["antall"][m] / b["pst"][m])
    return ut


ANSLAG_MAKS, ANSLAG_N, ANSLAG_PP = 0.0, 0, [0.0]


def fylke_mnd(kat, aar):
    def f(fy):
        if fy == "54":
            return slaa_54(f("55"), f("56"))
        r = FYL[fy].get(kat, {}).get(str(aar), {})
        mnd = r.get("mnd", {})
        return {"antall": {int(m): v[0] for m, v in mnd.items() if isinstance(v[0], float)},
                "pst": {int(m): v[1] for m, v in mnd.items() if isinstance(v[1], float)},
                "anslatt": {int(m) for m in r.get("anslatt_mnd", [])}}
    return f


# ---------------------------------------------------------------- 1. sumkontroll
P("# Kontroll av NAV-data for de 80 kommunene (fase 2)\n")
P(f"Generert av `analyse/nav/skript/kontroll.py` fra `nav_kommuner.json`.\n")
P("## 1. Summen av kommunene mot NAVs fylkestall\n")
P("Sammenlignet der inndelingen er lik. Antall skal være likt. For prosent er avviket "
  "avrunding, fordi NAV oppgir fylkesandelen med én desimal og vi regner den av kommunene.\n")
P("| Kategori | Sammenligninger | Avvik i antall | Største avvik i prosent (pp) |")
P("|---|---|---|---|")
alle_avvik = []
kilder = D["meta"]["kilder"]
for kat, ant_re, pst_re in (("helt_ledige", r"antall", r"prosent"), ("aap", r"antall", r"andel"), ("nedsatt", r"antall", r"andel")):
    n_tot, av_tot, pp = 0, [], 0.0
    for linje in kilder[kat]:
        m = re.match(r"^(20\d\d): (.+)$", linje)
        if not m:
            continue
        aar, fn = int(m.group(1)), m.group(2)
        fil = next((F.K / kat).glob(fn.replace("[", "?").replace("]", "?")))
        pub = publiserte(fil, ant_re, pst_re)
        av, mp, n = sammenlign(kat, aar, pub, fylke_mnd(kat, aar))
        n_tot += n
        av_tot += av
        pp = max(pp, mp)
    alle_avvik += av_tot
    P(f"| {kat} | {n_tot} | {len(av_tot)} | {pp:.2f} |".replace(".", ","))

# Uføre: fylkesrader i den valgte utgaven for hver tellingsdato
n_tot, av_u, pp = 0, [], 0.0
for linje in kilder["ufore"]:
    dt, fn = linje.split(": ", 1)
    fn = fn.split(" (aldersstandardisert")[0]
    aar = int(dt[:4])
    fil = next((F.K / "ufore").glob(fn.replace("[", "?").replace("]", "?")))
    pub = {}
    for an, rader in F.ark(fil):
        andel = "andel" in an.lower()
        hode = None
        for r in rader:
            d = [(j, F.dato_fra(x)) for j, x in enumerate(r) if F.dato_fra(x) and F.tall(x) is None]
            if len(d) >= 2:
                sett, hode = defaultdict(int), []
                for j, x in d:
                    hode.append((j, x, "pst" if andel else ("antall", "pst", "astd")[min(sett[x], 2)]))
                    sett[x] += 1
                continue
            fy = fylke_av(r) if hode else None
            if fy:
                for j, x, felt in hode:
                    if x == dt and j < len(r) and F.tall(r[j]) is not None:
                        pub.setdefault((fy, felt), {}).setdefault(0, F.tall(r[j]))

    def fu(fy, dt=dt):
        if fy == "54":
            return slaa_54(fu("55"), fu("56"))
        r = FYL[fy].get("ufore", {}).get(dt, {})
        return {"antall": {0: r["antall"]} if isinstance(r.get("antall"), float) else {},
                "pst": {0: r["pst"]} if isinstance(r.get("pst"), float) else {}}
    # andeler i brøk (0,13) i én utgave
    for k in list(pub):
        if k[1] == "pst" and pub[k][0] < 1:
            pub[k][0] *= 100
    av, mp, n = sammenlign("ufore", aar, pub, fu)
    n_tot += n
    av_u += [a.replace("/0", " " + dt) for a in av]
    pp = max(pp, mp)
# Kjent avvik i NAVs egen fil: Troms-kommunene summerer til 11 297, NAVs fylkessum er 11 298.
KJENT = {"ufore 2017 2017-12 Nord-Norge antall: sum 35624 | NAV 35625"}
kjente = [a for a in av_u if a in KJENT]
av_u = [a for a in av_u if a not in KJENT]
alle_avvik += av_u
P(f"| ufore | {n_tot} | {len(av_u)} | {pp:.2f} |".replace(".", ","))
P("")
P(f"I {ANSLAG_N} sammenligninger inneholder fylkessummen prikkede kommuner, telt som 1,5. "
  f"Største avvik fra NAVs fylkestall er da {ANSLAG_MAKS:g} personer og "
  + f"{ANSLAG_PP[0]:.2f}".replace(".", ",") + " prosentpoeng. Disse månedene er merket `anslatt_mnd` i dataene og regnes ikke som avvik.\n")
if kjente:
    P("Kjent avvik i NAVs egen fil (ikke regnet som feil): " + "; ".join(kjente) +
      ". Troms-kommunene i utgaven for desember 2019 summerer til 11 297, mens NAVs fylkessum er 11 298.\n")
if alle_avvik:
    P("Avvik:\n")
    for a in alle_avvik[:60]:
        P(f"- {a}")
    P("")

# ---------------------------------------------------------------- 2. dekning
P("## 2. Dekning per kategori og år\n")
P("Antall kommuner av 80 med tall for hele perioden, med prikkede måneder, med brudd "
  "(Narvik og Hamarøy) og med beregnede tall (sammenslåing uten NAVs omregning).\n")
P("| Kategori | Periode | Med tall | Prikket (minst én måned) | Brudd | Beregnet |")
P("|---|---|---|---|---|---|")
dekning_detalj = defaultdict(list)
for kat in ("helt_ledige", "aap", "nedsatt", "ufore", "pensjon"):
    perioder = sorted({p for k in KOM for p in KOM[k].get(kat, {})})
    for p in perioder:
        if kat == "ufore" and not (p.endswith("-12") or p in ("2025-09", "2026-09")):
            continue
        med = prikk = brudd = ber = 0
        for k in KOM:
            r = KOM[k].get(kat, {}).get(p)
            if not r:
                continue
            if "brudd" in r:
                brudd += 1
                continue
            if r.get("tegn"):
                prikk += 1
                dekning_detalj[(kat, p)].append(NAVN.get(k, k))
            if r.get("beregnet"):
                ber += 1
            v = r.get("pst") if kat != "pensjon" else r.get("minstepensjon")
            if v is not None:
                med += 1
        P(f"| {kat} | {p} | {med} | {prikk} | {brudd} | {ber} |")
P("")

# ---------------------------------------------------------------- 3. prikking
P("## 3. Prikking i helt ledige\n")
P("NAV erstatter tall under 4 med «*». For hvert kommuneår med prikkede måneder er "
  "årssnittet regnet på tre måter: av de publiserte månedene (slik `fetch_nav.py` gjør), "
  "med de prikkede satt til 0 og med de prikkede satt til 3. Prosent er antall delt på "
  "arbeidsstyrken, anslått som median(antall/andel) i året.\n")
P("Fra 20.11.2026 regner `fetch_nav.py` prikkede måneder som 1,5 (kolonnen «Brukt»), og viser ikke "
  "snitt når mer enn halvparten av månedene er prikket.\n")
P("| Kommune | År | Prikkede måneder | Publiserte måneder (%) | Prikket = 0 (%) | Prikket = 3 (%) | Brukt (%) |")
P("|---|---|---|---|---|---|---|")
prikk_rader = []
for k in F.KODER:
    for aar, r in KOM[k].get("helt_ledige", {}).items():
        mnd = r.get("mnd", {})
        pr = [m for m, v in mnd.items() if v[0] == "*"]
        if not pr:
            continue
        ant = {m: v[0] for m, v in mnd.items() if isinstance(v[0], float)}
        pst = {m: v[1] for m, v in mnd.items() if isinstance(v[1], float)}
        nev = F.nevner(ant, pst)
        pub = statistics.mean(pst.values()) if pst else None  # bare publiserte måneder
        lo = hi = None
        if nev:
            lo = (sum(ant.values()) + 0 * len(pr)) / len(mnd) / nev * 100
            hi = (sum(ant.values()) + 3 * len(pr)) / len(mnd) / nev * 100
        prikk_rader.append((k, aar, len(pr), len(mnd), pub, lo, hi, r.get("pst")))
fmt = lambda x: "–" if x is None else f"{x:.2f}".replace(".", ",")
for k, aar, n, nm, pub, lo, hi, brukt in prikk_rader:
    P(f"| {NAVN.get(k, k)} | {aar} | {n} av {nm} | {fmt(pub)} | {fmt(lo)} | {fmt(hi)} | {fmt(brukt)} |")
over = [x for x in prikk_rader if x[4] is not None and x[6] is not None and (x[4] - x[5]) > 0.3]
P(f"\n{len(prikk_rader)} kommuneår har prikkede måneder. I {len(over)} av dem ligger snittet av de "
  "publiserte månedene mer enn 0,3 prosentpoeng over snittet med de prikkede satt til 0.\n")

# ---------------------------------------------------------------- 4. hopp
P("## 4. Store endringer fra år til år\n")
P("Endring i kommunens andel minus endringen i fylket. Terskler: helt ledige og AAP 1,5 pp, "
  "nedsatt arbeidsevne 2 pp, uføre 1,5 pp (desember til desember). Nevneren viser hvor mange "
  "personer andelen regnes av; små nevnere gir store utslag.\n")
P("| Kategori | Kommune | Fra–til | Kommune (pp) | Fylke (pp) | Nevner | Merknad |")
P("|---|---|---|---|---|---|---|")
TERSKEL = {"helt_ledige": 1.5, "aap": 1.5, "nedsatt": 2.0, "ufore": 1.5}
hopp = []
for kat, ter in TERSKEL.items():
    for k in F.KODER:
        s = KOM[k].get(kat, {})
        fy = FYL[k[:2]].get(kat, {})
        nokler = sorted(p for p in s if (kat != "ufore" or p.endswith("-12")))
        for a, b in zip(nokler, nokler[1:]):
            ra, rb = s[a], s[b]
            if ra.get("pst") is None or rb.get("pst") is None:
                continue
            dk = rb["pst"] - ra["pst"]
            fa, fb = fy.get(a, {}).get("pst"), fy.get(b, {}).get("pst")
            df = (fb - fa) if fa is not None and fb is not None else 0.0
            if abs(dk - df) > ter:
                mnd = rb.get("mnd", {})
                ant = {m: v[0] for m, v in mnd.items() if isinstance(v[0], float)}
                pst = {m: v[1] for m, v in mnd.items() if isinstance(v[1], float)}
                nev = F.nevner(ant, pst) if mnd else (rb["antall"] / rb["pst"] * 100 if rb.get("antall") and rb["pst"] else None)
                merk = []
                if ra.get("beregnet") != rb.get("beregnet"):
                    merk.append("bytte fra beregnet til NAV-tall")
                if kat == "aap" and a == "2015":
                    merk.append("årssnitt → månedssnitt")
                hopp.append((kat, k, a, b, dk, df, nev, "; ".join(merk)))
for kat, k, a, b, dk, df, nev, merk in sorted(hopp, key=lambda x: -abs(x[4] - x[5])):
    P(f"| {kat} | {NAVN.get(k, k)} | {a}–{b} | {dk:+.2f} | {df:+.2f} | {'–' if not nev else f'{nev:,.0f}'.replace(',', ' ')} | {merk} |".replace(".", ","))
P(f"\n{len(hopp)} endringer over terskelen.\n")

# ---------------------------------------------------------------- 5. NAV mot SSB (uføre)
P("## 5. Uføreandel: NAV september 2025 mot SSB 11715 (2025)\n")
dj = (ROT / "assets/data.js").read_text(encoding="utf-8")
m = re.search(r"ARBEID_DATA\s*=\s*(\{.*?\});?\s*\n", dj, re.S)
ssb = json.loads(m.group(1))["kommuner"] if m else {}
diff = []
for k in F.KODER:
    n = KOM[k]["ufore"].get("2025-09", {}).get("pst")
    s = ssb.get(k, {}).get("uforePct18_67")
    if n is not None and s is not None:
        diff.append((n - s, k, n, s))
if diff:
    d = [x[0] for x in diff]
    P(f"{len(diff)} kommuner. NAV minus SSB: median {statistics.median(d):+.2f} pp, "
      f"fra {min(d):+.2f} til {max(d):+.2f} pp.\n".replace(".", ","))
    P("| Kommune | NAV sept. 2025 (%) | SSB 2025 (%) | Forskjell (pp) |")
    P("|---|---|---|---|")
    for x in sorted(diff)[:5] + sorted(diff)[-5:]:
        P(f"| {NAVN.get(x[1], x[1])} | {x[2]:.2f} | {x[3]:.1f} | {x[0]:+.2f} |".replace(".", ","))
    P("")

(ROT / "analyse/nav/KONTROLL.md").write_text("\n".join(linjer) + "\n", encoding="utf-8")
print("\n".join(linjer[:40]))
print("...")
print(f"Sumavvik: {len(alle_avvik)}; prikkede kommuneår: {len(prikk_rader)}; hopp: {len(hopp)}")
sys.exit(1 if alle_avvik else 0)
