# Åpne data om spesialisthelsetjenesten i Nord-Norge — kildekartlegging

Utarbeidet 29. oktober 2026 for temasiden om sykehusene i nord. Alle tall er hentet med skriptene i `skript/` samme dag. Rådata ligger i `kilder/data/` (gitignorert).

## Konklusjon

Temasiden kan bygges på åpne data uten innlogging. Fire kilder bærer det meste:

- **Opptaksområder:** SSB 13982 med vår kommunefordeling (`data/opptak.json`).
- **Personell:** SSB 13953 (avtalte årsverk etter yrke og HF, 2008–2025).
- **Aktivitet og bruk:** SSB 14824 og FHI/NPR tabell 517 for regionen, og SKDEs helseatlas for HF-områdene.
- **Ventetid:** FHI/NPR sine Excel-filer per HF og tertial.

Tre ting finnes ikke åpent:

- Ingen offentlig kilde lister kommunene i hvert lokalsykehusområde. Fordelingen er utledet av SSB-tall (se kilde 1).
- Innleie per HF finnes ikke som tabell. Det finnes bare regiontall i én SSB-artikkel.
- Fristbrudd finnes bare per RHF, ikke per HF.

---

## 1. Opptaksområder per kommune (somatikk)

**Fil:** `data/opptak.json`. Skript: `skript/opptak_los.py` (løser) og `skript/opptak_bygg.py` (bygger og kontrollerer).

**Observasjon.** Ingen åpen kilde lister kommunene i hvert lokalsykehusområde. Følgende er undersøkt uten treff:
- Helsedirektoratet
- SSB KLASS. Klassifikasjon 435 gjelder serviceområder for akuttmottak fra 2019, uten kommunetilordning.
- SKDE
- Helseforetakenes sider

**Metode.** SSB 13982 oppgir befolkningen per lokalsykehusområde. Kodelisten `vs_HelseOpptakSom` gir S01–S11 for Helse Nord. Skriptet prøver alle fordelinger av de usikre kommunene og beholder de som gir nøyaktig SSBs tall:
- per område
- for 2024, 2025 og 2026
- målt mot kommunefolketallet i SSB 07459 per 1. januar.

Fordelingen er entydig, med ett unntak (Tjeldsund, se under). Kontrollen gir null avvik alle tre år.

