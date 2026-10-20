# Bofasthet for flyktninger og innvandrere i Nord-Norge

Kildekartlegging og tall, hentet 20. oktober 2026. Strukturerte tall ligger i `statistikk.json` (8 316 poster), rådata i `kilder/` (holdes utenfor git) og skriptene i `skript/`.

## Konklusjon

Direkte mål på bofasthet (andel som fortsatt bor i bosettingskommunen) finnes per fylke bare fem år etter bosetting, men da for 16 bosettingskull fra 1998 til 2019. Lengre perioder finnes direkte bare for landet (opptil 14 år) og for Nord-Norge samlet (ti år, Fafo 2025). For 10, 15 og 20 år per fylke må bofastheten beregnes indirekte fra SSB-tabell 10598 (innvandrere etter fylke, landbakgrunn og ettårig botid, 2005–2026). Det gir netto bevaring i området, ikke andel i første kommune.

Hovedbildet er entydig: Nord-Norge beholder flyktninger klart dårligere enn landet, og forskjellen vokser med botiden. Etter fem år bor 58–90 % av flyktningene i Nordland, Troms og Finnmark fortsatt i bosettingskommunen (kullene 2007–2019), mot 77–86 % i landet. Etter ti år bor om lag 30 % fortsatt i bosettingskommunen i Nord-Norge. Etter 20 år er netto bevaring i landsdelen for innvandrere fra typiske flyktningland om lag 19 %, mot 84 % i Norge samlet. Arbeidsinnvandrere fra Polen og Litauen blir boende langt oftere (netto 52–60 % etter 10–20 år), og innvandrere fra Filippinene og Thailand, som i hovedsak er familieinnvandrere, blir nesten alle boende (86–91 %).

## Hovedtall for Nord-Norge

**Funn 01 — Femårsbofastheten har økt kraftig, men ligger fortsatt under landet.** Observasjon: Andelen flyktninger som bodde i bosettingskommunen fem år etter bosetting, steg i Nordland fra 21 % (kull 1998) til 82 % (kull 2019), i Troms fra 26 % til 81 % og i Finnmark fra 9 % til 90 %. Landet steg fra 53 % til 86 %. Nord-Norge-fylkene har aldri vært over landsnivået, unntatt Finnmark for kull 2019. Grunnlag: SSBs monitor for sekundærflytting, 11 utgaver 2005–2020, og SSB-artikler fra 2021 og 2024 (tabell A).

**Funn 02 — Etter ti år har sju av ti flyttet fra bosettingskommunen i Nord-Norge.** Observasjon: «Nært 70 prosent» av flyktningene som ble bosatt i nordnorske kommuner, har flyttet fra bosettingskommunen ti år etter bosetting. Trøndelag, som har nest mest fraflytting, ligger «rett under 50 prosent». Til sammenligning har 47 % av hele landets 2010-kull forlatt bosettingskommunen etter ti år. Grunnlag: Fafo-rapport 2025:14, s. 34 (PDF-side 36), og SSB 28.11.2024, figur 2.

**Funn 03 — Landsdelen beholder under halvparten netto.** Observasjon: Av 8 367 flyktninger som fikk første bostedskommune i Nord-Norge i 2010–2016, tilsvarte antallet fra de samme kullene som bodde i landsdelen 1.1.2023, 3 746 personer (44,8 %). Tilsvarende tall for Trøndelag var 72,3 %, for Vestlandet 81,0 % og for Østlandet 132,2 %. Grunnlag: Fafo-rapport 2025:14, tabell 3, s. 44 (PDF-side 46). Tallet er netto, fordi tilflyttere fra andre landsdeler inngår i telleren.

