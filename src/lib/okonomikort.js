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
const mill = v => (v == null ? "–" : v >= 1000 ? `${tall(v / 1000, 2)} milliarder kroner` : `${tall(v, 1)} millioner kroner`);

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
// nr: kommunenummer, eller med opt.nivaa: '18', '55', '56' eller 'NN' (fylkes- og landsdelssidene;
// tallene er summen av kommunene, se fetch_skatt.py)
export function skattKort(nr, host, opt = {}) {
  const S = L.SKATT;
  if (!S || !host) return;
  const kode = String(nr), niv = !!opt.nivaa, erNN = kode === 'NN';
  const kom = niv ? S.inngang.fylker[kode] : S.inngang.kommuner[kode], ko = niv ? S.kostra.fylker[kode] : S.kostra.kommuner[kode];
  if (!kom || !ko) { host.innerHTML = ''; return; }
  const navn = niv ? (erNN ? 'Nord-Norge' : FYLKE[kode]) : kortNavn(document.querySelector('[data-knavn]')?.dataset.knavn || L.K.find(k => String(k.nr) === kode)?.navn || kode);
  // sammenligningsnivået: fylket for en kommune, Nord-Norge for et fylke, ingen for Nord-Norge
  const fy = niv ? (erNN ? null : 'NN') : kode.slice(0, 2), fyNavn = fy === 'NN' ? 'Nord-Norge' : FYLKE[fy];
  const mottaker = niv ? `kommunene i ${navn}` : navn, kommunen = niv ? 'kommunene' : 'kommunen';
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
    (vK ? kpi(pp(vK.vekst), `Skatteinngang januar–${MND[vK.mnd]} ${aarNa}`, `mot samme periode i fjor${fy ? ` · ${fyNavn} ${vF ? pp(vF.vekst) : '–'}` : ''} · landet ${vL ? pp(vL.vekst) : '–'}`) : '') +
    kpi(kr(g(ko, 'skatt')), `Skatt per innbygger ${kaar}`, `${p0(andel('skatt'))} av landet · ${p0(g(lu, 'skatt') ? g(ko, 'skatt') / g(lu, 'skatt') * 100 : null)} av landet utenom Oslo`) +
    kpi(kr(g(ko, 'ramme')), `Rammetilskudd per innbygger ${kaar}`, `landet ${kr(g(la, 'ramme'))}`) +
    kpi(kr(g(ko, 'frie')), `Frie inntekter per innbygger ${kaar}`, `${p0(andel('frie'))} av landet`) +
    kpi(kr(g(ko, 'eiendom')), `Eiendomsskatt per innbygger ${kaar}`, `landet ${kr(g(la, 'eiendom'))}`) + '</div>';

  // tekst
  const avs = [];
  if (vK) {
    const endr = (v, fra) => `${tall(Math.abs(v), 1)} % ${v >= 0 ? 'mer' : 'mindre'} enn ${fra}`;
    avs.push(`Skatteinngangen til ${mottaker} var <b>${mill(vK.verdi)}</b> fra januar til ${MND[vK.mnd]} ${aarNa}, ${endr(vK.vekst, 'i samme periode i fjor')}.` +
      (vF && vL && fy ? ` I samme periode var endringen ${pp(vF.vekst)} i ${fyNavn} og ${pp(vL.vekst)} i landet.` : vL ? ` I samme periode var endringen ${pp(vL.vekst)} i landet.` : '') +
      (tot != null ? ` For hele ${helt} var inngangen ${mill(tot)}${totF ? `, ${endr((tot / totF - 1) * 100, 'i ' + forrige)}` : ''}.` : '') +
      ' Veksten henger også sammen med lønnsveksten og skattøren Stortinget fastsetter hvert år, og er ikke et mål på økt aktivitet alene.');
  }
  const as = andel('skatt'), af = andel('frie'), e = g(ko, 'eiendom');
  avs.push(`Innbyggerne betalte <b>${kr(g(ko, 'skatt'))}</b> i skatt på inntekt og formue per innbygger til ${kommunen} i ${kaar}, ${p0(as)} av landsgjennomsnittet. ` +
    `Med rammetilskudd på ${kr(g(ko, 'ramme'))} per innbygger, mot ${kr(g(la, 'ramme'))} i landet, fikk ${kommunen} frie inntekter på <b>${kr(g(ko, 'frie'))}</b> per innbygger, ${p0(af)} av landsnivået.` +
    (as != null && af != null && as < 95 && af >= 95 ? ' Inntektsutjevningen og rammetilskuddet veier altså opp for lav skatt per innbygger.' : '') +
    (e ? ` I tillegg kommer eiendomsskatt på ${kr(e)} per innbygger, mot ${kr(g(la, 'eiendom'))} i landet.` : ` KOSTRA viser ingen eiendomsskatt for ${kommunen} i ` + kaar + '.'));
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
    `<p class="hint" style="margin:0 0 10px">Hvor mye skatt innbyggerne i ${navn} betaler til ${kommunen}, og hvor mye utjevningen og rammetilskuddet legger til. ${niv ? ' Tallene er summen av kommunene.' : ''} Mer på <a href="metode.html#skatt">metodesiden</a>.</p>` +
    kpis + tekst + f1 + f2 + tabell + '</div>';
}

