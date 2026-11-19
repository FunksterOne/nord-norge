# Plan: kommunesiden, fylkessidene og landsdelssiden (anbefaling 07)

Utarbeidet 19. november 2026. Grunnlag: `analyse/LAYOUT-VURDERING.md`, funn 09 og anbefaling 07. Gjennomgått:
`kommune.html?k=5603` (Hammerfest) på 1280 og 390 piksler, `fylke.html?f=Troms` og `nord-norge.html` på 1280 piksler,
mørk visning. Ikke gjennomgått: lys visning, `sammenlign.html` og innholdet i hver fane i detalj.

## Konklusjon

Kommunesiden har mye godt innhold, men leseren må gjennom nesten tre skjermhøyder før selve innholdet begynner, og den
beste oppsummeringen står nederst i første fane. Anbefalingen er å snu rekkefølgen: fire nøkkeltall og kortversjonen
øverst, sammenligningen med de 80 kommunene kortere, deretter fanene. Fylkes- og landsdelssiden får samme topp, slik at
de tre nivåene følger én mal. Arbeidet deles i tre faser.

## Observasjoner

**Funn 01 — Innholdet begynner langt ned.** På Hammerfest-siden er toppen (navn, tre statusmerker, sju nøkkeltall)
668 piksler høy, og sammenligningen med de 80 kommunene (seks svermdiagrammer og kart) 1 581 piksler. Fanene begynner
dermed rundt 2 400 piksler ned, nær tre skjermhøyder på en bærbar PC. På mobil fyller de sju nøkkeltallene alene
nesten én skjermhøyde.

**Funn 02 — Kortversjonen står nederst.** Avsnittet «Kortversjon — demografi og framtid» er den beste oppsummeringen av
kommunen (folketall, SSB-bane, strukturmodellen, forsørgerbrøk, økonomi), men står nederst i fanen Befolkning.
Tilsvarende kortversjoner står i fanene Sammensetning («Hvem bor her») og Levekår («Inntektsbildet»).

**Funn 03 — Tall gjentas.** Folketallet står i nøkkeltallene øverst, i statusmerket «nedgang 3 %», i nøkkeltallene i
fanen Befolkning og i kortversjonen. Endringen mot 2050 står både som merke og som nøkkeltall i fanen.

**Funn 04 — To navigasjonsnivåer som ser like ut.** Åtte faner, og inne i flere faner egne knapperader (Folketall,
Drivkrefter, Forsørgerbrøk, Aldring; Livsfaser, 5-årig, Ettårig; Begge, Menn, Kvinner). Den aktive underknappen er
fylt blå, akkurat som den aktive fanen. Fanene kan lenkes til (`?sec=`), og det bør beholdes.

**Funn 05 — Fanene er svært ulike i lengde.** Arbeid og forsørgerbyrde er 5 595 piksler, Sammensetning 3 142,
Bærekraft 775. Figurene er ikke nummerert og har ikke felles enhets- og kildelinje (fase A gjaldt bare temasidene).

**Funn 06 — Fargebruk.** Nøkkeltallet «Sysselsatte innvandrere» er farget med seriefargen for innvandrere i
sysselsettingsfiguren (`--syss`), uten forklaring øverst på siden.
*Rettelse til layoutvurderingen:* Fylkesmerket er ikke utenfor paletten. Det bruker fylkesfargene (`--nl`, `--tr`,
`--fi`), som er definert i `tokens.css` og brukes likt i hele dashbordet. Funn 09 i LAYOUT-VURDERING.md var feil på dette
punktet.

**Funn 07 — Navnet.** Overskriften er SSB-formen «Hammerfest - Hámmerfeasta», med bindestrek og mellomrom. Resten av
dashbordet bruker kortnavn (`NN.kortNavn`).

**Funn 08 — Fylkessiden mangler konklusjon øverst.** Landsdelssiden åpner med en ingress som sier hva som skjer.
Fylkessiden åpner med «Velg seksjon nedenfor for å se hvordan dette fylket utvikler seg mot 2050.» Begge sidene har to
overskriftsnivåer i hver seksjon: et eget kort «1 · Befolkning» og rett under «Akt 1 · Hva skjer».

## Status

