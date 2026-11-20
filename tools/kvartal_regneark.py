#!/usr/bin/env python3
"""Regneark med folketall per kvartal for de 80 kommunene i Nord-Norge (SSB 01222).

Viser folketallet ved inngangen av året og ved utgangen av hvert kvartal i år, endringen per kvartal og hittil i år, og
hva endringen består av (fødselsoverskudd og nettoinnflytting). Fylkene og Nord-Norge er summen av kommunene.
Bruk:  python tools/kvartal_regneark.py <utfil.xlsx> [år]
"""
import json, re, sys, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")
UT = Path(sys.argv[1])
AAR = sys.argv[2] if len(sys.argv) > 2 else str(date.today().year)
ROT = Path(__file__).resolve().parents[1]

# Kommunenavn og fylke fra dashbordets datafil
js = (ROT / "assets/data.js").read_text(encoding="utf-8")
KOM = {nr: (navn, fylke) for nr, navn, fylke in re.findall(r'"(\d{4})":\{"navn":"([^"]+)","fylke":"([^"]+)"', js)}
assert len(KOM) == 80, len(KOM)
# Norsk navn først der SSB har samisk eller kvensk navn først
NORSK = {"Hábmer": "Hamarøy", "Aarborte": "Hattfjelldal", "Dielddanuorri": "Tjeldsund", "Gáivuotna": "Kåfjord", "Loabák": "Lavangen",
         "Guovdageaidnu": "Kautokeino", "Deatnu": "Tana", "Kárásjohka": "Karasjok", "Unjárga": "Nesseby"}


def visningsnavn(navn):
    deler = navn.split(" - ")
    if deler[0] in NORSK:
        return f"{NORSK[deler[0]]} ({deler[0]})"
    return deler[0] if len(deler) == 1 else f"{deler[0]} ({' – '.join(deler[1:])})"


# Hent 01222
kvartaler = [f"{AAR}K{i}" for i in range(1, 5)]
p = {"lang": "no", "outputFormat": "json-stat2", "valueCodes[Region]": ",".join(KOM),
     "valueCodes[ContentsCode]": "Folketallet1,Folketallet11,Fodselsoverskudd4,Nettoinnflytting9,Folketilvekst10", "valueCodes[Tid]": "*"}
j = json.load(urllib.request.urlopen("https://data.ssb.no/api/pxwebapi/v2/tables/01222/data?" + urllib.parse.urlencode(p), timeout=120))
dims, size = j["id"], j["size"]
kat = {d: list(j["dimension"][d]["category"]["index"]) for d in dims}
V = {}
for i, x in enumerate(j["value"]):
    idx, rest = {}, i
    for d, n in zip(reversed(dims), reversed(size)):
        idx[d] = kat[d][rest % n]; rest //= n
    V[(idx["Region"], idx["ContentsCode"], idx["Tid"])] = x
kv = [k for k in kvartaler if any(V.get((nr, "Folketallet11", k)) is not None for nr in KOM)]
assert kv, f"ingen kvartaler for {AAR} i 01222"
DATO = {"K1": "1. april", "K2": "1. juli", "K3": "1. oktober", "K4": "31. desember"}
print("Kvartaler:", kv)

# Kontroll: utgangen av ett kvartal = inngangen av neste
for nr in KOM:
    for a, b in zip(kv, kv[1:]):
        assert V[(nr, "Folketallet11", a)] == V[(nr, "Folketallet1", b)], (nr, a, b)

rader = []
for nr, (navn, fylke) in KOM.items():
    start = V[(nr, "Folketallet1", kv[0])]
    slutt = [V[(nr, "Folketallet11", k)] for k in kv]
    endr = [V[(nr, "Folketilvekst10", k)] for k in kv]
    fod = [V[(nr, "Fodselsoverskudd4", k)] for k in kv]
    flytt = [V[(nr, "Nettoinnflytting9", k)] for k in kv]
    rader.append({"fylke": fylke, "nr": nr, "navn": visningsnavn(navn), "start": start, "slutt": slutt, "endr": endr, "fod": fod, "flytt": flytt})

