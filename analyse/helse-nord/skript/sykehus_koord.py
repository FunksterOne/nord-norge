"""Bygger data/sykehus.json: somatiske sykehus/lokalisasjoner og distriktsmedisinske sentre (DMS) i Helse Nord,
med funksjonsnivå, akuttkirurgi, indremedisinsk akuttfunksjon, fødetilbud og kontrollerte koordinater.

Status (nivå, akutt, fødsel) er kuratert for hånd fra åpne kilder lest 2026-10-29 (se feltet «kilde»).
Rådata ligger i kilder/data/sykehus/ (hentet med skript/sykehus_hent.py og skript/sykehus_mfr.py).

Koordinater:
  1. OSM-objekt for selve sykehuset (amenity=hospital der det finnes), hentet med Nominatim /lookup.
  2. Kontroll mot Kartverkets offisielle adressepunkt (ws.geonorge.no/adresser) for besøksadressen.
  3. Kontroll av kommunenummer (api.kartverket.no/kommuneinfo/v1/punkt).
  4. Kontroll av avstand til tettstedet (api.kartverket.no/stedsnavn/v1/navn).
Uten OSM-sykehusobjekt brukes Kartverkets adressepunkt.
Kontrollrapport: kilder/data/sykehus/koord_kontroll.json"""
import json, math, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROT = Path(__file__).resolve().parents[1]
UT = ROT / "data" / "sykehus.json"
RÅ = ROT / "kilder" / "data" / "sykehus"
UA = "nord-norge-dashbord/1.0 (halvard@affectum.no)"
LEST = "lest 2026-10-29"

# Felles kilder
RUP = "https://www.helse-nord.no/regional-utviklingsplan-helse-nord/malomrader/samhandling-og-samarbeid/ (Helse Nord: regionsykehus, stort akuttsykehus, akuttsykehus, sykehus uten akuttfunksjoner; sist oppdatert 22.10.2026)"
MFR = "FHI Statistikk Open API, Medisinsk fødselsregister tabell Is1 (428) og P1b (491): https://statistikk-data.fhi.no/api/open/v1/mfr/Table/428"
HN2024 = ("Helse Nord RHF, ekstraordinært styremøte 9.1.2024, høringsutkast «Tiltak for å sikre bærekraft», s. 114 og alternativ 1: "
          "https://www.helse-nord.no/48d1ba/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2024/20240109/ekstraordinart-styremote-09012024---innkalling-og-saksdokumenter.pdf")
HN_MIDLER = "https://www.helse-nord.no/nyheter/2024/slik-fordeles-midlene-til-narvik-og-lofoten/ (Lofoten og Narvik beholder «akuttfunksjonene de har i dag»)"
BUDSJ27 = "Helse Nord RHF styresak 128-2026 Budsjett 2027 (beredskapstilskudd for å opprettholde akuttilbud i Lofoten og Narvik; lokal kopi kilder/hn-styresak-128-2026-...txt)"

