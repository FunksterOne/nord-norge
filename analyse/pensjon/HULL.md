# Hull i grunnlaget: hva som trengs, og utkast

Seks kommuner har ikke pensjonsnote fra årsregnskapet for 2025 i analysen, og to har noter som ikke går opp.
Dashbordet viser dem med merking («Bare KOSTRA-tall» eller forbehold).

## 1. Fem regnskap bak botsjekk

Regnskapene finnes, men møtedokumentene ligger i Acos Innsyn Pluss bak en botsjekk som ikke skal omgås maskinelt.
Halvard kan laste dem ned i egen nettleser: åpne møteoversikten, finn kommunestyremøtet i mai eller juni 2026 med saken
«Årsregnskap 2025» (eller kontrollutvalgets møte i april–mai 2026), last ned PDF-en og send den i samtalen.

| Kommune | Nr | Møteoversikt |
|---|---|---|
| Målselv | 5524 | https://innsynpluss.onacos.no/malselv/moteoversikt/ |
| Lyngen | 5536 | https://innsynpluss.onacos.no/lyngen/moteoversikt/ |
| Kåfjord | 5540 | lenken «Innsyn» på kafjord.kommune.no |
| Balsfjord | 5532 | lenken «Innsyn» på balsfjord.kommune.no |
| Andøy | 1871 | lenken «Innsyn» på andoy.kommune.no |

Når PDF-en er sendt: pensjonsnoten leses inn som `manuelle/<nr>.json` etter `SKJEMA.md`, og `python fetch_pensjon.py`
kjøres fra rotmappen.

## 2. Berlevåg: utkast til innsynsbegjæring

Berlevåg har ikke publisert årsregnskapet for 2025 på det nye nettstedet, og kommunen bruker ikke en åpen
innsynsløsning. Utkastet sendes av Halvard til kommunens postmottak (adressen står på berlevag.kommune.no).

> **Emne:** Innsynsbegjæring – årsregnskap 2025 med noter
>
> Hei,
>
> Med hjemmel i offentleglova § 3 ber jeg om innsyn i Berlevåg kommunes årsregnskap for 2025 med noter,
> slik det ble avlagt og behandlet av kommunestyret. Jeg er særlig interessert i noten om pensjonsforpliktelser
> (premie, pensjonskostnad, premieavvik, premiefond og beregningsforutsetninger).
>
> Dokumentet kan gjerne sendes som PDF til denne adressen.
>
> Med vennlig hilsen
> Halvard Nordang

## 3. Hamarøy og Lurøy: noter som ikke går opp

- **Hamarøy (1875):** Pensjonsmidlene i noten (687,5 mill. kr) avviker fra balansen og KOSTRA (776,9 mill. kr), og årets
  premieavvik (23,3 mill. kr) stemmer ikke med premie minus kostnad (17,8 mill. kr). Modellen bruker kostnaden fra noten.
- **Lurøy (1834):** Noten er en posteringsliste uten kostnad, premie og forutsetninger; kostnaden er anslått fra KOSTRA.

Utkast til avklaring som Halvard kan sende til økonomiavdelingen i kommunen:

> **Emne:** Spørsmål om pensjonsnoten i årsregnskapet for 2025
>
> Hei,
>
> Jeg arbeider med en analyse av pensjonsforpliktelsene i kommunene i Nord-Norge og bruker pensjonsnoten i deres
> årsregnskap for 2025. [Hamarøy: Pensjonsmidlene i noten ser ut til å avvike fra balansen, og årets premieavvik
> stemmer ikke med premie minus pensjonskostnad.] [Lurøy: Noten oppgir ikke pensjonskostnad, innbetalt premie eller
> beregningsforutsetninger.] Har dere en oppdatert eller fullstendig pensjonsnote, eventuelt aktuarberegningen fra
> KLP for 2025, som dere kan dele?
>
> Med vennlig hilsen
> Halvard Nordang
