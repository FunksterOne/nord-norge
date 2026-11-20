# Plan: NAV-statistikk for alle 80 kommuner i Nord-Norge-dashbordet

Status: alle seks faser ferdige 20. november 2026. Publisert i commit 385e9dc og kontrollert
på nord-norge.vercel.app.

## Status fase 6 (20. november 2026)

- **Metodesiden:** nytt kort `metode.html#nav` (NAV-statistikk per kommune) med kilder,
  inndeling, uføreutgaver, prikking, nivåer, tekstregler, kontroll og forbehold. Kortet er
  lagt inn i innholdsfortegnelsen og har en rad i tabellen «Andre offentlige kilder».
  Lenkene fra panelene peker hit.
- **Kontroller som går gjennom:**
  - `tools/sjekk_layout.py` og `tools/sjekk_funn.py` gir kode 0. De dekker temasidene, som
    ikke er endret.
  - `regresjon_lodingen.py` og `kontroll.py` gir kode 0.
  - `npm run build` går gjennom.
- **Prøvd i nettleseren uten konsollfeil:**
  - `metode.html#nav`
  - `nord-norge.html`
  - `fylke.html` for Nordland, Troms og Finnmark
  - kommunesiden for Lødingen, Narvik og Røst i lyst og mørkt tema og på smal skjerm
  - alle 80 kommuneblokkene, tegnet i én kjøring
- **Gjenstår:**
  - commit på `main` og push, som utløser publisering på Vercel
  - deretter kontroll av `nord-norge.vercel.app`
- **Oppdatering senere:** last ned nye NAV-filer til `analyse/nav/kilder/<kategori>/` med
  skriptene fra Lødingen-arbeidet (`nav_arkiv.py`). Kjør deretter `python fetch_nav.py`,
  regresjonstesten og `kontroll.py`.

## Status fase 5 (20. november 2026)

- **Panelet.** `NN.navNivaa(kode, host)` i `src/lib/navkort.js` tegner NAV-panelet i «Arbeid og
  forsørgerbyrde» på `nord-norge.html` og `fylke.html`, i `#navNivaa` etter
  «Hvem bærer hvem?». Kallet står i `assets/app.js` ved forsørgerkortet og tegner på nytt bare
  når fylket byttes (`data-kode`).
- **Landsdelen** sammenlignes med de tre fylkene og landet, og teksten nevner høyeste og
  laveste fylke. **Fylket** sammenlignes med Nord-Norge og landet.
- **Innhold:**
  - fem nøkkeltall
  - regelbasert tekst
  - kart over kommunene med valg mellom fire NAV-lag
  - fem linjediagrammer
- **Kartlag** i `src/charts/map.js`: `navLedige`, `navAap`, `navNedsatt` og `navUfore`. De
  leser `NAV_KART` via `L.NAVK` og er skjult i hovedkartets verktøylinje, slik andre
  temalag er. Kommuner uten tall, som Vevelstad for ledighet, får ingen farge.
- **To feil funnet og rettet:**
  - `fylke.html` bytter automatisk «Nord-Norge» med fylkesnavnet i all tekst, så panelet
    skrev «om lag som Troms samlet». `.nav-blokk` er nå unntatt fra byttet.
  - På `fylke.html` havnet panelet først inne i en lukket `<details>` («Bakteppe»), fordi
    siden er bygd annerledes enn `nord-norge.html`. Panelet er flyttet ut.
- **Kontroll:**
  - `nord-norge.html` og `fylke.html?f=Troms` er tegnet uten feil i konsollen.
  - Teksten er lest gjennom, og bytte av kartlag er prøvd.
  - Bygget går gjennom.

## Status fase 4 (20. november 2026)

- **Blokken.** `src/lib/navkort.js` (`NN.navKort`) tegner NAV-blokken i Arbeid-fanen på
  kommunesiden. Den står etter tolkningen og før forsørgerbyrdekortet, i `#navBlokk` i
  `renderArbeidPanel` i `kommune.html`. Dataene hentes ved behov fra `data/nav/<nr>.json`, og
  figurene nummereres etterpå.
