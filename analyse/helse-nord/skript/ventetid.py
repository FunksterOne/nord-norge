"""Ventetider, fristbrudd, tid til tjenestestart og passert planlagt tid i spesialisthelsetjenesten.

Kilde: Norsk pasientregister (NPR), FHI. Nedlastingssiden
https://www.fhi.no/he/npr/statistikk-npr/nedlasting-av-data/ lenker til Excel-filer per tertial og år.
Ventelistestatistikken finnes ikke i FHIs Statistikk Open API (kilden «npr» har bare aktivitetstall),
og heller ikke hos SSB.

Bruk:
    python ventetid.py          # henter filene hvis de mangler, bearbeider
    python ventetid.py --hent   # henter alle filene på nytt

Rådata: kilder/data/ventetid/ (gitignorert). Utdata: data/ventetid.csv (langt format).
Enhetsutvalg: landet, de fire RHF-ene, «Private» (private institusjoner samlet, bare i
ventelistefilene) og de fire HF-ene i Helse Nord.
"""
import csv, hashlib, json, sys, urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
HN = Path(__file__).resolve().parents[1]
RAA = HN / "kilder" / "data" / "ventetid"
UT = HN / "data" / "ventetid.csv"
BASE = "https://www.fhi.no/globalassets/dokumenterfiler/helseregistre/npr-kpr/ventetider-for-nedlasting/"
FILER = {
    "tertial": "2.tert2026_ventetider_henvisninger_fristbrudd.xlsx",
    "aar": "ar_2025_ventetider_henvisninger.xlsx",
    "maaned": "september2026_ventetider_henvisninger_fristbrudd.xlsx",  # lagres som rådata, brukes ikke i CSV
    "ttt_tertial": "tid-til-tjenestestart_2.tert2026.xlsx",
    "ttt_aar": "tid-til-tjenestestart_ar2025.xlsx",
    "ppt": "passert-planlagt-tid_2tert2026.xlsx",
}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) affectum-analyse"}

# Navnevarianter i filene -> kanonisk navn, enhetstype, overordnet RHF
HF_NAVN = {
    "Universitetssykehuset Nord-Norge": "Universitetssykehuset Nord-Norge HF",
    "Universitetssykehuset Nord-Norge HF": "Universitetssykehuset Nord-Norge HF",
    "Universitetssykehuset i Nord-Norge HF": "Universitetssykehuset Nord-Norge HF",
    "Nordlandssykehuset": "Nordlandssykehuset HF",
    "Nordlandssykehuset HF": "Nordlandssykehuset HF",
    "Helgelandssykehuset": "Helgelandssykehuset HF",
    "Helgelandssykehuset HF": "Helgelandssykehuset HF",
    "Finnmarkssykehuset": "Finnmarkssykehuset HF",
    "Finnmarkssykehuset HF": "Finnmarkssykehuset HF",
    "Helse Finnmark HF": "Finnmarkssykehuset HF",  # eldre navn, brukes i TTT-filene for 2012–2013
}
RHF_NAVN = {
    "Norge": ("Landet", "land"),
    "Helse Nord": ("Helse Nord RHF", "RHF"), "Helse Nord RHF": ("Helse Nord RHF", "RHF"),
    "Helse Midt-Norge": ("Helse Midt-Norge RHF", "RHF"), "Helse Midt-Norge RHF": ("Helse Midt-Norge RHF", "RHF"),
    "Helse Vest": ("Helse Vest RHF", "RHF"), "Helse Vest RHF": ("Helse Vest RHF", "RHF"),
    "Helse Sør-Øst": ("Helse Sør-Øst RHF", "RHF"), "Helse Sør-Øst RHF": ("Helse Sør-Øst RHF", "RHF"),
    "Private": ("Private institusjoner", "privat"),
}
SEKTOR = {"Alle sektorer": "Alle sektorer", "Somatikk": "Somatikk",
          "Psykisk helsevern voksne": "Psykisk helsevern voksne",
          "Psykisk helsevern barn og unge": "Psykisk helsevern barn og unge",
          "Rusbehandling": "Rusbehandling (TSB)"}  # «Ukjent» utelates
KOL = ["periode", "periodetype", "aar", "tertial", "enhet", "enhetstype", "rhf", "fagomrade",
       "indikator", "verdi", "enhet_maal", "kildefil"]


def hent(tving=False):
    RAA.mkdir(parents=True, exist_ok=True)
    logg_fil = RAA / "hentelogg.json"
    logg = json.loads(logg_fil.read_text(encoding="utf-8")) if logg_fil.exists() else {}
    for f in FILER.values():
        p = RAA / f
        if p.exists() and not tving:
            continue
        req = urllib.request.Request(BASE + f, headers=UA)
        b = urllib.request.urlopen(req, timeout=300).read()
        if not b.startswith(b"PK"):
            raise RuntimeError(f"{f}: ikke en xlsx-fil")
        p.write_bytes(b)
        logg[f] = {"url": BASE + f, "hentet": date.today().isoformat(), "bytes": len(b),
                   "sha256": hashlib.sha256(b).hexdigest()}
        print("hentet", f, len(b))
    logg_fil.write_text(json.dumps(logg, ensure_ascii=False, indent=1), encoding="utf-8")


