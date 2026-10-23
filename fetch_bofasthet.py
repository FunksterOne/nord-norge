#!/usr/bin/env python3
"""Bofasthet for flyktninger og innvandrere → BOFAST_DATA i assets/data.js.

Tre mål, som ikke skal blandes:
  kull5   Direkte: andel av bosettingskullet som bor i første bosettingskommune (og -fylke) fem år etter bosetting.
          SSBs monitor for sekundærflytting, kull 1998–2019 per fylke. Tallene er avlest manuelt fra rapportene,
          med tabell og PDF-side (se analyse/bofasthet/statistikk.md, tabell A).
  lang    Direkte, bare landet: andel i første bosettingskommune etter 5–14 år (SSB 2021 og 28.11.2024).
  netto   Indirekte: netto bevaring i området etter 5, 10, 15 og 20 års botid, pseudokohorter fra SSB 10598
          (analyse/bofasthet/skript/pseudokohort_10598.py, tabell C).
  botid10 Bestandsmål per kommune: andel av innvandrerne med ti års botid i Norge eller mer, 1.1.2021 og 1.1.2026
          (IMDi «Innvandrernes botid», kilde SSB). Leses fra analyse/bofasthet/kilder/imdi/, som hentes med
          analyse/bofasthet/skript/hent_imdi.py.

Kjør:  python fetch_bofasthet.py
"""
import json
import re
import sys
from pathlib import Path

HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
IMDI = HER / "analyse" / "bofasthet" / "kilder" / "imdi"
NN_FYLKER = ("18", "55", "56")

# ── A. Fem år etter bosetting, prosent av hele kullet (utvandrede og døde i nevneren) ──
KULL = [1998, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2015, 2019]
KULL5 = {
    "kull": KULL,
    "kommune": {
        "Landet":   [53, 53, 60, 65, 69, 70, 73, 76, 77, 78, 78, 78, 80, 81, 82, 86],
        "Nordland": [21, 32, 39, 37, 49, 49, 45, 52, 66, 69, 61, 60, 76, 69, 65, 82],
        "Troms":    [26, 27, 34, 37, 52, 52, 47, 60, 61, 65, 71, 69, 69, 74, None, 81],
        "Finnmark": [9, 24, 33, 42, 25, 54, 71, 58, 72, 70, 74, 71, 58, 72, None, 90],
        "Troms og Finnmark": [None] * 14 + [68, None],
    },
    "fylke": {
        "Nordland": [22, 35, 43, 40, 54, 54, 47, 54, 69, 70, 66, 65, 80, 73, 74, 84],
        "Troms":    [29, 31, 37, 38, 56, 56, 50, 64, 63, 66, 75, 72, 74, 78, None, 83],
        "Finnmark": [15, 26, 36, 46, 28, 57, 74, 59, 75, 74, 77, 76, 61, 74, None, None],
        "Troms og Finnmark": [None] * 14 + [73, None],
    },
    "kilde": ["Monitor 2005, tab. 3", "Monitor 2006, tab. 5", "Monitor 2007, tab. 13", "Monitor 2008, tab. 9",
              "Monitor 2009, tab. 10", "Monitor 2010, tab. 4.3", "Monitor 2011, tab. 4.3", "Monitor 2013, tab. 4.3",
              "Monitor 2014, tab. 4.3", "Monitor 2014, tab. 4.5", "Monitor 2017, tab. 4.6", "Monitor 2017, tab. 4.7",
              "Monitor 2020, tab. 4.3", "Monitor 2020, tab. 4.5", "SSB 2021, fig. 4", "SSB 28.11.2024, fig. 3"],
    "merknad": "Kull 2015 er publisert for Troms og Finnmark samlet. Kull 1999, 2013, 2014 og 2016–2018 er ikke publisert "
               "per fylke med hele kullet som nevner. Finnmark kull 2019, fylke: «over 90 %».",
}

