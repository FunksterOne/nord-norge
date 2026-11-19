# Forslag: figurer i tema 02, 03 og 06 (anbefaling 08)

Utarbeidet 19. november 2026. Grunnlag: `analyse/LAYOUT-VURDERING.md`, funn 06 og anbefaling 08.

## Konklusjon

Anbefaling: 11 figurer, 7 nye og 4 ombygde. Ni av dem kan lages med data som allerede ligger i `assets/data.js` eller
uten data i det hele tatt. To krever nye uttrekk fra SSB (07459 og 05539). Begge tabellene er kontrollert og har
inndelingen som trengs.

Akter av typen «Hva sier kildene?» (sitater) får ingen figur. Det er samme form som på de andre temasidene, og en figur
ville bare gjenta tall fra tidligere akter. Akten om svarte svaner i tema 06 får heller ingen, fordi det ikke finnes data
å vise. Med disse unntakene får hver akt minst én nummerert figur.

Rekkefølge: pakke A først (data finnes), deretter B (nye uttrekk) og C (diagrammer uten data).

## Tema 02 — Store mot små

| Akt | I dag | Forslag | Data | Pakke |
|---|---|---|---|---|
| 01 Sjokket | 4 KPI-er | **Ny:** De 80 kommunene sortert etter folketall, med de seks største uthevet. Søylene viser hvor bratt fordelingen er: seks høye, 74 lave. | `DATA.kommuner` | A |
| 02 Bildet | «Vekten» (eget HTML-oppsett) | **Ny i tillegg:** De seks største kommunenes andel av folketallet 2000–2050: 40,8 % i 2000, 46,6 % i 2026, 47,2 % i 2050 (hovedalternativet). Viser at konsentrasjonen har økt, men flater ut i framskrivingen. Vekten beholdes over figuren. | `DATA.kommuner[].hist`, `DATA.proj.kommuner[].main` | A |
| 03 Brutt opp | Tabell (4 indikatorer) | **Ny:** Aldersprofilen til de to gruppene: andel av befolkningen per ettårig alder, de seks mot de 74. Viser hvor forskjellen i medianalder kommer fra (20–40 år mot 55+). Tabellen beholdes. | `DATA.kommuner[].alder` | A |
| 04 Konsekvens | Figur (to baner) | Uendret. | — | — |
| 05 Stemmene | Sitater | Ingen figur. | — | — |
| 06 Reformen | 3 KPI-er | **Ny:** Kommunene etter størrelsesklasse (under 5 000, 5–10 000, 10–15 000, over 15 000), andel av kommunene i Nord-Norge mot landet. 59 av 80 kommuner i nord ligger under 5 000 innbyggere, mot 174 av 357 i landet. | `HELSE_DATA.hru.kommuner` | A |

## Tema 03 — Kvinneflukten

| Akt | I dag | Forslag | Data | Pakke |
|---|---|---|---|---|
| 01 Sjokket | 4 KPI-er | **Ny:** Menn per 100 kvinner i alderen 18–44 år, 1986–2026, Nord-Norge og landet. Viser om skjevheten øker eller avtar, noe siden ikke sier i dag. | **Nytt uttrekk:** SSB 07459 (kjønn, ettårig alder, 1986–2026, fylker og landet) | B |
| 02 Bildet | Figur (spredning) | Uendret. | — | — |
| 03 Brutt opp | To stolpekort (eget HTML-oppsett) | **Ombygd:** De to stolpekortene blir nummererte figurer med enhet og kilde. **Ny i tillegg:** Netto flytting etter kjønn og aldersgruppe, sum 2011–2025, fylkene i nord. Det er figuren som faktisk svarer på aktens spørsmål «Når flytter de?». I dag viser akten bare hvor mange som bor der. | Ombygging: `KJONN_DATA`. Ny: **SSB 05539** (fylke, kjønn, 9 aldersgrupper, inn-, ut- og nettoflytting, 2011–2025) | A + B |
| 04 Konsekvens | Stort tall og punktliste | **Ny:** Framskrevne kvinner i alderen 20–39 år i Nord-Norge 2026–2050, hovedalternativet. Gjør aktens påstand om «færre framtidige fødselskull» målbar. | **Nytt uttrekk:** SSB 14746 (kjønn og alder; tabellen brukes allerede uten kjønn) | B |
| 05 Stemmene | Sitater | Ingen figur. | — | — |

Forbehold om 05539: tabellen samler innenlandske flyttinger og flyttinger til og fra utlandet. Før figuren bygges, må
det avklares om nettotallet kan deles i innenlandsk og utenlandsk flytting. Hvis ikke, må figuren merkes «all flytting».
Det endrer tolkningen, fordi innvandringen er mannsdominert.

## Tema 06 — Fire fremtider

| Akt | I dag | Forslag | Data | Pakke |
|---|---|---|---|---|
| 01 Sjokket | 4 KPI-er | **Ny:** Folketallet 2000–2050 med lav, middels og høy bane: 427 522, 488 365 og 550 318 innbyggere i 2050. Viser spennvidden før scenariene, og knytter siden til tallgrunnlaget. | `DATA.kommuner[].hist`, `DATA.proj.landsdel` | A |
| 02 Bildet | Tre tekstkort | **Ny:** Beslutningstre: tre ja/nei-valg som fører til de fire scenariene. Gjør koblingen i sluttavsnittet synlig. | Ingen (diagram) | C |
| 03 Brutt opp | Fire scenariokort | **Ombygd:** En kompakt matrise over kortene (scenario × tre valg, ja/nei). Kortene beholdes. | Ingen | C |
| 04 Milepælene | Tidslinje (eget HTML-oppsett) | **Ombygd:** Tidslinjen blir en nummerert figur: tidsakse 2026–2040 med ett felt per kategori (kraft, sjømat, mineraler, forsvar, infrastruktur, arbeidskraft). Punktene blir klikkbare og viser dagens tekst. | Teksten i akten | C |
| 05 Svarte svaner | Gruppert liste | Ingen figur. Det finnes ingen sannsynligheter eller anslag å vise, og en figur ville gi et inntrykk av presisjon som ikke finnes. | — | — |
| 06 Stemmene | Sitater | Ingen figur. | — | — |

## Status

Pakke A er gjennomført 19. november 2026: fire nye figurer i tema 02, de to stolpekortene i tema 03 er nummererte
figurer, og tema 06 har fått folketallet med tre framskrivinger i akt 01. Vekten i tema 02 er beholdt. Pakke B og C
gjenstår.

## Omfang

- **Pakke A** (5 nye figurer og 1 ombygging, data finnes): én arbeidsøkt. Alle bruker figurtypene dashbordet har
  (`stolper`, `linjer`, `hstolper`).
- **Pakke B** (3 figurer): nytt skript `fetch_kjonn_tid.py` eller utvidelse av `fetch_kjonn.py`, med en ny datablokk
  eller nye felt i `KJONN_DATA`. Én arbeidsøkt, pluss avklaringen om 05539.
- **Pakke C** (1 ny og 2 ombygginger): egne SVG-diagrammer. Én arbeidsøkt.

Etter hver pakke: `tools/sjekk_layout.py` (figurnummerering) og `tools/sjekk_funn.py` (hovedfunnene).

## Valg som trengs

1. Skal alle tre pakkene gjennomføres, eller bare A?
2. Tema 02, akt 02: skal vekten beholdes ved siden av den nye linjefiguren, eller erstattes av den?
3. Tema 06, akt 04: er klikkbar tidslinje ønsket, eller holder det med en statisk figur med teksten under?
