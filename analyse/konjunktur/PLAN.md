# Konjunkturbarometer for Nord-Norge 2026 — vurdering og plan

Vurdert 19. november 2026. Grunnlag: Konjunkturbarometer for Nord-Norge 2026 (Kunnskapsbanken, SpareBank 1 Nord-Norge,
skrevet av KPB, 88 sider, data per medio oktober 2026). PDF-en ligger i `kilder/` (ikke i git). Planen venter på klarsignal.

## Konklusjon

Rapporten bør ikke bli en egen temaside. Den er en årlig sekundærkilde. Mye av den gjentar tall dashbordet allerede
henter fra primærkildene (befolkning, fylkesfakta, ROBEK, leiemarkedet). Fem ting er nye og verdt å ta inn. To av dem
finnes bare her, fordi KPB har brukt Microdata og Proff Forvalt. Det gjelder utenlandsfødt helsepersonell og
konjunkturtabellen for næringene. De skal merkes tydelig som KPBs beregninger. Resten kan beregnes på nytt fra SSB og
de nordiske statistikkbyråene og skal hentes derfra.

## Hva som tas med

**01 — Utenlandsfødte leger og sykepleiere → tema 12, akt 03 (høy prioritet).**
Antall etter fødeland 2015, 2019 og 2025 (Microdata, KPB). Tallene er kontrollert for indre sammenheng: summen gir
vekst på 14,3 %, utenlandsfødte øker med 36 %, og 22,5 % av legene og 12,6 % av sykepleierne var utenlandsfødte i 2025.

Hovedfunnet rapporten ikke sier rett ut: fra 2019 til 2025 falt antallet norskfødte sykepleiere fra 8 318 til 8 166.
Hele veksten i sykepleiere disse seks årene kom fra utenlandsfødte (fra 945 til 1 172).

Tas med som en figur pluss tekst om botid, statsborgerskap og at 41 % av de utenlandsfødte legene har hele eller deler av
utdanningen fra Norge. Kobles til utvalgets funn om omsorgsårsverk og til helsepersonellplanen.

**02 — Konjunkturen i næringene → tema 08, ny akt (høy prioritet).**
Tabell for elleve næringer:

- vurderingen av utviklingen i 2026 og utsiktene for 2027, i tre farger;
- omsetningsvekst 2024–2025;
- driftsmargin 2025;
- andel med negativt driftsresultat;
- sysselsettingsvekst.

Byggnæringen er den eneste med rødt både for 2026 og 2027.

Utvalget er virksomheter med hovedenhet i Nord-Norge og driftsinntekter over 1 million kroner begge år (Proff Forvalt).
Forbeholdet vises på siden.

**03 — Bygg og anlegg og strømnettet → tema 08 og tema 07 (høy prioritet).**

- Sysselsettingen i bygg og anlegg falt med 4,8 % (1 037 personer) fra 2022 til 2025, mest i Troms (−7,5 %). Byggnæringen
  falt med 7,9 %, mens anlegg økte med 2,8 %.
- Arbeidsinnvandrere i næringen: 2 752 i 2021, 2 478 i 2025.
- Investeringstelleren: om lag 3 300 prosjekter for 850 milliarder kroner i 2025–2032.
- Statnett stanset nye reservasjoner av nettkapasitet nord for Svartisen våren 2026, og om lag 150 milliarder kroner i
  planlagte investeringer kan bli forsinket.

Sysselsettingstallene beregnes på nytt fra SSB. Statnett-stansen kontrolleres mot Statnetts egen kunngjøring før den
legges inn. Tema 07 (bolig) får en henvisning, fordi fallet i byggnæringen henger sammen med boligbyggingen siden viser.

**04 — Nord-Norge mot Nord-Sverige og Nord-Finland → tema 05 (middels prioritet).**
Befolkningsframskriving 2026–2035 for 0–19, 20–66 og 67+ år: Nordland, Troms og Finnmark mot Västerbotten, Norrbotten,
Nord-Österbotten, Kainuu og Lappland. Rapporten viser bare figuren. Tallene hentes selv fra SSB 14746, SCB (PxWebApi v2)
og Statistics Finland (PxWeb), slik at dashbordet har tallene og kan oppdatere dem.

