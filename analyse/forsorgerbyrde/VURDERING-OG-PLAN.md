# Forsørgerbyrden: hva vi måler, hva vi bør få fram, og plan

**Status 21. oktober 2026: gjennomført** (fase 0–5). Avvik fra planen: dataene ligger i en egen blokk `FORSORG_DATA` (`fetch_forsorg.py`) i stedet for i `ARBEID_DATA`; sysselsettingsratene er gjennomsnitt av 2024 og 2025 (2023 har gamle kommunenummer i Troms og Finnmark), og 75+ er tatt med fra SSB 13563, slik at framskrivingen starter nær dagens tall (Nord-Norge 92,5 mot 92,2); scenarioene vises som en fast tabell. Analyseskriptene ligger i `skript/` (leser bufrede SSB-uttrekk; kjør `fetch_forsorg.py` for dashbordtallene).

21. oktober 2026. Grunnlag: gjennomgang av alle steder dashbordet omtaler forsørgerbyrde (kommunesiden, landsdels- og fylkessiden, tema 04, 05 og 06, kart, sammenligning og metode), og egne beregninger fra SSB 13563, 07984, 07459 og 14746 for de 80 kommunene og landet. Ingen kode er endret.

## Konklusjon

Dashbordet bruker i hovedsak den demografiske forsørgerbrøken: personer 65 år og over per 100 i alderen **20–64** (ikke 20–74). Den teller alle i alderen 20–64 som «bærere», også uføre, mottakere av arbeidsavklaringspenger, studenter og ledige, og alle over 65 som «båret», også de som jobber. Det er riktig å beholde den som hovedtall for sammenligning, fordi SSB (14751) og OECD bruker den. Men den skal omtales som det den er, et aldersmål, og den bør suppleres med et mål som teller faktisk arbeid.

Det som bør fram, er at **måten man teller på endrer konklusjonen**. Etter alder ligger Nord-Norge 15 % over landet. Teller man alle som ikke er i arbeid mot dem som er det, ligger Nord-Norge litt *under* landet i dag. Grunnen er at sysselsettingen i alderen 20–66 er like høy som i landet, og at færre er barn og studenter. Uføre og mottakere av arbeidsavklaringspenger veier tyngre i nord, men pensjonistene veier enda tyngre. Mot 2050 stiger begge målene nesten likt i Nord-Norge og i landet. Forskjellen er at antallet sysselsatte faller i nord og øker i landet. **Utfordringen i nord er færre hender, ikke flere å forsørge per hånd.**

Anbefalingen er tre tydelig adskilte mål, forklart med ett felles bilde: «Hvem bærer hvem?».

## Hva dashbordet gjør i dag

| Sted | Mål | Merknad |
|---|---|---|
| Kommunesiden, Arbeid-fanen og framskrivingsgrafen | 65+ per 100 i alderen 20–64 (SSB 14746) | Nøkkeltallet heter «65+ per 100 yrkesaktive». *Yrkesaktive* betyr i arbeid; målet gjelder alder. |
| Kommunesiden, seksjon 3 (sammendrag) | Samme | Merket «eldre per 100 i jobb». Feil: målet teller ikke hvem som er i jobb. |
| Landsdels- og fylkessiden, «Bæreevne» | 65+ / (20–64 × sysselsettingsrate 20–66) | Egen konstruksjon som ingen kilde bruker. Den blander to aldersspenn, holder sysselsettingen fast mot 2050 uten å si det, fjerner uføre og ledige fra nevneren uten å legge dem til i telleren, og ser bort fra at 30 177 personer over 62 år i Nord-Norge er i arbeid. Gir 48,7 for Nord-Norge i dag. |
| Tema 04, tema 05, kart, bærekraftstabell, sammenligning | 65+ per 100 i alderen 20–64 | Riktig definert. Tema 04 kaller 65+ «pensjonister»; pensjonsalderen er 67 og mange over 65 jobber. |
| Omvisningen (akt 2.2) | «Eldre per 100 yrkesaktive vokser fra ~30 til ~50» | For Nord-Norge er tallet 38 i dag. |

