# Riksrevisjonen om helse- og omsorgstjenester til eldre: essens og kontrollerte tall for Nord-Norge

Overleveringsnotat til arbeidet med dashbordet `nord-norge`. Laget 20. oktober 2026.
Sammenlignet med arbeidskopien på `main`, commit `1c28674` (20.10.2026 kl. 12.10), `data.js` endret 20.10.2026 kl. 12.07.
Notatet foreslår ingen endringer i koden. Det samler fakta og avvik som grunnlag for videre arbeid.

Vedlegg i samme mappe:
- `nn_kommuner_eldre_2026_2050.csv`: én rad per kommune (80 kommuner) med 80+, 90+, demens, 20–64 år, årsverk og behovsindeks. Semikolon som skilletegn.
- `beregn.py`: beregningen bak CSV-filen (dokumentasjon, avhenger av mellomfiler fra denne økten).

---

## 1. Hva rapporten er

- **Dokument 3:16 (2025–2026)**, *Riksrevisjonen si undersøking av kommunale helse- og omsorgstenester til eldre*. Datert 9. juni 2026, vedtatt 3. juni 2026, 197 sider, skrevet på nynorsk.
- **Overordnet vurdering: «Kritikkverdig».** Kritikken retter seg mot Helse- og omsorgsdepartementet, som ikke har fulgt opp om kommunene er forberedt på den demografiske utviklingen.
- **Fire problemstillinger:** (1) Sikrer kommunene nok kapasitet? (2) Har de forberedt seg ut fra befolkningsframskrivingene? (3) Jobber de systematisk med kvalitet? (4) Legger statens virkemidler til rette for kapasitet og kvalitet?
- **Datagrunnlag:**
  - spørreundersøkelse våren 2025 til alle kommuner (256 kommuner og 13 bydeler svarte, en svarprosent på 72 og 87)
  - gjennomgang av planene i 60 tilfeldig utvalgte kommuner
  - 74 tilsynsrapporter fra statsforvalterne (2022–2025)
  - 43 forvaltningsrevisjoner fra kommunerevisjonene
  - SSB-tabellene 07459, 11875, 12003, 12209, 12292, 14282, 14293 og 14534, samt Demenskartet
- **Framskrivingsårgang:** SSBs 2024-framskriving (14282/14293). Dashbordet bruker 2026-årgangen (14746/14751), som ble publisert 12. juni 2026, tre dager etter rapporten. Forskjellen er liten (se punkt 5).
- **Analyseenhet:** SSBs sentralitetsklasser 1–6. *Distriktskommuner* betyr klasse 5–6. Rapporten bruker aldri «Nord-Norge» som kategori, og fylkene opptrer bare på embetsnivå hos statsforvalterne.

## 2. Konklusjoner og anbefalinger

**Konklusjoner:**
- Tjenestene er i liten grad dimensjonert for økningen i antall eldre.
- Det er risiko for svikt i tjenestene til eldre.
- Kommunene planlegger ikke systematisk for framtiden.
- Departementet har lagt fram mange stortingsmeldinger og planer siden 2006, men med begrensede resultater.
- Staten mangler fortsatt nødvendig kunnskap om kvaliteten i tjenestene.

**Riksrevisjonen anbefaler at departementet:**
1. følger opp at kommunenes tjenester blir dimensjonert for den økende andelen eldre, med kommunal planlegging som forutsetning
2. sørger for bedre kunnskap om kvaliteten i tjenestene
3. setter statsforvalterne bedre i stand til å føre tilsyn og veilede om planer og kvalitetsforbedring
4. tilpasser investeringstilskuddet til omsorgsboliger og sykehjemsplasser til ulike kommuners behov

## 3. Rapportens nøkkeltall (hele landet)

