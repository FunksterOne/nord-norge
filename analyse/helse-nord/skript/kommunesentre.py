"""Koordinater for administrasjonssenteret i hver av de 80 kommunene (Kartverket stedsnavn-API).
Brukes som startpunkt for reisetid til sykehus. Treffet må ligge i riktig kommune (knr-filter).
Utdata: analyse/helse-nord/data/kommunesentre.json"""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
UT = Path(__file__).resolve().parents[1] / "data" / "kommunesentre.json"

# Administrasjonssenter per kommune (2024-inndeling)
SENTER = {
    "1804": "Bodø", "1806": "Narvik", "1811": "Terråk", "1812": "Vik", "1813": "Brønnøysund", "1815": "Gladstad",
    "1816": "Forvika", "1818": "Silvalen", "1820": "Sandnessjøen", "1822": "Leland", "1824": "Mosjøen", "1825": "Trofors",
    "1826": "Hattfjelldal", "1827": "Solfjellsjøen", "1828": "Nesna", "1832": "Korgen", "1833": "Mo i Rana", "1834": "Lurøy",
    "1835": "Husøy", "1836": "Vågaholmen", "1837": "Ørnes", "1838": "Inndyr", "1839": "Moldjord", "1840": "Rognan",
    "1841": "Fauske", "1845": "Straumen", "1848": "Leines", "1851": "Lødingen", "1853": "Bogen", "1856": "Røstlandet",
    "1857": "Sørland", "1859": "Ramberg", "1860": "Leknes", "1865": "Svolvær", "1866": "Stokmarknes", "1867": "Straume",
    "1868": "Myre", "1870": "Sortland", "1871": "Andenes", "1874": "Reine", "1875": "Oppeid",
    "5501": "Tromsø", "5503": "Harstad", "5510": "Borkenes", "5512": "Evenskjer", "5514": "Hamnvik", "5516": "Årstein",
    "5518": "Tennevoll", "5520": "Setermoen", "5522": "Sjøvegan", "5524": "Moen", "5526": "Sørreisa", "5528": "Brøstadbotn",
    "5530": "Finnsnes", "5532": "Storsteinnes", "5534": "Hansnes", "5536": "Lyngseidet", "5538": "Hatteng",
    "5540": "Olderdalen", "5542": "Skjervøy", "5544": "Storslett", "5546": "Burfjord",
    "5601": "Alta", "5603": "Hammerfest", "5605": "Kirkenes", "5607": "Vadsø", "5610": "Karasjok", "5612": "Kautokeino",
    "5614": "Øksfjord", "5616": "Breivikbotn", "5618": "Havøysund", "5620": "Honningsvåg", "5622": "Lakselv",
    "5624": "Kjøllefjord", "5626": "Mehamn", "5628": "Tana bru", "5630": "Berlevåg", "5632": "Båtsfjord",
    "5634": "Vardø", "5636": "Varangerbotn",
}
TYPER = ["By", "Tettsted", "Tettbebyggelse", "Tettsteddel", "Bygd", "Grend", "Bydel", "Gard", "Øy", "Kommune"]


def sok(navn, knr):
    q = urllib.parse.urlencode({"sok": navn, "knr": knr, "treffPerSide": 20, "utkoordsys": 4258, "fuzzy": "false"})
    req = urllib.request.Request("https://api.kartverket.no/stedsnavn/v1/navn?" + q, headers={"User-Agent": "nord-norge-dashbord/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=60)).get("navn", [])


def main():
    ut = {}
    for knr, navn in SENTER.items():
        alle = sok(navn, knr)
        treff = sorted([t for t in alle if t.get("navneobjekttype") in TYPER], key=lambda t: TYPER.index(t["navneobjekttype"]))
        if not treff and alle:  # ellers første treff uansett type, med typen i utdataene
            treff = alle
        if not treff:
            print(f"MANGLER {knr} {navn}"); continue
        t = treff[0]; p = t["representasjonspunkt"]
        ut[knr] = {"sted": navn, "type": t["navneobjekttype"], "lon": round(p["øst"], 5), "lat": round(p["nord"], 5)}
        print(knr, navn, t["navneobjekttype"], ut[knr]["lat"], ut[knr]["lon"])
        time.sleep(0.2)
    UT.parent.mkdir(parents=True, exist_ok=True)
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(ut), "av", len(SENTER))


if __name__ == "__main__":
    main()