Uføreandelen (SSB 11715, 18–67 år) og sysselsettingsraten (SSB 13563, 20–66 år) vises som egne nøkkeltall på kommunesiden, men inngår ikke i forsørgerbyrden.

## Funn

**Funn 01 — Demografisk ligger Nord-Norge klart over landet.** Observasjon (1.1.2026, SSB 07459):

| | Nord-Norge | Landet |
|---|---:|---:|
| 65+ per 100 i alderen 20–64 | 37,6 | 32,8 |
| 67+ per 100 i alderen 20–66 (norsk pensjonsalder) | 32,2 | 28,0 |
| (0–19 + 65+) per 100 i alderen 20–64 | 73,5 | 70,2 |

**Funn 02 — Teller man faktisk arbeid, ligger Nord-Norge litt under landet.** Observasjon: Personer som ikke er sysselsatt, per 100 sysselsatte (alle aldre, bosted, 4. kvartal 2025 og 1.1.2026, SSB 13563 og 07459), fordelt på hvorfor:

| Per 100 sysselsatte | Nord-Norge | Landet |
|---|---:|---:|
| Barn 0–14 år | 28,2 | 30,8 |
| Under utdanning | 7,9 | 9,8 |
| Arbeidsavklaringspenger og uføretrygd | 13,1 | 12,3 |
| AFP og alderspensjon | 32,8 | 29,5 |
| Registrerte ledige og på tiltak | 3,0 | 3,3 |
| Andre utenfor arbeid | 6,9 | 7,9 |
| **I alt** | **92,2** | **93,8** |

Grunnen er at sysselsettingsraten i alderen 20–66 er 77,2 % i Nord-Norge mot 76,7 % i landet, og at det er færre barn og studenter. Delsummene avviker 0,2–0,3 fra totalen fordi befolkningen er talt 1.1.2026 og statusene i 4. kvartal 2025.

**Funn 03 — Uføretrygd og arbeidsavklaringspenger veier tyngre i nord.** Observasjon: 11,3 % av befolkningen i alderen 20–66 i Nord-Norge mottar arbeidsavklaringspenger eller uføretrygd, mot 10,3 % i landet. Med landets andel ville om lag 2 800 færre i landsdelen stått utenfor arbeid av denne grunnen (SSB 13563, 2025). Variasjonen mellom kommunene er stor: Gratangen 18,3 %, Kvænangen 17,9 % og Dyrøy 17,7 %.

**Funn 04 — Mot 2050 stiger byrden nesten likt; antallet hender er forskjellen.** Hypotese: Dersom sysselsettingsraten i hver aldersgruppe holdes som i 2025 (SSB 07984, seks aldersgrupper), og befolkningen følger SSBs hovedalternativ, forventer vi:

| | 2026 | 2030 | 2040 | 2050 |
|---|---:|---:|---:|---:|
| Nord-Norge, demografisk | 37,6 | 40,7 | 49,3 | 51,1 |
| Nord-Norge, ikke-sysselsatte per 100 sysselsatte | 94,6 | 97,0 | 105,8 | 109,7 |
| Nord-Norge, sysselsatte | 251 710 | 249 669 | 239 365 | 232 856 |
| Landet, demografisk | 32,8 | 35,1 | 42,3 | 47,0 |
| Landet, ikke-sysselsatte per 100 sysselsatte | 95,9 | 97,1 | 103,7 | 110,1 |

Antallet sysselsatte i Nord-Norge faller med 7,5 %, mens det øker med 2,7 % i landet. Overslaget bruker 15–74 år; derfor er 2026-tallet litt høyere enn i funn 02.

**Funn 05 — Kommunene rangeres ulikt på de to målene.** Observasjon: Korrelasjonen over de 80 kommunene er 0,70. Kommuner med lav sysselsetting og mange uføre går opp på det økonomiske målet: Leirfjord fra plass 45 til 3, Nesna fra 55 til 9, Hasvik, Gamvik og Øksnes fra plass 60–68 til 22–29. Kommuner med mange eldre som er i arbeid, går ned: Røst fra plass 30 til 79, Steigen, Hattfjelldal og Lyngen. Tyngst økonomisk er Lavangen (130,9), Dyrøy (128,7), Leirfjord, Bindal og Lødingen. Lettest er Tromsø (73,4), Røst, Nordkapp, Træna og Bardu.

