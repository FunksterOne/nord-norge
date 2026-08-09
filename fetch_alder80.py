#!/usr/bin/env python3
"""Legger til aldersgruppen 80+ (a80) i DATA.proj fra SSB 14746 MMMM.

Aldringsgrafen i kommunekortet lover at «80+-andelen vokser raskest», men
serien manglet paa SSB-banen — bare TF-MVP-vinduene hadde a80. Dette scriptet
henter 80+ per kommune fra hovedalternativet, slik at alle fire seriene i
grafen kommer fra samme kilde.

a80 er en DELMENGDE av a65 og skal ikke summeres med den.
"""
import json
from pathlib import Path

from fetch_framskriving import hent_alternativ, serie_gruppe, NYE_AAR

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"


def main():
    js = DATA_JS.read_text(encoding="utf-8")
    linjer = js.split("\n")
    idx = next(i for i, l in enumerate(linjer) if l.startswith("const DATA = "))
    DATA = json.loads(linjer[idx][len("const DATA = "):].rstrip(";"))
    proj = DATA["proj"]
    assert proj["meta"]["tabell"] == "14746", "krever 14746-basert proj"
    assert proj["years"] == NYE_AAR, "aarsrekken i proj matcher ikke scriptet"
    koder = list(proj["kommuner"].keys())

    print("Henter 14746 MMMM for aldersgruppe 80+ ...", flush=True)
    mmmm = hent_alternativ(koder, "Personer")
    for k in koder:
        proj["kommuner"][k]["a80"] = serie_gruppe(mmmm, k, 80, 105)

    n = len(NYE_AAR)
    proj["landsdel"]["a80"] = [sum(proj["kommuner"][k]["a80"][i] for k in koder)
                               for i in range(n)]

    b = proj["kommuner"]["1804"]
    print(f"Bodoe 80+: {b['a80'][0]} (2026) -> {b['a80'][-1]} (2050), "
          f"{(b['a80'][-1]/b['a80'][0]-1)*100:+.0f} %. Til sammenligning 65+: "
          f"{(b['a65'][-1]/b['a65'][0]-1)*100:+.0f} %.")
    L = proj["landsdel"]
    print(f"Landsdelen 80+: {L['a80'][0]} -> {L['a80'][-1]} ({(L['a80'][-1]/L['a80'][0]-1)*100:+.0f} %)")

    linjer[idx] = "const DATA = " + json.dumps(DATA, ensure_ascii=False, separators=(",", ":")) + ";"
    DATA_JS.write_text("\n".join(linjer), encoding="utf-8")
    print("Injisert a80 i DATA.proj.")


if __name__ == "__main__":
    main()
