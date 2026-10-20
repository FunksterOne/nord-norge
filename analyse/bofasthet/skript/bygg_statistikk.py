"""Bygg analyse/bofasthet/statistikk.json fra rådata i kilder/ og manuelle tall i monitor_data.py.

Kjør etter hent_ssb.py, hent_imdi.py og pseudokohort_10598.py:
    python bygg_statistikk.py
"""
import json, collections
from pathlib import Path
import monitor_data as md
from jsonstat import les

ROT = Path(__file__).resolve().parents[1]
K = ROT / "kilder"
NN_FYLKER = {"Nordland", "Troms", "Finnmark", "Troms og Finnmark"}
rec = []


def add(**kw):
    base = dict(kull=None, botid_aar=None, omraade=None, nivaa=None, gruppe="flyktningbakgrunn", maal=None,
                andel=None, antall=None, teller=None, nevner=None, basis=None, kilde=None, fil=None, side=None, merknad=None)
    base.update(kw)
    rec.append(base)


def nivaa(omr):
    if omr in ("Hele landet", "Landet", "I alt"):
        return "landet"
    if omr in ("Nord-Norge", "Sørlandet", "Trøndelag", "Vestlandet", "Østlandet"):
        return "landsdel"
    if omr in NN_FYLKER:
        return "fylke"
    return "kommune"


# 1. Fylkestabeller per kohort (monitor), basis opprinnelig kohort
for kull, t in md.FYLKE_KOHORT.items():
    for omr, (n, forste, annen, annet_fylke, oslo, utv) in t["rader"].items():
        o = "Hele landet" if omr == "Hele landet" else omr
        felles = dict(kull=kull, botid_aar=5, omraade=o, nivaa=nivaa(o), basis="opprinnelig kohort",
                      kilde=t["kilde"], fil=t["fil"], side=t["side"], nevner=n)
        add(maal="i_forste_bosettingskommune", andel=forste, **felles)
        if annen is not None and forste is not None:
            add(maal="i_forste_bosettingsfylke", andel=forste + annen,
                merknad="Sum av «første bostedskommune» og «annen kommune i fylket»", **felles)
        for m, v in (("flyttet_annet_fylke_ikke_oslo", annet_fylke), ("flyttet_oslo", oslo), ("utvandret_eller_dod", utv)):
            if v is not None:
                add(maal=m, andel=v, **felles)

# 2. Fylke × kohort, basis i Norge
for tab, maal in ((md.FORSTE_KOMMUNE_I_NORGE, "i_forste_bosettingskommune"), (md.SAMME_FYLKE_I_NORGE, "i_forste_bosettingsfylke")):
    for omr, serie in tab["serier"].items():
        for kull, v in serie.items():
            add(kull=kull, botid_aar=5, omraade=omr, nivaa=nivaa(omr), maal=maal, andel=v,
                basis="fortsatt bosatt i Norge", kilde=tab["kilde"], fil=tab["fil"])

# 3. Landet: kumulativ utflytting etter botid -> andel fortsatt i første kommune
for t in md.LANDET_FORLATT:
    for kull, serie in t["kohorter"].items():
        for i, v in enumerate(serie, start=1):
            if v is None:
                continue
            add(kull=kull, botid_aar=i, omraade="Hele landet", nivaa="landet", maal="i_forste_bosettingskommune",
                andel=100 - v, basis="opprinnelig kohort", kilde=t["kilde"], fil=t["fil"], side=t.get("side"),
                merknad=f"Avledet som 100 minus andel {t['definisjon']}; «år {i}» = {i}. kalenderår regnet fra bosettingsåret")

