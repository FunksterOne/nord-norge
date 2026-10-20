# Kontroll av eldredataene og Riksrevisjonen-notatet

20. oktober 2026. Overleveringen (`riksrevisjonen-eldre-essens.md` og `nn_kommuner_eldre_2026_2050.csv`) er kontrollert mot SSB og mot Riksrevisjonens rapport (Dokument 3:16 (2025–2026), lastet ned fra stortinget.no til `kilder/`, ikke versjonert). Dashbordet bygger tallene selv med `fetch_eldre.py`; CSV-filen er bare brukt som kontroll.

## Konklusjon

Tallene i CSV-filen er riktige. Alle kolonnene som kommer direkte fra SSB, er identiske med en uavhengig henting for alle 80 kommuner. Avledede tall avviker bare i avrundingen. Notatets påstander om rapporten stemmer med rapportteksten. Én feil i dashbordet er rettet: landets forsørgerbyrde i 2050 er 47 i SSBs hovedalternativ, ikke 46.

## SSB-kolonnene

| Kolonne | Kilde | Største avvik |
|---|---|---|
| 80+, 90+, 20–64 år (2026 og 2050) | SSB 14746, MMMM | 0 |
| Årsverk og sykepleierårsverk 2025 | SSB 14534, POB | 0 |
| Forsørgerbrøk 2026 og 2050 | SSB 14751, MMMM | 0 |
| Sentralitet | KLASS 128 | 0 |
| Demens 2026 og 2050 | Demenskartets rater på 14746 | under én person (avrunding) |
| Bruksrater 0–66 / 67–79 / 80+ | SSB 12003 (A+B) / 07459, landet 2025 | 0 (2,28 / 7,93 / 36,11 %) |
| Behovsindeks 2050 | rater på 14746 | inntil 0,011, uten skjevhet |
| Årsverksbehov 2050 | årsverk × indeks | inntil 2,4 årsverk |

Behovsindeksen avviker fordi overleveringen avrundet indeksen til tre desimaler før den ble ganget med årsverkene. Summen for Nord-Norge blir 22 721 årsverk i dashbordet mot 22 706 i notatet, og for landet 220 129 mot 220 063.

## Notatets egne tall

- Nord-Norge 80+: 28 213 (2026), 34 223 (2030), 44 289 (2040), 54 071 (2050). Stemmer.
- 90+: 4 343 → 11 897. 20–64 år: −7,2 % (landet +2,3 %). Stemmer.
- Demens Nord-Norge: 11 459 → 19 307. Stemmer, men endringen er 68,5 %, avrundet 68 %, ikke 69 %.
- Årsverk per 100 i alderen 20–64: Nord-Norge 5,9 → 8,7, landet 4,5 → 6,5, klasse 6 7,4 → 10,5. Stemmer.
- 72 av 80 kommuner over landet i 2050, 36 på 0,60 eller høyere, 14 på 0,70 eller høyere, Bindal 0,83 og Lavangen 0,80. Stemmer.
- Medianer etter klasse (0,43 / 0,54 / 0,55 / 0,62) og per fylke (Nordland 0,60, Troms 0,62, Finnmark 0,54). Stemmer.
- Forsørgerbrøken faller i Loppa, Ibestad, Vevelstad og Lødingen. Stemmer.
- Topp ti per 100 i alderen 20–64 år i 2050: Rekkefølgen avviker litt fordi indeksen er regnet uten mellomavrunding. Bindal får 15,7 i stedet for 15,8.

## Rapporten (sidetall i PDF-en, som er lik trykt side)

| Påstand i notatet | Funnet | Side |
|---|---|---|
| Overordnet vurdering «Kritikkverdig» | ja | 10 |
| 33 av 60 kommuner planlegger ingen økning | ja | 34 |
| 31 % for få sykehjemsplasser, 43 % for få heldøgns omsorgsplasser | ja | 16 og 56 |
| 31 kommuner uten demensplasser (s. 17) mot 28 (s. 58) | ja, rapporten motsier seg selv | 17 og 58 |
| Demens «meir enn dobla fram mot 2040» mot «nær dobla innan 2050» | ja, rapporten motsier seg selv | 16, 54 og 119 |
| Forsørgerbrøk 0,32 (2024) → 0,48 (2050) | ja | 12 |
| Institusjonsbrukere 80+ −16 %, hjemmetjenester −3 % | ja | 15 og 50 |
| Årsverk +32 000 (+28 %) 2015–2025 | ja | 20 og 67 |
| Mangel på egnede boliger størst i de nordligste fylkene | ja | 18 og 65 |
| 2–3 allmennsykepleiere per fylke i nord mot 9–18 | ja | 75 |
| Nordland: om lag 76 % søkte tilskudd i 2024 og 2025 (31 av 41) | ja | 72 |
| Utbetalt tilskudd Nordland 27,6 / 34,3 / 20,0 mill. kr (2019 / 2020 / 2024) | ja | 72 |
| Rendalen, Bindal, Vevelstad, Beiarn, Osen og Ibestad rundt 30 % over 67 år | ja | 49 |
| «To av tre kommuner har vansker med å rekruttere og beholde» | ikke funnet med denne ordlyden | – |

Påstanden om rekruttering er ikke brukt i dashbordet.

## Rettet i dashbordet

- Tema 05: «SSB: 46» er endret til 47 (SSB 14751 gir 0,47; 14746 gir 1 590 452 / 3 380 581 = 0,4705), også i metodesiden. Fylkestallene på siden stemmer med 14746.