| Tema | Tall i rapporten | Kontroll |
|---|---|---|
| 80+ 2015–2025 | +50 000 (+23 %) | **Stemmer.** SSB 07459: 220 437 → 270 537 (+22,7 %) |
| 80+ 2020–2030 | +50 % | **Stemmer**, også i 2026-årgangen: 230 710 → 347 953 (+50,8 %) |
| 67+ 2020–2050 | nær +70 % | Ikke kontrollert separat |
| Institusjonsbrukere 80+ 2015–2025 | −16 % | Fra SSB 12003, ikke kontrollert |
| Hjemmetjenestemottakere 80+ 2015–2025 | −3 % | Fra SSB 12003, ikke kontrollert |
| Institusjonsplasser 2015 → 2025 | 40 708 → 39 988 (−720) | SSB 11875, gjengitt i rapportens tabell 2 |
| Etterspørsel etter heldøgns omsorgsplasser | 65 000 (2017) → 87 000 (2025) → 133 000 (2060) | SSB-framskriving, sitert fra Meld. St. 9 |
| Årsverk i omsorgstjenestene 2015–2025 | +32 000 (+28 %) | **Stemmer.** SSB 14534, pasient- og brukerrettede årsverk: 116 440 → 148 536 (+27,6 %) |
| Bemanning | om lag 0,5 årsverk per bruker (spenn 0,3–1,0) | SSB 12209 |
| Vekst i årsverk etter sentralitet | lavest i klasse 5–6 (figur 21) | Ikke kontrollert |
| Forsørgerbrøk (65+ per 20–64) | 0,32 (2024) → 0,48 (2050) | **Stemmer** med 2024-årgangen (14293). 2026-årgangen gir 0,33 (2026) → 0,47 (2050) |
| Personer med demens | «meir enn dobla fram mot 2040» (s. 16, 54) og «nær dobla innan 2050» (s. 119–120) | **Motsier seg selv.** Se punkt 6 |
| Kommuner uten demensplasser | 31 (s. 17) og 28 (s. 58) | **Motsier seg selv.** Begge steder: usentrale kommuner, de fleste under 5 000 innbyggere |
| For få sykehjemsplasser / heldøgns omsorgsplasser | 31 % / 43 % av kommunene | Spørreundersøkelsen |
| Ikke nok bemanning med rett kompetanse | 15 % (hjemme), 1 av 5 (sykehjem) | Spørreundersøkelsen. Mest uttalt i distriktskommuner og kommuner med mange eldre |
| Vanskelig å rekruttere og beholde | 2 av 3 kommuner | Spørreundersøkelsen |
| Konsekvens av personellmangel | over 80 %: eldre må ta mer ansvar selv; over halvparten: kvaliteten må ned | Spørreundersøkelsen |
| Planlegging | 33 av 60 kommuner planlegger ingen økning i plasser eller boliger; bare 16 % har tallfestet antall ansatte i planene; hver fjerde sier de ikke dekker dagens behov | Plangjennomgangen |
| Mangler tid, ressurser og kompetanse til planarbeid | 18–30 % (avhenger av spørsmålet) | Høyest i distriktskommuner |
| Helsepersonellkommisjonen (SSB 2023a) | sektorens andel av alle årsverk kan måtte dobles fra 13 % mot 2060 | Fotnote 369 |

## 4. Funn i rapporten som gjelder Nord-Norge direkte

- **Egnede boliger:** «Mangelen på eigna bustader er størst i dei nordlegaste fylka» (Husbankens kommuneundersøkelse). Distriktskommunene og de minste kommunene vurderer tilgangen klart dårligere enn andre.
- **Allmennsykepleiere med avansert klinisk kompetanse:** 2–3 per fylke i Nordland, Troms og Finnmark (og Trøndelag), mot 9–18 i de øvrige fylkene.
- **Kompetanse- og tjenesteutviklingstilskuddet:**
  - Nordland hadde færrest kommuner som søkte, om lag 76 % i 2024 og 2025 (31 av 41).
  - Troms og Finnmark: 34, 30 og 34 av 39 kommuner i 2023, 2024 og 2025.
  - Utbetalt i Nordland: 27,6 millioner kroner (2019), 34,3 (2020), 20,0 (2024). Troms og Finnmark: 25,0, 33,5 og 21,7.
- **Statsforvalternes ressurser** til planlagte tilsyn, oppfølging av bekymringsmeldinger og tilsyn med tjenester til eldre: Nordland og Troms og Finnmark svarer «for få» på flere av punktene (tabell i kapittel 11/14).
- **Kommuner med om lag 30 % innbyggere over 67 år i 2025:** Rapporten navngir Rendalen, Bindal, Vevelstad, Beiarn, Osen og Ibestad. Fire av seks ligger i Nord-Norge.

## 5. Kontroll: 80+ i Nord-Norge

Kilde: SSB 07459 (registrert befolkning) og 14746, hovedalternativet MMMM (framskriving).

| År | Nord-Norge 80+ | Hele landet 80+ |
|---|---|---|
| 2015 | 21 575 | 220 437 |
| 2020 | 22 964 | 230 710 |
| 2025 | 27 044 | 270 537 |
| 2026 | 28 213 | 284 939 |
| 2030 | 34 223 | 347 953 |
| 2040 | 44 289 | 462 112 |
| 2050 | 54 071 | 591 350 |