# 4. Landet fem år etter, 1995–2012 og 2010–2019
t = md.LANDET_5AAR
for kull, (n, utv, inorge, forste, annen, annet, oslo) in t["rader"].items():
    for m, v in (("i_forste_bosettingskommune", forste), ("i_forste_bosettingsfylke", forste + annen),
                 ("flyttet_annet_fylke_ikke_oslo", annet), ("flyttet_oslo", oslo)):
        add(kull=kull, botid_aar=5, omraade="Hele landet", nivaa="landet", maal=m, andel=v, nevner=inorge,
            basis="fortsatt bosatt i Norge", kilde=t["kilde"], fil=t["fil"], side=t["side"])
t = md.LANDET_5AAR_2025
for kull, (forste, annen, annet, oslo) in t["rader"].items():
    add(kull=kull, botid_aar=5, omraade="Hele landet", nivaa="landet", maal="i_forste_bosettingskommune", andel=forste,
        basis="fortsatt bosatt i Norge", kilde=t["kilde"], fil=t["fil"])
    add(kull=kull, botid_aar=5, omraade="Hele landet", nivaa="landet", maal="i_forste_bosettingsfylke", andel=forste + annen,
        basis="fortsatt bosatt i Norge", kilde=t["kilde"], fil=t["fil"])

# 5. Landbakgrunn og kommunestørrelse (landet)
t = md.LANDBAKGRUNN_5AAR
for land, (forste, annen, annet, oslo, utv) in t["rader"].items():
    add(kull="2010–2019", botid_aar=5, omraade="Hele landet", nivaa="landet", gruppe=f"flyktningbakgrunn, {land}",
        maal="i_forste_bosettingskommune", andel=forste, basis="opprinnelig kohort", kilde=t["kilde"], fil=t["fil"])
t = md.KOMMUNESTORRELSE
for kat, verdier in t["rader"].items():
    for kull, v in zip(t["kohorter"], verdier):
        add(kull=kull, botid_aar=5, omraade=f"Kommuner {kat}" if kat != "Hele landet" else "Hele landet",
            nivaa="kommunegruppe" if kat != "Hele landet" else "landet", maal="i_forste_bosettingskommune", andel=v,
            basis="opprinnelig kohort", kilde=t["kilde"], fil=t["fil"], side=t["side"],
            merknad="Folketall per 1.1.2017")

# 6. Kommuner i Nord-Norge
t = md.KOMMUNE_2009_2010
for kom, ((b10, f10), (b09, f09)) in t["rader"].items():
    for kull, b, f in ((2010, b10, f10), (2009, b09, f09)):
        add(kull=kull, botid_aar=5, omraade=kom, nivaa="kommune", maal="i_forste_bosettingskommune",
            andel=round(100 * f / b), teller=f, nevner=b, basis="opprinnelig kohort", kilde=t["kilde"], fil=t["fil"],
            side=t["side"], merknad="Kommuneinndeling før 2020")
t = md.KOMMUNE_2015_NETTO
for kom, (b, nå) in t["rader"].items():
    add(kull=2015, botid_aar=5, omraade=kom, nivaa="kommune", maal="netto_kohortbestand_i_kommunen",
        andel=round(100 * nå / b), teller=nå, nevner=b, basis="opprinnelig kohort", kilde=t["kilde"], fil=t["fil"],
        merknad="Bosatte fra 2015-kohorten i kommunen 1.1.2020 (inkl. tilflyttere fra andre kommuner) / bosatt 2015")

# 7. Fafo og KBNN
f = md.FAFO
add(kull="2010–2021", botid_aar=10, omraade="Nord-Norge", nivaa="landsdel", maal="i_forste_bosettingskommune",
    andel=100 - f["nn_flyttet_10aar"]["verdi"], basis="opprinnelig kohort", kilde=f["kilde"], fil=f["fil"],
    side=f["nn_flyttet_10aar"]["side"], merknad="Avledet: " + f["nn_flyttet_10aar"]["tekst"] + ". Avlest tekst, ikke tabell.")
