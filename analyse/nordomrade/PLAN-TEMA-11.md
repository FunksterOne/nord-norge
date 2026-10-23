# Plan for tema 11 — nordområdepolitikken 2006–2026

Status: implementert 23. oktober 2026 som `tema-nordomrade.html`. Overskriften ble «20 år med nordområdepolitikk — hva som ble sagt, og hva som skjedde» (Halvards valg); ellers fulgte vi anbefalingene i punkt 7. Omtalene av dokumentene ble lengre, med to avsnitt per dokument.
Utarbeidet 23. oktober 2026.

## 1. Konklusjon

Funnene hører hjemme på en egen temaside, tema 11. De passer ikke på kommune- og fylkessidene, og de skal heller ikke fordeles på de eksisterende temasidene. Begrunnelsen er tredelt:

1. **Dokumentene gjelder landsdelen, ikke kommunene.** Ingen av de sju dokumentene har mål eller tiltak som kan føres ned på én kommune. Kommunetall ved siden av dokumentene ville gi en kobling som ikke finnes.
2. **Verdien ligger i sammenstillingen.** Det nye er at det regjeringene sa skulle skje, legges ved siden av det som faktisk skjedde, i ett løp over 20 år. Delt opp på tema 01–10 ville tidslinjen og helhetsbildet gå tapt.
3. **Formatet finnes allerede.** Temasidene bruker akter med en påstand per akt, nøkkeltall og figurer. En gjennomgang av 20 år med politikk passer inn i det samme formatet.

Fra de eksisterende sidene lenkes det inn på fire steder (punkt 5.4). Ellers står tema 11 alene.

## 2. Grunnlaget

| År | Dokument | Regjering | Type | Sider |
|---|---|---|---|---|
| 2006 | Regjeringens nordområdestrategi (1. des.) | Stoltenberg II | strategi | 64 |
| 2009 | Nye byggesteiner i nord (12. mars) | Stoltenberg II | strategi, trinn 2 | 93 |
| 2011 | Meld. St. 7 (2011–2012) Nordområdene. Visjon og virkemidler (18. nov.) | Stoltenberg II | stortingsmelding | 134 |
| 2014 | Nordkloden (10. nov., Hammerfest) | Solberg | statusrapport | 37 oppslag |
| 2017 | Nordområdestrategi – mellom geopolitikk og samfunnsutvikling (april) | Solberg | strategi | 71 |
| 2020 | Meld. St. 9 (2020–2021) Mennesker, muligheter og norske interesser i nord (27. nov., Alta) | Solberg | stortingsmelding | 193 |
| 2025 | Norge i Nord. Nordområdepolitikken i en ny virkelighet (26. aug., Kirkenes) | Støre | strategi | 44 |

To mindre dokumenter vises som merker på tidslinjen, men registreres ikke fullt: statusrapporten fra oktober 2010 og «Plan for Norge» (15. desember 2025). Etter august 2025 er det ikke kommet noe nytt nordområdedokument. Nordområdemidlene er flyttet fra UD til KDD, og UDs post 118.70 er lagt ned fra 2026.

Forhistorien omtales i én setning, men registreres ikke. Den består av NOU 2003:32 «Mot nord!», St.meld. nr. 30 (2004–2005) og Innovasjonsløft Nord (KRD, august 2006). Innovasjonsløft Nord er tatt med fordi det viser hva som *ikke* ble tatt inn i strategien. Gruppen foreslo næringsvirkemidler for om lag 140 millioner kroner i året, og ingen av dem står i strategien fra desember 2006.

Notatene per dokument ligger i `notater/` (md og json), og kildefilene i `kilder/`. Kildefilene er gitignorert og hentes på nytt fra regjeringen.no.

## 3. Hovedfunn som siden skal bære

**Funn 01 — Temaet har gått fra samarbeid til sikkerhet.** Ordtellingen er gjort per 10 000 ord. Sikkerhet og forsvar gikk fra 17 (2006) og 30 (2020) til 139 (2025). Russland gikk fra 78 (2006) og 77 (2011) til 13 (2020) og 12 (2025). Klima, petroleum og forskning har falt jevnt.
*Grunnlag: egen telling i de sju dokumentene, ordlister i `skript/temaord.py`.*