def enhet_rhf(navn):
    return RHF_NAVN.get(str(navn).strip())


def tertialnr(s):  # «2. tert 2026» / «2. tertial 2026»
    return int(str(s).strip()[0])


def rad(rows, periode, ptype, aar, tert, enhet, etype, rhf, fag, ind, verdi, maal, kilde):
    if verdi is None or pd.isna(verdi):
        return
    rows.append([periode, ptype, int(aar), tert if tert else "", enhet, etype, rhf, fag, ind,
                 round(float(verdi), 4), maal, kilde])


def venteliste_tertial(rows):
    f = FILER["tertial"]
    x = pd.read_excel(RAA / f, sheet_name=None)
    spes = [  # ark, enhetskolonne, hf-nivå?, [(kolonne, indikator, mål)]
        ("Ventetider_Tertial RHF", "RHF", False, [("Ventetid oppstart helsehjelp", "ventetid_pabegynt_gjsn", "dager"),
                                                 ("Ventetid ventende", "ventetid_ventende_gjsn", "dager")]),
        ("Ventetider_Tertial HF", "Behandlingssted", True, [("Ventetid oppstart helsehjelp", "ventetid_pabegynt_gjsn", "dager"),
                                                            ("Ventetid ventende", "ventetid_ventende_gjsn", "dager")]),
        ("Henvisninger_Tertial RHF", "Behandlingssted", False, [("Antall nyhenviste", "antall_nyhenviste", "antall"),
                                                                ("Antall oppstart helsehjelp", "antall_pabegynt", "antall"),
                                                                ("Antall ventende", "antall_ventende", "antall")]),
        ("Henvisninger_Tertial HF", "Behandlingssted", True, [("Antall nyhenviste", "antall_nyhenviste", "antall"),
                                                              ("Antall oppstart helsehjelp", "antall_pabegynt", "antall"),
                                                              ("Antall ventende", "antall_ventende", "antall")]),
        ("Fristbrudd_Tertial RHF", "Behandlingssted", False, [("Andel fristbrudd oppstart helsehjelp", "andel_fristbrudd_pabegynt", "prosent"),
                                                              ("Andel fristbrudd for ventende", "andel_fristbrudd_ventende", "prosent"),
                                                              ("Antall fristbrudd oppstart helsehjelp", "antall_fristbrudd_pabegynt", "antall"),
                                                              ("Antall fristbrudd for ventende", "antall_fristbrudd_ventende", "antall")]),
    ]
    for ark, ekol, hf, mål in spes:
        df = x[ark]
        for _, r in df.iterrows():
            fag = SEKTOR.get(r["Fagområde"])
            if not fag:
                continue
            if hf:
                e = HF_NAVN.get(str(r[ekol]).strip())
                if not e:
                    continue
                enhet, etype, rhf = e, "HF", "Helse Nord RHF"
            else:
                er = enhet_rhf(r[ekol])
                if not er:
                    continue
                enhet, etype = er
                rhf = enhet if etype == "RHF" else ""
            t = tertialnr(r["Tertial"])
            for kol, ind, m in mål:
                rad(rows, f"{r['År']}-T{t}", "tertial", r["År"], t, enhet, etype, rhf, fag, ind, r[kol], m, f)


def venteliste_aar(rows):
    f = FILER["aar"]
    x = pd.read_excel(RAA / f, sheet_name=None)
    spes = [
        ("Ventetider_År RHF", "Behandlingssted", False, [("Ventetid påbegynt helsehjelp", "ventetid_pabegynt_gjsn", "dager")]),
        ("Ventetider_År HF", "Behandlingssted", True, [("Ventetid påbegynt helsehjelp", "ventetid_pabegynt_gjsn", "dager")]),
        ("Henvisninger_År RHF", "Behandlingssted", False, [("Antall nyhenviste", "antall_nyhenviste", "antall"),
                                                           ("Antall påbegynt helsehjelp", "antall_pabegynt", "antall")]),
        ("Henvisninger_År HF", "Behandlingssted", True, [("Antall nyhenviste", "antall_nyhenviste", "antall"),
                                                         ("Antall påbegynt helsehjelp", "antall_pabegynt", "antall")]),
        ("Fristbrudd_År RHF", "Behandlingssted", False, [("Andel fristbrudd påbegynt helsehjelp", "andel_fristbrudd_pabegynt", "prosent"),
                                                         ("Andel fristbrudd for ventende", "andel_fristbrudd_ventende", "prosent"),
                                                         ("Antall fristbrudd påbegynt helsehjelp", "antall_fristbrudd_pabegynt", "antall")]),
    ]
    for ark, ekol, hf, mål in spes:
        for _, r in x[ark].iterrows():
            fag = SEKTOR.get(r["Fagområde"])
            if not fag:
                continue
            if hf:
                e = HF_NAVN.get(str(r[ekol]).strip())
                if not e:
                    continue
                enhet, etype, rhf = e, "HF", "Helse Nord RHF"
            else:
                er = enhet_rhf(r[ekol])
                if not er:
                    continue
                enhet, etype = er
                rhf = enhet if etype == "RHF" else ""
            for kol, ind, m in mål:
                rad(rows, str(r["År"]), "år", r["År"], None, enhet, etype, rhf, fag, ind, r[kol], m, f)


