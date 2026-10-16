// Befolkningsbaner (kommune/fylke/landsdel): total, dekomponering, forsørgerbyrde, aldring.
// Leser de globale strukturene fra assets/data.js og assets/app.js (DATA, K, AGG, state, MW).
import { Plot, base, register, spec } from './core.js';
import { heltall, tall, endring } from '../lib/format.js';
import { L } from '../lib/legacy.js';


function findK(nr) {
  return L.K.find(x => x.nr === nr) || L.AGG[nr] || null;
}

// Skyv etiketter fra hverandre i pikselrom (minst `gap` px), returner nye dataverdier.
function dodge(labels, yScale, gap = 14) {
  const items = labels.map(l => ({ ...l, py: yScale(l.value) })).sort((a, b) => a.py - b.py);
  for (let i = 1; i < items.length; i++) {
    if (items[i].py - items[i - 1].py < gap) items[i].py = items[i - 1].py + gap;
  }
  return items;
}

function legend(items) {
  const d = document.createElement('div');
  d.className = 'nn-legend';
  d.innerHTML = items.map(([c, t, dash]) =>
    `<span><i style="background:${dash ? 'transparent' : c};border-top:${dash ? `2px dashed ${c}` : '0'}"></i>${t}</span>`).join('');
  return d;
}

