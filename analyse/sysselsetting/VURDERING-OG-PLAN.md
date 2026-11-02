# Sysselsatte per kommune og næring: kildevurdering og plan

20. oktober 2026. Grunnlag: SSBs tabellkatalog og PxWebApi v0/v2 (metadata, fotnoter og prøveuttrekk for alle 80 kommuner), Enhetsregisterets API, Fiskeridirektoratet og regjeringen.no. Ingen kode er endret.

## Konklusjon

Det finnes åpne, fullstendige og etterprøvbare tall for antall sysselsatte per kommune og næring, både etter arbeidssted og bosted, for hvert år 2008–2025. To SSB-tabeller bør være ryggraden: **13470** (næring ned til femsifret nivå, fritt aggregerbar) og **13472** (sektor: stat, kommune, fylkeskommune, offentlige foretak og privat). Begge publiseres uten anonymisering av bedrifter; bare 1- og 2-tall er endret til 0 eller 3. Seriene er sammenlignbare fra 2015, og SSB har kodelister som slår sammen gamle kommuner til dagens inndeling. Unntaket er Narvik og Hamarøy før 2020. Kommunetall finnes bare for 4. kvartal hvert år; siste årgang er 2025. Neste årgang kommer trolig med ny næringsstandard (SN2025) og dermed et brudd.

Dashbordet har i dag sysselsatte per næring bare på temasiden for næringsliv (`NAERING_DATA`, 19 grupper, ett år). Kommunesidene viser sysselsettingsrate og uføreandel, men ikke hvem som jobber hvor. Planen nedenfor legger til en egen datablokk og et kort «Hvem jobber her?» på kommunesidene, med sektor, næring, utvikling 2015–2025 og pendling.

## Kildeoversikt

| Kilde | Innhold | Nivå og periode | Vurdering |
|---|---|---|---|
| **SSB 13470** | Sysselsatte etter næring (SN2007, 1 825 koder fra hovedområde til femsifret), bosted og arbeidssted, 4. kvartal | Kommune, 2008–2025 | **Primær.** Ingen prikking av bedrifter. Kodelister for sammenslåtte kommuner, landsdel og sentralitet, og ferdige næringsgrupperinger. |
| **SSB 13472** | Sysselsatte etter sektor (5) og næring (8 grupper), bosted og arbeidssted | Kommune, 2008–2025 | **Primær for sektor.** Ingen prikking. Statsforvaltningen omfatter helseforetakene. |
| SSB 07984 | 17 næringsgrupper etter kjønn og alder | Kommune, 2008–2025 | Prikket: 287 skjulte celler i Nord-Norge (2015 og 2025). Narvik mangler industri, energi, IKT og finans. Brukes bare for kjønn og alder på totalnivå. |
| SSB 08536 | 88 næringer etter kjønn | Kommune, 2008–2025 | Prikket: 1 931 av 7 120 celler skjult i 2025. Summen av næringene i Narvik dekker bare 6 270 av 10 064. Ikke egnet. |
| SSB 11617 | Inn- og utpendling, 6 næringsgrupper, bosatte og arbeidssted | Kommune, 2008–2025 | **Sekundær.** Gir arbeidsplassdekning og pendling per sektor. |
| SSB 03321 | Pendlingsstrømmer kommune til kommune | Kommune, 2000–2025 | **Sekundær.** De viktigste pendlingsmålene per kommune. Ingen kodeliste for sammenslåing. |
| SSB 11917 | Sysselsatte i kommunal sektor etter funksjon (helse og omsorg, skole, barnehage mv.) | Kommune, 2015–2025 | **Sekundær.** Bodø: 4 666 i alt, 2 402 i helse og omsorg. Annen definisjon enn 13472 (4 608). |
| SSB 11619 | Sysselsatte etter yrke (10 grupper) | Kommune, 2015–2025 | Mulig senere. |
| SSB 07944 | Helse- og sosialfaglig utdannede etter sektor og årsverk | Kommune, 2008–2025 | Mulig kobling til eldreomsorgen (tema 05). |
| SSB 07091 | Antall bedrifter etter næring og størrelse | Kommune, 2009–2026 | Antall bedrifter, ikke sysselsatte. Kontekst. |
| SSB 11652 / 12315 | Lønnstakere og jobber per kvartal (a-ordningen) | **Bare fylke**, 2016K1–2026K2 | Gir ferskere tall for fylkene, ikke for kommunene. |
| SSB 11713 | Fylkesfordelt nasjonalregnskap: sysselsatte og bruttoprodukt per næring | Bare fylke, 2011–2023 | Kontekst for produktivitet. |
| **Enhetsregisteret** (Brønnøysund) | Underenheter med antall ansatte (fra Aa-registeret), femsifret næringskode (SN2025 fra 1.9.2025) og kommune | Underenhet, daglig | **Supplement.** Egner seg til å navngi de største arbeidsgiverne, ikke til totaler. Forsvaret er nesten usynlig: i Målselv er ingen forsvarsenhet blant de største. |
| Fiskeridirektoratet, fiskermanntallet | Fiskere etter bostedskommune, alder og kjønn | Kommune, årlig | Interaktiv visning; nedlasting eller API ikke funnet. Mulig supplement for fiske, der mange er selvstendige. |
| NAV | Ledige stillinger og helt ledige per kommune og yrke | Kommune, månedlig | Ikke sysselsetting, men utfyllende. |

