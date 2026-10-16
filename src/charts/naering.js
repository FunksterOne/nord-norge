// Næringsdiagrammer: konsentrasjonskart (lokaliseringskvotient per region) og manualdiagram.
import { Plot, register, spec, redraw } from './core.js';
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
import { L } from '../lib/legacy.js';
import { tall, heltall, prosent, endringPst } from '../lib/format.js';

/* global NAERING_DATA */
const ND = () => (typeof NAERING_DATA !== 'undefined' ? NAERING_DATA : null);

// Lokaliseringskvotient: regionens andel av sysselsettingen i næringen / landets andel.
// SØA kaller en næring «framtredende» når kvotienten er minst 1,5.
export function lqTabell(gruppeKeys) {
  const D = ND(); if (!D) return [];
  const rows = [];
  for (const r of L.REGIONS) {
    const nrs = Object.keys(L.KREGION).filter(nr => L.KREGION[nr] === r.id);
    const tot = nrs.reduce((s, nr) => s + (D.kommuner[nr]?.alle || 0), 0);
    for (const g of gruppeKeys) {
      const n = nrs.reduce((s, nr) => s + (D.kommuner[nr]?.[g] || 0), 0);
      const andel = tot ? n / tot : 0;
      const nat = D.landet[g] / D.landet.alle;
      rows.push({ region: r.navn, regionId: r.id, fylke: r.fylke, g, gNavn: D.grupper[g].navn, n, tot, andel: andel * 100, lq: nat ? andel / nat : 0 });
    }
  }
  return rows;
}

register('lq', (el, width) => {
  const s = spec(el);
  const D = ND(); if (!D) return document.createTextNode('');
  const keys = s.grupper;
  const rows = lqTabell(keys);
  const regioner = L.REGIONS.map(r => r.navn);
  const kol = keys.map(g => D.grupper[g].navn);
  const compact = width < 760;
  const fig = Plot.plot({
    width, height: regioner.length * (compact ? 30 : 34) + 150,
    marginLeft: compact ? 108 : 140, marginBottom: 8, marginTop: 150, marginRight: 70,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11.5px', color: 'var(--ink-2)', overflow: 'visible' },
    x: { domain: kol, axis: 'top', tickRotate: -40, tickSize: 0, label: null },
    y: { domain: regioner, tickSize: 0, label: null },
    color: { type: 'log', domain: [1, 16], range: [css('--panel'), css('--accent')], clamp: true, interpolate: 'lab' },
    marks: [
      Plot.cell(rows, { x: 'gNavn', y: 'region', fill: r => Math.max(1, Math.min(r.lq, 16)), inset: 1.5 }),
      Plot.cell(rows.filter(r => r.lq >= 1.5), { x: 'gNavn', y: 'region', stroke: 'var(--accent-text)', strokeWidth: 1.5, inset: 1.5, fill: 'none' }),
      Plot.text(rows.filter(r => r.n > 0), { x: 'gNavn', y: 'region', text: r => (r.lq >= 0.95 ? tall(r.lq, 1) : ''), fill: r => (r.lq >= 4 ? '#fff' : 'var(--ink)'), fontSize: compact ? 9.5 : 10.5, fontWeight: r => (r.lq >= 1.5 ? 600 : 400) }),
      Plot.tip(rows, Plot.pointer({ x: 'gNavn', y: 'region', title: r => `${r.region} · ${r.gNavn}\n${heltall(r.n)} sysselsatte (${prosent(r.andel, 1)} av regionen)\nKvotient mot landet: ${tall(r.lq, 2)}${r.lq >= 1.5 ? '\nFramtredende næring (≥ 1,5)' : ''}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  const leg = document.createElement('div'); leg.className = 'nn-legend';
  leg.innerHTML = '<span><i style="background:var(--panel);outline:1px solid var(--line)"></i>Under landssnittet</span><span><i style="background:color-mix(in srgb, var(--accent) 45%, var(--panel))"></i>Over</span><span><i style="background:var(--accent)"></i>Mye over</span><span><i style="background:transparent;outline:1.5px solid var(--accent-text)"></i>Framtredende (kvotient ≥ 1,5)</span>';
  const src = document.createElement('div'); src.className = 'nn-source';
  src.textContent = `Tallet i ruten er regionens andel av sysselsettingen i næringen delt på landets andel (1,0 = som landet). Sysselsatte etter arbeidssted, 4. kvartal ${D.aar}. Kilde: SSB tabell ${D.tabell}, egne beregninger etter SØAs metode (Nord-Norge 2040, figur 7).`;
  return [fig, leg, src];
});

// Manualdiagram: endring 2015 → siste år i Nord-Norge mot landet, per næring.
register('naeringvekst', (el, width) => {
  const s = spec(el);
  const D = ND(); if (!D) return document.createTextNode('');
  const rows = s.grupper.map(g => {
    const nn = D.nn_2015[g] ? (D.nn[g] / D.nn_2015[g] - 1) * 100 : null;
    const no = D.landet_2015[g] ? (D.landet[g] / D.landet_2015[g] - 1) * 100 : null;
    return { g, navn: D.grupper[g].navn, nn, no, n: D.nn[g], n0: D.nn_2015[g] };
  }).filter(r => r.nn != null && r.no != null).sort((a, b) => b.nn - a.nn);
  const lo = Math.min(0, ...rows.flatMap(r => [r.nn, r.no])), hi = Math.max(...rows.flatMap(r => [r.nn, r.no]));
  const fig = Plot.plot({
    width, height: rows.length * 30 + 50, marginLeft: 190, marginRight: 70, marginTop: 30, marginBottom: 24,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--ink-2)', overflow: 'visible' },
    x: { domain: [lo - 5, hi + 5], tickFormat: v => `${v > 0 ? '+' : ''}${tall(v, 0)} %`, ticks: 6, tickSize: 0, label: null, axis: 'top' },
    y: { domain: rows.map(r => r.navn), tickSize: 0, label: null },
    marks: [
      Plot.ruleX([0], { stroke: 'var(--line)' }),
      Plot.link(rows, { x1: 'no', x2: 'nn', y1: 'navn', y2: 'navn', stroke: 'var(--line)', strokeWidth: 3 }),
      Plot.dot(rows, { x: 'no', y: 'navn', r: 5, fill: 'var(--cat-4)' }),
      Plot.dot(rows, { x: 'nn', y: 'navn', r: 6, fill: 'var(--accent)', stroke: 'var(--bg)', strokeWidth: 1.5 }),
      Plot.text(rows, { x: r => Math.max(r.nn, r.no), y: 'navn', text: r => endringPst(r.nn, 0), dx: 12, textAnchor: 'start', fill: 'var(--accent-text)', fontWeight: 600 }),
      Plot.tip(rows, Plot.pointerY({ x: 'nn', y: 'navn', title: r => `${r.navn}\nNord-Norge: ${heltall(r.n0)} → ${heltall(r.n)} (${endringPst(r.nn, 1)})\nLandet: ${endringPst(r.no, 1)}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  });
  const leg = document.createElement('div'); leg.className = 'nn-legend';
  leg.innerHTML = `<span><i style="background:var(--accent);border-radius:50%;width:10px"></i>Nord-Norge</span><span><i style="background:var(--cat-4);border-radius:50%;width:10px"></i>Hele landet</span><span class="nn-legend-note">Endring i sysselsatte (arbeidssted) 2015–${D.aar}. SSB ${D.tabell}.</span>`;
  return [fig, leg];
});

window.addEventListener('nn:tema', () => document.querySelectorAll('[data-nnchart="lq"]').forEach(redraw));
