"""Reisetid med bil fra kommunesenteret til nærmeste akuttsykehus, nærmeste sykehus av alle typer
og regionsykehuset (UNN Tromsø), beregnet med OSRM (OpenStreetMap, bilprofil, ferger med rutetid).
Inndata: data/kommunesentre.json og data/sykehus.json. Utdata: data/reisetid.json

Forbehold: kjøretid uten kø, ventetid på ferge og værstengte veier; luftambulanse er ikke med.
Startpunktet er administrasjonssenteret, ikke der hver innbygger bor."""
import json, sys, time, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parents[1] / "data"
OSRM = "https://router.project-osrm.org"
AKUTT = {"regionsykehus", "stort_akutt", "akutt"}
# Nærmeste akuttmottak kan ligge utenfor Helse Nord (Bindal har kortere vei til Namsos). Koordinat: Kartverket stedsnavn.
EKSTRA = [{"navn": "Sykehuset Namsos", "hf": "HNT", "sted": "Namsos", "niva": "akutt", "utenfor": True, "lat": 64.47069, "lon": 11.50589,
           "kilde": "Helse Nord-Trøndelag; koordinat fra Kartverket stedsnavn"}]


def hent(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nord-norge-dashbord/1.0 (aapne data)"})
    for forsok in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:  # offentlig demotjener: vent og prøv igjen
            print("  venter:", e); time.sleep(5 * (forsok + 1))
    raise RuntimeError(url)


def main():
    K = json.loads((D / "kommunesentre.json").read_text(encoding="utf-8"))
    H = [h for h in json.loads((D / "sykehus.json").read_text(encoding="utf-8")) if h.get("lat") and "Longyearbyen" not in h["navn"]] + EKSTRA
    knr = sorted(K)
    pkt = lambda o: f"{o['lon']},{o['lat']}"
    dest = ";".join(pkt(h) for h in H)
    tid, km = {}, {}
    for i in range(0, len(knr), 40):  # matrise i biter, så adressen ikke blir for lang
        bit = knr[i:i + 40]
        url = f"{OSRM}/table/v1/driving/{';'.join(pkt(K[k]) for k in bit)};{dest}?sources={';'.join(str(j) for j in range(len(bit)))}" \
              f"&destinations={';'.join(str(len(bit) + j) for j in range(len(H)))}&annotations=duration,distance"
        d = hent(url)
        if d.get("code") != "Ok":
            raise RuntimeError(d)
        for j, k in enumerate(bit):
            tid[k], km[k] = d["durations"][j], d["distances"][j]
        time.sleep(1)
    ut = {}
    for k in knr:
        rader = [(tid[k][j], km[k][j], h) for j, h in enumerate(H) if tid[k][j] is not None]
        akutt = min((r for r in rader if r[2]["niva"] in AKUTT), key=lambda r: r[0])
        akutt_hn = min((r for r in rader if r[2]["niva"] in AKUTT and not r[2].get("utenfor")), key=lambda r: r[0])
        alle = min(rader, key=lambda r: r[0])
        reg = next(r for r in rader if r[2]["niva"] == "regionsykehus")
        # Rute til nærmeste akuttsykehus: går den med ferge?
        r = hent(f"{OSRM}/route/v1/driving/{pkt(K[k])};{akutt[2]['lon']},{akutt[2]['lat']}?steps=true&overview=false")
        ferge = any(s.get("mode") == "ferry" for leg in r["routes"][0]["legs"] for s in leg["steps"])
        ut[k] = {"sted": K[k]["sted"],
                 "akutt": {"navn": akutt[2]["navn"], "min": round(akutt[0] / 60), "km": round(akutt[1] / 1000), "ferge": ferge},
                 "akutt_hn": {"navn": akutt_hn[2]["navn"], "min": round(akutt_hn[0] / 60), "km": round(akutt_hn[1] / 1000)},
                 "naermest": {"navn": alle[2]["navn"], "niva": alle[2]["niva"], "min": round(alle[0] / 60), "km": round(alle[1] / 1000)},
                 "regionsykehus": {"navn": reg[2]["navn"], "min": round(reg[0] / 60), "km": round(reg[1] / 1000)}}
        print(k, K[k]["sted"], "→", akutt[2]["navn"], ut[k]["akutt"]["min"], "min", "(ferge)" if ferge else "")
        time.sleep(1)
    (D / "reisetid.json").write_text(json.dumps({"kilde": "OSRM (OpenStreetMap), bilprofil, beregnet " + time.strftime("%Y-%m-%d"),
                                                 "sykehus": H, "kommuner": ut}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