## Funn

**Funn 01 — 13470 og 13472 er fullstendige; tabellene med kjønn og alder er prikket.** Observasjon: I 13470 og 13472 er ingen celler skjult for de 80 kommunene. SSB oppgir at tabellene er «uten anonymisering av bedrifter» etter statistikkloven § 7(3); bare 1- og 2-tall er endret til 0 eller 3. I 07984 og 08536 er celler med én eller to bedrifter bak prikket, og i tillegg sekundærprikket. Grunnlag: fotnoter i tabellene og uttrekk 2015 og 2025.

**Funn 02 — Tabellene går ikke helt opp mot hverandre.** Observasjon: Bodø har 29 509 sysselsatte etter arbeidssted i 13472, 29 511 i 07984 og 29 511 i 13470. Avrundingen av små tall gjør at summer kan avvike med noen få personer. Hver figur må derfor bygge på én tabell.

**Funn 03 — Seriene er sammenlignbare fra 2015.** Observasjon: Fra 2015 bygger statistikken på a-ordningen og samordnes ikke lenger med arbeidskraftundersøkelsen. Landet har 2 650 000 sysselsatte i 2014 (avrundet) og 2 597 063 i 2015. I tillegg er sysselsatte i næring 09.1 flyttet fra sokkelen til fastlandet fra 4. kvartal 2018.

**Funn 04 — Kommunenummer må slås sammen bakover.** Observasjon: Tallene er lagret med kommunenummeret som gjaldt hvert år; Tromsø (5501) har 0 før 2024 og Narvik (1806) 0 før 2020. Kodelisten `agg_KommSummer` gir sammenslåtte serier for 13470 og 13472, for eksempel Senja = 1927, 1928, 1929, 1931, 5421 og 5530. Narvik og Hamarøy er bare definert fra 2020, fordi Tysfjord ble delt mellom dem.

**Funn 05 — Nord-Norge har en klart høyere offentlig andel.** Observasjon (13472, arbeidssted, 4. kvartal 2025):

| Sektor | Nord-Norge | Andel | Landet, andel |
|---|---:|---:|---:|
| Statsforvaltningen (inkl. helseforetak) | 39 135 | 15,8 % | 11,8 % |
| Kommunal forvaltning | 55 082 | 22,2 % | 18,1 % |
| Fylkeskommunal forvaltning | 6 943 | 2,8 % | 1,7 % |
| Offentlige foretak | 10 349 | 4,2 % | 4,1 % |
| Privat sektor | 136 703 | 55,1 % | 64,3 % |
| **I alt** | **248 212** | **100 %** | **2 872 855** |

Offentlig forvaltning sysselsetter 40,8 % i Nord-Norge mot 31,6 % i landet. I Tromsø står staten for 12 312 av 48 082 (25,6 %), i Bodø 6 887 av 29 509.

