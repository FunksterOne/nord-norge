// Kommunekart (koroplet / proporsjonale sirkler) for de 80 kommunene.
// Spesifikasjon: { ind, highlight, fylke, controls, height, noclick }
import { Plot, register, spec, redraw } from './core.js';
import { feature, merge, mesh } from 'topojson-client';
import { L } from '../lib/legacy.js';
import { tall, heltall, endringPst, prosent, kortNavn } from '../lib/format.js';

let topo = null;
let topoP = null;
function loadTopo() {
  if (!topoP) topoP = fetch(new URL('/geo/nn-kommuner.json', location.origin)).then(r => r.json()).then(t => (topo = t));
  return topoP;
}
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

function robekStatus(nr) {
  const R = L.DATA?.proj?.robek;
  if (!R) return 'ukjent';
  if (R.kommuner && R.kommuner[nr]) return 'i';
  if (R.pending && R.pending[nr]) return 'pend';
  return 'ikke';
}

export const INDIKATORER = {
  endring: {
    navn: 'Folketall 2026–2050', kort: 'Endring mot 2050',
    enhet: 'Endring i folketall 2026–2050, SSB hovedalternativ (MMMM)',
    verdi: k => { const o = L.DATA.proj.kommuner[k.nr]; return o ? (o.main[o.main.length - 1] / o.main[0] - 1) * 100 : null; },
    fmt: v => endringPst(v, 1), type: 'diverging',
  },
  eldre: {
    navn: 'Andel 65+', kort: 'Andel 65 år og over',
    enhet: 'Andel av befolkningen 65 år og over, 1.1.2026',
    verdi: k => k.alder.slice(65).reduce((a, b) => a + b, 0) / k.pop * 100,
    fmt: v => prosent(v, 1), type: 'sequential',
  },
  forsorg: {
    navn: 'Forsørgerbrøk 2050', kort: 'Forsørgerbrøk 2050',
    enhet: 'Personer 65+ per 100 i alderen 20–64 i 2050, SSB MMMM',
    verdi: k => { const o = L.DATA.proj.kommuner[k.nr]; const n = o?.a65?.length; return n ? o.a65[n - 1] / o.a2064[n - 1] * 100 : null; },
    fmt: v => tall(v, 0), type: 'sequential',
  },
  innv: {
    navn: 'Innvandrerbakgrunn', kort: 'Innvandrerbakgrunn',
    enhet: 'Innvandrere og norskfødte med innvandrerforeldre, andel av folketallet',
    verdi: k => k.andel, fmt: v => prosent(v, 1), type: 'sequential',
  },
  folketall: {
    navn: 'Folketall', kort: 'Folketall',
    enhet: 'Folketall 1.1.2026 — sirkelflaten er proporsjonal med folketallet',
    verdi: k => k.pop, fmt: v => heltall(v), type: 'size',
  },
  kryss: {
    navn: 'Flere eldre enn unge', kort: 'År da 67+ passerer 18–34',
    enhet: 'Første år med flere innbyggere 67 år og over enn 18–34 år. SSB 07459 (faktisk fra 2020) og 14746 hovedalternativet (MMMM)',
    verdi: k => { const o = L.UNG?.kommuner?.[String(k.nr)]; if (!o) return null; return o.kryss === 'før 2020' ? 2019 : o.kryss == null ? 2051 : o.kryss; },
    fmt: v => (v <= 2019 ? 'før 2020' : v >= 2051 ? 'ikke innen 2050' : String(v)), type: 'sequential',
    skjult: true, rangTitler: ['Senest', 'Tidligst'], utenStolpe: true,
  },
  botid10: {
    navn: 'Botid 10 år eller mer', kort: 'Innvandrere med botid minst 10 år',
    enhet: 'Andel av innvandrerne med ti års botid i Norge eller mer, 1.1.2026. IMDi (kilde SSB)',
    verdi: k => { const o = L.BOFAST?.botid10?.kommuner?.[String(k.nr)]; return o ? o[3] : null; },
    fmt: v => prosent(v, 1), type: 'sequential',
    kilde: 'Kilde: IMDi «Innvandrernes botid» (kilde SSB), alle innvandrere.',
    skjult: true,
  },
  bos2027: {
    navn: 'Bosetting 2027', kort: 'Anmodet bosatt i 2027, per 1 000 innbyggere',
    enhet: 'IMDis anmodning om bosetting av flyktninger i 2027, per 1 000 innbyggere (1.1.2026). Lyseste farge: ikke anmodet',
    verdi: k => { const o = L.BOFAST?.anmodning?.kommuner?.[String(k.nr)]; return o ? o[0] / k.pop * 1000 : null; },
    fmt: v => (v === 0 ? '0' : tall(v, 1)), akse: v => tall(v, 0), type: 'sequential',
    kilde: 'Kilde: IMDi, anmodning om bosetting per kommune 2027 (23.10.2026). Anmodning, ikke vedtak.',
    skjult: true,
  },
  okon: {
    navn: 'Ikke-sysselsatte per 100 sysselsatte', kort: 'Ikke-sysselsatte per 100 sysselsatte',
    enhet: 'Innbyggere som ikke er i arbeid (alle aldre) per 100 sysselsatte, 4. kvartal 2025',
    verdi: k => { const r = L.FORSORG?.regioner?.[String(k.nr)]; return r ? (r.bef.tot - r.s15[1]) / r.s15[1] * 100 : null; },
    fmt: v => tall(v, 1), type: 'sequential',
    kilde: 'Kilde: SSB 13563 (arbeidsstyrkestatus, bosted) og 07459 (fetch_forsorg.py).',
    skjult: true,
  },
  aapufo: {
    navn: 'AAP og uføretrygd', kort: 'AAP eller uføretrygd, 20–66 år',
    enhet: 'Andel av innbyggerne 20–66 år som mottar arbeidsavklaringspenger eller uføretrygd, 4. kvartal 2025',
    verdi: k => { const r = L.FORSORG?.regioner?.[String(k.nr)]; return r ? r.s2066[5] / r.s2066[0] * 100 : null; },
    fmt: v => prosent(v, 1), type: 'sequential',
    kilde: 'Kilde: SSB 13563 (fetch_forsorg.py).',
    skjult: true,
  },
  syssEndr: {
    navn: 'Sysselsatte 2026–2050', kort: 'Endring i sysselsatte 2026–2050',
    enhet: 'Endring i antall sysselsatte bosatte 2026–2050 med dagens sysselsetting per aldersgruppe og SSBs hovedalternativ',
    verdi: k => { const r = L.FORSORG?.regioner?.[String(k.nr)]; return r ? (r.syss[r.syss.length - 1] / r.syss[0] - 1) * 100 : null; },
    fmt: v => endringPst(v, 1), type: 'diverging',
    kilde: 'Kilde: egen beregning fra SSB 07984, 13563 og 14746 (fetch_forsorg.py).',
    skjult: true,
  },
  omsorg2050: {
    navn: 'Omsorgsårsverk 2050', kort: 'Omsorgsårsverk per 100 i alderen 20–64, 2050',
    enhet: 'Omsorgsårsverk som trengs i 2050 «alt annet likt», per 100 innbyggere i alderen 20–64 år',
    verdi: k => { const o = L.ELDRE?.kommuner?.[String(k.nr)]; return o && o[12] != null ? o[12] / o[8] * 100 : null; },
    fmt: v => tall(v, 1), type: 'sequential',
    kilde: 'Kilde: egen beregning fra SSB 14746, 14534, 12003 og 07459 (fetch_eldre.py).',
    skjult: true,
  },
  robek: {
    navn: 'ROBEK', kort: 'ROBEK-status',
    enhet: 'Kommuner registrert i ROBEK (kommuneloven § 28-1)',
    verdi: k => robekStatus(k.nr), fmt: v => ({ i: 'Registrert i ROBEK', pend: 'Innmelding under behandling', ikke: 'Ikke registrert', ukjent: '–' })[v], type: 'cat',
  },
};

