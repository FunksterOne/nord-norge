// Skatt og pendling på kommunesiden (pakke A1, A2 og B1 i analyse/PLAN-NARVIK-TEMAER.md).
// Data: SKATT_DATA (fetch_skatt.py: SSB 07022 og 12137) og PENDLING_DATA (fetch_pendling.py: SSB 03321).
// Teksten lages av regler fra tallene; ingen tekst er skrevet for hånd per kommune.
import { placeholder } from '../charts/core.js';
import { tall, heltall, kortNavn } from './format.js';
import { L } from './legacy.js';

const MND = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember'];
const MNDK = ['jan.', 'feb.', 'mars', 'april', 'mai', 'juni', 'juli', 'aug.', 'sep.', 'okt.', 'nov.', 'des.'];
const FYLKE = { 18: 'Nordland', 55: 'Troms', 56: 'Finnmark' };
const p0 = v => (v == null ? '–' : `${tall(v, 0)} %`);
const p1 = v => (v == null ? '–' : `${tall(v, 1)} %`);
const pp = v => `${v > 0 ? '+' : v < 0 ? '−' : ''}${tall(Math.abs(v), 1)} %`;
const kr = v => (v == null ? '–' : `${heltall(v)} kr`);
const mill = v => (v == null ? '–' : `${tall(v, 1)} millioner kroner`);

function figur(tittel, undertekst, innhold, kilde) {
  return `<div class="card nav-fig"><div class="ch"><h3 class="serif">${tittel}</h3></div>` +
    (undertekst ? `<p class="hint">${undertekst}</p>` : '') + innhold + (kilde ? `<p class="nn-kilde">${kilde}</p>` : '') + '</div>';
}
const kpi = (v, l, h) => `<div class="k"><div class="v">${v}</div><div class="l">${l}</div><div class="h">${h}</div></div>`;

// Vekst hittil i år: siste måned med tall i år mot samme måned i fjor
export function skatteVekst(serie, aar) {
  const i = serie?.[aar], f = serie?.[aar - 1];
  if (!i || !f) return null;
  const m = i.reduce((s, v, j) => (v != null ? j : s), -1);
  if (m < 0 || f[m] == null || !f[m]) return null;
  return { mnd: m, verdi: i[m], fjor: f[m], vekst: (i[m] / f[m] - 1) * 100 };
}

