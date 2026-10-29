# Ventetider og pasientrettigheter: kildenotat for `ventetid.csv`

Hentet 29. oktober 2026. Skript: `skript/ventetid.py`. Rådata: `kilder/data/ventetid/` (gitignorert, med `hentelogg.json` som har URL, størrelse og SHA-256 for hver fil).

## Konklusjon

Den offisielle ventelistestatistikken ligger hos FHI (Norsk pasientregister, NPR), ikke lenger hos Helsedirektoratet. Den er åpent tilgjengelig som Excel-filer på FHIs nedlastingsside. Den finnes ikke i FHI Statistikk Open API og ikke hos SSB.

Filene dekker følgende:

| Statistikk | Periode | Nivå |
|---|---|---|
| Ventetid og antall henvisninger | Tertial 2019–2. tertial 2026 og år 2012–2025 | Land, RHF og HF |
| Fristbrudd | Samme perioder | Bare land og RHF |
| Tid til tjenestestart | Tertial 2012–2. tertial 2026 og år 2012–2025 | Land, RHF og HF |
| Passert planlagt tid | Øyeblikkstall april, august og desember 2017–august 2026 | Land, RHF og HF |

Fristbrudd per HF finnes ikke i de åpne filene.

## 1. Kilde

Datakilde og dataansvar: Norsk pasientregister, Folkehelseinstituttet.

Nedlastingsside: <https://www.fhi.no/he/npr/statistikk-npr/nedlasting-av-data/>

Filbase: `https://www.fhi.no/globalassets/dokumenterfiler/helseregistre/npr-kpr/ventetider-for-nedlasting/`

Filene har ikke tabell-ID. Filnavnet er den nærmeste identifikatoren.

| Fil | Innhold | Brukt i CSV |
|---|---|---|
| `2.tert2026_ventetider_henvisninger_fristbrudd.xlsx` | Ventetid, henvisninger og fristbrudd per tertial, 1. tertial 2019–2. tertial 2026 | Ja |
| `ar_2025_ventetider_henvisninger.xlsx` | Samme mål per år, 2012–2025. Ventetid bare for påbegynt helsehjelp. | Ja |
| `september2026_ventetider_henvisninger_fristbrudd.xlsx` | Månedstall (foreløpige), til og med september 2026 | Nei, bare lagret som rådata |
| `tid-til-tjenestestart_2.tert2026.xlsx` | Tid til tjenestestart (TTT) per tertial, 2012–2. tertial 2026 | Ja |
| `tid-til-tjenestestart_ar2025.xlsx` | Tid til tjenestestart per år, 2012–2025 | Ja |
| `passert-planlagt-tid_2tert2026.xlsx` | Passert planlagt tid (PPT), april 2017–august 2026 | Ja |

FHIs egen omtale av statistikken:
- <https://www.fhi.no/he/npr/statistikk-npr/ventetider-og-pasientrettigheter/>
- <https://www.fhi.no/he/npr/statistikk-npr/tid-til-tjenestestart/>
- <https://www.fhi.no/he/npr/statistikk-npr/passert-planlagt-tid/>

## 2. Kilder som er undersøkt uten treff

| Kilde | Resultat |
|---|---|
| FHI Statistikk Open API (`statistikk-data.fhi.no/api/open/v1/`) | Kilden `npr` har 59 tabeller. Ingen av dem gjelder ventetid eller fristbrudd. Nøkkeltallstabellene 517, 518, 464 og 520 har bare aktivitetstall: pasienter, opphold og kontakter. Tabellene er etter bostedsregion og finnes ikke per HF. **Ventetid: ikke funnet.** |
| SSB (PxWebApi v2, søk «ventetid») | Ingen tabeller for ventetid i spesialisthelsetjenesten. **Ikke funnet.** |
| Helsedirektoratets kvalitetsindikatorer, NKI | Indikatorene for ventetid og fristbrudd ligger som årsdata i Power BI-visninger. Også NKI-eksporten er en Power BI-visning. Den er ikke hentet, fordi den krever nettleser. HAPI-API-et krever abonnementsnøkkel og er ikke brukt. Teksten på indikatorsidene er brukt til kontroll (avsnitt 5). |
| `helsedirektoratet.no/statistikk/statistikk-fra-npr/ventetider-og-pasientrettigheter` | Videresendes til FHI. |
| Årsrapportene «Ventetider og pasientrettigheter» 2019, 2020 og 2021 (PDF i FHIs arkiv) | Lastet ned som rådata og brukt til kontroll. Tabellene er på RHF-nivå. Jeg fant ingen utgaver for 2022 eller senere. |

