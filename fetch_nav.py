#!/usr/bin/env python3
"""NAV-statistikk per kommune for de 80 kommunene i Nord-Norge (fase 1 i analyse/PLAN-NAV.md).

Leser NAVs kommunetabeller i analyse/nav/kilder/<kategori>/ (landsfiler, lastet ned i
Lødingen-arbeidet, holdes utenfor git) og skriver analyse/nav/data/nav_kommuner.json.

Kategorier
  helt_ledige    HL060, månedstall 2012–2026 (antall og prosent av arbeidsstyrken)
  aap            AAP 2010–2015 (årsgjennomsnitt), juli–september 2015, AAP155 2016–2026 (måned)
  nedsatt        september 2015, NED155 2016–2026 (måned)
  ufore          kommunetabeller 2011–2026 (tellingsdatoer, antall og andel 18–67 år)
  alderspensjon  PST011 (september 2016–2026, dagens kommuner)
  minstepensjon  PST062 (september 2016–2026, dagens kommuner; NAV: korrekt fra september 2020)
  Kontantstøtte er utelatt (avgjort 20.11.2026): fylkestall bare for seks ulike tidspunkter,
  skiftende mål mellom utgavene og brudd ved reformen i august 2024.

Kommunenøkkel
  SSB Klass 131 (analyse/nav/data/klass131_endringer.json). Gamle koder føres fram til
  gjeldende kode. Sammenslåtte kommuner: antall summeres, andelen regnes som sum antall /
  sum nevner, der nevneren for hver gammel kommune er median(antall / andel) i året.
  Delte kommuner (Tysfjord 1850 → Narvik og Hamarøy, 2020): ingen verdier før 2020 for
  mottakerkommunene (brudd, avgjort 20.11.2026).
  Fylke og landsdel regnes som sum av kommunene; landet er NAVs egen «I alt»-rad.

Prikking og tegn («*», «:», «-», «–», «..») lagres som tegn og regnes aldri som 0.

Bruk: python fetch_nav.py
"""
import json
import re
import statistics
import sys
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
K = HER / "analyse" / "nav" / "kilder"
UT = HER / "analyse" / "nav" / "data"

KODER = re.findall(r'"(\d{4})"', re.search(r"CODES\s*=\s*\[(.*?)\]", (HER / "fetch_arbeid.py").read_text(encoding="utf-8"), re.S).group(1))
assert len(KODER) == 80, len(KODER)
FYLKE = {"18": "Nordland", "55": "Troms", "56": "Finnmark"}
MND = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"]
TEGN = ("*", ":", "-", "–", "..", ".")
t = lambda x: "" if x is None else str(x).strip()


