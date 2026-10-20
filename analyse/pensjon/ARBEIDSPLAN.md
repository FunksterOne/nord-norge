# Arbeidsplan: kommuneøkonomi og pensjonsforpliktelser

Videre arbeid etter at pensjonsanalysen ble lagt inn i dashbordet (commits 9f6df7e–a8292a8, 17. oktober 2026).
Skal gjennomføres senere, etter klarsignal. Rekkefølgen er anbefalt prioritet.

| Nr | Oppgave | Hvorfor | Omfang | Status |
|---|---|---|---|---|
| 01 | Avslutt oppgaven om gjeldsnormen | Endringene i `assets/app.js` og `kommune.html` (normene 1,75/5/85 fra `EXT_NORMS`, brudd over 85 % i stedet for 75 %) ligger ucommittet i arbeidsmappen | Lite | Ferdig 20.10.2026 (f4bc3fd) |
| 02 | Kalibrer 2026–2027 mot kommunebudsjettene | Modellen gir svak økning i 2026, mens TBU venter fall i 2026 og økning i 2027 | Middels | Venter |
| 03 | Stikkprøv notene som er lest av bilder | Om lag 20 pensjonsnoter er skannet og lest manuelt | Lite | Venter |
| 04 | Vis innbetalingene for alle 74 kommuner med note | Tabellen finnes bare for Bodø, Tromsø og Harstad | Lite | Venter |
| 05 | Tett hullene i grunnlaget | Seks kommuner har bare KOSTRA-tall | Lite til middels | Venter |
| 06 | Legg pensjon inn på sammenligningssiden | Kommuner kan ikke sammenlignes direkte på premieavvik og fremtidig kostnad | Lite | Venter |
| 07 | Planlegg den årlige oppdateringen | KOSTRA 2026 (foreløpig mars 2027) og KDDs rundskriv for 2028 | Lite | Venter |

## 01 Avslutt oppgaven om gjeldsnormen

- Kontroller at endringene er ferdige: brudd telles over 85 %, og teksten og normene leses fra `EXT_NORMS`.
- Sjekk den stagede versjonen før commit (se rutinen for delvis staging), og kontroller produksjonen etter push.

## 02 Kalibrer 2026–2027 mot kommunebudsjettene

- Hent pensjonskostnad og premie for 2026 og 2027 fra budsjett 2026 og økonomiplan 2026–2029. Tallene bygger på KLPs prognoser.
- Start med de største kommunene: Bodø, Tromsø, Narvik, Rana, Harstad, Alta, Hammerfest og Vefsn.
- Bruk prognosene til å sette nivået i 2026–2027 i `analyse/pensjon/fase4_modell.py`. Oppdater `RAPPORT.md`, metodekortet og forbeholdet om 2026–2027 på temasiden.
- Hent bare åpne kilder. Dokumenter bak botsjekk (Acos Innsyn Pluss) skal ikke omgås.

## 03 Stikkprøv notene som er lest av bilder

Velg fem til ti av notene som er lest av sidebilder. Kontroller premie, kostnad, premieavvik og forpliktelse mot originalene:

- Bindal, Brønnøy, Nesna, Hemnes, Rødøy og Vevelstad
- Beiarn, Bø, Evenes og Sortland
- Kvæfjord, Gratangen, Karlsøy og Ibestad
- Salangen, Sørreisa og Storfjord
- Vadsø og Nordkapp

Rett postene i `regnskap_gruppe*.json` eller `manuelle/`, og kjør `python fetch_pensjon.py`.

## 04 Vis innbetalingene for alle kommuner

- Utvid `innbet` i `fetch_pensjon.py` fra de tre byene til alle kommuner med pensjonsnote. Felter: innbetalt premie, beregnet kostnad, årets premieavvik og bruk av premiefond når det er oppgitt.
- Kassetallene (premiesats, reguleringspremie og innskudd) gjelder bare Bodø, Tromsø og Harstad.
- Vis tabellen i pensjonsblokken på kommunesiden. Kommuner som brukte mye premiefond, som Narvik (233,9 mill. kr) og Rana (200,5 mill. kr), blir da synlige.

## 05 Tett hullene i grunnlaget

- **Målselv, Lyngen, Kåfjord, Balsfjord og Andøy:** Halvard laster ned årsregnskapet for 2025 i egen nettleser og sender PDF-en. Regnskapet ligger bak en botsjekk i kommunens innsynsløsning.
- **Berlevåg:** Regnskapet for 2025 er ikke publisert. Lag et utkast til innsynsbegjæring som Halvard sender selv.
- **Hamarøy og Lurøy:** Notene går ikke opp. Vurder å hente regnskapet på nytt eller spørre kommunen.

## 06 Legg pensjon inn på sammenligningssiden

Legg til rader i `sammenlign.html`:

- premieavvik i % av BDI
- disposisjonsfond i % av BDI
- pensjonskostnad i % av BDI for 2030 og 2050 (basis, med spenn)
- leverandør og amortiseringstid

## 07 Planlegg den årlige oppdateringen

- **Mars 2027:** foreløpige KOSTRA-tall for 2026. Kjør `hent_kostra_pensjon.py`, `hent_kostra_bdi.py` og `hent_kostra_drift.py`.
- **Våren 2027:** pensjonsnotene i årsregnskapene for 2026 (april–juni).
- **Juni 2027:** KDDs rundskriv med forholdstallet for 2028, endelige KOSTRA-tall for 2026, og reguleringspremien for 2027 fra KLP.
- **Oktober 2027:** nasjonale tall i statsbudsjettet (Prop. 1 S) for pensjonsbidraget til deflatoren.
- Halvard har bedt om at det ikke settes opp påminnelser. Planen ligger her til den tas opp igjen.
