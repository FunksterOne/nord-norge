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


# ─── Nasjonalt KBN/TBU/KS-bakteppe (hardkodet — oppdateres manuelt årlig) ───
# Kilder per Q1 2026. Se docstring øverst for fulle referanser.
GJELD_BAKTEPPE = {
    "sist_oppdatert": "2026-05-20",
    "kilde": "KBN Q4-2025, KLP Kommunekreditt 2025, NOU 2025:10 (TBU), KS regnskapsundersøkelse 2025, KS FoU 2025",
    # Lånekildefordeling — markedsandel av kommunesektorens samlede gjeld
    "lanekilder": [
        {"navn": "Kommunalbanken (KBN)", "andel_pct": 49.7, "kilde": "KBN Q4-2025",
         "note": "Synker (var 50,2 % ved utgangen av 2024)"},
        {"navn": "Obligasjonsmarkedet", "andel_pct": 24.0, "kilde": "TBU/KS estimat",
         "note": "Voksende — særlig lave kredittspreader 2024–2025"},
        {"navn": "KLP Kommunekreditt", "andel_pct": 10.0, "kilde": "KLP 2025 (avledet fra OMF-volum)",
         "note": "23,0 mrd kr OMF utestående 31.12.2025"},
        {"navn": "Andre (banker, sertifikater, Husbanken)", "andel_pct": 16.3, "kilde": "Avledet",
         "note": "Inkluderer kommunenes lokale banker og lange sertifikatlån"},
    ],
    # Fastrente vs flytende — estimat, ikke offentliggjort eksplisitt på sektornivå
    "rentebinding": {
        "fastrente_pct_estimat": 30,
        "flytende_pct_estimat": 70,
        "kilde": "KBN regnskapsført til virkelig verdi (~28 %) brukes som proxy",
        "spennvidde": "25–35 % fastrente",
        "er_estimat": True
    },
    # Sektornivå-tall (2025)
    "sektor": {
        "netto_driftsresultat_2024_pct": -0.4,
        "netto_driftsresultat_2025_pct": 2.1,
        "korrigert_netto_lanegjeld_2024_pct": 87.7,
        "ks_norm_netto_lanegjeld_pct": 85.0,
        "ks_norm_disposisjonsfond_pct": 5.0,
        "ks_norm_ndr_kommune_pct": 1.75,
        "finansutgifter_endring_2024_2025_pct": 15.0,
        "rente_endring_2024_2025_pct": 8.5,
        "tbu_kilde": "NOU 2025:10",
        "ks_kilde": "KS FoU 2025 — Oslo Economics/Telemarksforsking",
        "ks_buffer_test": "+2 prosentpoeng renteøkning over 3 år + inntektssvikt i 10. persentil"
    },
    # Typisk løpetid (estimat)
    "lopetid": {
        "snitt_aar_estimat": 22,
        "spennvidde_aar": "20–30",
        "er_estimat": True,
        "kilde": "KBN typiske strukturer; ikke publisert vektet snitt"
    }
}


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
            bdi = None
            if ndr_p and ndr_p > 0:
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
        new_html = pat.sub(block, html)
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
