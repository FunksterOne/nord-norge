"""Henter SSB-tabeller om spesialisthelsetjenesten i Helse Nord til analyse/helse-nord/data/.

Tabeller (PxWebApi v2, https://data.ssb.no/api/pxwebapi/v2/tables/<id>/data):
  13953  Avtalte årsverk etter yrke, tjenesteområde og helseforetak, 2008–2025   -> arsverk_hf.csv
  13942  Aktivitet, kapasitet og belegg etter tjenesteområde og helseforetak, 2015–2025 -> aktivitet_hf.csv
  14824  Pasienter, behandlinger og oppholdsdøgn i somatikk etter bosted (fylke/helseregion), 2015–2025 -> somatikk_bosted.csv
  13982  Befolkning per opptaksområde (HF og lokalsykehus, somatikk), 2015–2026 -> befolkning_opptak.csv
  14022  Kostnader og inntekter etter helseforetak, løpende priser, 2015–2025 -> kostnader_hf.csv
  12764  Avstand og kjøretid langs vei til nærmeste akuttmottak per kommune, 2019 -> kjoretid_akuttmottak.csv
Kjør: python -X utf8 hent_ssb.py
"""
import csv, json, os
from ssb import RAA, UT, celler, data, etikett

AAR = [str(a) for a in range(2015, 2026)]
HF = {"H00": "Hele landet", "H05": "Helseregion Nord", "883658752": "Helse Nord RHF",
      "983974899": "UNN", "983974910": "Nordlandssykehuset", "983974929": "Helgelandssykehuset",
      "983974880": "Finnmarkssykehuset"}


def skriv(fil, rader, felt):
    with open(os.path.join(UT, fil), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felt)
        w.writeheader()
        w.writerows(rader)
    print(fil, len(rader), "rader")


def ren(s):
    return s.replace("\xa0", " ").strip()


# 13953 årsverk
d = data("13953", {"valueCodes[HelseReg]": ",".join(HF), "valueCodes[HelseTjenomr]": "TOT,SOM",
                   "valueCodes[Yrke]": "*", "valueCodes[ContentsCode]": "Arsverk", "valueCodes[Tid]": ",".join(AAR)},
         "ssb_13953.json")
skriv("arsverk_hf.csv", [{"aar": c["Tid"], "hf_kode": c["HelseReg"], "hf": HF[c["HelseReg"]],
                          "tjenesteomraade": ren(etikett(d, "HelseTjenomr", c["HelseTjenomr"])),
                          "yrke_kode": c["Yrke"], "yrke": ren(etikett(d, "Yrke", c["Yrke"])), "avtalte_arsverk": v}
                         for c, v in celler(d)],
      ["aar", "hf_kode", "hf", "tjenesteomraade", "yrke_kode", "yrke", "avtalte_arsverk"])

# 13942 aktivitet
d = data("13942", {"valueCodes[HelseReg]": ",".join(k for k in HF if k != "883658752"),
                   "valueCodes[HelseTjenomr]": "TOT,SOM", "valueCodes[ContentsCode]": "*",
                   "valueCodes[Tid]": ",".join(AAR)}, "ssb_13942.json")
skriv("aktivitet_hf.csv", [{"aar": c["Tid"], "hf_kode": c["HelseReg"], "hf": HF[c["HelseReg"]],
                            "tjenesteomraade": ren(etikett(d, "HelseTjenomr", c["HelseTjenomr"])),
                            "mal": ren(etikett(d, "ContentsCode", c["ContentsCode"])), "verdi": v}
                           for c, v in celler(d)],
      ["aar", "hf_kode", "hf", "tjenesteomraade", "mal", "verdi"])

# 14824 somatikk etter bosted
REG = ["0", "18", "55", "56", "54", "19", "20", "H05", "H03", "H04", "H12"]
d = data("14824", {"valueCodes[Region]": ",".join(REG), "valueCodes[Kjonn]": "0", "valueCodes[Alder]": "*",
                   "valueCodes[Aktor]": "_T,offhel", "valueCodes[Diagnose]": "_T", "valueCodes[ContentsCode]": "*",
                   "valueCodes[Tid]": ",".join(AAR)}, "ssb_14824.json")