**Funn 04 — Netto bevaring av innvandrere fra flyktningland faller til om lag en femdel etter 20 år.** Observasjon: Av innvandrere fra ti typiske flyktningland som var bosatt i Nord-Norge med ett års botid, var antallet med tilsvarende botid i landsdelen 65 % etter 5 år, 39 % etter 10 år, 30 % etter 15 år og 19 % etter 20 år. I landet var tallene 96, 91, 86 og 84 %. Gjennomsnitt veid over innvandringskullene 2003–2020 (5 år), 2003–2015 (10 år), 2003–2010 (15 år) og 2003–2005 (20 år). Grunnlag: SSB 10598, egen beregning (tabell C).

**Funn 05 — Arbeids- og familieinnvandrere blir boende langt oftere.** Observasjon: For innvandrere fra Polen og Litauen var netto bevaring i Nord-Norge 78 % etter 5 år, 60 % etter 10 år, 57 % etter 15 år og 52 % etter 20 år. Det er 70–93 % av landsnivået. Innvandrere fra Filippinene og Thailand lå på 86–91 % i hele perioden, høyere enn landet. Kunnskapsbanken for Nord-Norge finner det samme: 20 378 av 29 180 arbeidsinnvandrere fra Schengen-land utenom Norden som har kommet siden 2000, bor fortsatt i landsdelen (70 %).

**Funn 06 — Innvandrere i Nord-Norge har kortere botid enn i landet.** Observasjon: 1.1.2021 hadde 37,5 % av innvandrerne i Nord-Norge ti års botid eller mer, mot 52,3 % i landet (1.1.2026: 41,2 mot 57,9 %). Av de 4 616 flyktningene med minst fem års botid som bodde i Nordland 1.1.2023, bodde 70,0 % i sin første bosettingskommune. Nasjonalt gjaldt det 51,5 %. Det betyr at landsdelen får få tilflyttere med lang botid. Grunnlag: IMDi (kilde SSB), egen beregning.

**Funn 07 — Dashbordets 2019-tall avviker litt fra kilden.** Observasjon: `KOHORT_RET` i `assets/data.js` oppgir 80 % for Nordland og 80 % for Troms (kull 2019, fem år). Kilden (SSB 28.11.2024, figur 3) oppgir 82 % og 81 %. Finnmark (90 %), landet (86 %) og hele 2015-kullet stemmer. Rettet 20. oktober 2026; dashbordet bruker nå `BOFAST_DATA` fra `fetch_bofasthet.py`.

## Kildeoversikt

