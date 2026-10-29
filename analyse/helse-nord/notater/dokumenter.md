# Dokumentregister — spesialisthelsetjenesten i Nord-Norge og helsepersonellplanleggingen

Utarbeidet 29. oktober 2026 som grunnlag for temasiden om sykehusene i nord. Status: registrert og kontrollert mot kildeteksten, ikke publisert.

## Konklusjon

De viktigste tallene for temasiden ligger i styresak 108-2026, ikke i selve planen. Den reviderte nasjonale framskrivingsmodellen (vedtatt 24. september 2026) gir Helse Nord 7,3 % vekst i somatiske liggedøgn og 12,8 % vekst i polikliniske kontakter fra 2025 til 2045. Landet får 20,2 % og 24,3 %. Befolkningen i Helse Nord er tilnærmet uendret (+0,4 %), mens gruppen 18–64 år faller med 6,7 % og gruppen 65 år og eldre øker med 26,5 %. Helgeland er eneste helseforetaksområde med befolkningsnedgang (-4,7 %).

Regional utviklingsplan 2027–2042 (RU42) finnes bare som nettsider. Den inneholder få egne tall. Framskrivningssiden viser til tabeller som ikke er publisert i HTML-versjonen per 29. oktober.

Innleie er Helse Nords særtrekk. I 2021 fant 35 % av all innleie i spesialisthelsetjenesten sted i Helse Nord, som hadde 12 % av årsverkene og 9 % av befolkningen (NOU 2023: 4). Innleien er redusert med om lag 100 mill. kroner fra 2025 til 2026 (januar–september). Reduksjonen skyldes i hovedsak UNN, mens Nordlandssykehuset fortsatt ligger høyt.

## Metode og forbehold

- **Grunnlag:** dokumenter lastet ned med curl 29. oktober 2026 til `analyse/helse-nord/kilder/` (gitignorert). Tekst er trukket ut med `pdftotext -enc UTF-8 -layout`. Tabeller med forskjøvne kolonner er kontrollert med en radvis gjenoppbygging (PyMuPDF), og tall avlest fra figurer er merket «avlest fra figur».
- **Sidetall:** «PDF-side» er sidetallet i den nedlastede filen. «Trykt s.» er sidetallet som står på siden. Helse Nords styresaker har i tillegg en løpende samlenummerering (for eksempel 57/774), som ikke er brukt. Nettsider har ikke sidetall; der er sidenavn og oppdateringsdato oppgitt.
- **Finne styredokumentene:** Helse Nords møtesider laster dokumentlistene med JavaScript. Listene er hentet fra nettstedets eget åpne dokument-API (`/api/graph-proxy`), det samme som siden bruker. Ingen innlogging er omgått.
- **Skille:** Under hvert dokument står det dokumentet sier. Mine vurderinger er merket **Vurdering**.

---

## A. Regional utviklingsplan 2027–2042 og grunnlaget for den

### A1. Regional utviklingsplan 2027–2042, høringsutkast (digital plan)

- **Utgiver:** Helse Nord RHF
- **Dato:** styrebehandlet 28.10.2026, høring 30.10.–11.12.2026. Sidene er oppdatert 20.–22.10.2026.
- **URL:** https://www.helse-nord.no/regional-utviklingsplan-helse-nord/
- **Lokal fil:** `kilder/rup-web/<side>.txt` (27 sider, alle undersider gjennomgått, med HTML ved siden av)
- **Merk:** Det finnes ingen PDF. Styresak 127-2026 bekrefter at planen er «heldigital» (PDF-side 5). «Drivere for endring første fire år» er et avsnitt på hver målområdeside, ikke en egen side.

Nøkkeltall og funn:
1. Somatiske liggedøgn ventes å øke med 7,3 % og polikliniske kontakter med 12,8 % mot 2045 (side «Utfordringer og muligheter»). Tallene samsvarer med 108-2026, tabell 28 og 44. Planen kaller det «liggedøgn», ikke «døgnopphold».
2. Liggedøgn somatikk øker «ca. 7 prosent» mot 2040, mot «rundt 20 prosent» ved ren demografi. Psykisk helsevern: -2 % ved befolkningsendring, +1 % samlet behov mot 2040 (side «Framskrivning og demografi»). Tabellene siden viser til, mangler i HTML.
3. Nord-Norge har under 9 % av Norges befolkning. Fra 2023 var det flere over 65 år enn under 19 år (side «Utfordringer og muligheter»).
4. Helse Nord har «vesentlig mer innleie enn de andre helseregionene» og «beholder for få» av dem som utdannes (samme side). Ikke tallfestet.
5. Sykehusnivåene: regionsykehus UNN Tromsø, stort akuttsykehus NLSH Bodø, åtte akuttsykehus (Hammerfest, Kirkenes, Vesterålen, Lofoten, Mo i Rana, Sandnessjøen, Narvik, Harstad) og ett sykehus uten akuttfunksjoner (Mosjøen) (målområde «Samhandling og samarbeid»).
6. Om lag 95 % av somatiske akuttpasienter ble ikke akutt overført til annet sykehus (samme side).
7. Pandemitiltak som ble permanente, har gitt en bemanningsvekst på om lag 2 000 årsverk. UNN og FIN er under 2019-nivået for innleie (temaside «Økonomi»).
8. Basisfinansieringen ventes redusert med om lag 100 mill. kroner årlig på grunn av relativt redusert behov (temaside «Økonomi»).
9. Bygningsmassen er om lag 620 000 m² med en verdi på rundt 16 mrd. kroner. Vedlikeholdsetterslepet er om lag 8,5 mrd. kroner (temaside «Bygg, eiendom og MTU»).
10. IKT-andelen av omsetningen i spesialisthelsetjenesten økte fra 4–5 % (2018) til 5–7 % (2024) (temaside «Digitalisering og IKT»).
11. Helse Nord har høy til middels måloppnåelse på 81 % av 300 kvalitetsindikatorer (side «Status i norsk helsevesen»).