- **Innhold:**
  - fem nøkkeltall
  - regelbasert tekst i fire avsnitt pluss forbehold
  - fem linjediagrammer: kommunen mot fylket og landet, eller Nord-Norge for AAP og nedsatt
  - en årstabell med † for anslått og «brudd» og «skjult» der det gjelder
  - «Hva tallene måler»
- **Tekstreglene:**
  - Forskjeller under 0,2 prosentpoeng gir «om lag som».
  - Ledigheten telles «tydelig over fylkets» i N av M hele år.
  - Teksten viser høyeste måned siste hele år.
  - Uføreteksten forklarer forskjellen mot SSB-nøkkeltallet.
  - Forbehold gis for små arbeidsstyrker (under 1 000), anslåtte og skjulte år, brudd og
    sammenslåing.
  - Påstander dataene ikke dekker, er tatt ut.
- **Linjediagrammet** (`src/charts/linjer.js`) har fått `brudd: true`. Linjen brytes ved
  manglende verdi, og enkeltpunkter vises som prikk.
- **Data:** landsraden i PST011/PST062 ble ikke lest, fordi «I alt» stod i en annen kolonne. Det
  er rettet, og minstepensjon har nå landstall (12,5 % i 2026).
- **Kontroll:** alle 80 kommuner er tegnet i nettleseren uten feil, og ingen tekst inneholder
  `undefined`, `NaN` eller tomme prosenttall. Lødingen er kontrollert mot rapporten.
  Vevelstad (skjulte år), Narvik (brudd) og Senja (sammenslåing) er lest gjennom. Bygget
  går gjennom.
- **Kjent forskjell:** fylkesandelen kan avvike med 0,1 i visningen fra Lødingen-rapporten,
  for eksempel Nordland 2025 1,6 mot 1,5. Rapporten brukte NAVs avrundede fylkestall, mens
  dashbordet regner fylket av kommunene. Forskjellen er høyst 0,06 prosentpoeng (fase 2).

## Status fase 3 (20. november 2026)

`python fetch_nav.py` gjør nå alt i én kjøring: uttrekk, `nav_kommuner.json`, dashbordfiler og
`NAV_KART`. Kjør deretter `analyse/nav/skript/regresjon_lodingen.py` og
`analyse/nav/skript/kontroll.py`. Begge skal gi kode 0.

- **Filer som lastes ved behov:**
  - `data/nav/<kommunenr>.json`, 80 filer på om lag 17 KB.
  - `data/nav/fylke-{18,55,56,NN}.json`.
  - Vite-pluginen kopierer `data/` til `dist/`, og bygget er kontrollert.
- **Felt i kommunefilen:**
  - `ledige`, `aap` og `nedsatt` har `{aar, pst, antall, f, n, mnd}`. `f` er en flaggliste per
    år (`anslatt`, `skjult`, `beregnet`, `brudd`, `aarssnitt`), `n` er antall måneder, og
    `mnd[år]` har 12 par `[antall, andel]`.
  - `nedsatt.uten_aap` har andelen uten AAP per år.
  - `ufore` har `{dato, pst, antall, f, astd}`: desember hvert år og september de siste to
    årene. `f` inneholder `uforepensjon` til og med 2012.
  - `pensjon` har `{aar, alderspensjon, minstepensjon, pst, f}`, og `f` har `navfeil` før 2020.
  - `ref.fylke`, `ref.NN` og `ref.landet` har de samme seriene uten månedstall.
  - `meta` har tekstene om kilde, brudd, prikking og minstepensjon.
- **`NAV_KART` i `assets/data.js`:** siste hele år for ledige, AAP og nedsatt (2025), uføre
  september 2026 og minstepensjon 2026, per kommune og med referanser (fylker, NN, landet).
- **Prikking:** regelen fra fase 2 er innført. Lødingen 2023 er nå 1,39 % og merket anslått.
  Månedstallene er uendret, og regresjonstesten går gjennom.
