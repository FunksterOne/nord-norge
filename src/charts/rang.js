// Rangering av kommuner som loddrette stolper (lavest til venstre), med referanselinjer.
// Spesifikasjon: { rader:[{nr, navn, fylke, v, note}], ref:[{y, tekst}], format:'kr'|'pst', uthev:nr }
import { Plot, register, spec } from './core.js';
import { heltall, tall, kortNavn } from '../lib/format.js';

register('rang', (el, width) => {
  const s = spec(el);
  const fmt = s.format === 'pst' ? (v => `${tall(v, 1)} %`) : (v => `${heltall(v)} kr`);
  const akse = s.format === 'pst' ? (v => `${tall(v, 0)} %`) : (v => heltall(v));
  const rader = [...s.rader].sort((a, b) => a.v - b.v).map((r, i) => ({ ...r, i, kort: kortNavn(r.navn) }));
  const n = rader.length;
  const merk = [...rader.slice(0, 3), ...rader.slice(-3)];
  const vals = rader.map(r => r.v).concat((s.ref || []).map(r => r.y));
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const pad = (hi - lo) * 0.12;
  const fig = Plot.plot({
    width, height: 300, marginLeft: 64, marginRight: 110, marginTop: 24, marginBottom: 24,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11px', color: 'var(--ink-3)', overflow: 'visible' },
    x: { domain: rader.map(r => r.i), axis: null, padding: 0.15 },
    y: { domain: [lo - pad, hi + pad], nice: true, tickFormat: akse, ticks: 5, tickSize: 0, label: null },
    marks: [
      Plot.barY(rader, { x: 'i', y1: lo - pad, y2: 'v', fill: r => (r.nr === s.uthev ? 'var(--accent)' : 'var(--muted-mark)') }),
      ...(s.ref || []).flatMap(r => [
        Plot.ruleY([r.y], { stroke: r.farge || 'var(--ink-2)', strokeDasharray: '4,3' }),
        Plot.text([r.y], { y: d => d, frameAnchor: 'right', dx: 104, text: () => r.tekst, fill: r.farge || 'var(--ink-2)', fontSize: 11, textAnchor: 'end' }),
      ]),
      Plot.text(merk, { x: 'i', y: 'v', text: 'kort', dy: -8, fill: 'var(--ink-2)', fontSize: 10, rotate: n > 40 ? -40 : 0, textAnchor: n > 40 ? 'start' : 'middle' }),
      Plot.text(['← Lavest'], { x: () => rader[0].i, frameAnchor: 'bottom', dy: 16, text: d => d, textAnchor: 'start', fill: 'var(--ink-3)' }),
      Plot.text(['Høyest →'], { x: () => rader[n - 1].i, frameAnchor: 'bottom', dy: 16, text: d => d, textAnchor: 'end', fill: 'var(--ink-3)' }),
      Plot.tip(rader, Plot.pointerX({ x: 'i', y: 'v', title: r => `${r.kort} (${r.fylke})\n${fmt(r.v)}${r.note ? `\n${r.note}` : ''}\nKlikk for kommunesiden`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  fig.style.cursor = 'pointer';
  fig.addEventListener('click', () => { const v = fig.value; if (v && v.nr) location.href = `kommune.html?k=${v.nr}`; });
  return fig;
});