**Vurdering.** Punkt 7 står i strid med Årlig melding 2025 (B3, punkt 7), som sier at NLSH og UNN fortsatt lå over 2019-nivået i 2025. Planen ser ut til å bruke 2026-tall for UNN. Det bør avklares i høringen.

### A2. Styresak 127-2026 Regional utviklingsplan 2027–2042 – høring (med høringsbrev)

- **Utgiver:** Helse Nord RHF, styret
- **Dato:** saksframlegg 21.10.2026, møte 28.10.2026
- **URL:** https://www.helse-nord.no/4aa4cc/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20261028/styresak-127-2026-regional-utviklingsplan-2027-2042---horing.pdf
- **Lokal fil:** `kilder/styresak-127-2026-rup-horing.pdf` (+ `.txt`)

Nøkkeltall og funn:
1. Tabell 1 «Framskriving befolkningsutvikling 2025–2045» (bilde, PDF-side 3): Nord -6,5 % (0–17 år), -6,7 % (18–64 år), 26,5 % (65+), 0,4 % totalt. Landet: -0,7 %, 2,5 %, 42,4 %, 9,4 %. Tallene er identiske med 108-2026, tabell 3.
2. «Mindre enn ti av Nord-Norges 80 kommuner» ventes å få befolkningsvekst (PDF-side 2).
3. Planen skal møte de fem største risikoene fra styresak 62-2026 (PDF-side 3).
4. Høringsfrist 11.12.2026. Endelig plan til styret i februar 2027 (PDF-side 1 og 5).
5. 19 av 80 kommuner og Sametinget ga skriftlige innspill før utkastet ble ferdig (vedlegg 1, PDF-side 7).
6. Sametinget vil at det samiske perspektivet skal være et gjennomgående strategisk premiss, ikke et særtema (PDF-side 7).
7. Høringsbrevet (vedlegg 4, PDF-side 14–15) har tittelen «Regional utviklingsplan 2026–2042», og drøftingsprotokollen skriver «2027–2024» (PDF-side 5). Begge er skrivefeil i kilden.

**Vurdering.** I tabell 1 står kolonnen som «> 65 år», mens kilden (108-2026) bruker «65 år og eldre». Tallene er de samme, så det er trolig bare en etikettfeil.

### A3. Styresak 108-2026 Revisjon av framskrivningsmodeller for aktivitetsbehov innen somatikk, psykisk helsevern og TSB

- **Utgiver:** Helse Nord RHF. Den nasjonale modellen er laget i et samarbeid mellom de regionale helseforetakene, ledet av Helse Sør-Øst og med Sykehusbygg HF.
- **Dato:** saksframlegg 17.9.2026, møte 24.9.2026. Vedleggsrapportene er datert 26.8.2026.
- **URL:** https://www.helse-nord.no/4a67d0/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20260924/styresak-108-2026-revisjon-av-framskrivningsmodeller-for-aktivitetsbehov-innen-somatikk-psykisk-helsevern-og-tverrfaglig-spesialisert-rusbehandling.pdf
- **Lokal fil:** `kilder/hn-styresak-108-2026-revisjon-av-framskrivningsmodeller-for-aktivitetsbehov-innen-somatikk.pdf` (179 sider). PHV/TSB-rapporten er på PDF-side 13–104, somatikkrapporten på PDF-side 105–179.
- **Grunnlag:** aktiviteten i 2025, SSBs befolkningsframskriving fra 2026 (hovedalternativet), framskrevet til 2045 (PDF-side 3).

Nøkkeltall og funn:
1. Befolkning 2025–2045 (tabell 3, PDF-side 114, trykt s. 10): Helse Nord 487 729 → 489 893 (+0,4 %). FIN +2,3 %, HSYK -4,7 %, NLSH -0,5 %, UNN +2,4 %.
2. Befolkningen 65 år og eldre øker med 26,5 % i Helse Nord. Gruppen 18–64 år faller med 6,7 %, mest på Helgeland (-12,4 %) (samme tabell).
3. Somatiske liggedøgn, Helse Nord: 314 111 → 337 071 (+7,3 %). Ren demografi gir 392 032 (tabell 28, PDF-side 158, trykt s. 54).
4. Per helseforetak: FIN +17,6 %, HSYK +8,6 %, NLSH +5,6 %, UNN +5,8 % (samme tabell).
5. Polikliniske kontakter somatikk, Helse Nord: 695 715 → 784 648 (+12,8 %). FIN +15,2 %, HSYK +9,4 %, NLSH +12,2 %, UNN +13,6 % (tabell 44, PDF-side 171, trykt s. 67).
6. Landet: liggedøgn +20,2 % (ren demografi +32,3 %), poliklinikk +24,3 % (ren demografi +17,6 %) (PDF-side 5–6).
7. Regional forskjell: liggedøgn somatikk +23,3 % i Helse Sør-Øst mot +7,3 % i Helse Nord. VOP-liggedøgn +16,5 % mot +1,8 % (PDF-side 10).
8. Psykisk helsevern voksne, Helse Nord: liggedøgn +1,8 %, poliklinikk +1,7 %. Landet: +13,1 % og +13,3 % (tabell 39 og 41, PDF-side 92 og 94).
9. TSB, Helse Nord: liggedøgn -6,0 %, poliklinikk +5,0 %. Landet: +0,2 % og +14,7 % (tabell 48 og 50, PDF-side 100–101).
10. Avgrensning: modellen gjelder ordinær drift. Beredskap «følger egne prosesser» (PDF-side 10).
11. Avgrensning: modellen bygger på dagens organisering. Helsereformutvalget og andre reformer kan kreve revisjon (PDF-side 10).

