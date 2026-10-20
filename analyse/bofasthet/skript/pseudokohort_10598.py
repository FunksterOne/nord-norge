"""Pseudokohorter fra SSB 10598 (innvandrere etter fylke, landbakgrunn og ettårig botid, 2005–2026).

Kohort «innvandret år Y» = personer med botid 0 («bosatt under ett år») per 1.1.(Y+1).
Bevaringsgrad etter k år i område A:
    R_A(Y, k) = N_A(botid k, 1.1.(Y+1+k)) / N_A(botid 0, 1.1.(Y+1))
Dette er NETTO bevaring: utvandring, død og flytting ut av området trekker ned; innflytting fra
andre fylker av personer med samme botid trekker opp. For landet måler R bare utvandring + død.
Relativ bevaring R_A / R_landet ≈ netto innenlandsk bevaring i området.

Områder: Landet; Nordland (18); Troms og Finnmark samlet (19+20 til 2019, 54 i 2020–2023, 55+56 fra 2024);
Nord-Norge (Nordland + Troms og Finnmark); Troms (19) og Finnmark (20) bare innenfor 2005–2019, og
55/56 innenfor 2024–2026. Merk: Tjeldsund (1852) flyttet fra Nordland til Troms 2020 – liten brudd-
effekt for Nordland vs. Troms, ingen for Nord-Norge samlet.

Skriver resultat til kilder/avledet/pseudokohort_10598.json og en oversikt til stdout.
"""
import json
from pathlib import Path
from jsonstat import les

ROT = Path(__file__).resolve().parents[1]
UT = ROT / "kilder" / "avledet"
UT.mkdir(parents=True, exist_ok=True)

GRUPPER = {
    "flukt_land": ["564", "241", "346", "404", "452", "456", "356", "246", "420", "279"],
    "arbeid_EU_ost": ["131", "136"],
    "sverige": ["106"],
    "russland": ["140"],
    "filippinene_thailand": ["428", "568"],
    "ukraina": ["148"],
}
LANDNAVN = {}


def områdeverdi(v, omr, b, t, land=None):
    """Sum over fylkeskoder som utgjør området i år t (1.1.t)."""
    t = int(t)
    if omr == "Landet":
        koder = ["0"]
    elif omr == "Nordland":
        koder = ["18"]
    elif omr == "Troms og Finnmark":
        koder = ["19", "20"] if t <= 2019 else (["54"] if t <= 2023 else ["55", "56"])
    elif omr == "Nord-Norge":
        koder = ["18"] + (["19", "20"] if t <= 2019 else (["54"] if t <= 2023 else ["55", "56"]))
    elif omr == "Troms":
        koder = ["19"] if t <= 2019 else (["55"] if t >= 2024 else None)
    elif omr == "Finnmark":
        koder = ["20"] if t <= 2019 else (["56"] if t >= 2024 else None)
    if koder is None:
        return None
    s = 0
    for k in koder:
        if land is None:
            x = v.get((k, b, "Personer", str(t)))
        else:
            x = sum((v.get((k, l, b, "Personer", str(t))) or 0) for l in land)
        if x is None:
            return None
        s += x
    return s


def botid_kode(k):
    return "40+" if k >= 40 else f"{k:02d}"


def main():
    _, _, et, v_alle = les(ROT / "kilder/ssb/10598_nn_alle.json")
    _, koder_l, et_l, v_land = les(ROT / "kilder/ssb/10598_nn_land.json")
    resultat = []
    år = list(range(2005, 2027))
    for gruppe, land in [("alle", None)] + list(GRUPPER.items()):
        v = v_alle if land is None else v_land
        for omr in ["Landet", "Nord-Norge", "Nordland", "Troms og Finnmark", "Troms", "Finnmark"]:
            for s0 in (0, 1):  # startbotid: 0 = innvandringsåret, 1 = ett år etter (demper mottakseffekt)
              for t0 in år:  # 1.1.t0, botid s0 => innvandret t0-1-s0
                n0 = områdeverdi(v, omr, botid_kode(s0), t0, land)
                if not n0:
                    continue
                for k in (1, 2, 3, 5, 8, 10, 12, 15, 18, 20, 21):
                    t1 = t0 + k - s0
                    if t1 > 2026 or k <= s0:
                        continue
                    if omr in ("Troms", "Finnmark") and not ((t0 <= 2019 and t1 <= 2019) or t0 >= 2024):
                        continue
                    nk = områdeverdi(v, omr, botid_kode(k), t1, land)
                    if nk is None:
                        continue
                    resultat.append({"gruppe": gruppe, "område": omr, "innvandret_år": t0 - 1 - s0,
                                     "start_botid": s0, "botid_år": k, "n_start": n0, "n_slutt": nk,
                                     "bevaring": round(nk / n0, 4)})
    # relativ bevaring mot landet
    idx = {(r["gruppe"], r["område"], r["innvandret_år"], r["start_botid"], r["botid_år"]): r for r in resultat}
    for r in resultat:
        l = idx.get((r["gruppe"], "Landet", r["innvandret_år"], r["start_botid"], r["botid_år"]))
        r["relativ_til_landet"] = round(r["bevaring"] / l["bevaring"], 4) if l and l["bevaring"] else None
    (UT / "pseudokohort_10598.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=0), encoding="utf-8")

    # oversikt (START = startbotid som vises)
    import sys
    START = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    for gruppe in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["alle", "flukt_land", "arbeid_EU_ost", "sverige"]):
        print(f"\n### {gruppe}: netto bevaring (relativ til landet i parentes)")
        for k in (5, 10, 15, 20):
            print(f"  botid {k} år")
            for omr in ["Landet", "Nord-Norge", "Nordland", "Troms og Finnmark", "Troms", "Finnmark"]:
                rad = [r for r in resultat if r["gruppe"] == gruppe and r["område"] == omr and r["botid_år"] == k and r["start_botid"] == START]
                if not rad:
                    continue
                txt = "  ".join(f"{r['innvandret_år']}:{r['bevaring']*100:.0f}({(r['relativ_til_landet'] or 0)*100:.0f})[{r['n_start']}]" for r in rad)
                print(f"    {omr:18s} {txt}")


if __name__ == "__main__":
    main()