**Funn 02 — Befolkningen har fått mer plass, men aldri et mål.** Ordene for befolkning gikk fra 8 per 10 000 ord (2006) til 24 (2025). Arbeidskraft gikk fra 7 til 20 (2020). Ingen av dokumentene fra 2006–2020 har et tallfestet mål for folketall, bosetting, flytting eller arbeidskraft. Tiltakene er av typen «vurdere», «stimulere» og «utvikle gode praksiser». 2025-strategien nevner befolkningsnedgang og aldring uten ett eneste tall (s. 6, 27). Det første tallfestede arbeidsplassmålet i rekken gjelder Forsvaret: over 1 700 nye arbeidsplasser de neste ti årene (s. 22). «Plan for Norge» (desember 2025) sier «økt bosetting i nord», uten tall.

**Funn 03 — Problemet ble beskrevet stadig bedre.** Fra 2017 bruker dokumentene SSBs tall:
- Befolkningsveksten i Nord-Norge «skyldes innvandring» (2017, s. 9).
- De 77 kommunene utenom Tromsø, Bodø og Alta har mistet nesten 44 000 innbyggere siden 1980 (2020, s. 67).
- Antall sysselsatte per pensjonist går fra 3,1 til 1,9 i 2040 (2020, s. 54).

Beskrivelsen ble ikke fulgt av virkemidler. Meld. St. 9 skal gjennomføres «innenfor gjeldende budsjettrammer» (s. 168).

**Funn 04 — Utviklingen 2006–2026 ble som problembeskrivelsen, ikke som visjonen.**
- Folketallet økte fra 462 779 (1.1.2006) til 489 778 (1.1.2026), altså 5,8 %. Andelen av landets befolkning falt fra 9,97 % til 8,70 %.
- Nord-Norge hadde innenlandsk nettoutflytting hvert eneste år i 2006–2025, til sammen −64 151.
- Netto innvandring var +80 934 og fødselsoverskuddet +10 131. Fødselsoverskuddet har vært negativt eller nær null siden 2019.
- Sysselsettingen økte 5,6 % fra 2008 til 2025 (bosted), mot 13,8 % i landet. Etter arbeidssted er veksten 7,4 %.
- Forsørgerbrøken (65+/20–64) økte fra 25,7 til 37,6, mot 24,8 til 32,8 i landet.

*Grunnlag: SSB 07459, 01222 og 07984. Fylker i 2024-inndeling. Narvik og Hamarøy er rekonstruert før 2020 fra 1805, 1854, 1849 og 1850.*

**Funn 05 — Næringene dokumentene satset på, står for lite av veksten i arbeidsplasser.** Endringen er målt fra 2008 til 2025, etter arbeidssted:
- Primærnæringene gikk ned 4,4 % og industrien 1,0 %.
- Overnatting og servering økte 26,7 %, og bergverk og utvinning 84 % (fra 1 069 til 1 966 sysselsatte).
- Helse- og sosialtjenester økte med 8 493 sysselsatte, nesten halvparten (49 %) av den samlede veksten på 17 177.
Dette er en sammenstilling, ikke en virkningsvurdering.

**Funn 06 — Anslagene var for optimistiske.** Strategien fra 2017 viste til en vekst på 4,7 % fra 2017 til 2030. Fra 2017 til 2026 har veksten vært 1,1 %. For å nå anslaget må folketallet øke med 17 600 de neste fire årene. Til sammenligning var den samlede veksten de siste ni årene 5 100.

**Funn 07 — Nye penger er få og vanskelige å skille ut.** De fleste beløpene er hentet fra Nasjonal transportplan eller ordinære budsjetter:
- 2006: nye tiltak for 2007 på til sammen 199,5 millioner kroner.
- 2011: «over en milliard kroner årlig», uten samlet regnskap.
- 2017: om lag 40 milliarder kroner til samferdsel, nesten alt fra NTP.
- 2020: ingen nye rammer.
Ingen av dokumentene har indikatorer eller lover å evaluere politikken som helhet.

## 4. Oppbygging av siden

Fil: `tema-nordomrade.html`. Kicker: «TEMA 11 · NORDOMRÅDEPOLITIKKEN 2006–2026».

Hovedoverskrift (forslag): **«Sju dokumenter på tjue år. Befolkningen fikk aldri et mål.»**
Ingressen (dynamisk) stiller hovedtallene mot hverandre: −64 151 i innenlandsk nettoflytting, +80 934 fra innvandring, og andelen av landets befolkning ned fra 9,97 til 8,70 %.

