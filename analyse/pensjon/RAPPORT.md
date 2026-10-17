# Kommunale pensjonsforpliktelser i Nord-Norge

Analyse av de 80 kommunene i Nordland, Troms og Finnmark. Fase 1–4 utført 16.–17. oktober 2026.
I dashbordet: temasiden `tema-pensjon.html`, Økonomi-fanen på kommune-, fylkes- og landsdelssidene og
metodesiden. Datablokken `PENSJON_DATA` bygges med `python fetch_pensjon.py` fra rotmappen.

## Konklusjon

De 80 kommunene har 6,1 mrd. kr i premieavvik som ennå ikke er utgiftsført. Det tilsvarer 8,9 % av
brutto driftsinntekter (BDI), mot 8,7 % for landet. Troms ligger høyest med 11,4 %. Pensjonsordningene er
fullt finansiert samlet sett: forpliktelsen er 87,0 mrd. kr og midlene 88,0 mrd. kr.

Den regnskapsførte pensjonskostnaden er 7,3 % av BDI i 2025. I basisscenariet holder den seg mellom 7,2 og 7,4 %
fram mot 2033 og stiger til 7,9 % i 2050. Spennet i 2050 er 6,1–11,5 % av BDI. Den største risikoen er
premiefondet, ikke etterslepet: hvis KLPs overskudd ikke lenger dekker like mye av premien, øker
premieinnbetalingen med opptil 2,6 % av BDI fra 2027. Det gir likviditetsproblemer samme år og nytt
premieavvik som skal utgiftsføres de sju neste årene.

## Fase 1 — regelverk og metode

- **Hjemmel.** Budsjett- og regnskapsforskriften §§ 3-5 og 3-6.
- **Premieavvik.** Premieavvik er premie minus netto pensjonskostnad, inkludert arbeidsgiveravgift.
  Det balanseføres og amortiseres over 7 år (fra 2014), eller over 1 år hvis kommunestyret vedtar det.
  Eldre avvik amortiseres over 10 år (2011–2013) og 15 år (2002–2010); 15-årslagene er ferdige i 2025.
- **Forholdstallet.** KDD fastsetter forholdstallet, som i praksis er realrenten:
  - 1,0 for 2025 (H-3/25)
  - 0,88 for 2026 (H-4/25)
  - 0,75 for 2027 (H-2/26)

  Et lavere forholdstall gir høyere beregnet kostnad, slik at kostnaden nærmer seg premien.
- **Kompensasjon.** Fra 2026 kompenseres pensjonsveksten gjennom den kommunale deflatoren: −0,9
  prosentpoeng i 2026 og +0,5 i 2027 (Prop. 1 S (2026–2027)). Kommunene får dermed ikke dekket
  økningen krone for krone.
- **Nye ytelser.** Ny livsvarig AFP og nye særaldersregler ble tatt inn i beregningene fra 2025. Det ga
  store planendringer i 2025-notene, blant annet Vestvågøy 98,8, Meløy 82,5, Saltdal 72,1 og
  Nordreisa 58,9 mill. kr.
- **Nasjonale tall.** Akkumulert premieavvik er om lag 63 mrd. kr, og premiefondene i kommunesektoren er
  over 45 mrd. kr (Prop. 94 S (2025–2026)).

Kildenotater: `regelverk/kildenotater.md`.

## Fase 2 — organisering

| Leverandør | Kommuner | Merknad |
|---|---|---|
| Egen kommunal pensjonskasse | Bodø, Tromsø, Harstad | Solvenskapitaldekning 150–159 % (2025); alle har fått kapitalinnskudd fra kommunen |
| KLP (fellesordningen og sykepleiere) | 77 | Solvenskapitaldekning 324 % (2. kvartal 2026); utjevning mellom ca. 330 kommuner |
| SPK (lærere) | alle 80 | Ufondert; staten bærer avkastnings- og reguleringsrisikoen |

Ingen nord-norske kommuner er i Storebrand. Om lag 2 500 kunder eier KLP. Eierne betaler et årlig
egenkapitaltilskudd på 0,25 % av premiereserven, og KLP kan kalle inn kapital opp til 2,5 % av
premiereserven. Reguleringspremien var 4,6 % av premiereserven i 2025 og ligger an til om lag 5,1 % i 2026.

Kildenotater: `organisering/01_kilder_nasjonalt.md`, `02_klp.md`, `03_nn_kasser.md`, `04_spk_nasjonalt.md`.

## Fase 3 — tall fra årsregnskapene 2025

- **Grunnlag.** 74 av 80 kommuner har pensjonsnote fra årsregnskapet for 2025.
- **Mangler.** Seks kommuner bygger bare på KOSTRA:
  - Målselv, Lyngen, Kåfjord, Balsfjord og Andøy (regnskapet står bak en botsjekk)
  - Berlevåg (regnskapet er ikke publisert)