for omr, (forst, naa) in f["tabell3"]["rader"].items():
    if omr == "I alt":
        continue
    add(kull="2010–2016", botid_aar="7–13", omraade=omr, nivaa="landsdel", maal="netto_kohortbestand_i_landsdelen",
        andel=round(100 * naa / forst, 1), teller=naa, nevner=forst, basis="opprinnelig kohort", kilde=f["kilde"],
        fil=f["fil"], side=f["tabell3"]["side"],
        merknad="Bosatte fra kohortene 2010–2016 i landsdelen 1.1.2023 (inkl. tilflyttere fra andre landsdeler) / bosatt i landsdelen; utvandrede/døde (2 504) er ute av telleren")
b = md.KBNN
add(kull="2000–2024", botid_aar="0–24", omraade="Nord-Norge", nivaa="landsdel", gruppe="arbeidsinnvandrere fra Schengen (utenom Norden)",
    maal="fortsatt_bosatt_i_landsdelen", andel=round(100 * b["schengen"]["fortsatt"] / b["schengen"]["innvandret"], 1),
    teller=b["schengen"]["fortsatt"], nevner=b["schengen"]["innvandret"], basis="innvandret til landsdelen",
    kilde=b["kilde"], fil=b["fil"], merknad=b["schengen"]["tekst"] + ". Sekundærkilde; metode ikke dokumentert i detalj.")
add(kull="2000–2024", botid_aar="0–24", omraade="Nord-Norge", nivaa="landsdel", gruppe="innvandrere fra typiske flyktningland (ekskl. Ukraina)",
    maal="flyttet_til_sor_norge_strom", andel=round(100 * b["flukt"]["flyttet_sor"] / b["flukt"]["innvandret"], 1),
    teller=b["flukt"]["flyttet_sor"], nevner=b["flukt"]["innvandret"], basis="innvandret til landsdelen",
    kilde=b["kilde"], fil=b["fil"], merknad=b["flukt"]["tekst"] + ". Flyttinger, ikke personer – kan telle samme person flere ganger.")

# 8. Pseudokohorter SSB 10598 (avledet)
pk = json.loads((K / "avledet" / "pseudokohort_10598.json").read_text(encoding="utf-8"))
GRUPPENAVN = {"alle": "alle innvandrere", "flukt_land": "innvandrere fra ti flyktningland",
              "arbeid_EU_ost": "innvandrere fra Polen og Litauen", "sverige": "innvandrere fra Sverige",
              "russland": "innvandrere fra Russland", "filippinene_thailand": "innvandrere fra Filippinene og Thailand",
              "ukraina": "innvandrere fra Ukraina"}
for r in pk:
    if r["botid_år"] not in (5, 10, 15, 20, 21):
        continue
    felles = dict(kull=r["innvandret_år"], botid_aar=r["botid_år"], omraade=r["område"],
                  nivaa={"Landet": "landet", "Nord-Norge": "landsdel"}.get(r["område"], "fylke"),
                  gruppe=GRUPPENAVN[r["gruppe"]], teller=r["n_slutt"], nevner=r["n_start"],
                  basis=f"pseudokohort, startbotid {r['start_botid']}",
                  kilde="SSB tabell 10598 (Innvandrere etter fylke, landbakgrunn og botid), egen beregning",
                  fil="kilder/ssb/10598_nn_alle.json / 10598_nn_land.json; kilder/avledet/pseudokohort_10598.json")
    add(maal="netto_bevaring_omraade", andel=round(100 * r["bevaring"], 1),
        merknad="Antall med botid k år k år senere / antall med startbotid i området. Netto: utvandring, død og utflytting trekker ned, innflytting av personer med samme botid trekker opp.",
        **felles)
    if r["område"] != "Landet" and r["relativ_til_landet"]:
        add(maal="netto_bevaring_relativ_landet", andel=round(100 * r["relativ_til_landet"], 1),
            merknad="Områdets netto bevaring delt på landets (fjerner om lag effekten av utvandring og død).", **felles)