# ── B. Landet, lengre botid ──
LANG = {
    "botid": [5, 8, 10, 12, 14],
    "kull": {
        "2003": [69, 55, 48, None, None], "2005": [73, 60, 54, None, None], "2007": [77, 64, 57, None, None],
        "2010": [78, 60, 53, 47, 43], "2012": [82, 64, 56, 50, None], "2014": [81, 61, 53, None, None],
        "2016": [81, 61, None, None, None],
    },
    "kilde": "SSB 2021, fig. 2 (kull 2003 og 2005); Monitor 2020, tab. 3.1 (kull 2007); SSB 28.11.2024, fig. 2 (kull 2010–2016)",
    "storrelse": [  # fem år, kull 2007–2012, Monitor 2020 tab. 4.10
        {"l": "100 000 innbyggere eller flere", "lo": 89, "hi": 92},
        {"l": "2 000–4 999 innbyggere", "lo": 59, "hi": 73},
        {"l": "Under 2 000 innbyggere", "lo": 48, "hi": 73},
    ],
}

# ── C. Netto bevaring, pseudokohorter SSB 10598 (start ved ett års botid) ──
NETTO = {
    "botid": [5, 10, 15, 20],
    "kullspenn": ["2003–2020", "2003–2015", "2003–2010", "2003–2005"],
    "grupper": [
        {"navn": "Ti flyktningland", "landet": [96, 91, 86, 84], "nn": [65, 39, 30, 19],
         "nordland": [64, 37, 26, 18], "tf": [65, 42, 35, 20], "nn_spenn": ["43–76", "26–49", "19–38", "16–22"],
         "relativ": [68, 43, 35, 23]},
        {"navn": "Alle innvandrere", "landet": [80, 71, 69, 73], "nn": [70, 51, 46, 38],
         "nordland": [70, 51, 45, 36], "tf": [69, 52, 48, 38], "nn_spenn": ["58–76", "45–58", "39–49", "34–40"]},
        {"navn": "Polen og Litauen", "landet": [84, 71, 69, 74], "nn": [78, 60, 57, 52], "smaa20": True},
        {"navn": "Sverige", "landet": [65, 52, 49, 54], "nn": [63, 49, 46, 50], "smaa20": True},
        {"navn": "Russland", "landet": [85, 82, 83, 85], "nn": [64, 50, 41, 36]},
        {"navn": "Filippinene og Thailand", "landet": [73, 72, 75, 83], "nn": [91, 89, 89, 86]},
    ],
    "flyktningland": "Syria, Eritrea, Somalia, Afghanistan, Irak, Iran, Sudan, Etiopia, Myanmar og Kongo",
    "kilde": "SSB 10598, egen beregning (pseudokohorter, veid over innvandringskullene)",
}

# ── Fafo-rapport 2025:14 og SSB 06318 ──
FAFO = {
    "flyttet10_nn": 70, "flyttet10_trondelag": 50, "flyttet10_landet_2010": 47,
    "landsdel_netto": {"nn": 44.8, "teller": 3746, "nevner": 8367, "trondelag": 72.3, "vestlandet": 81.0, "ostlandet": 132.2},
    "andel_bosatt_nn": 15, "andel_flyttere_fra_nn": 23, "til_ostlandet": 64, "sentralitet6": 80,
    "kilde": "Fafo-rapport 2025:14 «Flytting etter bosetting» (Kjeøy mfl.), s. 33–44",
}
GRUNN = {
    "rader": [{"l": "Flukt", "v": 84.5}, {"l": "Familie", "v": 76.2}, {"l": "Arbeid", "v": 60.8}, {"l": "Utdanning", "v": 37.4}],
    "i_alt": 69.4,
    "kilde": "SSB 06318: ikke-nordiske førstegangsinnvandrere 1990–2025 som fortsatt bodde i Norge ved utgangen av 2025",
}
BOSETTING = {
    "aar": 2025, "nn": 2340, "landet": 12596, "kollektiv_nn": 2158,
    "fylker": {"Nordland": 1258, "Troms": 673, "Finnmark": 409}, "anmodet_2026_nn": 2366, "anmodet_2026_landet": 13000,
    "kilde": "IMDi, nøkkeltall for bosetting 2025 og anmodning 2026",
}
IMDI5 = {"nn": 66.8, "landet": 84.4, "fra": 2021, "til": 2026,
         "kilde": "IMDi «Innvandrernes botid»: botid 5–9 år 1.1.2026 delt på botid 0–4 år 1.1.2021"}


