// Sammenligningssiden (sammenlign.html): 2–4 kommuner ved siden av hverandre.
// 01 topp med fast farge per kommune · 02 profil med én prikk per kommune · 03 tabell med samme indikator på
// samme rad, Nord-Norge og landet som referanse · 04 tre figurer på felles akse · 05 regelbasert sammendrag.
// Tallene hentes fra de samme datablokkene og beregningene som kommunesidene og kartlagene (INDIKATORER).
// Ingen farger for «bra» eller «dårlig»: retningen er ikke opplagt for alle indikatorene.
import { L } from './legacy.js';
import { INDIKATORER as I } from '../charts/map.js';
import { placeholder } from '../charts/core.js';
import { tall, heltall, kortNavn } from './format.js';
import { indikatorer, plassering } from './profil.js';

export const FARGER = ['var(--cat-1)', 'var(--cat-5)', 'var(--cat-3)', 'var(--cat-6)'];
const FARGENAVN = ['cat-1', 'cat-5', 'cat-3', 'cat-6'];

const p1 = v => (v == null ? '–' : `${tall(v, 1)} %`);
const fortegn = v => (v == null ? '–' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${tall(Math.abs(v), 1)} %`);
const kr = v => (v == null ? '–' : `${heltall(v)} kr`);
const t0 = v => (v == null ? '–' : tall(v, 0));
const ok = v => (v == null || (typeof v === 'number' && !Number.isFinite(v)) ? null : v);

function median(arr) { let t = arr.reduce((a, b) => a + b, 0), c = 0; for (let i = 0; i < arr.length; i++) { c += arr[i]; if (c >= t / 2) return i; } return 0; }
const proj = k => L.DATA?.proj?.kommuner?.[k.nr];
const fbAar = (k, i) => { const o = proj(k); return o && o.a2064?.[i] ? o.a65[i] / o.a2064[i] * 100 : null; };
const rate = x => (x && x.tot[x.tot.length - 1] ? x.syss[x.syss.length - 1] / x.tot[x.tot.length - 1] * 100 : null);

// Største næring blant dem med tall (siste år)
function storstNaering(arb) {
  const N = L.NAERINGK; if (!N || !arb) return null;
  const i = N.aar.length - 1, tot = arb['00-99']?.[i];
  const r = N.naeringer.filter(([k]) => k !== '00' && arb[k]?.[i] != null).sort((a, b) => arb[b[0]][i] - arb[a[0]][i])[0];
  return r && tot ? { navn: r[1], andel: arb[r[0]][i] / tot * 100, skjult: N.naeringer.some(([k]) => k !== '00' && arb[k]?.[i] == null) } : null;
}
// Mest særpregede næring: høyest andel i forhold til landet (minst 3 % av arbeidsplassene)
function saerpreg(arb) {
  const N = L.NAERINGK; if (!N || !arb) return null;
  const i = N.aar.length - 1, tot = arb['00-99']?.[i], la = N.landet.arb, laT = la['00-99'][i];
  const r = N.naeringer.filter(([k]) => k !== '00' && arb[k]?.[i] != null && la[k]?.[i])
    .map(([k, n]) => ({ navn: n, andel: arb[k][i] / tot * 100, andelL: la[k][i] / laT * 100 }))
    .filter(x => x.andel >= 3).sort((a, b) => b.andel / b.andelL - a.andel / a.andelL)[0];
  return r || null;
}
const kortN = n => n.replace(/ og sosialtjenester$/, '').replace(/, skogbruk og fiske$/, ' og fiske');
const saerTekst = s => (s ? `${kortN(s.navn)} (${tall(s.andel, 0)} % mot ${tall(s.andelL, 0)} %)` : '–');
const naeringTekst = s => (s ? `${kortN(s.navn)} (${tall(s.andel, 0)} %)${s.skjult ? '†' : ''}` : '–');

// Skattevekst for en månedsserie: siste måned med tall i år mot samme måned i fjor
function vekst(s) {
  const S = L.SKATT; if (!S || !s) return null;
  const a = +S.siste_mnd.slice(0, 4), i = s[a], f = s[a - 1]; if (!i || !f) return null;
  const m = i.reduce((x, v, j) => (v != null ? j : x), -1);
  return m >= 0 && f[m] ? (i[m] / f[m] - 1) * 100 : null;
}

// Radene i tabellen. v(k): verdi for en kommune; nn()/la(): referanser (null = finnes ikke på samme grunnlag)
function rader() {
  const S = L.SKATT, N = L.NAERINGK, SY = L.SYSSN, NAV = L.NAVK, P = L.PENDLING, PE = L.PENSJON;
  const nnK = L.AGG?.[-1];
  const ka = S ? String(S.kostra_aar[S.kostra_aar.length - 1]) : '';
  const kostra = (k, f) => { const o = L.DATA?.proj?.kostra?.[k.nr]; return o && o[f] != null ? +o[f] : null; };
  const ft = typeof FYLKE_TALL !== 'undefined' ? FYLKE_TALL.verdier : null; // eslint-disable-line no-undef
  const R = L.DATA?.proj?.robek || {};
  const navAar = NAV?.meta || {};
  const nnPend = P?.fylker?.NN;
  const ni = N ? N.aar.length - 1 : 0;
  return [
    ['Befolkning', [
      // Ferskeste kvartal (SSB 01222), som «Folketall i dag» på kommunesiden; øvrige befolkningstall er per 1.1.2026
      { navn: 'Folketall', meta: L.BEFK ? `per ${L.BEFK.dato_norsk}` : '1.1.2026', v: k => L.BEFK?.kommuner?.[k.nr] ?? k.pop, fmt: heltall, nn: () => L.BEFK?.landsdel ?? L.K.reduce((s, k) => s + k.pop, 0) },
      { navn: 'Endring i folketall 2026–2050', meta: 'SSB hovedalternativ', v: k => I.endring.verdi(k), fmt: fortegn, nn: () => nnK && I.endring.verdi(nnK) },
      { navn: 'Andel 65 år og over', meta: '1.1.2026', v: k => I.eldre.verdi(k), fmt: p1, nn: () => nnK && I.eldre.verdi(nnK) },
      { navn: 'Medianalder', meta: '1.1.2026', v: k => median(k.alder), fmt: t0, nn: () => nnK && median(nnK.alder) },
      { navn: 'Forsørgerbrøk i dag', meta: '65+ per 100 i alderen 20–64, 2026', v: k => fbAar(k, 0), fmt: t0, nn: () => nnK && fbAar(nnK, 0), la: () => L.FORSORG?.regioner?.landet?.demo?.[0] },
      { navn: 'Forsørgerbrøk 2050', meta: 'SSB hovedalternativ', v: k => I.forsorg.verdi(k), fmt: t0, nn: () => nnK && I.forsorg.verdi(nnK) },
      { navn: 'Innvandrerbakgrunn', meta: 'andel av folketallet', v: k => k.andel, fmt: p1, nn: () => nnK?.andel },
    ]],
    ['Arbeid', [
      { navn: 'Sysselsatte 20–66 år', meta: '4. kvartal 2025', v: k => k.syss?.rate?.tot, fmt: p1, nn: () => SY && rate(SY.nivaa.NN), la: () => SY && rate(SY.nivaa.landet) },
      { navn: 'Innvandrere i arbeid, 20–66 år', meta: '4. kvartal 2025', v: k => k.syss?.rate?.zzz, fmt: p1, nn: () => SY && rate(SY.nivaa.NN.innv), la: () => SY && rate(SY.nivaa.landet.innv) },
      { navn: 'Helt ledige', meta: `NAV, årssnitt ${navAar.ledige ?? ''}`, v: k => NAV?.kommuner?.[String(k.nr)]?.ledige, fmt: p1, nn: () => NAV?.ref?.NN?.ledige, la: () => NAV?.ref?.landet?.ledige },
      { navn: 'Uføretrygd, 18–67 år', meta: `NAV, ${String(navAar.ufore ?? '').slice(0, 4)}`, v: k => NAV?.kommuner?.[String(k.nr)]?.ufore, fmt: p1, nn: () => NAV?.ref?.NN?.ufore, la: () => NAV?.ref?.landet?.ufore },
      { navn: 'Netto pendling', meta: 'inn minus ut, % av sysselsatte bosatte', v: k => I.pendNetto.verdi(k), fmt: fortegn, nn: () => nnPend && (nnPend.inn.at(-1) - nnPend.ut.at(-1)) / nnPend.bosatte.at(-1) * 100 },
      { navn: 'Arbeidsplasser, endring', meta: N ? `${N.aar[0]}–${N.aar[ni]}` : '', v: k => I.arbVekst.verdi(k), fmt: fortegn,
        nn: () => N && (N.NN.arb['00-99'][ni] / N.NN.arb['00-99'][0] - 1) * 100, la: () => N && (N.landet.arb['00-99'][ni] / N.landet.arb['00-99'][0] - 1) * 100 },
      { navn: 'Største næring', meta: 'andel av arbeidsplassene', tekst: true, v: k => naeringTekst(storstNaering(N?.kommuner?.[String(k.nr)]?.arb)), nn: () => naeringTekst(storstNaering(N?.NN?.arb)), la: () => naeringTekst(storstNaering(N?.landet?.arb)) },
      { navn: 'Mest særpregede næring', meta: 'andel mot landet, minst 3 % av arbeidsplassene', tekst: true, v: k => saerTekst(saerpreg(N?.kommuner?.[String(k.nr)]?.arb)), nn: () => saerTekst(saerpreg(N?.NN?.arb)) },
    ]],
    ['Økonomi', [
      { navn: 'Skatt per innbygger', meta: `inntekt og formue, ${ka}`, v: k => S?.kostra?.kommuner?.[String(k.nr)]?.skatt?.[ka], fmt: kr, nn: () => S?.kostra?.fylker?.NN?.skatt?.[ka], la: () => S?.kostra?.landet?.skatt?.[ka] },
      { navn: 'Frie inntekter per innbygger', meta: `skatt og rammetilskudd, ${ka}`, v: k => S?.kostra?.kommuner?.[String(k.nr)]?.frie?.[ka], fmt: kr, nn: () => S?.kostra?.fylker?.NN?.frie?.[ka], la: () => S?.kostra?.landet?.frie?.[ka] },
      { navn: 'Skatteinngang i år', meta: 'endring mot samme periode i fjor', v: k => I.skatteVekst.verdi(k), fmt: fortegn, nn: () => vekst(S?.inngang?.fylker?.NN), la: () => vekst(S?.inngang?.landet) },
      { navn: 'Netto driftsresultat', meta: `% av driftsinntektene, ${ka}`, v: k => kostra(k, 'ndr'), fmt: p1, nn: () => ft?.ndr?.['nord-norge'], la: () => ft?.ndr?.landet },
      { navn: 'Disposisjonsfond', meta: `% av driftsinntektene, ${ka}`, v: k => kostra(k, 'fond'), fmt: p1 },
      { navn: 'Premieavvik, akkumulert', meta: '% av driftsinntektene, 2025', v: k => PE?.kommuner?.[String(k.nr)]?.pa, fmt: p1, la: () => PE?.meta?.landet_pa },
      { navn: 'ROBEK', meta: 'statlig kontroll av økonomien', tekst: true,
        v: k => (R.kommuner?.[k.nr] ? 'Registrert' : R.pending?.[k.nr] ? 'Innmelding behandles' : 'Nei'),
        nn: () => `${Object.keys(R.kommuner || {}).length} av 80` },
    ]],
  ];
}

// 02 Profil: én rad per indikator, én prikk per kommune
function profil(ks) {
  let gruppe = '';
  return '<div class="nn-cmp-pr">' +
    '<div class="nn-cmp-pr-rad akse"><span></span><span class="nn-pr-akse-t"><span>lavest</span><span>median</span><span>høyest</span></span></div>' +
    indikatorer().map(d => {
      const pl = ks.map(k => plassering(k.nr, d));
      if (pl.every(x => !x)) return '';
      const hode = d.gruppe !== gruppe ? `<div class="nn-pr-gruppe">${(gruppe = d.gruppe)}</div>` : '';
      const tittel = ks.map((k, i) => (pl[i] ? `${kortNavn(k.navn)}: ${d.tekst(pl[i].v)}, ${pl[i].setning}` : `${kortNavn(k.navn)}: mangler tall`)).join(' · ');
      const prikker = pl.map((x, i) => (x ? `<i class="prikk" style="left:${x.p.toFixed(1)}%;background:${FARGER[i]};z-index:${4 - i}"></i>` : '')).join('');
      return `${hode}<div class="nn-cmp-pr-rad" title="${d.navn} — ${tittel}"><span class="nn-pr-navn">${d.navn}</span>` +
        `<span class="nn-pr-spor" aria-hidden="true"><i class="med"></i>${prikker}</span>` +
        `<span class="nn-sr">${tittel}</span></div>`;
    }).join('') + '</div>';
}

// 05 Sammendrag: indikatorene der plasseringene spriker mest (persentiler, så enhetene kan sammenlignes)
function sammendrag(ks) {
  const navn = k => kortNavn(k.navn);
  const ds = indikatorer().map(d => {
    const pl = ks.map(k => ({ k, x: plassering(k.nr, d) })).filter(r => r.x);
    if (pl.length < 2) return null;
    pl.sort((a, b) => b.x.p - a.x.p);
    return { d, hoy: pl[0], lav: pl[pl.length - 1], sprik: pl[0].x.p - pl[pl.length - 1].x.p };
  }).filter(Boolean).sort((a, b) => b.sprik - a.sprik);
  if (!ds.length) return '';
  const punkt = r => `<li><b>${r.d.navn}</b>: høyest ${navn(r.hoy.k)} (${r.d.tekst(r.hoy.x.v)}), lavest ${navn(r.lav.k)} (${r.d.tekst(r.lav.x.v)}).</li>`;
  const store = ds.filter(r => r.sprik >= 40).slice(0, 3);
  const like = ds.filter(r => r.sprik < 15);
  let h = store.length ? `<p>Kommunene skiller seg mest fra hverandre på ${store.length === 1 ? 'én indikator' : `${store.length === 2 ? 'to' : 'tre'} indikatorer`}:</p><ul class="nn-cmp-liste">${store.map(punkt).join('')}</ul>`
    : '<p>Kommunene ligger nær hverandre på alle indikatorene i profilen. Ingen av dem skiller mer enn 40 prosent av de 80 kommunene.</p>';
  if (like.length) h += `<p>De er mest like på ${like.slice(0, 3).map(r => r.d.navn.toLowerCase()).join(', ').replace(/, ([^,]*)$/, ' og $1')}.</p>`;
  h += '<p class="hint" style="margin-top:8px">Forskjellen måles i plassering blant de 80 kommunene, ikke i tallverdien, slik at indikatorer med ulik enhet kan sammenlignes.</p>';
  return '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hvor skiller de seg?</h3><span class="tag">Regelbasert tekst</span></div>' + h + '</div>';
}

// 04 Figurer
function figurer(ks) {
  const P = L.DATA?.proj; if (!P) return '';
  const fig = (tittel, under, innhold, kilde) => `<div class="card nav-fig"><div class="ch"><h3 class="serif">${tittel}</h3></div><p class="hint">${under}</p>${innhold}<p class="nn-source">${kilde}</p></div>`;
  // Folketall som indeks: historikk hvert femte år og framskriving, 2026 = 100
  const hx = Object.keys(ks[0].hist || {}).map(Number).filter(a => a < P.years[0]);
  const x = hx.concat(P.years);
  const f1 = fig('Folketall 2000–2050, indeks', 'Folketallet i hver kommune med 2026 = 100. Til og med 2025 faktisk folketall hvert femte år, deretter SSBs hovedalternativ.',
    placeholder('linjer', { x, format: 'tall', hoyde: 280, iDag: P.years[0], ref: [{ y: 100, tekst: '2026 = 100' }],
      serier: ks.map((k, i) => { const o = proj(k), b = o?.main?.[0]; return { navn: kortNavn(k.navn), kort: kortNavn(k.navn), farge: FARGENAVN[i], uthev: true,
        data: x.map(a => (a < P.years[0] ? (k.hist?.[a] != null && b ? k.hist[a] / b * 100 : null) : (o?.main?.[P.years.indexOf(a)] != null && b ? o.main[P.years.indexOf(a)] / b * 100 : null))) }; }) }, 290),
    'Kilde: SSB 07459 (folketall) og 14746 (framskriving, hovedalternativet).');
  const f2 = fig('Forsørgerbrøk 2026–2050', 'Innbyggere 65 år og over per 100 i alderen 20–64, SSBs hovedalternativ.',
    placeholder('linjer', { x: P.years, format: 'tall', hoyde: 260,
      serier: ks.map((k, i) => ({ navn: kortNavn(k.navn), kort: kortNavn(k.navn), farge: FARGENAVN[i], uthev: true, data: P.years.map((_, j) => fbAar(k, j)) })) }, 270),
    'Kilde: SSB 14746.');
  const grupper = typeof ageGroups === 'function' ? ageGroups(ks[0].alder, 'L').map(g => g.l) : null; // eslint-disable-line no-undef
  const f3 = grupper ? fig('Aldersfordeling 1.1.2026', 'Prosent av folketallet i hver livsfase, slik at store og små kommuner kan sammenlignes.',
    placeholder('stolper', { kategorier: grupper, format: 'pst', hoyde: 260,
      serier: ks.map((k, i) => ({ navn: kortNavn(k.navn), farge: FARGENAVN[i], data: ageGroups(k.alder, 'L').map(g => g.v / k.pop * 100) })) }, 270), // eslint-disable-line no-undef
    'Kilde: SSB 07459.') : '';
  return f1 + f2 + f3;
}

export function sammenlign(host, nrs) {
  const ks = nrs.map(nr => L.K.find(k => k.nr === +nr)).filter(Boolean).slice(0, 4);
  if (!host || ks.length < 2) return false;
  // 01 Toppen
  const topp = `<div class="nn-cmp-topp" style="grid-template-columns:repeat(${ks.length},minmax(0,1fr))">` + ks.map((k, i) =>
    `<div class="nn-cmp-k" style="border-top-color:${FARGER[i]}"><div class="nn-cmp-k-navn"><i style="background:${FARGER[i]}"></i>${kortNavn(k.navn)}</div>` +
    `<div class="nn-cmp-k-meta">${k.fylke} · ${heltall(L.BEFK?.kommuner?.[k.nr] ?? k.pop)} innbyggere</div><a href="kommune.html?k=${k.nr}">Kommunesiden →</a></div>`).join('') + '</div>';
  // 03 Tabellen
  const kol = ks.length + 3;
  const tab = rader().map(([gruppe, rs]) => `<tr class="gr"><td colspan="${kol}">${gruppe}</td></tr>` + rs.map(r => {
    const f = v => (r.tekst ? (v ?? '–') : r.fmt(ok(v)));
    const ref = fn => (fn ? f(fn()) : '–');
    return `<tr><th scope="row">${r.navn}<span class="meta">${r.meta}</span></th>` +
      ks.map(k => `<td${r.tekst ? ' class="tekst"' : ''}>${f(r.v(k))}</td>`).join('') + `<td class="ref${r.tekst ? ' tekst' : ''}">${ref(r.nn)}</td><td class="ref${r.tekst ? ' tekst' : ''}">${ref(r.la)}</td></tr>`;
  }).join('')).join('');
  const tabell = '<div class="nn-cmp-tab-rull"><table class="nn-cmp-tab"><thead><tr><th scope="col">Indikator</th>' +
    ks.map((k, i) => `<th scope="col"><i style="background:${FARGER[i]}"></i>${kortNavn(k.navn)}</th>`).join('') +
    '<th scope="col" class="ref">Nord-Norge</th><th scope="col" class="ref">Landet</th></tr></thead><tbody>' + tab + '</tbody></table></div>' +
    '<p class="nn-source">Kilder: SSB (07459, 14746, 09817, 11607, 13563, 03321, 07984, 07022, 12137, 12134), NAV og ROBEK-registeret; se <a href="metode.html">metodesiden</a>. Nord-Norge og landet står bare der tallet finnes på samme grunnlag; ellers står det –. Nord-Norge for ROBEK er antall registrerte kommuner. † SSB skjuler noen næringer, så en skjult næring kan være større.</p>';

  host.innerHTML = '<div class="dhead"><h2 class="serif">Sammenligning</h2><span style="font-size:13px;color:var(--ink3)"></span></div>' + topp +
    '<h3 class="nn-h3 nn-cmp-h">Hvor ligger kommunene blant de 80?</h3>' +
    '<p class="hint">Hver prikk er en kommune, plassert etter rangering blant alle 80 kommunene fra lavest til høyest; streken midt på er medianen. Pek på en rad for tallene.</p>' +
    profil(ks) + '<div class="nav-blokk">' + sammendrag(ks) + '</div>' +
    '<h3 class="nn-h3 nn-cmp-h">Tallene ved siden av hverandre</h3>' + tabell +
    '<h3 class="nn-h3 nn-cmp-h">Utviklingen</h3>' + figurer(ks);
  return true;
}