- **To feil funnet og rettet:**
  - Ett radformat ga «landstall» som egentlig var «Ukjent» (1 242 personer med ukjent bosted)
    i AAP-filen for 2024. Overskriftsraden bærer nå fylkesnavnet videre, slik at «I alt»
    under den regnes som fylkessum.
  - Landsreferansen for AAP og nedsatt arbeidsevne fra 2016 er tatt bort. Filene har ingen
    landsrad, og fylkesradene varierer for mye til å summeres pålitelig. Kommunene
    sammenlignes med fylket og Nord-Norge, slik Lødingen-rapporten gjorde. Helt ledige, uføre,
    pensjon og AAP 2010–2015 har landstall. Grunnlag: Lødingen-leveransen i
`~/Documents/Claude/Lodingen-folkehelse` (skript `nav_*.py`, data `data/nav_kommune/`).

## Status fase 2 (20. november 2026)

Rapporten er `analyse/nav/KONTROLL.md`, generert av `analyse/nav/skript/kontroll.py`
(kode 0 = ingen sumavvik).

- **Sumkontroll.** Summen av kommunene er sammenlignet med NAVs fylkestall i 2 024 tilfeller
  der inndelingen er lik.
  - Det er null avvik i antall for helt ledige, AAP og nedsatt arbeidsevne.
  - Uføre har ett avvik på én person (Nord-Norge, desember 2017). Det ligger i NAVs egen fil:
    Troms-kommunene summerer til 11 297, mens NAVs fylkessum er 11 298.
  - Andelene avviker høyst 0,07 prosentpoeng. Det er avrunding, fordi NAV oppgir
    fylkesandelen med én desimal.
- **Feil funnet og rettet.** Fylkessummen ble tom i alle måneder der minst én kommune var
  prikket. Det gjaldt blant annet Nordlands ledighetsandel i mange år. Prikkede celler telles
  nå som 1,5 i fylkessummer, som er midtpunktet i NAVs intervall 0–3. Månedene merkes
  `anslatt_mnd`. Avviket fra NAVs fylkestall er da høyst 5 personer og 0,06 prosentpoeng.
- **Dekning.** Alle 80 kommuner har tall i alle publiserte perioder, med disse unntakene:
  - Narvik og Hamarøy har brudd før 2020, og for uføre før desember 2018.
  - Vevelstad er prikket hele året i seks år (helt ledige).
- **Hopp.** 119 endringer fra år til år er over tersklene. Nesten alle gjelder kommuner med en
  nevner under 1 000 personer (Røst, Træna, Moskenes, Beiarn, Vevelstad, Hasvik). Ingen hopp
  faller sammen med bytte fra beregnede tall til NAV-tall, eller med overgangen fra
  årssnitt til månedssnitt for AAP i 2015–2016. De største hoppene i større kommuner har
  mulige forklaringer, som ikke er kontrollert:
  - Nordkapp og Moskenes 2019–2020 (pandemien og reiselivet)
  - Sør-Varanger 2015–2016 (gruvenedleggelsen)
- **NAV mot SSB (uføre).** NAV for september 2025 ligger i median 0,55 prosentpoeng under
  SSB 11715 for 2025, med et spenn fra −1,93 til +0,68. Dette må forklares der NAV-serien vises
  ved siden av SSB-nøkkeltallet. Forskjellen kommer av ulik telledato og ulik befolkning.
- **Beslutning som gjenstår — prikking i kommunenes årssnitt for helt ledige.**
  - I dag regnes snittet bare av de publiserte månedene, som i Lødingen-rapporten. Siden de
    prikkede månedene har 0–3 ledige, blir snittet for høyt. I 33 av 72 kommuneår er det mer
    enn 0,3 prosentpoeng over nedre grense.
  - Anbefaling: regn prikkede måneder som 1,5 og merk snittet som anslått. Vis ikke snitt når
    mer enn halvparten av månedene er prikket.
  - Konsekvens: Lødingen 2023 går fra 1,50 % til om lag 1,38 % og avviker fra rapporten.