- Nord-Norge 2026–2050: **+92 %** (Nordland +83 %, Troms +97 %, Finnmark +115 %). Hele landet: +108 %.
- 90+ i Nord-Norge: 4 343 → 11 897 (**+174 %**). Det er den mest pleietrengende gruppen.
- 20–64 år, 2026–2050: **−7,2 % i Nord-Norge** (Nordland −9,6 %, Troms −4,3 %, Finnmark −6,6 %), mot +2,3 % i landet.
- Etter sentralitet (hele landet) er den relative veksten i 80+ *lavest* i distriktet: klasse 1 +127 %, klasse 6 +72 %. Antall 80+ per 100 i alderen 25–69 år går fra 13,2 til 24,0 i klasse 6 og fra 6,2 til 12,8 i klasse 1. Problemet i distriktet er dermed høyt nivå og et krympende arbeidskraftgrunnlag, ikke rask vekst.
- Dashbordet har allerede 80+ fra 14746 (`fetch_alder80.py`, `DATA.proj.kommuner[k].a80`). Disse tallene bør stemme med tabellen over, men det er **ikke kontrollert mot `data.js`**.

## 6. Kontroll: antall personer med demens

**Rapporten motsier seg selv.** Den sier at antallet blir «meir enn dobla fram mot 2040» (s. 16 og 54) og «nær dobla innan 2050» (s. 119–120). Folkehelseinstituttet (oppdatert 27. mai 2026) gir 115 000 (2025), 135 000 (2030), 185 000 (2040) og 225 000 (2050). Det tilsvarer 1,6 ganger fram mot 2040 og 2,0 ganger fram mot 2050. Formuleringen om 2040 ser ut til å bygge på et eldre anslag. **Bruk «om lag dobling fram mot 2050».**

**Egen beregning for Nord-Norge.** Jeg brukte de aldersspesifikke forekomstratene fra Demenskartet (Aldring og helse; HUNT4 70+ / Gjøra mfl. 2021) på befolkningsbanen i SSB 14746:

| Alder | 30–64 | 65–69 | 70–74 | 75–79 | 80–84 | 85–89 | 90+ |
|---|---|---|---|---|---|---|---|
| Andel med demens | 0,08 % | 0,57 % | 6,39 % | 10,03 % | 17,80 % | 30,45 % | 41,47 % |

Kontroll mot hele landet: 116 100 (2026), 132 300 (2030), 176 700 (2040), 216 700 (2050). Det ligger 2–4 % under FHI, trolig fordi FHI bruker kjønnsspesifikke rater (flere kvinner blant de eldste). Tallene er derfor heller lave enn høye.

| | 2026 | 2030 | 2040 | 2050 | Endring |
|---|---|---|---|---|---|
| Nord-Norge | 11 459 | 12 939 | 16 742 | 19 307 | **+69 %** |
| Nordland | 6 102 | 6 822 | 8 685 | 9 842 | +61 % |
| Troms | 3 764 | 4 300 | 5 631 | 6 581 | +75 % |
| Finnmark | 1 592 | 1 817 | 2 426 | 2 884 | +81 % |
| Hele landet | 116 141 | 132 344 | 176 678 | 216 663 | +87 % |

Etter sentralitet innenfor Nord-Norge: klasse 3 (Bodø, Tromsø) +100 %, klasse 4 +64 %, klasse 5 +63 %, klasse 6 +54 %. Kommunetallene står i CSV-filen (`demens_2026`, `demens_2050`).

Forbehold:
- Ratene er like over hele landet og for begge kjønn.
- Små kommuner gir store tilfeldige utslag, og Demenskartet advarer selv mot det.
- Beregningen antar uendret forekomst per aldersgruppe. Synkende aldersspesifikk forekomst (dokumentert i flere land) ville gitt lavere tall.

## 7. Kontroll: behov for helsepersonell i kommunene

**Rapportens tall gjelder hele landet.** Rapporten tallfester ikke personellbehovet per kommune eller fylke. Den viser til Helsepersonellkommisjonen og SSB (2023a): sektorens andel av alle årsverk kan måtte dobles fra 13 % mot 2060. Ellers bruker den kommunenes egne vurderinger (se tabellen i punkt 3).