**Funn 06 — Flere bor enn jobber i landsdelen.** Observasjon (07984, 2025): 251 710 sysselsatte bor i Nord-Norge, og 248 214 har arbeidssted der. Forskjellen er 3 496. Per kommune er forskjellene store: Bardu har 2 479 arbeidsplasser og 2 196 sysselsatte bosatte (13470).

**Funn 07 — SSB plasserer Forsvaret riktig; Enhetsregisteret gjør det ikke.** Observasjon (13470, 2025): I Bardu er 1 384 av 2 479 sysselsatte i forsvar (84.22), i Målselv 871 av 3 556 og i Bodø 776. I Enhetsregisteret er Forsvarsbygg den eneste forsvarsenheten blant de største i Bardu, og i Målselv finnes ingen. Enhetsregisteret egner seg derfor bare til å navngi arbeidsgivere, med forbehold.

**Funn 08 — Kommunetall finnes bare årlig.** Observasjon: Kvartalsvise tall fra a-ordningen finnes bare per fylke (11652, 12315) og månedlige tall bare for landet (13126). SSB publiserte 4. kvartal 2025 den 26. februar 2026.

**Funn 09 — Ny næringsstandard gir trolig brudd neste år.** Observasjon: SN2025 ble tatt i bruk i Enhetsregisteret 1. september 2025, og flere SSB-tabeller bruker den fra 2025–2026. Sysselsettingstabellene bruker fortsatt SN2007. Hypotese: Dersom 4. kvartal 2026 publiseres med SN2025 (ventet februar 2027), forventer vi nye tabellnumre og brudd i næringsgruppene, men ikke i sektor og totaler.

**Funn 10 — Dagens `NAERING_DATA` er riktig, men smal.** Observasjon: Tema 08 bruker 13470 for 19 utvalgte grupper etter Samfunnsøkonomisk analyse, for 2025 og 2015 (bare landet og landsdelen). Siden 13470 ikke er prikket, gir tolkningen av tomme celler som 0 i `fetch_naering.py` ingen feil i dag. Tallene vises ikke på kommunesidene.

## Plan

### Fase 1 — Datagrunnlag (`fetch_sysselsetting.py` → `SYSS_DATA`)

1. **13470 via PxWebApi v2 med `agg_KommSummer`**, arbeidssted og bosted, 2015–2025:
   - de 17 næringshovedgruppene for alle år
   - detaljgruppene fra tema 08 (fiske, havbruk, fiskeindustri, reiseliv, forsvar osv.) for 2015 og siste år
   - samme tall for fylkene, landsdelen (`agg_LandsdelKommun`, LK06), sentralitetsklassene (`agg_SentralIndeksA`) og landet
2. **13472**, arbeidssted og bosted: fem sektorer for 2015–2025, og sektor × 8 næringsgrupper for siste år.
3. **11617**: inn- og utpendling og arbeidsplassdekning per kommune, 2015–2025. **03321**: de fem største pendlingsstrømmene inn og ut av hver kommune, siste år.
4. **11917**: kommunalt sysselsatte etter funksjon, siste år og 2015.
5. **Narvik og Hamarøy** vises fra 2020 med merknad. Alternativet er å rekonstruere 2015–2019 fra 1805, 1854, 1849 og 1850, slik pyramidedataene gjør, men Tysfjords arbeidsplasser kan ikke fordeles presist.
6. **Kontroller i skriptet**:
   - sum av næringsgrupper mot total (avvik bare fra avrunding)
   - sum av 80 kommuner mot LK06
   - 13470 mot 13472 og `NAERING_DATA`
   - bosatte sysselsatte mot 13563
7. **Størrelse:** 80 kommuner × 11 år × 2 mål × 17 grupper gir om lag 30 000 tall, anslått 150–200 kB. Det er i samme størrelsesorden som de andre blokkene. Detaljgrupper bare for to år.

### Fase 2 — Kommunesiden: kort «Hvem jobber her?» i Arbeid-fanen