| Kilde / tabell | Innhold | Periode | Nivå | Tilgang | Egnethet |
|---|---|---|---|---|---|
| SSB, Monitor for sekundærflytting (Notat 2005/13, 2006/31, 2007/35, 2008/43, 2009/50; Rapporter 2010/41, 2011/30, 2013, 2014, 2017/18, 2020/36) | Bosted fem år etter bosetting per fylke og kull: første kommune, annen kommune i fylket, annet fylke, Oslo, utvandret. Kumulativ utflytting etter botid for landet. Utvalgte kommuner. | Bosettingskull 1994–2016 | Landet, fylke (gammel inndeling), utvalgte kommuner | Åpne PDF-er (`kilder/pdf/`) | Høy. Eneste direkte mål på bofasthet per fylke, men bare for fem år. |
| SSB-artikler i monitorserien: «Mer bofaste flyktninger» (2021), «Høy bofasthet blant flyktninger de første årene» (28.11.2024), «Høy innflytting til mange sentrale kommuner» (16.12.2025) | Kull 2015 og 2019 per fylke etter fem år. Landet etter botid 1–14 år for kullene 2010–2022. Landbakgrunn. | Kull 2003–2023, fulgt til 1.1.2024 | Landet, fylke (2020- og 2024-inndeling), utvalgte kommuner | Figurdata ligger i sidens HTML (`kilder/web/*.figurer.json`). Fullt tallgrunnlag på forespørsel til forfatterne. | Høy. Gir de lengste nasjonale seriene (14 år). |
| Fafo-rapport 2025:14, «Flytting etter bosetting» (Kjeøy mfl.) | Fraflytting etter landsdel, sentralitet og kommunestørrelse, 1–13 år etter bosetting. Bosted 1.1.2023 for kullene 2010–2016. | Kull 2010–2023 | Landet, landsdel, sentralitetsklasse | Åpen PDF | Høy for Nord-Norge samlet (ti år). Kurvene er bare figurer, uten tabellverdier. |
| SSB 10598 | Innvandrere etter fylke, landbakgrunn (enkeltland) og ettårig botid (0–40+) | 2005–2026 | Fylke: 19/20 til 2019, 54 i 2020–2023, 55/56 fra 2024 | PxWebApi, åpen | Middels til høy. Gir indirekte netto bevaring i 5–21 år (pseudokohorter). Nord-Norge og «Troms og Finnmark» er sammenhengende i hele perioden. Troms og Finnmark hver for seg dekker bare 2005–2019 og 2024–2026. |
| SSB 08377 (og 05648) | Personer med flyktningbakgrunn etter botid (0–4, 5–9, 10–19, 20+) og verdensregion | 1998–2026 | Bare landet | PxWebApi | Lav for regionale formål |
| SSB 03810 | Personer med flyktningbakgrunn etter fylke og statsborgerskap | 1998–2026 | Fylke | PxWebApi | Kontekst (bestand), uten botid |
| SSB 06318, 07113, 08348, 14659 | Innvandringer etter innvandringsgrunn og om personen fortsatt er bosatt (06318), etter innflyttingsår (07113) | 1990–2025 | Bare landet | PxWebApi | Gir bosatt-i-Norge-andel etter innvandringsgrunn, ikke regionalt |
| SSB 10824 | Tidligere introdeltakere ett til fem år etter avsluttet program: antall etter nåværende bosted og etter bosted ved programdeltakelse | 2011–2024 | Kommune, fylke | PxWebApi | Middels. Indirekte netto bevaring omtrent 7–8 år etter bosetting. Mange tomme celler for små kommuner. |
| SSB 07210 | Innenlandsk nettoinnflytting etter innvandringskategori | 2008–2025 | Kommune | PxWebApi | Middels. Viser flyttestrøm, ikke kull |
| SSB 09817, 07110, 12816 | Bestand etter landbakgrunn per kommune (09817, 07110). Botid i tre grupper for 20–66 år (12816, bare landet). | 2010–2026 | Kommune / landet | PxWebApi | Kontekst |
| IMDi «Sekundærflytting blant flyktninger» (`flyktning_botid_flytting`) | Flyktninger etter botid (0–4, 5+) og om nåværende kommune er første bosettingskommune | 2014–2023 (2014–2015 med mange uoppgitte) | Kommune, fylke, næringsregion | Åpent JSON-API bak imdi.no/statistikk | Middels. Bestandsmål (sammensetning), ikke bofasthet |
| IMDi «Innvandrernes botid» (`befolkning_botid`) | Innvandrere etter botid (0–4, 5–9, 10+) og to verdensregioner | 2014–2026 | Kommune (2024-koder fra 2020), fylke | Samme API | Middels. Femårs pseudokohort per kommune. Små tall er avrundet. |
| IMDi «Innvandringsgrunn» (`befolkning_innvandringsgrunn`) | Innvandrere etter innvandringsgrunn og kjønn | 2006–2025 | Kommune, fylke | Samme API (lastet ned, ikke analysert) | Lav. Mangler botid |
| Kunnskapsbanken for Nord-Norge (2025), «Innvandrerne forlater Nord-Norge» | Netto innvandring og innenlands flytting etter landgruppe, 2000–2024 | 2000–2024 | Landsdel, fylke | Åpen nettartikkel | Sekundærkilde. Bygger på flyttestrømmer, ikke personer. |
| SSB Rapporter 2019/13 (Tønnessen og Andersen) | Bosettingskommune og integreringsutfall | — | — | Åpen PDF | Ikke relevant for bofasthet |

Søk i Statistikkbanken (PxWebApi v0 og v2) på «bosettingsår», «bofasthet», «sekundærflytting», «bosettingskommune», «busetjing» og «flyttemønster» ga ingen treff. Monitortallene finnes ikke som Statistikkbank-tabell.

