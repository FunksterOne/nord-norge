# Bosetting 2027 og Fafo 2026:32 — vurdering og plan

Status: plan, ikke implementert. Utarbeidet 23. oktober 2026.

## Konklusjon

Kildene hører hjemme på tema 01 «Hvem blir værende?» og på kommunesidene. De er ikke stoff for en egen temaside.

- **IMDis anmodning for 2027** gir et nytt tall for hver kommune. Den passer i Befolkning-fanen på kommunesidene og som kart på tema 01.
- **Fafo-rapporten** gjelder unntakene fra flyttebegrensningene. Den hører hjemme i akt 05 om flytteforbudet, som allerede følger saken.

Grunnlaget er:
- IMDi, «Forventer færre flyktninger i 2027», 23. oktober 2026
- IMDi, oversikt over anmodning om bosetting per kommune 2027 (xlsx)
- Fafo-rapport 2026:32 «Vilkårlig og restriktivt» (Kjeøy, Andresen og Zhang)

Kildefilene ligger i `kilder/` og er ikke versjonert.

## 1. Hva tallene viser

**Observasjon — anmodningen går ned med en tredel.** IMDi ber kommunene bosette 8 680 flyktninger i 2027. For 2026 var anmodningen 13 000, og kommunene vedtok 10 727. Om lag 10 500 ventes bosatt i 2026.

**Observasjon — Nord-Norge får fortsatt dobbelt så mye som befolkningen tilsier.** De 80 kommunene er anmodet om 1 595 i 2027, mot 2 366 i 2026. Det er 18,4 % av landet, mot 8,7 % av befolkningen. Andelen er den samme som i 2026 (18,2 %) og som de bosatte i 2025 (18,6 %, 2 340 av 12 596). Kontroll: arket gir 2 366 for 2026, det samme tallet som dashbordet allerede bruker.

| | Anmodning 2026 | Vedtak 2026 | Anmodning 2027 | Endring i anmodningen |
|---|---:|---:|---:|---:|
| Nordland | 1 100 | 1 050 | 845 | −23 % |
| Troms | 850 | 713 | 510 | −40 % |
| Finnmark | 416 | 330 | 240 | −42 % |
| Nord-Norge | 2 366 | 2 093 | 1 595 | −33 % |
| Landet | 13 000 | 10 727 | 8 680 | −33 % |

**Observasjon — flere kommuner utenfor.** 22 av de 80 kommunene er ikke anmodet for 2027, mot 14 i 2026. Ti av dem bosatte etter vedtak i 2026:

| Fylke | Kommuner |
|---|---|
| Nordland | Bindal, Vega, Hattfjelldal, Rødøy, Beiarn |
| Troms | Dyrøy, Storfjord |
| Finnmark | Nordkapp, Porsanger, Lebesby |

I landet som helhet er 58 av 357 kommuner ikke anmodet.

**Observasjon — små kommuner bærer mest per innbygger.** Regnet per 1 000 innbyggere er anmodningen høyest i:
- Evenes (12,9)
- Loppa (11,8)
- Nesseby (11,4, ny i 2027)
- Lavangen (10,0)
- Gratangen (9,4)

De store byene ligger på 1–3 per 1 000. Eksempler: Tromsø 120 (2026: 170), Bodø 145 (175), Harstad 110 (150) og Vadsø 20 (67).

**Observasjon — enslige mindreårige.** 74 av 400 i landet skal bosettes i Nord-Norge, det vil si 18,5 %.

**Hypotese.** IMDi legger vekt på arbeids- og utdanningsmuligheter, levekår og uønsket sekundærflytting (IMDi, 23.10.2026). Dersom kriteriet om sekundærflytting veier tyngre framover, forventer vi at flere små nordnorske kommuner faller ut i 2028. Nord-Norge har høyest fraflytting fra bosettingskommunene, så landsdelens andel kan da gå ned. Dette kan ikke avgjøres av tilgjengelige data før vedtakene for 2027 foreligger.

## 2. Fafo-rapport 2026:32 — det som er relevant for dashbordet