**Egen mekanisk beregning («alt annet likt»).** Metoden er en forenklet utgave av SSBs HELSEMOD:
- Bruksrater: andelen mottakere av hjemmetjenester eller institusjonstjenester per aldersgruppe i hele landet i 2025 (SSB 12003 delt på 07459). Det gir 2,28 % for 0–66 år, 7,93 % for 67–79 år og 36,11 % for 80+.
- Ratene brukes på hver kommunes befolkningsbane (14746). Resultatet er en behovsindeks for 2050 med 2026 som utgangspunkt.
- Indeksen ganges med kommunens faktiske pasient- og brukerrettede årsverk i 2025 (SSB 14534).
- Bemanning per bruker og bruksrate per aldersgruppe holdes konstant.

| | Årsverk 2025 | Behov 2050 | Økning | Per 100 i alderen 20–64, 2026 → 2050 |
|---|---|---|---|---|
| Nord-Norge | 16 646 | 22 706 | +6 060 (+36 %) | 5,9 → 8,7 |
| Nordland | 8 035 | 10 567 | +2 532 (+32 %) | 5,9 → 8,5 |
| Troms | 5 652 | 7 884 | +2 232 (+39 %) | 5,6 → 8,2 |
| Finnmark | 2 959 | 4 255 | +1 296 (+44 %) | 6,7 → 10,3 |
| Klasse 6 (54 kommuner) | 4 229 | 5 563 | +1 334 (+32 %) | 7,4 → 10,5 |
| Hele landet | 148 536 | 220 063 | +71 500 (+48 %) | 4,5 → 6,5 |

**Tolkning:** Den prosentvise økningen er lavere i Nord-Norge enn i landet. Men behovet målt mot arbeidsstyrken er høyere allerede i dag og stiger mest. I 2050 må nesten 9 av 100 nordlendinger i alderen 20–64 år jobbe i pleie og omsorg, mot 6,5 av 100 i landet, og over 10 av 100 i de minst sentrale kommunene. Det stemmer med rapportens hovedfunn om at det er bemanningen som binder i distriktet.

Høyest behov per 100 i alderen 20–64 år i 2050 (CSV-kolonne `aarsverk_pr_100_i_2064_2050`): Kvæfjord 17,7, Bindal 15,8, Dønna 15,4, Kvænangen 15,1, Nesseby 14,9, Beiarn 14,5, Bø 14,3, Karlsøy 14,2, Saltdal 13,8, Gratangen 13,7. Kvæfjord kan være påvirket av regionale institusjoner. Sjekk før tallet brukes.

Forbehold:
- Beregningen vekter brukere likt, men en institusjonsbruker krever langt flere årsverk enn en hjemmetjenestebruker. Siden 80+ dominerer i institusjon, undervurderer modellen trolig veksten noe.
- Nasjonale bruksrater brukes for alle kommuner, men distriktskommuner har i dag høyere dekning (rapportens figur 5).
- Årsverk omfatter alle brukere, også under 67 år.
- Mer bruk av velferdsteknologi og dagens trend mot strengere tildeling (færre institusjonsbrukere 80+ fra 2015 til 2025) trekker behovet ned.
- Dette er et behov som følger av demografien, ikke en prognose. Det er ikke det samme som NAVs anslag for dagens mangel (dashbordets tema 04: 1 750 i helse og sosial).

## 8. Sentralitet og forsørgerbrøk i Nord-Norge (2026-årgangen, SSB 14751 og KLASS 128)

- Av 80 kommuner: 54 i klasse 6, 16 i klasse 5, 8 i klasse 4 (Narvik, Vefsn, Rana, Fauske, Sortland, Harstad, Alta, Hammerfest) og 2 i klasse 3 (Bodø, Tromsø). **70 av 80 er distriktskommuner** etter rapportens definisjon.
- Median forsørgerbrøk i 2050 etter klasse: 3: 0,43, 4: 0,54, 5: 0,55, 6: 0,62. Klasse 6 har allerede 0,51 i 2026, høyere enn landet i 2050 (0,47).
- 72 av 80 kommuner ligger over landet i 2050, 36 på 0,60 eller høyere og 14 på 0,70 eller høyere. Høyest er Bindal (0,83) og Lavangen (0,80).
- Fylkestallet skjuler forskjellene: Troms har 0,48, men medianen for kommunene i Troms er 0,62. Nordland har 0,54 (median 0,60), Finnmark 0,49 (median 0,54).
- Forsørgerbrøken faller fra 2026 til 2050 i Loppa (0,53 → 0,46), Ibestad, Vevelstad og Lødingen. Det skyldes trolig hvordan framskrivingen virker i bittesmå kommuner. Loppa er en av dashbordets tre eksempelkommuner.

