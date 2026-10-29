"""Bygger data/opptak.json: helseforetak og lokalsykehus (somatikk) for de 80 kommunene.

Fordelingen er utledet med opptak_los.py: den eneste fordelingen av kommuner (Lurøy delt på grunnkretser)
som gir nøyaktig SSB 13982-befolkningen per lokalsykehusområde 2024, 2025 og 2026 (se notater/data.md).
HF-nivået er i tillegg kontrollert mot UNNs egen kommuneliste (unn.no/om-oss, 1.1.2025, 24 kommuner, 195 499).
Kjør: python -X utf8 opptak_bygg.py
"""
import json, os
import opptak_los as O
from ssb import RAA, UT

HF = {"S01": "FIN", "S02": "FIN", "S03": "UNN", "S04": "UNN", "S05": "UNN", "S06": "NLSH", "S07": "NLSH",
      "S08": "NLSH", "S09": "HSYK", "S10": "HSYK", "S11": "HSYK"}
NAVN = {"S01": "Hammerfest", "S02": "Kirkenes", "S03": "Harstad", "S04": "Narvik", "S05": "Tromsø", "S06": "Bodø",
        "S07": "Lofoten (Gravdal)", "S08": "Vesterålen (Stokmarknes)", "S09": "Mo i Rana", "S10": "Mosjøen",
        "S11": "Sandnessjøen"}

los = json.load(open(os.path.join(RAA, "opptak_losninger.json"), encoding="utf-8"))
assert len(los["2024,2025"]["losninger"]) == 1 and len(los["2026"]["losninger"]) == 1, "fordelingen er ikke entydig"
A = {**los["2024,2025"]["faste"], **los["2024,2025"]["losninger"][0]}
B = {**los["2026"]["faste"], **los["2026"]["losninger"][0]}
K = json.load(open(os.path.join(RAA, "kommuner80.json"), encoding="utf-8"))

MERK = {
    "1834": "Delt: fastlandet (grunnkretsene Røytvik, Klevhals–Bratlandselv, Bratlandselv–Olvik, Kvinen, Konsvik, "
            "Aspdal–Rødøy; 548 innb. 1.1.2026) til Mo i Rana, øyene (Lovund, Onøy, Kvarøy, Sleneset m.fl.; 1 405 innb.) "
            "til Sandnessjøen. Utledet av SSB 13982 og grunnkretstall (SSB 04317); entydig løsning, men ikke bekreftet i tekstkilde.",
    "5512": "Hovedsakelig Harstad. SSB 13982 regner 734–835 innbyggere fra UNN Harstads kommuner til Narvik (2024–2026). "
            "Hvilken kommune/del er ikke fastslått; Tjeldsund er mest sannsynlig, men ingen grunnkretskombinasjon passer alle tre år.",
    "1824": "Til Mosjøen t.o.m. 2025. Fra 1.10.2025 er akutt- og døgnfunksjonene i somatikk flyttet fra Mosjøen; "
            "Helse Nord vedtok at Vefsn legges til Mo i Rana (indremedisin). SSB 13982 2026 bekrefter.",
    "1825": "Til Mosjøen t.o.m. 2025; fra 1.10.2025 Sandnessjøen (Helse Nord-vedtak 2025, indremedisin). SSB 13982 2026 bekrefter.",
    "1826": "Til Mosjøen t.o.m. 2025; fra 1.10.2025 Sandnessjøen (Helse Nord-vedtak 2025, indremedisin). SSB 13982 2026 bekrefter.",
    "1811": "Helgelandssykehuset (Sandnessjøen) i SSB 13982, ikke Helse Nord-Trøndelag/Namsos.",
    "1871": "Nordlandssykehuset Vesterålen, ikke UNN Harstad.",
    "1851": "UNN (Narvik), ikke Nordlandssykehuset; bekreftet av unn.no.",
    "1853": "UNN (Narvik); bekreftet av unn.no.",
    "1806": "UNN (Narvik); bekreftet av unn.no.",
    "1875": "Nordlandssykehuset Bodø (også tidligere Tysfjord vest).",
    "1856": "Bodø, ikke Lofoten.",
    "1857": "Bodø, ikke Lofoten.",
    "5546": "UNN Tromsø, ikke Finnmarkssykehuset.",
    "5614": "Finnmarkssykehuset Hammerfest, ikke UNN.",
    "5610": "Hammerfest.",
    "5624": "Kirkenes.", "5626": "Kirkenes.", "5628": "Kirkenes.",
    "5516": "Harstad.", "5518": "Harstad.", "5522": "Harstad.", "5514": "Harstad.",
}