function renderTot(el, width, k, o) {
  const P = L.DATA.proj, yrs = P.years, n = yrs.length;
  const st = L.state;
  const mw = L.MW(o);
  const us = st.ukr ? (st.ukrbase === 'attr' ? (o['ukra' + st.ukr] || null) : ((mw && mw['u' + st.ukr]) || null)) : null;
  const hist = k.hist || {};
  const histYears = Object.keys(hist).map(Number).sort((a, b) => a - b);

  const lines = [];
  const push = (serie, arr, yearsArr = yrs) => arr && arr.forEach((v, i) => v != null && lines.push({ year: yearsArr[i], value: v, serie }));
  push('hist', histYears.map(y => hist[y]), histYears);
  if (histYears.length && histYears[histYears.length - 1] < yrs[0]) lines.push({ year: yrs[0], value: o.main[0], serie: 'hist' });
  push('main', o.main);
  push('low', o.low);
  push('high', o.high);
  if (o.tfattr) push('attr', o.tfattr);
  if (mw && st.showMVP) push('mvp', mw.pop);
  if (us) push('ukr', us);

  const band = yrs.map((y, i) => ({ year: y, low: o.low[i], high: o.high[i] }));
  const sens = (st.sens && mw && st.showMVP) ? yrs.map((y, i) => ({ year: y, lo: mw.s75[i], hi: mw.s125[i] })) : null;

  const all = lines.map(d => d.value).concat(sens ? sens.flatMap(d => [d.lo, d.hi]) : []);
  let lo = Math.min(...all), hi = Math.max(...all);
  const pad = (hi - lo) * 0.06 || hi * 0.04; lo -= pad; hi += pad;

  const height = 340, mt = 26, mb = 30;
  const yScale = v => mt + (1 - (v - lo) / (hi - lo)) * (height - mt - mb);
  const yInv = py => lo + (1 - (py - mt) / (height - mt - mb)) * (hi - lo);

  const last = (arr) => arr[arr.length - 1];
  const endLabels = [
    { serie: 'main', value: last(o.main), text: `SSB ${heltall(last(o.main))}`, color: 'var(--accent-text)', weight: 600 },
    { serie: 'high', value: last(o.high), text: `Høy ${heltall(last(o.high))}`, color: 'var(--ink-3)' },
    { serie: 'low', value: last(o.low), text: `Lav ${heltall(last(o.low))}`, color: 'var(--ink-3)' },
  ];
  if (o.tfattr) endLabels.push({ serie: 'attr', value: last(o.tfattr), text: `TF-ATTR ${heltall(last(o.tfattr))}`, color: 'var(--cat-4)' });
  if (mw && st.showMVP) endLabels.push({ serie: 'mvp', value: last(mw.pop), text: `TF-MVP ${heltall(last(mw.pop))}`, color: 'var(--cat-5)' });
  if (us) endLabels.push({ serie: 'ukr', value: last(us), text: `Ukraina ${heltall(last(us))}`, color: 'var(--cat-6)' });
  const placed = dodge(endLabels, yScale).map(l => ({ ...l, y: yInv(l.py), year: yrs[n - 1] }));

  // Bred tabell for verktøytips
  const wide = new Map();
  for (const d of lines) {
    const r = wide.get(d.year) || { year: d.year };
    r[d.serie] = d.value; wide.set(d.year, r);
  }
  const tipRows = [...wide.values()].sort((a, b) => a.year - b.year).map(r => ({
    ...r,
    yAnchor: r.main ?? r.hist,
    tekst: [
      r.hist != null && r.year <= 2026 ? `Faktisk: ${heltall(r.hist)}` : null,
      r.main != null ? `SSB MMMM: ${heltall(r.main)}` : null,
      r.low != null ? `SSB lav–høy: ${heltall(r.low)}–${heltall(r.high)}` : null,
      r.attr != null ? `TF-ATTR: ${heltall(r.attr)}` : null,
      r.mvp != null ? `TF-MVP: ${heltall(r.mvp)}` : null,
      r.ukr != null ? `Ukraina-scenario: ${heltall(r.ukr)}` : null,
    ].filter(Boolean).join('\n'),
  }));

  const xMin = histYears.length ? Math.min(histYears[0], yrs[0]) : yrs[0];
  const ticks = [];
  for (let y = Math.ceil(xMin / 10) * 10; y <= yrs[n - 1]; y += 10) ticks.push(y);

  const S = (serie) => lines.filter(d => d.serie === serie);
  const fig = Plot.plot(base({
    width, height, marginTop: mt, marginBottom: mb, marginRight: 96,
    x: { domain: [xMin, yrs[n - 1]], ticks, tickFormat: d => String(d) },
    y: { domain: [lo, hi], nice: false },
    marks: [
      Plot.areaY(band, { x: 'year', y1: 'low', y2: 'high', fill: 'var(--accent)', fillOpacity: 0.13 }),
      sens && Plot.areaY(sens, { x: 'year', y1: 'lo', y2: 'hi', fill: 'var(--cat-5)', fillOpacity: 0.14 }),
      Plot.ruleX([2026], { stroke: 'var(--ink-3)', strokeDasharray: '2,3' }),
      Plot.text([2026], { x: d => d, frameAnchor: 'top', dy: -14, text: () => 'I dag', fill: 'var(--ink-3)', fontSize: 11 }),
      Plot.lineY(S('low'), { x: 'year', y: 'value', stroke: 'var(--accent)', strokeOpacity: 0.55, strokeWidth: 1, strokeDasharray: '3,3' }),
      Plot.lineY(S('high'), { x: 'year', y: 'value', stroke: 'var(--accent)', strokeOpacity: 0.55, strokeWidth: 1, strokeDasharray: '3,3' }),
      Plot.lineY(S('hist'), { x: 'year', y: 'value', stroke: 'var(--ink)', strokeWidth: 2 }),
      Plot.dot(S('hist').filter(d => d.year <= 2025), { x: 'year', y: 'value', r: 2.6, fill: 'var(--ink)' }),
      o.tfattr && Plot.lineY(S('attr'), { x: 'year', y: 'value', stroke: 'var(--cat-4)', strokeWidth: 1.8, strokeDasharray: '1,4', strokeLinecap: 'round' }),
      mw && st.showMVP && Plot.lineY(S('mvp'), { x: 'year', y: 'value', stroke: 'var(--cat-5)', strokeWidth: 1.8, strokeDasharray: '6,3' }),
      us && Plot.lineY(S('ukr'), { x: 'year', y: 'value', stroke: 'var(--cat-6)', strokeWidth: 2 }),
      Plot.lineY(S('main'), { x: 'year', y: 'value', stroke: 'var(--accent)', strokeWidth: 2.6 }),
      Plot.dot([{ year: 2026, value: k.pop }], { x: 'year', y: 'value', r: 4.5, fill: 'var(--accent)', stroke: 'var(--bg)', strokeWidth: 2 }),
      Plot.text(placed, { x: 'year', y: 'y', text: 'text', fill: d => d.color, dx: 8, textAnchor: 'start', fontWeight: d => d.weight || 400, fontSize: 11.5 }),
      Plot.ruleX(tipRows, Plot.pointerX({ x: 'year', stroke: 'var(--ink-3)', strokeOpacity: 0.6 })),
      Plot.dot(tipRows, Plot.pointerX({ x: 'year', y: 'yAnchor', r: 4, fill: 'var(--accent)', stroke: 'var(--bg)', strokeWidth: 2 })),
      Plot.tip(tipRows, Plot.pointerX({ x: 'year', y: 'yAnchor', title: d => `${d.year}\n${d.tekst}`, fill: 'var(--raised)', stroke: 'var(--line)', textPadding: 9, fontSize: 12 })),
    ].filter(Boolean),
  }));

  const leg = [['var(--ink)', histYears.length ? `Faktisk ${histYears[0]}–${histYears[histYears.length - 1]}` : 'Faktisk'],
    ['var(--accent)', 'SSB MMMM (hovedbane)'], ['color-mix(in srgb, var(--accent) 30%, transparent)', 'SSB lav–høy']];
  if (o.tfattr) leg.push(['var(--cat-4)', 'TF-ATTR (tilleggsbane)', true]);
  if (mw && st.showMVP) leg.push(['var(--cat-5)', 'TF-MVP (tilleggsbane)', true]);
  if (us) leg.push(['var(--cat-6)', 'Ukraina-scenario']);
  return [fig, legend(leg)];
}