// ------------------------------------------------------------------ B1: pendling
// nr: kommunenummer, eller med opt.nivaa: '18', '55', '56' eller 'NN' (strømmer over fylkes- eller landsdelsgrensen)
export function pendlingKort(nr, host, opt = {}) {
  const P = L.PENDLING;
  if (!P || !host) return;
  const niv = !!opt.nivaa, erNN = String(nr) === 'NN';
  const d = niv ? P.fylker?.[String(nr)] : P.kommuner[String(nr)];
  if (!d || !d.aar.length) { host.innerHTML = ''; return; }
  const navn = niv ? (erNN ? 'Nord-Norge' : FYLKE[nr]) : kortNavn(L.K.find(k => String(k.nr) === String(nr))?.navn || String(nr));
  // område: «kommunen», «fylket» eller «landsdelen»
  const omr = niv ? (erNN ? 'landsdelen' : 'fylket') : 'kommunen';
  const andre = niv ? (erNN ? 'resten av landet' : 'andre fylker') : 'andre kommuner';
  const i = d.aar.length - 1, a = d.aar[i];
  const bo = d.bosatte[i], ut = d.ut[i], inn = d.inn[i], arb = d.arbeid[i], hjemme = bo - ut, netto = inn - ut;
  const kpis = '<div class="bf-kpis">' +
    kpi(heltall(ut), `Utpendlere ${a}`, `${p1(ut / bo * 100)} av ${heltall(bo)} sysselsatte bosatte`) +
    kpi(heltall(inn), `Innpendlere ${a}`, `${p1(inn / arb * 100)} av ${heltall(arb)} arbeidsplasser`) +
    kpi(`${netto > 0 ? '+' : netto < 0 ? '−' : ''}${heltall(Math.abs(netto))}`, 'Netto pendling', netto >= 0 ? 'flere pendler inn enn ut' : 'flere pendler ut enn inn') +
    (d.ut_nn[i] != null ? kpi(heltall(d.ut_nn[i]), niv ? 'Jobber ellers i Nord-Norge' : 'Utpendlere som jobber i Nord-Norge', `${p0(ut ? d.ut_nn[i] / ut * 100 : null)} av utpendlerne`) : '') +
    (niv ? kpi(heltall(d.mellom[i]), `Pendler mellom kommuner i ${omr}`, `${p1(d.mellom[i] / bo * 100)} av de sysselsatte bosatte`) : '') + '</div>';

  const avs = [];
  const topp = (l, n = 2) => l.slice(0, n).map(([k, v]) => `${kortNavn(k)} (${heltall(v)})`).join(' og ');
  avs.push(`Av ${heltall(bo)} sysselsatte som bor i ${navn}, jobber ${heltall(hjemme)} i ${omr} og <b>${heltall(ut)}</b> (${p1(ut / bo * 100)}) ${niv ? `utenfor ${omr}` : 'i en annen kommune'}` +
    (d.topp_ut?.length ? `, flest i ${topp(d.topp_ut)}` : '') + '.' +
    (niv ? ` I tillegg pendler ${heltall(d.mellom[i])} mellom to kommuner i ${omr}.` : ''));
  avs.push(`Samtidig kommer <b>${heltall(inn)}</b> av de ${heltall(arb)} som jobber i ${navn} (${p1(inn / arb * 100)}), fra ${andre}` +
    (d.topp_inn?.length ? `, særlig ${topp(d.topp_inn)}` : '') + `. Det gir en netto ${netto < 0 ? 'utpendling' : 'innpendling'} på ${heltall(Math.abs(netto))} personer.`);
  if (d.aar[0] < a) {
    const u0 = d.ut[0], n0 = d.inn[0], a0 = d.aar[0];
    const retn = (x0, x1) => (x1 > x0 ? 'økt' : x1 < x0 ? 'gått ned' : 'vært uendret');
    avs.push(`Siden ${a0} har utpendlingen ${retn(u0, ut)} fra ${heltall(u0)} til ${heltall(ut)}, mens innpendlingen har ${retn(n0, inn)} fra ${heltall(n0)} til ${heltall(inn)}.`);
  }
  avs.push('Inntektsskatten går til kommunen der man bor, så utpendlere betaler skatt til bostedskommunen. Arbeidssted er der arbeidsgiveren har registrert virksomheten; noen av dem jobber på avstand eller ukependler.' +
    (niv ? ` Tallene er summen av strømmene mellom kommunene; de største strømmene er oppgitt per kommune utenfor ${omr}.` : ''));
  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hvem pendler?</h3><span class="tag">SSB · regelbasert tekst</span></div>' +
    avs.map(t => `<p>${t}</p>`).join('') + '</div>';

  const stolper = (l, tittel) => placeholder('hstolper', { format: 'tall', grupper: [{ tittel, rader: l.map(([k, v]) => ({ l: kortNavn(k), v })) }] }, 40 + 26 * l.length);
  const f1 = (d.topp_ut?.length || d.topp_inn?.length) ? figur(`De største pendlerstrømmene, ${a}`, `Antall sysselsatte. Utpendling går fra ${omr} til arbeidsstedet; innpendling kommer fra bostedet.`,
    (d.topp_ut?.length ? stolper(d.topp_ut, `Jobber i … (bor i ${navn})`) : '') + (d.topp_inn?.length ? stolper(d.topp_inn, `Bor i … (jobber i ${navn})`) : ''),
    'Kilde: SSB 03321, sysselsatte 15–74 år per 4. kvartal.') : '';
  const f2 = figur(`Utpendling og innpendling ${d.aar[0]}–${a}`, 'Antall sysselsatte per 4. kvartal.',
    placeholder('linjer', { x: d.aar, format: 'tall', hoyde: 230, serier: [
      { navn: 'Utpendlere', kort: 'Ut', data: d.ut, farge: 'accent', uthev: true },
      { navn: 'Innpendlere', kort: 'Inn', data: d.inn, farge: 'ink' }].concat(niv ? [{ navn: `Mellom kommuner i ${omr}`, kort: 'Mellom', data: d.mellom, farge: 'var(--ink-3)', stil: 'stiplet' }] : []) }, 240),
    'Kilde: SSB 03321. Kommunekoder ført fram til dagens inndeling.');

  host.innerHTML = '<div class="nav-blokk"><h3 class="nn-h3" style="margin:26px 0 4px">Pendling inn og ut</h3>' +
    `<p class="hint" style="margin:0 0 10px">Hvor de som bor i ${navn}, jobber, og hvor de som jobber i ${navn}, bor.${niv ? ` Pendling over ${erNN ? 'landsdelsgrensen' : 'fylkesgrensen'}.` : ''} Mer på <a href="metode.html#pendling">metodesiden</a>.</p>` +
    kpis + tekst + f1 + f2 + '</div>';
}