ut = {}
for k in K:
    nr = str(k["nr"])
    if nr == "1834":
        a, b = "S09", "S09"
    else:
        a, b = A[nr], B[nr]
    rad = {"hf": HF[b], "sykehus": NAVN[b], "ssb_kode": b}
    if a != b:
        rad["sykehus_2024_2025"] = NAVN[a]
    if nr == "1834":
        rad["delt"] = {"Mo i Rana": "fastlandet", "Sandnessjøen": "øyene"}
    if nr == "5512":
        rad["delt"] = {"Harstad": "hovedsakelig", "Narvik": "trolig en mindre del (734–835 innb., ikke stedfestet)"}
    if nr in MERK:
        rad["merknad"] = MERK[nr]
    rad["navn"] = k["navn"]
    ut[nr] = rad

doc = {
    "kilde": "SSB 13982 Befolkning per opptaksområde i spesialisthelsetjenesten (kodeliste vs_HelseOpptakSom, "
             "somatikk, lokalsykehus S01–S11), sammenholdt med SSB 07459 (folketall per kommune 1.1.) og SSB 04317 "
             "(grunnkretser, Lurøy). Fordelingen er den eneste som gir SSBs tall nøyaktig 2024, 2025 og 2026. "
             "HF-nivå kontrollert mot unn.no/om-oss (24 kommuner, 195 499 innb. 1.1.2025). Helgeland-endringen 2025 mot Helgelandssykehusets "
             "nyhet 5.9.2025 og Helse Nords vedtak (styresak 22-2025). Hentet 29.10.2026.",
    "gjelder": "Somatikk, 2026-inndeling (etter at Mosjøen mistet akuttfunksjonene 1.10.2025). Feltet "
               "sykehus_2024_2025 viser tidligere lokalsykehus der det er endret.",
    "hf_koder": {"UNN": "Universitetssykehuset Nord-Norge HF", "NLSH": "Nordlandssykehuset HF",
                 "HSYK": "Helgelandssykehuset HF", "FIN": "Finnmarkssykehuset HF"},
    "kommuner": ut,
}
os.makedirs(UT, exist_ok=True)
json.dump(doc, open(os.path.join(UT, "opptak.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Kontroll: summer per område mot SSB 13982
P, M = O.P, O.MAAL
for aar in ("2024", "2025", "2026"):
    S = {}
    for nr, r in ut.items():
        kode = r["ssb_kode"] if aar == "2026" else [c for c, n in NAVN.items() if n == r.get("sykehus_2024_2025", r["sykehus"])][0]
        if nr == "1834":
            S[kode] = S.get(kode, 0) + P["1834f"][aar]
            S["S11"] = S.get("S11", 0) + P["1834o"][aar]
        else:
            S[kode] = S.get(kode, 0) + P[nr][aar]
    S["S04"] += O.REST_S04[aar]; S["S03"] -= O.REST_S04[aar]
    avvik = {c: S.get(c, 0) - M[aar][c] for c in NAVN if S.get(c, 0) != M[aar][c]}
    print(aar, "avvik mot SSB 13982:", avvik or "ingen")
print("HF-summer 2025:", {h: sum(P[n]["2025"] for n, r in ut.items() if r["hf"] == h) for h in ("UNN", "NLSH", "HSYK", "FIN")})
print("Kommuner:", len(ut))
