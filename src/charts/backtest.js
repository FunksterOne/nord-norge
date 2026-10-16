// Backtest 2020 → 2024: gjennomsnittlig prosentfeil per sentralitetsklasse og modell.
// Spesifikasjon: { grupper:[{lab, sub, v:[ssb, mvp, attr], uthev}], serier:[[navn, farge], …] }
import { Plot, register, spec } from './core.js';
import { tall } from '../lib/format.js';

register('backtest', (el, width) => {
  const s = spec(el);
  const rows = [];
  s.grupper.forEach((g, gi) => {
    const vals = g.v.filter(v => v != null);
    const min = vals.length ? Math.min(...vals) : null;
    g.v.forEach((v, si) => rows.push({
      g: `${gi}\u0000${g.lab}`, lab: g.lab, sub: g.sub, serie: s.serier[si][0], farge: s.serier[si][1], si, v,
      vinner: v != null && min != null && v - min <= 0.05, uthev: g.uthev,
    }));
  });
  const vis = rows.filter(r => r.v != null);
  const maks = Math.max(...vis.map(r => r.v)) * 1.15;
  const compact = width < 600;
  const fig = Plot.plot({
    width, height: s.grupper.length * (compact ? 58 : 52) + 36,
    marginLeft: compact ? 120 : 180, marginRight: 70, marginTop: 6, marginBottom: 30,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11.5px', color: 'var(--ink-2)', overflow: 'visible' },
    fy: { domain: s.grupper.map((g, gi) => `${gi}\u0000${g.lab}`), tickFormat: k => k.split('\u0000')[1], label: null, tickSize: 0, padding: 0.18 },
    y: { domain: s.serier.map(x => x[0]), axis: null, padding: 0.12 },
    x: { domain: [0, maks], tickFormat: v => `${tall(v, 1)} %`, ticks: 5, tickSize: 0, label: 'Gjennomsnittlig prosentfeil — lavere er bedre →', labelAnchor: 'right' },
    marks: [
      Plot.barX(vis, { fy: 'g', y: 'serie', x: 'v', fill: r => r.farge, fillOpacity: r => (r.vinner ? 1 : 0.38) }),
      Plot.text(vis, { fy: 'g', y: 'serie', x: 'v', text: r => tall(r.v, 2) + (r.vinner ? ' ●' : ''), dx: 5, textAnchor: 'start', fill: r => (r.vinner ? 'var(--ink)' : 'var(--ink-3)'), fontWeight: r => (r.vinner ? 600 : 400), fontSize: 11 }),
      Plot.tip(vis, Plot.pointer({ fy: 'g', y: 'serie', x: 'v', title: r => `${r.lab} (${r.sub})\n${r.serie}: ${tall(r.v, 2)} % feil${r.vinner ? '\nLavest i raden' : ''}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  const leg = document.createElement('div'); leg.className = 'nn-legend';
  leg.innerHTML = s.serier.map(z => `<span><i style="background:${z[1]}"></i>${z[0]}</span>`).join('') + '<span class="nn-legend-note">● = lavest feil i raden (toleranse 0,05 prosentenheter). Bleke stolper = ikke best.</span>';
  return [fig, leg];
});