| Akt | Påstand (h2) | Innhold | Figur |
|---|---|---|---|
| 01 Rekken | «Tre regjeringer, sju dokumenter, samme hovedmål.» | Tabellen i punkt 2, med det overordnede målet sitert under 15 ord med sidetall. Befolkningskurven 2006–2026 med loddrette merker for hvert dokument. | `linjer` med ny `xMerker` |
| 02 Hva de snakker om | «Fra *samarbeid* med Russland til *sikkerhet*.» | Temaord per 10 000 ord, 17 temaer × 7 dokumenter. Forklaring av metoden i figurteksten. | ny `varmekart` |
| 03 Problemet og målet | «Problemet ble beskrevet stadig bedre — men fikk *aldri et mål*.» | Per dokument: om befolkning, aldring og arbeidskraft beskrives med tall, om det finnes tallfestet mål, og antall målbare tiltak (etter samordnet koding, se 5.2). | tabell med Harvey-baller |
| 04 Hva som skjedde | «All vekst kom fra innvandring.» | Befolkningsregnskap 2006–2025 i stablede stolper, KPI-rad (folketall, andel av landet, nettoflytting, forsørgerbrøk). | `stablet`, KPI |
| 05 Arbeidsplassene | «Satsingsnæringene vokste lite — *helse* vokste mest.» | Sysselsatte etter næring 2008–2025, Nord-Norge mot landet. | `hstolper` (to grupper) |
| 06 Anslag mot fasit | «Anslagene i dokumentene var for *optimistiske*.» | 2017-anslaget mot faktisk utvikling, og 2020-tallet for sysselsatte per pensjonist mot forsørgerkortet. Lenke til etterprøvingen på tema 06. | `linjer` |
| 07 Pengene | «Nye penger er få, og *ingen* lovet å måle effekten.» | Tabell over beløp merket «nytt», «NTP/ordinært» eller «uklart». Forbehold: bevilgningene er ikke etterprøvd i statsbudsjettene. | tabell |
| 08 Om grunnlaget | «Hva en slik gjennomgang kan — og *ikke* kan — si.» | Metode, koding, ordlister, forbehold (punkt 6). | tekstboks |

## 5. Gjennomføring

### 5.1 Data

Det skal lages et nytt skript `fetch_nordomrade.py` som bygger `NORD_DATA` (ny blokk `/* NORD_DATA BEGIN */` i `assets/data.js`). Skriptet samler fire kilder:
- `dokumenter`: metadata, sitat og side, innsatsområder (fra `notater/*.json`).
- `temaord`: resultatet av `skript/temaord.py` (flyttes fra scratchpad til `analyse/nordomrade/skript/`).
- `regnskap`: SSB 01222 per år 2006–2025 (fødselsoverskudd, innvandring, utvandring, innenlands inn og ut). Summen over de tre fylkene opphever flytting mellom dem.
- `befolkning`: SSB 07459 1.1. for 2006–2026 (totalt, 20–64, 65+, 80+), Nord-Norge og landet.
- `sysselsetting`: SSB 07984 2008–2025, totalt og etter næring. Kilden er fylkeskoder 18/19/20 → 18/54 → 18/55/56, kontrollert mot kommunesummen.
- `anslag`: anslagene dokumentene selv oppgir, med side.

Alt hentes med SSB PxWebApi v2. Totalsummene er allerede kontrollert: arbeidssted 2008 er 231 037 begge veier.

### 5.2 Samordnet koding av løftene

Agentene som leste dokumentene, har kodet «målbart» ulikt. 2014 har 69 av 92 målbare tiltak, mens 2011 har 30 av 60. Tallene kan derfor ikke sammenlignes slik de står. Før noe vises, kodes alle tiltakene på nytt etter én regel:
- **Målbart** betyr at tiltaket har tall *og* frist, eller en leveranse som kan kontrolleres (et senter opprettet, en lov vedtatt).
- **Nytt** betyr at beløpet ikke er hentet fra NTP eller ordinært budsjett.
- **Vagt** gjelder verb som «vurdere», «arbeide for» og «legge til rette».

Kodingen gjøres i én omgang med samme regelsett for alle dokumentene. Ti tilfeldige tiltak per dokument kontrolleres for hånd. Det samordnede resultatet skrives til `notater/lofter-samordnet.json`.

### 5.3 Diagrammotoren