def les(navn):
    f = IMDI / navn
    if not f.exists():
        print(f"ERROR: mangler {f}. Kjør analyse/bofasthet/skript/hent_imdi.py først.", file=sys.stderr)
        sys.exit(1)
    return json.loads(f.read_text(encoding="utf-8"))


def botid10():
    """Andel med botid 10+ av alle innvandrere, per kommune og fylke, 1.1.2021 og 1.1.2026."""
    aar = ["2021", "2026"]

    def tell(rader, nøkkel):
        ut = {}
        for r in rader:
            if r["vreg3"] != "alle" or r["aar"] not in aar or r["botid4"] not in ("10+", "alle"):
                continue
            try:
                v = int(r["tabellvariabel"])
            except (TypeError, ValueError):
                continue
            ut.setdefault(r[nøkkel], {}).setdefault(r["aar"], {})[r["botid4"]] = v
        return ut

    def post(d):
        o = []
        for a in aar:
            t, n = d.get(a, {}).get("10+"), d.get(a, {}).get("alle")
            o += [round(100 * t / n, 1) if t is not None and n else None, t, n]
        return o  # [andel21, teller21, nevner21, andel26, teller26, nevner26]

    kom = tell(les("befolkning_botid_kommuneNr.json"), "kommuneNr")
    fyl = tell(les("befolkning_botid_fylkeNr.json"), "fylkeNr")
    k = {nr: post(d) for nr, d in sorted(kom.items()) if nr[:2] in NN_FYLKER and d.get("2026")}
    # Fylkene 55 og 56 mangler i IMDis fylketabell for 2020–2023: summer da kommunene (2024-inndeling)
    for nr in NN_FYLKER:
        for a in aar:
            if not fyl.get(nr, {}).get(a, {}).get("alle"):
                ks = [d[a] for knr, d in kom.items() if knr[:2] == nr and a in d]
                fyl.setdefault(nr, {})[a] = {b: sum(x.get(b) or 0 for x in ks) for b in ("10+", "alle")}
    nn = {a: {b: sum(fyl[f][a][b] for f in NN_FYLKER) for b in ("10+", "alle")} for a in aar}
    return {
        "felt": ["andel2021", "teller2021", "nevner2021", "andel2026", "teller2026", "nevner2026"],
        "kommuner": k,
        "fylker": {navn: post(fyl.get(nr, {})) for navn, nr in (("Nordland", "18"), ("Troms", "55"), ("Finnmark", "56"))},
        "nn": post(nn), "landet": post(fyl.get("00", {})),
        "kilde": "IMDi «Innvandrernes botid» (kilde SSB). Botid i Norge, ikke i kommunen.",
    }


ANM_XLSX = HER / "analyse" / "bosetting-2027" / "kilder" / "anmodning-2027.xlsx"   # IMDi, 23.10.2026 (ikke versjonert)
ANM_JSON = HER / "analyse" / "bosetting-2027" / "anmodning_2027_nn.json"            # avledet uttrekk (versjonert)


