#!/usr/bin/env python3
"""Konjunkturbarometer for Nord-Norge 2026 (tema 08 og tema 12) → KONJ_DATA i assets/data.js.

Kilder:
  - Konjunkturbarometer for Nord-Norge 2026 (Kunnskapsbanken, SpareBank 1 Nord-Norge; skrevet av KPB, data per medio
    oktober 2026). Sidetall i feltene «side». Tallene for næringene bygger på Proff Forvalt (hovedenhet i Nord-Norge,
    driftsinntekter over 1 million kroner i 2024 og 2025), sysselsetting på SSB. Helsepersonell etter fødeland er KPBs
    beregning på Microdata.no og kan ikke etterprøves med åpne data. Verdiene er avlest fra figurene i rapporten.
  - SSB 13470 for sysselsatte i bygg og anlegg, beregnet på nytt (analyse/konjunktur/skript/bygg_anlegg.py).
Vurdering og plan: analyse/konjunktur/PLAN.md.
Kjør:  python fetch_konjunktur.py
"""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HER = Path(__file__).parent
DATA_JS = HER / "assets" / "data.js"
A = HER / "analyse" / "konjunktur" / "data"
KB = "Konjunkturbarometer for Nord-Norge 2026"

# ── Næringene, s. 20–22. vurdering: [utvikling 2026, utsikter 2027] med 1 = positiv, 0 = nøytral, -1 = negativ ──
# oms = omsetningsvekst 2024–2025, margin = driftsmargin 2025, neg = andel med negativt driftsresultat 2025,
# syss = sysselsettingsvekst 2024–2025 (SSB), alle i prosent. None = ikke oppgitt i rapporten.
NAERINGER = [
    {"kode": "F", "navn": "Fiskeflåten", "vurdering": [1, 1], "oms": 19.8, "margin": 24.7, "neg": 19.4, "syss": -1.7},
    {"kode": "FI", "navn": "Fiskeindustri", "vurdering": [0, 0], "oms": None, "margin": None, "neg": None, "syss": None},
    {"kode": "H", "navn": "Havbruk", "vurdering": [1, 1], "oms": 13.3, "margin": 12.8, "neg": 20.9, "syss": 6.1},
    {"kode": "KI", "navn": "Kraftforedlende industri", "vurdering": [0, 0], "oms": 2.3, "margin": 10.5, "neg": 11.1, "syss": 0.4},
    {"kode": "V", "navn": "Varehandel", "vurdering": [1, 1], "oms": 8.2, "margin": 3.1, "neg": 23.3, "syss": -0.6},
    {"kode": "R", "navn": "Reiseliv", "vurdering": [1, 1], "oms": 8.4, "margin": 7.4, "neg": 29.4, "syss": 3.2},
    {"kode": "A", "navn": "Anlegg", "vurdering": [1, 1], "oms": 6.9, "margin": 5.5, "neg": 25.4, "syss": 0.7},
    {"kode": "BN", "navn": "Byggnæring", "vurdering": [-1, -1], "oms": 2.7, "margin": 3.2, "neg": 27.1, "syss": -1.8},
    {"kode": "T", "navn": "Tjenesteyting", "vurdering": [0, 0], "oms": 7.0, "margin": 17.6, "neg": 22.2, "syss": 0.5},
    {"kode": "NE", "navn": "Næringseiendom", "vurdering": [0, 0], "oms": -5.2, "margin": 32.2, "neg": 12.3, "syss": 4.3},
    {"kode": "OG", "navn": "Leverandører til olje og gass", "vurdering": [1, 0], "oms": 22.7, "margin": None, "neg": None, "syss": 3.3},
]

# ── Bygg og anlegg, s. 46–50 (tall SSB beregner vi selv; disse er rapportens egne) ──
BYGG_KB = {"arbeidsinnvandrere": {"aar": [2020, 2021, 2025], "antall": [2313, 2752, 2478], "side": 48, "kilde": "Microdata.no, KPB"},
           "rapport_endring": {"nn": -1037, "nn_pst": -4.8, "troms": -7.5, "finnmark": 0.9, "nordland": -4.8, "bygg": -7.9, "anlegg": 2.8, "side": 46},
           "investeringer": {"prosjekter": 3300, "mrd": 850, "periode": "2025–2032", "modne_mrd": 432, "realendring_pst": -3, "side": 50,
                             "kilde": "Investeringstelleren 2025, gjengitt i rapporten (ikke kontrollert mot primærkilden)"},
           "statnett": {"dato": "2026-04-22", "mrd_i_fare": 150, "side": 50,
                        "kilde": "Statnett, nyhet 22.4.2026: reservasjon av nettkapasitet for nytt forbruk over 5 MW nord for Svartisen satt på hold. "
                                 "Beløpet er rapportens anslag (ikke kontrollert)"}}