- Ny type `varmekart` i `src/charts/varmekart.js`, med tema × år og én fargeskala (accent). Tallet står i hver celle med `tabular-nums`, og på mobil vises de sju årene som kolonner.
- Utvidelse av `linjer`: `xMerker:[{x, tekst}]` for loddrette dokumentmerker (mønster som `iDag`).
- Resten bruker typer som finnes (`stablet`, `hstolper`, KPI-rad).

### 5.4 Innlemming

- Kort 11 på forsiden, i samme mal som kort 10.
- Metodesiden får kortet `#nordomradepolitikk` (dokumentliste, ordlister, kodingsregel, SSB-tabeller) og nye kilderader.
- Lenker inn fra:
  - tema 06 (scenarier): «Anslagene i nordområdedokumentene»
  - tema 04 (arbeidskraft): «Ingen av dokumentene satte mål for arbeidskraften»
  - tema 01 (innvandring): «All vekst siden 2006 kom fra innvandring»
  - landsdelssiden: kort lenkeboks
- Ikke på kommune- og fylkessidene (se punkt 1).
- `tools/fasit.cjs` får `NORD_DATA`, så tallene i teksten kontrolleres som ellers.

### 5.5 Kontroll før publisering

1. Hvert sitat er under 15 ord og har trykt sidetall, kontrollert mot PDF-en.
2. Hvert tall i teksten er hentet fra `NORD_DATA` eller merket med kilde og side.
3. Nettleserkontroll i mørk og lys utgave og på mobil, med skjermbilder.
4. Fasitkontroll, `node --check` og byggekontroll før commit. Produksjonen kontrolleres etter push.

## 6. Forbehold siden må vise

1. **Ingen årsakspåstand.** Siden viser hva dokumentene sa og hva som skjedde, ikke at det ene førte til det andre. Utviklingen er påvirket av olje- og fiskepriser, innvandring, pandemien, krigen i Ukraina og nasjonal politikk utenfor nordområdedokumentene. Formuleringen skal være «utviklingen ble ikke som visjonen», ikke «politikken virket ikke».
2. **Samme målestokk for alle regjeringer.** Fire dokumenter er fra Stoltenberg II og Støre, tre fra Solberg. Alle måles med de samme fire kriteriene: tallfestet mål, beløp, frist og lovet evaluering. Ingen partinavn brukes i påstandene.
3. **Ordtelling er en indikator, ikke en lesning.** Den måler vekt, ikke innhold. Dokumentene er også svært ulike i lengde, fra 13 600 til 92 000 ord, og derfor oppgis alt per 10 000 ord.
4. **Bevilgningene er ikke etterprøvd.** Akt 07 viser hva dokumentene sier om penger, ikke hva som faktisk ble bevilget.
5. **2025-strategien er bare 14 måneder gammel.** Den kan beskrives, men ikke etterprøves. Siden sier det rett ut. Målet om forsvarsarbeidsplasser kan likevel følges fra nå av i SSB 07984 (offentlig administrasjon og forsvar: 21 898 sysselsatte i Nord-Norge i 2025). Det kan bli en egen «følges opp»-boks som oppdateres hver vår.

## 7. Valg som trenger klarsignal

1. **Vinkel og overskrift.** Anbefalt: «Sju dokumenter på tjue år. Befolkningen fikk aldri et mål.» Alternativet er mer nøytralt: «Tjue år med nordområdepolitikk — hva som ble sagt, og hva som skjedde.»
2. **Akt 07 om penger.** Anbefalt: ta den med som beskrivelse med forbehold. En full etterprøving mot statsbudsjettene (UDs nordområdetiltak, Arktis 2030) er et eget arbeid på flere dager.
3. **Forhistorien.** Anbefalt: én setning om NOU 2003:32 og St.meld. nr. 30 (2004–2005), og en egen boks om Innovasjonsløft Nord.
4. **Stortingsbehandlingen.** Anbefalt: én linje per melding (2011 enstemmig 17. april 2012, 2020 votert 20. april 2021, med vedtaket om Nord-Norgebanen 56–30), ikke en egen akt.

## 8. Omfang

| Del | Arbeid |
|---|---|
| Samordnet koding (5.2) | ½ dag |
| `fetch_nordomrade.py` og `NORD_DATA` | ½ dag |
| `varmekart` og `xMerker` | ½ dag |
| Siden med åtte akter og dynamiske tekster | 1 dag |
| Metodeside, forside, lenker, kontroll | ½ dag |
