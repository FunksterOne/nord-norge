// «Hvor står kommunen?» som én kompakt profil: én rad per indikator, prikken viser hvor kommunen ligger
// blant de 80 (persentil, lavest til venstre, høyest til høyre), streken midt på er medianen.
// Erstatter bisvermstripene øverst på kommunesiden (de ligger nå i en utfoldbar boks), og gir de fire
// nøkkeltallene i toppen en tynn plasseringslinje (rangLinjer).
// Ingen farger for «bra» eller «dårlig»: retningen er ikke opplagt for alle indikatorene.
import { L } from './legacy.js';
import { INDIKATORER } from '../charts/map.js';
import { tall, prosent, endringPst, heltall } from './format.js';

const kostra = (nr, f) => { const k = L.DATA?.proj?.kostra?.[nr]; return k && k[f] != null ? +k[f] : null; };
const aarK = () => (L.DATA?.proj?.kostra && Object.values(L.DATA.proj.kostra)[0]?.yr) || '';

function indikatorer() {
  const I = INDIKATORER;
  const nav = L.NAVK?.meta || {};
  return [
    { gruppe: 'Befolkning', key: 'endring', navn: 'Folketall 2026–2050', verdi: I.endring.verdi, tekst: v => endringPst(v, 1) },
    { gruppe: 'Befolkning', key: 'eldre', navn: 'Andel 65 år og over', verdi: I.eldre.verdi, tekst: v => prosent(v, 1) },
    { gruppe: 'Befolkning', key: 'forsorg', navn: 'Forsørgerbrøk 2050', verdi: I.forsorg.verdi, tekst: v => tall(v, 0) },
    { gruppe: 'Befolkning', key: 'innv', navn: 'Innvandrerbakgrunn', verdi: I.innv.verdi, tekst: v => prosent(v, 1) },
    { gruppe: 'Arbeid', key: 'navLedige', navn: `Helt ledige ${nav.ledige || ''}`.trim(), verdi: I.navLedige.verdi, tekst: v => prosent(v, 1) },
    { gruppe: 'Arbeid', key: 'navUfore', navn: 'Uføretrygd (NAV)', verdi: I.navUfore.verdi, tekst: v => prosent(v, 1) },
    { gruppe: 'Arbeid', key: 'pendNetto', navn: 'Netto pendling', verdi: I.pendNetto.verdi, tekst: v => endringPst(v, 1) },
    { gruppe: 'Økonomi', key: 'skattAndel', navn: 'Skatt per innbygger', verdi: I.skattAndel.verdi, tekst: v => `${tall(v, 0)} % av landet` },
    { gruppe: 'Økonomi', key: 'ndr', navn: `Netto driftsresultat ${aarK()}`, verdi: k => kostra(k.nr, 'ndr'), tekst: v => prosent(v, 1) },
    { gruppe: 'Økonomi', key: 'fond', navn: `Disposisjonsfond ${aarK()}`, verdi: k => kostra(k.nr, 'fond'), tekst: v => prosent(v, 1) },
  ];
}
const EKSTRA = { folketall: { key: 'folketall', navn: 'Folketall', verdi: k => k.pop, tekst: v => heltall(v) } };

// Plassering blant kommunene: persentil og en setning som «12. høyest av 80»
export function plassering(nr, d) {
  const alle = L.K.map(k => ({ nr: k.nr, v: d.verdi(k) })).filter(r => r.v != null && Number.isFinite(r.v));
  const me = alle.find(r => r.nr === nr);
  if (!me) return null;
  const andre = alle.filter(r => r.nr !== nr);
  const lav = andre.filter(r => r.v < me.v).length, hoy = andre.filter(r => r.v > me.v).length, lik = andre.length - lav - hoy;
  const m = andre.length;
  const p = m ? (lav + lik / 2) / m * 100 : 50;
  // Rangering fra nærmeste ende: «12. høyest av 80», «5. lavest av 80», «høyest av 80»
  const n = m + 1;
  const setning = hoy < lav ? (hoy ? `${hoy + 1}. høyest av ${n}` : `høyest av ${n}`)
    : lav < hoy ? (lav ? `${lav + 1}. lavest av ${n}` : `lavest av ${n}`)
    : `midt blant de ${n}`;
  return { v: me.v, p, setning, m };
}

const spor = (p, liten) => `<span class="nn-pr-spor${liten ? ' liten' : ''}" aria-hidden="true"><i class="med"></i><i class="prikk" style="left:${p.toFixed(1)}%"></i></span>`;

// Profilen: HTML-streng (ingen Plot nødvendig; skalerer med CSS)
export function profilHTML(nr) {
  let gruppe = '';
  const rader = indikatorer().map(d => {
    const pl = plassering(nr, d);
    if (!pl) return '';
    const hode = d.gruppe !== gruppe ? `<div class="nn-pr-gruppe">${(gruppe = d.gruppe)}</div>` : '';
    return `${hode}<div class="nn-pr-rad" title="${d.navn}: ${d.tekst(pl.v)}, ${pl.setning} kommuner">` +
      `<span class="nn-pr-navn">${d.navn}</span>${spor(pl.p)}` +
      `<span class="nn-pr-verdi">${d.tekst(pl.v)}</span><span class="nn-pr-rang">${pl.setning}</span></div>`;
  }).join('');
  return '<div class="nn-pr">' +
    '<div class="nn-pr-akse"><span class="nn-pr-akse-t"><span>lavest</span><span>median</span><span>høyest</span></span></div>' +
    rader + '</div>';
}

// Tynn plasseringslinje under nøkkeltallene i toppen. kort: [{el, key}]
export function rangLinjer(nr, kort) {
  const alle = Object.fromEntries(indikatorer().map(d => [d.key, d]));
  kort.forEach(({ el, key, etter = '' }) => {
    const d = alle[key] || EKSTRA[key];
    if (!el || !d || el.querySelector('.nn-pr-mini')) return;
    const pl = plassering(nr, d);
    if (!pl) return;
    const div = document.createElement('div');
    div.className = 'nn-pr-mini';
    div.innerHTML = `${spor(pl.p, true)}<span>${pl.setning.charAt(0).toUpperCase() + pl.setning.slice(1)} kommuner${etter}</span>`;
    el.appendChild(div);
  });
}
