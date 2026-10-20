"""Hent rådata fra SSB (PxWebApi v0, JSON-stat2) og lagre i kilder/ssb/.

Tabellene:
  10598  Innvandrere etter fylke, landbakgrunn og botid (ettårig), 2005–2026
  08377  Personer med flyktningbakgrunn etter botid og landbakgrunn (landet), 2010–2026
  05648  Samme, avsluttet serie 1998–2009
  03810  Personer med flyktningbakgrunn etter fylke, 1998–2026
  06318  Innvandringer 1990–t etter innvandringsgrunn og om de fortsatt er bosatt
  07113  Innvandringer etter innvandringsgrunn og innflyttingsår (strøm)
  10824  Tidligere introdeltakere: nåværende bosted vs. bosted ved programdeltakelse (K)
  07210  Innenlandsk nettoinnflytting etter innvandringskategori (K)
"""
import json, time, urllib.request
from pathlib import Path

UT = Path(__file__).resolve().parents[1] / "kilder" / "ssb"
UT.mkdir(parents=True, exist_ok=True)
NN_FYLKER = ["0", "18", "55", "56", "54", "19", "20"]
LAND = ["131", "136", "106", "140", "148", "241", "246", "346", "356", "404", "452", "456", "564", "420", "428", "568", "279"]


def post(tab, query, navn):
    body = json.dumps({"query": query, "response": {"format": "json-stat2"}}).encode()
    req = urllib.request.Request(f"https://data.ssb.no/api/v0/no/table/{tab}", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "affectum-nord-norge/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    (UT / f"{navn}.json").write_bytes(data)
    print(navn, len(data), "byte")
    time.sleep(1)


def q(code, vals, filt="item"):
    return {"code": code, "selection": {"filter": filt, "values": vals}}


def nn_kommuner():
    """Kommunekoder i Nord-Norge (2024-inndeling 18xx, 55xx, 56xx og eldre 19xx/20xx/54xx)."""
    m = json.loads((UT.parent / "meta" / "10824.json").read_text(encoding="utf-8"))
    reg = m["variables"][0]["values"]
    return [r for r in reg if r[:2] in ("18", "19", "20", "54", "55", "56") or r == "0"]


if __name__ == "__main__":
    import sys
    valg = set(sys.argv[1:]) or {"10598", "08377", "05648", "03810", "06318", "07113", "10824", "07210"}
    if "10598" in valg:
        post("10598", [q("Region", NN_FYLKER), q("Botid", ["*"], "all")], "10598_nn_alle")
        post("10598", [q("Region", NN_FYLKER), q("Lanbakgrunn", LAND), q("Botid", ["*"], "all")], "10598_nn_land")
    if "08377" in valg:
        post("08377", [q("Botid", ["*"], "all"), q("Lanbakgrunn", ["*"], "all")], "08377_landet")
    if "05648" in valg:
        post("05648", [q("Botid", ["*"], "all"), q("Lanbakgrunn", ["*"], "all")], "05648_landet")
    if "03810" in valg:
        post("03810", [q("Region", ["18", "55", "56", "54", "19", "20"]), q("Statsborg", ["*"], "all")], "03810_nn")
    if "06318" in valg:
        post("06318", [q("Innvandringsgrunn", ["*"], "all"), q("Bosettingsstatus", ["*"], "all")], "06318_landet")
    if "07113" in valg:
        post("07113", [q("Innvandringsgrunn", ["*"], "all"), q("Lanbakgrunn", ["1", "2", "3", "4", "5", "6", "8", "9"])], "07113_landet")
    if "10824" in valg:
        reg = nn_kommuner()
        post("10824", [q("Region", reg), q("Kjonn", ["0"]), q("Arbeidsmarkedsstatus", ["00"])], "10824_nn")
    if "07210" in valg:
        m = json.loads((UT.parent / "meta" / "07210.json").read_text(encoding="utf-8"))
        reg = [r for r in m["variables"][0]["values"] if r[:2] in ("18", "19", "20", "54", "55", "56")]
        post("07210", [q("Region", reg), q("InnvandrKat", ["*"], "all")], "07210_nn")