## Status fase 1 (20. november 2026)

- `fetch_nav.py` skriver `analyse/nav/data/nav_kommuner.json` (1,1 MB) for alle 80 kommuner,
  de tre fylkene, landsdelen og landet. Kildefilene ligger i `analyse/nav/kilder/` utenfor git.
- **Dekning per kommune:**
  - helt ledige 2012–2026
  - AAP 2010–2026 (2010–2015 som årssnitt, 2015 også juli–september)
  - nedsatt arbeidsevne 2016–2026 (pluss september 2015)
  - uføre for 26 tellingsdatoer fra desember 2010 til september 2026
  - alderspensjon og minstepensjon 2016–2026
- **Regresjonstest:** `analyse/nav/skript/regresjon_lodingen.py` viser at Lødingen er
  identisk med den kontrollerte leveransen i alle kategorier, også i den kuraterte
  uføreserien med aldersstandardiserte andeler.
- **Kommunenøkkel:** fra SSB Klass 131. For hver kommune og periode brukes den nyeste
  kodegenerasjonen som har tall. Da går NAVs egne omregninger foran vår summering, og
  Harstad/Bjarkøy i 2012-filen telles ikke to ganger. Sammenslåtte kommuner uten NAV-omregning
  er merket `beregnet`: Senja, Hammerfest og Tjeldsund før 2020, og Harstad 2010–2011.
- **Uføre:** hver fil er en utgave. For hver tellingsdato velges den nyeste utgaven med presise
  andeler. Det er samme regel som i Lødingen-leveransen, og NAVs revisjoner kommer med.
- **Prikking:** helt ledige har prikkede måneder i små kommuner. Vevelstad er prikket hele året
  i 2019–2023 og 2025. Årssnittet regnes av de publiserte månedene. Fase 2 må vurdere om det gir et
  skjevt bilde, siden de prikkede månedene er de laveste.
- **Kontantstøtte på fylkesnivå (avvik fra planen, må avgjøres):**
  - Fylkestall finnes bare for september og desember 2016, andre kvartal 2018, desember 2023,
    desember 2025 og september 2026.
  - Ellers er for mange kommuner prikket til at fylket kan summeres.
  - Målene skifter mellom utgavene. Landsandelen var 26,5 % i desember 2016, men 43,3 % i
    andre kvartal 2018 ifølge NAVs egen fil.
  - Reformen i august 2024 bryter serien.
  - Anbefaling: dropp kontantstøtte i dashbordet.

## Konklusjon

Det lar seg gjøre, og det meste av datajobben er allerede gjort. NAVs kommunetabeller er
landsfiler. Hver fil har alle kommunene i landet, så de 13 MB som ble lastet ned for Lødingen
dekker alle de 80 kommunene for de samme årene. Det som gjenstår er å trekke ut dataene per
kommune og håndtere kommunereformen i 2020 og fylkesdelingen i 2024. Etter det må
presentasjonen bygges inn i dashbordet.

Anbefalt form er en ny NAV-blokk i Arbeid-fanen på kommunesiden. Den bygges med de samme
linjediagrammene som Lødingen-presentasjonen, med kommunen, fylket og landet. I tillegg
kommer en kort tidsserie på fylkes- og landsdelssidene og fire kartindikatorer.

## Observasjoner om datagrunnlaget

- HL060 for oktober 2026 har 381 kommune- og fylkesrader, og alle 80 NN-kommuner er med.
- Filene fra 2015–2017 bruker den gamle inndelingen: 44 kommuner i Nordland, og
  19xx- og 20xx-koder i Troms og Finnmark.
- Hullene som ble tettet for Lødingen er tettet for alle kommuner. Det gjelder helt ledige
  2016–2018, AAP og nedsatt arbeidsevne 2016–2017 og uføretrygd 2016. Filene er de samme.
- Disse hullene er nasjonale og kan ikke tettes:
  - Kontantstøtte 2017: NAV publiserte ingen tabeller.
  - Kontantstøtte 2024 til mars 2025: NAV har trukket tallene.
  - Alderspensjon og minstepensjon før 2020: NAV oppgir feil i tallene.
