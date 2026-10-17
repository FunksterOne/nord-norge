"""Pensjonsforpliktelser og fremskrevet pensjonskostnad for de 80 kommunene → PENSJON_DATA i assets/data.js.

Kjører modellen i analyse/pensjon/fase4_modell.py og bygger en kompakt datablokk:
  - premieavvik og disposisjonsfond 2025 i % av brutto driftsinntekter (SSB 13202 og 12364, kommunekonsern)
  - regnskapsført pensjonskostnad i % av BDI 2025–2050 i tre scenarier (lav, basis, høy)
  - premie og akkumulert premieavvik i % av BDI 2030 per scenario
  - leverandør, amortiseringstid og datagrunnlag (pensjonsnote i årsregnskapet 2025 eller bare KOSTRA)
Grunnlagsdataene hentes på nytt med analyse/pensjon/hent_kostra_*.py; regnskapsnotene ligger i analyse/pensjon/.
"""
import json, re, runpy, sys
from pathlib import Path

ROT = Path(__file__).parent
AN = ROT / "analyse" / "pensjon"
HTML = ROT / "assets" / "data.js"
FYLKER = ("Nordland", "Troms", "Finnmark")
EGNE_KASSER = {"1804": "Bodø Pensjonskasse", "5501": "Tromsø kommunale pensjonskasse", "5503": "Harstad kommunale pensjonskasse"}
SCEN = ("lav", "basis", "hoy")
# Noter som ikke går opp internt: vises, men merkes
SVAK_NOTE = {"1875": "Pensjonsnoten går ikke opp: midlene i noten avviker fra balansen.",
             "1834": "Pensjonsnoten er en posteringsliste uten kostnad og premie; kostnaden er anslått fra KOSTRA."}


def fylke(nr):
    return "Nordland" if nr.startswith("18") else ("Troms" if nr.startswith("55") else "Finnmark")


def r1(v):
    return None if v is None else round(v, 1)


def r2(v):
    # Tre desimaler: unngår at visningen avrunder samme tall ulikt (0,05-grenser) på ulike steder
    return None if v is None else round(v, 3)


