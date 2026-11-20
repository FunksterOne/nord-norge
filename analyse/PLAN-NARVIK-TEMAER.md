# Plan: sysselsetting, pendling, næringsliv og skatteinngang i dashbordet

Status: plan, ikke påbegynt (20. november 2026). Grunnlag: rapporten «Narvik mot 2030, 2036
og 2050» (Affectum, 19. november 2026, 12 sider, 17 kildetabeller). Rapporten er bygd på tall
fra dashbordet, supplert med seks SSB-tabeller som dashbordet ikke henter i dag.

## Konklusjon

Om lag to tredeler av rapportens grunnlag finnes allerede i dashbordet. Fire tillegg er verdt å
gjøre, og alle kan lages for alle 80 kommuner med samme metode:

1. **Skatteinngang per måned** (SSB 07022). Dette er det eneste ferske månedstallet for
   kommuneøkonomien, og det går til oktober 2026.
2. **Skatt, utjevning og frie inntekter per innbygger** (SSB 12137, KOSTRA). Tallene viser
   hvordan lav skatt per innbygger jevnes ut.
3. **Pendling inn og ut** (SSB 03321). Tabellen gir pendlingsstrømmer mellom alle kommuner
   2000–2025.
4. **Arbeidsstyrkestatus som tidsserie 2020–2025** (SSB 13563). Tabellen er i bruk i dag, men
   bare for siste år.

Bedrifter, nyetableringer og konkurser (07091, 13701, 07165) gir mindre per kommune, fordi
tallene er små og svinger mye. De bør komme sist, eller bare på fylkes- og landsdelsnivå.

## Hva som finnes i dashbordet i dag

Kontrollert 20. november 2026 ved å søke etter tabellnumrene i `fetch_*.py`:

| Rapportens tall | Tabell | I dashbordet |
|---|---|---|
| Folketall og alder | 07459 | ja |
| Fødte, døde | 06913 | ja (fetch_ung.py) |
| Flytting, inn- og utvandring | 09588 | ja (fetch_flows.py, fetch_refugee.py) |
| Framskriving, tre alternativer | 14746 | ja (MMMM, LLML, HHMH) |
| Framskriving, ni alternativer | 14746 | nei, bare tre av ni |
| Landbakgrunn (ukrainskfødte) | 09817 | ja (kommunesiden, ukr-bryteren) |
| Sysselsetting, AAP og uføre, registrert ledige | 13563 | ja, men bare siste år |
| Sysselsatte «alt annet likt» | 07984 + 14746 | ja (fetch_forsorg.py) |
| Arbeidsplasser etter næring | 07984 / 13470 | delvis: 13470 siste år, uten endring siden 2020 |
| Pendling | 03321 | **nei** |
| Bedrifter etter størrelse | 07091 | **nei** |
| Nyetablerte foretak | 13701 | **nei** |
| Konkurser | 07165 | **nei** |
| Skatt, rammetilskudd, frie inntekter, eiendomsskatt per innbygger | 12137 | **nei**. Frie inntekter finnes fra 12134 |
| Skatteinngang per måned | 07022 | **nei** |
| Driftsresultat, fond, gjeld | 12134 / 12143 | ja |
| Pensjon og premieavvik | 13202, 12364 | ja |
| Eldreomsorg, årsverk, demens | 14534, 14746 | ja |
| NAVs bedriftsundersøkelse | – | ja (fylkesnivå) |

De seks nye tabellene er kontrollert mot SSBs API 20. november 2026. Alle har tall per kommune
(også 1806 Narvik og 5501 Tromsø). Siste perioder:

- 07022: oktober 2026
- 12137: 2025
- 03321: 2025, med serie fra 2000
- 07091: 2026
- 13701: 2024
- 07165: 3. kvartal 2026

Rapporten sier at 13701 bare har kommunetall til 2023, mens tabellen går til 2024. Om 2024 har
tall per kommune, må kontrolleres.

