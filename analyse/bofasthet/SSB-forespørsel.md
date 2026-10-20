# Forespørsel til SSB: tallgrunnlaget i monitoren for sekundærflytting

Utkast som Halvard sender selv. SSB opplyser i artikkelen «Høy bofasthet blant flyktninger de første årene» (28. november 2024) at tallgrunnlaget kan fås ved henvendelse til forfatterne. Adressene står på artikkelsiden og på ssb.no under de ansatte.

**Til:** Mads Ivar Kirkeberg og Frøydis Strøm, Statistisk sentralbyrå

**Emne:** Forespørsel om tallgrunnlag – bofasthet blant bosatte flyktninger per fylke og kull

> Hei,
>
> Jeg arbeider med et åpent analyseverktøy for de 80 kommunene i Nordland, Troms og Finnmark (nord-norge.vercel.app) og bruker monitoren for sekundærflytting til å vise hvor mange flyktninger som blir boende i bosettingskommunen.
>
> I artikkelen fra 28. november 2024 skriver dere at tallgrunnlaget kan fås ved henvendelse. Jeg vil gjerne be om følgende, om mulig som regneark:
>
> 1. Andelen som bor i første bosettingskommune, i annen kommune i samme fylke, i annet fylke og som har utvandret, etter botid 1–14 år, for hvert bosettingskull 2010–2023.
> 2. Fordelt på bosettingsfylke (Nordland, Troms og Finnmark, og gjerne alle fylker), med 2024-inndelingen.
> 3. Antall bosatte i hvert kull og fylke (nevneren), slik at små celler kan vurderes.
> 4. Hvis det er mulig: samme tall for kommunene i Nord-Norge med minst 50 bosatte i kullet, eller gruppert etter sentralitet.
>
> Tallene vil bli publisert med SSB som kilde og med de forbeholdene dere oppgir. Jeg tar gjerne imot tall der små celler er skjult eller avrundet.
>
> Med vennlig hilsen
> Halvard Nordang

## Hva tallene skal brukes til

- Erstatte netto bevaring (SSB 10598) med direkte fylkestall for 10 og 14 år etter bosetting på temasiden «Hvem blir værende?» og i bofasthetskortet på fylkessidene.
- Fylle hullene i femårsserien (kull 2013, 2014 og 2016–2018).
- Kontrollere Fafos tiårstall for Nord-Norge (nær 70 % flyttet).

Når tallene kommer: legg dem i `analyse/bofasthet/kilder/` (ikke versjonert), oppdater tabellene i `fetch_bofasthet.py` og kjør `python fetch_bofasthet.py`.