# 9. SSB 10824 – tidligere introdeltakere
ids, koder, et, v = les(K / "ssb" / "10824_nn.json")
for reg in koder[0]:
    navn = et["Region"][reg]
    for a, år_etter in (("01", 1), ("03", 3), ("05", 5)):
        for t in koder[5]:
            nå = v.get((reg, "0", a, "00", "Deltakere", t)); da = v.get((reg, "0", a, "00", "DeltakereProg", t))
            if not nå or not da or da < 20 or reg == "0":
                continue
            add(kull=f"avsluttet {int(t) - år_etter}", botid_aar=f"{år_etter} år etter avsluttet program",
                omraade=navn, nivaa="fylke" if len(reg) == 2 else "kommune", gruppe="tidligere deltakere i introduksjonsprogrammet",
                maal="netto_bevaring_intro", andel=round(100 * nå / da, 1), teller=nå, nevner=da,
                basis="bosatt i Norge i november", kilde="SSB tabell 10824, egen beregning", fil="kilder/ssb/10824_nn.json",
                merknad=f"Personer etter nåværende bosted / etter bosted ved programdeltakelse, november {t}. Nevner < 20 er utelatt.")

# 10. SSB 06318 – landet, bosatt i Norge etter innvandringsgrunn
ids, koder, et, v = les(K / "ssb" / "06318_landet.json")
for g in koder[0]:
    for t in koder[3]:
        b_ = v[(g, "01", koder[2][0], t)]; i_ = v[(g, "05", koder[2][0], t)]
        add(kull=t, botid_aar=None, omraade="Hele landet", nivaa="landet", gruppe=f"innvandringsgrunn: {et['Innvandringsgrunn'][g]}",
            maal="fortsatt_bosatt_i_norge", andel=round(100 * b_ / (b_ + i_), 1), teller=b_, nevner=b_ + i_,
            basis="alle innvandringer i perioden", kilde="SSB tabell 06318, egen beregning", fil="kilder/ssb/06318_landet.json",
            merknad="Ikke-nordiske førstegangsinnvandringer i perioden som fortsatt er bosatt i Norge ved periodens slutt")

# 11. IMDi – flyktninger etter botid og om de bor i første bosettingskommune (bestandsmål)
klass = {}
for fil in ("kommuner_2019-01-01.json", "kommuner_2023-01-01.json", "kommuner_2025-01-01.json"):
    for c in json.loads((K / "klass" / fil).read_text(encoding="utf-8"))["codes"]:
        klass.setdefault(c["code"], c["name"])
FYLKE = {"00": "Hele landet", "18": "Nordland", "54": "Troms og Finnmark", "55": "Troms", "56": "Finnmark"}


def imdi_tab(fil, nøkkel):
    d = json.loads((K / "imdi" / fil).read_text(encoding="utf-8"))
    c = {}
    for r in d:
        k = tuple(r[x] for x in nøkkel)
        c[k] = r["tabellvariabel"]
    return c


for nivå, fil in (("fylkeNr", "flyktning_botid_flytting_fylkeNr.json"), ("kommuneNr", "flyktning_botid_flytting_kommuneNr.json")):
    c = imdi_tab(fil, [nivå, "aar", "botid3", "forsteBosettingskommune", "enhet"])
    regioner = sorted({k[0] for k in c})
    for reg in regioner:
        if nivå == "fylkeNr" and reg not in FYLKE:
            continue
        navn = FYLKE.get(reg) if nivå == "fylkeNr" else klass.get(reg, reg)
        for år in sorted({k[1] for k in c if k[0] == reg}):
            for bt in ("5+", "0_4"):
                ja = c.get((reg, år, bt, "ja", "personer")); nei = c.get((reg, år, bt, "nei", "personer"))
                try:
                    ja, nei = int(ja), int(nei)
                except (TypeError, ValueError):
                    continue
                if ja + nei < 20 or int(år) < 2016:
                    continue
                add(kull=f"bestand 1.1.{år}", botid_aar="5+" if bt == "5+" else "0–4", omraade=navn,
                    nivaa="fylke" if nivå == "fylkeNr" and reg != "00" else ("landet" if reg == "00" else "kommune"),
                    maal="andel_av_bestand_i_forste_bosettingskommune", andel=round(100 * ja / (ja + nei), 1),
                    teller=ja, nevner=ja + nei, basis="flyktninger bosatt i området (bestand)",
                    kilde="IMDi, «Sekundærflytting blant flyktninger» (tabell flyktning_botid_flytting, kilde SSB)",
                    fil=f"kilder/imdi/{fil}",
                    merknad="Andel av flyktningene med denne botiden som bor i sin første bosettingskommune (resten har flyttet inn fra en annen kommune). Måler sammensetning, ikke bofasthet. «Uoppgitt» utelatt; 2014–2015 utelatt pga. mange uoppgitte.")

