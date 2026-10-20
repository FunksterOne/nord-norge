// Generelt linje-/områdediagram for temasidene.
// Spesifikasjon:
// { x:[…], serier:[{navn, data:[…], farge:'accent'|'ink'|'neg'|'pos'|'warn'|'cat-1..6'|'muted',
//                    stil:'linje'|'stiplet'|'område'|'stolpe', etikett:true}],
//   format:'tall'|'pst'|'indeks'|'endring'|'kr', null:false, iDag:2026, ref:[{y, tekst}],
//   hoyde:320, xTicks:[…], xFormat:'aar'|'tekst', yTittel:'…' }
import { Plot, base, register, spec } from './core.js';
import { heltall, tall, endring, prosent } from '../lib/format.js';

const FARGE = f => {
  if (!f) return 'var(--ink-2)';
  if (f.startsWith('var(') || f.startsWith('#')) return f;
  return ({ accent: 'var(--accent)', ink: 'var(--ink)', neg: 'var(--neg)', pos: 'var(--pos)', warn: 'var(--warn)', muted: 'var(--muted-mark)' })[f] || `var(--${f})`;
};
const TEKSTFARGE = f => (f === 'accent' ? 'var(--accent-text)' : FARGE(f));
const FMT = {
  pst1: v => prosent(v, 1), pst0: v => prosent(v, 0), kr1000: v => `${heltall(v)} kr`,
  tall: v => heltall(v), indeks: v => tall(v, 0), pst: v => prosent(v, 1),
  endring: v => endring(Math.round(v), 0), kr: v => `${heltall(v)} kr`,
};
const AKSE = {
  pst1: v => `${tall(v, 0)} %`, pst0: v => `${tall(v, 0)} %`, kr1000: v => heltall(v),
  tall: v => heltall(v), indeks: v => tall(v, 0), pst: v => `${tall(v, 0)} %`,
  endring: v => endring(v, 0), kr: v => heltall(v),
};

function dodge(items, gap = 14) {
  items.sort((a, b) => a.py - b.py);
  for (let i = 1; i < items.length; i++) if (items[i].py - items[i - 1].py < gap) items[i].py = items[i - 1].py + gap;
  return items;
}

