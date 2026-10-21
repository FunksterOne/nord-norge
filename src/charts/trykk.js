// Trykkmatrise for de 13 SØA-regionene: aldring i dag mot tap av arbeidsføre mot 2050.
// Animert overgang (D3) mellom spredningsdiagram og rangering. Spesifikasjon: { view }
import * as d3 from 'd3';
import { register, spec } from './core.js';
import { L } from '../lib/legacy.js';
import { tall, heltall, endringPst } from '../lib/format.js';

const FY = { Nordland: 'var(--fy-nordland)', Troms: 'var(--fy-troms)', Finnmark: 'var(--fy-finnmark)' };

function regionRows() {
  const P = L.DATA?.proj; if (!P) return [];
  const last = P.years.length - 1;
  return L.REGIONS.map((r, i) => {
    const ag = L.AGG[-(101 + i)]; if (!ag) return null;
    let e65 = 0; for (let a = 65; a < 106; a++) e65 += ag.alder[a] || 0;
    const pk = P.kommuner[String(-(101 + i))];
    const wf = pk ? (pk.a2064[last] / pk.a2064[0] - 1) * 100 : null;
    const b50 = pk ? pk.a65[last] / pk.a2064[last] * 100 : null;
    return { id: r.id, navn: r.navn, fylke: r.fylke, pop: ag.pop, a65: e65 / ag.pop * 100, wf, b50, n: ag.naggk };
  }).filter(Boolean);
}