Lenken til nedlastingssiden ble funnet i rapportdefinisjonen til FHIs offentlige Power BI-rapport «Ventetider og pasientrettigheter». Den ble lest gjennom den offentlige publiser-på-nett-tjenesten, uten innlogging. Ingen tall i CSV-en er hentet fra Power BI.

## 3. Innhold i `ventetid.csv`

CSV-en er i langt format med 16 831 rader. Kolonnene er:

- `periode`
  - tertial: `2026-T2`
  - år: `2025`
  - øyeblikkstall: `2026-08`
- `periodetype`: `tertial`, `år` eller `øyeblikk`.
- `aar` og `tertial`: tertialnummeret 1–3. For øyeblikkstallene gjelder april = 1, august = 2 og desember = 3.
- `enhet`: Landet, de fire RHF-ene, Private institusjoner og de fire HF-ene i Helse Nord. De fire HF-ene er Universitetssykehuset Nord-Norge HF, Nordlandssykehuset HF, Helgelandssykehuset HF og Finnmarkssykehuset HF.
- `enhetstype`: `land`, `RHF`, `privat` eller `HF`.
- `rhf`: overordnet RHF.
- `fagomrade`
  - venteliste: Alle sektorer, Somatikk, Psykisk helsevern voksne, Psykisk helsevern barn og unge, Rusbehandling (TSB). «Ukjent» er utelatt.
  - TTT: «TTT: Alle utredninger/behandlinger», «TTT: Alle utredninger» og «TTT: Alle behandlinger».
  - PPT: «Alle fagområder».
- `indikator`, `verdi`, `enhet_maal` (`dager`, `antall` eller `prosent`) og `kildefil`.

| Indikator | Definisjon (FHI) | Tertial | År | Nivå |
|---|---|---|---|---|
| `ventetid_pabegynt_gjsn` | Gjennomsnittlig antall kalenderdager fra henvisningen er mottatt til helsehjelpen er påbegynt, for dem som har fått påbegynt helsehjelp i perioden | 2019–2026 | 2012–2025 | Land, RHF og HF |
| `ventetid_ventende_gjsn` | Gjennomsnittlig antall dager fra henvisningen er mottatt til periodeslutt, for dem som fortsatt venter siste dag i perioden | 2019–2026 | – | Land, RHF og HF |
| `antall_nyhenviste`, `antall_pabegynt` | Henvisninger som er rettighetsvurdert og har fått rett i perioden, og henvisninger der helsehjelpen er påbegynt. Øyeblikkelig hjelp og kontroller er ikke med. | 2019–2026 | 2012–2025 | Land, RHF og HF |
| `antall_ventende` | Øyeblikkstall siste dag i perioden | 2019–2026 | – | Land, RHF og HF |
| `andel_fristbrudd_pabegynt`, `antall_fristbrudd_pabegynt` | Helsehjelpen er påbegynt etter fristdato. Andelen er fristbruddene delt på antall påbegynt helsehjelp, i prosent. | 2019–2026 | 2012–2025 | Land og RHF |
| `andel_fristbrudd_ventende`, `antall_fristbrudd_ventende` | Venter fortsatt siste dag i perioden, og fristdatoen er passert. Andelen er fristbruddene delt på antall ventende, i prosent. | 2019–2026 | Andel 2012–2025, ikke antall | Land og RHF |
| `ttt_gjsn`, `ttt_median`, `ttt_antall` | Tid fra mottatt henvisning til en bestemt utredning eller behandling er utført. Gjelder et utvalg av tjenester definert med diagnose- og prosedyrekoder. `ttt_antall` er antall avviklede. | 2012–2026 | 2012–2025 | Land, RHF og HF |
| `ppt_andel`, `ppt_antall` | Andel og antall pasientavtaler som er forsinket i forhold til tidspunktet registrert i pasientdatasystemet. Øyeblikkstall 30. april, 31. august og 31. desember. Andelen er regnet om fra brøk til prosent. | – | – | Land, RHF og HF |

## 4. Forbehold

