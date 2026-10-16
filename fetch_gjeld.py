#!/usr/bin/env python3
"""Henter komplett gjeldsbilde fra SSB KOSTRA tabell 12143 + KS/TBU/KBN-bakteppe.

Utvider det opprinnelige RENTE_DATA-bildet med avdrag, langsiktig gjeld, og
sektorvis sammenligning slik at vi kan svare på: 'Hvor stort problem er gjeld
og renter+avdrag sammenlignet med øvrige utgifter?'

Felter per kommune (siste tilgjengelige år):
  yr          År
  ndr_kr      Netto renter, 1000 kr (AGD97)
  avd_kr      Avdrag på lån, 1000 kr (AGD21)
  fin_kr      Netto finansutgifter, 1000 kr (AGD86)
  bdi_kr      Brutto driftsinntekter (avledet fra ndr_kr / ndr_pct hvis tilgjengelig)
  ndr_pct     Netto renter i % av BDI
  avd_pct     Avdrag i % av BDI
  fin_pct     Netto finansutgifter i % av BDI
  gjb_kr      Gjeldsbetjening = renter + avdrag, 1000 kr (avledet)
  gjb_pct     Gjeldsbetjening i % av BDI (avledet)
  lan_kr      Langsiktig gjeld, 1000 kr (KG25)
  lan_pct     Langsiktig gjeld i % av BDI
  nlan_kr     Netto lånegjeld, 1000 kr (KG31)
  nlan_pct    Netto lånegjeld i % av BDI
  rxp_kr      Renteeksponert gjeld, 1000 kr (KG39)
  rxp_pct     Renteeksponert gjeld i % av BDI
  proxy       Hvis KG39 mangler — KG31 brukes som proxy

I tillegg hardkodes GJELD_BAKTEPPE_2026 med nasjonale KBN/TBU/KS-tall (årlig
manuell oppdatering). Kilder: KBN årsrapport 2025 (publ. 12.3.2026), KLP
Kommunekreditt årsrapport 2025, NOU 2025:10 (TBU høstrapport), KS regnskaps-
undersøkelse 2025 (publ. 3.3.2026), KS FoU 2025 (Oslo Economics/Telemarks-
forsking).
"""
import json
import re
import sys
import urllib.request
import datetime
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "assets" / "data.js"

CODES = ["1804","1806","1811","1812","1813","1815","1816","1818","1820","1822",
"1824","1825","1826","1827","1828","1832","1833","1834","1835","1836","1837",
"1838","1839","1840","1841","1845","1848","1851","1853","1856","1857","1859",
"1860","1865","1866","1867","1868","1870","1871","1874","1875","5501","5503",
"5510","5512","5514","5516","5518","5520","5522","5524","5526","5528","5530",
"5532","5534","5536","5538","5540","5542","5544","5546","5601","5603","5605",
"5607","5610","5612","5614","5616","5618","5620","5622","5624","5626","5628",
"5630","5632","5634","5636"]

YEARS = ["2024", "2025"]
BEGREP = ["AGD97", "AGD21", "AGD86", "KG25", "KG31", "KG39", "AGD18", "AGD23"]


def post_ssb(body):
    url = "https://data.ssb.no/api/v0/no/table/12143"
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch(contents_code):
    body = {
        "query": [
            {"code": "KOKkommuneregion0000", "selection": {"filter": "item", "values": CODES}},
            {"code": "KOKartkap0000", "selection": {"filter": "item", "values": BEGREP}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [contents_code]}},
            {"code": "Tid", "selection": {"filter": "item", "values": YEARS}},
        ],
        "response": {"format": "json-stat2"},
    }
    return post_ssb(body)