# 12. IMDi – innvandrere etter botid: 5-års pseudokohort per kommune (0–4 år -> 5–9 år)
c = imdi_tab("befolkning_botid_kommuneNr.json", ["kommuneNr", "aar", "botid4", "vreg3"])
cf = imdi_tab("befolkning_botid_fylkeNr.json", ["fylkeNr", "aar", "botid4", "vreg3"])
VREG = {"alle": "alle innvandrere", "1": "innvandrere fra EU/EFTA, Nord-Amerika, Australia og New Zealand",
        "2": "innvandrere fra Asia, Afrika, Latin-Amerika, Øst-Europa utenom EU m.fl."}
# Troms, Finnmark og Nord-Norge 2020–2026 summeres fra kommunetall (IMDi har ikke fylkene 55/56 for 2020–2023)
sum_k = collections.defaultdict(int)
for (reg, år, bt, vr), val in c.items():
    if int(år) >= 2020 and reg[:2] in ("18", "55", "56"):
        try:
            n = int(val)
        except (TypeError, ValueError):
            continue
        for omr in ({"55": ["55", "NN"], "56": ["56", "NN"], "18": ["NN"]}[reg[:2]]):
            sum_k[(omr, år, bt, vr)] += n
FYLKE.update({"NN": "Nord-Norge"})
for kilde_c, nivå in ((c, "kommune"), (cf, "fylke"), (dict(sum_k), "fylke")):
    regioner = sorted({k[0] for k in kilde_c})
    for reg in regioner:
        if nivå == "fylke" and reg not in FYLKE:
            continue
        navn = FYLKE.get(reg) if nivå == "fylke" else klass.get(reg, reg)
        for t0 in (2014, 2020, 2021):
            t1 = t0 + 5
            if t0 == 2014:
                t1 = 2019
            for vr in ("alle", "1", "2"):
                try:
                    n0 = int(kilde_c[(reg, str(t0), "0_4", vr)]); n1 = int(kilde_c[(reg, str(t1), "5_9", vr)])
                except (KeyError, ValueError, TypeError):
                    continue
                if n0 < 20:
                    continue
                add(kull=f"botid 0–4 per 1.1.{t0}", botid_aar=5, omraade=navn,
                    nivaa=("landet" if reg == "00" else "landsdel" if reg == "NN" else nivå), gruppe=VREG[vr],
                    maal="netto_bevaring_omraade", andel=round(100 * n1 / n0, 1), teller=n1, nevner=n0,
                    basis="pseudokohort, femårige botidsgrupper",
                    kilde="IMDi, «Innvandrernes botid» (tabell befolkning_botid, kilde SSB), egen beregning",
                    fil=f"kilder/imdi/befolkning_botid_{'kommuneNr' if nivå == 'kommune' else 'fylkeNr'}.json",
                    merknad=f"Antall med botid 5–9 år 1.1.{t1} / antall med botid 0–4 år 1.1.{t0}. IMDi har avrundet små tall (1–4 erstattet med tilfeldig tall).")
        # andel med 10+ års botid 2021 (før Ukraina-bosettingen) og 2026; kommunesummer brukes bare der
        # fylkestallet mangler (Troms/Finnmark 2021) og for Nord-Norge
        er_sum = kilde_c is not c and kilde_c is not cf
        for år_b in ("2021", "2026"):
          if er_sum and reg != "NN" and år_b == "2026":
            continue
          for vr in ("alle", "2"):
            try:
                n10 = int(kilde_c[(reg, år_b, "10+", vr)]); nall = int(kilde_c[(reg, år_b, "alle", vr)])
            except (KeyError, ValueError, TypeError):
                continue
            if nall < 20:
                continue
            add(kull=f"bestand 1.1.{år_b}", botid_aar="10+", omraade=navn,
                nivaa=("landet" if reg == "00" else "landsdel" if reg == "NN" else nivå), gruppe=VREG[vr],
                maal="andel_av_bestand_med_botid_10pluss", andel=round(100 * n10 / nall, 1), teller=n10, nevner=nall,
                basis="innvandrere bosatt i området (bestand)", kilde="IMDi, «Innvandrernes botid» (kilde SSB)",
                fil=f"kilder/imdi/befolkning_botid_{'kommuneNr' if nivå == 'kommune' else 'fylkeNr'}.json",
                merknad="Botid i Norge, ikke i kommunen.")