## Tallene i detalj

### A. Bosatt i bosettingskommunen og -fylket fem år etter bosetting, per kull

Prosent av hele bosettingskullet. Utvandrede og døde inngår i nevneren. Målt 1.1. fem år etter bosettingsåret. Fylke = første kommune pluss annen kommune i samme fylke.

| Kull | Landet, kommune | Nordland, kommune / fylke | Troms, kommune / fylke | Finnmark, kommune / fylke | Kilde (PDF-side) |
|---|---|---|---|---|---|
| 1998 | 53 | 21 / 22 | 26 / 29 | 9 / 15 | Monitor 2005, tab. 3 (22) |
| 2000 | 53 | 32 / 35 | 27 / 31 | 24 / 26 | Monitor 2006, tab. 5 (25) |
| 2001 | 60 | 39 / 43 | 34 / 37 | 33 / 36 | Monitor 2007, tab. 13 (33) |
| 2002 | 65 | 37 / 40 | 37 / 38 | 42 / 46 | Monitor 2008, tab. 9 (23) |
| 2003 | 69 | 49 / 54 | 52 / 56 | 25 / 28 | Monitor 2009, tab. 10 (23) |
| 2004 | 70 | 49 / 54 | 52 / 56 | 54 / 57 | Monitor 2010, tab. 4.3 (21) |
| 2005 | 73 | 45 / 47 | 47 / 50 | 71 / 74 | Monitor 2011, tab. 4.3 (22) |
| 2006 | 76 | 52 / 54 | 60 / 64 | 58 / 59 | Monitor 2013, tab. 4.3 (24) |
| 2007 | 77 | 66 / 69 | 61 / 63 | 72 / 75 | Monitor 2014, tab. 4.3 (23) |
| 2008 | 78 | 69 / 70 | 65 / 66 | 70 / 74 | Monitor 2014, tab. 4.5 (28) |
| 2009 | 78 | 61 / 66 | 71 / 75 | 74 / 77 | Monitor 2017, tab. 4.6 (36) |
| 2010 | 78 | 60 / 65 | 69 / 72 | 71 / 76 | Monitor 2017, tab. 4.7 (37) |
| 2011 | 80 | 76 / 80 | 69 / 74 | 58 / 61 | Monitor 2020, tab. 4.3 (33) |
| 2012 | 81 | 69 / 73 | 74 / 78 | 72 / 74 | Monitor 2020, tab. 4.5 (37) |
| 2015 | 82 | 65 / 74 | Troms og Finnmark: 68 / 73 | (samlet) | SSB 2021, fig. 4 |
| 2019 | 86 | 82 / 84 | 81 / 83 | 90 / over 90 | SSB 2024, fig. 3 |

Merknader: Kull 1999 finnes bare med basis «fortsatt bosatt i Norge» (Nordland 27, Troms 39, Finnmark 35, landet 59; Monitor 2009, tab. 11). Det samme gjelder 1997 (35 / 12 / 21 / 67). Kullene 2013, 2014 og 2016–2018 er ikke publisert per fylke. For kull 2019 viser figuren ingen verdi for Finnmarks «annen kommune i fylket», og utvandringsandelen i Finnmark er 4 %. Tabell 4.7 i 2020-rapporten blander to grunnlag: kullene 2000–2008 er regnet av dem som fortsatt bodde i Norge, kullene 2009–2012 av hele kullet. Begge seriene ligger i `statistikk.json` med feltet `basis`.

Hvor flytterne fra Nord-Norge drar (prosent av kullet, fem år): Annet fylke utenom Oslo er hovedretningen i alle kull. For Nordland var andelen 50 % i kull 1998, 12–24 % i kull 2008–2015 og 13 % i kull 2019. Til Oslo dro 2–23 %. For kull 2011 flyttet 49 % av flytterne fra Nordland, 45 % fra Troms og 73 % fra Finnmark til et annet fylke utenom Oslo (Monitor 2020, tab. 4.4). Blant alle som flyttet fra Nord-Norge i 2010–2023, flyttet 64 % til Østlandet (Fafo 2025:14, s. 40, PDF-side 42).