function renderDec(el, width, k, o) {
  const st = L.state;
  const mw = L.MW(o);
  const n = L.DATA.proj.years.length;
  const p0 = mw ? mw.pop[0] : o.main[0];
  const nat = mw ? mw.nat[n - 1] : 0, mig = mw ? mw.mig[n - 1] : 0, tot = nat + mig;
  const rows = [
    { lab: 'Fødselsoverskudd', v: nat },
    { lab: 'Nettoflytting', v: mig },
    { lab: 'Sum 2026–2050', v: tot, sum: true },
  ];
  const winLab = ({ kons: 'smalt vindu 2017–2021', sentral: 'bredt vindu', opt: 'vektet 2022–2023' })[st.mw] || st.mw;
  const head = document.createElement('div');
  head.className = 'nn-chart-note';
  head.innerHTML = `Bane: <b>TF-MVP, ${winLab}</b> (tilleggsbane — SSB publiserer ikke komponentene per kommune). Folketall ${heltall(p0)} → <b>${heltall(p0 + tot)}</b>.`;
  const m = Math.max(...rows.map(r => Math.abs(r.v)), 1) * 1.25;
  const fig = Plot.plot(base({
    width, height: 300, marginLeft: 64, marginRight: 24,
    x: { domain: rows.map(r => r.lab), padding: 0.45, tickFormat: d => d },
    y: { domain: [-m, m], tickFormat: v => endring(v, 0) },
    marks: [
      Plot.ruleY([0], { stroke: 'var(--rule)' }),
      Plot.barY(rows, { x: 'lab', y: 'v', fill: d => d.sum ? (d.v < 0 ? 'var(--neg)' : 'var(--accent)') : 'var(--muted-mark)' }),
      Plot.text(rows, { x: 'lab', y: 'v', text: d => endring(Math.round(d.v), 0), dy: d => d.v < 0 ? 12 : -10, fill: 'var(--ink)', fontWeight: 600, fontSize: 13 }),
      Plot.tip(rows, Plot.pointer({ x: 'lab', y: 'v', title: d => `${d.lab}\n${endring(Math.round(d.v), 0)} personer`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  }));
  return [head, fig];
}

function renderFb(el, width, k, o, sp = {}) {
  const yrs = L.DATA.proj.years;
  const r = o.a65.map((v, i) => ({ year: yrs[i], v: o.a2064[i] ? 100 * v / o.a2064[i] : null }));
  const i65 = o.a65.map((v, i) => ({ year: yrs[i], v: 100 * v / o.a65[0], g: '65+' }));
  const i20 = o.a2064.map((v, i) => ({ year: yrs[i], v: 100 * v / o.a2064[0], g: '20–64' }));
  const r0 = r[0].v, rN = r[r.length - 1].v;
  const ticks = [2026, 2030, 2035, 2040, 2045, 2050];

  const t1 = document.createElement('div'); t1.className = 'nn-subhead';
  t1.textContent = 'Eldre (65+) per 100 i yrkesaktiv alder (20–64)';
  const figA = Plot.plot(base({
    width, height: 230, marginRight: 56,
    x: { ticks, tickFormat: String },
    y: { nice: true, tickFormat: v => tall(v, 0), domain: sp.ref ? [Math.min(...r.map(d => d.v)) - 2, Math.max(sp.ref, ...r.map(d => d.v)) + 2] : undefined },
    marks: [
      Plot.areaY(r, { x: 'year', y1: r0, y2: 'v', fill: 'var(--accent)', fillOpacity: 0.12 }),
      Plot.ruleY([r0], { stroke: 'var(--ink-3)', strokeDasharray: '2,3' }),
      sp.ref && Plot.ruleY([sp.ref], { stroke: 'var(--warn)', strokeWidth: 1.2 }),
      sp.ref && Plot.text([sp.ref], { y: d => d, frameAnchor: 'right', dx: 52, dy: -8, text: () => `OECD 2050 ≈ ${sp.ref}`, fill: 'var(--warn)', fontSize: 11 }),
      Plot.lineY(r, { x: 'year', y: 'v', stroke: 'var(--accent)', strokeWidth: 2.6 }),
      Plot.dot([r[0], r[r.length - 1]], { x: 'year', y: 'v', r: 4.5, fill: 'var(--accent)', stroke: 'var(--bg)', strokeWidth: 2 }),
      Plot.text([r[0]], { x: 'year', y: 'v', text: d => tall(d.v, 0), dy: -12, fill: 'var(--ink)', fontWeight: 600, fontSize: 13 }),
      Plot.text([r[r.length - 1]], { x: 'year', y: 'v', text: d => tall(d.v, 0), dx: 10, textAnchor: 'start', fill: 'var(--accent-text)', fontWeight: 600, fontSize: 13 }),
      Plot.tip(r, Plot.pointerX({ x: 'year', y: 'v', title: d => `${d.year}\n${tall(d.v, 1)} eldre per 100 yrkesaktive\n${tall(100 / d.v, 1)} yrkesaktive per eldre`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  }));
  const t2 = document.createElement('div'); t2.className = 'nn-subhead';
  t2.textContent = 'Hvorfor: eldre og yrkesaktive, indeksert (2026 = 100)';
  const both = i65.concat(i20);
  const ends = [i65[i65.length - 1], i20[i20.length - 1]];
  const figB = Plot.plot(base({
    width, height: 190, marginRight: 96,
    x: { ticks, tickFormat: String },
    y: { nice: true, tickFormat: v => tall(v, 0) },
    marks: [
      Plot.ruleY([100], { stroke: 'var(--ink-3)', strokeDasharray: '2,3' }),
      Plot.lineY(both, { x: 'year', y: 'v', z: 'g', stroke: d => d.g === '65+' ? 'var(--accent)' : 'var(--cat-4)', strokeWidth: 2.2 }),
      Plot.text(ends, { x: 'year', y: 'v', text: d => `${d.g} ${endring(d.v - 100, 0)} %`, dx: 8, textAnchor: 'start', fill: d => d.g === '65+' ? 'var(--accent-text)' : 'var(--ink-2)', fontWeight: 600 }),
      Plot.tip(both, Plot.pointer({ x: 'year', y: 'v', title: d => `${d.year} · ${d.g}\nIndeks ${tall(d.v, 1)}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  }));
  const note = document.createElement('div'); note.className = 'nn-chart-note';
  note.innerHTML = `Fra <b>${tall(r0, 0)}</b> til <b>${tall(rN, 0)}</b> eldre per 100 yrkesaktive. Grunnlag: SSB tabell 14746, hovedalternativet (MMMM).`;
  return [t1, figA, t2, figB, note];
}

function renderAge(el, width, k, o) {
  const yrs = L.DATA.proj.years;
  const groups = [['a019', '0–19 år', 'var(--cat-4)'], ['a2064', '20–64 år', 'var(--cat-2)'], ['a65', '65+ år', 'var(--accent)']];
  if (o.a80) groups.push(['a80', 'herav 80+', 'var(--cat-5)']);
  const want = [2026, 2030, 2035, 2040, 2045, 2050].filter(y => yrs.includes(y));
  const rows = [];
  for (const y of want) for (const [key, lab] of groups) rows.push({ year: String(y), g: lab, v: o[key][yrs.indexOf(y)] });
  const color = Object.fromEntries(groups.map(g => [g[1], g[2]]));
  const compact = width < 640;
  const fig = Plot.plot(base({
    width, height: 320, marginRight: 16,
    fx: { label: null, tickSize: 0, padding: 0.12 },
    x: { axis: null, domain: groups.map(g => g[1]), padding: 0.12 },
    y: { nice: true },
    marks: [
      Plot.ruleY([0], { stroke: 'var(--rule)' }),
      Plot.barY(rows, { fx: 'year', x: 'g', y: 'v', fill: d => color[d.g] }),
      !compact && Plot.text(rows, { fx: 'year', x: 'g', y: 'v', text: d => heltall(d.v), dy: -8, fill: 'var(--ink-2)', fontSize: 10 }),
      Plot.tip(rows, Plot.pointer({ fx: 'year', x: 'g', y: 'v', title: d => `${d.year} · ${d.g}\n${heltall(d.v)} personer`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
  }));
  const leg = legend(groups.map(g => [g[2], g[1]]));
  if (o.a80) leg.insertAdjacentHTML('beforeend', '<span class="nn-legend-note">80+ er en del av 65+ og skal ikke legges sammen.</span>');
  return [fig, leg];
}

register('proj', (el, width) => {
  const s = spec(el);
  const P = L.DATA && L.DATA.proj;
  const o = P && P.kommuner[s.nr];
  const k = findK(s.nr);
  if (!o || !k) return document.createTextNode('');
  if (s.mode === 'tot') return renderTot(el, width, k, o);
  if (s.mode === 'dec') return renderDec(el, width, k, o);
  if (s.mode === 'fb') return renderFb(el, width, k, o, s);
  return renderAge(el, width, k, o);
});