# 13. SSB 07210 – innenlandsk nettoinnflytting (antall) for innvandrere og norskfødte med innvandrerforeldre
ids, koder, et, v = les(K / "ssb" / "07210_nn.json")
OMR = {"Nord-Norge": ("18", "19", "20", "54", "55", "56"), "Nordland": ("18",), "Troms og Finnmark": ("19", "20", "54", "55", "56")}
for omr, pref in OMR.items():
    kum = collections.Counter()
    for t in koder[3]:
        for kat, gnavn in (("10", "innvandrere og norskfødte med innvandrerforeldre"), ("90", "øvrige befolkning")):
            s = sum((v.get((r, kat, koder[2][0], t)) or 0) for r in koder[0] if len(r) == 4 and r[:2] in pref)
            kum[kat] += s
            for maal, verdi in (("netto_innenlands_flytting_antall", s), ("netto_innenlands_flytting_kumulativt_fra_2008", kum[kat])):
                add(kull=t, omraade=omr, nivaa="landsdel" if omr == "Nord-Norge" else "fylke", gruppe=gnavn, maal=maal,
                    andel=None, antall=verdi, basis="flyttinger mellom kommuner, netto",
                    kilde="SSB tabell 07210, egen summering av kommunetall", fil="kilder/ssb/07210_nn.json",
                    merknad="Flytting mellom kommuner innenfor området nuller seg ut. Kjønn/alder ikke skilt. Måler flyttestrøm, ikke personoppfølging.")

ut = {
    "beskrivelse": "Bofasthet for flyktninger og innvandrere, med vekt på Nord-Norge. Bygget av skript/bygg_statistikk.py.",
    "hentet": "2026-10-20",
    "felter": {"kull": "bosettings-/innvandringsår eller periode", "botid_aar": "år etter bosetting/innvandring",
               "andel": "prosent", "basis": "nevnerens definisjon", "maal": "se statistikk.md, avsnittet «Mål»"},
    "antall_poster": len(rec),
    "poster": rec,
}
# kompakt: én post per linje
NL = "\n"
hode = json.dumps({k: v for k, v in ut.items() if k != "poster"}, ensure_ascii=False, indent=1)[:-2]
linjer = ("," + NL).join("  " + json.dumps(r, ensure_ascii=False) for r in rec)
(ROT / "statistikk.json").write_text(hode + "," + NL + ' "poster": [' + NL + linjer + NL + " ]" + NL + "}" + NL,
                                     encoding="utf-8")
json.loads((ROT / "statistikk.json").read_text(encoding="utf-8"))  # kontroll
print(len(rec), "poster")
print(collections.Counter(r["maal"] for r in rec))