## Pakke A — Skatt og kommuneøkonomi (anbefalt først)

**A1. Skatteinngang hittil i år (07022).**

- **Innhold:** «Ordinær skatt til primærkommunen», akkumulert per måned. Kommunen vises mot
  samme periode i fjor, mot fylket og mot landet.
- **Nøkkeltall:** vekst hittil i år og vekst i fylket.
- **Figur:** akkumulert skatteinngang per måned i år og i fjor.
- **Tekstregel:** veksten sammenlignes alltid med landet. Teksten skal si at skattøre og
  lønnsvekst påvirker tallet, slik rapportens hypotese sier.
- **Plassering:** Økonomi-fanen på kommunesiden, og fylket i tall.
- **Oppdatering:** hver måned. Skriptet tar siste måned automatisk.

**A2. Skatt og utjevning per innbygger (12137).**

- **Innhold:**
  - skatt på inntekt og formue
  - rammetilskudd
  - frie inntekter
  - eiendomsskatt
- **Sammenligning:** alt i kroner per innbygger 2015–2025, og i prosent av landet og av
  landet utenom Oslo.
- **Figur:** stablet stolpe «skatt + rammetilskudd = frie inntekter» for kommunen og landet.
- **Konflikt med dagens tall:** dashbordet henter frie inntekter fra 12134 i dag. Før
  innføring må det avgjøres hvilken tabell som gjelder, og forskjellen må kontrolleres for
  alle 80 kommuner.
- **Plassering:** Økonomi-fanen, og kart over skatt per innbygger i prosent av landet.

## Pakke B — Arbeid og pendling

**B1. Pendling (03321).**

- **Nøkkeltall:** utpendlere, innpendlere og netto, og andelen av de sysselsatte, 2020 og 2025.
- **Figurer:** de fem største strømmene inn og ut som liggende stolper, og tidsserien for
  utpendling og innpendling.
- **Teksten** skal skille bosted fra arbeidssted, og si at skatten følger bostedet.
- **Kart:** kartlag for netto pendling i prosent av sysselsatte bosatte. Kartet kan senere
  utvides med pendlingsstrømmer mellom kommunene.
- **Datamengde:** 03321 er en matrise mellom alle kommunene. Uttrekket begrenses til strømmer
  der minst én side er en av de 80 kommunene, og lagres per kommune i `data/pendling/<nr>.json`
  som lastes ved behov, på samme måte som NAV-dataene.
- **Kommunegrenser:** det samme kommunenøkkelproblemet som i NAV-arbeidet. Serien vises
  derfor fra 2020, som i rapporten, med mindre SSB har regnet om eldre år.

**B2. Arbeidsstyrkestatus 2020–2025 (13563).**

- **Innhold:** utvid `fetch_arbeid.py` og `fetch_forsorg.py` til seks år, med sysselsatt, AAP
  eller uføre, og registrert ledig for 20–66 år.
- **Figur:** tre små tidsserier, kommunen mot landet.
- **Tekstregel:** «med landets andel ville om lag N færre stått utenfor arbeid av helsegrunner»,
  regnet fra tallene. Formuleringen skal være forsiktig, fordi alderssammensetningen ikke er
  justert.
- **Tre mål som må forklares samlet:** dashbordet viser nå tre forskjellige mål for ledighet og
  helserelatert utenforskap:
  - SSB 13563: registrert ledig og AAP eller uføre, 20–66 år, 4. kvartal
  - NAV: helt ledige av arbeidsstyrken, og AAP av 18–66 år
  - SSB 11715: uføre 18–67 år

  For Narvik gir de 13,9 % (AAP og uføre samlet, SSB) mot 4,4 % AAP og 15,0 % uføre (NAV).
  Det trengs en forklaringsboks og et avsnitt på metodesiden, slik at målene ikke blandes.