**Vurdering.** Døgnplasser framskrives ikke i modellen. Kapasitet (senger, beleggsprosent) må beregnes separat (PDF-side 10). For temasiden betyr det at «døgnplasser» ikke kan hentes herfra.

### A4. Styresak 62-2026 Vurdering av risiko i Helse Nord (og 130-2026 Prioritert plan for risikohåndtering)

- **Utgiver:** Helse Nord RHF
- **Dato:** 62-2026: saksframlegg 20.5.2026, møte 27.5.2026. 130-2026: saksframlegg 21.10.2026, møte 28.10.2026.
- **URL:** https://www.helse-nord.no/49b35c/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20260527/styresak-62-2026-vurdering-av-risiko-i-helse-nord.pdf og https://www.helse-nord.no/4aab47/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20261028/styresak-130-2026-prioritert-plan-for-risikohandtering--oppfolging-av-styresak-62-2026.pdf
- **Lokal fil:** `kilder/hn-styresak-62-2026-vurdering-av-risiko-i-helse-nord.pdf`, `kilder/hn-styresak-130-2026-prioritert-plan-for-risikohandtering--oppfolging-av-styresak-62-2026..pdf`

Nøkkeltall og funn:
1. Fem største risikoer (tabell 1, PDF-side 4). Omstillingsevne/økonomi: kritisk. Fagpersonell, samhandling, vedlikeholdsetterslep og beredskap: høy.
2. Omstillingsbehovet i 2026 er om lag 576 mill. kroner (2,1 % av omsetningen) (vedlegg 1, PDF-side 7).
3. Omstillingsbehovet for 2026–2029 er beregnet til 2,3 mrd. kroner (PDF-side 8).
4. Helse Nord bruker 28 % flere årsverk per innbygger enn resten av landet (2022), mot 22 % i 2015 (PDF-side 8).
5. Det er størst mangel på sykepleiere, helsefagarbeidere, enkelte legespesialiteter, psykisk helsepersonell, laboratoriepersonell og teknisk/IKT-personell. På kort sikt trengs bioingeniører, audiografer og jordmødre (PDF-side 8).
6. Vedlikeholdsetterslepet er 8,5 mrd. kroner. Det kritiske vedlikeholdsbehovet har økt med 4 mrd. kroner på fire år (PDF-side 9).
7. 130-2026 legger fram tiltak, men inneholder ingen nye tall (PDF-side 1–2, gjennomgått overflatisk).

### A5. Styresak 139-2025 Arbeid med utviklingsplaner og føringer for revisjon av RU 2023–2038

- **Utgiver:** Helse Nord RHF
- **Dato:** saksframlegg 11.12.2025, møte 18.12.2025
- **URL:** https://www.helse-nord.no/4aeb55/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2025/20251218/styresak-139-2025-arbeid-med-utviklingsplaner-og-foringer-for-revisjon-av-regional-utviklingsplan-2023-2038---oppdatert-veileder.pdf
- **Lokal fil:** `kilder/hn-styresak-139-2025-revisjon-ru-veileder.pdf`

Nøkkeltall og funn:
1. Helseforetakenes lokale utviklingsplaner revideres ikke. RU42 erstatter dem (PDF-side 1, og 127-2026 PDF-side 2).
2. Revidert nasjonal veileder for utviklingsplaner er lagt til grunn. Den gir en mer fleksibel planstruktur (PDF-side 1–2).

Gjennomgått bare for formål og vedtak. Ingen tall er registrert.

### A6. Regional utviklingsplan for Helse Nord 2023–2038 (gjeldende plan)

- **Utgiver:** Helse Nord RHF
- **Dato:** vedtatt 14.12.2022 (styresak 179-2022)
- **URL:** https://www.helse-nord.no/499f58/siteassets/dokumenter-og-blokker/3-helsefaglig/fagplaner-og-rapporter/regional-utviklingsplan-2038/regional-utviklingsplan-20232038-del-1-analyse-og-veivalg-vedtatt-14.12.22-styresak-1792022.pdf og …-del-2-rammer-og-forutsetninger-vedtatt-14.12.22-styresak-1792022.pdf
- **Lokal fil:** `kilder/hn-regional-utviklingsplan-20232038-del-1-…pdf` (14 sider), `…-del-2-…pdf` (54 sider)

Nøkkeltall og funn:
1. Helse Nord har sørge for-ansvar for om lag 9 % av befolkningen og utdanner 20 % av landets leger (del 1, PDF-side 4).
2. Opptaksområder: FIN ca. 76 000 og HSYK ca. 78 000 innbyggere (del 2, PDF-side 6). NLSH ca. 138 000 (del 2, PDF-side 23).
3. Ifølge inFutures trendanalyse må antall årsverk øke med 35 % fram mot 2035 dersom behovet skal dekkes med dagens måte å løse oppgavene på (del 2, PDF-side 41).

**Vurdering.** Planen er erstattet av framskrivingene i 108-2026. Bruk den bare som historisk sammenligning.

---

## B. Økonomi, personell og innleie i Helse Nord