- Sykefravær finnes ikke på kommunenivå hos NAV (SYFRA510 er fylkestall). Kommunetall må
  hentes fra SSB eller FHI.
- Dashbordet har allerede uføreandelen fra SSB 11715 (18–67 år, 2025). NAVs serie bruker en
  annen aldersgruppe og en annen telledato. De to kildene gir derfor ikke samme tall.

## Fase 1 — Datauttrekk og kommunenøkkel

Skriptet blir `fetch_nav.py` i repoet. Kildefilene kopieres til `analyse/nav/kilder/` og
holdes utenfor git.

1. Gjør om `nav_data.py` fra én kommune til en kommuneliste (`CODES` fra fetch_arbeid.py).
   Kommunerader finnes ved koden, ikke ved navnet, og det er enklere enn fylkesradene var.
2. Lag en kommunenøkkel fra gammel til gjeldende kode for 2020 og 2024.
   - Sammenslåtte kommuner: antallene summeres. Andelen regnes som summen av antallene delt
     på summen av nevnerne. Nevneren hentes fra SSB 07459 (befolkning 18–66 år), ikke fra
     antall delt på NAVs avrundede andel.
   - Delte kommuner: Tysfjord (1850) gikk til Narvik og Hamarøy, og Tjeldsund ble delt i
     2020. For disse anbefales et brudd i serien fra 2020, uten fordeling. Hvilke kommuner
     som ble delt, må kontrolleres mot SSBs endringskatalog før koding. Listen her er fra egen
     kunnskap og ikke kontrollert i dag.
3. Prikkede verdier («*», «–», «:») lagres som `null` med et flagg og vises aldri som 0. Det
   er mest aktuelt for kontantstøtte og AAP i de minste kommunene (Træna, Røst, Værøy).
4. Hent fylkes- og landstall fra de samme filene (Nordland-logikken i `nordland_indeks`
   gjenbrukes for Troms og Finnmark).

## Fase 2 — Kontroll av data

Denne fasen er den viktigste.

- **Regresjonstest:** Lødingen fra det nye skriptet skal være identisk med den kontrollerte
  `nav_data.json`.
- **Sumkontroll:** summen av kommunene skal være lik NAVs fylkestall for hvert år og hver
  kategori, innenfor prikkingen.
- **Dekningsmatrise:** kommune × år × kategori, der hvert hull har en årsak som
  ikke publisert, prikket, trukket eller brudd.
- **Hopp-liste:** endringer fra år til år over en terskel, kontrollert mot kommunereformen og
  feilpubliseringer. Ett eksempel på en feilpublisering er HL301-filen merket oktober 2026,
  som inneholder tall for juni 2024.
- Resultatet skrives til `analyse/nav/KONTROLL.md`.

## Fase 3 — Dataformat

- `NAV_KART` i `assets/data.js` får siste år per kommune for kartet og nøkkeltallene,
  anslått til om lag 10 KB.
- `data/nav/<knr>.json` får de fulle årsseriene, månedstallene og fylkes- og landstallene.
  Filene lastes ved behov, slik `data/pyramide/` gjør, med anslagsvis 10–20 KB per kommune.
  Vite-pluginen kopierer mappen.

## Fase 4 — Kommunesiden

Arbeid-fanen får en ny blokk med disse delene:

- Fem figurer av typen `linjer` (kommune, fylke, landet): helt ledige, AAP, nedsatt
  arbeidsevne med og uten AAP, uføretrygd, og minstepensjon som andel av alderspensjonistene
  fra 2020. Minstepensjon er et mål på lav inntekt blant eldre, og dashbordet har ikke et slikt
  mål i dag. Tallene før 2020 brukes ikke, fordi NAV oppgir feil i dem.
- En tabell med årstallene, med låst første kolonne via tabeller.js. Andelen med alderspensjon
  står bare i tabellen. Den følger i hovedsak andelen eldre, som dashbordet allerede viser.
