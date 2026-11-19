# Layout og presentasjon — vurdering

19. november 2026. Ikke implementert.

Grunnlag:
- Alle 18 sider på nord-norge.vercel.app er målt maskinelt i headless Chromium, i 1280 og 390 piksler bredde. Målingene
  omfatter sidehøyde, akter, ord per ingress og avsnitt, figurer, tabeller, KPI-kort, CSS-komponenter, horisontal
  rulling og skriptfeil.
- Skjermbilder av forsiden, kommunesiden (Bodø), metodesiden og tema 12 er vurdert.

## Konklusjon

Dashbordet er teknisk solid. Ingen sider ruller sidelengs på mobil, ingen diagrammer mangler, og ingen sider har
skriptfeil. Svakhetene ligger i lesbarhet og helhet, ikke i funksjon. Nyere temasider er blitt tunge å lese, komponentene
har sprikt fra side til side, og de lengste sidene mangler et sammendrag øverst. Fire grep vil gi mest: et
hovedfunn-sammendrag øverst på temasidene, kortere ingresser, felles komponenter for figur, tabell og boks, og bedre
tabeller på mobil.

## Funn

**Funn 01 — De nyeste temasidene er dobbelt så tekstrike som de eldste.**
Ingressene i aktene i tema 10, 11 og 12 er på 90–160 ord. I tema 01–09 er de på 40–70 ord. Tema 12 har en hero-ingress
på 101 ord og to avsnitt på over 150 ord. Det bryter med skrivestilens prinsipp om ett poeng per avsnitt.

**Funn 02 — De lengste sidene mangler sammendrag.**
Sidehøyde i piksler:

| Side | Stor skjerm | Mobil |
|---|---|---|
| Tema 12 | 14 800 | 20 500 |
| Tema 01 | 13 300 | 17 700 |
| Tema 11 | 11 600 | 17 800 |
| Metodesiden | 14 800 | 26 100 |

Aktmenyen hjelper med navigasjonen, men ingen temaside samler hovedfunnene øverst. Leseren må gjennom 5–9 akter for å
få det samlede bildet. Skrivestilen krever konklusjonen først.

**Funn 03 — Komponentene har sprikt.**
Tabeller har minst ti egne klasser (`hs-tabell`, `konj-tabell`, `norden-tabell`, `fb-tabell`, `gap-tabell`,
`kvote-tabell`, `el-tabell`, `beh-tabell`, `kildetabell`, `fyt`). Bokser og kort har minst åtte (`hs-boks`, `ug-boks`,
`card`, `graf-kort`, `fylke-graf`, `drv`, `exhibit`, `fb-kort`). Antall ulike skriftstørrelser per side varierer fra 4 til
20; flest er det på fylkes- og landsdelssidene, som bygges av den gamle `app.js`.

Resultatet er små, men synlige forskjeller i luft, kantlinjer, etikettstil og kildelinjer fra side til side, og hver ny
side legger til egne stiler.

**Funn 04 — Figurene er nummerert på noen sider, men ikke på andre.**
Tema 08 nummererer figurene («Figur 09–11»). Tema 05, 10 og 12 gjør det ikke. Kildelinjen står noen steder med «Kilde:»
foran og andre steder uten. McHalvard-profilen forutsetter at hver figur er en nummerert «exhibit» med tittel, enhet og
kilde.

**Funn 05 — Tabellene er vanskelige å lese på mobil.**
De fleste tabeller har en minstebredde på 560–700 piksler og ruller sidelengs i en boks på mobil. I tabellen over
årsverk per helseforetak i tema 12 ser leseren bare tre av seks kolonner, og ingenting viser at det finnes flere.

**Funn 06 — Noen temasider har nesten ingen figurer.**
Tema 06 (scenarier) har ingen. Tema 02 og 03 har én hver. Tema 12 har 19, og tema 04 har 12. Sidene med få figurer
består mest av tekstkort og sitater, og bryter med resten av dashbordets visuelle form.

**Funn 07 — Overskriftene følger ikke ett mønster.**
Hovedtitlene er dels spørsmål («Hvem blir værende?», «Bygges det nok?»), dels påstander med punktum («Sju av ti unge
regner med å bli. Likevel …»), dels navn («Kvinneflukten»). Akt-titlene er stort sett påstander. Det er ikke feil, men
oversikten på forsiden blir mindre konsekvent.