1. **Behandlingssted, ikke bosted.**
   - Enhetene er det behandlende foretaket, ikke pasientens bostedsregion.
   - «Helse Nord» i ventelistefilene er summen av de fire HF-ene og «Privat Nord». Kontrollert for 2. tertial 2026: 34 237 + 676 = 34 913 påbegynt.
   - «Private institusjoner» er en egen kategori. Den inngår i Landet, men ikke i RHF-ene.
2. **Private står for mye av fristbruddene nasjonalt.** For eksempel hadde de 30,6 % fristbrudd for ventende i 3. tertial 2024. Andelen for Landet ligger derfor ikke mellom RHF-tallene.
3. **Avtalespesialister inngår ikke** i ventetidstallene.
4. **Fristbrudd per HF finnes ikke åpent.** Det gjelder både FHI-filene og Power BI-visningen. Helse Nords månedlige virksomhetsrapporter viser fristbrudd per HF, men bare i figurer og med Helse Nords egne styringsdata (HN LIS).
5. **Brudd og sammenlignbarhet over tid**
   - **Tertialserien starter i 2019.** For 2012–2018 finnes bare årstall.
   - **Begrepene er byttet ut.** Årsrapportene fram til 2021 bruker «ordinært avviklet». Det er det samme som «påbegynt helsehjelp» (rapport 2019, kap. 2).
   - **Nyhenviste ble definert om.** I 2019-rapporten endret Helsedirektoratet hvilke henvisninger som regnes med. Henvisninger som avvikles samme dag og sendes videre, er nå med. Tallene ble regnet om bakover og omtales som sammenlignbare.
   - **Sammenlignbarheten for 2012–2014 er ikke kontrollert.**
   - **Fristbrudd i 2020 er ikke fristbrudd i juridisk forstand.** Fra 27. mars til 1. oktober 2020 satte en midlertidig forskrift retten til helsehjelp innen frist til side. Fristbruddene er likevel telt på vanlig måte (rapport 2021). Andelen fristbrudd i Helse Nord steg fra 2,6 % i 2019 til 15,0 % i 2020.
6. **Feil i data fra Helse Midt-Norge 2022–2024.** Det nye journalsystemet ble innført fra november 2022 til november 2024. Det har gitt mangler og feil i dataene til NPR for Helse Midt-Norge og dermed også for landet (Helsedirektoratet).
7. **Feil i data fra Helse Sør-Øst 2025–2026.** FHIs Power BI-rapport (siden «Feil i tall», merket «Tall for mars 2025») varsler alvorlige feil i rapporteringen fra Helse Sør-Øst.
   - Ventetiden for ventende blir for lang.
   - Ventetiden for påbegynt helsehjelp oppgis å være riktig.
   - FHI kjenner ikke omfanget av feilen. Det berører også landstallet for `ventetid_ventende_gjsn`. Det er ikke kontrollert nøyaktig hvilke perioder feilen gjelder.
8. **Årstallet for andel fristbrudd blant ventende er ikke et øyeblikkstall ved årsslutt.**
   - For 2024 er årstallet 8,75 % for Landet. Til sammenligning var det 7,41 % ved utgangen av 3. tertial 2024, og snittet av de tre tertialene er 8,73 %.
   - Filen beskriver ikke hvordan årstallet er beregnet.
9. **Avvik i passert planlagt tid**
   - FHIs side sier at Helse Nord ikke rapporterte tall for 3. tertial 2024. Filen har likevel tall for Helse Nord for desember 2024: 41 189, eller 16,1 %. Avviket er ikke avklart.
   - Sidens kompletthetsnotat sier også at Helse Nord mangler tall per fagområde for april 2017.
   - For UNN i august 2026 har filen en ekstra rad med Antall = 1 og Andel = 1. Den er fjernet. En enkeltrad for «Universitetssykehuset Nord Norge Tromsø» i april 2026 er utelatt.
10. **Tid til tjenestestart er et utvalg tjenester.** Utvalget kan endres; Helsedirektoratet fikk i 2026 i oppdrag å gå gjennom det. «Helse Finnmark HF» (2012–2013) er slått sammen med Finnmarkssykehuset HF som samme foretak med nytt navn.
11. **Månedstall er foreløpige** og er ikke tatt med i CSV-en. Tertial- og årstallene er den offisielle statistikken og oppdateres ikke senere (FHI).
12. **Ingen prikking.** FHI publiserer ventelistetallene uten prikking. PPT og TTT er anonymisert ved at tall under tre er slettet. Summer kan derfor avvike noe.