### B1. Strategi for personell, utdanning og kompetanse i Helse Nord (2023), regional handlingsplan 2024–2026 og internrevisjon 1/2026

- **Utgiver:** Helse Nord RHF
- **Dato:** strategien er vedtatt 26.4.2023 (styresak 40-2023). Handlingsplanen er vedtatt i styresak 54-2024. Internrevisjonen er behandlet i styresak 18-2026 (25.2.2026).
- **URL:** https://www.helse-nord.no/49a881/siteassets/dokumenter-og-blokker/3-helsefaglig/fagplaner-og-rapporter/rapporter-og-dokumenter/strategi-for-personell-utdanning-og-kompetanse-i-helse-nord.pdf ; https://www.helse-nord.no/4a5606/siteassets/dokumenter-og-blokker/3-helsefaglig/fagplaner-og-rapporter/rapporter-og-dokumenter/regional-handlingsplan-for-personell-utdanning-og-kompetanse-2024-2026.pdf ; https://www.helse-nord.no/4921a0/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20260225/styresak-18-2026-internrevisjonsrapport-1-2026-helse-nord-rhfs-oppfolging-av-strategi-for-personell-utdanning-og-kompetanse.pdf
- **Lokal fil:** `kilder/personell/hn-strategi-personell-utdanning-kompetanse-2023.pdf`, `kilder/personell/hn-regional-handlingsplan-personell-2024-2026.pdf`, `kilder/hn-styresak-18-2026-…pdf`

Nøkkeltall og funn:
1. Helse Nord har 24 % flere leger og sykepleiere per innbygger enn resten av landet (2021), mot 10 % i 2008. Tallet gjelder faste årsverk (strategien, PDF-side 6).
2. Faste legeårsverk økte med 55 % (670) og sykepleierårsverk med 35 % (1 172) fra 2008 til 2021. Befolkningen økte med 4 % (PDF-side 6).
3. Regionen utdanner om lag 20 % av landets leger og 14 % av sykepleierne (PDF-side 8).
4. Handlingsplanens tiltak er blant annet Tørn-programmet, LISKART og kartlegging av turnover. Turnover er ikke tallfestet (handlingsplanen, PDF-side 5–8).
5. Internrevisjonen anbefaler en overordnet tidsplan, mer avgrensede tiltak, tydelig ansvar og frister og risikovurdering av tiltakene (18-2026, PDF-side 2).

**Ikke funnet:** en egen «Helsepersonellplan 2035», bemanningsplan eller regional helsepersonellplan med framskrevne tall for Helse Nord. Strategien (mot 2038) og handlingsplanen er de nærmeste. Turnover er ikke tallfestet i noen av de gjennomgåtte dokumentene.

### B2. Styresak 31-2026 Årlig melding 2025 for Helse Nord RHF

- **Utgiver:** Helse Nord RHF
- **Dato:** saksframlegg 6.3.2026, møte 13.3.2026
- **URL:** https://www.helse-nord.no/493690/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20260313/styresak-31-2026-arlig-melding-2025-for-helse-nord-rhf.pdf
- **Lokal fil:** `kilder/hn-styresak-31-2026-arlig-melding-2025-for-helse-nord-rhf.pdf` (105 sider)

Nøkkeltall og funn:
1. Foreløpig regnskapsresultat 2025: om lag +5 mill. kroner. Sykehusforetakene hadde samlet et underskudd på 193 mill. kroner (PDF-side 11, trykt s. 6).
2. Omstillingsbehov 2026: 576 mill. kroner. Det forutsetter om lag 300 færre egne årsverk og om lag 83 mill. kroner mindre innleie (PDF-side 9, trykt s. 4).
3. Helse Nord fikk ca. 215 mill. kroner i særskilt finansiering til rekruttering og stabilisering (PDF-side 9).
4. Pakkeforløp kreft: 59 % innen standard tid i 2025, mot 64 % i 2024. Målet er 70 % (PDF-side 9).
5. Sykefravær: 8,1 % i 2019 og 9,5 % i 2024. Nivået holdt seg i 2025 (PDF-side 29, trykt s. 24).
6. Akuttfunksjonene for somatikk er flyttet fra Mosjøen til Sandnessjøen og Mo i Rana, med døgnkontinuerlig slagalarm i Mosjøen (PDF-side 9 og 13).
7. Kravet om innleie ned på 2019-nivå er delvis nådd. NLSH og UNN lå over 2019-nivået (vedlegg, PDF-side 67, trykt s. 19).
8. Andel helsefagarbeidere av årsverk (krav minst 5 %): bare NLSH oppfyller kravet. HSYK har 4,7 %, FIN 3,7 % og UNN 3,2 % (PDF-side 67).
9. Nye sykehusbygg i Hammerfest og Narvik er tatt i bruk (PDF-side 9).

### B3. Virksomhetsrapport for september 2026 (styresak 126-2026)

- **Utgiver:** Helse Nord RHF
- **Dato:** møte 28.10.2026
- **URL:** https://www.helse-nord.no/4aae27/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20261028/styresak-126-2026-virksomhetsrapport-for-september-2026.pdf
- **Lokal fil:** `kilder/hn-styresak-126-2026-virksomhetsrapport-for-september-2026.pdf`. Rapporten for august (styresak 107-2026) er også lastet ned, men ikke brukt.

