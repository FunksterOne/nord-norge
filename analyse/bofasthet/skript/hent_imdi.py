"""Hent IMDi-tall (åpent JSON-API bak imdi.no/statistikk, app-simapi-prod.azurewebsites.net).

Tabeller:
  flyktning_botid_flytting  Flyktninger etter botid (0–4, 5+) og om nåværende kommune er første
                            bosettingskommune. Kommune/fylke, 2014–2023 (kilde SSB).
  befolkning_botid          Innvandrere etter botid (0–4, 5–9, 10+) og verdensregion. 2014–2026.
  befolkning_innvandringsgrunn  Innvandrere etter innvandringsgrunn (kommune).

Lagrer rå svar i kilder/imdi/<tabell>_<nivå>.json.
"""
import json, time, urllib.request
from pathlib import Path

UT = Path(__file__).resolve().parents[1] / "kilder" / "imdi"
API = "https://app-simapi-prod.azurewebsites.net/"
HDR = {"User-Agent": "imdikator:api-client", "Accept": "application/json", "Content-Type": "application/json"}
NN = ("18", "19", "20", "54", "55", "56")


def get(path):
    req = urllib.request.Request(API + path, headers=HDR)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def query(body):
    rader, cont = [], None
    while True:
        b = dict(body)
        if cont:
            b["Continuation"] = cont
        req = urllib.request.Request(API + "query", data=json.dumps(b).encode(), headers=HDR)
        with urllib.request.urlopen(req, timeout=180) as r:
            svar = json.loads(r.read().decode("utf-8"))
        rader += svar.get("data", [])
        cont = svar.get("continuation")
        if not cont:
            return rader
        time.sleep(0.3)


def hent(tabell, dims):
    hg = get(f"headergroups/{tabell}")
    (UT / f"hg_{tabell}.json").write_text(json.dumps(hg, ensure_ascii=False), encoding="utf-8")
    for gruppe in hg["data"]:
        nivå = next(k for k in gruppe if k.endswith("Nr"))
        if nivå not in ("kommuneNr", "fylkeNr"):
            continue
        koder = [k for k in gruppe[nivå] if k[:2] in NN] if nivå == "kommuneNr" else gruppe[nivå]
        betingelser = {d: gruppe[d] for d in dims if d in gruppe}
        betingelser[nivå] = koder
        # API-et filtrerer bare på én region per spørring (klienten bruker /compare for flere)
        rader = []
        for kode in koder:
            body = {"TableName": tabell, "Include": [d for d in dims if d in gruppe] + [nivå, "enhet", "aar"],
                    "Conditions": {**betingelser, nivå: [kode], "enhet": gruppe["enhet"], "aar": gruppe["aar"]}}
            rader += query(body)
            time.sleep(0.2)
        (UT / f"{tabell}_{nivå}.json").write_text(json.dumps(rader, ensure_ascii=False, indent=0), encoding="utf-8")
        print(tabell, nivå, len(rader), "rader")
        time.sleep(0.5)


if __name__ == "__main__":
    hent("flyktning_botid_flytting", ["botid3", "forsteBosettingskommune"])
    hent("befolkning_botid", ["botid4", "vreg3"])
    hent("befolkning_innvandringsgrunn", ["innvgrunn5", "innvgrunn6", "innvandringsgrunn", "kjonn"])