- **Overstyringer.** Postene i `manuelle/` overstyrer agentpostene for Lavangen, Porsanger, Nordkapp,
  Salangen, Sørreisa, Storfjord og Skjervøy.

| Område | Premieavvik 2025 | Andel av BDI 2025 | 2024 |
|---|---:|---:|---:|
| Nordland (41) | 2,58 mrd. kr | 7,7 % | 9,4 % |
| Troms (21) | 2,58 mrd. kr | 11,4 % | 13,2 % |
| Finnmark (18) | 0,92 mrd. kr | 7,7 % | 8,9 % |
| Nord-Norge (80) | 6,08 mrd. kr | 8,9 % | |

Funn:

- **Funn 01 — beholdningen krympet i 2025.** Det kom 0,65 mrd. kr i nytt premieavvik, mens 1,41 mrd. kr
  ble amortisert (n=74).
- **Funn 02 — premiefondene ble brukt mye.** 67 kommuner brukte tilsammen 2,5 mrd. kr. Narvik brukte
  233,9 mill. kr og Rana 200,5 mill. kr.
- **Funn 03 — pensjon veier tyngre i nord.** Regnskapsført pensjon utgjorde 12,9 % av lønn i Finnmark,
  12,2 % i Troms og 11,9 % i Nordland, mot 11,2 % for landet.
- **Funn 04 — svak buffer.** Premieavviket er større enn disposisjonsfondet i 48 av 80 kommuner.
- **Datakvalitet.** Om lag hver tredje note har interne avvik; der note og balanse er uenige, er
  balansen brukt. Om lag 20 noter er lest av sidebilder. Sju noter har utdaterte forutsetninger
  (Grane, Vefsn og Kvæfjord bruker 3,5 % diskonteringsrente). Reguleringspremien er oppgitt i bare 3 noter.

## Fase 4 — fremskriving 2026–2050

### Brutto driftsinntekter (BDI)

BDI er summen av kommunekonsernets driftsinntekter i ett år (SSB 12364, art AGD13). Finansinntekter,
bruk av fond og lån er ikke med.

| Inntektspost (andel av BDI, 2025) | Nord-Norge | Landet |
|---|---:|---:|
| Rammetilskudd | 33,5 % | 29,9 % |
| Inntekts- og formuesskatt | 27,6 % | 36,0 % |
| Overføringer fra andre (refusjoner m.m.) | 14,2 % | 12,3 % |
| Salgs- og leieinntekter | 11,5 % | 12,0 % |
| Andre statlige overføringer (øremerket) | 6,3 % | 4,3 % |
| Eiendomsskatt | 3,4 % | 2,7 % |
| Brukerbetalinger | 2,9 % | 2,5 % |

BDI er 68,3 mrd. kr for de 80 kommunene og 674,2 mrd. kr for landet (2025).

BDI er standardnevneren i KOSTRA og i normene for netto driftsresultat, gjeld og fond. Svakheter:

- Om lag 20 % av BDI er øremerket eller refusjoner. Målt mot frie inntekter, som er 61 % av BDI, blir
  pensjonsandelen om lag 1,6 ganger høyere.
- Engangsinntekter kan gi hopp i andelen.
- Troms og Finnmark har tall bare fra 2024, etter regionreformen.
- Modellen antar at BDI og lønn vokser like raskt.

### Modell (`fase4_modell.py`)

Per kommune og år:

- regnskapsført pensjonskostnad R = netto kostnad K × (1 + AGA) + amortisering A
- premie P = K × (1 + γ) + premiefondsbortfall
- nytt premieavvik N = (P − K) × (1 + AGA)
- akkumulert premieavvik S(t) = S(t−1) + N − A

Forutsetninger:

- **Amortisering.** Beholdningen for 2025 amortiseres med lineært fallende beløp over sju år fra 2026. Første
  års beløp er kalibrert mot kommunens observerte amortisering i 2025, avgrenset til mellom 1/7 og 1/4 av
  beholdningen. Nye lag amortiseres med 1/7 per år fra året etter. Kommuner med 1-årsregel amortiserer hele
  avviket året etter.
- **γ (premie over kostnad).** γ = 21,0 % (Nord-Norge 2025, n=72). Den normaliserer premien slik at
  enkeltkommuners premiefondsbruk i 2025 ikke følger med inn i framtiden.
- **Vekst.** Lønn og BDI vokser nominelt med 3,5 % per år.
- **Kalibrering.** Modellen gir 7,3 % av BDI i 2025. Den faktiske pensjonsposten i KOSTRA (art 090 med
  AGA) er 7,1 %.