**Funn 08 — Forsiden er god øverst, men temaoversikten er en flat liste.**
Kartet sammen med ingressen fungerer godt. De tolv temakortene står i nummerrekkefølge uten gruppering. Temaene faller
naturlig i tre grupper:

- befolkning og flytting: 01, 02, 03, 05 og 10;
- arbeid og næring: 04, 06 og 08;
- tjenester og økonomi: 07, 09, 11 og 12.

Kortene oppgir kilde ulikt («BIN 2023», «SØA 2026», eller ingenting). Listen over de seks største kommunene bruker
navneformer som avviker fra resten av dashbordet («Rana - Raane», «Harstad - Hárstták»).

**Funn 09 — Kommunesiden har to navigasjonsnivåer og mange tall over bretten.**
Øverst står tre statusmerker og sju KPI-kort. Deretter kommer en prikkplott-seksjon, åtte faner og underfaner inne i
fanene. Fylkesmerket «Nordland» er cyan og ligger utenfor fargepaletten. KPI-en for sysselsatte innvandrere er farget
oransje uten at det er forklart.

**Funn 10 — «Fylket i tall» skyver innholdet langt ned på stor skjerm.**
Kortet har 15 rader og er åpent på stor skjerm. Det skyver seksjonsmenyen nesten én skjermhøyde ned.

**Funn 11 — Metodesiden har utdatert tekst og er svær å bla i.**
Teksten sier at alle tall hentes via «PxWebApi v0», men flere skript bruker nå v2, SCB og Statistics Finland. Siden er
26 100 piksler høy på mobil og har ingen innholdsfortegnelse eller filter etter tema.

Ikke målt: fargekontrast for de små, grå hint- og kildetekstene (11–12 piksler). De bør kontrolleres mot WCAG AA.

## Anbefalinger, i prioritert rekkefølge

**01. Legg et sammendrag med hovedfunn under heroen på hver temaside.**
3–5 nummererte funn, én setning hver, med lenke til akten. Begrunnelse: konklusjonen først er den viktigste regelen i
skrivestilen, og de lengste sidene trenger det mest.

**02. Kort ned ingressene til 60–80 ord.**
Flytt forbehold og detaljer til kildelinjen eller til en lukket «Les mer»-boks. Begynn med tema 10, 11 og 12.
Begrunnelse: tekstmengden har doblet seg på de nyeste sidene.

**03. Lag felles komponenter for figur (exhibit), tabell, boks og KPI i `src/styles/`.**
Figur-komponenten skal ha nummer, tittel, enhet og kilde. Ta komponentene i bruk side for side. Begrunnelse: én endring
gir lik form overalt og stopper veksten av egne stiler.

**04. Gjør tabellene lesbare på mobil.**
Lås den første kolonnen og vis et tydelig tegn på at tabellen kan rulles. Vis smale tabeller som kort per rad under 600
piksler. Begrunnelse: kolonner som ikke synes, er tall som ikke blir lest.

**05. Gruppér temakortene på forsiden og gi alle kortene samme oppbygning.**
Samme felt på alle: tittel, undertittel, ett nøkkeltall og kilde. Bruk kortnavn på kommunene. Begrunnelse: forsiden er
inngangen for de fleste.

**06. La «Fylket i tall» være lukket på alle skjermer, eller vis det i to kolonner på stor skjerm.**
Begrunnelse: kortet er oppslagsstoff og bør ikke skyve fortellingen ned.

**07. Rydd toppen av kommunesiden.**
Behold fire KPI-er over bretten, flytt resten til fanene, og bruk fylkesfargene fra paletten. Begrunnelse: mindre
konkurranse om oppmerksomheten.

**08. Gi tema 02, 03 og 06 minst én figur i hver akt.**
Begrunnelse: likere form og mindre tekst.

**09. Gi metodesiden en innholdsfortegnelse eller et filter etter tema, og oppdater beskrivelsen av datakildene.**

**10. Kontroller kontrasten på hint- og kildetekst, og vurder ett felles mønster for hovedtitlene.**
For eksempel påstand med kursiv fremheving, slik tema 11 og 12 har.

**Anslått omfang:** 01, 02, 05, 06 og 09 er hver en kort arbeidsøkt. 03 og 04 er større, fordi alle sider berøres, og bør
gjøres samlet. 07 og 08 krever egne vurderinger av innholdet.