Nøkkeltall og funn:
1. Innleiekostnadene er om lag 100 mill. kroner lavere enn per september 2025. Nivået er det laveste på flere år (PDF-side 2).
2. Innleie fra firma per september: ca. 166 mill. kroner, ca. 40 mill. kroner over budsjett. Bare i september ble det bokført vel 17 mill. kroner (PDF-side 26, trykt s. 23).
3. Innleie januar–september per helseforetak, avlest fra figur 25 (mill. kroner, 2026 / 2025 / 2019): FIN 19 / 23 / 50, UNN 36 / 128 / 70, NLSH 88 / 90 / 49, HSYK 26 / 26 / 23. Sum 168 / 268 / 192 (PDF-side 27, trykt s. 24).
4. Brutto månedsverk inkl. innleie, snitt siste tre måneder: 16 372, ca. 82 færre enn året før (PDF-side 24, trykt s. 21).
5. Sykefravær i september: 7,85 % (PDF-side 27).
6. Utskrivningsklare pasienter: ca. 18 200 døgn og en anslått merkostnad på ca. 219 mill. kroner per september (PDF-side 24).
7. Resultat per september: om lag +30 mill. kroner, ca. 110 mill. kroner svakere enn budsjett (PDF-side 2).

**Vurdering.** Teksten oppgir 166 mill. kroner, mens figuren summerer til 168. Forskjellen skyldes trolig avrunding eller ulik periode. Månedsverk per helseforetak finnes bare som figurer (PDF-side 34–35). Bare UNN (7 482) og HSYK (1 835) er avlest for september 2026, fordi etikettene for FIN og NLSH overlapper.

### B4. Styresak 128-2026 Budsjett 2027, foretaksgruppen – rammer og føringer

- **Utgiver:** Helse Nord RHF
- **Dato:** møte 28.10.2026
- **URL:** https://www.helse-nord.no/4aa4cc/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2026/20261028/styresak-128-2026-budsjett-2027-foretaksgruppen---rammer-og-foringer.pdf
- **Lokal fil:** `kilder/hn-styresak-128-2026-budsjett-2027-foretaksgruppen---rammer-og-foringer.pdf`. Styresak 129-2026 (Helse Nord RHFs eget budsjett) er lastet ned, men ikke brukt.

Nøkkeltall og funn:
1. Resultatkrav 2027: +239 mill. kroner samlet. FIN +40, UNN +30, NLSH +25, HSYK +1 og Helse Nord RHF/felles +10 mill. kroner (PDF-side 1).
2. Omstillingsbehov 2027: 382 mill. kroner (1,6 %). FIN 19 (0,6 %), UNN 119 (1,0 %), NLSH 169 (2,6 %) og HSYK 75 (2,5 %) mill. kroner (PDF-side 5).
3. Produktiviteten er 3,3 % lavere enn i 2019, tilsvarende 375 mill. kroner (SAMDATA 2025) (PDF-side 6).
4. 7 mill. kroner er bevilget til beredskap og 14 mill. kroner til psykisk helsevern (PDF-side 4).

### B5. Nordlandssykehuset styresak 040-2026 Innleie av helsepersonell fra firma

- **Utgiver:** Nordlandssykehuset HF
- **Dato:** 16.5.2026, møte 20.5.2026
- **URL:** https://www.nordlandssykehuset.no/49a89b/siteassets/documents/styret-i-nordlandssykehuset/styremoter-2026/20.-mai/styresak-040-2026-innleie-av-helsepersonell-fra-firma-m_vedlegg.pdf
- **Lokal fil:** `kilder/nlsh-styresak-040-2026-innleie-av-helsepersonell-fra-firma-m_vedlegg.pdf`

Nøkkeltall og funn:
1. Samlet innleie fra firma: 71,4 (2019), 165,1 (2021), 154,7 (2022), 138,9 (2023), 113,9 (2024) og 127,3 (2025) mill. kroner (tabell 1, PDF-side 4).
2. Per lokasjon i 2025: Bodø 65,5, Lofoten 24,6 og Vesterålen 37,2 mill. kroner (tabell 3, PDF-side 6).
3. 69 % av innleien i 2025 var legeinnleie (tabell 2, PDF-side 4).
4. Akuttberedskap: 40,0 mill. kroner (91 % lege), mot 24,3 mill. kroner i 2019 (PDF-side 4).
5. Radiologi er firedoblet, fra 6,5 til 25,6 mill. kroner fra 2019 til 2025 (PDF-side 5).
6. Forventet innleie i 2026: 103–116 mill. kroner. Tiltaksplanen la til grunn ca. 88 mill. kroner (PDF-side 2–3).

---

## C. Helseforetakenes utviklingsplaner

Lokale planer revideres ikke nå, fordi RU42 erstatter dem (A5). Nyeste versjoner er derfor fra 2022.

### C1. Finnmarkssykehuset HF: Strategisk utviklingsplan 2023–2038

- **Dato:** revidert 2022 (sak 78-2022). Filen er datert 24.11.2022 i dokumentregisteret.
- **URL:** https://www.finnmarkssykehuset.no/4ad47e/siteassets/dokumenter-til-sider-i-sidetre/strategisk-utviklingsplan-2023-2038-fin.pdf
- **Lokal fil:** `kilder/hf-planer/fin-strategisk-utviklingsplan-2023-2038.pdf` (50 sider). FIN sak 09-2024 Utvikling av spesialisthelsetjenestetilbudet i Klinikk Alta ligger i samme mappe.

Nøkkeltall og funn:
1. FIN har 1 700 ansatte og et budsjett på 1,8 mrd. kroner. Virksomheten omfatter 82 000 polikliniske konsultasjoner, over 4 300 operasjoner, nesten 50 000 liggedøgn og 17 500 pasienter i akuttmottaket (PDF-side 7).
2. Liggedøgn somatikk ventes å øke med 14,2 % mot 2040, eller ca. 25 % uten 10 % overføring til kommunene. Liggedøgn i psykisk helsevern og rus ventes å falle med 13,7 % (PDF-side 14).
3. Kliniske enheter: Hammerfest sykehus, Kirkenes sykehus, Klinikk Alta, Sámi klinihkka og prehospitale tjenester (PDF-side 7).