TTT_GRUPPE = {"Alle": "Alle utredninger/behandlinger", "Alle utredninger": "Alle utredninger",
              "Alle behandlinger": "Alle behandlinger"}


def ttt(rows):
    for nøkkel, ptype in (("ttt_tertial", "tertial"), ("ttt_aar", "år")):
        f = FILER[nøkkel]
        x = pd.read_excel(RAA / f, sheet_name=["RHFogNorge", "HF"])
        for ark, df in x.items():
            df = df.rename(columns={"tjeneste": "Tjeneste"})
            df = df[df["Tjeneste"].isin(TTT_GRUPPE)]
            for _, r in df.iterrows():
                if ark == "HF":
                    e = HF_NAVN.get(str(r["Helseforetak"]).strip())
                    if not e:
                        continue
                    enhet, etype, rhf = e, "HF", "Helse Nord RHF"
                else:
                    er = enhet_rhf(r["Enheter"])
                    if not er or er[1] == "privat":
                        continue
                    enhet, etype = er
                    rhf = enhet if etype == "RHF" else ""
                aar = int(r["År"])
                if ptype == "tertial":
                    t = int(r["TertialNr"]); periode = f"{aar}-T{t}"
                else:
                    t = None; periode = str(aar)
                fag = "TTT: " + TTT_GRUPPE[r["Tjeneste"]]
                rad(rows, periode, ptype, aar, t, enhet, etype, rhf, fag, "ttt_gjsn",
                    r["Gjennomsnitt tid til tjenestestart"], "dager", f)
                rad(rows, periode, ptype, aar, t, enhet, etype, rhf, fag, "ttt_median",
                    r["Median tid til tjenestestart"], "dager", f)
                rad(rows, periode, ptype, aar, t, enhet, etype, rhf, fag, "ttt_antall",
                    r["Antall ordinært avviklede"], "antall", f)


MND = {"apr": (4, 1), "aug": (8, 2), "des": (12, 3)}


def ppt(rows):
    f = FILER["ppt"]
    df = pd.read_excel(RAA / f)
    df = df[df["Fagområde"] == "Alle fagområder"].copy()
    # UNN har to rader for aug 2026; den ene har Antall=1 og Andel=1 (åpenbart en restpost). Behold største.
    df = df.sort_values("Antall").drop_duplicates(["Periode", "RHF-HF"], keep="last")
    for _, r in df.iterrows():
        navn = str(r["RHF-HF"]).strip()
        e = HF_NAVN.get(navn)
        if e:
            enhet, etype, rhf = e, "HF", "Helse Nord RHF"
        else:
            er = enhet_rhf(navn)
            if not er or er[1] == "privat":
                continue
            enhet, etype = er
            rhf = enhet if etype == "RHF" else ""
        m, aar = str(r["Periode"]).split()
        mn, t = MND[m]
        periode = f"{aar}-{mn:02d}"
        rad(rows, periode, "øyeblikk", aar, t, enhet, etype, rhf, "Alle fagområder", "ppt_andel",
            r["Andel"] * 100, "prosent", f)
        rad(rows, periode, "øyeblikk", aar, t, enhet, etype, rhf, "Alle fagområder", "ppt_antall",
            r["Antall"], "antall", f)


def main():
    hent(tving="--hent" in sys.argv)
    rows = []
    venteliste_tertial(rows); venteliste_aar(rows); ttt(rows); ppt(rows)
    rekkef = {"land": 0, "RHF": 1, "privat": 2, "HF": 3}
    rows.sort(key=lambda r: (r[8], r[1], r[0], rekkef[r[5]], r[4], r[7]))
    UT.parent.mkdir(parents=True, exist_ok=True)
    with open(UT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(KOL); w.writerows(rows)
    print(f"skrev {len(rows)} rader til {UT}")
    df = pd.DataFrame(rows, columns=KOL)
    print(df.groupby(["indikator", "periodetype"]).agg(fra=("periode", "min"), til=("periode", "max"), n=("verdi", "size")).to_string())


if __name__ == "__main__":
    main()