// ------------------------------------------------------------------ Sysselsetting etter næring (NAERING_K, fetch_naering_kommune.py)
// nr: kommunenummer, eller med opt.nivaa: '18', '55', '56' eller 'NN'
export function naeringKort(nr, host, opt = {}) {
  const N = L.NAERINGK;
  if (!N || !host) return;
  const niv = !!opt.nivaa, erNN = String(nr) === 'NN';
  const d = niv ? (erNN ? N.NN : N.fylker?.[String(nr)]) : N.kommuner[String(nr)];
  if (!d) { host.innerHTML = ''; return; }
  const navn = niv ? (erNN ? 'Nord-Norge' : FYLKE[nr]) : kortNavn(L.K.find(k => String(k.nr) === String(nr))?.navn || String(nr));
  // Startåret er det første året der minst halvparten av næringene med tall i siste år også har tall.
  // For Troms og Finnmark blir det 2024: før det har SSB bare fylkene samlet, og summen av kommunene har
  // for mange skjulte celler.
  const i1 = N.aar.length - 1;
  const medTall = N.naeringer.filter(([k]) => d.arb[k]?.[i1] != null).map(([k]) => k);
  const i0Funnet = N.aar.findIndex((_, i) => i < i1 && medTall.filter(k => d.arb[k]?.[i] != null).length * 2 >= medTall.length);
  const aar = N.aar, i0 = i0Funnet < 0 ? i1 : i0Funnet, a0 = aar[i0], a1 = aar[i1];
  const tot = d.arb['00-99'], la = N.landet.arb, nn = N.NN.arb;
  const T1 = tot[i1], T0 = tot[i0];
  const rader = N.naeringer.filter(([k]) => k !== '00').map(([k, n]) => {
    const v0 = d.arb[k]?.[i0], v1 = d.arb[k]?.[i1];
    const andel = v1 != null && T1 ? v1 / T1 * 100 : null;
    const andelL = la[k]?.[i1] != null ? la[k][i1] / la['00-99'][i1] * 100 : null;
    const andelN = nn[k]?.[i1] != null ? nn[k][i1] / nn['00-99'][i1] * 100 : null;
    return { k, n, v0, v1, endr: v0 != null && v1 != null ? v1 - v0 : null, andel, andelL, andelN, skjult: v1 == null };
  });
  const synlig = rader.filter(r => !r.skjult).sort((a, b) => b.v1 - a.v1);
  const skjulte = rader.filter(r => r.skjult);
  const medEndr = rader.filter(r => r.endr != null).sort((a, b) => b.endr - a.endr);
  const storst = synlig[0], vekst = medEndr[0], fall = medEndr[medEndr.length - 1];
  const sign = v => `${v > 0 ? '+' : v < 0 ? '−' : ''}${heltall(Math.abs(v))}`;
  const blant = skjulte.length ? ' blant dem med tall' : '';

  const kpis = '<div class="bf-kpis">' +
    kpi(heltall(T1), `Arbeidsplasser ${a1}`, `${sign(T1 - T0)} siden ${a0} (${pp((T1 / T0 - 1) * 100)})`) +
    (storst ? kpi(p0(storst.andel), storst.n, `størst${blant}: ${heltall(storst.v1)} arbeidsplasser · landet ${p0(storst.andelL)}`) : '') +
    (vekst && vekst.endr > 0 ? kpi(sign(vekst.endr), `Størst vekst: ${vekst.n.toLowerCase()}`, `${heltall(vekst.v0)} → ${heltall(vekst.v1)} siden ${a0}`) : '') +
    (fall && fall.endr < 0 ? kpi(sign(fall.endr), `Størst nedgang: ${fall.n.toLowerCase()}`, `${heltall(fall.v0)} → ${heltall(fall.v1)} siden ${a0}`) : '') + '</div>';

  const avs = [];
  avs.push(`Det er <b>${heltall(T1)}</b> arbeidsplasser i ${navn} i ${a1}, ${T1 === T0 ? 'like mange som' : T1 > T0 ? `${heltall(T1 - T0)} flere enn` : `${heltall(T0 - T1)} færre enn`} i ${a0}.` +
    (storst ? ` ${storst.n} er den største næringen${blant}, med ${heltall(storst.v1)} arbeidsplasser (${p0(storst.andel)}), mot ${p0(storst.andelL)} i landet.` : ''));
  if (vekst && fall && vekst !== fall) {
    avs.push((vekst.endr > 0 ? `${skjulte.length ? 'Blant næringene med tall har ' + vekst.n.toLowerCase() : vekst.n + ' har'} vokst mest (${sign(vekst.endr)})` : 'Ingen næring med tall har vokst') +
      (fall.endr < 0 ? `, mens ${fall.n.toLowerCase()} har gått mest ned (${sign(fall.endr)}).` : '.'));
  }
  const sterk = synlig.filter(r => r.andelL && r.andel >= 3 && r.andel / r.andelL >= 1.5).sort((a, b) => b.andel / b.andelL - a.andel / a.andelL).slice(0, 3);
  if (sterk.length) avs.push(`Næringer med klart større andel av arbeidsplassene enn i landet: ${sterk.map(r => `${r.n.toLowerCase()} (${p0(r.andel)} mot ${p0(r.andelL)})`).join(', ')}.`);
  if (skjulte.length) avs.push(erNN
    ? `Tallene for ${skjulte.map(r => r.n.toLowerCase()).join(', ')} mangler fordi SSB skjuler dem for minst ett av fylkene. De er ikke med i figurene, men inngår i totalen.`
    : `SSB skjuler tallene for ${skjulte.map(r => r.n.toLowerCase()).join(', ')} for at enkeltbedrifter ikke skal kunne identifiseres. De er ikke med i figurene, men inngår i totalen.`);
  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hvor jobber folk?</h3><span class="tag">SSB · regelbasert tekst</span></div>' +
    avs.map(t => `<p>${t}</p>`).join('') + '</div>';

  const f1 = figur(`Arbeidsplasser etter næring, ${a1}`, `Sysselsatte 15–74 år med arbeidssted i ${navn}, 4. kvartal. Skjulte næringer og næringer uten arbeidsplasser er utelatt.`,
    placeholder('hstolper', { format: 'tall', grupper: [{ tittel: '', rader: synlig.filter(r => r.v1 > 0).map((r, j) => ({ l: r.n, v: r.v1, farge: j === 0 ? 'accent' : 'ink' })) }] }, 40 + 26 * synlig.filter(r => r.v1 > 0).length),
    'Kilde: SSB 07984, sysselsatte etter arbeidssted.');
  const f2 = medEndr.length ? figur(`Endring i arbeidsplasser ${a0}–${a1}`, 'Antall arbeidsplasser. Næringer uten endring og næringer som er skjult ett av årene, er utelatt.',
    placeholder('hstolper', { format: 'tall', grupper: [{ tittel: '', rader: medEndr.filter(r => r.endr !== 0).map(r => ({ l: r.n, v: r.endr, farge: r.endr >= 0 ? 'pos' : 'neg' })) }] }, 40 + 26 * medEndr.filter(r => r.endr !== 0).length),
    'Kilde: SSB 07984.') : '';
  const celle = v => (v == null ? 'skjult' : heltall(v));
  const nnKol = !erNN; // landsdelen sammenlignes ikke med seg selv
  const tab = rader.slice().sort((a, b) => (b.v1 ?? -1) - (a.v1 ?? -1)).map(r => `<tr><td>${r.n}</td><td class="num">${celle(r.v0)}</td><td class="num">${celle(r.v1)}</td>` +
    `<td class="num">${r.endr == null ? '–' : sign(r.endr)}</td><td class="num">${r.andel == null ? '–' : tall(r.andel, 1)}</td>${nnKol ? `<td class="num">${r.andelN == null ? '–' : tall(r.andelN, 1)}</td>` : ''}<td class="num">${r.andelL == null ? '–' : tall(r.andelL, 1)}</td></tr>`).join('');
  const tabell = figur(`Arbeidsplasser i ${navn} etter næring`, `Antall ${a0} og ${a1}, og andel av alle arbeidsplasser ${a1} i prosent.`,
    '<div class="nn-tabell-rull"><table class="nn-tabell"><thead><tr><th>Næring</th>' +
    `<th class="num">${a0}</th><th class="num">${a1}</th><th class="num">Endring</th><th class="num">Andel</th>${nnKol ? '<th class="num">Andel NN</th>' : ''}<th class="num">Andel landet</th></tr></thead>` +
    `<tbody>${tab}<tr class="sum"><td>Alle næringer</td><td class="num">${heltall(T0)}</td><td class="num">${heltall(T1)}</td><td class="num">${sign(T1 - T0)}</td><td class="num">100</td>${nnKol ? '<td class="num">100</td>' : ''}<td class="num">100</td></tr></tbody></table></div>`,
    `Kilde: SSB 07984.${nnKol ? ' NN = Nord-Norge.' : ''} Summen omfatter de skjulte næringene.${niv && !erNN && String(nr) !== '18' ? ` Sammenligningen starter i ${a0}: før 2024 har SSB bare tall for Troms og Finnmark samlet, og summen av kommunene har for mange skjulte tall.` : ''}`);

  host.innerHTML = '<div class="nav-blokk"><h3 class="nn-h3" style="margin:26px 0 4px">Arbeidsplasser etter næring</h3>' +
    `<p class="hint" style="margin:0 0 10px">Hvilke næringer arbeidsplassene i ${navn} finnes i, og hvordan de har endret seg siden ${a0}. Mer på <a href="metode.html#naering-kommune">metodesiden</a>.</p>` +
    kpis + tekst + f1 +
    '<details class="nn-mer"><summary>Vis endring per næring og tabell</summary>' + f2 + tabell + '</details>' + '</div>';
}