Fase 1 er gjennomført 19. november 2026. Avvik fra planen: overskriften er det første navnet i kommunens offisielle navn
hos SSB, ikke alltid det norske. For Gáivuotna – Kåfjord – Kaivuono står det samiske navnet først, og siden følger det.
Fase 2 er gjennomført samme dag. Underknappene er små valg med strek under det aktive; figurtitlene i fanene får
nummer (`nummererFigurer` i kommune.html); figuren i fanen Befolkning og landbakgrunnskortet har fått kildelinje; og
«Hvem bærer hvem?» legger fordelingen per 100 sysselsatte og scenariotabellen bak «Les mer» på kommunesiden
(`forsorgCard(..., {kompakt:true})`). Fanen Arbeid gikk fra 5 595 til 4 873 piksler på Hammerfest-siden. Figurene i
Levekår og KOSTRA-delen av Økonomi ligger i lukkede bokser under en tekstoppsummering og er ikke nummerert. Rettelse
til planen: bare `forsorgCard` deles med fylkes- og landsdelssiden, så risikoen var mindre enn antatt.
Fase 3 gjenstår.

## Anbefalinger

### Fase 1 — toppen av kommunesiden

**01. Fire nøkkeltall øverst.** Forslag: folketall i dag, endring 2026–2050 (SSB MMMM), forsørgerbrøk i dag og 2050, og
netto driftsresultat 2025 mot TBU-normen 1,75 %, med ROBEK-status i merknaden. Begrunnelse: de fire dekker de tre
spørsmålene siden handler om — hvor mange, hvor gamle, hvor godt rustet. De seks andre nøkkeltallene (innvandrerandel,
medianalder, under skolealder, 80 år og over, 0–17/67+, sysselsatte innvandrere) flyttes til fanen Sammensetning, der de
hører hjemme. De tre statusmerkene fjernes; innholdet står i nøkkeltallene.

**02. Kortversjonen rett under nøkkeltallene.** Avsnittet flyttes fra bunnen av fanen Befolkning og blir sidens
ingress. Begrunnelse: konklusjon først.

**03. Kortere sammenligning med de 80 kommunene.** Tre svermdiagrammer synlige (folketall 2026–2050, forsørgerbrøk
2050, netto driftsresultat), de tre andre bak «Vis tre til». Kartet beholdes.

**04. Navnet.** Norsk navn som overskrift, samisk eller kvensk navn på egen linje rett under, i samme skrifttype og
mindre grad. Begge navnene skal fortsatt stå synlig øverst.

**05. Farge på nøkkeltall.** Ingen nøkkeltall får seriefarge uten forklaring. Tall som bryter en norm (for eksempel netto
driftsresultat under 1,75 %), får varselfarge med normen i merknaden.

### Fase 2 — fanene

**06. Underknappene får eget utseende.** Små, avgrensede valg (segmentert kontroll) i stedet for fylte blå knapper, så
de ikke kan forveksles med fanene. Fanene og `?sec=`-lenkene beholdes.

**07. Felles figurstandard.** Figurer og tabeller i fanene migreres til komponentene fra fase A (nn-fig med nummer,
enhet og kilde; nn-tabell). Nummereringen følger fanen som vises, fordi skjulte faner ikke teller.

**08. Lange faner.** Arbeid og forsørgerbyrde og Sammensetning gjennomgås kort for innhold som kan stå bak «Les mer».
Ingen tall fjernes.

### Fase 3 — fylkes- og landsdelssiden

**09. Konklusjon øverst på fylkessiden.** Ingressen lages av tallene, etter mønster fra landsdelssiden: folketallets
utvikling, hvor mange kommuner som får nedgang, og forsørgerbrøken mot 2050.

**10. Samme fire nøkkeltall på alle tre nivåer.** Fylkes- og landsdelssiden får de samme fire nøkkeltallene som
kommunesiden, over «Fylket i tall». Netto driftsresultat vises der som andel kommuner under TBU-normen.

**11. Ett overskriftsnivå per seksjon.** Kortet «1 · Befolkning» slås sammen med «Akt 1 · Hva skjer».

## Omfang og risiko

Fase 1 er én arbeidsøkt. Fase 2 er én til to, fordi fanene tegnes av `assets/app.js` (2 891 linjer, eldre kode) og
`kommune.html`. Fase 3 er én. Risikoen ligger i fase 2: fanene deler tegnefunksjoner med fylkes- og landsdelssiden, så
hver endring må kontrolleres på alle tre sidetyper. Kontroll etter hver fase: skjermbilder av tre kommuner (en stor, en
middels, en liten), alle tre fylker og landsdelen, på 1280 og 390 piksler, i mørk og lys visning.

## Valg som trengs

1. Er de fire nøkkeltallene i anbefaling 01 riktige, eller skal ett byttes (for eksempel innvandrerandel i stedet for
   netto driftsresultat)?
2. Skal statusmerkene fjernes helt, eller beholdes som én linje?
3. Skal sammenligningen vise tre svermdiagrammer, eller alle seks som i dag?
