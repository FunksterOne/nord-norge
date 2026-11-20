# Kontroll av NAV-data for de 80 kommunene (fase 2)

Generert av `analyse/nav/skript/kontroll.py` fra `nav_kommuner.json`.

## 1. Summen av kommunene mot NAVs fylkestall

Sammenlignet der inndelingen er lik. Antall skal være likt. For prosent er avviket avrunding, fordi NAV oppgir fylkesandelen med én desimal og vi regner den av kommunene.

| Kategori | Sammenligninger | Avvik i antall | Største avvik i prosent (pp) |
|---|---|---|---|
| helt_ledige | 766 | 0 | 0,06 |
| aap | 538 | 0 | 0,06 |
| nedsatt | 622 | 0 | 0,07 |
| ufore | 98 | 0 | 0,00 |

I 224 sammenligninger inneholder fylkessummen prikkede kommuner, telt som 1,5. Største avvik fra NAVs fylkestall er da 5 personer og 0,06 prosentpoeng. Disse månedene er merket `anslatt_mnd` i dataene og regnes ikke som avvik.

Kjent avvik i NAVs egen fil (ikke regnet som feil): ufore 2017 2017-12 Nord-Norge antall: sum 35624 | NAV 35625. Troms-kommunene i utgaven for desember 2019 summerer til 11 297, mens NAVs fylkessum er 11 298.

## 2. Dekning per kategori og år

Antall kommuner av 80 med tall for hele perioden, med prikkede måneder, med brudd (Narvik og Hamarøy) og med beregnede tall (sammenslåing uten NAVs omregning).

| Kategori | Periode | Med tall | Prikket (minst én måned) | Brudd | Beregnet |
|---|---|---|---|---|---|
| helt_ledige | 2012 | 78 | 0 | 2 | 4 |
| helt_ledige | 2013 | 78 | 0 | 2 | 3 |
| helt_ledige | 2014 | 77 | 2 | 2 | 3 |
| helt_ledige | 2015 | 78 | 4 | 2 | 3 |
| helt_ledige | 2016 | 78 | 4 | 2 | 3 |
| helt_ledige | 2017 | 78 | 5 | 2 | 3 |
| helt_ledige | 2018 | 77 | 8 | 2 | 3 |
| helt_ledige | 2019 | 77 | 8 | 2 | 3 |
| helt_ledige | 2020 | 79 | 3 | 0 | 0 |
| helt_ledige | 2021 | 78 | 5 | 0 | 0 |
| helt_ledige | 2022 | 79 | 7 | 0 | 0 |
| helt_ledige | 2023 | 78 | 9 | 0 | 0 |
| helt_ledige | 2024 | 80 | 5 | 0 | 0 |
| helt_ledige | 2025 | 78 | 5 | 0 | 0 |
| helt_ledige | 2026 | 79 | 7 | 0 | 0 |
| aap | 2010 | 78 | 0 | 2 | 3 |
| aap | 2011 | 78 | 0 | 2 | 3 |
| aap | 2012 | 78 | 0 | 2 | 3 |
| aap | 2013 | 78 | 0 | 2 | 3 |
| aap | 2014 | 78 | 0 | 2 | 3 |
| aap | 2015 | 78 | 0 | 2 | 3 |
| aap | 2016 | 78 | 0 | 2 | 3 |
| aap | 2017 | 78 | 0 | 2 | 3 |
| aap | 2018 | 78 | 0 | 2 | 3 |
| aap | 2019 | 78 | 0 | 2 | 3 |
| aap | 2020 | 80 | 0 | 0 | 0 |
| aap | 2021 | 80 | 0 | 0 | 0 |
| aap | 2022 | 80 | 0 | 0 | 0 |
| aap | 2023 | 80 | 0 | 0 | 0 |
| aap | 2024 | 79 | 0 | 0 | 0 |
| aap | 2025 | 80 | 0 | 0 | 0 |
| aap | 2026 | 80 | 0 | 0 | 0 |
| nedsatt | 2016 | 78 | 0 | 2 | 3 |
| nedsatt | 2017 | 78 | 0 | 2 | 3 |
| nedsatt | 2018 | 78 | 0 | 2 | 3 |
| nedsatt | 2019 | 78 | 0 | 2 | 3 |
| nedsatt | 2020 | 80 | 0 | 0 | 0 |
| nedsatt | 2021 | 80 | 0 | 0 | 0 |
| nedsatt | 2022 | 80 | 0 | 0 | 0 |
| nedsatt | 2023 | 80 | 0 | 0 | 0 |
| nedsatt | 2024 | 80 | 0 | 0 | 0 |
| nedsatt | 2025 | 80 | 0 | 0 | 0 |
| nedsatt | 2026 | 80 | 0 | 0 | 0 |
| ufore | 2010-12 | 0 | 0 | 2 | 4 |
| ufore | 2011-12 | 0 | 0 | 2 | 4 |
| ufore | 2012-12 | 78 | 1 | 2 | 3 |
| ufore | 2013-12 | 78 | 0 | 2 | 3 |
| ufore | 2014-12 | 78 | 0 | 2 | 3 |
| ufore | 2015-12 | 78 | 0 | 2 | 3 |
| ufore | 2016-12 | 78 | 0 | 2 | 3 |
| ufore | 2017-12 | 78 | 0 | 2 | 3 |
| ufore | 2018-12 | 80 | 0 | 0 | 0 |
| ufore | 2019-12 | 80 | 0 | 0 | 0 |
| ufore | 2020-12 | 80 | 0 | 0 | 0 |
| ufore | 2021-12 | 80 | 0 | 0 | 0 |
| ufore | 2022-12 | 80 | 0 | 0 | 0 |
| ufore | 2023-12 | 80 | 0 | 0 | 0 |
| ufore | 2024-12 | 80 | 0 | 0 | 0 |
| ufore | 2025-09 | 80 | 0 | 0 | 0 |
| ufore | 2026-09 | 80 | 0 | 0 | 0 |
| pensjon | 2016 | 80 | 0 | 0 | 0 |
| pensjon | 2017 | 80 | 0 | 0 | 0 |
| pensjon | 2018 | 80 | 0 | 0 | 0 |
| pensjon | 2019 | 80 | 0 | 0 | 0 |
| pensjon | 2020 | 80 | 0 | 0 | 0 |
| pensjon | 2021 | 80 | 0 | 0 | 0 |
| pensjon | 2022 | 80 | 0 | 0 | 0 |
| pensjon | 2023 | 80 | 0 | 0 | 0 |
| pensjon | 2024 | 80 | 0 | 0 | 0 |
| pensjon | 2025 | 80 | 0 | 0 | 0 |
| pensjon | 2026 | 80 | 0 | 0 | 0 |

