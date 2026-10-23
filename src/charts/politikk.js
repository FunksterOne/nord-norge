// Diagrammer for tema 11 (nordområdepolitikken).
// varmekart: { kolonner:[…], rader:[{l, v:[…], uthev}], des:1, kilde }
//   Fargen i hver rad er skalert mot radens egen høyeste verdi, slik at skiftet over tid vises for hvert tema.
// regnskap:  { x:[…], serier:[{navn, data:[…], farge}], netto:{navn, data:[…]}, kilde }
//   Stablede stolper med positive og negative bidrag per år, og nettoendringen som punkt.
import { Plot, base, register, spec } from './core.js';
import { tall, heltall } from '../lib/format.js';

const FARGE = f => (!f ? 'var(--muted-mark)' : f.startsWith('var(') ? f : ({ accent: 'var(--accent)', ink: 'var(--ink)', neg: 'var(--neg)', pos: 'var(--pos)', warn: 'var(--warn)', muted: 'var(--muted-mark)' })[f] || `var(--${f})`);

function kildeNode(s) {
  if (!s.kilde) return null;
  const k = document.createElement('div'); k.className = 'nn-source'; k.textContent = s.kilde; return k;
}

register('varmekart', (el, width) => {
  const s = spec(el);
  const smal = width < 520;
  const des = s.des ?? 1, desCelle = smal ? 0 : des;
  const rows = [];
  s.rader.forEach((r, ri) => {
    const maks = Math.max(...r.v.filter(v => v != null)) || 1;
    r.v.forEach((v, ci) => rows.push({ l: r.l, k: s.kolonner[ci], v, a: v == null ? 0 : v / maks, ri, uthev: r.uthev }));
  });
  const marginLeft = smal ? 118 : 170;
  const celleH = smal ? 26 : 28;
  const fig = Plot.plot({
    width, height: s.rader.length * celleH + 34, marginLeft, marginRight: 4, marginTop: 26, marginBottom: 6,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: smal ? '10.5px' : '11.5px', color: 'var(--ink-3)', overflow: 'visible' },
    x: { domain: s.kolonner, axis: 'top', label: null, tickSize: 0, padding: 0.06, tickFormat: k => (smal && /^\d{4}$/.test(k) ? `’${k.slice(2)}` : k) },
    y: { domain: s.rader.map(r => r.l), label: null, tickSize: 0, padding: 0.08 },
    marks: [
      Plot.cell(rows, { x: 'k', y: 'l', fill: 'var(--accent)', fillOpacity: d => 0.08 + 0.82 * d.a }),
      Plot.text(rows, {
        x: 'k', y: 'l', text: d => (d.v == null ? '–' : tall(d.v, desCelle)),
        fill: d => (d.a > 0.55 ? 'var(--paper, #fff)' : 'var(--ink)'),
        fontWeight: d => (d.a >= 0.999 ? 700 : 500), fontVariant: 'tabular-nums',
      }),
      Plot.tip(rows, Plot.pointer({ x: 'k', y: 'l', title: d => `${d.l} · ${d.k}\n${tall(d.v, des)} per 10 000 ord`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  return [fig, kildeNode(s)];
});

register('regnskap', (el, width) => {
  const s = spec(el);
  const rows = [];
  s.serier.forEach((se, si) => se.data.forEach((v, i) => rows.push({ x: s.x[i], v: v || 0, serie: se.navn, si })));
  const netto = s.netto ? s.netto.data.map((v, i) => ({ x: s.x[i], v })) : [];
  const legende = document.createElement('div');
  legende.className = 'nn-chart-note';
  legende.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px 16px;margin-bottom:6px';
  legende.innerHTML = s.serier.map(se => `<span><i style="display:inline-block;width:10px;height:10px;background:${FARGE(se.farge)};margin-right:6px;vertical-align:-1px"></i>${se.navn}</span>`).join('')
    + (s.netto ? `<span><i style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ink);margin-right:6px;vertical-align:0"></i>${s.netto.navn}</span>` : '');
  const fig = Plot.plot(base({
    width, height: s.hoyde || 300, marginRight: 12, marginLeft: 52,
    x: { type: 'band', tickFormat: v => (width < 520 && Number(v) % 5 !== 0 ? '' : String(v)), padding: 0.18 },
    y: { tickFormat: v => heltall(v), ticks: 6 },
    color: { domain: s.serier.map(se => se.navn), range: s.serier.map(se => FARGE(se.farge)) },
    marks: [
      Plot.barY(rows, Plot.stackY({ x: 'x', y: 'v', fill: 'serie', order: s.serier.map(se => se.navn) })),
      Plot.ruleY([0], { stroke: 'var(--ink-3)' }),
      s.netto && Plot.dot(netto, { x: 'x', y: 'v', r: 3.2, fill: 'var(--ink)', stroke: 'var(--bg)', strokeWidth: 1 }),
      Plot.tip(s.x.map((x, i) => ({ x, linjer: s.serier.map(se => `${se.navn}: ${heltall(se.data[i])}`).concat(s.netto ? [`${s.netto.navn}: ${heltall(s.netto.data[i])}`] : []) })),
        Plot.pointerX({ x: 'x', title: d => `${d.x}\n${d.linjer.join('\n')}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
  }));
  return [legende, fig, kildeNode(s)];
});