- **Unntak gis ytterst sjelden, og praksisen er vilkårlig.** Det gjelder avtalt sekundærflytting, introduksjonsprogram ved flytting og sosialhjelp når et avslag er «åpenbart urimelig». Hvem som får unntak, avhenger mer av hvilken kommune og hvilken saksbehandler de møter enn av situasjonen deres (Sammendrag, s. 4–5).
- **Regjeringen utreder to modeller høsten 2026.** Den ene er et generelt flytteforbud, den andre et forbud mot å flytte til enkelte områder (s. 8). Rapporten mener begge krever rom for unntak for å være i tråd med Grunnloven og menneskerettighetene.
- **Bakgrunnstall fra SSB-monitoren.** Over 80 % av flyktningene som ble bosatt i 2010–2017, bodde fortsatt i bosettingskommunen etter fem år. For dem som ble bosatt i 2018–2019, var andelen 87–88 % (s. 9). Det stemmer med det dashbordet viser i akt 03.
- **Forbehold om Nord-Norge.** Svarprosenten var lavest i Finnmark (33 %) og Troms (38 %), og 39 % i kommuner med sentralitet 6 (s. 13). Rapporten sier derfor minst om de kommunene i Nord-Norge som bosetter flest per innbygger. Fem av de 18 intervjukommunene ligger i Nord-Norge.

## 3. Forslag til innlemming

**Anbefaling 01 — Akt 05 på tema 01 oppdateres.**
- **Nøkkeltall:** «Nord-Norge er anmodet om 18,4 % av flyktningene i 2027, mot 8,7 % av befolkningen». Det kommer i tillegg til tallet for de bosatte i 2025.
- **Fafo-boks:** «Unntakene er sjeldne og vilkårlige». Tre setninger med sidetall, og forbeholdet om svarprosenten i Finnmark og Troms.
- **Statusboksen:** ny dato. Det skal kontrolleres at det fortsatt ikke er publisert noe høringsnotat. Modellen med forbud mot flytting til enkelte områder nevnes.
- **Kilderaden:** utvides med IMDi 23.10.2026 og Fafo 2026:32.

**Anbefaling 02 — Nytt element i akt 05 eller en kort akt 06, «Bosettingen i 2027».**
- **Kart:** anmodningen per 1 000 innbyggere, som ny skjult kartindikator `bos2027`. De 22 kommunene uten anmodning markeres med grått.
- **Tabell:** fylkestabellen over.
- **Tekst:** én setning om at tallene er anmodninger, ikke vedtak.

**Anbefaling 03 — Kommunesidene, Befolkning-fanen.** Én linje: «IMDi ber [kommunen] bosette X flyktninger i 2027, Y per 1 000 innbyggere (2026: anmodet A, vedtatt B)». For kommuner uten anmodning skal det stå at kommunen ikke er anmodet i 2027.

**Anbefaling 04 — Fylkes- og landsdelssiden.** Fylkets tall i tabellen og andelen av landet.

**Anbefaling 05 — Metodesiden.** Kortet «Bofasthet» utvides med anmodningen for 2027 og med hva den er og ikke er:
- Den er IMDis anmodning, ikke kommunestyrets vedtak og ikke faktisk bosetting.
- Enslige mindreårige er inkludert.
- IMDi kan justere tallene gjennom året.

## 4. Gjennomføring

- **Data:** `fetch_bofasthet.py` leser arket fra `analyse/bosetting-2027/kilder/`. Navnet «Bø (Nordland)» knyttes til 1867. Skriptet lagrer et lite avledet uttrekk med de 80 kommunene i `analyse/bosetting-2027/anmodning_2027_nn.json`, versjonert, slik at bygget ikke trenger regnearket.
- **Datablokk:** `BOFAST_DATA.anmodning`, med kommune → [2027, anmodning 2026, vedtak 2026, enslige mindreårige] og summer per fylke, for landsdelen og for landet.
- **Kontroll:** summene skal stemme med fylkesarket (Nordland 845, Troms 510, Finnmark 240, landet 8 680), og 2026 skal stemme med `anmodet_2026_nn` (2 366).
- **Omfang:** om lag en halv dag.

## 5. Valg som trenger klarsignal

1. **Plassering på tema 01:** utvide akt 05 (anbefalt) eller lage en egen akt 06 «Bosettingen i 2027»?
2. **Kommunesidene:** ta med linjen i Befolkning-fanen (anbefalt)?
3. **Kartet:** vise anmodningen per 1 000 innbyggere (anbefalt) eller i antall personer?
