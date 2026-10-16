// Differansediagram: behov mot tilbud av arbeidskraft, med gapet skyggelagt.
// Spesifikasjon: { years:[], behov:[], tilbud:[], marker:[2030,…] }
import { Plot, base, register, spec } from './core.js';
import { heltall, endring } from '../lib/format.js';

register('gap', (el, width) => {
  const s = spec(el);
  const rows = s.years.map((y, i) => ({ year: y, behov: s.behov[i], tilbud: s.tilbud[i], gap: s.behov[i] - s.tilbud[i] }));
  const marks = (s.marker || []).map(y => rows.find(r => r.year === y)).filter(Boolean);
  const last = rows[rows.length - 1];
  const fig = Plot.plot(base({
    width, height: 330, marginRight: 110, marginTop: 30,
    x: { ticks: [2026, 2030, 2035, 2040, 2045, 2050], tickFormat: String },
    y: { nice: true, zero: false },
    marks: [
      Plot.differenceY(rows, { x: 'year', y1: 'tilbud', y2: 'behov', positiveFill: 'var(--neg)', negativeFill: 'var(--pos)', fillOpacity: 0.22, stroke: null }),
      Plot.lineY(rows, { x: 'year', y: 'tilbud', stroke: 'var(--ink-2)', strokeWidth: 2 }),
      Plot.lineY(rows, { x: 'year', y: 'behov', stroke: 'var(--accent)', strokeWidth: 2.6 }),
      Plot.ruleX(marks, { x: 'year', y1: 'tilbud', y2: 'behov', stroke: 'var(--neg)', strokeWidth: 1.2 }),
      Plot.text(marks, { x: 'year', y: 'behov', text: d => endring(Math.round(d.gap), 0), dy: -12, fill: 'var(--neg)', fontWeight: 600, fontSize: 12.5 }),
      Plot.text([last], { x: 'year', y: 'behov', text: d => `Behov ${heltall(d.behov)}`, dx: 8, textAnchor: 'start', fill: 'var(--accent-text)', fontWeight: 600 }),
      Plot.text([last], { x: 'year', y: 'tilbud', text: d => `Tilbud ${heltall(d.tilbud)}`, dx: 8, textAnchor: 'start', fill: 'var(--ink-2)', fontWeight: 600 }),
      Plot.ruleX(rows, Plot.pointerX({ x: 'year', stroke: 'var(--ink-3)', strokeOpacity: 0.6 })),
      Plot.tip(rows, Plot.pointerX({ x: 'year', y: 'behov', title: d => `${d.year}\nBehov: ${heltall(d.behov)}\nTilbud: ${heltall(d.tilbud)}\nGap: ${endring(Math.round(d.gap), 0)} årsverk`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  }));
  const leg = document.createElement('div');
  leg.className = 'nn-legend';
  leg.innerHTML = '<span><i style="background:var(--accent)"></i>Behov (stillinger som må fylles)</span><span><i style="background:var(--ink-2)"></i>Tilbud (arbeidsføre med dagens sysselsettingsrate)</span><span><i style="background:color-mix(in srgb, var(--neg) 35%, transparent)"></i>Gap</span>';
  return [fig, leg];
});