### C2. Nordlandssykehuset HF: Strategisk utviklingsplan 2023–2038 (styresak 095-2022)

- **Dato:** møte 26.10.2022
- **URL:** https://www.nordlandssykehuset.no/4aa19f/siteassets/documents/styret-i-nordlandssykehuset/styremoter-2022/26.-oktober/styresak-095-2022-nordlandssykehusets-strategisk-utviklingsplan-2023-38-m_vedlegg.pdf
- **Lokal fil:** `kilder/hf-planer/nlsh-styresak-095-2022-strategisk-utviklingsplan-2023-38.pdf`

Nøkkeltall og funn:
1. NLSH hadde 3 280 budsjetterte årsverk og 5 085 ansatte (personer) i 2021 (PDF-side 20).
2. Liggedøgn ventes å øke med ca. 13 % til 2040 etter den gamle modellen (PDF-side 35).

**Nyere:** NLSH styresak 092-2026 (28.10.2026) bruker den reviderte modellen. Demografien alene gir 22,9 % flere liggedøgn, netto vekst er 5,6 %. Befolkningen endres med -0,5 %, gruppen 65+ med +23,8 % og gruppen 18–64 år med -7,0 % (PDF-side 3). Fil: `kilder/nlsh-styresak-092-2026-…pdf`. URL: https://www.nordlandssykehuset.no/4aa3ce/siteassets/documents/styret-i-nordlandssykehuset/styremoter-2026/28.-oktober/styresak-092-2026-reviderte-nasjonale-framskrivningsmodeller-for-somatikk-psykisk-helsevern-og-tsb--betydning-for-nordlandssykehuset-hf-m_vedlegg.pdf

### C3. Helgelandssykehuset HF: Strategisk utviklingsplan 2023–2038 (styresak 90-2022) og strukturvedtaket

- **Dato:** møte 26.10.2022
- **URL:** https://www.helgelandssykehuset.no/4a9eaa/siteassets/motedokumenter/styret/styresaker-2022/20221026/20221026-styresak-90-vedlegg-1-strategisk-utviklingsplan-2023---2038.pdf (planen) og https://www.helgelandssykehuset.no/4aa0eb/siteassets/motedokumenter/styret/styresaker-2022/20221026/20221026-styresak-90-strategisk-utviklingsplan-2023---2038.pdf (saken)
- **Lokal fil:** `kilder/hf-planer/hsyk-styresak-90-2022-…`

Nøkkeltall og funn:
1. Planen er overordnet og bygger på Faglig strategisk utviklingsplan 2021–2035 (saken, PDF-side 1). Den har ingen egne framskrivingstall.
2. Den viser fire lokalisasjoner: Mo i Rana, Sandnessjøen, Mosjøen og DMS Brønnøysund (planen, PDF-side 4).

**Ny sykehusstruktur på Helgeland:** Helse Nord RHF styresak 22-2025 (14.3.2025). URL: https://www.helse-nord.no/493550/siteassets/dokumenter-og-blokker/4-om-oss/styret/styremoter/styremoter-2025/20250314/styresak-22-2025-funksjons--og-oppgavedeling-i-helgelandssykehuset-hf---oppfolging-av-strukturvedtaket-av-3-juli-2024-og-foretaksmote-i-helgelandssykehuset-30.-august-2024.pdf. Fil: `kilder/struktur/hn-styresak-22-2025-funksjons-og-oppgavedeling-hsyk.pdf`.
3. Vedtaket er ett sykehus med fire lokalisasjoner. Mo i Rana og Sandnessjøen er akuttsykehus med indremedisin, generell kirurgi og fødsler (PDF-side 1).
4. Vefsn hører til Mo i Rana for indremedisin. Grane og Hattfjelldal hører til Sandnessjøen (PDF-side 1).
5. Fødsler i 2023: Mo i Rana 265, Sandnessjøen 302 og Brønnøysund 25 (PDF-side 6).
6. Akutt- og døgnfunksjonene i Mosjøen ble avviklet 1.10.2025 (styresak 136-2026-13, PDF-side 2).
7. Etter omleggingen falt innleggelsesraten for Vefsn, Grane og Hattfjelldal fra 157 til 133 per 1 000 innbyggere. Ingen negative konsekvenser for pasientsikkerheten er identifisert (styresak 112-2026, PDF-side 2).

### C4. Universitetssykehuset Nord-Norge HF: Utviklingsplan 2038 (sak 82/2022)

- **Status: ikke lastet ned.** Adressen fra søk (unn.no/Documents/Styremøter dokumenter/2022/241022/Sak 82 …) gir 404, og filen finnes ikke i dokumentregisteret.
- **Lastet ned i stedet:** UNN sak 75-2025 Forlengelse av UNNs strategi til ut 2027. Saken bekrefter at Utviklingsplan 2038 ble styrebehandlet i oktober 2022 (sak 82/2022) og fortsatt ligger til grunn. URL: https://www.unn.no/4acf7d/siteassets/documents/styremoter-dokumenter/2025/styredokumenter_25112025/sak-75---forlengelse-av-unns-strategi-til-ut-2027.pdf. Fil: `kilder/hf-planer/unn-sak-75-2025-forlengelse-strategi.pdf`.
- **Erstatning for tallene:** UNN-tallene i 108-2026 (befolkning +2,4 %, liggedøgn +5,8 %, poliklinikk +13,6 %).