### B. Lengre botid for landet

Andel som fortsatt bor i bosettingskommunen, i prosent av kullet. Utvandrede regnes som flyttet.

| Kull | 5 år | 8 år | 10 år | 12 år | 14 år | Kilde |
|---|---|---|---|---|---|---|
| 2003 | 69 | 55 | 48 | — | — | SSB 2021, fig. 2 |
| 2005 | 73 | 60 | 54 | — | — | SSB 2021, fig. 2 |
| 2007 | 77 | 64 | 57 | — | — | Monitor 2020, tab. 3.1 |
| 2010 | 78 | 60 | 53 | 47 | 43 | SSB 28.11.2024, fig. 2 |
| 2012 | 82 | 64 | 56 | 50 | — | SSB 28.11.2024, fig. 2 |
| 2014 | 81 | 61 | 53 | — | — | SSB 28.11.2024, fig. 2 |
| 2016 | 81 | 61 | — | — | — | SSB 28.11.2024, fig. 2 |

Desemberartikkelen fra 2025 (figur 1) gir 1–4 prosentpoeng høyere andeler for de samme kullene. 2010-kullet ligger der på 47 % etter 14 år. Den måler trolig bare innenlands flytting. Av alle som ble bosatt i 2010–2019, bodde 59 % i bosettingskommunen 1.1.2024, etter 5–14 års botid.

Bofasthet etter fem år og kommunestørrelse, landet (Monitor 2020, tab. 4.10, kull 2007–2012): Kommuner med 100 000 innbyggere eller flere ligger på 89–92 %. Kommuner med 2 000–4 999 innbyggere ligger på 59–73 %, og kommuner under 2 000 innbyggere på 48–73 %. Etter ti år har «nesten 80 prosent» av dem som ble bosatt i sentralitetsklasse 6 flyttet (Fafo 2025:14, s. 33).

### C. Netto bevaring i Nord-Norge etter 5, 10, 15 og 20 år (pseudokohorter, SSB 10598)

Metode: Antall innvandrere i området med botid k år, delt på antallet i samme område med ett års botid k − 1 år tidligere. Tallet er veid over alle tilgjengelige innvandringskull. Spennet mellom kullene står i parentes.

| Gruppe | Område | 5 år | 10 år | 15 år | 20 år |
|---|---|---|---|---|---|
| Ti flyktningland¹ | Landet | 96 | 91 | 86 | 84 |
| | Nord-Norge | 65 (43–76) | 39 (26–49) | 30 (19–38) | 19 (16–22) |
| | Nordland | 64 | 37 | 26 | 18 |
| | Troms og Finnmark | 65 | 42 | 35 | 20 |
| Alle innvandrere | Landet | 80 | 71 | 69 | 73 |
| | Nord-Norge | 70 (58–76) | 51 (45–58) | 46 (39–49) | 38 (34–40) |
| | Nordland | 70 | 51 | 45 | 36 |
| | Troms og Finnmark | 69 | 52 | 48 | 38 |
| Polen og Litauen | Landet | 84 | 71 | 69 | 74 |
| | Nord-Norge | 78 | 60 | 57 | 52² |
| Sverige | Landet | 65 | 52 | 49 | 54 |
| | Nord-Norge | 63 | 49 | 46 | 50² |
| Russland | Landet | 85 | 82 | 83 | 85 |
| | Nord-Norge | 64 | 50 | 41 | 36 |
| Filippinene og Thailand | Landet | 73 | 72 | 75 | 83 |
| | Nord-Norge | 91 | 89 | 89 | 86 |

Kullene som inngår: 5 år 2003–2020, 10 år 2003–2015, 15 år 2003–2010, 20 år 2003–2005. ¹ Syria, Eritrea, Somalia, Afghanistan, Irak, Iran, Sudan, Etiopia, Myanmar og Kongo. ² Under 300 personer i nevneren.

