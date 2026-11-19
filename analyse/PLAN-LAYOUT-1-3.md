# Plan: hovedfunn, kortere ingresser og felles komponenter (anbefaling 01–03)

19. november 2026. Bygger på LAYOUT-VURDERING.md. Avklaringene er besluttet 19.11.2026 etter forslagene (se nederst). Venter på klarsignal for fase A.

## Konklusjon

Arbeidet gjøres i tre faser, i denne rekkefølgen: felles komponenter først, deretter hovedfunn, til slutt kortere
ingresser. Komponentene kommer først fordi hovedfunn-boksen og «Les mer»-boksen er komponenter selv, og fordi hver side
bare skal åpnes og testes én gang per fase.

Omfanget er de tolv temasidene. Fylkes-, landsdels- og kommunesidene bygges av den gamle `app.js` og har sitt eget
oppsett. De tas i en egen runde. Ingen tall eller kilder endres. Endringene gjelder form og tekstmengde.

## Fase A — felles komponenter

### Hva som finnes i dag

Figurnummereringen finnes allerede. `base.css` teller `.card > .ch h3` og `.exhibit-title`. Bare tema 04 og 08 bruker
dette. Andre sider har egne beholdere uten nummer:

| Komponent | Sider og antall i dag |
|---|---|
| Figurbeholdere | `hs-boks` (tema 12: 14), `ug-boks` (tema 10: 13), `graf-kort` (tema 07: 13), `fylke-graf` (tema 05: 3), `card` (tema 08: 11) |
| Tabeller | `hs-tabell` (15), `konj-tabell` (7), `norden-tabell` (8), `gap-tabell` (9), `kvote-tabell` (12), `el-tabell` (5), `beh-tabell` (7), `fb-tabell` (1) |
| Etikettmerker | `hs-merke` (15), `ug-merke` (12) |
| Undertekst i KPI-kort | stort sett `.nh`, men `.s` i tema 07 |
| Stiler per side | 11–67 linjer i hver temaside |

### Nye komponenter i `src/styles/komponenter.css`

Filen importeres i `main.js`, slik at alle sider får den.

- **`.nn-fig` (figur):**
  - Overlinje med nummeret «Figur 01» (samme teller som i dag, utvidet til `.nn-fig`).
  - Tittel (`h3`) og eventuelt enhetslinje (`.nn-fig-enhet`).
  - Selve figuren.
  - Kildelinje (`.nn-kilde`), alltid med «Kilde:» foran, i samme skriftstørrelse og farge overalt.
  - Valgfritt merke (`.nn-merke`, for eksempel SSB, FHI eller Beregnet) foran tittelen.
- **`.nn-tabell` (tabell):**
  - Én tabellstil med tabulære tall og høyrestilte tallkolonner (`.num`).
  - Summerader (`tr.sum`) med tykkere linje over, gruppeoverskrifter (`tr.gr`) og uthevet rad (`tr.uthev`).
  - Omsluttes av `.nn-tabell-rull`. Den forbereder mobilforbedringen i anbefaling 04 (låst første kolonne og tydelig
    tegn på at tabellen kan rulles), men den delen gjøres ikke i denne runden.
- **`.nn-funn` (hovedfunn):** se fase B.
- **`.nn-mer` (Les mer):** en lukket `details` for detaljer og bakgrunn som tas ut av ingressene.
- **`.nn-boks` (notis):** tekstboks med venstrelinje. Den erstatter `kildeboks` og liknende.
- **KPI-kort:** `.nh` blir standard for underteksten. `.s` i tema 07 skiftes ut.

Diagrammene trenger ingen endring. `NN.placeholder` tegner inn i hvilken som helst beholder, og kildeteksten i
diagrammene beholdes.

### Gjennomføring

1. Skriv `komponenter.css` og prøv den på tema 12, som er siden med flest figurer og tabeller.
2. Ta før- og etterbilder (stor skjerm og mobil, mørk og lys visning) og kontroller at alle figurer har nummer.
3. Flytt sidene over i denne rekkefølgen: 12, 10, 05, 07, 08, 04, 01, 02, 03, 06, 09, 11. Sidespesifikke stiler som
   blir overflødige, slettes. Stiler som er særegne for én side, beholdes (for eksempel kortene for scenariene og
   vektskålen i tema 02).