function colorScale(def, values) {
  const nums = values.filter(v => typeof v === 'number' && Number.isFinite(v));
  if (def.type === 'diverging') {
    const m = Math.max(...nums.map(Math.abs));
    const lim = Math.ceil(m / 5) * 5;
    return { type: 'diverging', domain: [-lim, lim], pivot: 0, range: [css('--neg'), css('--panel'), css('--pos')], interpolate: 'lab', legend: true, tickFormat: v => endringPst(v, 0), label: null };
  }
  if (def.type === 'sequential') {
    const lo = Math.min(...nums), hi = Math.max(...nums);
    return { type: 'linear', domain: [lo, hi], range: [css('--line'), css('--accent')], interpolate: 'lab', legend: true, tickFormat: def.akse || (v => def.fmt(v).replace(/,0 %$/, ' %')), label: null };
  }
  if (def.type === 'cat') {
    return { domain: ['i', 'pend', 'ikke'], range: [css('--neg'), css('--warn'), css('--line')], legend: true, tickFormat: v => def.fmt(v), label: null };
  }
  return null;
}

function render(el, width) {
  const s = spec(el);
  if (!topo) {
    loadTopo().then(() => redraw(el));
    const p = document.createElement('div'); p.className = 'nn-chart-note'; p.textContent = 'Laster kart …';
    return p;
  }
  const ind = s.ind && INDIKATORER[s.ind] ? s.ind : 'endring';
  const def = INDIKATORER[ind];
  const geoAll = feature(topo, topo.objects.nn);
  const byNr = new Map(L.K.map(k => [k.nr, k]));
  for (const f of geoAll.features) {
    const k = byNr.get(f.properties.nr);
    f.properties.k = k;
    f.properties.v = k ? def.verdi(k) : null;
    f.properties.region = L.KREGION[String(f.properties.nr)] || null;
  }
  const focus = s.fylke && s.fylke !== 'Alle' ? geoAll.features.filter(f => f.properties.k?.fylke === s.fylke) : geoAll.features;
  const focusFC = { type: 'FeatureCollection', features: focus };
  const side = s.side !== false && width >= 760;
  const mapW = side ? Math.round(width * 0.6) : width;
  const height = s.height || Math.round(Math.min(720, Math.max(380, mapW * (s.fylke && s.fylke !== 'Alle' ? 0.95 : 1.12))));

  // Regiongrenser som sammenslåtte flater
  const regionMesh = mesh(topo, topo.objects.nn, (a, b) => a !== b && (L.KREGION[String(a.properties.nr)] !== L.KREGION[String(b.properties.nr)]));
  const fylkeMesh = mesh(topo, topo.objects.nn, (a, b) => a !== b && (String(a.properties.nr).slice(0, 2) !== String(b.properties.nr).slice(0, 2)));
  const outline = merge(topo, topo.objects.nn.geometries);

  const scale = colorScale(def, geoAll.features.map(f => f.properties.v));
  const hl = s.highlight ? geoAll.features.find(f => f.properties.nr === s.highlight) : null;
  const centroids = geoAll.features.map(f => ({ ...f.properties, f }));
  const tipText = d => {
    const k = d.k; if (!k) return d.navn;
    const regNavn = (L.REGIONS.find(r => r.id === d.region) || {}).navn;
    return `${k.navn}\n${def.kort}: ${def.fmt(d.v)}\n${k.fylke}${regNavn ? ' · ' + regNavn : ''}\nFolketall: ${heltall(k.pop)}`;
  };

  const isSize = def.type === 'size';
  const marks = [
    Plot.geo(geoAll, {
      fill: isSize ? css('--panel') : (f => f.properties.v == null ? css('--panel') : f.properties.v),
      stroke: css('--bg'), strokeWidth: 0.6,
      fillOpacity: f => (s.fylke && s.fylke !== 'Alle' && f.properties.k?.fylke !== s.fylke) ? 0.25 : 1,
    }),
    Plot.geo(regionMesh, { stroke: css('--ink-3'), strokeWidth: 0.9, strokeOpacity: 0.8 }),
    Plot.geo(fylkeMesh, { stroke: css('--ink-2'), strokeWidth: 1.4 }),
    Plot.geo(outline, { stroke: css('--ink-3'), strokeWidth: 0.6 }),
    isSize && Plot.dot(centroids, Plot.centroid({ geometry: d => d.f, r: d => d.v, fill: css('--accent'), fillOpacity: 0.55, stroke: css('--accent-text'), strokeWidth: 0.8 })),
    hl && Plot.geo([hl], { stroke: css('--accent-text'), strokeWidth: 2.8, fill: 'none' }),
    Plot.tip(centroids, Plot.pointer(Plot.centroid({ geometry: d => d.f, title: tipText, fill: css('--raised'), stroke: css('--line'), textPadding: 9, fontSize: 12 }))),
  ].filter(Boolean);

  const fig = Plot.plot({
    width: mapW, height,
    projection: { type: 'transverse-mercator', rotate: [-17, -66], domain: focusFC, inset: 8 },
    color: scale || undefined,
    r: isSize ? { range: [1.5, Math.max(14, width / 26)] } : undefined,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', color: 'var(--ink-3)', fontSize: '12px', overflow: 'hidden' },
    marks,
  });
  const svg = fig.tagName === 'svg' ? fig : fig.querySelector('svg');
  if (svg) {
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', `Kart over kommunene i Nord-Norge: ${def.enhet}`);
  }
  if (!s.noclick) {
    fig.style.cursor = 'pointer';
    fig.addEventListener('click', () => { const v = fig.value; if (v && v.nr) location.href = `kommune.html?k=${v.nr}`; });
  }

  const out = [];
  if (s.controls) {
    const bar = document.createElement('div');
    bar.className = 'nn-seg';
    bar.setAttribute('role', 'tablist');
    bar.innerHTML = Object.entries(INDIKATORER).filter(([key, d]) => !d.skjult || key === ind).map(([key, d]) =>
      `<button type="button" role="tab" data-ind="${key}" aria-selected="${key === ind}">${d.navn}</button>`).join('');
    bar.addEventListener('click', e => {
      const b = e.target.closest('button[data-ind]'); if (!b) return;
      el.dataset.spec = JSON.stringify({ ...s, ind: b.dataset.ind });
      redraw(el);
    });
    out.push(bar);
  }
  const cap = document.createElement('div'); cap.className = 'nn-chart-note'; cap.textContent = def.enhet + '.';
  out.push(cap);
  if (side || s.rank) {
    const grid = document.createElement('div');
    grid.className = 'nn-kart-grid';
    const left = document.createElement('div'); left.appendChild(fig);
    grid.append(left, rankPanel(def, ind, geoAll.features, s));
    out.push(grid);
  } else out.push(fig);
  const src = document.createElement('div'); src.className = 'nn-source';
  src.textContent = (def.kilde || 'Kilde: SSB (folketall, framskriving 14746, innvandring 09817), KDD (ROBEK).') + ' Kart: Kartverket, CC BY 4.0. Tykk linje = fylkesgrense, tynn = regiongrense (SØA 2026).';
  out.push(src);
  return out;
}