def anmodning():
    """IMDis anmodning om bosetting 2027 (med anmodning og vedtak 2026) for de 80 kommunene.
    Leser regnearket når det finnes lokalt og lagrer et lite uttrekk; ellers brukes uttrekket."""
    if ANM_XLSX.exists():
        import openpyxl
        wb = openpyxl.load_workbook(ANM_XLSX, read_only=True, data_only=True)
        rader = list(wb["Kommuner"].iter_rows(values_only=True))[1:]
        fylkesark = {r[0]: r for r in wb["Fylker"].iter_rows(values_only=True) if r[0]}
        landet = next(r for r in wb["Fylker"].iter_rows(values_only=True) if r[0] is None and r[1])
        navn = {}
        for m in re.finditer(r'"(\d{4})":\{"navn":"([^"]+)"', DATA_JS.read_text(encoding="utf-8")):
            for d in m.group(2).split(" - "):
                navn.setdefault(re.sub(r"\s*\(.*\)$", "", d).strip().lower(), m.group(1))
        k = {}
        for r in rader:
            if r[0] not in ("Nordland", "Troms", "Finnmark"):
                continue
            nr = navn.get(re.sub(r"\s*\(.*\)$", "", r[1]).strip().lower())
            if not nr:
                print(f"ERROR: fant ikke kommunen {r[1]}", file=sys.stderr); sys.exit(1)
            k[nr] = [r[2] or 0, r[3] or 0, r[4] or 0, (r[5] or 0) + (r[6] or 0), r[0]]
        ut = {"aar": 2027, "dato": "2026-10-23", "felt": ["anm2027", "anm2026", "ved2026", "em2027"],
              "kommuner": {nr: v[:4] for nr, v in sorted(k.items())},
              "fylker": {f: [sum(v[i] for v in k.values() if v[4] == f) for i in range(4)] for f in ("Nordland", "Troms", "Finnmark")},
              "landet": [landet[1], landet[3], landet[4], landet[2]],
              "kilde": "IMDi, anmodning om bosetting av flyktninger per kommune 2027 (23.10.2026)"}
        for f, s in ut["fylker"].items():  # kontroll mot fylkesarket
            if s[0] != fylkesark[f][1] or s[1] != fylkesark[f][3] or s[2] != fylkesark[f][4]:
                print(f"ERROR: {f} summerer ikke til fylkesarket: {s} mot {fylkesark[f]}", file=sys.stderr); sys.exit(1)
        ANM_JSON.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        ut = json.loads(ANM_JSON.read_text(encoding="utf-8"))
    ut["nn"] = [sum(v[i] for v in ut["kommuner"].values()) for i in range(4)]
    if len(ut["kommuner"]) != 80 or ut["nn"][1] != BOSETTING["anmodet_2026_nn"]:
        print(f"ERROR: anmodningen gir {len(ut['kommuner'])} kommuner og {ut['nn'][1]} for 2026", file=sys.stderr); sys.exit(1)
    return ut


def main():
    anm = anmodning()
    b10 = botid10()
    if len(b10["kommuner"]) != 80:
        print(f"ERROR: forventet 80 kommuner, fikk {len(b10['kommuner'])}", file=sys.stderr); sys.exit(1)
    payload = {
        "hentet": "2026-10-23",
        "kull5": KULL5, "lang": LANG, "netto": NETTO, "fafo": FAFO, "grunn": GRUNN,
        "bosetting": BOSETTING, "imdi5": IMDI5, "botid10": b10, "anmodning": anm,
        "status": {"dato": "2026-10-23", "tekst": "Ingen høringsnotat eller lovforslag om flytteforbud er publisert."},
    }
    html = DATA_JS.read_text(encoding="utf-8")
    js_lit = "const BOFAST_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* BOFAST_DATA BEGIN */", "/* BOFAST_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in html:
        new = re.sub(r"/\* BOFAST_DATA BEGIN \*/.*?/\* BOFAST_DATA END \*/", lambda _m: block, html, flags=re.DOTALL)
    elif "/* UNG_DATA END */" in html:
        new = html.replace("/* UNG_DATA END */", "/* UNG_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret UNG_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(new, encoding="utf-8")
    print(f"Injected BOFAST_DATA ({len(js_lit)} tegn); NN botid 10+ 2026: {b10['nn'][3]} %, landet {b10['landet'][3]} %; anmodning 2027 NN {anm['nn'][0]} av {anm['landet'][0]}")


if __name__ == "__main__":
    main()