Tolkning og forbehold:
- Tallene er netto. Utvandring, død og utflytting trekker ned. Innflytting fra andre fylker av personer med samme botid trekker opp.
- For landet måler tallet bare utvandring og død. Forholdet mellom område og landet (`netto_bevaring_relativ_landet` i JSON) er derfor et rimelig mål på netto innenlands bevaring. For flyktningland gir det 68, 43, 35 og 23 % for Nord-Norge.
- Hypotese: Flyktninger som får oppholdstillatelse i et mottak i Nord-Norge, registreres der før de bosettes i en annen kommune. Dersom det stemmer, blåser de opp startantallet og trekker bevaringen ned. Å starte ved ett års botid (som her) demper effekten. Tall med startbotid 0 ligger også i JSON.
- k års botid i 10598 tilsvarer omtrent k + 1 år etter bosetting i monitorens forstand.
- Andeler over 100 forekommer for små grupper. Det skyldes tilflytting og trolig gjeninnvandring.

### D. Innvandringsgrunn

Statistikk for innvandringsgrunn finnes ikke etter region og botid samtidig. Nærmeste tilnærming er landbakgrunn (tabell C). For landet viser SSB 06318 hvor mange av de ikke-nordiske førstegangsinnvandrerne i 1990–2025 som fortsatt bodde i Norge ved utgangen av perioden:

| Grunn | I alt | Flukt | Familie | Arbeid | Utdanning |
|---|---|---|---|---|---|
| Andel som fortsatt bor i Norge | 69,4 % | 84,5 % | 76,2 % | 60,8 % | 37,4 % |

Flyktninger forlater altså sjelden Norge, men flytter ofte innenlands. Arbeidsinnvandrere forlater oftere landet, men blir oftere værende der de bosatte seg.

### E. Kommuner i Nord-Norge

Andel bosatt i kommunen fem år etter bosetting (Monitor 2017, vedleggstabell 4.9, PDF-side 92, kommuneinndeling før 2020):

| Kommune | Kull 2009 | Kull 2010 |
|---|---|---|
| Alta | 96 % (45) | 97 % (33) |
| Bodø | 81 % (126) | 62 % (85) |
| Hammerfest | 82 % (72) | 79 % (33) |
| Harstad | 83 % (103) | 87 % (76) |
| Lenvik | 53 % (38) | 41 % (27) |
| Narvik | 77 % (47) | 70 % (43) |
| Nesna | 54 % (24) | 42 % (24) |
| Rana | 82 % (39) | 85 % (39) |
| Sortland | 44 % (32) | 58 % (45) |
| Tromsø | 83 % (127) | 72 % (93) |
| Vadsø | 72 % (116) | 69 % (65) |

Antall bosatte står i parentes. 2008-kolonnen i samme vedleggstabell er forskjøvet i selve PDF-en (Askim står for eksempel med 566 bosatte) og er ikke brukt.

Kull 2015, netto (SSB 2021, figur 5): Bosatte fra kullet i kommunen 1.1.2020, i prosent av antallet bosatt i 2015. Tallet inkluderer tilflyttere. Tromsø 106 % (200), Bodø 106 % (141), Vågan 83 % (103), Senja 74 % (129), Vadsø 45 % (102).

Femårs netto bevaring av alle innvandrere fra 1.1.2021 til 1.1.2026, regnet fra botid 0–4 til 5–9 år (IMDi): Nord-Norge 66,8 %, mot 84,4 % i landet. Utvalgte kommuner: Senja 76,0 %, Fauske 77,0 %, Vefsn 76,7 %, Harstad 73,3 %, Rana 72,7 %, Hammerfest 70,1 %, Tromsø 69,8 %, Bodø 68,4 %, Alta 68,2 %, Narvik 65,9 %, Vestvågøy 62,0 %, Sør-Varanger 55,7 %, Vadsø 48,4 %, Nordreisa 48,1 %. Tall for alle 80 kommuner, også 2014–2019 og 2020–2025, ligger i JSON.