skriv("somatikk_bosted.csv", [{"aar": c["Tid"], "region_kode": c["Region"], "region": ren(etikett(d, "Region", c["Region"])),
                               "alder": ren(etikett(d, "Alder", c["Alder"])), "aktor": ren(etikett(d, "Aktor", c["Aktor"])),
                               "mal": ren(etikett(d, "ContentsCode", c["ContentsCode"])), "verdi": v}
                              for c, v in celler(d) if v is not None],
      ["aar", "region_kode", "region", "alder", "aktor", "mal", "verdi"])

# 13982 befolkning per opptaksområde (HF og lokalsykehus), somatikk, aldersgrupper
rader = []
for kl, koder in (("vs_HelseForetak02", "983974899,983974910,983974929,983974880"),
                  ("vs_HelseOpptakSom", "S01,S02,S03,S04,S05,S06,S07,S08,S09,S10,S11")):
    d = data("13982", {"codelist[HelseReg]": kl, "valueCodes[HelseReg]": koder, "valueCodes[HelseTjenomr]": "SOM",
                       "valueCodes[Kjonn]": "0", "valueCodes[Alder]": "*", "valueCodes[ContentsCode]": "Personer",
                       "valueCodes[Tid]": ",".join(AAR + ["2026"])}, f"ssb_13982_{kl}.json")
    S = {}
    for c, v in celler(d):
        a = int(c["Alder"].rstrip("+"))
        g = "0-17" if a < 18 else "18-66" if a < 67 else "67-79" if a < 80 else "80+"
        for gg in (g, "alle"):
            key = (c["Tid"], c["HelseReg"], gg)
            S[key] = S.get(key, 0) + (v or 0)
    for (t, r, g), v in sorted(S.items()):
        rader.append({"aar": t, "niva": "HF" if kl == "vs_HelseForetak02" else "lokalsykehus", "kode": r,
                      "omraade": ren(etikett(d, "HelseReg", r)), "alder": g, "personer": v})
skriv("befolkning_opptak.csv", rader, ["aar", "niva", "kode", "omraade", "alder", "personer"])

# 14022 kostnader. Faste 2025-priser finnes bare for landet totalt; derfor løpende priser.
d = data("14022", {"valueCodes[HelseReg]": ",".join(HF), "valueCodes[HelseTjenomr]": "TOT,SOM",
                   "valueCodes[InntektKostnad]": "K00,K02,K03,K05,K06,K08,K99,I00",
                   "valueCodes[ContentsCode]": "LopendePriser", "valueCodes[Tid]": ",".join(AAR)}, "ssb_14022.json")
skriv("kostnader_hf.csv", [{"aar": c["Tid"], "hf_kode": c["HelseReg"], "hf": HF[c["HelseReg"]],
                            "tjenesteomraade": ren(etikett(d, "HelseTjenomr", c["HelseTjenomr"])),
                            "post_kode": c["InntektKostnad"], "post": ren(etikett(d, "InntektKostnad", c["InntektKostnad"])),
                            "mill_kr_lopende": v} for c, v in celler(d) if v is not None],
      ["aar", "hf_kode", "hf", "tjenesteomraade", "post_kode", "post", "mill_kr_lopende"])

# 12764 kjøretid til nærmeste akuttmottak, 2019 (kommunekoder slik SSB oppgir dem)
m = json.load(open(os.path.join(RAA, "meta_12764.json"), encoding="utf-8"))
reg = [k for k in m["dimension"]["Region"]["category"]["index"] if k[:2] in ("18", "19", "20", "54", "55", "56") or k == "0"]
d = data("12764", {"valueCodes[Region]": ",".join(reg), "valueCodes[Persentiler]": "*",
                   "valueCodes[ContentsCode]": "*", "valueCodes[Tid]": "2019"}, "ssb_12764.json")
R = {}
for c, v in celler(d):
    if v is None:
        continue
    R.setdefault(c["Region"], {"region_kode": c["Region"], "region": ren(etikett(d, "Region", c["Region"]))})[
        ("km_" if c["ContentsCode"] == "Avstand" else "min_") + c["Persentiler"]] = v
rader = list(R.values())
pers = list(m["dimension"]["Persentiler"]["category"]["index"])
felt = ["region_kode", "region"] + [p + q for p in ("min_", "km_") for q in pers if any(p + q in r for r in rader)]
skriv("kjoretid_akuttmottak.csv", rader, felt)