| Forutsetning | Lav | Basis | Høy |
|---|---|---|---|
| Kostnadsøkning ved forholdstall 0,75 (2027) | +5 % | +10 % | +21 % (kostnad = premie) |
| Strukturell vekst fra 2028 | 0 % | 0,5 %/år | 1,0 %/år |
| Premiefondets dekning fra 2027 (2025 = 100 %) | 100 % | 75 % | 25 % |

### Resultater: regnskapsført pensjonskostnad i % av BDI (basis, lav–høy)

| | 2025 | 2030 | 2033 | 2040 | 2050 |
|---|---|---|---|---|---|
| Nord-Norge | 7,3 | 7,4 (6,7–8,8) | 7,2 (6,1–9,4) | 7,6 (6,1–10,4) | 7,9 (6,1–11,5) |
| Nordland | 7,1 | 7,4 (6,6–9,0) | 7,4 (6,1–9,9) | 7,8 (6,1–11,0) | 8,2 (6,1–12,1) |
| Troms | 7,6 | 7,4 (6,8–8,6) | 7,0 (6,0–8,9) | 7,3 (5,9–9,8) | 7,7 (5,9–10,8) |
| Finnmark | 7,2 | 7,3 (6,6–8,5) | 7,1 (6,1–9,0) | 7,4 (6,1–9,9) | 7,8 (6,1–11,0) |

Pensjonspremien utgjorde 6,2 % av BDI i 2025. I 2030 er den 6,2 % (lav), 7,4 % (basis) eller 10,0 % (høy).

Funn:

- **Funn 06 — amortiseringen er ikke en ny utgift.** Den ligger allerede i dagens kostnad, om lag 2 % av
  BDI. Etterslepet er nedbetalt rundt 2032 og avlaster driften fra da.
- **Funn 07 — premiefondet er den største risikoen.** Premiefondsbruken i 2025 var like stor som netto
  kostnad (median 1,04 ganger). Med 25 % dekning øker premien med om lag 2,6 % av BDI fra 2027.
- **Funn 08 — varig økning for mange.** 31 kommuner får mer enn ett prosentpoeng høyere andel fra 2025 til
  2050 i basis. Høyest i 2050 ligger Bø (11,3 %), Kvæfjord (10,4 %) og Kåfjord (10,0 %).
- **Funn 09 — risikogruppen.** 13 kommuner har premieavvik over 10 % av BDI og mindre disposisjonsfond
  enn premieavvik: Sørreisa, Saltdal, Hamarøy, Hammerfest, Målselv, Salangen, Vevelstad, Harstad, Tromsø,
  Sortland, Kautokeino, Senja og Steigen.

### Usikkerhet

1. **2026–2027 avviker fra TBU.** TBUs pensjonsbidrag (−0,9 / +0,5 prosentpoeng) tilsier at kostnaden
   faller i 2026 og stiger i 2027. Modellen gir en svak økning i 2026. Avviket skyldes trolig avkastningen
   i 2025. Kalibrer mot kommunenes budsjetter for 2026, som bygger på KLPs prognoser.
2. **Premiefondets dekning** er en forutsetning, ikke en prognose.
3. **Svakt grunnlag.** Hamarøy og Lurøy har noter som ikke går opp. Seks kommuner bygger bare på KOSTRA.

## Filer

| Fil | Innhold |
|---|---|
| `kommuner.json` | De 80 kommunene i fire grupper |
| `SKJEMA.md` | Skjema for uttrekk av pensjonsnoter |
| `regnskap_gruppe1–4.json`, `rec*/` | Poster fra årsregnskapene (agenter) |
| `manuelle/` | Manuelt leste poster; overstyrer gruppefilene |
| `hent_kostra_pensjon.py` → `kostra_pensjon.json` | SSB 13202 og 12143: pensjonsposter i balansen, BDI |
| `hent_kostra_drift.py` → `kostra_drift.json` | SSB 12367: pensjon (art 090), AGA og lønn |
| `hent_kostra_bdi.py` → `kostra_bdi.json` | SSB 13551 og 12364: BDI-sammensetning, disposisjonsfond |
| `kostra_13545.json` | SSB 13545: kommunekasse |
| `fase3_samlet.json` | Sammenstilling for fase 3 |
| `fase4_modell.py` → `fase4_resultat.json` | Modellen og alle år, scenarier og kommuner |
| `fase4_kommuner.csv` | Nøkkeltall per kommune (semikolonseparert) |
| `regelverk/`, `organisering/` | Kildenotater; kildedokumentene ligger lokalt, utenfor git |
| `pdf/`, `bilder/` | Nedlastede regnskap og sidebilder; lokalt, utenfor git |

Kjør modellen på nytt med `python fase4_modell.py` og tabellen med `python lag_tabell.py` fra denne mappen,
eller `python fetch_pensjon.py` fra rotmappen for å oppdatere dashbordet.