**B3. Arbeidsplasser etter næring med endring (07984).**

- **Innhold:** utvid næringsfiguren med endring 2020–2025.
- **Prikking:** SSB skjuler fem næringer i Narvik for å skjerme enkeltbedrifter. Prikkede
  næringer skal vises som «skjult», og summen skal hentes fra totalen, slik rapporten gjør.

## Pakke C — Næringsliv (lavest prioritet)

- **07091:** bedrifter etter antall ansatte, 2020–2026.
- **13701:** nyetablerte foretak, registrerte og med aktivitet.
- **07165:** konkurser per år.

Tallene er små i de fleste av de 80 kommunene. Anbefalingen er å vise dem som en enkel tabell i
Næring-delen på kommunesiden, uten kart og uten regelbasert tolkning, og som tidsserie på
fylkes- og landsdelsnivå.

## Pakke D — Framskriving: alle ni alternativer (valgfri)

Hent de seks manglende alternativene fra 14746 og vis tabellen «ni alternativer for 2050». Den
gjør det tydelig hvor mye innvandringen betyr: for Narvik gir MMM0 17 761, mot 19 754 i
hovedalternativet. Bane-doktrinen gjelder fortsatt: MMMM er hovedbanen, og de andre er
følsomhetsalternativer.

## Metodiske avklaringer før start

1. **Frie inntekter.** Skal 12137 eller 12134 være kilden, og stemmer de overens?
2. **Tysfjord.** Rapporten fordeler Tysfjord med 39 % til Narvik for folketall før 2020, og
   befolkningspyramiden gjør det samme. I NAV-arbeidet ble det bestemt å ikke fordele. For
   pendling og næring foreslås det å vise data fra 2020, så spørsmålet ikke oppstår.
3. **Skatteinngang.** Vekst i prosent er lett å feiltolke. Teksten skal alltid ha landet ved
   siden av, og ikke omtale veksten som et mål på aktivitet.

## Beslutninger Halvard må ta

1. **Omfang.** Hvilke pakker skal være med? Anbefalt: A og B, så C og D senere.
2. **Kilde for frie inntekter.** Anbefalt: 12137 i det nye kortet, kontrollert mot dagens 12134.
3. **Pendlingskart.** Bare kartlag (netto pendling) nå, eller også strømmer mellom kommuner?
   Anbefalt: bare kartlag i første runde.

## Overslag

Overslaget er usikkert. Det bygger på erfaringen fra NAV-arbeidet, som brukte om lag 250
verktøykall over seks faser.

| Pakke | Verktøykall | Agenttid |
|---|---|---|
| A1 Skatteinngang | 30–45 | 1,5–2 t |
| A2 Skatt og utjevning | 30–45 | 1,5–2 t |
| B1 Pendling | 50–80 | 2,5–3,5 t |
| B2 Arbeidsstyrkestatus som tidsserie + forklaring av målene | 30–45 | 1,5–2 t |
| B3 Næring med endring | 20–30 | 1 t |
| C Næringsliv | 30–45 | 1,5 t |
| D Ni alternativer | 20–30 | 1 t |
| Felles kontroll, metodeside, publisering | 30–40 | 1,5 t |
| **A + B + felles** | **190–285** | **9–12 t** |
| **Alt** | **240–360** | **11–15 t** |

- **Tokens:** med 150–250 000 tokens kontekst per kall gir A + B om lag 30–70 millioner
  inndatatokens, for det meste fra mellomlager, og 0,5–1 million utdatatokens.
- **Rekkefølge:** A1 → A2 → B2 → B1 → B3 → (C, D). Hver pakke får egen kontroll mot rapportens
  Narvik-tall som regresjonstest, slik Lødingen ble brukt for NAV:
  - skatteinngang 2025: 830,4 millioner kroner
  - skatt per innbygger: 38 363 kroner
  - utpendlere: 1 189
  - AAP og uføre: 13,9 %