Rapportens tolkning tas med som hypotese: regionene med universitetsby (Troms, Västerbotten, Nord-Österbotten) holder
best på gruppen i arbeidsfør alder.

**05 — Unge utenfor arbeid og utdanning → tema 10 (middels prioritet).**
Utviklingen fra 2015 hentes fra SSBs åpne statistikk, hvis tabellen finnes per fylke. Det kontrolleres i gjennomføringen.

KPBs panelfunn tas med som KPBs beregning: av de 2 800 med ukjent status i 2024 hadde bare om lag 14 % ukjent status i
alle fire årene 2021–2024. Tall og forbehold om hva statistikken måler, legges inn i akten «Hva undersøkelsen kan — og
ikke».

## Hva som ikke tas med, og hvorfor

- **Leiemarkedet (s. 65–71).** Tema 07 har allerede KPBs analyse fra juli 2026 og SSBs leieandeler per kommune. Bare
  datoen og henvisningen oppdateres.
- **Fylkesfakta, global og norsk økonomi (s. 8–19).** Dekkes av primærkildene på fylkes- og landsdelssidene.
- **ROBEK (s. 75).** Dashbordets liste (KDD, 9.10.2026) har de samme 13 kommunene.
- **Kraftaksjer og utbytte (s. 72–78).** Relevant for kommuneøkonomien, men bygger på enkeltkommuners budsjetter og egne
  vurderinger. Kan bli en egen boks senere, men ikke i denne runden.
- **Oppstartsselskaper, reiseliv, petroleum, prosessindustri og rom (s. 33–45, 59–64).** Delvis dekket i tema 08.
  Tallene er enten fra Proff Forvalt uten fast avgrensning eller enkeltår. Reiseliv (vinterturister, flypassasjerer)
  kan vurderes ved neste oppdatering av tema 08.
- **Totalberedskap og ROS i kommunene (s. 24–29).** Passer best i tema 11, men tallene (DSB) bør hentes fra DSB direkte.
  Ikke med nå.

## Feil og uklarheter i rapporten

- **ROBEK:** s. 75 skriver «én i Troms», men lister to kommuner (Kåfjord og Tromsø). Summen 13 stemmer med to. Teksten
  oppgir også både «september 2026» og «per mai 2026».
- **Unge utenfor:** s. 79 skriver at «andelen» falt med «rett i overkant av 30 prosent, fra 6.600 personer til 4.600».
  Det er antallet som har falt med 30 %, ikke andelen. Side 80 oppgir 4 500 for samme år.
- **Ikke kontrollert:** Investeringstelleren (850 milliarder kroner), Statnett-stansen (150 milliarder kroner) og
  andelene for botid og utdanning blant utenlandsfødte leger. De to første kontrolleres i gjennomføringen. De siste
  bygger på Microdata og kan ikke etterprøves med åpne data.

## Gjennomføring

1. `analyse/konjunktur/` får `fetch_konjunktur.py`, som lager `KONJ_DATA`. Konstanter fra rapporten har sidetall (punkt
   01 og 02). Sysselsetting i bygg og anlegg hentes fra SSB (punkt 03).
2. Tema 12, akt 03: figur over leger og sykepleiere etter fødeland, pluss ett avsnitt (punkt 01).
3. Tema 08: ny akt, «Konjunkturen 2026–2027», med konjunkturtabell, figur over driftsmargin og andel med negativt
   resultat, og en boks om bygg og anlegg og strømnettet (punkt 02 og 03). Henvisning fra tema 07.
4. Tema 05: nordisk sammenligning som egen figur, med data fra SSB, SCB og Statistics Finland (punkt 04).
5. Tema 10: unge utenfor, med SSB-serie hvis den finnes, og KPBs panelfunn (punkt 05).
6. Metodesiden: nytt kort, «Konjunkturbarometeret», med utvalg (Proff Forvalt, over 1 million kroner i driftsinntekter,
   skjønnsmessige justeringer), Microdata-forbeholdet og hva som er beregnet på nytt.
7. Søk, bygg, kontroll i forhåndsvisning på stor skjerm og mobil, commit, push og kontroll av nettstedet.

Anslått omfang: punkt 1–3 og 6 er en arbeidsøkt. Punkt 4 og 5 avhenger av hva SCB og Statistics Finland gir, og kan tas i
en egen runde.