- Fortolkningstekst som genereres av regler fra dataene, som «over/under fylket i N av M år»
  og «høyeste måned». Teksten skal ikke skrives for hånd per kommune. I Lødingen ble det funnet
  om lag 20 tekstfeil i håndskrevet tekst, og 80 kommuner kan ikke kontrolleres manuelt.
- Hullene merkes med årsak i figuren, slik at linjen brytes og ikke trekkes over et
  manglende år.

## Fase 5 — Fylke, landsdel og kart

- Et panel på fylke.html og nord-norge.html.
- Fire kartindikatorer: ledighet, AAP, nedsatt arbeidsevne og uføre (NAV).
- Kontantstøtte vises bare på fylkesnivå og landsdelsnivå, fordi kommunetallene for det
  meste er prikket.

## Fase 6 — Kvalitetskontroll og publisering

- `tools/sjekk_layout.py`, `tools/sjekk_funn.py`, bygg, forhåndsvisning på mobil og i mørkt
  tema.
- Metodesiden får et avsnitt om kilder, brudd og prikking.
- Commit og deploy etter godkjenning.

## Beslutninger

1. **Uføreandel i nøkkeltallene (avgjort 20. november 2026).** SSB 11715 beholdes i
   nøkkeltallene. NAV vises som tidsserie med en forklaring av forskjellen.
2. **Delte kommuner (avgjort 20. november 2026).** Ingen fordeling. Der NAV selv har regnet
   om tidligere år til dagens inndeling, brukes NAVs tall (Narvik og Hamarøy fra desember
   2018 for uføre, 2016 for pensjon). Ellers er det brudd før 2020.
3. **Omfang (avgjort 20. november 2026).** Minstepensjon er med i første runde, og andelen
   med alderspensjon står bare i tabellen. Sykefravær tas i en egen runde (se nedenfor).

## Senere runde — sykefravær per kommune

NAV har ikke kommunetall for sykefravær (SYFRA510 er fylkestall). Kommunetallene må hentes
fra SSB via FHI (tabell 826, som ble brukt for Lødingen). Det krever eget innhentingsskript,
egne regler for prikking og egen kontroll, og anslås til 40–60 verktøykall. Tema 12 viser
allerede sykefravær blant ansatte i kommunal omsorg. Det er et annet mål, og de to må merkes
slik at de ikke forveksles.

## Overslag over arbeidsmengde

Overslaget er usikkert. Det bygger på antall verktøykall i Lødingen-arbeidet og
dashbordarbeidet, ikke på en måling. Det eksakte forbruket i Lødingen-økten er ikke målt.

| Fase | Verktøykall | Agenttid |
|---|---|---|
| 1 Uttrekk og nøkkel | 55–90 | 2–3,5 t |
| 2 Kontroll | 35–55 | 1,5–2 t |
| 3 Dataformat | 10–20 | 0,5 t |
| 4 Kommunesiden | 55–90 | 2–3,5 t |
| 5 Fylke, landsdel, kart | 25–40 | 1–1,5 t |
| 6 Kontroll og publisering | 30–40 | 1–1,5 t |
| **Sum** | **210–335** | **8–12,5 t** |

Minstepensjon og alderspensjon er tatt med i tallene (anslagsvis 15–25 kall). Sykefravær
kommer i tillegg.

- **Tokens:** hvert kall leser hele konteksten på nytt, som i snitt er 150–250 000 tokens i
  dette repoet, fordi app.js alene har 2 932 linjer. Det gir om lag 30–70 millioner
  inndatatokens, for det meste fra hurtigbuffer, og 0,5–1 million utdatatokens. Med
  minstepensjon blir det trolig nærmere den øvre delen av intervallet.
- **Plangrense:** trolig to til fire femtimersvinduer på Max. Arbeidet bør deles i tre til
  fire økter, med faseskille etter fase 2 og etter fase 4.
- **Halvards egen tid:** tre beslutninger og gjennomlesing av kontrollrapporten og den
  ferdige siden, om lag 1–2 timer.
