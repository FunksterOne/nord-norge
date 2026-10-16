// «80 skjebner»: små multipler – folketall 2000–2050 for hver kommune, indeksert (2026 = 100).
// Sortert etter endring mot 2050. Spesifikasjon: { fylke }
import { Plot, register, spec, redraw } from './core.js';
import { L } from '../lib/legacy.js';
import { endringPst, heltall, kortNavn } from '../lib/format.js';

register('skjebner', (el, width) => {
  const s = spec(el);
  const P = L.DATA?.proj; if (!P) return document.createTextNode('');
  const yrs = P.years;
  const ks = L.K.filter(k => !s.fylke || s.fylke === 'Alle' || k.fylke === s.fylke).map(k => {
    const o = P.kommuner[k.nr];
    const base = o.main[0];
    const ch = (o.main[o.main.length - 1] / base - 1) * 100;
    return { k, o, base, ch };
  }).sort((a, b) => (s.sort === 'navn' ? a.k.navn.localeCompare(b.k.navn, 'nb') : b.ch - a.ch));

  const cols = width >= 1000 ? 10 : width >= 760 ? 8 : width >= 520 ? 5 : 4;
  const rows = [];
  ks.forEach((d, i) => {
    const fx = i % cols, fy = Math.floor(i / cols);
    const hist = d.k.hist || {};
    Object.keys(hist).map(Number).sort((a, b) => a - b).forEach(y => rows.push({ fx, fy, year: y, v: hist[y] / d.base * 100, s: 'h', nr: d.k.nr }));
    d.o.main.forEach((v, j) => rows.push({ fx, fy, year: yrs[j], v: v / d.base * 100, s: 'p', nr: d.k.nr }));
  });
  const labels = ks.map((d, i) => ({ fx: i % cols, fy: Math.floor(i / cols), navn: kortNavn(d.k.navn), ch: d.ch, nr: d.k.nr, pop: d.k.pop }));
  const nRows = Math.ceil(ks.length / cols);
  const cellH = width < 520 ? 72 : 78;

  const bar = document.createElement('div');
  bar.className = 'nn-seg';
  bar.innerHTML = ['Alle', 'Nordland', 'Troms', 'Finnmark'].map(f => `<button type="button" data-f="${f}" aria-selected="${(s.fylke || 'Alle') === f}">${f === 'Alle' ? 'Hele landsdelen' : f}</button>`).join('')
    + `<button type="button" data-sort="1" aria-pressed="${s.sort === 'navn'}">${s.sort === 'navn' ? 'Sortert etter navn' : 'Sortert etter endring'}</button>`;
  bar.addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    const ns = { ...s };
    if (b.dataset.f) ns.fylke = b.dataset.f;
    if (b.dataset.sort) ns.sort = s.sort === 'navn' ? 'endring' : 'navn';
    el.dataset.spec = JSON.stringify(ns); redraw(el);
  });

  const fig = Plot.plot({
    width, height: nRows * cellH + 10,
    marginTop: 4, marginBottom: 4, marginLeft: 4, marginRight: 4,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '10.5px', color: 'var(--ink-3)', overflow: 'visible' },
    fx: { axis: null, padding: 0.12 }, fy: { axis: null, padding: 0.22 },
    x: { axis: null, domain: [2000, 2050] },
    y: { axis: null, domain: [55, 150], clamp: true },
    marks: [
      Plot.frame({ stroke: 'var(--line-soft)' }),
      Plot.ruleY([100], { stroke: 'var(--line)', strokeWidth: 0.8 }),
      Plot.ruleX([2026], { stroke: 'var(--line)', strokeWidth: 0.8 }),
      Plot.lineY(rows.filter(r => r.s === 'h'), { fx: 'fx', fy: 'fy', x: 'year', y: 'v', z: 'nr', stroke: 'var(--ink-2)', strokeWidth: 1.2 }),
      Plot.lineY(rows.filter(r => r.s === 'p'), { fx: 'fx', fy: 'fy', x: 'year', y: 'v', z: 'nr', stroke: r => r.v >= 100 ? 'var(--pos)' : 'var(--neg)', strokeWidth: 1.8 }),
      Plot.text(labels, { fx: 'fx', fy: 'fy', frameAnchor: 'top-left', dx: 4, dy: 4, text: 'navn', fill: 'var(--ink)', fontSize: 10.5, fontWeight: 500 }),
      Plot.text(labels, { fx: 'fx', fy: 'fy', frameAnchor: 'bottom-right', dx: -4, dy: -3, text: d => endringPst(d.ch, 0), fill: d => d.ch >= 0 ? 'var(--pos)' : 'var(--neg)', fontSize: 10.5, fontWeight: 600 }),
      Plot.tip(labels, Plot.pointer({ fx: 'fx', fy: 'fy', frameAnchor: 'middle', title: d => `${d.navn}\nFolketall 2026: ${heltall(d.pop)}\nEndring mot 2050 (SSB MMMM): ${endringPst(d.ch, 1)}\nKlikk for kommunesiden`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  fig.style.cursor = 'pointer';
  fig.addEventListener('click', () => { const v = fig.value; if (v && v.nr) location.href = `kommune.html?k=${v.nr}`; });
  const note = document.createElement('div'); note.className = 'nn-source';
  note.textContent = 'Indeksert folketall (2026 = 100). Grå = faktisk 2000–2025 (SSB 07459), farget = SSB hovedalternativ MMMM 2026–2050 (14746): grønn over, rød under dagens nivå. Lik skala i alle ruter, kuttet ved 55 og 150.';
  return [bar, fig, note];
});