- **Nøkkeltall:**
  - arbeidsplasser (arbeidssted)
  - sysselsatte bosatte
  - arbeidsplassdekning (arbeidssted per bosatt sysselsatt)
  - andel i offentlig forvaltning mot landsdelen og landet
  - endring i arbeidsplasser 2015–2025
- **Sektorfordeling** som én stablet stolpe mot Nord-Norge og landet.
- **Næringer**, 17 grupper som liggende stolper med landets andel i merknaden. Den næringen der kommunen er mest spesialisert (lokaliseringskvotient: andel i kommunen delt på andel i landet), utheves.
- **Utvikling 2015–2025** for de fem største næringene.
- **Pendling:** inn og ut, og de viktigste kommunene folk pendler til og fra.
- **Forbehold** for små kommuner, der avrundingen av 1- og 2-tall slår mer ut.

### Fase 3 — Landsdel, fylker, sammenligning og kart

- Fylkes- og landsdelssidene: samme kort, aggregert.
- Sammenlign-siden: rader for arbeidsplasser, offentlig andel og vekst 2015–2025.
- Skjulte kartindikatorer: offentlig andel, privat andel, arbeidsplassvekst 2015–2025 og arbeidsplassdekning. De brukes på tema 04 og 08.
- Tema 08 flyttes over på `SYSS_DATA`, slik at næringslivssiden og kommunesidene bruker samme tall.

### Fase 4 — Supplement (valgfritt)

- **De største arbeidsgiverne per kommune** fra Enhetsregisteret (bulknedlasting under bygget, de fem største underenhetene etter ansatte). Det må merkes at tallene er ansatte i Aa-registeret, at offentlige virksomheter kan være registrert samlet et annet sted, og at Forsvaret mangler.
- **Fiskermanntallet**, dersom Fiskeridirektoratet har en nedlastbar fil. Det må undersøkes.

### Fase 5 — Klar for SN2025

- Næringsgruppene defineres ett sted i skriptet, som en tabell fra kode til gruppe.
- Når SSB publiserer 4. kvartal 2026, legges en kodenøkkel fra SN2025 til gruppene inn, og bruddet markeres i figurene.
- Sektor og totaler påvirkes ikke.

### Metode

Nytt metodekort `#sysselsetting`. Det skal forklare:

- arbeidssted mot bosted
- brudd i 2015 og 2018
- avrunding av 1- og 2-tall
- at helseforetakene ligger under staten
- Narvik og Hamarøy
- at Enhetsregisteret bare brukes til navn

## Valg som må tas

01. **Hovedmål på kommunesiden: arbeidssted.** Begrunnelse: Det viser arbeidsplassene i kommunen; bosted vises ved siden av.
02. **Narvik og Hamarøy fra 2020.** Begrunnelse: Delingen av Tysfjord kan ikke fordeles presist på arbeidsplasser.
03. **Navngitte arbeidsgivere fra Enhetsregisteret: utsett til fase 4.** Begrunnelse: Tallene er svakere enn SSBs, og Forsvaret mangler.
04. **Kjønn og alder: ikke i første omgang.** Begrunnelse: Tabellene med kjønn og alder er prikket på næringsnivå.

Grunnlag: SSB 13470, 13472, 07984, 08536, 11617, 03321, 11917 (uttrekk 20. oktober 2026, 80 kommuner, 2015 og 2025); Enhetsregisteret (API, 20. oktober 2026); [SSB om SN2025](https://www.ssb.no/virksomheter-foretak-og-regnskap/metoder-og-dokumentasjon/ny-standard-for-naeringsgruppering-innfores-1.september-2025); [Fiskeridirektoratet, fiskermanntallet](https://www.fiskeridir.no/statistikk-tall-og-analyse/data-og-statistikk-om-yrkesfiske/fiskere-i-fiskermanntallet); [regjeringen.no om statlige arbeidsplasser](https://www.regjeringen.no/no/tema/kommuner-og-regioner/regional--og-distriktspolitikk/flytting-og-oppretting-av-statlige-arbeidsplasser/id3095519/), der departementet bruker SSB 13472.