## 9. Avvik i dashbordet (commit `1c28674`)

1. `tema-aldring.html` oppgir «SSB: 46» for landet i 2050 (i teksten og som referanselinje i fylkesgrafen). Både SSB 14751 og egen beregning fra 14746 gir **0,47** (1 590 452 / 3 380 581 = 0,470). Forsiden og temakortet sier 49 (FN-grunnlag). Det er en annen kilde og ikke feil.
2. De hardkodede fylkestallene i `tema-aldring.html` stemmer med 14751 når de avrundes. Nord-Norge «~51» stemmer (0,511).
3. «Innlandet sliter mer enn Nord-Norge» stemmer når man veier etter folketall, men ikke når man teller kommuner. Rapportens analyseenhet er kommunen, siden det er kommunene som har ansvaret for tjenestene.
4. Dashbordet har økonomiske mål for tjenestesiden (KOSTRA 12209 i `fetch_kostra.py`: `omsorg_pct`, `omsorg_pi`) og 80+ (`fetch_alder80.py`). Det har ikke kapasitetsmålene rapporten bygger på: institusjonsplasser per 80+ (11875), årsverk og utdanning (14534), brukere etter alder (12003), demens og sentralitetsklasse.
5. Boligbehovsmodellen (`fetch_behov.py`, BB-KVOTE) bygger på husholdninger. Den skiller ikke ut boliger tilpasset eldre eller omsorgsboliger, og det er nettopp der rapporten peker på at mangelen er størst i nord.
6. Jeg har ikke lest temasidene 07–10 (bolig, næring, pensjon, ung) og har ikke kontrollert verdiene i `data.js` direkte.

## 10. Kilder og tabell-ID-er (for gjenbruk i koden)

| Kilde | Innhold | Merknad |
|---|---|---|
| SSB 14746 | Framskrevet folkemengde etter kjønn og ettårig alder, 2026–2050 | Dashbordets eksisterende kilde. Kodelister: `agg_FemAarigGruppering`, `agg_Funksjonell4` (80–89, 90+), `agg_SentralIndeksC2024` (sentralitet) |
| SSB 14751 | Framskrevne forsørgerbrøker 2026–2050 (65+/20–64), kommuner og fylker | `ForsByrdeEldre`, alternativ `MMMM` |
| SSB 14293 | Samme, 2024-årgangen (avsluttet serie) | Rapportens grunnlag |
| SSB 07459 | Registrert befolkning etter alder, 1986–2026 | `agg_LandsdelKommun`: LK06 = Nord-Norge |
| SSB 12003 | Brukere av omsorgstjenester etter alder (0–66, 67–79, 80+) og tjenestegruppe (A hjem, B institusjon, C aktivisering) | Små tall skjermes med «..». Bruk nasjonale rater eller aggregerte tall |
| SSB 14534 | Avtalte årsverk i omsorgstjenestene etter stillingstype og utdanning, 2015–2025 | `POB` = pasient- og brukerrettet, `01` = sykepleier, `EAK` = landet. Troms og Finnmark mangler 2015 med 2024-kommunekoder |
| SSB 11875 | Institusjonsplasser | Ikke hentet her |
| SSB 12209 | KOSTRA pleie og omsorg, nøkkeltall | Brukes allerede i `fetch_kostra.py` |
| SSB KLASS 128/131 | Sentralitetsindeks 2024 per kommune | `https://data.ssb.no/api/klass/v1/classifications/131/correspondsAt.json?targetClassificationId=128&date=2024-06-01` (svarer fra økten, uten nøkkel) |
| Demenskartet | Aldersspesifikke forekomstrater (se punkt 6) | demenskartet.no, Aldring og helse |
| FHI | Antall med demens 2025–2050 | Folkehelserapporten, oppdatert 27.05.2026 |

Lenker:
- Riksrevisjonen, Dokument 3:16 (2025–2026): <https://www.riksrevisjonen.no>
- SSB statistikkbanken: <https://www.ssb.no/statbank/table/14746>, <https://www.ssb.no/statbank/table/14751>, <https://www.ssb.no/statbank/table/12003>, <https://www.ssb.no/statbank/table/14534>
- FHI, Demens i Norge: <https://www.fhi.no/he/folkehelserapporten/ikke-smittsomme/demens>
- Demenskartet: <https://demenskartet.no/>
- Helsedirektoratet om Demenskartet: <https://www.helsedirektoratet.no/forebygging-diagnose-og-behandling/diagnose-og-behandling/demens/demenskartet>