## 3. Prikking i helt ledige

NAV erstatter tall under 4 med «*». For hvert kommuneår med prikkede måneder er årssnittet regnet på tre måter: av de publiserte månedene (slik `fetch_nav.py` gjør), med de prikkede satt til 0 og med de prikkede satt til 3. Prosent er antall delt på arbeidsstyrken, anslått som median(antall/andel) i året.

Fra 20.11.2026 regner `fetch_nav.py` prikkede måneder som 1,5 (kolonnen «Brukt»), og viser ikke snitt når mer enn halvparten av månedene er prikket.

| Kommune | År | Prikkede måneder | Publiserte måneder (%) | Prikket = 0 (%) | Prikket = 3 (%) | Brukt (%) |
|---|---|---|---|---|---|---|
| Bindal | 2018 | 1 av 12 | 1,19 | 1,11 | 1,15 | 1,11 |
| Bindal | 2019 | 4 av 12 | 1,20 | 0,79 | 0,94 | 0,88 |
| Vega | 2022 | 1 av 12 | 1,22 | 1,11 | 1,16 | 1,14 |
| Vega | 2023 | 2 av 12 | 1,41 | 1,17 | 1,25 | 1,22 |
| Vega | 2024 | 2 av 12 | 1,39 | 1,17 | 1,25 | 1,20 |
| Vevelstad | 2014 | 7 av 12 | 1,33 | 0,90 | 1,69 | – |
| Vevelstad | 2015 | 2 av 12 | 2,48 | 2,06 | 2,28 | 2,17 |
| Vevelstad | 2016 | 4 av 12 | 1,65 | 1,09 | 1,47 | 1,29 |
| Vevelstad | 2017 | 1 av 12 | 2,00 | 1,83 | 1,93 | 1,88 |
| Vevelstad | 2018 | 9 av 12 | 1,70 | 0,42 | 1,38 | – |
| Vevelstad | 2019 | 12 av 12 | – | – | – | – |
| Vevelstad | 2020 | 12 av 12 | – | – | – | – |
| Vevelstad | 2021 | 12 av 12 | – | – | – | – |
| Vevelstad | 2022 | 12 av 12 | – | – | – | – |
| Vevelstad | 2023 | 12 av 12 | – | – | – | – |
| Vevelstad | 2024 | 5 av 12 | 2,26 | 1,31 | 1,90 | 1,61 |
| Vevelstad | 2025 | 12 av 12 | – | – | – | – |
| Vevelstad | 2026 | 9 av 10 | 2,30 | 0,23 | 1,47 | – |
| Grane | 2022 | 3 av 12 | 0,77 | 0,58 | 0,69 | 0,63 |
| Grane | 2023 | 3 av 12 | 1,18 | 0,89 | 0,99 | 0,94 |
| Grane | 2026 | 1 av 10 | 1,24 | 1,11 | 1,16 | 1,14 |
| Hattfjelldal | 2019 | 2 av 12 | 0,87 | 0,74 | 0,81 | 0,76 |
| Hattfjelldal | 2020 | 6 av 12 | 1,30 | 0,65 | 0,87 | 0,76 |
| Hattfjelldal | 2021 | 7 av 12 | 0,98 | 0,40 | 0,66 | – |
| Hattfjelldal | 2022 | 6 av 12 | 0,70 | 0,34 | 0,56 | 0,46 |
| Hattfjelldal | 2023 | 3 av 12 | 0,94 | 0,71 | 0,83 | 0,77 |
| Hattfjelldal | 2024 | 5 av 12 | 0,83 | 0,48 | 0,68 | 0,58 |
| Hattfjelldal | 2025 | 1 av 12 | 1,00 | 0,92 | 0,96 | 0,94 |
| Dønna | 2019 | 1 av 12 | 1,15 | 1,04 | 1,07 | 1,07 |
| Dønna | 2022 | 1 av 12 | 0,97 | 0,88 | 0,91 | 0,91 |
| Lurøy | 2018 | 3 av 12 | 0,97 | 0,73 | 0,81 | 0,77 |
| Træna | 2014 | 1 av 12 | 2,77 | 2,72 | 2,81 | 2,76 |
| Træna | 2015 | 1 av 12 | 3,89 | 3,57 | 3,67 | 3,62 |
| Træna | 2017 | 5 av 12 | 3,37 | 1,97 | 2,47 | 2,22 |
| Træna | 2018 | 5 av 12 | 2,63 | 1,53 | 2,03 | 1,78 |
| Træna | 2019 | 1 av 12 | 2,42 | 2,24 | 2,34 | 2,27 |
| Træna | 2020 | 2 av 12 | 3,76 | 3,14 | 3,36 | 3,24 |
| Træna | 2021 | 4 av 12 | 3,14 | 2,09 | 2,53 | 2,31 |
| Træna | 2023 | 1 av 12 | 2,58 | 2,33 | 2,43 | 2,42 |
| Træna | 2025 | 1 av 12 | 2,73 | 2,50 | 2,60 | 2,55 |
| Træna | 2026 | 1 av 10 | 2,94 | 2,65 | 2,78 | 2,71 |
| Rødøy | 2018 | 2 av 12 | 0,94 | 0,79 | 0,87 | 0,82 |
| Rødøy | 2019 | 4 av 12 | 0,97 | 0,65 | 0,81 | 0,73 |
| Rødøy | 2021 | 2 av 12 | 1,09 | 0,90 | 0,98 | 0,95 |
| Rødøy | 2023 | 1 av 12 | 1,05 | 0,98 | 1,02 | 0,99 |
| Beiarn | 2015 | 3 av 12 | 1,62 | 1,18 | 1,33 | 1,29 |
| Beiarn | 2017 | 5 av 12 | 1,69 | 0,98 | 1,23 | 1,11 |
| Beiarn | 2018 | 2 av 12 | 1,22 | 1,02 | 1,12 | 1,07 |
| Lødingen | 2023 | 1 av 12 | 1,50 | 1,36 | 1,39 | 1,39 |
| Evenes | 2026 | 1 av 10 | 1,08 | 0,99 | 1,03 | 0,99 |
| Røst | 2015 | 1 av 12 | 2,26 | 2,07 | 2,15 | 2,11 |
| Røst | 2016 | 2 av 12 | 2,95 | 2,46 | 2,63 | 2,54 |
| Røst | 2017 | 2 av 12 | 4,49 | 3,74 | 3,91 | 3,83 |
| Røst | 2018 | 2 av 12 | 2,68 | 2,22 | 2,39 | 2,32 |
| Røst | 2019 | 1 av 12 | 2,21 | 2,01 | 2,10 | 2,07 |
| Røst | 2022 | 4 av 12 | 2,46 | 1,65 | 2,02 | 1,83 |
| Røst | 2023 | 7 av 12 | 3,44 | 1,43 | 2,12 | – |
| Røst | 2024 | 2 av 12 | 3,08 | 2,57 | 2,77 | 2,67 |
| Røst | 2025 | 7 av 12 | 2,64 | 1,10 | 1,80 | – |
| Røst | 2026 | 2 av 10 | 6,15 | 4,92 | 5,15 | 5,04 |
| Dielddanuorri - Tjeldsund | 2016 | 2 av 12 | 2,16 | 1,80 | 1,83 | 1,82 |
| Ibestad | 2022 | 2 av 12 | 2,26 | 1,89 | 1,98 | 1,93 |
| Loabák - Lavangen | 2024 | 3 av 12 | 1,28 | 0,95 | 1,12 | 1,04 |
| Senja | 2016 | 1 av 12 | 2,06 | 1,88 | 1,89 | 1,89 |
| Senja | 2017 | 1 av 12 | 1,93 | 1,77 | 1,77 | 1,77 |
| Senja | 2018 | 1 av 12 | 1,80 | 1,65 | 1,65 | 1,65 |
| Senja | 2019 | 3 av 12 | 1,72 | 1,29 | 1,30 | 1,29 |
| Loppa | 2023 | 3 av 12 | 1,39 | 1,05 | 1,23 | 1,13 |
| Loppa | 2025 | 1 av 12 | 1,75 | 1,60 | 1,66 | 1,63 |
| Loppa | 2026 | 1 av 10 | 3,00 | 2,69 | 2,76 | 2,74 |
| Unjárga - Nesseby | 2021 | 1 av 12 | 2,34 | 2,15 | 2,21 | 2,17 |
| Unjárga - Nesseby | 2026 | 1 av 10 | 1,72 | 1,55 | 1,63 | 1,59 |

