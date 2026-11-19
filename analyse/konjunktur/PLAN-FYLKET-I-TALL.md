# Fylket i tall — plan

Laget 19. november 2026. Venter på klarsignal. Bakgrunn: fylkesfaktasidene i Konjunkturbarometer for Nord-Norge 2026
(s. 14–19). Se også PLAN.md.

## Konklusjon

Fylkessidene får et nytt kort, «Fylket i tall», med 15 nøkkeltall. Hvert tall hentes fra primærkilden med eget år og egen
kilde, og vises for fylket, Nord-Norge og landet. Barometerets tall brukes bare som kontroll. Avvik over avrundingsnivå
skal være forklart før publisering. Landsdelssiden (`nord-norge.html`) får det samme kortet med Nord-Norge og landet.

## Plassering

Kortet legges rett under ingressen på `fylke.html` og `nord-norge.html`, før seksjonsmenyen. Det viser tre kolonner:
fylket, Nord-Norge og landet. Radene er gruppert i fem blokker. Hver rad oppgir år, og kilden vises med SSB-tabellnummer.

- På stor skjerm er kortet åpent.
- På mobil er kortet lukket (`details`), slik at ingressen og menyen ikke skyves ned.
- Tall dashbordet allerede viser lenger ned, får en lenke til seksjonen i stedet for å gjentas. Det gjelder ROBEK,
  NAV-mangel og forsørgerbrøk.

## Indikatorene

| Blokk | Indikator | Kilde | År | Barometerets tall for Nordland (kontroll) |
|---|---|---|---|---|
| Arbeid | Sysselsettingsgrad 15–74 år, bosted | SSB 13563 | 2025 | 67,7 % |
| Arbeid | Ledige stillinger, arbeidssted | SSB 14306 | 2026K3 | 1 491 (juli 2026, NAV) |
| Arbeid | Gjennomsnittlig månedslønn, arbeidssted | SSB 11422 | 2025 | kr 57 580 |
| Utdanning | Andel 16 år og over med universitets- og høgskoleutdanning | SSB 09429 | 2025 | 30,9 % |
| Utdanning | Andel med videregående som høyeste utdanning | SSB 09429 | 2025 | 38,8 % |
| Utdanning | Studenter etter studiested | SSB 03814 | 2025 | 8 812 |
| Bolig | Boliger i alt | SSB 06265 | 2026 | 132 814 |
| Bolig | Fullførte boliger | SSB 05940 | 2025 | 595 |
| Bolig | Kvadratmeterpris, brukte boliger (veid med omsetninger) | SSB 14310 | 2026K3 | (gjennomsnittspris kr 3 455 997) |
| Areal | Samlet areal (land og ferskvann) | SSB 09594 | 2026 | 38 153 km² |
| Areal | Bebygd areal og jordbruksareal, andel | SSB 09594 | 2026 | 1,0 % og 1,9 % |
| Areal | Vernet areal, andel | SSB 08936 | 2025 | 19,8 % |
| Kommuneøkonomi | Netto driftsresultat, kommunene samlet | SSB 12134 / dashbordets KOSTRA-data | 2025 | 1,0 % |
| Kommuneøkonomi | Kommuner over TBUs norm på 1,75 % | dashbordets KOSTRA-data | 2025 | 12 av 41 |
| Kommuneøkonomi | Brutto investeringsutgifter, kommunene samlet | SSB 12134 | 2025 | 4,3 milliarder kroner |

Tre tall mangler i dag på dashbordets fylkessider: månedslønn, utdanningsnivå og vernet areal. Resten finnes delvis i
andre tabeller (06265 og 14310 i levekår og boligmarked), men ikke samlet per fylke.

## Status 19. november 2026

Registrerte arbeidsledige (SSB 13563), husholdninger med høy gjeld (SSB 08781, i stedet for forbruksgjeld) og fylkesvei
med dårlig dekke (SSB 11842) er lagt inn; se `notater/fylketall.md`. Punktet om fylkesvei under var feil: 11842 har
dekketilstand. Eksport og forbruksgjeld er fortsatt utelatt. Kortet har 19 rader (merket sa 15, men det var 16).

## Det som ikke tas med i denne runden, og hvorfor

- **Helt ledige.** Ligger hos NAV, ikke i SSB-API-et. Kan legges til senere fra NAVs månedsstatistikk.
- **Forbruksgjeld per innbygger.** Gjeldsregisteret har ikke et åpent API med fylkestall. Utsatt.
- **Eksportverdi og sjømatandel.** SSBs utenrikshandel har ikke fylkesfordeling i statistikkbanken. Barometerets tall
  kommer trolig fra Sjømatrådet og egne beregninger. Kan tas med som merkede tall i en senere runde.
- **Anslått verdiskaping per innbygger.** KPBs eget anslag, uten åpen metode.
- **Fylkesvei, dårlig dekke.** Statens vegvesen eller fylkeskommunen. SSB 11842 har vei-km, men ikke dekketilstand.
  Utsatt.
- **Gjennomsnittlig boligpris i kroner.** Eiendom Norges tall. Dashbordet bruker SSBs kvadratmeterpris i stedet.
- **Fagskolestudenter, studiesteder og flyplasser.** Lav verdi for sidene.

## Kjente feil i barometerets fylkesfakta (skal stå i metodekortet)

- Troms: «5 av 11 tromskommuner». Troms har 21 kommuner. Riktig tall beregnes fra KOSTRA-dataene.
- Nordland: «Landets 5. største fylke for sjømateksport, etter Møre og Romsdal, Vestland, Nordland og Trøndelag»
  nevner Nordland foran seg selv. Setningen er trolig kopiert fra Troms.

## Gjennomføring

1. Skriv `fetch_fylketall.py`, som lager `FYLKE_TALL`. Det henter de 15 tallene for F-18, F-55, F-56 og landet med
   SSBs PxWebApi v2 (sammenslåtte fylkesserier der tabellen har dem). Nord-Norge summeres, eller vektes for andeler,
   priser og satser.
2. Lag en kontrollutskrift mot barometerets verdier. Avvik over 1 % eller ett prosentpoeng forklares i
   `analyse/konjunktur/notater/fylketall.md` før publisering.
3. Lag en felles funksjon for kortet (i `src/lib/` eller i den delte sidekoden). Den monteres på `fylke.html` (fylket,
   Nord-Norge og landet) og `nord-norge.html` (Nord-Norge og landet).
4. Legg inn metodekort og lenker fra radene til seksjonene der temaet behandles videre (levekår, boligmarked, økonomi).
5. Sjekk på stor skjerm og mobil, i mørk og lys visning. Bygg, commit, push og sjekk nettstedet.

Anslått omfang: én arbeidsøkt. Den største usikkerheten er om alle tabellene har sammenslåtte fylkesserier for 2024–2026.
Hvis ikke, summeres kommunene med dashbordets kommuneliste.