**Funn 06 — Det økonomiske målet har egne svakheter.** Det teller et barn, en pensjonist og en uføretrygdet likt, selv om de koster svært ulikt og finansieres ulikt (kommunen, folketrygden, familien). En sysselsatt er en som har arbeidet minst én time i referanseuka, så deltid teller som en hel. Små kommuner gir store tilfeldige utslag. Målet kan derfor ikke erstatte det demografiske, bare utfylle det.

**Funn 07 — En kodefeil i navnevisningen (utenfor denne saken).** Observasjon: `navnK` på tema 01 og tema 05 tar siste ledd i kommunenavnet. For Lyngen, Kåfjord, Gratangen og Hammerfest gir det det samiske eller kvenske navnet. Det vises ikke i dag fordi ingen av disse kommunene er nevnt der, men det bør erstattes med `kortNavn` fra `src/lib/format.js`.

## Datagrunnlag

| Kilde | Innhold | Nivå | Bruk |
|---|---|---|---|
| SSB 14746 | Befolkning etter ettårig alder, 2026–2050, MMMM | Kommune | Begge mål, framskriving (finnes) |
| SSB 14751 | Forsørgerbrøk 65+/20–64 | Kommune, fylke, landet | Kontroll av det demografiske målet |
| SSB 13563 | Prioritert arbeidsstyrkestatus: sysselsatt, ledig, tiltak, utdanning, AAP og uføretrygd, AFP og alderspensjon, andre; for 15+, 20–66, 15–29, 30–61 og 62+ | Kommune, 2008–2025 | Fordelingen i funn 02 og 03. Brukes i dag bare for 20–66 og siste år. |
| SSB 07984 og 06445 | Sysselsatte og sysselsettingsrate etter seks aldersgrupper (15–19 … 67–74) og kjønn | Kommune, 2008–2025 | Framskriving i funn 04 |
| SSB 07459 | Befolkning 1. januar etter alder | Kommune | Barn 0–14 og nevnere |
| SSB 11715 | Uføretrygdede 18–67 år | Kommune | Finnes; uføretrygd alene, uten arbeidsavklaringspenger |

Alle tabellene er åpne og har tall for de 80 kommunene med 2024-koder for 2025. Seriene for sysselsetting er sammenlignbare fra 2015.

## Plan

### Fase 0 — Rette ordbruken (liten, kan gjøres først)

- «yrkesaktive» erstattes med «i alderen 20–64» der målet er alder. Det gjelder kommunesiden, sammendraget i seksjon 3, temasidene og omvisningen.
- «eldre per 100 i jobb» rettes.
- «pensjonister» brukes ikke om 65+.
- Omvisningens «~30 til ~50» erstattes med tall fra dataene.
- Navnefeilen i funn 07 rettes.

### Fase 1 — Data (`fetch_arbeid.py` utvides → `ARBEID_DATA`)

1. SSB 13563 per kommune, fylke, landsdel og landet, 2015–2025:
   - alle statuskategorier for 15+ og 20–66
   - sysselsatte for 62+
2. SSB 07984: sysselsatte bosatte etter seks aldersgrupper, gjennomsnitt 2023–2025 for å dempe tilfeldige utslag i små kommuner.
3. Framskriving 2026–2050 per kommune (beregnet i Python, ikke i nettleseren):
   - begge målene i grunnbanen
   - to scenarioer: (a) andelen på arbeidsavklaringspenger og uføretrygd senkes til landsnivå der den er høyere, (b) 5 prosentpoeng høyere sysselsetting i alderen 55–74
4. Kontroller i skriptet:
   - statuskategoriene summerer til total
   - det demografiske målet stemmer med SSB 14751 (avrundet)
   - landsdelen stemmer med summen av kommunene
   - funn 02 og 04 gjenskapes