L = [
    {"navn": "UNN Tromsø", "hf": "UNN", "sted": "Tromsø", "kommunenr": "5501", "niva": "regionsykehus",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "W25444602", "adresse": ("Hansine Hansens veg 67", "Tromsø"), "tettsted": "Tromsø",
     "kilde": [RUP, "https://www.unn.no/steder/unn-tromso/",
               "https://www.unn.no/avdelinger/medisinsk-klinikk-tromso/akuttmottak-og-observasjonspost/akuttmottaket-tromso/",
               "https://www.unn.no/avdelinger/kirurgisk-klinikk-tromso/kvinneklinikken/fodeavdelingen-tromso/", MFR],
     "merknad": "Regionsykehus og universitetssykehus for Nord-Norge (Breivika). Fødeavdelingen er kvinneklinikk (høyeste fødenivå), her kodet som fodeavdeling. MFR: 1 292 fødsler i 2025."},
    {"navn": "UNN Harstad", "hf": "UNN", "sted": "Harstad", "kommunenr": "5503", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "W103088720", "adresse": ("St Olavs gate 70", "Harstad"), "tettsted": "Harstad",
     "kilde": [RUP, "https://www.unn.no/steder/unn-harstad/ (generell kirurgi, indremedisin, akuttmottak, fødeavdeling)",
               "https://www.unn.no/avdelinger/klinikk-harstad/medisinsk-avdeling-harstad/akuttmottaket-harstad/ (ø-hjelp til alle fagområder)",
               "https://www.unn.no/avdelinger/klinikk-harstad/kirurgisk-avdeling-harstad/fode-og-gynekologi-harstad/", MFR],
     "merknad": "Lokalsykehus for Sør-Troms. MFR: 258 fødsler i 2025."},
    {"navn": "UNN Narvik", "hf": "UNN", "sted": "Narvik", "kommunenr": "1806", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "N12388471524", "adresse": ("Stasjonsveien 61", "Narvik"), "tettsted": "Narvik",
     "kilde": [RUP, "https://www.unn.no/steder/unn-narvik-furumoen/ (nytt sykehus på Furumoen tatt i bruk høsten 2024)",
               "https://www.unn.no/avdelinger/klinikk-narvik/akutt-og-operasjonsavdeling-narvik/ (akuttmottak, intensiv, ortopedisk/kirurgisk sengepost)",
               "https://www.unn.no/avdelinger/klinikk-narvik/kirurgisk-avdeling-narvik/Fode-og-gynekologi-Narvik/ (fødeavdeling, keisersnitt)",
               HN2024, HN_MIDLER, "Helse Nord RHF styresak 26-2026/3 (stortingssvar: akuttilbudet ved Narvik sykehus opprettholdes)", BUDSJ27, MFR],
     "merknad": "Koordinat for nytt sykehus på Furumoen (Stasjonsveien 61), ikke det gamle sykehuset i sentrum. Akuttkirurgi står ikke uttrykkelig på unn.no; status bygger på at Helse Nord i januar 2024 foreslo å avvikle akuttkirurgisk funksjon i Narvik, at forslaget ikke ble gjennomført, og at staten fortsatt finansierer videreført akuttilbud (budsjett 2027). MFR: 269 fødsler i 2025."},
    {"navn": "UNN Longyearbyen", "hf": "UNN", "sted": "Longyearbyen", "kommunenr": None, "niva": "uten_akutt",
     "akuttkirurgi": False, "akutt_indremedisin": None, "fodsel": "ingen",
     "osm": "W190025212", "adresse": None, "tettsted": "Longyearbyen",
     "kilde": ["https://www.unn.no/avdelinger/prehospital-klinikk/longyearbyen-sykehus/ (akuttmedisinsk beredskapssykehus; kirurgi kun livreddende stabilisering; ingen fødestue)",
               "https://www.unn.no/en/locations/our-hospital-in-longyearbyen-svalbard/"],
     "merknad": "Ligger på Svalbard, utenfor de 80 kommunene i Nord-Norge, og har ikke kommunenummer (Kartverkets kommuneinfo gir ingen treff). Akuttmedisinsk beredskapssykehus med døgnkontinuerlig vaktteam (lege, anestesi- og operasjonssykepleier) og seks senger; ikke akuttsykehus i Helse Nords definisjon, derfor uten_akutt. Akutt indremedisin satt til null fordi kategorien ikke passer. Kirurgi kun livreddende stabilisering før overføring til fastlandet."},
    {"navn": "DMS Midt-Troms (Finnsnes)", "hf": "UNN", "sted": "Finnsnes", "kommunenr": "5530", "niva": "dms",
     "akuttkirurgi": False, "akutt_indremedisin": False, "fodsel": "fodestue",
     "osm": None, "adresse": ("Helsesenterveien 32", "Finnsnes"), "tettsted": "Finnsnes",
     "kilde": ["https://www.unn.no/steder/distriktsmedisinsk-senter-midt-troms/ (UNN har ansvar for fødestua, røntgen, dialyse, geriatri, rehabilitering)",
               "https://www.unn.no/avdelinger/kirurgisk-klinikk-tromso/kvinneklinikken/fodestua-finnsnes/", MFR],
     "merknad": "Samarbeid mellom UNN og Senja kommune. Ingen OSM-sykehusobjekt; koordinat fra Kartverkets adressepunkt. MFR («Distriktsmedisinsk senter Midt-Troms»): 50 fødsler i 2025, og fødsler hver måned januar–juli 2026."},
    {"navn": "DMS Nord-Troms (Sonjatun, Storslett)", "hf": "UNN", "sted": "Storslett", "kommunenr": "5544", "niva": "dms",
     "akuttkirurgi": False, "akutt_indremedisin": False, "fodsel": "fodestue",
     "osm": "R12772694", "adresse": ("Sonjatunvegen 21", "Storslett"), "tettsted": "Storslett",
     "kilde": ["https://www.unn.no/steder/distriktsmedisinsk-senter-nord-troms/ (UNN har ansvar for fødestua, røntgen, dialyse, lysbehandling)",
               "https://www.unn.no/avdelinger/kirurgisk-klinikk-tromso/kvinneklinikken/fodestua-sonjatun/ (døgnkontinuerlig vaktberedskap)", MFR],
     "merknad": "Samarbeid mellom UNN og Nordreisa kommune. OSM-objektet er Sonjatun helsesenter (building=civic), ikke amenity=hospital. UNN-siden skriver «Sonjatunveien 21»; Kartverkets adresse er «Sonjatunvegen 21». Helse Nord foreslo i januar 2024 å gjøre fødestua om til svangerskaps- og barseltilbud, men MFR viser fødsler også i 2026 (24 fødsler i 2025). Siden oppgir også telefon til en sykestue; driftsform ikke kontrollert."},
    {"navn": "Nordlandssykehuset Bodø", "hf": "NLSH", "sted": "Bodø", "kommunenr": "1804", "niva": "stort_akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "W396742652", "adresse": ("Parkveien 95", "Bodø"), "tettsted": "Bodø",
     "kilde": [RUP, "https://www.nordlandssykehuset.no/avdelinger/kirurgisk-klinikk/kvinneklinikken/fodeavdeling-bodo/ (risikofødende fra hele Nordland)",
               "https://www.nordlandssykehuset.no/om-oss/om-nordlandssykehuset/", MFR],
     "merknad": "Eneste store akuttsykehus i Helse Nord. Koordinat for det somatiske sykehuset i sentrum (Parkveien 95); Rønvik er psykisk helsevern og er ikke med. Fødeavdelingen har kvinneklinikknivå, her kodet som fodeavdeling. MFR: 1 027 fødsler i 2025."},
    {"navn": "Nordlandssykehuset Vesterålen", "hf": "NLSH", "sted": "Stokmarknes", "kommunenr": "1866", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "W397959960", "adresse": ("Ivar Bergsmos gate 3", "Stokmarknes"), "tettsted": "Stokmarknes",
     "kilde": [RUP, "https://www.nordlandssykehuset.no/steder/vesteralen/",
               "https://www.nordlandssykehuset.no/avdelinger/kirurgisk-klinikk/kvinneklinikken/fodeavdeling-vesteralen/ (døgnberedskap gynekolog, akutte keisersnitt)",
               "https://www.nordlandssykehuset.no/avdelinger/medisinsk-klinikk/medisinsk-avdeling-vesteralen/ (intensivsenger, akutt slagenhet)",
               HN2024, MFR],
     "merknad": "Nytt lokalsykehus tatt i bruk 2014. Akuttkirurgi står ikke uttrykkelig på NLSH-sidene; belagt i Helse Nords dokument fra januar 2024 (akuttkirurgi fra Gravdal foreslått flyttet hit). Ingen ortopedisk vakt ifølge samme dokument. MFR: 275 fødsler i 2025."},
    {"navn": "Nordlandssykehuset Lofoten", "hf": "NLSH", "sted": "Gravdal", "kommunenr": "1860", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodestue",
     "osm": "N1380945804", "adresse": ("Sykehusbakken 23", "Gravdal"), "tettsted": "Gravdal",
     "kilde": [RUP, "https://www.nordlandssykehuset.no/steder/lofoten-gravdal/",
               "https://www.nordlandssykehuset.no/avdelinger/kirurgisk-klinikk/kvinneklinikken/fodestue-lofoten/ (jordmorstyrt fødestue)",
               "https://www.nordlandssykehuset.no/avdelinger/kirurgisk-klinikk/kirurgisk-sengeenhet-lofoten/",
               HN2024, HN_MIDLER, "Meld. St. 9 (2023–2024) s. 46–47 (akuttilbudet i Lofoten og Narvik skal ikke svekkes)", BUDSJ27, MFR],
     "merknad": "Akuttkirurgi står ikke uttrykkelig på NLSH-sidene; status bygger på at Helse Nord i januar 2024 foreslo å avvikle akuttkirurgisk funksjon her, at forslaget ikke ble gjennomført, og at staten fortsatt finansierer videreført akuttilbud (budsjett 2027). Fødetilbudet var i 2024 en forsterket fødestue med keisersnittberedskap (HN 2024); NLSH omtaler det i dag som jordmorstyrt fødestue, og om keisersnittberedskapen består, er ikke bekreftet. MFR: 41 fødsler i 2025."},
    {"navn": "Helgelandssykehuset Mo i Rana", "hf": "HSYK", "sted": "Mo i Rana", "kommunenr": "1833", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "W401423370", "adresse": ("Sjøforsgata 36", "Mo i Rana"), "tettsted": "Mo i Rana",
     "kilde": [RUP, "https://www.helgelandssykehuset.no/steder/helgelandssykehuset-mo-i-rana/ (kirurgi, ortopedi for hele Helgeland, intensiv, kvinne- og fødepost)",
               "https://www.helgelandssykehuset.no/nyheter/slik-forbereder-akuttsykehusene-seg/ (Mo i Rana og Sandnessjøen begge akuttsykehus)",
               "https://www.helgelandssykehuset.no/avdelinger/kirurgisk-klinikk/kvinne-og-fodepost-mo-i-rana/ (planlagte og akutte keisersnitt)",
               "https://www.helgelandssykehuset.no/nyheter/endringer-i-fodetilbudet---sporsmal-og-svar/ (to fullverdige fødeavdelinger)", MFR],
     "merknad": "Ett av to akuttsykehus i Helgelandssykehuset etter 1.10.2025. Fødeavdelingene i Mo i Rana og Sandnessjøen har alternerende sommerstenging. MFR: 251 fødsler i 2025."},
    {"navn": "Helgelandssykehuset Sandnessjøen", "hf": "HSYK", "sted": "Sandnessjøen", "kommunenr": "1820", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "N3412237053", "adresse": ("Prestmarkveien 1", "Sandnessjøen"), "tettsted": "Sandnessjøen",
     "kilde": [RUP, "https://www.helgelandssykehuset.no/steder/helgelandssykehuset-sandnessjoen/ (akuttkirurgisk, unntatt ortopedi, også for Grane, Hattfjelldal og Vefsn)",
               "https://www.helgelandssykehuset.no/nyheter/slik-forbereder-akuttsykehusene-seg/",
               "https://www.helgelandssykehuset.no/avdelinger/kirurgisk-klinikk/kvinne-og-fodepost-sandnessjoen/",
               "https://www.helgelandssykehuset.no/nyheter/endringer-i-fodetilbudet---sporsmal-og-svar/", MFR],
     "merknad": "Ett av to akuttsykehus i Helgelandssykehuset; tar imot fødende fra Sør-Helgeland mens fødestua i Brønnøysund er stengt. Akutt ortopedi går til Mo i Rana. MFR: 284 fødsler i 2025."},
    {"navn": "Helgelandssykehuset Mosjøen", "hf": "HSYK", "sted": "Mosjøen", "kommunenr": "1824", "niva": "uten_akutt",
     "akuttkirurgi": False, "akutt_indremedisin": False, "fodsel": "ingen",
     "osm": "W597009281", "adresse": ("Vefsnvegen 25", "Mosjøen"), "tettsted": "Mosjøen",
     "kilde": ["https://www.helgelandssykehuset.no/nyheter/slik-blir-sykehusets-tilbud-i-mosjoen (publisert 5.9.2025: fra 1. oktober ivaretas alle akutt- og døgnfunksjoner i Mo i Rana og Sandnessjøen)",
               RUP, "Helse Nord RHF styresak 136-2026/13 (stortingssvar: akutt- og døgnfunksjonene i Mosjøen lagt ned 1.10.2025)",
               HN2024 + " (Mosjøen har siden 2006 bare hatt akutt indremedisin, ikke akuttkirurgi)", MFR],
     "merknad": "Kontrollert: akutt- og døgnfunksjonene i somatikk ble flyttet ut 1.10.2025. Tilbyr fortsatt bl.a. skadepoliklinikk, dagkirurgi, indremedisinsk poliklinikk med øyeblikkelig hjelp-funksjoner, døgnbasert slagalarm og fødepoliklinikk. HSYKs stedsside for Mosjøen omtaler fortsatt «lokalsykehus» og «operasjon», og er trolig ikke oppdatert. Ingen registrerte fødsler i MFR 2018–2025."},
    {"navn": "DMS Sør-Helgeland (Brønnøysund)", "hf": "HSYK", "sted": "Brønnøysund", "kommunenr": "1813", "niva": "dms",
     "akuttkirurgi": False, "akutt_indremedisin": False, "fodsel": "ingen",
     "osm": None, "adresse": ("Skules vei 13", "Brønnøysund"), "tettsted": "Brønnøysund",
     "kilde": ["https://www.helgelandssykehuset.no/steder/dms-sor-helgeland/",
               "https://www.helgelandssykehuset.no/avdelinger/kirurgisk-klinikk/fode-og-barselstue-bronnoysund/ (alle gravide på Sør-Helgeland henvises til Sandnessjøen for fødsel)",
               "https://www.helgelandssykehuset.no/nyheter/endringer-i-fodetilbudet---sporsmal-og-svar/ (midlertidig stengt uten bestemt sluttdato)",
               "Helse Nord RHF styresak 119-2026/5 og 75-2026/7 (stortingssvar: fødestua stengt for fødsler fra 20.3.2026)", MFR],
     "merknad": "Formelt jordmorstyrt fødestue, men stengt for fødsler fra 20.3.2026 uten bestemt sluttdato; derfor kodet som ingen. Jordmor i beredskap 24/7 for undersøkelse og følgetjeneste. MFR: 26 fødsler i 2025. Foreløpige månedstall (P1b, t.o.m. juli 2026) viser én fødsel i mars og én i april 2026, øvrige måneder uten tall («manglende data»); HSYK oppgir fem fødsler i stengt fødestue per høsten 2026. Laboratorium, røntgen, slagalarm, dialyse og poliklinikker. Ingen OSM-sykehusobjekt; koordinat fra Kartverkets adressepunkt."},
    {"navn": "Hammerfest sykehus", "hf": "FIN", "sted": "Hammerfest", "kommunenr": "5603", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "R13504208", "adresse": ("Kransvikveien 35", "Hammerfest"), "tettsted": "Hammerfest",
     "kilde": [RUP, "https://www.finnmarkssykehuset.no/steder/hammerfest-sykehus/ (akuttfunksjon; akuttmedisin, kirurgi, ortopedi, indremedisin, gynekologi/føde)",
               "https://www.finnmarkssykehuset.no/nyheter/innflytting-i-nytt-sykehus/ (innflytting i nye Hammerfest sykehus 2.–4.1.2025)",
               "https://www.finnmarkssykehuset.no/avdelinger/hammerfest-sykehus/gynekologi-og-fode/foden-hammerfest/ (døgnkontinuerlig beredskap for akutte keisersnitt)",
               "Finnmarkssykehuset strategisk utviklingsplan 2023–2038, s. 30 (full akuttmedisinsk funksjon med intensiv; lokal kopi kilder/hf-planer/)", MFR],
     "merknad": "Koordinat for nytt sykehus på Fuglenes (Kransvikveien 35), tatt i bruk januar 2025; det gamle lå i Sykehusveien 35. Fødeavdelingen på FIN-siden har fortsatt gammel adresse (Sykehusveien 35). MFR: 391 fødsler i 2025."},
    {"navn": "Kirkenes sykehus", "hf": "FIN", "sted": "Kirkenes", "kommunenr": "5605", "niva": "akutt",
     "akuttkirurgi": True, "akutt_indremedisin": True, "fodsel": "fodeavdeling",
     "osm": "R13497453", "adresse": ("Skytterhusveien 2", "Kirkenes"), "tettsted": "Kirkenes",
     "kilde": [RUP, "https://www.finnmarkssykehuset.no/steder/kirkenes-sykehus/ (akuttfunksjon, nytt i 2018)",
               "https://www.finnmarkssykehuset.no/nyheter/innflytting-i-nytt-sykehus/ (Kirkenes tok ø-hjelp innen medisin, kirurgi og ortopedi under flyttingen i Hammerfest)",
               "https://www.finnmarkssykehuset.no/avdelinger/kirkenes-sykehus/fode-gyn-kirkenes/ (planlagte og akutte keisersnitt)",
               BUDSJ27 + " (tilskudd til beredskap og akuttjenester ved Kirkenes sykehus)", MFR],
     "merknad": "Lokalsykehus for Øst-Finnmark ved Andrevann. MFR: 164 fødsler i 2025."},
    {"navn": "Klinikk Alta", "hf": "FIN", "sted": "Alta", "kommunenr": "5601", "niva": "dms",
     "akuttkirurgi": False, "akutt_indremedisin": False, "fodsel": "fodestue",
     "osm": "R11058191", "adresse": ("Markveien 31", "Alta"), "tettsted": "Alta",
     "kilde": ["https://www.finnmarkssykehuset.no/avdelinger/klinikk-alta/",
               "https://www.finnmarkssykehuset.no/avdelinger/klinikk-alta/somatisk-dognenhet/fodestue-alta/ (fødestue i Alta, fødeavdeling i Hammerfest og Kirkenes)",
               "Finnmarkssykehuset strategisk utviklingsplan 2023–2038, s. 30 (slagalarm med 24/7 akuttvakt ved Klinikk Alta)",
               "Helse Nord RHF styresak 56-2026/7 og 94-2026/4 (stortingssvar: fødestue i Alta, 70 barn i 2025)", MFR],
     "merknad": "Ikke akuttsykehus. Spesialistklinikk med somatisk døgnenhet, poliklinikker, slagalarm og fødestue; kodet som dms fordi skjemaet mangler egen kategori. Ikke regnet som indremedisinsk akuttfunksjon, selv om klinikken har slagalarm med 24/7 akuttvakt. Planlagt sommerflytting av fødsler til Hammerfest i 2026 ble omgjort (pressemelding 20.2.2026). MFR: 70 fødsler i 2025."},
]