# ---------------------------------------------------------------- regneark
GRAN, LYS, STREK = "1F4D43", "F3F5F4", "CDD3D0"
hode_font, hode_fyll = Font(bold=True, color="FFFFFF", name="Calibri"), PatternFill("solid", fgColor=GRAN)
sum_font, sum_fyll = Font(bold=True), PatternFill("solid", fgColor=LYS)
tynn = Side(style="thin", color=STREK)
TALL, ENDR, PST = '#,##0', '+#,##0;-#,##0;0', '+0.0%;-0.0%;0.0%'   # vises med norsk tusenskille og desimalkomma i Excel

wb = Workbook()
ws = wb.active
ws.title = f"Folketall {AAR}"
hode = ["Fylke", "Kommunenr.", "Kommune", f"1. januar {AAR}"] + [f"{DATO[k[-2:]]} {AAR}" for k in kv] + \
       [f"Endring {k[-1]}. kvartal" for k in kv] + [f"Endring hittil i {AAR}", "Endring i prosent"]
ws.append(hode)
n_k = len(kv)
c_start, c_slutt0, c_endr0 = 4, 5, 5 + n_k
c_tot, c_pst = c_endr0 + n_k, c_endr0 + n_k + 1


def skriv_rad(ws, r, fylke, nr, navn, verdier=None, sum_rader=None, uthev=False):
    """Kommuner: folketallene som verdier. Fylker og Nord-Norge: summer som formler. Endringene er formler.
    sum_rader: radnumre som summeres (for fylker og Nord-Norge)."""
    ws.cell(r, 1, fylke); ws.cell(r, 2, nr); ws.cell(r, 3, navn)
    for c in range(c_start, c_start + 1 + n_k):
        L = get_column_letter(c)
        if sum_rader:
            ws.cell(r, c, f"=SUM({L}{sum_rader[0]}:{L}{sum_rader[-1]})" if sum_rader == list(range(sum_rader[0], sum_rader[-1] + 1))
                    else "=" + "+".join(f"{L}{x}" for x in sum_rader))
        else:
            ws.cell(r, c, verdier[c - c_start])
        ws.cell(r, c).number_format = TALL
    for i in range(n_k):   # endring per kvartal: utgang minus forrige utgang
        cur, prev = get_column_letter(c_slutt0 + i), get_column_letter(c_slutt0 + i - 1)
        ws.cell(r, c_endr0 + i, f"={cur}{r}-{prev}{r}").number_format = ENDR
    s_, e_ = get_column_letter(c_start), get_column_letter(c_slutt0 + n_k - 1)
    ws.cell(r, c_tot, f"={e_}{r}-{s_}{r}").number_format = ENDR
    ws.cell(r, c_pst, f"={get_column_letter(c_tot)}{r}/{s_}{r}").number_format = PST
    if uthev:
        for c in range(1, c_pst + 1):
            ws.cell(r, c).font = sum_font; ws.cell(r, c).fill = sum_fyll


r = 2
fylkesrader = []
for fylke in ("Nordland", "Troms", "Finnmark"):
    ks = sorted((x for x in rader if x["fylke"] == fylke), key=lambda x: -x["slutt"][-1])
    forste = r
    for x in ks:
        skriv_rad(ws, r, fylke, x["nr"], x["navn"], [x["start"]] + x["slutt"]); r += 1
    skriv_rad(ws, r, fylke, "", f"{fylke} i alt", sum_rader=list(range(forste, r)), uthev=True)
    fylkesrader.append(r); r += 2
skriv_rad(ws, r, "Nord-Norge", "", "Nord-Norge i alt", sum_rader=fylkesrader, uthev=True)
for c in ws[1]:
    c.font = hode_font; c.fill = hode_fyll; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
ws.row_dimensions[1].height = 32
for c, b in zip(range(1, c_pst + 1), [11, 11, 30] + [13] * (1 + n_k) + [12] * n_k + [14, 12]):
    ws.column_dimensions[get_column_letter(c)].width = b