72 kommuneår har prikkede måneder. I 33 av dem ligger snittet av de publiserte månedene mer enn 0,3 prosentpoeng over snittet med de prikkede satt til 0.

## 4. Store endringer fra år til år

Endring i kommunens andel minus endringen i fylket. Terskler: helt ledige og AAP 1,5 pp, nedsatt arbeidsevne 2 pp, uføre 1,5 pp (desember til desember). Nevneren viser hvor mange personer andelen regnes av; små nevnere gir store utslag.

| Kategori | Kommune | Fra–til | Kommune (pp) | Fylke (pp) | Nevner | Merknad |
|---|---|---|---|---|---|---|
| helt_ledige | Moskenes | 2019–2020 | +7,23 | +1,84 | 541 |  |
| helt_ledige | Moskenes | 2021–2022 | -5,17 | -0,82 | 525 |  |
| helt_ledige | Beiarn | 2024–2025 | -4,00 | -0,01 | 467 |  |
| helt_ledige | Beiarn | 2023–2024 | +3,84 | +0,23 | 453 |  |
| nedsatt | Røst | 2024–2025 | -3,13 | +0,22 | 287 |  |
| helt_ledige | Træna | 2021–2022 | +2,45 | -0,82 | 250 |  |
| nedsatt | Kvænangen | 2017–2018 | -3,19 | -0,26 | 705 |  |
| helt_ledige | Herøy i Nordland | 2016–2017 | +2,48 | -0,39 | 875 |  |
| helt_ledige | Loppa | 2019–2020 | -0,66 | +2,09 | 418 |  |
| helt_ledige | Herøy i Nordland | 2013–2014 | -2,67 | -0,09 | 868 |  |
| helt_ledige | Herøy i Nordland | 2012–2013 | +2,77 | +0,20 | 841 |  |
| helt_ledige | Skjervøy | 2021–2022 | +1,72 | -0,83 | 1 398 |  |
| nedsatt | Røst | 2018–2019 | +1,93 | -0,50 | 325 |  |
| helt_ledige | Båtsfjord | 2012–2013 | +2,77 | +0,38 | 1 094 |  |
| ufore | Dønna | 2022-12–2023-12 | -2,76 | -0,40 | 835 |  |
| ufore | Vevelstad | 2019-12–2020-12 | +2,56 | +0,21 | 274 |  |
| nedsatt | Røst | 2025–2026 | -2,21 | +0,11 | 290 |  |
| helt_ledige | Træna | 2022–2023 | -2,34 | -0,02 | 250 |  |
| helt_ledige | Båtsfjord | 2022–2023 | +2,18 | -0,02 | 1 135 |  |
| helt_ledige | Hasvik | 2022–2023 | -2,21 | -0,02 | 447 |  |
| aap | Røst | 2011–2012 | +1,70 | -0,48 | 364 |  |
| helt_ledige | Hasvik | 2017–2018 | +1,91 | -0,27 | 509 |  |
| helt_ledige | Berlevåg | 2023–2024 | +2,52 | +0,38 | 468 |  |
| helt_ledige | Gamvik | 2012–2013 | +2,48 | +0,38 | 517 |  |
| ufore | Røst | 2014-12–2015-12 | +2,09 | -0,01 | 353 |  |
| helt_ledige | Ibestad | 2019–2020 | +0,26 | +2,33 | 619 |  |
| helt_ledige | Nordkapp | 2019–2020 | +4,10 | +2,09 | 1 673 |  |
| ufore | Loabák - Lavangen | 2023-12–2024-12 | -1,98 | +0,01 | 542 |  |
| ufore | Steigen | 2021-12–2022-12 | -2,23 | -0,28 | 1 546 |  |
| helt_ledige | Unjárga - Nesseby | 2023–2024 | -1,56 | +0,38 | 404 |  |
| helt_ledige | Gildeskål | 2020–2021 | +0,36 | -1,58 | 951 |  |
| ufore | Evenes | 2023-12–2024-12 | -2,03 | -0,10 | 813 |  |
| helt_ledige | Hasvik | 2012–2013 | +2,28 | +0,38 | 500 |  |
| ufore | Lødingen | 2015-12–2016-12 | +1,85 | -0,05 | 1 256 |  |
| aap | Røst | 2013–2014 | +1,80 | -0,10 | 345 |  |
| ufore | Hasvik | 2016-12–2017-12 | +1,95 | +0,08 | 670 |  |
| helt_ledige | Hattfjelldal | 2019–2020 | +0,00 | +1,84 | 658 |  |
| helt_ledige | Sør-Varanger | 2015–2016 | +1,70 | -0,10 | 5 695 |  |
| ufore | Dyrøy | 2013-12–2014-12 | +1,54 | -0,26 | 696 |  |
| helt_ledige | Loppa | 2017–2018 | +1,53 | -0,27 | 434 |  |
| ufore | Vevelstad | 2016-12–2017-12 | -1,58 | +0,22 | 301 |  |
| ufore | Unjárga - Nesseby | 2016-12–2017-12 | -1,70 | +0,08 | 556 |  |
| ufore | Vevelstad | 2022-12–2023-12 | -2,17 | -0,40 | 254 |  |
| ufore | Berlevåg | 2012-12–2013-12 | -2,24 | -0,47 | 675 |  |
| helt_ledige | Meløy | 2013–2014 | -1,85 | -0,09 | 3 233 |  |
| helt_ledige | Bindal | 2012–2013 | +1,96 | +0,20 | 693 |  |
| ufore | Flakstad | 2018-12–2019-12 | -1,18 | +0,58 | 766 |  |
| aap | Sømna | 2011–2012 | -2,20 | -0,48 | 1 250 |  |
| aap | Loabák - Lavangen | 2011–2012 | +1,20 | -0,52 | 576 |  |
| aap | Hattfjelldal | 2022–2023 | -1,36 | +0,36 | 721 |  |
| ufore | Loabák - Lavangen | 2017-12–2018-12 | +1,70 | -0,00 | 572 |  |
| ufore | Nesna | 2014-12–2015-12 | +1,68 | -0,01 | 1 160 |  |
| helt_ledige | Værøy | 2025–2026 | +1,71 | +0,02 | 330 |  |
| helt_ledige | Værøy | 2022–2023 | -1,71 | -0,02 | 359 |  |
| ufore | Gratangen - Rivtták | 2012-12–2013-12 | -1,69 | +0,00 | 668 |  |
| helt_ledige | Røst | 2016–2017 | +1,29 | -0,39 | 296 |  |
| helt_ledige | Gamvik | 2018–2019 | +1,56 | -0,12 | 611 |  |
| ufore | Ibestad | 2012-12–2013-12 | -1,67 | +0,00 | 827 |  |
| helt_ledige | Hasvik | 2023–2024 | +2,03 | +0,38 | 455 |  |
| ufore | Rødøy | 2014-12–2015-12 | +1,64 | -0,01 | 738 |  |
| helt_ledige | Herøy i Nordland | 2019–2020 | +0,19 | +1,84 | 846 |  |
| ufore | Nesna | 2019-12–2020-12 | +1,85 | +0,21 | 1 059 |  |
| aap | Røst | 2015–2016 | -1,84 | -0,20 | 345 | årssnitt → månedssnitt |
| ufore | Evenes | 2014-12–2015-12 | -1,65 | -0,01 | 813 |  |
| ufore | Træna | 2014-12–2015-12 | -1,63 | -0,01 | 301 |  |
| helt_ledige | Loabák - Lavangen | 2019–2020 | +0,71 | +2,33 | 448 |  |
| helt_ledige | Gamvik | 2017–2018 | -1,88 | -0,27 | 600 |  |
| ufore | Fauske | 2012-12–2013-12 | +1,44 | -0,16 | 5 964 |  |
| helt_ledige | Bardu | 2019–2020 | +0,75 | +2,33 | 2 263 |  |
| ufore | Grane | 2018-12–2019-12 | -1,00 | +0,58 | 870 |  |
| ufore | Vevelstad | 2017-12–2018-12 | -1,13 | +0,45 | 289 |  |
| ufore | Moskenes | 2019-12–2020-12 | -1,35 | +0,21 | 629 |  |
| aap | Hasvik | 2022–2023 | -1,47 | +0,09 | 619 |  |
| helt_ledige | Værøy | 2019–2020 | +3,40 | +1,84 | 373 |  |
| helt_ledige | Sørfold | 2019–2020 | +0,28 | +1,84 | 905 |  |
| aap | Gamvik | 2011–2012 | -2,00 | -0,45 | 700 |  |
| ufore | Træna | 2019-12–2020-12 | -1,34 | +0,21 | 295 |  |
| helt_ledige | Kvænangen | 2017–2018 | +1,33 | -0,22 | 570 |  |
| ufore | Beiarn | 2016-12–2017-12 | +1,75 | +0,22 | 610 |  |
| aap | Bindal | 2012–2013 | -1,60 | -0,07 | 886 |  |
| helt_ledige | Vardø | 2023–2024 | +1,91 | +0,38 | 961 |  |
| helt_ledige | Gáivuotna - Kåfjord - Kaivuono | 2019–2020 | +0,82 | +2,33 | 1 000 |  |
| helt_ledige | Gratangen - Rivtták | 2020–2021 | -0,46 | -1,97 | 519 |  |
| ufore | Træna | 2013-12–2014-12 | +1,39 | -0,12 | 302 |  |
| ufore | Sørfold | 2012-12–2013-12 | -1,66 | -0,16 | 1 191 |  |
| ufore | Evenes | 2021-12–2022-12 | -1,78 | -0,28 | 750 |  |

86 endringer over terskelen.

## 5. Uføreandel: NAV september 2025 mot SSB 11715 (2025)

80 kommuner, NAV minus SSB: median -0,55 pp, fra -1,93 til +0,68 pp,

| Kommune | NAV sept. 2025 (%) | SSB 2025 (%) | Forskjell (pp) |
|---|---|---|---|
| Dønna | 14,27 | 16,2 | -1,93 |
| Hattfjelldal | 13,55 | 15,2 | -1,65 |
| Unjárga - Nesseby | 9,64 | 10,9 | -1,26 |
| Sørfold | 14,30 | 15,5 | -1,20 |
| Bindal | 16,91 | 18,0 | -1,09 |
| Gratangen - Rivtták | 20,73 | 20,6 | +0,13 |
| Kvæfjord | 16,64 | 16,5 | +0,14 |
| Værøy | 9,18 | 8,8 | +0,38 |
| Loppa | 14,40 | 14,0 | +0,40 |
| Vevelstad | 16,38 | 15,7 | +0,68 |