---

## D. Nasjonale dokumenter

### D1. NOU 2023: 4 Tid for handling (Helsepersonellkommisjonen)

- **Utgiver:** Helse- og omsorgsdepartementet
- **Dato:** 2023
- **URL:** https://www.regjeringen.no/contentassets/337fef958f2148bebd326f0749a1213d/no/pdfs/nou202320230004000dddpdfs.pdf
- **Lokal fil:** `kilder/nasjonalt/nou-2023-4-tid-for-handling.pdf` (337 sider)

Nøkkeltall og funn:
1. 35 % av all innleie i spesialisthelsetjenesten fant sted i Helse Nord i 2021. Helse Nord hadde 12 % av årsverkene og 9 % av befolkningen (PDF-side 88, trykt s. 86).
2. Helse Nords andel av innleien var 69 % for anestesiologi, 49 % for sykepleiere utenom spesialsykepleiere og 43 % for psykologspesialister (samme side).
3. Innleie av sykepleiere i Helse Nord økte fra 1,0 % til 2,8 % av arbeidede timer fra 2019 til 2021. For leger falt andelen fra 3,7 % til 3,0 % (samme side).
4. FIN har over tid hatt den høyeste relative andelen innleie av leger i regionen (samme side).
5. Rundt 15 % av de sysselsatte jobber i helse og omsorg. Kommisjonen mener tjenesten ikke bør ta en vesentlig større andel (PDF-side 54 og 119, trykt s. 52 og 117).

### D2. Meld. St. 9 (2023–2024) Nasjonal helse- og samhandlingsplan 2024–2027

- **Utgiver:** Helse- og omsorgsdepartementet
- **Dato:** 1.3.2024
- **URL:** https://www.regjeringen.no/contentassets/4e5d9e6c63d24cd7bdab5d8c58d8adc4/no/opri/stm202320240009000dddopri.pdf
- **Lokal fil:** `kilder/nasjonalt/meld-st-9-2023-2024-nasjonal-helse-og-samhandlingsplan.pdf`

Nøkkeltall og funn:
1. Åtte av 11 somatiske sykehus i Helse Nord har i snitt færre enn tre kirurgiske akuttinnleggelser per døgn (PDF-side 48, trykt s. 46).
2. Dagens fødetilbud skal opprettholdes i planperioden, gitt forsvarlig drift (PDF-side 48).
3. Akuttilbudet i Narvik og Lofoten skal ikke svekkes (PDF-side 48).
4. Helse Nord fikk 200 mill. kroner i 2024 for å beholde og rekruttere personell (PDF-side 84, trykt s. 82).
5. Regjeringen er ikke enig i at det trengs en nasjonal utredning av sykehusstrukturen (PDF-side 48).

### D3. Meld. St. 11 (2025–2026) Helsepersonellplan 2040

- **Utgiver:** Helse- og omsorgsdepartementet
- **Dato:** 12.6.2026
- **URL:** https://www.regjeringen.no/contentassets/6d2ec1946c744942a24cb528ca666ae0/no/pdfs/stm202520260011000dddpdfs.pdf
- **Lokal fil:** `kilder/nasjonalt/meld-st-11-2025-2026-helsepersonellplan.pdf`

Nøkkeltall og funn:
1. Underskuddet av helsepersonell (14 grupper, SSBs Helsemod) øker fra ca. 9 900 årsverk i 2025 til ca. 42 400 i 2040 (PDF-side 18, trykt s. 16).
2. Sykepleiere og helsefagarbeidere utgjør ca. 40 600 av de 42 400 årsverkene (samme side).
3. Anslaget i Helsepersonellkommisjonens rapport var 70 000 årsverk (samme side).
4. Gjennomsnittlig stillingsprosent var 92,7 % i Helse Nord og om lag 92 % i Helse Sør-Øst (2024) (PDF-side 44, trykt s. 42).
5. Behovet for innleie har vært størst i distriktene, «og særlig i Nord-Norge». Innleie utgjør ca. 0,8 % av lønnskostnadene i Helse Sør-Øst og «noe høyere» i Helse Nord (PDF-side 54–55, trykt s. 52–53).

**Vurdering.** Dette dokumentet var ikke på oppgavelisten, men det er det nyeste nasjonale helsepersonellplandokumentet og bør brukes framfor NOU-en for framskrivingstall.

### D4. Riksrevisjonen Dokument 3:10 (2025–2026) Riksrevisjonens undersøkelse av helsetjenestenes samhandling om eldre (hovedfunn)

- **Utgiver:** Riksrevisjonen
- **Dato:** 5.5.2026 (nynorsk)
- **URL:** https://www.stortinget.no/globalassets/pdf/dokumentserien/2025-2026/dok3-202526-010.pdf
- **Lokal fil:** `kilder/nasjonalt/riksrevisjonen-dok3-10-2025-2026-samhandling-eldre.pdf`

Nøkkeltall og funn:
1. Overordnet vurdering: kritikkverdig. Mange pasienter som kunne vært behandlet i kommunene, legges inn på sykehus, og utskrivningsklare pasienter blir ikke alltid tatt imot (PDF-side 3).
2. Antall eldre over 80 år øker med 50 % fra 2024 til 2033 (PDF-side 3).
3. Ved uendret bruk blir det 26 % flere polikliniske konsultasjoner og 29 % flere akutte kontakter i 2050 enn i 2024 (PDF-side 21).
4. Alle helseforetakene i Helse Nord har relativt få planlagte polikliniske konsultasjoner per 1 000 innbyggere over 80 år (PDF-side 64).
5. Helse Midt-Norge og Helse Nord har størst utfordringer med overliggerdøgn blant utskrivningsklare pasienter (PDF-side 90–91).

