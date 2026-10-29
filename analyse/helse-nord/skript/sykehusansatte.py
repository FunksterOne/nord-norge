"""Sysselsatte i sykehustjenester (SN2007 86.1) etter arbeidssted og bosted, SSB 13470.
Per kommune 2020–siste år (agg_KommSummer; Narvik og Hamarøy finnes fra 2020), og for Nord-Norge og landet
2008–siste år (fylkeskodene følger inndelingen det enkelte år). Utdata: data/sykehusansatte.json"""
import json, sys, urllib.request, urllib.parse
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROT = Path(__file__).resolve().parents[3]
D = Path(__file__).resolve().parents[1] / "data"
V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/"


def get(p):
    u = V2 + "13470/data?" + urllib.parse.urlencode({"lang": "no", "outputFormat": "json-stat2", **p})
    return json.load(urllib.request.urlopen(u, timeout=300))


def celler(d):
    ids = d["id"]
    keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
    for n, v in enumerate(d["value"]):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1):
            co[ids[i]] = keys[i][rest % d["size"][i]]; rest //= d["size"][i]
        yield co, v


def main():
    import re
    dj = (ROT / "assets" / "data.js").read_text(encoding="utf-8")
    knr = sorted({m.group(1) for m in re.finditer(r'"(1[89]\d\d|5[56]\d\d)":\{"navn"', dj)})
    aar_alle = [str(a) for a in range(2008, 2026)]
    # Per kommune
    K = {}
    for co, v in celler(get({"codelist[Region]": "agg_KommSummer", "valueCodes[Region]": ",".join("K-" + k for k in knr),
                             "valueCodes[NACE2007]": "86.1,86-88", "valueCodes[ContentsCode]": "SysselsatteArb,Sysselsatte",
                             "valueCodes[Tid]": ",".join(aar_alle[12:])})):
        K.setdefault(co["Region"][2:], {}).setdefault(co["ContentsCode"] + "|" + co["NACE2007"], {})[co["Tid"]] = v
    # Nord-Norge og landet
    V = {}
    for co, v in celler(get({"valueCodes[Region]": "0,18,19,20,54,55,56", "valueCodes[NACE2007]": "86.1,86-88",
                             "valueCodes[ContentsCode]": "SysselsatteArb", "valueCodes[Tid]": ",".join(aar_alle)})):
        V[(co["Region"], co["NACE2007"], int(co["Tid"]))] = v or 0
    regs = lambda t: ["18", "19", "20"] if t < 2020 else (["18", "54"] if t < 2024 else ["18", "55", "56"])
    serie = {n: {"nn": [sum(V[(r, n, t)] for r in regs(t)) for t in range(2008, 2026)],
                 "landet": [V[("0", n, t)] for t in range(2008, 2026)]} for n in ("86.1", "86-88")}
    ut = {"aar": list(range(2008, 2026)), "serie": serie, "kommuner_aar": [int(a) for a in aar_alle[12:]],
          "kommuner": {k: {"arb_sykehus": [K[k]["SysselsatteArb|86.1"][a] for a in aar_alle[12:]],
                           "bos_sykehus": [K[k]["Sysselsatte|86.1"][a] for a in aar_alle[12:]],
                           "arb_helse": [K[k]["SysselsatteArb|86-88"][a] for a in aar_alle[12:]]} for k in sorted(K)},
          "kilde": "SSB 13470, sysselsatte 15–74 år, 4. kvartal. Sykehustjenester = SN2007 86.1; helse og sosial = 86–88."}
    s = sum(ut["kommuner"][k]["arb_sykehus"][-1] or 0 for k in ut["kommuner"])
    print("kommuner", len(ut["kommuner"]), "sum sykehus arbeidssted 2025", s, "NN-serie 2025", serie["86.1"]["nn"][-1],
          "landet", serie["86.1"]["landet"][-1], "NN 2008", serie["86.1"]["nn"][0])
    (D / "sykehusansatte.json").write_text(json.dumps(ut, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