register('trykkmatrise', (el, width) => {
  const s = spec(el);
  const data = regionRows();
  const wrap = document.createElement('div');
  wrap.className = 'nn-trykk';
  const bar = document.createElement('div');
  bar.className = 'nn-seg';
  bar.innerHTML = '<button type="button" data-v="matrise" aria-selected="true">Trykkmatrise</button><button type="button" data-v="rang" aria-selected="false">Rangering: arbeidsføre 2050</button><button type="button" data-v="byrde" aria-selected="false">Rangering: forsørgerbrøk 2050</button>';
  const legend = document.createElement('div');
  legend.className = 'nn-legend';
  legend.innerHTML = Object.entries(FY).map(([f, c]) => `<span><i style="background:${c};border-radius:50%;width:10px"></i>${f}</span>`).join('') + '<span class="nn-legend-note">Sirkelflate = folketall</span>';
  const H = Math.max(420, Math.min(520, width * 0.62));
  const m = { t: 18, r: 24, b: 46, l: 58 };
  const svg = d3.create('svg').attr('viewBox', `0 0 ${width} ${H}`).attr('width', width).attr('height', H)
    .attr('role', 'img').attr('aria-label', 'Regioner etter andel 65 år og over og endring i arbeidsføre mot 2050');
  const tip = document.createElement('div'); tip.className = 'nn-d3tip';
  wrap.append(bar, legend);
  const holder = document.createElement('div'); holder.style.position = 'relative';
  holder.append(svg.node(), tip);
  wrap.append(holder);

  const x = d3.scaleLinear([d3.min(data, d => d.a65) - 1.5, d3.max(data, d => d.a65) + 1.5], [m.l, width - m.r]);
  const y = d3.scaleLinear([d3.min(data, d => d.wf) - 1.5, Math.max(0, d3.max(data, d => d.wf) + 1)], [H - m.b, m.t]);
  const r = d3.scaleSqrt([0, d3.max(data, d => d.pop)], [0, Math.min(30, width / 30)]);
  const medX = d3.median(data, d => d.a65), medY = d3.median(data, d => d.wf);

  const quad = svg.append('rect').attr('fill', 'var(--neg)').attr('opacity', 0.09);
  const qtxt = svg.append('text').attr('fill', 'var(--neg)').style('font-size', '11.5px').attr('text-anchor', 'end');
  const gx = svg.append('g').attr('transform', `translate(0,${H - m.b})`);
  const gy = svg.append('g').attr('transform', `translate(${m.l},0)`);
  const xl = svg.append('text').attr('x', width - m.r).attr('y', H - 10).attr('text-anchor', 'end').style('font-size', '11.5px').attr('fill', 'var(--ink-2)');
  const yl = svg.append('text').attr('x', m.l).attr('y', 11).style('font-size', '11.5px').attr('fill', 'var(--ink-2)');
  const mx = svg.append('line').attr('stroke', 'var(--ink-3)').attr('stroke-dasharray', '2,3');
  const my = svg.append('line').attr('stroke', 'var(--ink-3)').attr('stroke-dasharray', '2,3');
  const g = svg.append('g').selectAll('g').data(data, d => d.id).join('g').style('cursor', 'pointer');
  g.append('circle').attr('r', d => r(d.pop)).attr('fill', d => FY[d.fylke]).attr('fill-opacity', 0.82).attr('stroke', 'var(--bg)').attr('stroke-width', 1.5);
  const lab = g.append('text').style('font-size', '11.5px').attr('fill', 'var(--ink)').attr('dy', '0.32em').text(d => d.navn);
  const val = g.append('text').style('font-size', '11.5px').style('font-variant-numeric', 'tabular-nums').attr('fill', 'var(--ink-2)').attr('dy', '0.32em').attr('text-anchor', 'end').attr('opacity', 0);

  g.on('pointermove', (e, d) => {
    const b = holder.getBoundingClientRect();
    tip.style.opacity = 1;
    tip.style.left = Math.min(e.clientX - b.left + 14, b.width - 210) + 'px';
    tip.style.top = (e.clientY - b.top + 12) + 'px';
    tip.innerHTML = `<b>${d.navn}</b> · ${d.fylke} · ${d.n} kommuner<br>Folketall: ${heltall(d.pop)}<br>65+ i dag: ${tall(d.a65, 1)} %<br>Arbeidsføre 2026–2050: ${endringPst(d.wf, 1)}<br>Forsørgerbrøk 2050: ${tall(d.b50, 0)}`;
  }).on('pointerleave', () => { tip.style.opacity = 0; })
    .on('click', () => { const t = document.getElementById('regTbl'); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); });

  const ax = (sel, axis) => sel.call(axis).call(a => { a.select('.domain').attr('stroke', 'var(--line)'); a.selectAll('line').remove(); a.selectAll('text').attr('fill', 'var(--ink-3)').style('font-size', '11px'); });
  const DUR = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 750;
  const tr = sel => sel.transition().duration(DUR).ease(d3.easeCubicInOut);

  function matrise() {
    tr(quad).attr('x', x(medX)).attr('y', y(medY)).attr('width', x.range()[1] - x(medX)).attr('height', y.range()[0] - y(medY)).attr('opacity', 0.09);
    tr(qtxt).attr('x', width - m.r - 6).attr('y', H - m.b - 8).attr('opacity', 1).text('Eldre enn medianen og større tap av arbeidsføre');
    tr(mx).attr('x1', x(medX)).attr('x2', x(medX)).attr('y1', m.t).attr('y2', H - m.b).attr('opacity', 1);
    tr(my).attr('x1', m.l).attr('x2', width - m.r).attr('y1', y(medY)).attr('y2', y(medY)).attr('opacity', 1);
    ax(tr(gx), d3.axisBottom(x).ticks(6).tickFormat(v => `${tall(v, 0)} %`));
    ax(tr(gy), d3.axisLeft(y).ticks(6).tickFormat(v => `${tall(v, 0)} %`));
    xl.text('Andel 65 år og over i dag →');
    yl.text('↑ Endring i arbeidsføre (20–64 år) 2026–2050, SSB MMMM');
    tr(g).attr('transform', d => `translate(${x(d.a65)},${y(d.wf)})`);
    tr(lab).attr('x', d => r(d.pop) + 5).attr('text-anchor', 'start');
    tr(val).attr('opacity', 0);
  }
  function rang(key) {
    const s2 = [...data].sort((a, b) => key === 'wf' ? a.wf - b.wf : b.b50 - a.b50);
    const yb = d3.scaleBand(s2.map(d => d.id), [m.t + 4, H - m.b]).padding(0.25);
    const dom = key === 'wf' ? [Math.min(0, d3.min(data, d => d.wf)) - 1, 0] : [0, d3.max(data, d => d.b50) + 4];
    const xr = d3.scaleLinear(dom, [m.l + 150, width - m.r - 60]);
    tr(quad).attr('opacity', 0); tr(qtxt).attr('opacity', 0);
    tr(mx).attr('opacity', 0); tr(my).attr('opacity', 0);
    ax(tr(gx), d3.axisBottom(xr).ticks(6).tickFormat(v => key === 'wf' ? `${tall(v, 0)} %` : tall(v, 0)));
    tr(gy).call(a => a.selectAll('*').remove());
    xl.text(key === 'wf' ? 'Endring i arbeidsføre 2026–2050 →' : 'Eldre per 100 i alderen 20–64 i 2050 →');
    yl.text(key === 'wf' ? 'Størst tap øverst' : 'Høyest forsørgerbrøk øverst');
    const v = d => key === 'wf' ? d.wf : d.b50;
    tr(g).attr('transform', d => `translate(${xr(v(d))},${yb(d.id) + yb.bandwidth() / 2})`);
    tr(lab).attr('x', d => m.l - xr(v(d)) + 4).attr('text-anchor', 'start');
    tr(val.text(d => key === 'wf' ? endringPst(d.wf, 1) : tall(d.b50, 0))).attr('x', d => -(r(d.pop) + 6)).attr('opacity', 1);
  }
  bar.addEventListener('click', e => {
    const b = e.target.closest('button[data-v]'); if (!b) return;
    bar.querySelectorAll('button').forEach(x2 => x2.setAttribute('aria-selected', String(x2 === b)));
    if (b.dataset.v === 'matrise') matrise(); else rang(b.dataset.v === 'rang' ? 'wf' : 'byrde');
  });
  matrise();
  if (s.view === 'rang') bar.querySelector('[data-v="rang"]').click();
  const src = document.createElement('div'); src.className = 'nn-source';
  src.textContent = 'Kilde: SSB 07459 (alder 1.1.2026) og 14746 (MMMM), aggregert til SØAs 13 regioner. Stiplede linjer = median for regionene.';
  wrap.append(src);
  return wrap;
});