### Fase 2 — Forklaringen og kommunesiden

- **Metodekort `#forsorgerbyrde`** med de tre målene, definisjoner, kilder og forbehold, og eksempelet fra funn 01 og 02.
- **Kort «Hvem bærer hvem?»** i Arbeid-fanen på kommunesiden:
  - **100 personer i alderen 20–66 som prikker**, fargelagt etter status: i arbeid, AAP og uføretrygd, utdanning, ledige og tiltak, pensjon, andre. Nord-Norge og landet vises ved siden av. Dette er det pedagogiske hovedgrepet: man ser hvor mange som faktisk bærer.
  - **Stablet stolpe** «per 100 sysselsatte forsørges …» (funn 02) for kommunen, landsdelen og landet.
  - **Nøkkeltall:**
    - demografisk mål i dag og i 2050, merket «per 100 i alderen 20–64»
    - økonomisk mål i dag og i 2050
    - andelen på AAP og uføretrygd mot landet
  - **Linjediagram 2026–2050** med begge målene, indeksert til 2026, så det synes at de beveger seg ulikt.
  - **Scenariobrytere** for (a) og (b), med effekten i 2050 i tekst: «Med landets uføreandel ville … ».
  - **Tekst** som skiller observasjon og hypotese, og som sier fra når tallene er usikre fordi kommunen er liten.

### Fase 3 — Landsdel, fylker og temasider

- **Landsdels- og fylkessiden:** dagens «justerte» mål erstattes av det økonomiske målet med samme kort som på kommunesiden. Den demografiske grafen beholdes.
- **Tema 04 «Hvem skal bære?»:** ny akt **«Tre måter å telle på»**:
  - samme befolkning, tre mål og tre svar
  - Nord-Norge-paradokset fra funn 02 og 04
  - kommunene som bytter plass (funn 05)
  - scenarioene
- **Tema 05:** OECD-sammenligningen beholdes demografisk, med en setning om hvorfor og en lenke til tema 04.

### Fase 4 — Kart og sammenligning

- Skjulte kartindikatorer:
  - «Ikke-sysselsatte per 100 sysselsatte»
  - «AAP og uføretrygd, andel 20–66»
  - «Endring i sysselsatte 2026–2050»
- Nye rader på sammenligningssiden og i bærekraftstabellen.

### Fase 5 — Verifisering

- Tall i tekst kontrolleres mot `tools/fasit.cjs`.
- Siden kontrolleres i mørkt og lyst tema, på desktop og mobil.
- Produksjonen kontrolleres etter publisering.

## Valg som må tas

01. **Behold 65+/20–64 som hovedtall for sammenligning.** Begrunnelse: Det er SSBs og OECDs mål og det eneste som kan sammenlignes over land og fylker.
02. **Innfør det økonomiske målet som tilleggsmål, med fordeling på årsak.** Begrunnelse: Det er bare dette målet som viser uføretrygd, arbeidsavklaringspenger og faktisk sysselsetting.
03. **Fjern dagens «justerte» mål.** Begrunnelse: Det er en egen konstruksjon uten kilde, og det teller uføre og ledige inkonsekvent.
04. **To faste scenarioer, ikke fri glidebryter.** Begrunnelse: Faste scenarioer er etterprøvbare og enklere å forklare.
05. **67+/20–66 vises bare i forklaringen.** Begrunnelse: Det følger norsk pensjonsalder, men finnes ikke i SSBs eller OECDs tabeller.
06. **Navn på målene:** «forsørgerbrøk» (SSBs eget ord) for aldersmålet og «ikke-sysselsatte per 100 sysselsatte» for det økonomiske. Begrunnelse: Navnet sier hva som telles.

Grunnlag: SSB 13563 (4. kvartal 2025), 07984 (4. kvartal 2025), 07459 (1.1.2026), 14746 (MMMM, 2026–2050), 14751; n = 80 kommuner og landet. Beregningsskriptene ligger i `analyse/forsorgerbyrde/skript/`.