def main():
    runpy.run_path(str(AN / "fase4_modell.py"), run_name="__main__")
    M = json.loads((AN / "fase4_resultat.json").read_text(encoding="utf-8"))
    KP = json.loads((AN / "kostra_pensjon.json").read_text(encoding="utf-8"))
    rec = {}
    for f in sorted(AN.glob("regnskap_gruppe*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            rec[r["nr"]] = r
    for f in (AN / "manuelle").glob("*.json"):
        r = json.loads(f.read_text(encoding="utf-8")); rec[r["nr"]] = r

    aar = list(range(2025, 2051))
    G = {x["nr"]: x for x in M["grunnlag"]}
    R = M["resultat"]
    kommuner = {}
    for nr, x in G.items():
        r = rec[nr]
        kasse = EGNE_KASSER.get(nr)
        note = x["kilde"].startswith("note") and r.get("innbetalt_premie") is not None
        url = r.get("kilde_url") or ""
        kommuner[nr] = {
            "bdi": round(x["bdi"] / 1000),                       # 1000 kr
            "pa": r2(x["S25"] / x["bdi"] * 100),                 # akkumulert premieavvik inkl. AGA, % av BDI
            "pa24": r2(x["S24"] / (KP[nr]["2024"]["bdi"] * 1000) * 100) if x["S24"] is not None and KP[nr]["2024"].get("bdi") else None,
            "pa_kr": round(x["S25"] / 1000),
            "df": r2(x["dispfond"] / x["bdi"] * 100),
            "df_kr": round(x["dispfond"] / 1000),
            "R": {s: [r2(R[nr][s][str(t)]["R"] / R[nr][s][str(t)]["bdi"] * 100) for t in aar] for s in SCEN},
            "P30": {s: r2(R[nr][s]["2030"]["P"] / R[nr][s]["2030"]["bdi"] * 100) for s in SCEN},
            "P25": r2(R[nr]["basis"]["2025"]["P"] / x["bdi"] * 100),
            "S30": {s: r2(R[nr][s]["2030"]["S"] / R[nr][s]["2030"]["bdi"] * 100) for s in SCEN},
            "amort": x["amort"],
            "lev": kasse or "KLP",
            "grunnlag": "note" if note else "kostra",
            "svak": SVAK_NOTE.get(nr),
            "url": url if (note and url.startswith("http")) else "",
        }

    def agg(nrs):
        bdi = sum(G[n]["bdi"] for n in nrs)
        ut = {"n": len(nrs), "bdi": round(bdi / 1000),
              "pa": r2(sum(G[n]["S25"] for n in nrs) / bdi * 100),
              "pa_kr": round(sum(G[n]["S25"] for n in nrs) / 1000),
              "df": r2(sum(G[n]["dispfond"] for n in nrs) / bdi * 100)}
        with24 = [n for n in nrs if G[n]["S24"] is not None and KP[n]["2024"].get("bdi")]
        ut["pa24"] = r2(sum(G[n]["S24"] for n in with24) / sum(KP[n]["2024"]["bdi"] * 1000 for n in with24) * 100) if with24 else None
        ut["R"] = {s: [r2(sum(R[n][s][str(t)]["R"] for n in nrs) / sum(R[n][s][str(t)]["bdi"] for n in nrs) * 100) for t in aar] for s in SCEN}
        ut["P30"] = {s: r2(sum(R[n][s]["2030"]["P"] for n in nrs) / sum(R[n][s]["2030"]["bdi"] for n in nrs) * 100) for s in SCEN}
        ut["P25"] = r2(sum(R[n]["basis"]["2025"]["P"] for n in nrs) / bdi * 100)
        ut["S30"] = {s: r2(sum(R[n][s]["2030"]["S"] for n in nrs) / sum(R[n][s]["2030"]["bdi"] for n in nrs) * 100) for s in SCEN}
        ut["pa_over_df"] = sum(1 for n in nrs if G[n]["S25"] > G[n]["dispfond"])
        ut["risiko"] = sorted([n for n in nrs if G[n]["S25"] > G[n]["dispfond"] and G[n]["S25"] / G[n]["bdi"] > 0.10],
                              key=lambda n: -G[n]["S25"] / G[n]["bdi"])
        return ut

    alle = list(G)
    fylker = {f: agg([n for n in alle if fylke(n) == f]) for f in FYLKER}
    landsdel = agg(alle)
    landet = KP["EAK"]["2025"]
    landet_pa = ((landet["premieavvik_eiendel"] or 0) - (landet["premieavvik_gjeld"] or 0)) / landet["bdi"] * 100

    # Flyten i 2025 fra pensjonsnotene (kommunekassen, i hovedsak uten arbeidsgiveravgift)
    med = [r for r in rec.values() if r.get("innbetalt_premie") and r.get("aarets_pensjonskostnad") and r.get("aarets_premieavvik") is not None]
    pf = [r["premiefond_bruk"] for r in rec.values() if r.get("premiefond_bruk")]
    amort = [x["A_impl"] for x in G.values() if x["A_impl"] is not None]
    flyt = {"n": len(med), "premie_mrd": r2(sum(r["innbetalt_premie"] for r in med) / 1e9),
            "kostnad_mrd": r2(sum(r["aarets_pensjonskostnad"] for r in med) / 1e9),
            "nytt_pa_mrd": r2(sum(x["N"] * (1 + x["aga"]) for x in G.values() if x["N"] is not None and x["A_impl"] is not None) / 1e9),
            "amort_mrd": r2(sum(amort) / 1e9), "n_amort": len(amort),
            "premiefond_mrd": r2(sum(pf) / 1e9), "n_premiefond": len(pf),
            "forpl_mrd": r1(sum((KP[n]["2025"]["pensjonsforpliktelse"] or 0) for n in alle) / 1e6),
            "midler_mrd": r1(sum((KP[n]["2025"]["pensjonsmidler"] or 0) for n in alle) / 1e6)}

    P = M["parametre"]
    payload = {
        "aar": aar,
        "kommuner": kommuner, "fylker": fylker, "landsdel": landsdel,
        "meta": {
            "regnskapsaar": 2025,
            "landet_pa": r2(landet_pa),
            "gamma_pct": r1(P["GAMMA"] * 100),
            "vekst_pct": r1(P["G"] * 100),
            "scenarier": {
                "lav":   {"navn": "Lav", "kostnad_pct": 5, "struktur_pct": 0.0, "premiefond_pct": 100},
                "basis": {"navn": "Basis", "kostnad_pct": 10, "struktur_pct": 0.5, "premiefond_pct": 75},
                "hoy":   {"navn": "Høy", "kostnad_pct": r1((P["scenarier"]["hoy"]["u27"] - 1) * 100), "struktur_pct": 1.0, "premiefond_pct": 25},
            },
            "n_note": sum(1 for v in kommuner.values() if v["grunnlag"] == "note"),
            "flyt2025": flyt,
            "pf_median_mot_kostnad": r2(P["median_PF_K"]),
            # Organisering: Finanstilsynet, årsrapporter 2025 og KLPs kvartalsrapport for 2. kvartal 2026
            "org": {
                "klp_kommuner": 77, "klp_solvens_pct": 324, "klp_solvens_per": "30.06.2026",
                "kasser": [
                    {"nr": "1804", "navn": "Bodø Pensjonskasse", "solvens_pct": 150, "ek_innskutt_mill": 91.8},
                    {"nr": "5501", "navn": "Tromsø kommunale pensjonskasse", "solvens_pct": 150, "ek_innskutt_mill": 372.9},
                    {"nr": "5503", "navn": "Harstad kommunale pensjonskasse", "solvens_pct": 159, "ek_innskutt_mill": 310.0},
                ],
                "kommunale_kasser_snitt_pct": 169,
                "klp_reguleringspremie_2025_pct": 4.6, "klp_egenkapitaltilskudd_pct": 0.25,
                "kilde": "Årsrapporter 2025 for pensjonskassene; Finanstilsynet (pensjonskassekonferansen 2026); KLP, kvartalsrapport 2. kvartal 2026",
            },
            "nasjonalt": {"pa_mrd": 63, "premiefond_mrd": 45, "renteulempe_mrd": 2.8,
                          "kilde": "Prop. 94 S (2025–2026) kapittel 8.4"},
            "forholdstall": {"2025": 1.0, "2026": 0.88, "2027": 0.75},
            "egne_kasser": EGNE_KASSER,
            "kilde": "Årsregnskap 2025 (pensjonsnoter); SSB 13202, 12364, 13551 og 12367 (KOSTRA 2025, kommunekonsern); KDDs rundskriv H-3/25, H-4/25 og H-2/26; egne beregninger",
            "sist_oppdatert": "2026-10-17",
        },
    }

    ld = landsdel
    print(f"\nNord-Norge: premieavvik {ld['pa']} % av BDI (2024: {ld['pa24']} %), landet {r2(landet_pa)} %")
    print("  pensjonskostnad % av BDI 2025/2030/2050:", {s: (ld['R'][s][0], ld['R'][s][5], ld['R'][s][-1]) for s in SCEN})
    print(f"  premieavvik > disposisjonsfond: {ld['pa_over_df']} av {ld['n']}; risikogruppe: {len(ld['risiko'])}")

    html = HTML.read_text(encoding="utf-8")
    js_lit = "const PENSJON_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    start, slutt = "/* PENSJON_DATA BEGIN */", "/* PENSJON_DATA END */"
    block = f"{start}\n{js_lit}\n{slutt}"
    if start in html:
        new = re.sub(r"/\* PENSJON_DATA BEGIN \*/.*?/\* PENSJON_DATA END \*/", lambda _m: block, html, flags=re.DOTALL)
    elif "/* GJELD_DATA END */" in html:
        new = html.replace("/* GJELD_DATA END */", "/* GJELD_DATA END */\n" + block, 1)
    else:
        print("ERROR: fant ikke ankeret GJELD_DATA END", file=sys.stderr); sys.exit(1)
    HTML.write_text(new, encoding="utf-8")
    print(f"Injected PENSJON_DATA ({len(js_lit)} tegn)")


if __name__ == "__main__":
    main()