Andel av flyktningene med minst fem års botid som bor i sin første bosettingskommune, 1.1.2023 (IMDi): Tromsø 62,4 %, Rana 61,2 %, Hammerfest 65,9 %, Narvik 67,0 %, Alta 69,4 %, Bodø 70,2 %, Harstad 73,4 %, Senja 81,3 %, Vadsø 90,4 %. Dette er et sammensetningsmål: En lav andel betyr mange tilflyttere, ikke nødvendigvis lav bofasthet.

### F. Tidligere deltakere i introduksjonsprogrammet (SSB 10824)

Bosatte etter nåværende bosted, i prosent av antallet etter bosted under programmet, fem år etter avsluttet program. Det tilsvarer omtrent 7–8 år etter bosetting.

- Nordland: 53 % (avsluttet 2013), 61 % (2014), 48 % (2015), 55 % (2016), 47 % (2017), 47 % (2018) og 48 % (2019).
- Troms (gammelt fylke): 69 % (2011), 65 % (2013) og 64 % (2014).
- Finnmark (gammelt fylke): 61 % (2011), 52 % (2013) og 40 % (2014).
- Bodø: 72–93 % for avslutningsårene 2015–2019.
- Tromsø: 87–96 % for 2011–2014.

Landet er 100 % per definisjon. Nevnere under 20 er utelatt.

### G. Netto innenlands flytting (SSB 07210)

Nord-Norge hadde en netto innenlands utflytting av innvandrere og norskfødte med innvandrerforeldre på til sammen 32 674 personer i 2008–2025. For den øvrige befolkningen var tallet 24 282. Året 2024 skiller seg ut: Innvandrerne sto for 3 346 av 4 542 netto utflyttede. Flyttinger mellom kommuner i Nord-Norge nuller seg ut i summen.

## Mål og definisjoner (feltet `maal` i JSON)

- `i_forste_bosettingskommune`: Bor i første bosettingskommune (SSB-monitoren). `basis` angir om nevneren er hele kullet eller dem som fortsatt bor i Norge.
- `i_forste_bosettingsfylke`: Første kommune pluss annen kommune i samme fylke.
- `netto_bevaring_omraade` og `netto_bevaring_relativ_landet`: Pseudokohorter (SSB 10598 og IMDi-botid).
- `netto_kohortbestand_i_kommunen` og `netto_kohortbestand_i_landsdelen`: Kullets bestand i kommunen eller landsdelen senere, delt på antallet bosatt der. Tilflyttere inngår.
- `netto_bevaring_intro`: SSB 10824.
- `andel_av_bestand_i_forste_bosettingskommune` og `andel_av_bestand_med_botid_10pluss`: IMDi-bestandsmål.
- `fortsatt_bosatt_i_norge`: SSB 06318.
- `netto_innenlands_flytting_*`: SSB 07210. Verdien står i feltet `antall`.

## Hva som ikke finnes

1. Ingen Statistikkbank-tabell gir bofasthet etter bosettingsår eller sekundærflytting. Monitortallene publiseres bare i rapporter og artikler.
2. Det finnes ingen direkte fylkestall for 10, 15 eller 20 år etter bosetting. Monitoren gir bare fem år per fylke. De lange seriene (opptil 14 år) gjelder bare landet. Unntaket er Fafos tiårstall og landsdelstall for Nord-Norge samlet.
3. Kullene 2013, 2014 og 2016–2018 er ikke publisert per fylke. SSB opplyser at tallgrunnlaget for alle kull i 2024-monitoren (2010–2023, fulgt i opptil 14 år) kan fås ved henvendelse til forfatterne, Mads Ivar Kirkeberg og Frøydis Strøm.
4. Innvandringsgrunn finnes ikke krysset med region og botid. Innvandringsgrunn per kommune (IMDi) mangler botid. 06318 er bare nasjonal.
5. IMDi publiserer ingen indikator for bofasthet fem år etter bosetting per kommune, bare bestandsmålet «Sekundærflytting blant flyktninger» (til og med 2023).
6. For ukrainske flyktninger er historikken for kort (bosatt 2022–2023). SSB oppgir at 9 % av 2022-kullet hadde forlatt bosettingskommunen etter to år, de fleste ved å utvandre.
7. Kommunetall før 2020 gjelder gammel inndeling. 2008-kolonnen i vedleggstabell 4.9 i 2017-rapporten er ubrukelig.

