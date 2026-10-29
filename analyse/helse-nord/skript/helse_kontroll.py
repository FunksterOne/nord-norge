"""Kontroll av demografipåstandene i Helse Nords regionale utviklingsplan (kronikk 28.10.2026).
SSB 07459 (faktisk 1.1.) og 14746 (framskriving, hovedalternativ MMMM) for Nord-Norge, Helgeland og landet."""
import json, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/"


def get(tab, p):
    u = V2 + tab + "/data?" + urllib.parse.urlencode({"lang": "no", "outputFormat": "json-stat2", **p})
    return json.load(urllib.request.urlopen(u, timeout=300))


def celler(d):
    ids = d["id"]
    keys = [sorted(d["dimension"][i]["category"]["index"], key=d["dimension"][i]["category"]["index"].get) for i in ids]
    for n, v in enumerate(d["value"]):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1):
            co[ids[i]] = keys[i][rest % d["size"][i]]; rest //= d["size"][i]
        yield co, v


def alder(a):
    return 105 if a.endswith('+') else int(a)


# Faktisk: 07459 for de tre fylkene, 2022–2026, ettårig alder
A = {}
for co, v in celler(get("07459", {"codelist[Region]": "agg_KommFylker", "valueCodes[Region]": "F-18,F-55,F-56",
                                   "valueCodes[Tid]": "2022,2023,2024,2025,2026", "valueCodes[Alder]": "*",
                                   "valueCodes[Kjonn]": "1,2", "valueCodes[ContentsCode]": "Personer1"})):
    A.setdefault(co["Tid"], [0] * 106)[alder(co["Alder"])] += v or 0
print("Nord-Norge 1. januar (SSB 07459):")
for t in sorted(A):
    a = A[t]
    print(f"  {t}: 0–19 {sum(a[:20]):>7}  0–18 {sum(a[:19]):>7}  65+ {sum(a[65:]):>7}  66+ {sum(a[66:]):>7}")

# Framskriving 14746: metadata for regioner og alder
m = json.load(urllib.request.urlopen(V2 + "14746/metadata?lang=no", timeout=120))
dims = {k: list(v["category"]["index"]) for k, v in m["dimension"].items()}
print("14746 dimensjoner:", {k: (len(v), v[:3]) for k, v in dims.items()})


# Framskriving 14746 MMMM: landet, fylkene og Helgeland-kommunene, 2026–2045
HEL = [str(x) for x in json.load(open('helgeland.json'))]
R = {}
aar = [str(a) for a in range(2026, 2046)]
for regs in (["0", "18", "55", "56"], HEL):
    for co, v in celler(get("14746", {"valueCodes[Region]": ",".join(regs), "valueCodes[Tid]": ",".join(aar),
                                       "valueCodes[Alder]": "*", "valueCodes[Kjonn]": "1,2", "valueCodes[ContentsCode]": "Personer"})):
        g = "landet" if co["Region"] == "0" else ("NN" if co["Region"] in ("18", "55", "56") else "helgeland")
        R.setdefault((g, co["Tid"]), [0] * 106)[alder(co["Alder"])] += v or 0
for g in ("landet", "NN", "helgeland"):
    t0, t1 = R[(g, "2026")], R[(g, "2045")]
    kryss = next((t for t in aar if sum(R[(g, t)][65:]) > sum(R[(g, t)][:20])), "før 2026")
    print(f"{g:10s} 2026 {sum(t0):>8} 2045 {sum(t1):>8} vekst {100*(sum(t1)/sum(t0)-1):5.1f} %  "
          f"0–19 2026→2045 {100*(sum(t1[:20])/sum(t0[:20])-1):6.1f} %  65+ {100*(sum(t1[65:])/sum(t0[65:])-1):5.1f} %  "
          f"20–64 {100*(sum(t1[20:65])/sum(t0[20:65])-1):5.1f} %  65+>0–19 første år: {kryss}")
