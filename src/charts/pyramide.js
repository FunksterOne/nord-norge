// Animert befolkningspyramide 2000–2050 (D3). Faktiske tall til siste 1. januar, deretter SSBs
// hovedalternativ. Spesifikasjon: { id:'nn'|'1804'|'troms'|'r-bodo', aar?:start, sammenlign?:år }
// Dataene ligger i data/pyramide/<id>.json og hentes først når diagrammet tegnes.
import * as d3 from 'd3';
import { register, spec } from './core.js';
import { heltall, tall } from '../lib/format.js';

const cache = new Map();
const hent = id => {
  if (!cache.has(id)) cache.set(id, fetch(`/data/pyramide/${encodeURIComponent(id)}.json`).then(r => (r.ok ? r.json() : Promise.reject(new Error(r.status)))));
  return cache.get(id);
};
const reduser = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
const ELDRE = 13; // indeks for 65–69: grupper fra og med denne er 65 år og over
const ARB = [4, 12]; // 20–24 til og med 60–64

function nøkkeltall(d, i) {
  const m = d.m[i], k = d.k[i];
  const sum = (a, b) => d3.sum(d3.range(a, b + 1), g => m[g] + k[g]);
  const tot = sum(0, m.length - 1);
  const e65 = sum(ELDRE, m.length - 1);
  const e80 = sum(16, m.length - 1);
  const arb = sum(ARB[0], ARB[1]);
  // Medianalder: lineær interpolasjon innenfor femårsgruppen der halvparten passeres
  let acc = 0, med = null;
  for (let g = 0; g < m.length; g++) {
    const n = m[g] + k[g];
    if (acc + n >= tot / 2) { med = g * 5 + (n ? ((tot / 2 - acc) / n) * 5 : 0); break; }
    acc += n;
  }
  return { tot, e65, e80, arb, andel65: (e65 / tot) * 100, andel80: (e80 / tot) * 100, byrde: (e65 / arb) * 100, med };
}