**HF-nivået** er i tillegg bekreftet mot UNNs egen kommuneliste. Den viser 24 kommuner og 195 499 innbyggere per 1.1.2025, som er identisk med SSB ([unn.no/om-oss](https://www.unn.no/om-oss)).

**Kontrollpunktene:**

| Kommune | Resultat |
|---|---|
| Narvik, Evenes, Lødingen | UNN Narvik. Lødingen hører til UNN, ikke Nordlandssykehuset. |
| Hamarøy | Nordlandssykehuset Bodø |
| Tjeldsund | UNN Harstad, men delt. SSB regner 735, 734 og 835 innbyggere (2024–2026) fra Harstad-området til Narvik. Jeg har ikke klart å stedfeste dem: ingen kombinasjon av grunnkretser i Tjeldsund passer alle tre år. Restposten er lagt inn som konstant i kontrollen. |
| Andøy | Nordlandssykehuset Vesterålen, ikke UNN |
| Ibestad, Gratangen, Lavangen, Salangen | UNN Harstad. Bardu hører til Tromsø. |
| Bindal | Helgelandssykehuset (Sandnessjøen). Namsos-området i SSB består av Namdal-kommunene og Osen, uten Bindal. |
| Kvænangen | UNN Tromsø |
| Loppa | Finnmarkssykehuset Hammerfest |
| Karasjok | Hammerfest |
| Lebesby, Gamvik, Tana | Kirkenes |
| Røst, Værøy | Bodø, ikke Lofoten |
| Lurøy | Delt. Fastlandet (6 grunnkretser, 548 innbyggere i 2026) hører til Mo i Rana, øyene (1 405 innbyggere) til Sandnessjøen. Løsningen er entydig etter grunnkretstall fra SSB 04317, men den er ikke bekreftet i noen tekstkilde. |
| Træna | Sandnessjøen |
| Nesna, Rødøy | Mo i Rana |

**Endringen på Helgeland:** Mosjøen-området (S10) hadde 16 179 innbyggere i 2025 og er tomt i 2026. Vefsn er flyttet til Mo i Rana, og Grane og Hattfjelldal til Sandnessjøen. Endringen stemmer med to kilder:
- Helse Nords vedtak (styresak 22-2025 og foretaksmøtet 24.3.2025)
- Helgelandssykehusets nyhet 5.9.2025: akutt- og døgnfunksjonene i somatikken flyttes fra Mosjøen 1.10.2025.

Feltet `sykehus_2024_2025` i fila viser det tidligere lokalsykehuset.

**Forbehold:**
- Fordelingen gjelder somatikk. Opptaksområdene for psykisk helsevern er ikke undersøkt.
- Vedtaket på Helgeland gjelder indremedisin. For kirurgi har Vefsn, Grane og Hattfjelldal trolig allerede brukt Mo i Rana eller Sandnessjøen. Det er ikke kontrollert.
- SSB 13982 viser hvilken avtale som gjelder, ikke hvor pasientene faktisk behandles. Pasientstrømmene kan avvike.

## 2. Sykehus og DMS med koordinater

**Fil:** `data/sykehus.json`, med 16 lokalisasjoner: 12 sykehus og 4 DMS, Longyearbyen medregnet.
- Skript: `skript/sykehus_hent.py`, `sykehus_koord.py` og `sykehus_mfr.py`.
- Kontroll av koordinatene: `kilder/data/sykehus/koord_kontroll.json`.

**Innhold.** Fila gir funksjonsnivå etter Helse Nords utviklingsplan: regionsykehus, stort akuttsykehus, åtte akuttsykehus og Mosjøen uten akuttfunksjon. Den gir også akuttkirurgi, indremedisinsk akuttfunksjon og fødetilbud med kildelenker.

Fødetilbudet er kontrollert mot fødsler per institusjon i Medisinsk fødselsregister (FHI, 2025–juli 2026):

| Fødetilbud | Steder |
|---|---|
| Fødeavdeling (9) | Tromsø, Harstad, Narvik, Bodø, Vesterålen, Mo i Rana, Sandnessjøen, Hammerfest, Kirkenes |
| Fødestue (4) | Lofoten, Finnsnes, Sonjatun, Alta |

Brønnøysund er kodet «ingen», fordi fødestua har vært stengt for fødsler siden 20.3.2026.

**Koordinater.** Koordinatene kommer fra OpenStreetMap og Kartverket. Alle ligger 0–138 m fra Kartverkets adressepunkt og i riktig kommune etter Kartverkets kommuneinfo-API. Jeg har i tillegg sjekket hver koordinat mot stedet: Breivika, Furumoen, det nye sykehuset i Hammerfest, Gravdal, Stokmarknes og så videre.

**Forbehold:**
- Akuttkirurgi i Narvik, Lofoten og Vesterålen står ikke uttrykkelig på helseforetakenes sider. Verdien «true» bygger på at nedleggelsen som ble foreslått i 2024, ikke ble gjennomført, og at funksjonen er finansiert i budsjettet for 2027.
- `notater/sykehus.md` (eget arbeid) setter flere av disse til «ikke verifisert». Det må avklares før siden publiseres.
- Klinikk Alta er kodet som DMS fordi skjemaet ikke har noen egen kategori for den.

## 3. Personell

| Tabell | Innhold | Brukt |
|---|---|---|
| **SSB 13953** | Avtalte årsverk etter yrke (30 grupper), tjenesteområde og helseforetak, 2008–2025 | `data/arsverk_hf.csv` (2015–2025, Hele landet, Helseregion Nord, Helse Nord RHF og de fire HF-ene; tjenesteområde «I alt» og somatikk) |
| SSB 13954 | Samme, etter utdanning | Ikke hentet. Metadata ligger i `kilder/data`. |
| SSB 14080 | Legespesialister og psykologer etter spesialitet og HF, 2008–2025 | Ikke hentet. Aktuell hvis siden skal vise spesialiteter. |
| SSB 13849 | Samhandlingsleger, timeverk etter helseregion, 2014–2025 | Ikke hentet |
| SSB-artikkel 15.11.2024, «Mest bruk av vikarbyrå ved sykehusene i Nord-Norge» | Innleie, vikarer, overtid og ekstrahjelp som andel av lønnskostnadene. Per region for 2023, og for Helse Nord 2019–2023. | `data/innleie_ssb_2023.json`, hentet fra figurdataene i siden (`skript/innleie_ssb_artikkel.py`) |

**Observasjon (13953).** Avtalte årsverk økte fra 2015 til 2025 i begge sammenligningene:

| | 2015 | 2025 | Endring |
|---|---|---|---|
| Helseregion Nord, alle årsverk | 12 983 | 15 520 | +19,5 % |
| Landet, alle årsverk | 122 176 | 142 826 | +16,9 % |
| Legespesialister, Helseregion Nord | 1 263 | 1 672 | +32 % |
| Legespesialister, landet | 13 072 | 17 087 | +31 % |

Fordelt på helseforetak i 2025:

| HF | Avtalte årsverk 2025 |
|---|---|
| UNN | 7 157 |
| Nordlandssykehuset | 3 904 |
| Helgelandssykehuset | 1 715 |
| Finnmarkssykehuset | 1 817 |

**Observasjon (innleie, 2023).** Helse Nord skiller seg ut på alle fire kostnadene. Tallene er andel av lønns- og personalkostnadene:

| Kostnad | Helse Nord | Andre regioner |
|---|---|---|
| Innleie fra vikarbyrå | 3,9 % | 0,9–1,5 % |
| Vikarer | 6,0 % | 2,9–4,1 % |
| Overtid | 5,4 % | 3,4–4,5 % |

Innleien i Helse Nord var 2,9 % i 2019 og 4,6 % i 2022.

**Forbehold:**
- **Helseregion Nord (H05) er ikke det samme som summen av HF-ene.** H05 er 792 årsverk høyere enn de fire HF-ene og RHF-et samlet i 2025. Differansen er trolig Helse Nord IKT, Sykehusapotek Nord og private institusjoner. Det er ikke kontrollert. Bruk HF-kodene når HF-ene skal sammenlignes.
- **Brudd i RHF-tallene.** Helse Nord RHF falt fra 361 til 113 årsverk mellom 2015 og 2020. Det skyldes trolig at funksjoner ble skilt ut i egne foretak, ikke kutt.
- **Innleie per HF** finnes ikke åpent. Kilden er HF-enes egne regnskapstall til SSB, og de er ikke publisert i Statistikkbanken. Nyere tall enn 2023 er ikke funnet.

## 4. Aktivitet og bruk

| Tabell | Innhold | Regionnivå | Brukt |
|---|---|---|---|
| **SSB 14824** | Pasienter, døgnopphold, oppholdsdøgn, polikliniske kontakter og dagbehandlinger i somatikken. Etter bosted, alder, aktør og diagnose (222 grupper). | Landet, fylker (2024-, 2020- og 2019-inndeling) og helseregioner. **Ikke kommune eller HF.** | `data/somatikk_bosted.csv` (2015–2025, alle aldersgrupper, diagnose i alt) |
| **SSB 13942** | Døgnplasser, utskrivninger, liggedager, polikliniske konsultasjoner, dagbehandlinger og beleggsprosent. Etter **behandlende** HF. | Landet, Helseregion Nord og fire HF | `data/aktivitet_hf.csv` (2015–2025, i alt og somatikk) |
| **SSB 13982** | Befolkningen per opptaksområde (HF og lokalsykehus), etter alder | HF og lokalsykehus | `data/befolkning_opptak.csv` (2015–2026; aldersgruppene 0–17, 18–66, 67–79 og 80+). Nevner for rater per HF-område. |
| **FHI/NPR tabell 517** | Nøkkeltall for somatikk (pasienter, døgnopphold, oppholdsdøgn, poliklinikk og dagbehandling), etter bostedsregion. **Har jan–apr og jan–aug 2026.** | Landet og fire regioner | `data/npr_som_nokkeltall.csv` (2017–aug. 2026; `skript/fhi_npr.py`) |
| **SKDEs helseatlas** | 26 analyser med kjønns- og aldersjusterte rater per 1 000 innbyggere (direkte metode, befolkningen i 2023 som referanse) | Opptaksområde = HF-område (21 i landet) og region. Ikke lokalsykehus. | `data/skde_atlas_rater.csv` (alle år og nivåer) og `data/skde_atlas_nord.csv` (siste år, de fire HF-ene mot landet); `skript/skde_atlas.py` |
| SSB 12764 | Kjøretid og avstand langs vei til nærmeste akuttmottak per kommune, i persentiler, 2019 | Kommune (2019-koder for Troms og Finnmark) | `data/kjoretid_akuttmottak.csv` |
| SSB 14022 | Kostnader og inntekter etter HF (mill. kr, løpende priser). Faste priser finnes bare for landet totalt. | HF | `data/kostnader_hf.csv` |
| SSB 09556 | Ambulanser, beredskapstimer og oppdrag etter HF, 2011–2025 | HF | Ikke hentet |

**SKDEs helseatlas.** Atlaset ligger åpent som JSON i Payload-API-et til analyser.skde.no: `https://analyser.skde.no/api/analyser?limit=200&depth=0`. Det krever ingen innlogging. Det gamle repoet `github.com/Helseatlas/data` har CSV-filer for atlasene fra 2015–2019.

Fem analyser er merket `publiseringsStatus: test`: skulder, MR kne, PPP, epilepsi og den nye biopsianalysen. De bør ikke brukes før de er publisert.

**Hvor Helse Nord skiller seg ut** (publiserte analyser, 2025, rate i Helse Nord delt på landets rate):

| Analyse | Helse Nord mot landet | Helseforetakene |
|---|---|---|
| Hallux valgus-operasjon | 1,75 | Finnmark 2,42, Helgeland 0,82 |
| Spesifikk utviklingsforstyrrelse, barn og unge | 1,58 | |
| Fremfallskirurgi | 1,49 | |
| ADHD, barn og unge | 1,40 | |
| Mandeloperasjon, barn | 1,38 | Finnmark 1,98, Nordland 0,80 |
| Mandeloperasjon, voksne | 1,27 | |
| Depresjon, barn og unge | 1,26 | Finnmark 2,39 |
| Akuttinnleggelser for hjertesvikt | 0,84 | |
| Akuttinnleggelser, 75 år og eldre | 0,99 | |

Akuttinnleggelser for eldre ligger altså på landsnivå.

**Forbehold:**
- **Tallene fra SSB og FHI er ikke identiske.** SSB 14824 og NPR 517 avviker med om lag 1 %. Region Nord hadde 88 488 døgnopphold i 2025 hos SSB og 89 741 hos NPR. Avviket skyldes trolig ulik uttaksdato. Bruk én kilde konsekvent.
- **Brudd i SSB 13942 i 2025.** Utskrivningene øker med 11 % nasjonalt (767 072 til 855 222), mens døgnoppholdene i NPR er nesten uendret. Det tyder på et brudd i definisjonen eller rapporteringen. Bruk ikke utskrivningene for 2025 før dette er avklart.
- **Behandlingssted og bosted.** 13942 måler etter behandlende HF, 14824 og NPR etter bosted.
- **Fylkesserien i 14824 brytes i 2020 og 2024.** Bruk helseregion H05 for en sammenhengende serie.
- **SSB 12764 er fra 2019.** Tallene er eldre enn nedleggelsen av akuttmottaket i Mosjøen og det nye sykehuset i Narvik. De bør bare brukes med dette forbeholdet, eller beregnes på nytt.

## 5. Ventetid og fristbrudd

**Fil:** `data/ventetid.csv` med 16 831 rader. Kildenotat i `data/ventetid_kilde.md`, skript i `skript/ventetid.py`.

**Kilde.** FHI, Norsk pasientregister. Statistikken er flyttet fra Helsedirektoratet. Filene er Excel og lastes ned fra [FHIs nedlastingsside](https://www.fhi.no/he/npr/statistikk-npr/nedlasting-av-data/). De har ingen tabell-ID, og de finnes ikke i FHIs Open API eller hos SSB.

| Indikator | Periode | Nivå |
|---|---|---|
| Ventetid og antall henvisninger | Tertial 2019–2. tertial 2026 og år 2012–2025 | Land, RHF og HF |
| Fristbrudd | Samme perioder | **Bare land og RHF** |
| Tid til tjenestestart | Fra 2012 | Land, RHF og HF |
| Passert planlagt tid | 2017–august 2026 | Land, RHF og HF |

**Observasjon (2. tertial 2026).** Gjennomsnittlig ventetid for påbegynte forløp var 65,8 dager i Helse Nord og 61,5 i landet.

| HF | Ventetid, dager |
|---|---|
| UNN | 69,2 |
| Helgelandssykehuset | 71,2 |
| Nordlandssykehuset | 62,4 |
| Finnmarkssykehuset | 53,0 |

Andelen fristbrudd var 8,0 % i Helse Nord og 6,3 % i landet.

**Forbehold:**
- «Helse Nord RHF» omfatter også private institusjoner i regionen.
- Fristbruddene i 2020 er ikke fristbrudd i juridisk forstand. En midlertidig forskrift satte fristene til side det året.
- Tid til tjenestestart for UNN avviker fra Helse Nords eget tall i et svar til Stortinget i februar 2026: 102,5 mot 141 dager. Avviket er ikke avklart.

## 6. Ikke funnet

- **Kommunelisten per lokalsykehusområde** i en offisiell tekstkilde. Den er derfor utledet, se kilde 1.
- **Innleie og vikarbruk per HF** i åpne tabeller, og nyere tall enn 2023.
- **Fristbrudd per HF.**
- **Aktivitet etter bostedskommune** i somatikken, verken hos SSB eller i FHIs Open API. SKDE har bare HF-områder.
- **Reisetid til akuttsykehus etter 2019.**

## 7. Anbefaling til temasiden

**01. Bruk `opptak.json` som felles nøkkel.** Begrunnelse: fordelingen gir SSBs befolkning per lokalsykehus nøyaktig 2024–2026. Merk Tjeldsund og Lurøy som delt i kartet.

**02. Bygg akt 1 (premissene) på SSB 13982 og 14746 per HF og lokalsykehus.** Begrunnelse: 13982 er SSBs egen befolkning per opptaksområde og passer direkte som nevner.

**03. Bygg akt 2 (hendene) på SSB 13953 per HF og yrke 2015–2025, med innleiefiguren fra SSB-artikkelen som egen boks.** Begrunnelse: 13953 er den eneste åpne serien per HF. Innleie finnes bare per region og må merkes med år og kilde.

**04. Bygg akt 3 (tilgangen) på sykehus.json, SKDEs helseatlas og ventetidsfilene.** Bruk:
- `sykehus.json` på kart
- SKDEs helseatlas, publiserte analyser, med hallux valgus, mandler, ADHD og depresjon hos barn som eksempler på variasjon
- FHIs ventetidsfiler per HF

SSB 12764 kan brukes som et historisk bilde av kjøretiden (2019), med forbehold. Begrunnelse: dette er de eneste åpne kildene per HF eller kommune.

**05. Bruk NPR tabell 517 (eller SSB 14824 for helseregion Nord) til aktivitetsutviklingen, ikke SSB 13942.** Begrunnelse: 13942 har et brudd i 2025 og måler etter behandlingssted.

**06. Avklar akuttkirurgi i Narvik, Lofoten og Vesterålen mot helseforetakene før publisering.** Begrunnelse: åpne kilder belegger funksjonen bare indirekte.

Grunnlag:
- SSB 13982, 07459, 04317, 13953, 13942, 14824, 14022 og 12764 (PxWebApi v2)
- FHI/NPR tabell 517 og ventetidsfilene
- SKDE analyser.skde.no
- SSB-artikkelen av 15.11.2024
- unn.no, helgelandssykehuset.no og helse-nord.no

Alt er hentet 29. oktober 2026.
