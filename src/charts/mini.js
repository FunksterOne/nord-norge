// Små linjediagrammer (KOSTRA): faktisk serie, landsdelsmedian (stiplet), valgfri framskriving
// og referanselinje. Spesifikasjon: { tittel, sub, hx, hv, bench, px, pv, ref:{val,label}, signed, unit:'pct'|'kr', farge }
import { Plot, register, spec } from './core.js';
import { tall, heltall } from '../lib/format.js';

register('mini', (el, width) => {
  const s = spec(el);
  const f = s.unit === 'kr' ? (v => heltall(v)) : (v => `${s.signed && v > 0 ? '+' : ''}${tall(v, 1)}`);
  const ser = (xs, vs, navn) => (xs || []).map((x, i) => ({ x, v: vs ? vs[i] : null, navn })).filter(d => d.v != null);
  const hist = ser(s.hx, s.hv, 'faktisk'), bench = ser(s.hx, s.bench, 'median'), proj = ser(s.px, s.pv, 'framskrevet');
  if (!hist.length && !proj.length) return document.createTextNode('');
  const farge = s.farge || 'var(--accent)';
  const xs = [...(s.hx || []), ...(s.px || [])];
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const ticks = []; for (let y = Math.ceil(x0 / 5) * 5; y <= x1; y += 5) ticks.push(y);
  const vals = [...hist, ...bench, ...proj].map(d => d.v).concat(s.ref && s.ref.val != null ? [s.ref.val] : []).concat(s.signed ? [0] : []);
  const lastH = hist[hist.length - 1], lastP = proj[proj.length - 1];
  const head = document.createElement('div'); head.className = 'nn-mini-h';
  head.innerHTML = `<b>${s.tittel}</b><span>${s.sub || ''}</span>`;
  const fig = Plot.plot({
    width, height: 150, marginLeft: 40, marginRight: 40, marginTop: 14, marginBottom: 22,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '10.5px', color: 'var(--ink-3)', overflow: 'visible' },
    x: { domain: [x0, x1], ticks, tickFormat: String, tickSize: 0, label: null },
    y: { domain: [Math.min(...vals), Math.max(...vals)], nice: true, ticks: 3, tickSize: 0, tickFormat: f, label: null },
    marks: [
      s.signed && Plot.ruleY([0], { stroke: 'var(--line)' }),
      s.ref && s.ref.val != null && Plot.ruleY([s.ref.val], { stroke: 'var(--warn)', strokeWidth: 1 }),
      s.ref && s.ref.val != null && Plot.text([s.ref.val], { y: d => d, frameAnchor: 'left', dx: 2, dy: -6, text: () => s.ref.label, fill: 'var(--warn)', fontSize: 10, textAnchor: 'start' }),
      proj.length && Plot.ruleX([proj[0].x], { stroke: 'var(--ink-3)', strokeDasharray: '2,3' }),
      Plot.lineY(bench, { x: 'x', y: 'v', stroke: 'var(--ink-3)', strokeWidth: 1, strokeDasharray: '2,3' }),
      Plot.lineY(proj, { x: 'x', y: 'v', stroke: farge, strokeWidth: 1.8, strokeDasharray: '5,3' }),
      Plot.lineY(hist, { x: 'x', y: 'v', stroke: farge, strokeWidth: 2.2 }),
      lastH && Plot.dot([lastH], { x: 'x', y: 'v', r: 3, fill: farge }),
      lastH && !lastP && Plot.text([lastH], { x: 'x', y: 'v', text: d => f(d.v), dx: 6, textAnchor: 'start', fill: 'var(--ink)', fontWeight: 600, fontSize: 11 }),
      lastP && Plot.text([lastP], { x: 'x', y: 'v', text: d => f(d.v), dx: 6, textAnchor: 'start', fill: 'var(--ink)', fontWeight: 600, fontSize: 11 }),
      Plot.tip([...hist, ...bench, ...proj], Plot.pointer({ x: 'x', y: 'v', title: d => `${d.x} · ${d.navn}\n${f(d.v)}${s.unit === 'kr' ? ' kr' : ' %'}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
  });
  return [head, fig];
});