register('pyramide', (el, width) => {
  const s = spec(el);
  const id = s.id || 'nn';
  const wrap = document.createElement('div');
  wrap.className = 'nn-pyr';
  const compact = width < 640;
  const H = compact ? 330 : 380;
  wrap.style.minHeight = `${H + 120}px`;

  clearInterval(el.__pyrTimer);

  hent(id).then(d => {
    const n = d.aar.length;
    const ref = d.aar.indexOf(s.sammenlign || d.faktiskTil);
    let i = el.__pyrI ?? Math.max(0, d.aar.indexOf(s.aar || d.faktiskTil));

    // Kontroller
    const ctl = document.createElement('div'); ctl.className = 'nn-pyr-ctl';
    ctl.innerHTML = `<button type="button" class="nn-pyr-play" aria-label="Spill av">Spill av</button>
      <input type="range" min="0" max="${n - 1}" step="1" value="${i}" aria-label="Velg år">
      <div class="nn-pyr-aar"><b></b><span></span></div>`;
    const btn = ctl.querySelector('button'), sl = ctl.querySelector('input');
    const aarB = ctl.querySelector('.nn-pyr-aar b'), aarS = ctl.querySelector('.nn-pyr-aar span');

    const stats = document.createElement('div'); stats.className = 'nn-pyr-stats';

    const m = { t: 26, r: 8, b: 26, l: 8 };
    const midt = compact ? 40 : 52;
    const half = (width - m.l - m.r - midt) / 2;
    const maks = d3.max(d.aar, (_, j) => d3.max([...d.m[j], ...d.k[j]]));
    const x = d3.scaleLinear([0, maks * 1.04], [0, half]);
    const y = d3.scaleBand(d3.range(d.grupper.length).reverse(), [m.t, H - m.b]).paddingInner(0.18);
    const xM = v => m.l + half - x(v), xK = m.l + half + midt;

    const svg = d3.create('svg').attr('viewBox', `0 0 ${width} ${H}`).attr('width', width).attr('height', H)
      .attr('role', 'img').attr('aria-label', `Befolkningspyramide for ${d.navn}`);
    const farge = g => (g >= ELDRE ? 'var(--accent)' : 'var(--muted-mark)');

    // Akse (antall personer) under hver halvdel
    const ticks = x.ticks(compact ? 2 : 4).filter(t => t > 0);
    const ax = svg.append('g').attr('fill', 'var(--ink-3)').style('font-size', '10.5px').style('font-variant-numeric', 'tabular-nums');
    for (const t of ticks) {
      ax.append('line').attr('x1', xM(t)).attr('x2', xM(t)).attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--line-soft)');
      ax.append('line').attr('x1', xK + x(t)).attr('x2', xK + x(t)).attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--line-soft)');
      ax.append('text').attr('x', xM(t)).attr('y', H - 8).attr('text-anchor', 'middle').text(heltall(t));
      ax.append('text').attr('x', xK + x(t)).attr('y', H - 8).attr('text-anchor', 'middle').text(heltall(t));
    }
    svg.append('text').attr('x', m.l + half - 4).attr('y', 13).attr('text-anchor', 'end').attr('fill', 'var(--ink-2)').style('font-size', '12px').style('font-weight', 600).text('Menn');
    svg.append('text').attr('x', xK + 4).attr('y', 13).attr('fill', 'var(--ink-2)').style('font-size', '12px').style('font-weight', 600).text('Kvinner');

    const rader = d3.range(d.grupper.length);
    const bh = y.bandwidth();
    const barM = svg.append('g').selectAll('rect').data(rader).join('rect').attr('y', g => y(g)).attr('height', bh).attr('fill', farge);
    const barK = svg.append('g').selectAll('rect').data(rader).join('rect').attr('y', g => y(g)).attr('height', bh).attr('x', xK).attr('fill', farge);
    svg.append('g').selectAll('text').data(rader).join('text')
      .attr('x', m.l + half + midt / 2).attr('y', g => y(g) + bh / 2).attr('dy', '0.34em').attr('text-anchor', 'middle')
      .attr('fill', 'var(--ink-3)').style('font-size', compact ? '9.5px' : '10.5px').style('font-variant-numeric', 'tabular-nums')
      .text(g => (compact && g % 2 ? '' : d.grupper[g]));

    // Omriss for sammenligningsåret
    const omriss = (side, arr) => {
      const p = d3.path();
      rader.forEach(g => {
        const v = arr[g];
        const x0 = side === 'm' ? xM(v) : xK + x(v);
        p.moveTo(x0, y(g)); p.lineTo(x0, y(g) + bh);
      });
      return p.toString();
    };
    if (ref >= 0) {
      svg.append('path').attr('d', omriss('m', d.m[ref])).attr('stroke', 'var(--ink)').attr('stroke-width', 1.5).attr('fill', 'none');
      svg.append('path').attr('d', omriss('k', d.k[ref])).attr('stroke', 'var(--ink)').attr('stroke-width', 1.5).attr('fill', 'none');
    }

    const tip = document.createElement('div'); tip.className = 'nn-d3tip';
    const holder = document.createElement('div'); holder.style.position = 'relative';
    holder.append(svg.node(), tip);
    const vis = (ev, g, kj) => {
      const v = (kj === 'm' ? d.m : d.k)[i][g], tot = d3.sum(d.m[i]) + d3.sum(d.k[i]);
      const r0 = ref >= 0 ? (kj === 'm' ? d.m : d.k)[ref][g] : null;
      tip.innerHTML = `<b>${kj === 'm' ? 'Menn' : 'Kvinner'} ${d.grupper[g]} år, ${d.aar[i]}</b><br>${heltall(v)} personer (${tall((v / tot) * 100, 1)} % av alle)${r0 != null && ref !== i ? `<br>${d.aar[ref]}: ${heltall(r0)}` : ''}`;
      const b = holder.getBoundingClientRect();
      tip.style.left = `${Math.min(ev.clientX - b.left + 12, b.width - 200)}px`;
      tip.style.top = `${ev.clientY - b.top - 10}px`;
      tip.style.opacity = 1;
    };
    barM.on('pointermove', (ev, g) => vis(ev, g, 'm')).on('pointerleave', () => { tip.style.opacity = 0; });
    barK.on('pointermove', (ev, g) => vis(ev, g, 'k')).on('pointerleave', () => { tip.style.opacity = 0; });

    const legend = document.createElement('div'); legend.className = 'nn-legend';
    legend.innerHTML = `<span><i style="background:var(--muted-mark)"></i>Under 65 år</span><span><i style="background:var(--accent)"></i>65 år og over</span>${ref >= 0 ? `<span><i style="background:transparent;border-left:1.5px solid var(--ink);width:2px"></i>Omriss: ${d.aar[ref] === d.faktiskTil ? `1. januar ${d.aar[ref]}` : d.aar[ref]}</span>` : ''}`;
    const src = document.createElement('div'); src.className = 'nn-source';
    src.textContent = `Kilde: ${d.kilde}. Kommuneinndeling per 2024. Framskrivingen viser hva dagens trender gir, ikke en prognose.`;

    const k0 = nøkkeltall(d, ref >= 0 ? ref : 0);
    const tittel = el.closest('section, .card, .exhibit')?.querySelector('[data-pyr-tittel]');
    if (tittel) {
      const a = nøkkeltall(d, 0), b = nøkkeltall(d, n - 1);
      const tekst = `Andelen 65 år og over i ${d.navn} går fra ${tall(a.andel65, 1)} % i ${d.aar[0]} til ${tall(b.andel65, 1)} % i ${d.aar[n - 1]}`;
      tittel.textContent = tekst;
    }
    const oppdater = (anim) => {
      const dur = anim && !reduser() ? 260 : 0;
      barM.transition().duration(dur).ease(d3.easeCubicOut).attr('x', g => xM(d.m[i][g])).attr('width', g => x(d.m[i][g]));
      barK.transition().duration(dur).ease(d3.easeCubicOut).attr('width', g => x(d.k[i][g]));
      const fram = d.aar[i] > d.faktiskTil;
      barM.attr('fill-opacity', fram ? 0.78 : 1); barK.attr('fill-opacity', fram ? 0.78 : 1);
      aarB.textContent = d.aar[i];
      aarS.textContent = fram ? 'Framskrevet, SSBs hovedalternativ' : d.aar[i] === d.faktiskTil ? 'Faktisk, siste tall (1. januar)' : 'Faktisk (1. januar)';
      aarS.classList.toggle('fram', fram);
      sl.value = i;
      const kt = nøkkeltall(d, i);
      const diff = (a, b, f) => (ref >= 0 && i !== ref ? `<em>${a - b >= 0 ? '+' : '−'}${f(Math.abs(a - b))} mot ${d.aar[ref]}</em>` : '<em>&nbsp;</em>');
      stats.innerHTML = `
        <div><span>Folketall</span><b>${heltall(kt.tot)}</b>${diff(kt.tot, k0.tot, heltall)}</div>
        <div><span>65 år og over</span><b>${tall(kt.andel65, 1)} %</b>${diff(kt.andel65, k0.andel65, v => `${tall(v, 1)} pp`)}</div>
        <div><span>80 år og over</span><b>${tall(kt.andel80, 1)} %</b>${diff(kt.andel80, k0.andel80, v => `${tall(v, 1)} pp`)}</div>
        <div><span>Eldre per 100 i alderen 20–64</span><b>${tall(kt.byrde, 0)}</b>${diff(kt.byrde, k0.byrde, v => tall(v, 0))}</div>
        <div><span>Medianalder</span><b>${tall(kt.med, 1)} år</b>${diff(kt.med, k0.med, v => `${tall(v, 1)} år`)}</div>`;
      el.__pyrI = i;
    };

    const stopp = () => { clearInterval(el.__pyrTimer); el.__pyrTimer = null; btn.textContent = 'Spill av'; btn.setAttribute('aria-label', 'Spill av'); };
    const start = () => {
      if (i >= n - 1) i = 0;
      btn.textContent = 'Pause'; btn.setAttribute('aria-label', 'Pause');
      el.__pyrTimer = setInterval(() => {
        if (i >= n - 1) { stopp(); return; }
        i++; oppdater(true);
      }, reduser() ? 600 : 280);
    };
    btn.addEventListener('click', () => (el.__pyrTimer ? stopp() : start()));
    sl.addEventListener('input', () => { stopp(); i = +sl.value; oppdater(true); });

    const topp = document.createElement('div'); topp.className = 'nn-pyr-topp';
    topp.append(ctl);
    wrap.replaceChildren(topp, stats, holder, legend, src);
    wrap.style.minHeight = '';
    oppdater(false);
  }).catch(err => {
    wrap.textContent = 'Befolkningspyramiden kunne ikke lastes.';
    console.error('Pyramide', id, err);
  });
  return wrap;
});
