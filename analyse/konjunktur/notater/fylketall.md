# Fylket i tall — kontroll mot Konjunkturbarometer for Nord-Norge 2026

Kjørt 19. november 2026 med `python fetch_fylketall.py`. Barometerets fylkesfakta står på s. 15, 17 og 19.

## Resultat

36 av 42 kontrollerte verdier er like barometerets, med samme avrunding. Det gjelder:

- sysselsatte 15–74 år;
- månedslønn;
- utdanningsnivå (unntatt Finnmark);
- studenter;
- boliger;
- fullførte boliger;
- bebygd areal og jordbruksareal;
- vernet areal (unntatt Finnmark);
- netto driftsresultat;
- antall kommuner over 1,75 %.

## Avvik og forklaring

| Indikator | Fylke | Dashbordet (SSB) | Barometeret | Forklaring |
|---|---|---|---|---|
| Ledige stillinger | alle tre | 3 700 / 2 700 / 1 300 | 1 491 / 1 032 / 458 | Ulike mål. Dashbordet bruker SSB 14306, en utvalgsundersøkelse av alle ledige stillinger, 3. kvartal 2026, avrundet til hundre. Barometeret oppgir NAV-tall for juli 2026, trolig utlyste stillinger. Tallene skal ikke sammenlignes. |
| Samlet areal | alle tre | 38 145 / 26 176 / 48 633 km² | 38 153 / 26 189 / 48 637 km² | Under 0,1 %. Dashbordet summerer arealklassene i SSB 09594 utenom sjø. Barometeret har trolig brukt SSBs samlede flatemål. Ikke vesentlig. |
| Bebygd areal | Troms | 0,8 % | 0,9 % | Avrunding nær 0,85 %. |
| Universitets- og høgskoleutdanning | Finnmark | 31,6 % | 32,0 % | Ikke forklart. Nordland og Troms er like. SSB 09429 gir 23,2 % kort og 8,4 % lang for 2025. |
| Vernet areal | Finnmark | 11,2 % | 9,4 % | Ikke forklart. SSB 08936 gir 5 455 km² vernet på land i 2024 og 2025, delt på 48 633 km². Nordland og Troms er like, så metoden er trolig den samme. Barometerets tall kan bygge på et eldre år eller et annet arealgrunnlag. Dashbordet bruker SSB-tallet. |
| Kommunale investeringer | Nordland og Finnmark | 4,2 og 1,7 mrd. kr | 4,3 og 1,4 mrd. kr | Dashbordet bruker konsolidert kommuneregnskap (SSB 13544, AGI1), som trolig avviker fra barometerets grunnlag. Vises også som andel av driftsinntektene i datafilen. |

## Feil i barometerets tekst

- **Troms, s. 17:** «5 av 11 tromskommuner hadde positivt netto driftsresultat». Tallet 5 stemmer (SSB 12134), men Troms
  har 21 kommuner.
- **Nordland, s. 15:** barometeret oppgir at 22 av 41 kommuner hadde positivt netto driftsresultat. SSB 12134 gir 20.
  Forskjellen kan skyldes at kommuner med 0,0 % er telt med, eller at tallene er revidert. Ikke kontrollert videre.
- **Nordland, s. 15:** setningen om femteplass i sjømateksport lister «Nordland» blant fylkene foran Nordland.

## Merknader om metode

- **Netto driftsresultat:** gjelder kommunekonsern (SSB 12134), slik TBU-normen måles. Da treffer tallene barometeret
  nøyaktig. Konsolidert kommuneregnskap (13544) ga 0,6 % for Nordland mot 1,0 %.
- **Vernet areal for landet:** SSB 08936 tar med Svalbard i landstallet. Svalbard trekkes fra, slik at landstallet
  (17,9 %) gjelder samme areal som SSB 09594.
- **Evenes og Gamvik:** mangler konsolidert regnskap for 2025 i SSB 13544 (november 2026). Investeringsutgiftene for
  Nordland og Finnmark mangler derfor disse to kommunene. Netto driftsresultat og antall over 1,75 % fra SSB 12134 omfatter
  alle 80 kommuner.