# ── Helsepersonell etter fødeland, s. 82–87 (Microdata.no, KPB). Leger = allmennleger og spesialister;
#    sykepleiere = sykepleiere, spesialsykepleiere og jordmødre; hovedarbeidsforhold i Nord-Norge ──
HELSEPERS = {"aar": [2015, 2019, 2025],
             "leger": {"norge": [1435, 1740, 2115], "utland": [466, 525, 614]},
             "sykepleiere": {"norge": [7811, 8318, 8166], "utland": [847, 945, 1172]},
             "botid_leger": {"grupper": ["0–4 år", "5–9 år", "10–19 år", "20–29 år", "30 år eller mer"], "pst": [9, 18, 36, 31, 6]},
             "statsborger_leger": {"Troms": 93, "Finnmark": 89, "Nordland": 88},
             "norskfodt_fylke": {"leger": {"Troms": 82, "Nordland": 75, "Finnmark": 73}, "sykepleiere": {"Nordland": 90, "Troms": 86, "Finnmark": 82}},
             "utd_norge_leger": 41, "side": "82–87",
             "kilde": f"{KB}, s. 82–87: KPBs beregning på Microdata.no (hovedarbeidsforhold i Nord-Norge)"}


def main():
    ba = json.loads((A / "bygg_anlegg.json").read_text(encoding="utf-8"))
    h = HELSEPERS
    # Kontroll mot rapportens egne summer (s. 82–83): om lag 1 300 → 1 800 utenlandsfødte, +14,3 % i alt, +36 % utenlandsfødte
    u = [h["leger"]["utland"][i] + h["sykepleiere"]["utland"][i] for i in range(3)]
    t = [u[i] + h["leger"]["norge"][i] + h["sykepleiere"]["norge"][i] for i in range(3)]
    assert round(100 * (t[2] / t[0] - 1), 1) == 14.3 and round(100 * (u[2] / u[0] - 1)) == 36, (t, u)
    assert sum(h["botid_leger"]["pst"]) == 100
    payload = {"hentet": "2026-11-19", "kilde": KB + " (Kunnskapsbanken, SpareBank 1 Nord-Norge; KPB)",
               "naeringer": NAERINGER, "naering_kilde": f"{KB}, s. 20–22. Proff Forvalt: hovedenhet i Nord-Norge, driftsinntekter over 1 million kroner i 2024 og 2025. Sysselsetting: SSB",
               "bygg": ba, "bygg_kb": BYGG_KB, "helsepersonell": h}
    i22, i25 = ba["aar"].index(2022), ba["aar"].index(2025)
    nn = ba["serie"]["Nord-Norge"]
    print("Bygg og anlegg NN 2022→2025:", nn["bygg"][i22] + nn["anlegg"][i22], "→", nn["bygg"][i25] + nn["anlegg"][i25])
    print("Utenlandsfødte leger og sykepleiere:", u, "i alt", t)

    js = DATA_JS.read_text(encoding="utf-8")
    lit = "const KONJ_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    block = f"/* KONJ_DATA BEGIN */\n{lit}\n/* KONJ_DATA END */"
    if "/* KONJ_DATA BEGIN */" in js:
        js = re.sub(r"/\* KONJ_DATA BEGIN \*/.*?/\* KONJ_DATA END \*/", lambda _m: block, js, flags=re.DOTALL)
    elif "/* HELSE_DATA END */" in js:
        js = js.replace("/* HELSE_DATA END */", "/* HELSE_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret HELSE_DATA END", file=sys.stderr); sys.exit(1)
    DATA_JS.write_text(js, encoding="utf-8")
    print(f"Injected KONJ_DATA ({len(lit)} tegn)")


if __name__ == "__main__":
    main()