## Inndeling og skjøting

- Monitoren bruker gamle fylker (Nordland, Troms, Finnmark) til og med kull 2012. Kull 2015 bruker Troms og Finnmark samlet. Kull 2019 bruker 2024-inndelingen. Endringen for Troms er liten: Tjeldsund-delen fra Nordland ble flyttet til Troms i 2020.
- I 10598 er Nord-Norge samlet og «Troms og Finnmark» (19+20 → 54 → 55+56) sammenhengende for 2005–2026. Troms og Finnmark hver for seg dekker bare 2005–2019 og 2024–2026, altså høyst 14 år.
- IMDi har regnet kommunetallene fra 2020 om til 2024-koder. Fylkene 55 og 56 mangler for 2020–2023 og er her summert fra kommunetall.

## Anbefalinger for dashbordet

01. Erstatt de to manuelle kullene i `KOHORT_RET` med serien i tabell A (16 kull, 1998–2019, basis hele kullet). Rett 2019-verdiene til Nordland 82 og Troms 81. Begrunnelse: Kildene gir en sammenhengende og etterprøvbar serie med sidetall.
02. Vis lange perioder (10, 15 og 20 år) som netto bevaring fra SSB 10598, for Nord-Norge samlet, Nordland og Troms og Finnmark, med landet som referanse. Merk tallene som indirekte. Begrunnelse: Det er den eneste åpne kilden som dekker 20 år regionalt.
03. Bruk Fafos tiårstall (om lag 30 % i bosettingskommunen) og landsdelsbevaringen på 44,8 % (kull 2010–2016, målt 2023) som kontrollpunkter. Begrunnelse: Pseudokohortene (39 % netto etter ti år) og Fafo peker i samme retning.
04. Be SSB om monitorgrunnlaget per fylke og kull for botid 1–14 år. Begrunnelse: Det er eneste vei til direkte fylkestall ut over fem år.
05. Bruk kommunetall (IMDi-pseudokohort og SSB 10824) bare med antall og forbehold. Begrunnelse: Mange nordnorske kommuner har under 50 personer i nevneren.

## Filer og skript

- `skript/sok_ssb.py` og `skript/meta_ssb.py`: tabellsøk og metadata (PxWebApi v0).
- `skript/hent_ssb.py`: henter 10598, 08377, 05648, 03810, 06318, 07113, 10824 og 07210 til `kilder/ssb/`.
- `skript/hent_imdi.py`: henter IMDi-tabeller til `kilder/imdi/`. API-et filtrerer på én region per spørring.
- `skript/pdf_tekst.py`, `skript/fylketabeller.py`, `skript/nn_rader.py` og `skript/pdf_rader.py`: tekst og tabellrader fra PDF-ene.
- `skript/ssb_figurdata.py` og `skript/html_tekst.py`: figurdata og tekst fra SSB-artikler.
- `skript/pseudokohort_10598.py`: pseudokohorter. Resultat i `kilder/avledet/pseudokohort_10598.json`.
- `skript/monitor_data.py`: manuelt avleste monitortall med kilde og side.
- `skript/bygg_statistikk.py`: bygger `statistikk.json`.

Grunnlag: SSB (Statistikkbanken, PxWebApi v0/v2; monitor for sekundærflytting 2005–2025), IMDi (statistikk-API, kilde SSB), Fafo-rapport 2025:14 og Kunnskapsbanken for Nord-Norge (2025). Hentet 20. oktober 2026.
