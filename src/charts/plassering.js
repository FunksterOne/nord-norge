// «Hvor står kommunen?» — bisvermstriper for alle 80 kommuner per indikator,
// med valgt kommune fremhevet i aksentblått. Spesifikasjon: { nr }
import { Plot, register, spec } from './core.js';
import { L } from '../lib/legacy.js';
import { tall, endringPst, prosent, kortNavn } from '../lib/format.js';
import { INDIKATORER } from './map.js';

const kostra = (nr, f) => { const k = L.DATA?.proj?.kostra?.[nr]; return k && k[f] != null ? +k[f] : null; };

function defs() {
  const yr = (L.DATA?.proj?.kostra && Object.values(L.DATA.proj.kostra)[0]?.yr) || '';
  return [
    { ...INDIKATORER.endring, key: 'endring', navn: 'Folketall 2026–2050', tekst: v => endringPst(v, 1) },
    { ...INDIKATORER.eldre, key: 'eldre', navn: 'Andel 65 år og over', tekst: v => prosent(v, 1) },
    { ...INDIKATORER.forsorg, key: 'forsorg', navn: 'Forsørgerbrøk 2050', tekst: v => tall(v, 0) },
    { ...INDIKATORER.innv, key: 'innv', navn: 'Innvandrerbakgrunn', tekst: v => prosent(v, 1) },
    { key: 'ndr', navn: `Netto driftsresultat ${yr}`, verdi: k => kostra(k.nr, 'ndr'), tekst: v => prosent(v, 1), ref: 1.75, refTxt: 'TBU-norm 1,75 %' },
    { key: 'fond', navn: `Disposisjonsfond ${yr}`, verdi: k => kostra(k.nr, 'fond'), tekst: v => prosent(v, 1), ref: 10, refTxt: 'Solid buffer: minst 10 %' },
  ];
}

register('plassering', (el, width) => {
  const s = spec(el);
  const me = L.K.find(k => k.nr === s.nr);
  if (!me) return document.createTextNode('');
  const out = [];
  const compact = width < 560;
  for (const d of defs()) {
    const rows = L.K.map(k => ({ nr: k.nr, navn: kortNavn(k.navn), fylke: k.fylke, v: d.verdi(k) })).filter(r => r.v != null && Number.isFinite(r.v));
    const mine = rows.find(r => r.nr === me.nr);
    if (!mine) continue;
    const sorted = rows.map(r => r.v).sort((a, b) => a - b);
    const rank = rows.filter(r => r.v > mine.v).length + 1;
    const median = sorted[Math.floor(sorted.length / 2)];

    const head = document.createElement('div');
    head.className = 'nn-pl-head';
    head.innerHTML = `<span class="nn-pl-navn">${d.navn}</span><span class="nn-pl-verdi">${d.tekst(mine.v)}</span><span class="nn-pl-rang" title="Rangert etter verdi, høyeste verdi er nr. 1">nr. ${rank} av ${rows.length} (høyest = 1)</span>`;
    const others = rows.filter(r => r.nr !== me.nr);
    const fig = Plot.plot({
      width, height: d.key === 'fond' ? 122 : (compact ? 92 : 88),
      y: { axis: null },
      marginLeft: 8, marginRight: 8, marginTop: 6, marginBottom: 22,
      style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11px', color: 'var(--ink-3)', overflow: 'visible' },
      x: { nice: true, ticks: compact ? 3 : 5, tickSize: 0, tickFormat: v => d.tekst(v).replace(/,0 %$/, ' %'), label: null },
      marks: [
        Plot.ruleX([median], { stroke: 'var(--ink-3)', strokeDasharray: '2,2', y1: 0, y2: 1 }),
        d.ref != null && Plot.ruleX([d.ref], { stroke: 'var(--warn)', strokeWidth: 1.2 }),
        Plot.dot(others, Plot.dodgeY({ x: 'v', anchor: 'middle', r: 2.8, fill: 'var(--muted-mark)', padding: 0.5 })),
        Plot.dot([mine], { x: 'v', frameAnchor: 'middle', r: 7, fill: 'var(--accent)', stroke: 'var(--bg)', strokeWidth: 2 }),
        Plot.tip(others, Plot.pointer(Plot.dodgeY({ x: 'v', anchor: 'middle', r: 2.8, padding: 0.5, title: r => `${r.navn} (${r.fylke})\n${d.tekst(r.v)}`, fill: 'var(--raised)', stroke: 'var(--line)' }))),
      ].filter(Boolean),
    });
    fig.addEventListener('click', () => { const v = fig.value; if (v && v.nr) location.href = `kommune.html?k=${v.nr}`; });
    fig.style.cursor = 'pointer';
    const row = document.createElement('div');
    row.className = 'nn-pl-row';
    row.append(head, fig);
    if (d.refTxt) {
      const n = document.createElement('div'); n.className = 'nn-pl-ref';
      n.innerHTML = `<i></i>${d.refTxt}<span>Stiplet = median for de 80</span>`;
      row.appendChild(n);
    }
    out.push(row);
  }
  const src = document.createElement('div'); src.className = 'nn-source';
  src.textContent = 'Hver prikk er én kommune. Kilde: SSB (07459, 14746, 09817, KOSTRA 12143). Pek på en prikk for navn, klikk for å åpne kommunen.';
  out.push(src);
  return out;
});
