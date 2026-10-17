# Uttrekk av pensjonsnoter fra kommunenes årsregnskap

Én JSON-fil per gruppe: `regnskap_gruppeN.json`, en liste med ett objekt per kommune.
Beløp i hele kroner (ikke tusen). Bruk `null` når tallet ikke finnes. Ikke gjett.

```json
{
  "nr": "1804",
  "navn": "Bodø",
  "regnskapsaar": 2025,                       // 2025 hvis publisert, ellers 2024
  "kilde_url": "https://…/arsregnskap-2025.pdf",
  "kilde_side": "note 7, s. 42",
  "konsern_eller_kasse": "kommunekasse",      // hva notetallene gjelder
  "leverandorer": [                           // én rad per ordning
    {"ordning": "Fellesordningen", "leverandor": "KLP", "gruppe": "fellesordning"},
    {"ordning": "Sykepleiere", "leverandor": "KLP", "gruppe": "sykepleiere"},
    {"ordning": "Lærere", "leverandor": "SPK", "gruppe": "laerere"}
    // egen kommunal pensjonskasse: "leverandor": "Bodø kommunale pensjonskasse"
  ],
  "brutto_pensjonsforpliktelse": null,        // 31.12, ekskl. arbeidsgiveravgift
  "pensjonsmidler": null,                     // 31.12
  "netto_forpliktelse": null,                 // brutto − midler
  "netto_inkl_aga": null,                     // hvis oppgitt
  "aarets_pensjonskostnad": null,             // netto pensjonskostnad (regnskapsmessig)
  "innbetalt_premie": null,                   // inkl. administrasjon, ekskl. AGA hvis mulig
  "aarets_premieavvik": null,                 // positivt = premie > kostnad
  "akkumulert_premieavvik": null,             // balansen 31.12, ekskl. AGA
  "akkumulert_premieavvik_inkl_aga": null,
  "amortisering_aar": null,                   // 1, 7, 10 eller 15 (oftest 7)
  "reguleringspremie": null,                  // hvis oppgitt
  "egenkapitaltilskudd_klp": null,            // årets innbetaling, hvis oppgitt
  "premiefond_bruk": null,                    // bruk av premiefond i året, hvis oppgitt
  "forutsetninger": {
    "diskonteringsrente": null, "avkastning": null, "lonnsvekst": null, "g_regulering": null, "pensjonsregulering": null
  },
  "sykepleiere_separat": null,                // true/false: er sykepleierordningen oppgitt separat?
  "merknader": "fritekst: avvik, uklarheter, om tallene er per ordning og summert av deg"
}
```

Når noten oppgir tallene per ordning (fellesordning, sykepleiere, SPK), summer dem selv og forklar det i `merknader`.
SPK-ordningen for lærere har ofte bare premie, ikke forpliktelse; noter det.