def tall(x):
    """Tall fra celle (også tekst som «1086» eller «5.4»), ellers None."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = t(x).replace(" ", "").replace(" ", "")
    if re.fullmatch(r"-?\d+([.,]\d+)?", s):
        return float(s.replace(",", "."))
    return None


def verdi(x):
    """Tall, tegn for prikking/manglende, eller None."""
    v = tall(x)
    if v is not None:
        return v
    s = t(x)
    return s if s in TEGN else None


def ark(fil):
    if fil.suffix.lower() == ".xls":
        import xlrd
        bok = xlrd.open_workbook(str(fil), logfile=open("nul" if sys.platform == "win32" else "/dev/null", "w"))
        for s in bok.sheets():
            yield s.name, [s.row_values(i) for i in range(s.nrows)]
    else:
        import openpyxl
        bok = openpyxl.load_workbook(str(fil), read_only=False, data_only=True)  # read_only kutter kolonner
        for s in bok.worksheets:
            yield s.title, [list(r) for r in s.iter_rows(values_only=True)]


def kode(r):
    """(kommunekode, kolonne for navnet) fra de første ikke-tomme cellene."""
    celler = [(j, t(x)) for j, x in enumerate(r[:8]) if t(x)][:4]
    for i, (j, s) in enumerate(celler):
        if re.fullmatch(r"\d{3,4}(\.0)?", s) and i + 1 < len(celler) and re.search(r"[A-Za-zÆØÅæøåÁá]", celler[i + 1][1]):
            k = s.split(".")[0].zfill(4)
            return (None, None) if k.endswith("00") else (k, celler[i + 1][0])  # «1800 Nordland» er fylke
        m = re.match(r"^(\d{4})\s+(\S.*)$", s)
        if m:
            return m.group(1), j
    return None, None


def navn_fra(r, j):
    s = t(r[j])
    return re.sub(r"^\d{4}\s+", "", s)


def er_landet(r):
    lab = " ".join(t(x) for x in r[:3] if t(x) and tall(x) is None)
    return bool(re.fullmatch(r"(I alt|Landet i alt|Hele landet|Landet|I alt, alle kommuner)", lab.strip()))


# ------------------------------------------------------------------ kommunenøkkel
def lag_nokkel():
    d = json.loads((UT / "klass131_endringer.json").read_text(encoding="utf-8"))
    per_dato = defaultdict(lambda: defaultdict(set))
    for c in d["codeChanges"]:
        per_dato[c["changeOccurred"]][c["oldCode"]].add(c["newCode"])
    delt = {}  # gammel kode -> (dato, nye koder)
    neste = {}
    for dato in sorted(per_dato):
        for gml, nye in per_dato[dato].items():
            if len(nye) > 1:
                delt[gml] = (dato, sorted(nye))
            else:
                neste.setdefault(gml, []).append((dato, next(iter(nye))))

    def fram(k):
        """Fører en kode fram til gjeldende kode; None hvis kommunen ble delt."""
        sett = set()
        while True:
            if k in delt:
                return None
            nye = [n for _, n in neste.get(k, []) if n != k]
            if not nye or k in sett:
                return k
            sett.add(k)
            k = nye[0]

    def hopp(k):
        """Antall kodeendringer fram til gjeldende kode (kodegenerasjon; 0 = gjeldende)."""
        n, sett = 0, set()
        while True:
            nye = [x for _, x in neste.get(k, []) if x != k]
            if not nye or k in sett or k in delt:
                return n
            sett.add(k)
            k, n = nye[0], n + 1

    mottakere = {}
    for gml, (dato, nye) in delt.items():
        for n in nye:
            g = fram(n)
            if g:
                mottakere[g] = (int(dato[:4]), gml)
    return fram, mottakere, delt, hopp


FRAM, BRUDD, DELT, HOPP = lag_nokkel()  # BRUDD: gjeldende kode -> (første hele år, delt kode)


# ------------------------------------------------------------------ innlesing
def dato_fra(s):
    """«Desember 2017», «des. 2011», «31.12.14», «30.06.2015» -> 'YYYY-MM'."""
    s = t(s).lower()
    m = re.search(r"(januar|februar|mars|april|mai|juni|juli|august|september|oktober|november|desember|des)\.?\s*(20\d\d)", s)
    if m:
        mnd = 12 if m.group(1) == "des" else MND.index(m.group(1)) + 1
        return f"{m.group(2)}-{mnd:02d}"
    m = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})\b", s)
    if m:
        aar = int(m.group(3)) + (2000 if len(m.group(3)) == 2 else 0)
        return f"{aar}-{int(m.group(2)):02d}"
    return None


def maanedsark(rader):
    """Kommunerader i et ark med månedskolonner: {kode: ({mnd: verdi}, navn)}. Landet under '0000'."""
    """Fylkessummer lagres under 'F:<etikett>' og brukes til landstallet når filen mangler en landsrad."""
    ut, hode, fylkehode = {}, None, None
    for r in rader:
        m = {j: MND.index(t(x).lower()) + 1 for j, x in enumerate(r) if t(x).lower() in MND}
        m.update({j: int(re.fullmatch(r"20\d\d(\d\d)(\.0)?", t(x)).group(1)) for j, x in enumerate(r)
                  if re.fullmatch(r"20\d\d(0[1-9]|1[0-2])(\.0)?", t(x))})  # «202101»
        if len(m) >= 2:
            hode = m
            # Overskriftsraden kan også bære fylkesnavnet («03 Oslo | Januar …»); da er neste
            # «I alt» fylkets sum, ikke landets.
            tekst = [t(x) for j, x in enumerate(r) if j not in m and t(x)]
            fylkehode = tekst[0] if tekst and not re.match(r"(?i)^(kommune|fylke|bosted|region|år|periode)", tekst[0]) else None
            continue
        if not hode:
            continue
        k, j = kode(r)
        lab =" ".join(t(x) for x in r[:4] if t(x) and tall(x) is None)
        har_tall = sum(tall(x) is not None for x in r) >= 2
        nokkel = None
        if not k and re.match(r"^I alt\s+\S", lab) and har_tall:
            nokkel = "F:" + lab  # «I alt 18 Nordland», «I alt Ukjent»
        elif not k and re.match(r"^\d\d\s+\S", lab) and not har_tall:
            fylkehode = lab  # «18 Nordland» som overskrift, fulgt av en rad «I alt»
            continue
        elif not k and lab == "I alt" and fylkehode and har_tall:
            nokkel, fylkehode = "F:" + fylkehode, None
        if nokkel and nokkel in ut:
            continue
        if nokkel:
            v = {mnd: verdi(r[c]) for c, mnd in hode.items() if c < len(r) and verdi(r[c]) is not None}
            if v:
                ut[nokkel] = (v, nokkel)
            continue
        nokkel = k if k else ("0000" if er_landet(r) and not fylkehode else None)
        if not nokkel or nokkel in ut:
            continue
        v = {mnd: verdi(r[c]) for c, mnd in hode.items() if c < len(r) and verdi(r[c]) is not None}
        if v:
            ut[nokkel] = (v, navn_fra(r, j) if k else "Landet")
    return ut


def fil_aar(navn, monster):
    m = re.findall(monster, navn)
    return int(m[-1]) if m else None


KILDER = defaultdict(list)


def les_maaned(kat, filter_re, ant_re, pst_re, aar_re):
    """Månedskategorier. Returnerer {aar: {kode: {'antall':{m:v}, 'pst':{m:v}}}}, navn."""
    beste = {}
    navn = {}
    for f in sorted((K / kat).glob("*.xls*")):
        if not re.search(filter_re, f.name, re.I):
            continue
        aar = fil_aar(f.name, aar_re)
        rec = defaultdict(dict)
        for an, rader in ark(f):
            al = an.lower()
            fylkeark = "fylke" in al and "kommune" not in al  # brukes bare for landstallet
            if "kommune" not in al and not fylkeark:
                continue
            felt = "antall" if re.search(ant_re, al) else "pst" if re.search(pst_re, al) else None
            if not felt:
                continue
            for k, (v, nv) in maanedsark(rader).items():
                if fylkeark and (k != "0000" or felt in rec.get("0000", {})):
                    continue
                rec[k][felt] = v
                navn.setdefault(k, nv)
        # Fylkessummene («F:…») brukes ikke: antall fylker og radformat skifter mellom filene, så
        # landstallet for AAP og nedsatt fra 2016 kan ikke summeres pålitelig. Landet vises bare
        # der NAV har en egen landsrad (avgjort 20.11.2026).
        for k in [k for k in rec if k.startswith("F:")]:
            del rec[k]
        nmnd = max((len(x.get("antall", {})) for k, x in rec.items() if k != "0000"), default=0)
        if nmnd and (aar not in beste or nmnd > beste[aar][0]):
            beste[aar] = (nmnd, dict(rec), f.name)
    for aar, (_, _, fn) in sorted(beste.items()):
        KILDER[kat].append(f"{aar}: {fn}")
    return {aar: rec for aar, (_, rec, _) in beste.items()}, navn


def les_ufore():
    """{dato: {kode: {'antall':v,'pst':v,'astd':v}}}.

    Hver fil er en utgave, datert med den nyeste tellingsdatoen i filen. For hver tellingsdato
    velges én utgave for alle kommuner: den nyeste med presise andeler (mer enn én desimal),
    ellers den nyeste med andeler, ellers den nyeste med antall. Andeler oppgitt som brøk
    (0,171) ganges med 100 og regnes som upresise.
    """
    utg = {}  # filnavn -> {dato: {kode: {...}}}, presisjon per (fil, dato)
    presis = defaultdict(bool)
    utgave = {}
    for f in sorted((K / "ufore").glob("*.xls*")):
        data = defaultdict(dict)
        for an, rader in ark(f):
            andel_ark = "andel" in an.lower()
            hode = None
            for r in rader:
                d = [(j, dato_fra(x)) for j, x in enumerate(r) if dato_fra(x) and tall(x) is None]
                if len(d) >= 2:
                    hode, sett = [], defaultdict(int)
                    for j, dt in d:
                        n = sett[dt]
                        sett[dt] += 1
                        felt = "pst" if andel_ark else ("antall", "pst", "astd")[min(n, 2)]
                        hode.append((j, dt, felt))
                    continue
                if not hode:
                    continue
                k, _ = kode(r)
                nokkel = k if k else ("0000" if er_landet(r) else None)
                if not nokkel:
                    continue
                for j, dt, felt in hode:
                    if j < len(r) and verdi(r[j]) is not None:
                        data[dt].setdefault(nokkel, {})[felt] = verdi(r[j])
        for dt, rec in data.items():
            andeler = [x["pst"] for x in rec.values() if isinstance(x.get("pst"), float)]
            if andeler and max(andeler) < 1:  # brøk
                for x in rec.values():
                    if isinstance(x.get("pst"), float):
                        x["pst"] *= 100
            else:
                presis[(f.name, dt)] = any(abs(v * 10 - round(v * 10)) > 1e-6 for v in andeler)
        if data:
            utg[f.name] = data
            utgave[f.name] = max(data)
    ut = {}
    for dt in sorted({d for x in utg.values() for d in x}):
        kand = sorted((f for f in utg if dt in utg[f]), key=lambda f: utgave[f], reverse=True)
        har_andel = [f for f in kand if any(isinstance(x.get("pst"), float) for x in utg[f][dt].values())]
        valgt = next((f for f in har_andel if presis[(f, dt)]), None) or (har_andel or kand)[0]
        ut[dt] = {k: dict(x) for k, x in utg[valgt][dt].items()}
        KILDER["ufore"].append(f"{dt}: {valgt}")
        # aldersstandardiserte andeler (2015–2017) finnes bare i enkelte utgaver: nyeste som har dem
        for f in kand:
            astd = {k: x["astd"] for k, x in utg[f][dt].items() if "astd" in x}
            if astd:
                for k, x in ut[dt].items():
                    if k in astd:
                        x["astd"] = astd[k]
                    else:
                        x.pop("astd", None)
                if f != valgt:
                    KILDER["ufore"][-1] += f" (aldersstandardisert: {f})"
                break
    return ut


def les_pst(kode_fil):
    """PST011/PST062: {aar: {kode: antall}} (dagens kommuner, september)."""
    f = next((K / "alderspensjon").glob(f"*{kode_fil}*"))
    KILDER[kode_fil].append(f.name)
    ut = defaultdict(dict)
    for an, rader in ark(f):
        if not an.startswith("1"):
            continue
        hode = None
        for r in rader:
            if "Kommunenavn" in [t(x) for x in r]:
                hode = {j: int(tall(x)) for j, x in enumerate(r) if tall(x) and 2000 < tall(x) < 2100}
                continue
            if not hode:
                continue
            k, _ = kode(r)
            nokkel = k if k else ("0000" if "I alt" in [t(x) for x in r[:3]] else None)
            if nokkel:
                for j, aar in hode.items():
                    if j < len(r) and verdi(r[j]) is not None:
                        ut[aar][nokkel] = verdi(r[j])
    return ut


# ------------------------------------------------------------------ omregning til gjeldende kommuner
def nevner(antall, pst):
    """Median av antall/andel*100 over måneder/datoer med andel > 0."""
    v = [antall[m] / pst[m] * 100 for m in antall if isinstance(antall.get(m), float) and isinstance(pst.get(m), float) and pst[m] > 0 and antall[m] > 0]
    return statistics.median(v) if v else None


def snitt(d):
    v = [x for x in (d or {}).values() if isinstance(x, float)]
    return round(statistics.mean(v), 9) if v else None


def til_gjeldende(aar, rec):
    """rec: {gammel kode: {'antall':{m:v}, 'pst':{m:v}}} -> {gjeldende kode: {...}} for de 80 + fylker."""
    grupper = defaultdict(list)
    for k, x in rec.items():
        if k == "0000":
            continue
        g = FRAM(k)
        if g is None:  # delt kommune: tas bare med i fylkessummen
            grupper["delt:" + k].append((k, x))
            continue
        grupper[g].append((k, x))
    def har_tall(x):
        return any(isinstance(v, float) for v in list(x.get("antall", {}).values()) + list(x.get("pst", {}).values()))

    ut, valgt = {}, {}
    for g, deler in grupper.items():
        if g.startswith("delt:"):
            continue
        # Nyeste kodegenerasjon med tall vinner. NAVs egne omregninger til ny inndeling (f.eks.
        # 2018–2019 i utgaven for 2020) går dermed foran vår summering, og gamle koder som står
        # igjen i en fil sammen med den nye koden (Harstad/Bjarkøy 2012) telles ikke to ganger.
        gen = sorted({HOPP(k) for k, x in deler if har_tall(x)})
        if gen:
            deler = [(k, x) for k, x in deler if HOPP(k) == gen[0]]
        valgt[g] = deler
        if g not in KODER:
            continue
        if g in BRUDD and aar < BRUDD[g][0] and g not in [k for k, _ in deler]:
            ut[g] = {"brudd": f"Tysfjord ble delt mellom Narvik og Hamarøy i {BRUDD[g][0]}"}
            continue
        if len(deler) == 1:
            k, x = deler[0]
            ut[g] = {"antall": x.get("antall", {}), "pst": x.get("pst", {}), "deler": [k]}
            continue
        ut[g] = slaa_sammen(deler)
    # fylkessummen: valgte deler, og delte kommuner bare når mottakerne står med gamle koder
    for g, deler in grupper.items():
        if g.startswith("delt:") and any(m in valgt and m not in [k for k, _ in valgt[m]] for m in BRUDD if BRUDD[m][1] == g[5:]):
            valgt[g] = deler
    return ut, valgt


PRIKK_ANSLAG = 1.5  # NAV prikker tall under 4; midtpunktet i 0–3 brukes bare i fylkessummer


def slaa_sammen(deler, anslag=False):
    """Summerer deler. Kommuner (anslag=False): én prikket del gir prikket sum.
    Fylker (anslag=True): prikket celle telles som 1,5 og måneden merkes som anslått; en del uten
    nevner (prikket hele året) tas med i antallet, men ikke i andelen."""
    mnd = sorted({m for _, x in deler for m in x.get("antall", {})})
    ant, pst, anslatt = {}, {}, []
    nev = {k: nevner(x.get("antall", {}), x.get("pst", {})) for k, x in deler}
    for m in mnd:
        vv = [x.get("antall", {}).get(m) for _, x in deler]
        prikket = [v == "*" for v in vv]
        if any(not isinstance(v, float) for v, p in zip(vv, prikket) if not (anslag and p)):
            ant[m] = "*"  # minst én del prikket eller mangler
            continue
        vv = [PRIKK_ANSLAG if p else v for v, p in zip(vv, prikket)]
        ant[m] = sum(vv)
        if any(prikket):
            anslatt.append(m)
        if anslag:
            med = [(v, nev[k]) for v, (k, _) in zip(vv, deler) if nev[k]]
            pst[m] = sum(v for v, _ in med) / sum(n for _, n in med) * 100 if med else None
        elif all(nev[k] for k, _ in deler):
            pst[m] = ant[m] / sum(nev[k] for k, _ in deler) * 100
    r = {"antall": ant, "pst": pst, "deler": [k for k, _ in deler], "beregnet": True}
    if anslatt:
        r["anslatt_mnd"] = anslatt
    return r


def fylkessum(grupper_aar):
    """Sum av alle gamle kommuner som hører til hvert av dagens fylker (inkl. delte kommuner)."""
    per_fylke = defaultdict(list)
    for g, deler in grupper_aar.items():
        if g.startswith("delt:"):
            k = g[5:]
            if k not in DELT:  # delt lenger fram i kjeden; aldri i Nord-Norge
                continue
            fy = (FRAM(DELT[k][1][0]) or "")[:2]
        else:
            fy = g[:2]
        if fy in FYLKE:
            per_fylke[fy].extend(deler)
    ut = {fy: slaa_sammen(d, anslag=True) for fy, d in per_fylke.items()}
    ut["NN"] = slaa_sammen([d for fy in FYLKE for d in per_fylke.get(fy, [])], anslag=True)
    return ut


def aarsrad(x, n_mnd=None):
    if "brudd" in x:
        return {"brudd": x["brudd"]}
    ant, pst = x.get("antall", {}), x.get("pst", {})
    prikket = [m for m, v in ant.items() if v == "*"]
    skjult = False
    if prikket:
        # Prikkede måneder (0–3 personer) telles som 1,5 i årssnittet (avgjort 20.11.2026);
        # er mer enn halvparten prikket, vises ikke snitt.
        if len(prikket) * 2 > len(ant):
            skjult = True
        else:
            nev = nevner(ant, pst)
            ant = {m: (PRIKK_ANSLAG if v == "*" else v) for m, v in ant.items()}
            pst = dict(pst)
            for m in prikket:
                pst[m] = PRIKK_ANSLAG / nev * 100 if nev else None
            if not nev:
                pst = {}
    r = {"antall": None if skjult else snitt(ant), "pst": None if skjult else snitt(pst),
         "mnd": {m: [x.get("antall", {}).get(m), round(x["pst"][m], 4) if isinstance(x.get("pst", {}).get(m), float) else x.get("pst", {}).get(m)] for m in sorted(x.get("antall", {}))}}
    if x.get("beregnet"):
        r["beregnet"] = True
    if 1 < len(x.get("deler", [])) <= 6:  # sammenslåtte kommuner (ikke fylkessummer)
        r["deler"] = x["deler"]
    if x.get("anslatt_mnd"):
        r["anslatt_mnd"] = x["anslatt_mnd"]
    if prikket:
        r["prikket_mnd"] = len(prikket)
        r["anslatt" if not skjult else "skjult"] = True
    tegn = sorted({v for v in list(x.get("antall", {}).values()) + list(x.get("pst", {}).values()) if isinstance(v, str)})
    if tegn:
        r["tegn"] = tegn
    return r


# ------------------------------------------------------------------ fase 3: filer til dashbordet
def r4(x):
    return None if not isinstance(x, (int, float)) else round(x, 4)


def flagg(r, ekstra=None):
    f = []
    if "brudd" in r:
        return ["brudd"]
    for k in ("anslatt", "skjult", "beregnet"):
        if r.get(k):
            f.append(k)
    if ekstra:
        f.append(ekstra)
    return f


def serie_maaned(s, maks_aar=None, mnd=True):
    """Årsserie for helt ledige / AAP / nedsatt: {aar:[...], pst:[...], antall:[...], f:[[flagg]], n:[mnd], mnd:{aar:[[a,p]×12]}}."""
    ut = {"aar": [], "pst": [], "antall": [], "f": [], "n": []}
    if mnd:
        ut["mnd"] = {}
    for a in sorted(s, key=int):
        r = s[a]
        m = r.get("mnd", {})
        ekstra = "aarssnitt" if list(m) == ["0"] else None
        ut["aar"].append(int(a))
        ut["pst"].append(r4(r.get("pst")))
        ut["antall"].append(r4(r.get("antall")))
        ut["f"].append(flagg(r, ekstra))
        ut["n"].append(0 if ekstra or "brudd" in r else len(m))
        if mnd and m and not ekstra:
            ut["mnd"][a] = [[(r4(m[str(i)][0]) if isinstance(m[str(i)][0], (int, float)) else m[str(i)][0]),
                             (r4(m[str(i)][1]) if isinstance(m[str(i)][1], (int, float)) else m[str(i)][1])]
                            if str(i) in m else None for i in range(1, 13)]
    return ut


def uten_aap(ned, aap):
    """Andel av personer med nedsatt arbeidsevne som ikke har AAP, snitt over felles måneder."""
    ut = {}
    for a, r in ned.items():
        q = aap.get(a, {})
        mn, ma = r.get("mnd", {}), q.get("mnd", {})
        felles = [m for m in mn if m in ma and isinstance(mn[m][0], float) and isinstance(ma[m][0], float) and mn[m][0] > 0]
        if felles:
            ut[int(a)] = r4(statistics.mean((mn[m][0] - ma[m][0]) / mn[m][0] * 100 for m in felles))
    return ut


def serie_ufore(s):
    """Desember hvert år, og september for de to siste årene uten desembertall."""
    datoer = sorted(d for d in s if d.endswith("-12"))
    siste_des = int(datoer[-1][:4]) if datoer else 0
    datoer += sorted(d for d in s if d.endswith("-09") and int(d[:4]) > siste_des)
    ut = {"dato": [], "pst": [], "antall": [], "f": [], "astd": []}
    for d in datoer:
        r = s[d]
        ut["dato"].append(d)
        ut["pst"].append(r4(r.get("pst")))
        ut["antall"].append(r4(r.get("antall")))
        ut["f"].append(flagg(r, "uforepensjon" if int(d[:4]) <= 2012 else None))
        ut["astd"].append(r4(r.get("aldersstandardisert")))
    return ut


def serie_pensjon(s):
    ut = {"aar": [], "alderspensjon": [], "minstepensjon": [], "pst": [], "f": []}
    for a in sorted(s, key=int):
        r = s[a]
        ut["aar"].append(int(a))
        ut["alderspensjon"].append(r4(r.get("alderspensjon")))
        ut["minstepensjon"].append(r4(r.get("minstepensjon")))
        ut["pst"].append(r4(r.get("pst")))
        ut["f"].append(["navfeil"] if int(a) < 2020 else flagg(r))
    return ut


def niva_fil(x, mnd=True):
    ut = {}
    if "helt_ledige" in x:
        ut["ledige"] = serie_maaned(x["helt_ledige"], mnd=mnd)
    if "aap" in x:
        ut["aap"] = serie_maaned(x["aap"], mnd=mnd)
    if "nedsatt" in x:
        ut["nedsatt"] = serie_maaned(x["nedsatt"], mnd=mnd)
        ut["nedsatt"]["uten_aap"] = uten_aap(x["nedsatt"], x.get("aap", {}))
    if "ufore" in x:
        ut["ufore"] = serie_ufore(x["ufore"])
    if "pensjon" in x:
        ut["pensjon"] = serie_pensjon(x["pensjon"])
    return ut


def landet_fil(L):
    ut = {}
    for kat, navn in (("helt_ledige", "ledige"), ("aap", "aap"), ("nedsatt", "nedsatt")):
        if L.get(kat):
            ut[navn] = serie_maaned(L[kat], mnd=False)
    u = {d: {"antall": v.get("antall"), "pst": v.get("pst")} for d, v in L.get("ufore", {}).items()}
    ut["ufore"] = serie_ufore(u)
    ut["pensjon"] = serie_pensjon(L.get("pensjon", {}))
    return ut


def publiser(D):
    """data/nav/<kode>.json (kommune med fylke og landet som referanse) og NAV_KART i assets/data.js."""
    mappe = HER / "data" / "nav"
    mappe.mkdir(parents=True, exist_ok=True)
    meta = {"kilde": "NAV, statistikk per kommune; kommuneinndeling etter SSB Klass 131",
            "hentet": "2026-11-20",
            "brudd": "Tysfjord ble delt mellom Narvik og Hamarøy i 2020. Der NAV ikke har regnet om eldre tall, vises ingen tall før 2020.",
            "prikking": "NAV skjuler tall under 4. Skjulte måneder telles som 1,5 i årssnittet (merket anslått); er mer enn halvparten skjult, vises ikke snitt.",
            "minstepensjon": "NAV oppgir feil i minstepensjonstallene før september 2020."}
    fylker = {fy: niva_fil(D["fylker"][fy], mnd=False) for fy in D["fylker"]}
    landet = landet_fil(D["landet"])
    for fy, navn in list(FYLKE.items()) + [("NN", "Nord-Norge")]:
        (mappe / f"fylke-{fy}.json").write_text(json.dumps({"kode": fy, "navn": navn, "meta": meta, **fylker[fy], "landet": landet},
                                                           ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for k in KODER:
        fil = {"kode": k, "navn": D["navn"].get(k, k), "fylke": k[:2], "meta": meta,
               **niva_fil(D["kommuner"][k]),
               "ref": {"fylke": {"navn": FYLKE[k[:2]], **fylker[k[:2]]}, "NN": fylker["NN"], "landet": landet}}
        (mappe / f"{k}.json").write_text(json.dumps(fil, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # NAV_KART: siste hele år (månedskategorier), siste tellingsdato (uføre), siste år (minstepensjon)
    def siste_hele(s):
        hele = [a for a, r in s.items() if len(r.get("mnd", {})) == 12 and r.get("pst") is not None]
        return max(hele, key=int) if hele else None

    kart = {"meta": {}, "kommuner": {}, "ref": {}}
    aar = {kat: siste_hele(D["fylker"]["NN"][kat]) for kat in ("helt_ledige", "aap", "nedsatt")}
    udato = max(d for d in D["fylker"]["NN"]["ufore"])
    paar = max(D["fylker"]["NN"]["pensjon"], key=int)
    kart["meta"] = {"ledige": aar["helt_ledige"], "aap": aar["aap"], "nedsatt": aar["nedsatt"], "ufore": udato, "minstepensjon": paar}

    def rad(x):
        return {"ledige": r4(x.get("helt_ledige", {}).get(aar["helt_ledige"], {}).get("pst")),
                "aap": r4(x.get("aap", {}).get(aar["aap"], {}).get("pst")),
                "nedsatt": r4(x.get("nedsatt", {}).get(aar["nedsatt"], {}).get("pst")),
                "ufore": r4(x.get("ufore", {}).get(udato, {}).get("pst")),
                "minstepensjon": r4(x.get("pensjon", {}).get(paar, {}).get("pst"))}
    for k in KODER:
        kart["kommuner"][k] = rad(D["kommuner"][k])
        if D["kommuner"][k].get("helt_ledige", {}).get(aar["helt_ledige"], {}).get("anslatt"):
            kart["kommuner"][k]["ledige_anslatt"] = True
    for fy in list(FYLKE) + ["NN"]:
        kart["ref"][fy] = rad(D["fylker"][fy])
    L = D["landet"]
    kart["ref"]["landet"] = {"ledige": r4(L["helt_ledige"].get(aar["helt_ledige"], {}).get("pst")),
                             "aap": r4(L.get("aap", {}).get(aar["aap"], {}).get("pst")),
                             "nedsatt": r4(L.get("nedsatt", {}).get(aar["nedsatt"], {}).get("pst")),
                             "ufore": r4(L["ufore"].get(udato, {}).get("pst")),
                             "minstepensjon": r4(L["pensjon"].get(paar, {}).get("pst"))}
    djs = HER / "assets" / "data.js"
    js = djs.read_text(encoding="utf-8")
    blokk = "/* NAV_KART BEGIN */\nconst NAV_KART = " + json.dumps(kart, ensure_ascii=False, separators=(",", ":")) + ";\n/* NAV_KART END */"
    if "/* NAV_KART BEGIN */" in js:
        js = re.sub(r"/\* NAV_KART BEGIN \*/.*?/\* NAV_KART END \*/", lambda _m: blokk, js, flags=re.S)
    else:
        js = js.rstrip("\n") + "\n" + blokk + "\n"
    djs.write_text(js, encoding="utf-8")
    return kart


# ------------------------------------------------------------------ hovedløp
def main():
    D = {"meta": {"kilde": "NAV, kommunetabeller (se kilder)", "kommunenokkel": "SSB Klass 131",
                  "nevner": "andel for sammenslåtte kommuner og fylker = sum antall / sum (antall/andel), median per år",
                  "brudd": {g: {"forste_aar": a, "delt_kode": k} for g, (a, k) in BRUDD.items()}},
         "kommuner": {k: {} for k in KODER}, "fylker": {f: {} for f in list(FYLKE) + ["NN"]}, "landet": {}, "navn": {}}

    def legg_inn(kat, aar, rec):
        ut, grp = til_gjeldende(aar, rec)
        for g, x in ut.items():
            D["kommuner"][g].setdefault(kat, {})[aar] = aarsrad(x)
        for fy, x in fylkessum(grp).items():
            D["fylker"][fy].setdefault(kat, {})[aar] = aarsrad(x)
        if "0000" in rec:
            D["landet"].setdefault(kat, {})[aar] = aarsrad(rec["0000"])

    # 1. Helt ledige
    hl, navn = les_maaned("helt_ledige", r"hl060", r"antall", r"prosent", r"(20\d\d)\d\d")
    D["navn"].update({k: v for k, v in navn.items() if k in KODER})
    for aar, rec in sorted(hl.items()):
        legg_inn("helt_ledige", aar, rec)

    # 2. AAP og 3. nedsatt arbeidsevne (AAP155/NED155, 2016–)
    for kat, filt in (("aap", r"aap155"), ("nedsatt", r"ned155")):
        data, _ = les_maaned(kat, filt, r"antall", r"andel", r"(20\d\d)")
        for aar, rec in sorted(data.items()):
            legg_inn(kat, aar, rec)

    # AAP 2010–2015: årsgjennomsnitt (ett ark per år, kolonnene antall og andel)
    f = next((K / "aap").glob("*2010-2015*"))
    KILDER["aap"].insert(0, f"2010–2015 (årsgjennomsnitt): {f.name}")
    for an, rader in ark(f):
        if not re.fullmatch(r"20\d\d", an.strip()):
            continue
        rec = {}
        for r in rader:
            k, j = kode(r)
            nokkel = k if k else ("0000" if er_landet(r) else None)
            if not nokkel:
                continue
            v = [verdi(x) for x in r[(j + 1 if k else 1):] if verdi(x) is not None]
            if len(v) >= 2:
                rec[nokkel] = {"antall": {0: v[0]}, "pst": {0: v[1]}}  # måned 0 = årsgjennomsnitt
        legg_inn("aap", int(an), rec)

    # Juli–september 2015 (AAP og nedsatt): ett ark per måned
    for kat in ("aap", "nedsatt"):
        f = next((K / kat).glob("*juli-september-2015*"))
        KILDER[kat].append(f"2015 (juli–september): {f.name}")
        rec = defaultdict(lambda: {"antall": {}, "pst": {}})
        for an, rader in ark(f):
            if an.strip().lower() not in MND:
                continue
            m = MND.index(an.strip().lower()) + 1
            for r in rader:
                k, j = kode(r)
                nokkel = k if k else ("0000" if er_landet(r) else None)
                if not nokkel:
                    continue
                v = [verdi(x) for x in r[(j + 1 if k else 1):] if verdi(x) is not None]
                if len(v) >= 2:
                    rec[nokkel]["antall"][m], rec[nokkel]["pst"][m] = v[0], v[1]
        nokkel_kat = kat + "_2015"
        legg_inn(nokkel_kat, 2015, dict(rec))

    # 4. Uføretrygd
    uf = les_ufore()
    for dt in sorted(uf):
        rec = {k: {"antall": {0: x.get("antall")}, "pst": {0: x.get("pst")}} for k, x in uf[dt].items() if x.get("antall") is not None}
        aar = int(dt[:4])
        ut, grp = til_gjeldende(aar, rec)
        for g, x in ut.items():
            r = aarsrad(x)
            r.pop("mnd", None)
            astd = uf[dt].get(g, {}).get("astd") if len(x.get("deler", [])) == 1 else None
            if astd is not None:
                r["aldersstandardisert"] = astd
            D["kommuner"][g].setdefault("ufore", {})[dt] = r
        for fy, x in fylkessum(grp).items():
            r = aarsrad(x)
            r.pop("mnd", None)
            D["fylker"][fy].setdefault("ufore", {})[dt] = r
        if "0000" in uf[dt]:
            D["landet"].setdefault("ufore", {})[dt] = {k: v for k, v in uf[dt]["0000"].items()}

    # 5. Alderspensjon og minstepensjon (dagens kommuner)
    ap, mp = les_pst("PST011"), les_pst("PST062")
    for aar in sorted(ap):
        for nivaa, koder in (("kommuner", KODER), ("landet", ["0000"])):
            for k in koder:
                a, m = ap[aar].get(k), mp.get(aar, {}).get(k)
                r = {"alderspensjon": a, "minstepensjon": m,
                     "pst": round(m / a * 100, 6) if isinstance(a, float) and isinstance(m, float) and a else None}
                if aar < 2020:
                    r["merk"] = "NAV: minstepensjonstallene er korrekte fra september 2020"
                (D["kommuner"][k] if nivaa == "kommuner" else D["landet"]).setdefault("pensjon", {})[aar] = r
        for fy in list(FYLKE) + ["NN"]:
            kk = [k for k in KODER if fy == "NN" or k[:2] == fy]
            a = [ap[aar].get(k) for k in kk]
            m = [mp.get(aar, {}).get(k) for k in kk]
            ok = all(isinstance(x, float) for x in a + m)
            D["fylker"][fy].setdefault("pensjon", {})[aar] = {
                "alderspensjon": sum(a) if ok else None, "minstepensjon": sum(m) if ok else None,
                "pst": round(sum(m) / sum(a) * 100, 6) if ok else None, "beregnet": True}

    D["meta"]["kilder"] = KILDER
    UT.mkdir(parents=True, exist_ok=True)
    (UT / "nav_kommuner.json").write_text(json.dumps(D, ensure_ascii=False, indent=None, separators=(",", ":"), default=str), encoding="utf-8")
    return D


if __name__ == "__main__":
    D = main()
    print("Skrevet", UT / "nav_kommuner.json")
    kart = publiser(json.loads((UT / "nav_kommuner.json").read_text(encoding="utf-8")))
    print("Skrevet data/nav/ (80 kommuner + 4 fylkesfiler) og NAV_KART i assets/data.js:", kart["meta"])
    for kat in ("helt_ledige", "aap", "nedsatt", "ufore", "pensjon"):
        aar = sorted({a for k in KODER for a in D["kommuner"][k].get(kat, {})}, key=str)
        mangler = {a: [k for k in KODER if a not in D["kommuner"][k].get(kat, {})] for a in aar}
        print(f"{kat}: {len(aar)} perioder {aar[0]}–{aar[-1]}; perioder der kommuner mangler:",
              {a: len(v) for a, v in mangler.items() if v} or "ingen")
