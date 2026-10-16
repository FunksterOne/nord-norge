// Liggende stolper, eventuelt i grupper med egen tittel.
// Spesifikasjon: { grupper:[{tittel, rader:[{l, v, farge, uthev, note}] , ref:{v, tekst}}],
//                  format:'tall'|'pst'|'pst2', maks, farge, etikettBredde }
import { Plot, register, spec } from './core.js';
import { heltall, tall } from '../lib/format.js';

const FARGE = f => (!f ? 'var(--muted-mark)' : f.startsWith('var(') || f.startsWith('color-mix') ? f : ({ accent: 'var(--accent)', ink: 'var(--ink)', neg: 'var(--neg)', pos: 'var(--pos)', warn: 'var(--warn)', muted: 'var(--muted-mark)' })[f] || `var(--${f})`);
const FMT = { tall1: v => tall(v, 1), tall: v => heltall(v), kr: v => `${heltall(v)} kr`, pst: v => `${tall(v, 1)} %`, pst2: v => `${tall(v, 2)} %` };

register('hstolper', (el, width) => {
  const s = spec(el);
  const fmt = FMT[s.format || 'tall'];
  const alle = s.grupper.flatMap(g => g.rader).filter(r => r.v != null);
  const maks = s.maks || Math.max(1, ...alle.map(r => r.v), ...s.grupper.flatMap(g => [g.ref, ...(g.refs || [])].filter(Boolean).map(r => r.v)));
  const longest = Math.max(4, ...s.grupper.flatMap(g => g.rader.map(r => String(r.l).length)));
  const left = s.etikettBredde || Math.min(Math.round(width * 0.42), 14 + longest * 6.6);
  const out = [];
  for (const g of s.grupper) {
    const n = g.rader.length;
    const rh = n > 40 ? 15 : n > 20 ? 20 : 27;
    const rader = g.rader.map((r, i) => ({ ...r, key: `${i}\u0000${r.l}` }));
    const vals = rader.filter(r => r.v != null);
    const tom = rader.filter(r => r.v == null);
    if (g.tittel) {
      const t = document.createElement('div'); t.className = 'nn-hst-tittel'; t.textContent = g.tittel; out.push(t);
    }
    const fig = Plot.plot({
      width, height: n * rh + ((g.ref || g.refs) ? 30 : 12), marginLeft: left, marginRight: 96, marginTop: (g.ref || g.refs) ? 22 : 4, marginBottom: 6,
      style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: n > 40 ? '10px' : '12px', color: 'var(--ink-2)', overflow: 'visible' },
      x: { domain: [0, maks], axis: null },
      y: { domain: rader.map(r => r.key), tickFormat: k => k.split('\u0000')[1], tickSize: 0, padding: n > 40 ? 0.12 : 0.22, label: null },
      marks: [
        Plot.barX(rader, { x: maks, y: 'key', fill: 'var(--line-soft)' }),
        Plot.barX(vals, { x: 'v', y: 'key', fill: r => FARGE(r.farge || (r.uthev ? 'accent' : s.farge)) }),
        ...[g.ref, ...(g.refs || [])].filter(Boolean).flatMap((r, ri) => [
          Plot.ruleX([r.v], { stroke: r.farge || 'var(--ink-3)', strokeDasharray: '3,3' }),
          Plot.text([r.v], { x: d => d, frameAnchor: 'top', dy: ri % 2 ? -2 : -12, text: () => r.tekst, fill: r.farge || 'var(--ink-3)', fontSize: 11 }),
        ]),
        Plot.text(vals, { x: 'v', y: 'key', text: r => fmt(r.v) + (r.note ? `  ${r.note}` : ''), dx: 6, textAnchor: 'start', fill: r => (r.uthev ? 'var(--ink)' : 'var(--ink-2)'), fontWeight: r => (r.uthev ? 600 : 400), fontSize: n > 40 ? 10 : 11.5 }),
        tom.length && Plot.text(tom, { x: 0, y: 'key', text: () => 'undertrykt', dx: 6, textAnchor: 'start', fill: 'var(--ink-3)', fontSize: 11 }),
        Plot.tip(vals, Plot.pointerY({ x: 'v', y: 'key', title: r => `${r.l}\n${fmt(r.v)}${r.note ? `\n${r.note}` : ''}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
      ].filter(Boolean),
    });
    out.push(fig);
  }
  if (s.kilde) { const k = document.createElement('div'); k.className = 'nn-source'; k.textContent = s.kilde; out.push(k); }
  return out;
});