## 5. Kontroll mot publiserte tall

| Publisert tall | Kilde | Tall i CSV | Vurdering |
|---|---|---|---|
| Ventetid i landet, 2. tertial 2026: alle 62, somatikk 63, PHV 43, PHBU 42, TSB 26 dager. 2. tertial 2025: 61, 63, 43, 41 og 26. | FHI-nyhet 20.10.2026 («Ventetid og aktivitet … ved utgangen av august 2026») | 2026: 61,5 / 63,1 / 43,1 / 42,4 / 26,3. 2025: 61,4 / 63,5 / 43,1 / 40,9 / 25,9. | Stemmer etter avrunding. Somatikk 2025 er 63,46. |
| Gjennomsnittlig ventetid i somatikken 2024: landet 76,8, Helse Nord 72,2 og Helse Sør-Øst 79,3 dager | Helsedirektoratet, kvalitetsindikatoren «Sykehusopphold – ventetid påbegynt helsehjelp» | 76,75 / 72,21 / 79,34 (år 2024, Somatikk) | Stemmer. |
| Fristbrudd for ventende ved utgangen av 2024: landet 7,7 %, Helse Nord 12,2 % og Helse Sør-Øst 6,0 % | Helsedirektoratet, indikatoren for fristbrudd blant ventende | 3. tertial 2024: 7,41 / 12,11 / 5,61 % | Samme nivå. Helsedirektoratet teller bare pasienter med gyldig frist i nevneren og får derfor noe høyere tall (forklaring på Helsedirektoratets side). |
| Gjennomsnittlig ventetid i somatikken i Helse Nord 2017–2021: 59, 59, 60, 70, 69 dager. Totalt: 58, 60, 61, 65, 63. | Ventetider og pasientrettigheter 2021, tabell V4 | Helse Nord: 59,1 / 58,6 / 59,7 / 70,2 / 68,8. Landet: 58,3 / 60,2 / 61,3 / 65,4 / 62,6. | Stemmer. Årsserien henger sammen med de eldre rapportene. |
| Helse Nord, september 2026: ventetid 68 dager for både påbegynt og ventende. Somatikk 69 påbegynt og 70 ventende. Fristbrudd 9,8 % for påbegynt og 5,8 % for ventende. | Helse Nord, styresak 126-2026 (virksomhetsrapport september; kilde HN LIS/NPR) | FHIs månedsfil: 67,7 / 68,7 dager. Somatikk 68,4 / 70,1. Fristbrudd 9,16 % / 5,84 %. | Ventetid og fristbrudd for ventende stemmer. Fristbrudd for påbegynt er 9,8 mot 9,2 %. Det kan skyldes at Helse Nords tall bygger på egne styringsdata og at månedstallene er foreløpige. |
| Tid til tjenestestart 2025 per HF, i dager: Finnmark 107, UNN 141, Nordland 115, Helgeland 116, Helse Nord 125. Passert planlagt tid «utgangen januar 2025»: 12,1–14,1 %. | Helse Nord RHF gjengitt i statsrådens svar på spørsmål 1583 (Dokument 15, 20.02.2026) | FHI 2025: Finnmark 80,2, UNN 102,5, Nordland 97,2, Helgeland 96,9, Helse Nord 96,7 | **Stemmer ikke.** Helse Nords egne tall ligger 20–40 dager over FHIs, og antallene er høyere (46 574 mot 36 124). Trolig brukes et annet tjenesteutvalg eller datagrunnlag. Dette er ikke avklart, og tallene er ikke tatt med i CSV-en. PPT for januar finnes ikke i FHIs fil, som bare har april, august og desember. |

## 6. Ikke funnet åpent

- Fristbrudd per HF (bare RHF og land).
- Ventetid for ventende som årstall. Den finnes per tertial.
- Tertialtall for ventetid og fristbrudd før 2019.
- Ventetid etter pasientens bostedskommune eller bostedsregion. Ventelistefilene viser bare behandlingssted.
- Ventetid for avtalespesialister.
- Tid til operasjon (Helse Nords og de andre regionenes interne indikator). Den finnes ikke som åpen FHI-fil.