def hent(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for forsøk in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (forsøk + 1))
        except Exception:
            time.sleep(3 * (forsøk + 1))
    raise RuntimeError(url)


def avstand(a, b):
    (la1, lo1), (la2, lo2) = a, b
    r = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def osm_oppslag(ids):
    url = "https://nominatim.openstreetmap.org/lookup?" + urllib.parse.urlencode(
        {"osm_ids": ",".join(ids), "format": "jsonv2", "extratags": 1})
    d = hent(url)
    time.sleep(1.1)
    ut = {}
    for x in d:
        ut[x["osm_type"][0].upper() + str(x["osm_id"])] = x
    return ut


def adresse(gate, sted):
    d = hent("https://ws.geonorge.no/adresser/v1/sok?" + urllib.parse.urlencode(
        {"sok": gate, "poststed": sted, "treffPerSide": 5, "utkoordsys": 4258}))
    for a in (d or {}).get("adresser", []):
        if a["adressetekst"].lower().replace(".", "") == gate.lower().replace(".", ""):
            p = a["representasjonspunkt"]
            return {"tekst": f"{a['adressetekst']}, {a['postnummer']} {a['poststed']}", "kommunenr": a["kommunenummer"],
                    "lat": p["lat"], "lon": p["lon"]}
    return None