ws.freeze_panes = "D2"
ws.auto_filter.ref = f"A1:{get_column_letter(c_pst)}{r - 3}"

# Fane 2: hva endringen består av
w2 = wb.create_sheet("Hva endringen består av")
h2 = ["Fylke", "Kommunenr.", "Kommune"]
for k in kv:
    h2 += [f"{k[-1]}. kv.: fødte minus døde", f"{k[-1]}. kv.: nettoinnflytting"]
h2 += [f"Hittil i {AAR}: fødte minus døde", f"Hittil i {AAR}: nettoinnflytting", f"Hittil i {AAR}: i alt"]
w2.append(h2)
for fylke in ("Nordland", "Troms", "Finnmark"):
    for x in sorted((x for x in rader if x["fylke"] == fylke), key=lambda x: -x["slutt"][-1]):
        rad = [fylke, x["nr"], x["navn"]]
        for i in range(n_k):
            rad += [x["fod"][i], x["flytt"][i]]
        rad += [sum(x["fod"]), sum(x["flytt"]), sum(x["endr"])]
        w2.append(rad)
for row in w2.iter_rows(min_row=2, min_col=4):
    for c in row:
        c.number_format = ENDR
for c in w2[1]:
    c.font = hode_font; c.fill = hode_fyll; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
w2.row_dimensions[1].height = 44
for c, b in zip(range(1, len(h2) + 1), [11, 11, 30] + [13] * (len(h2) - 3)):
    w2.column_dimensions[get_column_letter(c)].width = b
w2.freeze_panes = "D2"
w2.auto_filter.ref = w2.dimensions

# Fane 3: om tallene
w3 = wb.create_sheet("Om tallene")
for linje in [
    f"Folketall per kvartal {AAR} for de 80 kommunene i Nordland, Troms og Finnmark.",
    f"Kilde: SSB tabell 01222 «Endringar i befolkninga i løpet av kvartalet», hentet {date.today():%d.%m.%Y}.",
    "1. januar er folketallet ved inngangen av 1. kvartal. De andre datoene er folketallet ved utgangen av hvert kvartal.",
    "Endring per kvartal = folketallet ved utgangen minus folketallet ved utgangen av kvartalet før (formler i arket).",
    "Fylkene og Nord-Norge er summen av kommunene (formler). Endring i prosent gjelder hittil i år.",
    "Nettoinnflytting omfatter både flytting innenlands og inn- og utvandring.",
    "Kvartalstallene er foreløpige og kan bli justert noe når SSB publiserer årstallene.",
    "Der SSB oppgir samisk eller kvensk navn først, står det norske navnet først og det andre i parentes.",
]:
    w3.append([linje])
w3.column_dimensions["A"].width = 120

UT.parent.mkdir(parents=True, exist_ok=True)
wb.save(UT)

# openpyxl lagrer formler uten utregnede verdier; forhåndsvisninger viser dem da som tomme celler.
# LibreOffice åpner filen, regner ut formlene og lagrer den igjen med både formler og verdier.
import shutil, subprocess, tempfile
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
if SOFFICE.exists():
    with tempfile.TemporaryDirectory() as tmp:
        inn = Path(tmp) / "inn" / UT.name; inn.parent.mkdir(); shutil.copy(UT, inn)
        subprocess.run([str(SOFFICE), "--headless", f"-env:UserInstallation=file:///{tmp}/profil".replace("\\", "/"),
                        "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", tmp, str(inn)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        shutil.copy(Path(tmp) / UT.name, UT)
    print("Formlene er regnet ut med LibreOffice")
else:
    print("ADVARSEL: LibreOffice ikke funnet; formlene regnes ut først når filen åpnes i Excel")
tot = lambda i: sum(x["slutt"][i] for x in rader)
print("Skrevet", UT, "| Nord-Norge:", sum(x["start"] for x in rader), [tot(i) for i in range(n_k)])