register('linjer', (el, width) => {
  const s = spec(el);
  const fmt = FMT[s.format || 'tall'];
  const isYear = s.xFormat !== 'tekst';
  const rows = [];
  s.serier.forEach((se, si) => se.data.forEach((v, i) => { if (v != null && Number.isFinite(v)) rows.push({ x: s.x[i], v, serie: se.navn, si }); }));
  const bandRows = s.band ? s.band.x.map((x, i) => ({ x, lo: s.band.lo[i], hi: s.band.hi[i] })).filter(d => d.lo != null && d.hi != null) : [];
  const vals = rows.map(r => r.v).concat((s.ref || []).map(r => r.y), bandRows.flatMap(d => [d.lo, d.hi]));
  if (s.null) vals.push(0);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  const pad = (hi - lo) * 0.06 || 1; lo -= s.null && lo >= 0 ? 0 : pad; hi += pad;
  const height = s.hoyde || 320, mt = 26, mb = 30;
  const yScale = v => mt + (1 - (v - lo) / (hi - lo)) * (height - mt - mb);
  const yInv = py => lo + (1 - (py - mt) / (height - mt - mb)) * (hi - lo);

  const ends = [];
  s.serier.forEach((se, si) => {
    if (se.etikett === false) return;
    const pts = rows.filter(r => r.si === si);
    const last = pts[pts.length - 1]; if (!last) return;
    ends.push({ x: last.x, value: last.v, py: yScale(last.v), text: `${se.kort || se.navn} ${fmt(last.v)}`, farge: se.farge, uthev: se.uthev });
  });
  const placed = dodge(ends).map(e => ({ ...e, y: yInv(e.py) }));

  const marks = [];
  if (bandRows.length) marks.push(Plot.areaY(bandRows, { x: 'x', y1: 'lo', y2: 'hi', fill: FARGE(s.band.farge || 'accent'), fillOpacity: 0.16 }));
  if (s.null || (lo < 0 && hi > 0)) marks.push(Plot.ruleY([0], { stroke: 'var(--line)' }));
  if (s.iDag) {
    marks.push(Plot.ruleX([s.iDag], { stroke: 'var(--ink-3)', strokeDasharray: '2,3' }));
    marks.push(Plot.text([s.iDag], { x: d => d, frameAnchor: 'top', dy: -14, text: () => 'I dag', fill: 'var(--ink-3)', fontSize: 11 }));
  }
  (s.markor || []).forEach(m => {
    marks.push(Plot.ruleX([m.x], { stroke: 'var(--ink-3)', strokeDasharray: '2,3', strokeOpacity: 0.7 }));
    if (m.tekst) marks.push(Plot.text([m.x], { x: d => d, frameAnchor: 'top', dy: -14, text: () => m.tekst, fill: 'var(--ink-3)', fontSize: 11 }));
  });
  (s.ref || []).forEach(r => {
    marks.push(Plot.ruleY([r.y], { stroke: 'var(--warn)', strokeWidth: 1.1 }));
    if (r.tekst) marks.push(Plot.text([r.y], { y: d => d, frameAnchor: 'left', dx: 4, dy: -8, text: () => r.tekst, fill: 'var(--warn)', fontSize: 11, textAnchor: 'start' }));
  });
  s.serier.forEach((se, si) => {
    const d = rows.filter(r => r.si === si);
    const c = FARGE(se.farge);
    if (se.stil === 'område') {
      marks.push(Plot.areaY(d, { x: 'x', y: 'v', fill: c, fillOpacity: 0.28 }));
      marks.push(Plot.lineY(d, { x: 'x', y: 'v', stroke: c, strokeWidth: 1.6 }));
    } else if (se.stil === 'stolpe') {
      marks.push(Plot.rectY(d, { x: 'x', y: 'v', fill: c, interval: isYear ? 1 : undefined, inset: 1 }));
    } else {
      marks.push(Plot.lineY(d, { x: 'x', y: 'v', stroke: c, strokeWidth: se.uthev ? 2.6 : se.svak ? 1.2 : 1.8, strokeOpacity: se.svak ? 0.45 : 1, strokeDasharray: se.stil === 'stiplet' ? '5,3' : null }));
    }
  });
  marks.push(Plot.text(placed, { x: 'x', y: 'y', text: 'text', fill: d => TEKSTFARGE(d.farge), dx: 8, textAnchor: 'start', fontWeight: d => (d.uthev ? 600 : 500), fontSize: 11.5 }));
  // Verktøytips: alle serier ved valgt x
  const byX = new Map();
  rows.forEach(r => { const o = byX.get(r.x) || { x: r.x, y: r.v, lines: [] }; o.lines.push(`${s.serier[r.si].navn}: ${fmt(r.v)}`); byX.set(r.x, o); });
  const tips = [...byX.values()];
  marks.push(Plot.ruleX(tips, Plot.pointerX({ x: 'x', stroke: 'var(--ink-3)', strokeOpacity: 0.5 })));
  marks.push(Plot.tip(tips, Plot.pointerX({ x: 'x', y: 'y', title: d => `${s.xEtikett ? (s.xEtikett[s.x.indexOf(d.x)] ?? d.x) : d.x}\n${d.lines.join('\n')}`, fill: 'var(--raised)', stroke: 'var(--line)' })));

  const maxLabel = Math.max(0, ...placed.map(p => p.text.length));
  const fig = Plot.plot(base({
    width, height, marginTop: mt, marginBottom: mb, marginRight: Math.min(200, 20 + maxLabel * 6.6),
    x: isYear ? { ticks: s.xTicks, tickFormat: v => String(Math.floor(v)), domain: [Math.min(...s.x, ...(s.band ? s.band.x : [])), Math.max(...s.x, ...(s.band ? s.band.x : []))] } : { type: 'point', ticks: s.xTicks, padding: 0.2 },
    y: { domain: [lo, hi], nice: false, tickFormat: AKSE[s.format || 'tall'] },
    marks,
  }));
  const out = [fig];
  if (s.yTittel) {
    const t = document.createElement('div'); t.className = 'nn-chart-note'; t.textContent = s.yTittel; out.unshift(t);
  }
  if (s.kilde) { const k = document.createElement('div'); k.className = 'nn-source'; k.textContent = s.kilde; out.push(k); }
  return out;
});