Dokument 3:16 (2025–2026) om kommunale tjenester til eldre er omtalt i `analyse/eldreomsorg/riksrevisjonen-eldre-essens.md`.

### D5. SSB Rapporter 2026/18 Behov for og tilgang på arbeidskraft i offentlig helse og omsorg fremover (Helsemod)

- **Utgiver:** Statistisk sentralbyrå
- **Dato:** 27.5.2026 (publisert 1.6.2026)
- **URL:** https://www.ssb.no/helse/helsetjenester/artikler/behov-for-og-tilgang-pa-arbeidskraft-i-offentlig-helse-og-omsorg-fremover/_/attachment/inline/e35491e6-e7b1-43f0-82f9-726b8b21574e:2475fafc0fdb77314f7751654ffea53725e30f2e/RAPP2026-18.pdf
- **Lokal fil:** `kilder/nasjonalt/ssb-rapp2026-18-arbeidskraft-helse-omsorg.pdf`

Nøkkeltall og funn:
1. Etterspørselen etter helsepersonell øker mer enn tilbudet. Mangelen er størst for helsefagarbeidere og sykepleiere (sammendrag, PDF-side 4).
2. Økt utdanningskapasitet gir størst effekt. Tiltak for eldre arbeidstakere har moderat betydning (PDF-side 4).
3. Rapporten bygger på befolkningsframskrivingen fra 2024 og basisåret 2024 (PDF-side 4).

**Ikke funnet:** regionale tall. Rapporten nevner verken Helse Nord, Nord-Norge eller fylker.

### D6. Helsedirektoratets eller Sykehusbyggs framskrivingsmodell

**Ikke funnet som egen rapport.** Den gjeldende nasjonale modellen for spesialisthelsetjenesten er RHF-modellen i 108-2026 (A3). Sykehusbygg HF og Helsedirektoratet deltok i arbeidet som observatør og analysestøtte (108-2026, PDF-side 3). Den har tall for Helse Nord og hvert helseforetak.

---

## E. Struktur og fødetilbud: kortere kilder

- **Spørsmål besvart i Stortinget** (Helse Nords styresaker 2026, `kilder/stortingssvar/`). Svarene gjelder fødetilbudet i Finnmark (94-2026-4), Brønnøysund (43-2026-06, 75-2026-7, 119-2026-5, 136-2026-14/15/16), Mosjøen og Helgeland (43-2026-04, 136-2026-13), Narvik (26-2026-3) og sengekapasiteten ved UNN (119-2026-6). Nøkkeltallene står i `noekkeltall.json` og `sykehus.md`.
- **Helseforetakenes avdelingssider** for fødeavdelinger, fødestuer og DMS (20 sider, `kilder/struktur/*.txt`). Se `sykehus.md`.
- **Helse Nord, «Nøkkeltall»** (oppdatert 19.8.2026): 20 200 ansatte, 16 000 årsverk, 27,4 mrd. kroner i omsetning og 711 mill. kroner til pasientreiser (2025). Helse Nord dekker 8,8 % av innbyggerne (2024) og 45 % av landarealet. Fil: `kilder/web/hn-nokkeltall.txt`. URL: https://www.helse-nord.no/om-oss/nokkeltall/
- **Styresak 41-2026 Beredskap i Helse Nord – orientering** (25.3.2026): saksdokumentene er unntatt offentlighet (offl. § 21), og saken er behandlet i lukket møte. Ingen tall.
- **Styresak 73-2026 Rekrutterings- og samhandlingstilskuddet** (27.5.2026): søknader på ca. 900 mill. kroner (52 prosjekter) og 123 mill. kroner tildelt 32 prosjekter (PDF-side 2–3).

## F. Ikke funnet eller ikke lastet ned

| Etterspurt | Status |
|---|---|
| RU42 som PDF, høringsbrev og framskrivingsnotat som egne vedlegg | Ingen PDF. Planen er heldigital. Høringsbrevet er vedlegg 4 i 127-2026. Framskrivingene står i 108-2026. |
| Tabellene på RU42s side «Framskrivning og demografi» | Ikke publisert i HTML per 29.10.2026 |
| Styresaker 2026 med framskriving av døgnplasser og personell | Ikke funnet. 108-2026 framskriver aktivitet, ikke senger eller personell. |
| Helse Nords regionale helsepersonellplan eller «Helsepersonellplan 2035» | Ikke funnet. Strategien fra 2023 og handlingsplanen 2024–2026 er de nærmeste. |
| UNN Utviklingsplan 2038 (sak 82/2022) | Gir 404, ikke lastet ned |
| Turnover i Helse Nord | Ikke tallfestet i noen gjennomgått kilde |
| Årsverk per helseforetak 2025 i tekstform | Ikke funnet. Bare figurer (126-2026). |
| Regionale Helsemod-tall | Ikke funnet |
| Slagalarm i Alta og på Finnsnes | Ikke belagt. FINs prosedyre gir 404. |
| Akuttkirurgi ved Harstad, Narvik, Hammerfest og Kirkenes | Ikke uttrykkelig belagt i nedlastede kilder |
| Tall for samisk befolkning | Ikke funnet i de gjennomgåtte dokumentene. Bare kvalitative føringer (Sametingets innspill, Sámi klinihkka). |