4. Lag et kontrollskript `tools/sjekk_layout.cjs` som finner gamle klassenavn som ikke er tatt ut, og figurer uten nummer
   eller kildelinje.

## Fase B — hovedfunn øverst på hver temaside

### Utforming

En boks med overskriften «Hovedfunn» rett under heroen. Den har 3–5 nummererte funn: «01», «02» og så videre i
kapitéler. Hvert funn er én setning på høyst 25 ord, med et tall der det finnes, og ender med en lenke til akten som
utdyper det («→ Akt 03»).

På stor skjerm står funnene i to kolonner. På mobil står de i én. Boksen erstatter ikke heroens ingress, men ingressen
kortes ned i fase C.

### Tall som må holde seg riktige

Der tallene i aktene beregnes av sidens skript (tema 05, 07, 08, 10 og 12), fylles tallene i funnene inn av det samme
skriptet med de samme variablene. Da kan de ikke komme i utakt med figurene når dataene oppdateres. Der teksten allerede
er statisk (tema 02, 03, 06, 09 og 11), skrives funnene som statisk tekst. Tallene kontrolleres mot datafilen med
`tools/fasit.cjs`.

### Eksempel, tema 12 (utkast)

1. Aldringen alene gir 24,8 % flere liggedøgn fram mot 2045. Helse Nords plan regner med 7,3 %. → Akt 02
2. Fire av ti bor i kommuner med over én times kjøretid til akuttsykehus. → Akt 04
3. Hele nettoveksten i sykepleiere siden 2019 kom fra utenlandsfødte. → Akt 03
4. Omsorgsårsverkene per eldre har falt i nord og økt i landet, og forspranget er nesten halvert. → Akt 03
5. Helsereformutvalgets flertall vil legge ned Helse Nord RHF, mens 74 av 80 kommuner er mindre enn utvalgets mål om 15 000
   innbyggere. → Akt 07

Funnene til de andre sidene skrives ut fra aktene som finnes. Utkastet legges fram samlet for godkjenning før det
publiseres.

## Fase C — kortere ingresser

### Regler

- Heroens ingress: høyst 60 ord.
- Ingressen i hver akt (`.akt-intro`): 60–80 ord, ett poeng og konklusjonen først.
- Forbehold som påvirker hvordan et tall skal leses, blir stående synlig, men flyttes til kildelinjen under figuren.
- Bakgrunn, metode og detaljer flyttes til en `.nn-mer`-boks i akten eller til metodesiden.
- Hypoteser beholdes, merket «Hypotese:».
- Tall, kilder og formuleringer i funnene endres ikke, bare fordelingen mellom ingress, kildelinje og «Les mer».

### Sider som må kortes mest (ord i aktenes ingresser, målt 19.11.2026)

| Side | Ingresser over 80 ord |
|---|---|
| Tema 12 | 79, 138, 158, 128, 75, 137, 145, 156 (hero 101) |
| Tema 11 | 121, 89, 140, 97, 93, 93, 96, 93 |
| Tema 10 | 81, 98, 106, 75, 105, 106, 160, 108 |
| Tema 05 | 99 (hero 89) |
| Tema 09 | 98, 94 |
| Tema 08 | 98 (akt 07) |
| Tema 01 | 97, 92 |
| Tema 04 | 123 (akt 06) |
| Tema 02 | 113 (akt 06) |

## Kontroll for alle tre fasene

`revisjon.py` utvides og kjøres før og etter hver fase. Den skal vise:

- at ingen ingress er over 80 ord og ingen hero over 60;
- at alle figurer har nummer og kildelinje;
- at ingen gamle klassenavn er igjen på sidene som er flyttet over;
- at ingen side ruller sidelengs, og at ingen side har skriptfeil.

I tillegg tas skjermbilder av alle temasider på stor skjerm og mobil, og noen i lys visning. Det blir én commit per fase,
pushet og kontrollert på nettstedet.

## Omfang og avklaringer

**Omfang:**
- Fase A: to arbeidsøkter (prøveside og tolv sider).
- Fase B: én arbeidsøkt pluss din gjennomlesing av funnene.
- Fase C: én arbeidsøkt.

**Beslutninger (19.11.2026, etter forslagene):**
1. Figurnumrene starter på 01 på hver side, som i dag.
2. Funnene til alle tolv sider legges fram samlet og godkjennes før de publiseres.
3. Fylkes-, landsdels- og kommunesidene tas i en egen runde etter denne.
