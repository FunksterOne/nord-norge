"""Fødsler per fødeinstitusjon i Helse Nord fra Medisinsk fødselsregister (FHI Statistikk Open API).
Brukes til å kontrollere hvilke fødesteder som faktisk har fødsler (fødeavdeling/fødestue) i 2024–2026.

Tabeller: Is1 (428) fødsler per år og fødeinstitusjon, P1b (491) fødte per måned og fødeinstitusjon.
Rådata lagres i kilder/data/sykehus/ (gitignorert). Utdata: utskrift + kilder/data/sykehus/mfr_helse_nord.json"""
import json, sys, time, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
API = "https://statistikk-data.fhi.no/api/open/v1/mfr/Table"
UT = Path(__file__).resolve().parents[1] / "kilder" / "data" / "sykehus"
UA = "nord-norge-dashbord/1.0 (halvard@affectum.no)"


def hent(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def kategorier(dim):
    ut = {}
    def gå(c):
        for x in c:
            ut[x["value"]] = x["label"]
            gå(x.get("children") or [])
    gå(dim["categories"])
    return ut


def institusjoner(tab):
    dims = hent(f"{API}/{tab}/dimension")["dimensions"]
    d = next(x for x in dims if x["code"] == "FODEINSTITUSJON")
    k = kategorier(d)
    return {v: l for v, l in k.items() if v.startswith("4_") and v.count("_") == 2}, dims


def spørring(tab, valg):
    body = {"dimensions": [{"code": k, "filter": "item", "values": v} for k, v in valg.items()],
            "response": {"format": "json-stat2"}}
    return hent(f"{API}/{tab}/data", body)


def tabell(js):
    """json-stat2 -> liste av (koordinater, verdi)."""
    ids, size = js["id"], js["size"]
    idx = [list(js["dimension"][i]["category"]["index"].keys()) if isinstance(js["dimension"][i]["category"]["index"], dict)
           else js["dimension"][i]["category"]["index"] for i in ids]
    verdi = js["value"]
    status = js.get("status") or {}
    rader = []
    for n in range(len(verdi) if isinstance(verdi, list) else 0):
        rest, koord = n, []
        for s in reversed(size):
            koord.append(rest % s); rest //= s
        koord = list(reversed(koord))
        rader.append(({ids[i]: idx[i][koord[i]] for i in range(len(ids))}, verdi[n],
                      status.get(str(n)) if isinstance(status, dict) else (status[n] if status else None)))
    return rader


def main():
    resultat = {"kilde": "FHI Statistikk Open API, Medisinsk fødselsregister, tabell Is1 (428) og P1b (491)",
                "lest": time.strftime("%Y-%m-%d")}
    inst, _ = institusjoner(428)
    år = [str(a) for a in range(2018, 2026)]
    js = spørring(428, {"FODSELSTIDSPUNKT_2005": år, "FODEINSTITUSJON": list(inst), "FODESTEDTYPE": ["1"],
                        "ENKELT_FLERFODSEL": ["0000"], "MEASURE_TYPE": ["SVANGERSKAP_ANTALL"]})
    (UT / "mfr_is1_428.json").write_text(json.dumps(js, ensure_ascii=False), encoding="utf-8")
    per = {}
    for k, v, st in tabell(js):
        per.setdefault(k["FODEINSTITUSJON"], {})[k["FODSELSTIDSPUNKT_2005"]] = v if v is not None else st
    print("Fødsler i institusjon per år (Is1):")
    print(f"{'kode':14} {'institusjon':42} " + " ".join(f"{a:>5}" for a in år))
    for kode, navn in inst.items():
        print(f"{kode:14} {navn:42} " + " ".join(f"{str(per.get(kode, {}).get(a, '')):>5}" for a in år))
    resultat["is1_fodsler_per_aar"] = {inst[k]: per.get(k, {}) for k in inst}

    inst2, _ = institusjoner(491)
    mnd = [f"{m:02d}" for m in range(1, 13)]
    js2 = spørring(491, {"FODSELSTIDSPUNKT_2020": ["2025", "2026"], "FODEINSTITUSJON": list(inst2),
                         "FODSELSMANED": mnd, "MEASURE_TYPE": ["BARN_ANTALL"]})
    (UT / "mfr_p1b_491.json").write_text(json.dumps(js2, ensure_ascii=False), encoding="utf-8")
    per2 = {}
    for k, v, st in tabell(js2):
        per2.setdefault(k["FODEINSTITUSJON"], {})[k["FODSELSTIDSPUNKT_2020"] + "-" + k["FODSELSMANED"]] = v if v is not None else st
    print("\nFødte per måned 2025–2026 (P1b, foreløpige tall):")
    kol = [f"{a}-{m}" for a in ("2025", "2026") for m in mnd]
    print(f"{'institusjon':42} " + " ".join(c[2:] for c in kol))
    for kode, navn in inst2.items():
        print(f"{navn:42} " + " ".join(f"{str(per2.get(kode, {}).get(c, '')):>5}" for c in kol))
    resultat["p1b_fodte_per_maned"] = {inst2[k]: per2.get(k, {}) for k in inst2}
    (UT / "mfr_helse_nord.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