// ------------------------------------------------------------------ A1 + A2: skatt
export function skattKort(nr, host) {
  const S = L.SKATT;
  if (!S || !host) return;
  const kode = String(nr);
  const kom = S.inngang.kommuner[kode], ko = S.kostra.kommuner[kode];
  if (!kom || !ko) { host.innerHTML = ''; return; }
  const navn = kortNavn(document.querySelector('[data-knavn]')?.dataset.knavn || L.K.find(k => String(k.nr) === kode)?.navn || kode);
  const fy = kode.slice(0, 2), fyNavn = FYLKE[fy];
  const aarNa = +S.siste_mnd.slice(0, 4);
  const vK = skatteVekst(kom, aarNa), vF = skatteVekst(S.inngang.fylker[fy], aarNa), vL = skatteVekst(S.inngang.landet, aarNa);
  const helt = String(aarNa - 1), forrige = String(aarNa - 2);
  const aarSum = s => (s?.[11] != null ? s[11] : null);
  const tot = aarSum(kom[helt]), totF = aarSum(kom[forrige]);
  const kaar = String(S.kostra_aar[S.kostra_aar.length - 1]);
  const la = S.kostra.landet, lu = S.kostra.landet_uo;
  const g = (o, a, t = kaar) => o?.[a]?.[t] ?? null;
  const andel = (a, t = kaar) => (g(ko, a, t) != null && g(la, a, t) ? g(ko, a, t) / g(la, a, t) * 100 : null);

  const kpis = '<div class="bf-kpis">' +
    (vK ? kpi(pp(vK.vekst), `Skatteinngang januar–${MND[vK.mnd]} ${aarNa}`, `mot samme periode i fjor · ${fyNavn} ${vF ? pp(vF.vekst) : '–'} · landet ${vL ? pp(vL.vekst) : '–'}`) : '') +
    kpi(kr(g(ko, 'skatt')), `Skatt per innbygger ${kaar}`, `${p0(andel('skatt'))} av landet · ${p0(g(lu, 'skatt') ? g(ko, 'skatt') / g(lu, 'skatt') * 100 : null)} av landet utenom Oslo`) +
    kpi(kr(g(ko, 'ramme')), `Rammetilskudd per innbygger ${kaar}`, `landet ${kr(g(la, 'ramme'))}`) +
    kpi(kr(g(ko, 'frie')), `Frie inntekter per innbygger ${kaar}`, `${p0(andel('frie'))} av landet`) +
    kpi(kr(g(ko, 'eiendom')), `Eiendomsskatt per innbygger ${kaar}`, `landet ${kr(g(la, 'eiendom'))}`) + '</div>';

  // tekst
  const avs = [];
  if (vK) {
    const endr = (v, fra) => `${tall(Math.abs(v), 1)} % ${v >= 0 ? 'mer' : 'mindre'} enn ${fra}`;
    avs.push(`Skatteinngangen til ${navn} var <b>${mill(vK.verdi)}</b> fra januar til ${MND[vK.mnd]} ${aarNa}, ${endr(vK.vekst, 'i samme periode i fjor')}.` +
      (vF && vL ? ` I samme periode var endringen ${pp(vF.vekst)} i ${fyNavn} og ${pp(vL.vekst)} i landet.` : '') +
      (tot != null ? ` For hele ${helt} var inngangen ${mill(tot)}${totF ? `, ${endr((tot / totF - 1) * 100, 'i ' + forrige)}` : ''}.` : '') +
      ' Veksten henger også sammen med lønnsveksten og skattøren Stortinget fastsetter hvert år, og er ikke et mål på økt aktivitet alene.');
  }
  const as = andel('skatt'), af = andel('frie'), e = g(ko, 'eiendom');
  avs.push(`Innbyggerne betalte <b>${kr(g(ko, 'skatt'))}</b> i skatt på inntekt og formue per innbygger til kommunen i ${kaar}, ${p0(as)} av landsgjennomsnittet. ` +
    `Med rammetilskudd på ${kr(g(ko, 'ramme'))} per innbygger, mot ${kr(g(la, 'ramme'))} i landet, fikk kommunen frie inntekter på <b>${kr(g(ko, 'frie'))}</b> per innbygger, ${p0(af)} av landsnivået.` +
    (as != null && af != null && as < 95 && af >= 95 ? ' Inntektsutjevningen og rammetilskuddet veier altså opp for lav skatt per innbygger.' : '') +
    (e ? ` I tillegg kommer eiendomsskatt på ${kr(e)} per innbygger, mot ${kr(g(la, 'eiendom'))} i landet.` : ' KOSTRA viser ingen eiendomsskatt for kommunen i ' + kaar + '.'));
  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hva viser skattetallene?</h3><span class="tag">SSB · regelbasert tekst</span></div>' +
    avs.map(a => `<p>${a}</p>`).join('') + '</div>';

  // figur 1: akkumulert skatteinngang i år og i fjor
  const x = MND.map((_, i) => i + 1);
  const serie = (s, a) => (s?.[a] || []).map(v => (v == null ? null : v));
  const f1 = vK ? figur(`Skatteinngang ${aarNa} mot ${aarNa - 1}`, 'Ordinær skatt til kommunen, akkumulert fra januar, millioner kroner.',
    placeholder('linjer', {
      x, xEtikett: MNDK, xFormat: 'tekst', format: 'tall1', hoyde: 240, brudd: true,
      serier: [{ navn: `${navn} ${aarNa}`, kort: String(aarNa), data: serie(kom, String(aarNa)), farge: 'accent', uthev: true },
        { navn: `${navn} ${aarNa - 1}`, kort: String(aarNa - 1), data: serie(kom, String(aarNa - 1)), farge: 'var(--ink-3)', stil: 'stiplet' }],
    }, 250), `Kilde: SSB 07022, skatteregnskapet. Til og med ${MND[+S.siste_mnd.slice(5) - 1]} ${aarNa}.`) : '';

  // figur 2: skatt og frie inntekter i prosent av landet, 2020–siste år
  const aarK = S.kostra_aar.map(String);
  const f2 = figur('Skatt og frie inntekter per innbygger i prosent av landet',
    'Linjen ved 100 er landsgjennomsnittet. Avstanden mellom linjene viser hvor mye inntektsutjevningen og rammetilskuddet løfter kommunen.',
    placeholder('linjer', {
      x: aarK.map(Number), format: 'tall', hoyde: 240, ref: [{ y: 100, tekst: 'Landet = 100' }],
      serier: [{ navn: 'Skatt per innbygger', kort: 'Skatt', data: aarK.map(t => andel('skatt', t)), farge: 'var(--ink-3)' },
        { navn: 'Frie inntekter per innbygger', kort: 'Frie inntekter', data: aarK.map(t => andel('frie', t)), farge: 'accent', uthev: true }],
    }, 250), 'Kilde: SSB 12137 (KOSTRA, kommunekonsern). Frie inntekter er skatt på inntekt og formue pluss rammetilskudd.');

  // tabell
  const rader = [...aarK].reverse().map(t => `<tr><td>${t}</td><td class="num">${heltall(g(ko, 'skatt', t))}</td><td class="num">${heltall(g(la, 'skatt', t))}</td>` +
    `<td class="num">${heltall(g(ko, 'ramme', t))}</td><td class="num">${heltall(g(ko, 'frie', t))}</td><td class="num">${heltall(g(la, 'frie', t))}</td>` +
    `<td class="num">${heltall(g(ko, 'eiendom', t))}</td><td class="num">${tot != null && kom[t]?.[11] != null ? tall(kom[t][11], 1) : '–'}</td></tr>`).join('');
  const tabell = figur(`Skatt og frie inntekter i ${navn} år for år`, 'Kroner per innbygger, og skatteinngang i millioner kroner for hele året.',
    '<div class="nn-tabell-rull"><table class="nn-tabell"><thead><tr><th>År</th><th class="num">Skatt</th><th class="num">Skatt, landet</th><th class="num">Rammetilskudd</th><th class="num">Frie inntekter</th><th class="num">Frie, landet</th><th class="num">Eiendomsskatt</th><th class="num">Skatteinngang (mill.)</th></tr></thead>' +
    `<tbody>${rader}</tbody></table></div>`, 'Kilde: SSB 12137 og 07022.');

  host.innerHTML = '<div class="nav-blokk"><h3 class="nn-h3" style="margin:26px 0 4px">Skatteinngang og inntektsutjevning</h3>' +
    `<p class="hint" style="margin:0 0 10px">Hvor mye skatt innbyggerne i ${navn} betaler til kommunen, og hvor mye utjevningen og rammetilskuddet legger til. Mer på <a href="metode.html#skatt">metodesiden</a>.</p>` +
    kpis + tekst + f1 + f2 + tabell + '</div>';
}