function rankPanel(def, ind, features, s) {
  const box = document.createElement('div');
  box.className = 'nn-rank';
  const rows = features.map(f => f.properties).filter(d => d.k && d.v != null && (!s.fylke || s.fylke === 'Alle' || d.k.fylke === s.fylke));
  if (def.type === 'cat') {
    const inR = rows.filter(d => d.v === 'i').sort((a, b) => b.k.pop - a.k.pop);
    const pend = rows.filter(d => d.v === 'pend');
    const R = L.DATA?.proj?.robek || {};
    box.innerHTML = `<div class="nn-rank-h">${inR.length} av ${rows.length} kommuner i ROBEK</div>
      <div class="nn-rank-sub">Per ${R.oppdatert || '–'}${pend.length ? ` · ${pend.length} under behandling` : ''}</div>
      <ol class="nn-rank-list">${inR.map(d => `<li><a href="kommune.html?k=${d.nr}">${kortNavn(d.k.navn)}</a><span>${(R.kommuner[d.nr] || '').toUpperCase()}</span></li>`).join('')}</ol>`;
    return box;
  }
  rows.sort((a, b) => b.v - a.v);
  const max = Math.max(...rows.map(d => Math.abs(d.v)));
  const li = d => {
    const w = Math.max(2, Math.abs(d.v) / max * 100);
    const col = def.type === 'diverging' ? (d.v < 0 ? 'var(--neg)' : 'var(--pos)') : 'var(--accent)';
    const bar = def.utenStolpe ? '<span class="nn-rank-bar"></span>' : `<span class="nn-rank-bar"><i style="width:${w}%;background:${col}"></i></span>`;
    return `<li><a href="kommune.html?k=${d.nr}">${kortNavn(d.k.navn)}</a>${bar}<span class="num">${def.fmt(d.v)}</span></li>`;
  };
  const [hoy, lav] = def.rangTitler || ['Høyest', 'Lavest'];
  box.innerHTML = `<div class="nn-rank-h">${hoy}</div><ol class="nn-rank-list">${rows.slice(0, 6).map(li).join('')}</ol>
    <div class="nn-rank-h">${lav}</div><ol class="nn-rank-list">${rows.slice(-6).reverse().map(li).join('')}</ol>
    <div class="nn-rank-sub">${rows.length} kommuner. Navn er klikkbare.</div>`;
  return box;
}

register('kart', render);
// Kartfarger er beregnet fra temaet; tegn på nytt ved temabytte.
window.addEventListener('nn:tema', () => document.querySelectorAll('[data-nnchart="kart"]').forEach(redraw));