def parse(d):
    dim = d["dimension"]
    dim_ids = d.get("id") or list(dim.keys())
    sizes = d.get("size") or [len(dim[k]["category"]["index"]) for k in dim_ids]
    cats = {k: list(dim[k]["category"]["index"].keys()) for k in dim_ids}
    values = d["value"]
    strides = []; acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    out = {}
    for i in range(len(values)):
        rem = i; coords = []
        for st, sz in zip(strides, sizes):
            coords.append(rem // st); rem %= st
        codes = {dim_ids[j]: cats[dim_ids[j]][coords[j]] for j in range(len(dim_ids))}
        region = codes.get("KOKkommuneregion0000")
        begrep = codes.get("KOKartkap0000")
        tid = codes.get("Tid")
        out.setdefault(region, {}).setdefault(begrep, {})[tid] = values[i]
    return out


# ─── Nasjonalt bakteppe ───
# Sektortall, lånekilder og rentebinding hentes fra SSB ved hver kjøring (se hent_sektor, hent_lanekilder,
# hent_rentebinding). Bare normene under og KBN/KLP-konstantene over hent_sektor oppdateres manuelt.
GJELD_BAKTEPPE = {
    "sist_oppdatert": None,  # settes til hentedato i main()
    "kilde": "SSB 12143 (KOSTRA), SSB 06718 (K2), SSB 10648, KBN kvartalsrapport 2. kvartal 2026, KLP Kommunekreditt 2025, NOU 2025:10 (TBU), KS-rapport mai 2025",
    # Normer og kilder for sektoren. Selve sektortallene (netto driftsresultat, disposisjonsfond,
    # netto lånegjeld, finansutgifter) hentes fra SSB 12143 i hent_sektor() og legges inn her.
    "sektor": {
        "ks_norm_netto_lanegjeld_pct": 85.0,
        "ks_norm_disposisjonsfond_pct": 5.0,
        "ks_norm_ndr_kommune_pct": 1.75,
        "tbu_kilde": "TBU, NOU 2025:10",
        "ks_kilde": "KS-rapport mai 2025 (Oslo Economics og Telemarksforskning)",
        "ks_buffer_test": "+2 prosentpoeng renteøkning over 3 år + inntektssvikt i 10. persentil"
    }
}


SEKTOR_REG = {"EAK": "Landet", "EAKUO": "Landet uten Oslo", "EKA18": "Nordland", "EKA55": "Troms", "EKA56": "Finnmark"}
SEKTOR_BEG = {"AGD23": "ndr", "56": "fond", "KG31": "nlan", "KG39": "rxp", "KG25": "lan", "AGD97": "renter", "AGD21": "avdrag", "AGD86": "finans"}


# ─── Tall SSB ikke publiserer (oppdateres manuelt ved ny kvartalsrapport) ───
# KBNs markedsandel av utlån til kommunesektoren, uten Husbanken i nevneren (KBN kvartalsrapport 2. kvartal 2026, 6.8.2026)
KBN_UTLAN_ANDEL_EKS_HUSBANKEN = {"verdi": 48.9, "periode": "2. kvartal 2026", "kilde": "KBN kvartalsrapport 2. kvartal 2026"}
# KBNs fastrenteandel: lån til virkelig verdi + virkelig verdi-sikring delt på alle utlån (note 3)
KBN_FASTRENTE_ANDEL = {"verdi": 36.4, "periode": "2. kvartal 2026", "kilde": "KBN kvartalsrapport 2. kvartal 2026, note 3"}
# KLP Kommunekreditt: andel av utlånsvolumet med flytende rente (årsrapport 2025)
KLPKK_FLYTENDE_ANDEL = {"verdi": 88, "periode": "2025", "kilde": "KLP Kommunekreditt, årsrapport 2025"}
# Gjennomsnittlig avdragstid for sektoren (TBU, NOU 2025:10 kap. 4). Gjenværende løpetid publiseres ikke.
AVDRAGSTID = {"tekst": "25–30 år", "kilde": "TBU, NOU 2025:10, kap. 4"}


def ssb_post(tabell, query):
    req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{tabell}",
        data=json.dumps({"query": query, "response": {"format": "json-stat2"}}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
    ids, size = d["id"], d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    ut = {}
    for i, v in enumerate(d["value"]):
        rest, co = i, {}
        for j in range(len(ids) - 1, -1, -1):
            co[ids[j]] = cats[ids[j]][rest % size[j]]; rest //= size[j]
        ut[tuple(co[k] for k in ids)] = (co, v)
    return ut


def siste_tid(tabell):
    meta = json.loads(urllib.request.urlopen(f"https://data.ssb.no/api/v0/no/table/{tabell}", timeout=60).read().decode("utf-8"))
    return next(v for v in meta["variables"] if v["code"] == "Tid")["values"]


MND = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"]


def periodenavn(t):
    """2026M08 -> august 2026, 2026K2 -> 2. kvartal 2026."""
    if "M" in t: return f"{MND[int(t[5:]) - 1]} {t[:4]}"
    if "K" in t: return f"{t[5:]}. kvartal {t[:4]}"
    return t


def hent_lanekilder():
    """Kommuneforvaltningens innenlandske bruttogjeld etter kilde (SSB K2, tabell 06718), siste måned."""
    tid = siste_tid("06718")[-1]
    koder = {"LTOT": "I alt", "L202+L203": "Banker og kredittforetak", "L214": "Obligasjoner og sertifikater",
             "L201": "Husbanken (statlige låneinstitutter)", "L206": "KLP og andre livsforsikringsselskaper", "L204": "Finansieringsforetak"}
    r = ssb_post("06718", [
        {"code": "Valuta", "selection": {"filter": "item", "values": ["00"]}},
        {"code": "Lantaker2", "selection": {"filter": "item", "values": ["Kred02"]}},
        {"code": "Kredittkilde", "selection": {"filter": "item", "values": list(koder)}},
        {"code": "Tid", "selection": {"filter": "item", "values": [tid]}}])
    belop = {co["Kredittkilde"]: v for co, v in r.values()}
    tot = belop["LTOT"]
    kilder = []
    for k in ("L202+L203", "L214", "L201", "L206", "L204"):
        if belop.get(k) is None: continue
        kilder.append({"navn": koder[k], "belop_mrd": round(belop[k] / 1000, 1), "andel_pct": round(belop[k] / tot * 100, 1)})
    rest = tot - sum(belop.get(k) or 0 for k in ("L202+L203", "L214", "L201", "L206", "L204"))
    if rest > tot * 0.001:
        kilder.append({"navn": "Andre", "belop_mrd": round(rest / 1000, 1), "andel_pct": round(rest / tot * 100, 1)})
    # KBN er en del av «banker og kredittforetak». Markedsandelen (uten Husbanken) omregnes til andel av all gjeld.
    kbn = KBN_UTLAN_ANDEL_EKS_HUSBANKEN["verdi"] * (tot - (belop.get("L201") or 0)) / tot
    kilder[0]["herav"] = [{"navn": "Kommunalbanken (KBN)", "andel_pct": round(kbn, 1),
                           "note": "avledet fra KBNs markedsandel",
                           "markedsandel": KBN_UTLAN_ANDEL_EKS_HUSBANKEN}]
    return {"periode": tid, "periode_navn": periodenavn(tid), "total_mrd": round(tot / 1000, 1), "kilder": kilder,
            "kilde": f"SSB tabell 06718 (kredittindikator K2), kommuneforvaltningen, innenlandsk bruttogjeld, {periodenavn(tid)}"}


def hent_rentebinding():
    """Rentebinding for kommuneforvaltningens lån i banker og kredittforetak (SSB tabell 10648), siste kvartal og trend."""
    alle = siste_tid("10648")
    siste = alle[-1]
    ett_aar = f"{int(siste[:4]) - 1}{siste[4:]}"
    perioder = [t for t in (f"{int(siste[:4]) - 3}K4", f"{int(siste[:4]) - 2}K4", f"{int(siste[:4]) - 1}K4", ett_aar, siste) if t in alle]
    perioder = sorted(dict.fromkeys(perioder))
    r = ssb_post("10648", [
        {"code": "Laangiver960", "selection": {"filter": "item", "values": ["02"]}},
        {"code": "Utlanstype", "selection": {"filter": "item", "values": ["00b"]}},
        {"code": "Sektor", "selection": {"filter": "item", "values": ["58"]}},
        {"code": "Rentebinding", "selection": {"filter": "item", "values": ["99", "08", "09"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["UtlaanBelop"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": perioder}}])
    b = {}
    for co, v in r.values():
        b[(co["Tid"], co["Rentebinding"])] = v
    def andeler(t):
        tot, fl, kort = b.get((t, "99")), b.get((t, "08")), b.get((t, "09"))
        if not tot or fl is None: return None
        kort = kort or 0
        return {"flytende_pct": round(fl / tot * 100, 1), "kort_pct": round(kort / tot * 100, 1),
                "lang_pct": round((tot - fl - kort) / tot * 100, 1), "grunnlag_mrd": round(tot / 1000, 1)}
    trend = {t: andeler(t)["flytende_pct"] for t in perioder if andeler(t)}
    return {"periode": siste, "periode_navn": periodenavn(siste), **andeler(siste), "flytende_trend": trend,
            "trend_navn": {t: periodenavn(t) for t in trend},
            "kbn_fastrente": KBN_FASTRENTE_ANDEL, "klpkk_flytende": KLPKK_FLYTENDE_ANDEL,
            "kilde": f"SSB tabell 10648, utlån fra banker og kredittforetak til kommuneforvaltningen, {periodenavn(siste)}"}


def hent_sektor():
    """KOSTRA-nøkkeltall (kommunekonsern) for landet og Nord-Norge-fylkene, siste to år, fra SSB 12143."""
    meta = json.loads(urllib.request.urlopen("https://data.ssb.no/api/v0/no/table/12143", timeout=60).read().decode("utf-8"))
    tid = next(v for v in meta["variables"] if v["code"] == "Tid")["values"][-2:]
    ut = {}
    for cc, felt in (("KOSbelopbrinv0000", "pct"), ("KOSbelop0000", "kr")):
        d = post_ssb({"query": [
            {"code": "KOKkommuneregion0000", "selection": {"filter": "item", "values": list(SEKTOR_REG)}},
            {"code": "KOKartkap0000", "selection": {"filter": "item", "values": list(SEKTOR_BEG)}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [cc]}},
            {"code": "Tid", "selection": {"filter": "item", "values": tid}}], "response": {"format": "json-stat2"}})
        for reg, beg in parse(d).items():
            for b, aar in beg.items():
                for y, v in aar.items():
                    ut.setdefault(SEKTOR_REG[reg], {}).setdefault(y, {})[SEKTOR_BEG[b] + "_" + felt] = v
    siste, forrige = tid[-1], tid[-2]
    omr = {}
    for navn, aar in ut.items():
        a, f = aar.get(siste, {}), aar.get(forrige, {})
        rec = {k: a.get(k + "_pct") for k in ("ndr", "fond", "nlan", "rxp", "lan", "renter", "avdrag", "finans")}
        rec["gjeldsbetjening"] = round((a.get("renter_pct") or 0) + (a.get("avdrag_pct") or 0), 1)
        for k in ("renter", "finans"):
            if a.get(k + "_kr") and f.get(k + "_kr"):
                rec[k + "_endring_kr_pct"] = round((a[k + "_kr"] / f[k + "_kr"] - 1) * 100, 1)
        rec["forrige"] = {k: f.get(k + "_pct") for k in ("ndr", "fond", "nlan")}
        omr[navn] = rec
    return {"aar": int(siste), "forrige_aar": int(forrige), "omrader": omr,
            "kilde": "SSB tabell 12143, KOSTRA kommunekonsern, % av brutto driftsinntekter"}


def main():
    print("Fetching 12143 beløp (1000 kr)...", flush=True)
    kr_data = parse(fetch("KOSbelop0000"))
    print("Fetching 12143 % av BDI...", flush=True)
    pct_data = parse(fetch("KOSbelopbrinv0000"))

    payload = {
        "retrieved_at": datetime.date.today().isoformat(),
        "source_id": "SSB_STATBANK",
        "table": "12143",
        "year_priority": YEARS[::-1],
        "kommuner": {},
        "bakteppe": GJELD_BAKTEPPE,
    }
    print("Fetching 12143 sektortall (landet og fylker)...", flush=True)
    kostra = hent_sektor()
    GJELD_BAKTEPPE["sist_oppdatert"] = datetime.date.today().isoformat()
    GJELD_BAKTEPPE["kostra"] = kostra
    print("Fetching 06718 (lånekilder) og 10648 (rentebinding)...", flush=True)
    lk = hent_lanekilder()
    rb = hent_rentebinding()
    GJELD_BAKTEPPE["lanekilder"] = lk["kilder"]
    GJELD_BAKTEPPE["lanekilder_meta"] = {k: lk[k] for k in ("periode", "periode_navn", "total_mrd", "kilde")}
    rb["andel_av_gjelden_pct"] = lk["kilder"][0]["andel_pct"]
    GJELD_BAKTEPPE["rentebinding"] = rb
    GJELD_BAKTEPPE["lopetid"] = AVDRAGSTID
    L = kostra["omrader"]["Landet"]
    GJELD_BAKTEPPE["sektor"].update({
        "aar": kostra["aar"],
        f"netto_driftsresultat_{kostra['aar']}_pct": L["ndr"],
        f"netto_driftsresultat_{kostra['forrige_aar']}_pct": L["forrige"]["ndr"],
        f"netto_lanegjeld_{kostra['aar']}_pct": L["nlan"],
        f"netto_lanegjeld_{kostra['forrige_aar']}_pct": L["forrige"]["nlan"],
        f"disposisjonsfond_{kostra['aar']}_pct": L["fond"],
        f"finansutgifter_endring_{kostra['forrige_aar']}_{kostra['aar']}_pct": L.get("finans_endring_kr_pct"),
        f"rente_endring_{kostra['forrige_aar']}_{kostra['aar']}_pct": L.get("renter_endring_kr_pct"),
        "netto_lanegjeld_kilde": "SSB 12143, kommunekonsern, landet",
    })

    for c in CODES:
        kr = kr_data.get(c, {})
        pct = pct_data.get(c, {})
        rec = None
        for y in YEARS[::-1]:
            ndr = (kr.get("AGD97") or {}).get(y)
            avd = (kr.get("AGD21") or {}).get(y)
            fin = (kr.get("AGD86") or {}).get(y)
            lan = (kr.get("KG25") or {}).get(y)
            nlan = (kr.get("KG31") or {}).get(y)
            rxp = (kr.get("KG39") or {}).get(y)
            ndr_p = (pct.get("AGD97") or {}).get(y)
            avd_p = (pct.get("AGD21") or {}).get(y)
            fin_p = (pct.get("AGD86") or {}).get(y)
            lan_p = (pct.get("KG25") or {}).get(y)
            nlan_p = (pct.get("KG31") or {}).get(y)
            rxp_p = (pct.get("KG39") or {}).get(y)
            if ndr is None:
                continue
            # Avled BDI (brutto driftsinntekter) fra ndr_kr / ndr_pct hvis mulig
            # Avled BDI fra posten med størst andel (langsiktig gjeld, ~240 %), så avrundingen
            # i prosenttallet (én desimal) gir minst mulig feil. Netto renter brukes bare som reserve.
            bdi = None
            if lan and lan_p and lan_p > 0:
                bdi = round(lan / (lan_p / 100))
            elif ndr_p and ndr_p > 0:
                bdi = round(ndr / (ndr_p / 100))
            # Beregn gjeldsbetjening = renter + avdrag
            gjb_kr = None
            gjb_pct = None
            if ndr is not None and avd is not None:
                gjb_kr = ndr + avd
                if bdi and bdi > 0:
                    gjb_pct = round(gjb_kr / bdi * 100, 2)
            rec = {
                "yr": y,
                "ndr_kr": ndr, "ndr_pct": ndr_p,
                "avd_kr": avd, "avd_pct": avd_p,
                "fin_kr": fin, "fin_pct": fin_p,
                "lan_kr": lan, "lan_pct": lan_p,
                "nlan_kr": nlan, "nlan_pct": nlan_p,
                "rxp_kr": rxp if rxp is not None else nlan,
                "rxp_pct": rxp_p,
                "gjb_kr": gjb_kr, "gjb_pct": gjb_pct,
                "bdi_kr": bdi,
                "proxy": rxp is None,
            }
            break
        if rec is None:
            rec = {"yr": None}
        payload["kommuner"][c] = rec

    # Aggregat per fylke og landsdel
    NL = [c for c in CODES if c.startswith("18")]
    TR = [c for c in CODES if c.startswith("55")]
    FI = [c for c in CODES if c.startswith("56") or c == "5601" or c.startswith("560")]
    # Korriger: Finnmark = 5601-5636, Troms = 5501-5546
    NL = [c for c in CODES if 1800 <= int(c) < 1900]
    TR = [c for c in CODES if 5500 <= int(c) < 5600]
    FI = [c for c in CODES if 5600 <= int(c) < 5700]

    def agg(codes, label):
        tot = {"ndr_kr":0, "avd_kr":0, "fin_kr":0, "lan_kr":0, "nlan_kr":0, "rxp_kr":0,
               "gjb_kr":0, "bdi_kr":0, "n_kommuner":0}
        for c in codes:
            r = payload["kommuner"].get(c) or {}
            if r.get("ndr_kr") is None:
                continue
            tot["n_kommuner"] += 1
            for k in ("ndr_kr","avd_kr","fin_kr","lan_kr","nlan_kr","rxp_kr","gjb_kr","bdi_kr"):
                v = r.get(k)
                if v is not None:
                    tot[k] += v
        if tot["bdi_kr"]:
            tot["ndr_pct"] = round(tot["ndr_kr"]/tot["bdi_kr"]*100, 2)
            tot["avd_pct"] = round(tot["avd_kr"]/tot["bdi_kr"]*100, 2)
            tot["fin_pct"] = round(tot["fin_kr"]/tot["bdi_kr"]*100, 2)
            tot["lan_pct"] = round(tot["lan_kr"]/tot["bdi_kr"]*100, 2)
            tot["nlan_pct"] = round(tot["nlan_kr"]/tot["bdi_kr"]*100, 2)
            tot["rxp_pct"] = round(tot["rxp_kr"]/tot["bdi_kr"]*100, 2)
            tot["gjb_pct"] = round(tot["gjb_kr"]/tot["bdi_kr"]*100, 2)
        return tot

    payload["fylker"] = {"Nordland": agg(NL, "Nordland"), "Troms": agg(TR, "Troms"), "Finnmark": agg(FI, "Finnmark")}
    # Fylkestallene i prosent tas direkte fra SSB (EKA-regionene), som er eksakte summer for kommunene i fylket
    for nm in ("Nordland", "Troms", "Finnmark"):
        o = kostra["omrader"].get(nm)
        if not o: continue
        f = payload["fylker"][nm]
        for k_ut, k_inn in (("ndr_pct","renter"), ("avd_pct","avdrag"), ("fin_pct","finans"), ("lan_pct","lan"), ("nlan_pct","nlan"), ("rxp_pct","rxp")):
            if o.get(k_inn) is not None: f[k_ut] = o[k_inn]
        if o.get("renter") is not None and o.get("avdrag") is not None: f["gjb_pct"] = round(o["renter"] + o["avdrag"], 2)
        f["kilde_pct"] = "SSB 12143 (fylkessum)"
    payload["landsdel"] = agg(CODES, "Nord-Norge")

    # Print summary
    print(f"\nKommuner med komplett data: {sum(1 for k,v in payload['kommuner'].items() if v.get('ndr_kr') is not None)}/{len(CODES)}")
    for nm in ("Nordland","Troms","Finnmark"):
        f = payload["fylker"][nm]
        print(f"  {nm}: n={f['n_kommuner']}  rente={f.get('ndr_pct')}%  avdrag={f.get('avd_pct')}%  gjeldsbetj={f.get('gjb_pct')}%  langsiktig gjeld={f.get('lan_pct')}%")
    ld = payload["landsdel"]
    print(f"\nNord-Norge: rente={ld.get('ndr_pct')}%  avdrag={ld.get('avd_pct')}%  gjeldsbetjening={ld.get('gjb_pct')}%")
    print(f"  Langsiktig gjeld: {ld.get('lan_pct')}% av BDI ({round(ld.get('lan_kr',0)/1e6,1)} mrd kr)")
    print(f"  Netto lånegjeld:  {ld.get('nlan_pct')}% av BDI (KS-norm: 85 %)")

    # Inject
    html = HTML.read_text(encoding="utf-8")
    js_lit = "const GJELD_DATA = " + json.dumps(payload, ensure_ascii=False, indent=0).replace("\n","") + ";"
    marker_start = "/* GJELD_DATA BEGIN */"
    marker_end = "/* GJELD_DATA END */"
    block = f"{marker_start}\n{js_lit}\n{marker_end}"
    if marker_start in html:
        pat = re.compile(r"/\* GJELD_DATA BEGIN \*/.*?/\* GJELD_DATA END \*/", re.DOTALL)
        new_html = pat.sub(lambda _m: block, html)
    else:
        for anchor in ("/* RENTE_DATA END */", "/* SSB_FLOWS END */"):
            if anchor in html:
                new_html = html.replace(anchor, anchor + "\n" + block, 1)
                break
        else:
            print("ERROR: anchor not found", file=sys.stderr); sys.exit(1)
    HTML.write_text(new_html, encoding="utf-8")
    print(f"\nInjected GJELD_DATA ({len(js_lit)} chars)")


if __name__ == "__main__":
    main()
