# Nord-Norge — KOSTRA, ROBEK & demografi

Interaktivt, frittstående dashbord for de 80 kommunene i Nord-Norge (Nordland, Troms, Finnmark) etter kommune- og regionreformen 2024.

**Innhold:** demografisk framskriving (kohort-komponentmodell, SSB-basert, 2026-årgangen/tabell 14746), kommuneøkonomi (KOSTRA), ROBEK-status med kalibrert risikoproxy på de økonomiske fundamentene, og boligmodul (temaserie 07): byggetakt (SSB 05889/10784, kommuneserier skjøtet via KLASS) mot beregnet boligbehov per kommune fram til 2050 (BB-KVOTE-modellen, kalibrert mot Prognosesenteret), pluss bruktmarkedet (kvadratmeterpriser 14545/14310, omsetninger 06726, nybyggpris 13500) og leiemarkedet (eierstatus 11084, kommunale boliger 12008). Ferskeste folketall per 1. juli 2026 (01222) vises der folketall presenteres; modellene er forankret i 1.1.2026.

## Teknisk oppbygning

- 13 HTML-sider (forside, landsdel, fylke, kommune, sammenligning, metode og sju temasider) bygges med **Vite** (`npm run build` → `dist/`). Vercel bygger automatisk ved push til `main` (se `vercel.json`).
- **Profil:** McHalvard, mørk visning som standard (`data-tema`), tokens i `src/styles/tokens.css`.
- **Diagrammotor:** `src/charts/` med Observable Plot og D3. Eldre kode i `assets/app.js` setter inn plassholdere (`NN.placeholder(navn, spesifikasjon)`) som tegnes, tilpasses bredden og følger temaet automatisk.
  Typer: `proj` (befolkningsbaner), `kart` (kommunekart med rangering), `plassering` (bisverm «hvor står kommunen»), `skjebner` (små multipler), `trykkmatrise` (regioner, animert), `gap` (differansediagram), `linjer`, `stolper`, `spredning`.
- **Søk:** Ctrl K eller «/» på alle sider (`src/lib/search.js`). Rullestyrt fortelling på forsiden (`src/lib/scrolly.js`).
- **Data:** `assets/data.js` (innbakte datablokker) oppdateres av `fetch_*.py` mot SSB PxWebApi; `fetch_kostra.py` og `update_robek.py` for KOSTRA og ROBEK. Kart: `geo/nn-kommuner.json` (Kartverket 2024, CC BY 4.0).

## Lokalt

```
npm install
npm run dev      # http://localhost:8123
npm run build    # produksjonsbygg i dist/
```

> Risikoproxyen er et gjennomsiktig tidligvarsel på KOSTRA-tall, **ikke** de juridiske ROBEK-vilkårene (kommuneloven §28-1). Registerstatus er et øyeblikksbilde.