def kommune(lat, lon):
    d = hent(f"https://api.kartverket.no/kommuneinfo/v1/punkt?nord={lat}&ost={lon}&koordsys=4258")
    return (d["kommunenummer"], d["kommunenavn"]) if d else (None, None)


def tettsted(navn, knr):
    d = hent("https://api.kartverket.no/stedsnavn/v1/navn?" + urllib.parse.urlencode(
        {"sok": navn, "fuzzy": "false", "utkoordsys": 4258, "treffPerSide": 50}))
    typer = ("By", "Tettsted", "Tettbebyggelse", "Bydel", "Tettstedsdel")
    kandidater = [n for n in (d or {}).get("navn", []) if n.get("navneobjekttype") in typer
                  and (knr is None or any(k.get("kommunenummer") == knr for k in n.get("kommuner", [])))]
    if not kandidater:
        kandidater = [n for n in (d or {}).get("navn", []) if n.get("navneobjekttype") in typer]
    if not kandidater:
        return None
    n = kandidater[0]
    p = n["representasjonspunkt"]
    return {"type": n["navneobjekttype"], "lat": p["nord"], "lon": p["øst"]}


def main():
    osm = osm_oppslag([x["osm"] for x in L if x["osm"]])
    rapport, ut = [], []
    for x in L:
        k = {"navn": x["navn"]}
        o = osm.get(x["osm"]) if x["osm"] else None
        a = adresse(*x["adresse"]) if x["adresse"] else None
        if x["osm"] and not o:
            k["avvik_osm"] = f"OSM-objekt {x['osm']} ikke funnet"
        if o:
            lat, lon = float(o["lat"]), float(o["lon"])
            navn_osm = o.get("name") or o.get("display_name", "").split(",")[0]
            ktekst = f"OSM {x['osm']} {o['category']}={o['type']} «{navn_osm}» via Nominatim /lookup"
        elif a:
            lat, lon = a["lat"], a["lon"]
            ktekst = f"Kartverket adresseregister (ws.geonorge.no/adresser): {a['tekst']}"
        else:
            raise RuntimeError(x["navn"])
        k["osm"] = x["osm"]; k["valgt"] = [round(lat, 5), round(lon, 5)]
        if a:
            k["adresse"] = a["tekst"]
            k["avstand_til_adressepunkt_m"] = round(avstand((lat, lon), (a["lat"], a["lon"])))
            if o:
                ktekst += f"; kontrollert mot Kartverkets adressepunkt {a['tekst']} ({k['avstand_til_adressepunkt_m']} m)"
            if k["avstand_til_adressepunkt_m"] > 300:
                k["avvik_adresse"] = "over 300 m fra adressepunkt"
        knr, knavn = kommune(lat, lon)
        k["kommune_punkt"] = [knr, knavn]
        if knr != x["kommunenr"]:
            k["avvik_kommune"] = f"forventet {x['kommunenr']}, punktet ligger i {knr} {knavn}"
        t = tettsted(x["tettsted"], x["kommunenr"])
        if t:
            k["tettsted"] = f"{x['tettsted']} ({t['type']})"
            k["avstand_til_tettsted_m"] = round(avstand((lat, lon), (t["lat"], t["lon"])))
            ktekst += f"; {str(round(k['avstand_til_tettsted_m'] / 1000, 1)).replace('.', ',')} km fra stedsnavnpunktet {x['tettsted']} (Kartverket stedsnavn, {t['type']})"
            if k["avstand_til_tettsted_m"] > 6000:
                k["avvik_tettsted"] = "over 6 km fra tettstedets stedsnavnpunkt"
        ktekst += f"; kommune kontrollert med Kartverket kommuneinfo: {knr or 'ingen treff'}{' ' + knavn if knavn else ''}"
        rapport.append(k)
        merknad = x["merknad"]
        avvik = [v for kk, v in k.items() if kk.startswith("avvik")]
        if avvik:
            merknad += " KOORDINATAVVIK: " + "; ".join(avvik) + "."
        ut.append({"navn": x["navn"], "hf": x["hf"], "sted": x["sted"], "kommunenr": x["kommunenr"], "niva": x["niva"],
                   "akuttkirurgi": x["akuttkirurgi"], "akutt_indremedisin": x["akutt_indremedisin"], "fodsel": x["fodsel"],
                   "lat": round(lat, 5), "lon": round(lon, 5), "koord_kilde": ktekst,
                   "kilde": "; ".join(x["kilde"]) + f" ({LEST})", "merknad": merknad})
        print(f"{x['navn']:40} {lat:.5f},{lon:.5f} knr {knr} (forv. {x['kommunenr']}) "
              f"adr {k.get('avstand_til_adressepunkt_m', '-')} m, tettsted {k.get('avstand_til_tettsted_m', '-')} m "
              + (" AVVIK: " + "; ".join(avvik) if avvik else ""))
        time.sleep(0.3)
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
    RÅ.mkdir(parents=True, exist_ok=True)
    (RÅ / "koord_kontroll.json").write_text(json.dumps({"kjort": time.strftime("%Y-%m-%d %H:%M"), "rader": rapport},
                                                       ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nSkrev {len(ut)} lokalisasjoner til {UT}")


if __name__ == "__main__":
    main()