// ------------------------------------------------------------------ B1: pendling
export function pendlingKort(nr, host) {
  const P = L.PENDLING;
  if (!P || !host) return;
  const d = P.kommuner[String(nr)];
  if (!d || !d.aar.length) { host.innerHTML = ''; return; }
  const navn = kortNavn(L.K.find(k => String(k.nr) === String(nr))?.navn || String(nr));
  const i = d.aar.length - 1, a = d.aar[i];
  const bo = d.bosatte[i], ut = d.ut[i], inn = d.inn[i], arb = d.arbeid[i], hjemme = bo - ut, netto = inn - ut;
  const kpis = '<div class="bf-kpis">' +
    kpi(heltall(ut), `Utpendlere ${a}`, `${p1(ut / bo * 100)} av ${heltall(bo)} sysselsatte bosatte`) +
    kpi(heltall(inn), `Innpendlere ${a}`, `${p1(inn / arb * 100)} av ${heltall(arb)} arbeidsplasser`) +
    kpi(`${netto > 0 ? '+' : netto < 0 ? '−' : ''}${heltall(Math.abs(netto))}`, 'Netto pendling', netto >= 0 ? 'flere pendler inn enn ut' : 'flere pendler ut enn inn') +
    kpi(heltall(d.ut_nn[i]), 'Utpendlere som jobber i Nord-Norge', `${p0(ut ? d.ut_nn[i] / ut * 100 : null)} av utpendlerne`) + '</div>';

  const avs = [];
  const topp = (l, n = 2) => l.slice(0, n).map(([k, v]) => `${kortNavn(k)} (${heltall(v)})`).join(' og ');
  avs.push(`Av ${heltall(bo)} sysselsatte som bor i ${navn}, jobber ${heltall(hjemme)} i kommunen og <b>${heltall(ut)}</b> (${p1(ut / bo * 100)}) i en annen kommune` +
    (d.topp_ut?.length ? `, flest i ${topp(d.topp_ut)}` : '') + '.');
  avs.push(`Samtidig kommer <b>${heltall(inn)}</b> av de ${heltall(arb)} som jobber i ${navn} (${p1(inn / arb * 100)}), fra andre kommuner` +
    (d.topp_inn?.length ? `, særlig ${topp(d.topp_inn)}` : '') + `. Det gir en netto ${netto < 0 ? 'utpendling' : 'innpendling'} på ${heltall(Math.abs(netto))} personer.`);
  if (d.aar[0] < a) {
    const u0 = d.ut[0], n0 = d.inn[0], a0 = d.aar[0];
    const retn = (x0, x1) => (x1 > x0 ? 'økt' : x1 < x0 ? 'gått ned' : 'vært uendret');
    avs.push(`Siden ${a0} har utpendlingen ${retn(u0, ut)} fra ${heltall(u0)} til ${heltall(ut)}, mens innpendlingen har ${retn(n0, inn)} fra ${heltall(n0)} til ${heltall(inn)}.`);
  }
  avs.push('Inntektsskatten går til kommunen der man bor, så utpendlere betaler skatt til bostedskommunen. Arbeidssted er der arbeidsgiveren har registrert virksomheten; noen av dem jobber på avstand eller ukependler.');
  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hvem pendler?</h3><span class="tag">SSB · regelbasert tekst</span></div>' +
    avs.map(t => `<p>${t}</p>`).join('') + '</div>';

  const stolper = (l, tittel) => placeholder('hstolper', { format: 'tall', grupper: [{ tittel, rader: l.map(([k, v]) => ({ l: kortNavn(k), v })) }] }, 40 + 26 * l.length);
  const f1 = (d.topp_ut?.length || d.topp_inn?.length) ? figur(`De største pendlerstrømmene, ${a}`, 'Antall sysselsatte. Utpendling går fra kommunen til arbeidsstedet; innpendling kommer fra bostedet.',
    (d.topp_ut?.length ? stolper(d.topp_ut, `Jobber i … (bor i ${navn})`) : '') + (d.topp_inn?.length ? stolper(d.topp_inn, `Bor i … (jobber i ${navn})`) : ''),
    'Kilde: SSB 03321, sysselsatte 15–74 år per 4. kvartal.') : '';
  const f2 = figur(`Utpendling og innpendling ${d.aar[0]}–${a}`, 'Antall sysselsatte per 4. kvartal.',
    placeholder('linjer', { x: d.aar, format: 'tall', hoyde: 230, serier: [
      { navn: 'Utpendlere', kort: 'Ut', data: d.ut, farge: 'accent', uthev: true },
      { navn: 'Innpendlere', kort: 'Inn', data: d.inn, farge: 'ink' }] }, 240),
    'Kilde: SSB 03321. Kommunekoder ført fram til dagens inndeling.');

  host.innerHTML = '<div class="nav-blokk"><h3 class="nn-h3" style="margin:26px 0 4px">Pendling inn og ut</h3>' +
    `<p class="hint" style="margin:0 0 10px">Hvor de som bor i ${navn}, jobber, og hvor de som jobber i ${navn}, bor. Mer på <a href="metode.html#pendling">metodesiden</a>.</p>` +
    kpis + tekst + f1 + f2 + '</div>';
}
