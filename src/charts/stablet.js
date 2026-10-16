// Stablet areal (andeler til 100 %), med «i dag»-skille og etiketter for siste år.
// Spesifikasjon: { x:[…], serier:[{navn, data:[…], farge}], iDag }
import { Plot, register, spec } from './core.js';
import { tall } from '../lib/format.js';

register('stablet', (el, width) => {
  const s = spec(el);
  const rows = [];
  s.serier.forEach((se, si) => se.data.forEach((v, i) => rows.push({ x: s.x[i], v: v || 0, serie: se.navn, si })));
  const n = s.x.length;
  const etiketter = [];
  let cum = 0;
  s.serier.forEach(se => {
    const v = se.data[n - 1] || 0, v0 = se.data[0] || 0;
    if (v >= 4) etiketter.push({ x: s.x[n - 1], y: cum + v / 2, t: `${se.navn} ${tall(v0, 0)}→${tall(v, 0)} %` });
    cum += v;
  });
  const fig = Plot.plot({
    width, height: 280, marginLeft: 44, marginRight: Math.min(220, 30 + Math.max(...etiketter.map(e => e.t.length)) * 6.2), marginTop: 18, marginBottom: 24,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11px', color: 'var(--ink-3)', overflow: 'visible' },
    x: { tickFormat: String, ticks: 6, tickSize: 0, label: null },
    y: { domain: [0, 100], tickFormat: v => `${v} %`, ticks: 4, tickSize: 0, label: null },
    color: { domain: s.serier.map(se => se.navn), range: s.serier.map(se => se.farge) },
    marks: [
      Plot.areaY(rows, { x: 'x', y: 'v', fill: 'serie', z: 'serie', order: s.serier.map(se => se.navn), stroke: 'var(--bg)', strokeWidth: 0.6, fillOpacity: 0.9 }),
      s.iDag && Plot.ruleX([s.iDag], { stroke: 'var(--ink)', strokeDasharray: '3,3' }),
      s.iDag && Plot.text([s.iDag], { x: d => d, frameAnchor: 'top', dy: -12, text: () => 'I dag', fill: 'var(--ink-2)', fontSize: 10.5 }),
      Plot.text(etiketter, { x: 'x', y: 'y', text: 't', dx: 8, textAnchor: 'start', fill: 'var(--ink-2)', fontSize: 10.5, fontWeight: 600 }),
      Plot.tip(rows, Plot.pointer(Plot.stackY({ x: 'x', y: 'v', z: 'serie', order: s.serier.map(se => se.navn), title: d => `${d.x} · ${d.serie}\n${tall(d.v, 1)} %`, fill: 'var(--raised)', stroke: 'var(--line)' }))),
    ].filter(Boolean),
  });
  return fig;
});
