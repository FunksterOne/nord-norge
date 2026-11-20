// «Fylket i tall»: nøkkeltall for fylket, Nord-Norge og landet (FYLKE_TALL, fetch_fylketall.py).
// Monteres i elementer med data-fylketall="auto" (fylket fra state.fylke) eller data-fylketall="nord-norge".
/* global FYLKE_TALL, SYSS_NIVAA, state */

const RADER = [
  ['Arbeid', [
    ['syss2066', 'Sysselsatte i alderen 20–66 år', 'pst', 'SSB 13563', 'nat'],
    ['syssInnv', 'Sysselsatte innvandrere i alderen 20–66 år', 'pst', 'SSB 13563', 'nat'],
    ['syss', 'Sysselsatte i alderen 15–74 år', 'pst', 'SSB 13563'],
    ['arbled', 'Registrerte arbeidsledige, andel av arbeidsstyrken 15–74 år', 'pst', 'SSB 13563'],
    ['ledige', 'Ledige stillinger', 'tall', 'SSB 14306', 'nat'],
    ['lonn', 'Gjennomsnittlig månedslønn, arbeidssted', 'kr', 'SSB 11422'],
  ]],
  ['Utdanning', [
    ['uh', 'Universitets- eller høgskoleutdanning, 16 år og over', 'pst', 'SSB 09429'],
    ['vgs', 'Videregående som høyeste utdanning', 'pst', 'SSB 09429'],
    ['stud', 'Studenter etter studiested', 'tall', 'SSB 03814'],
  ]],
  ['Bolig', [
    ['boliger', 'Boliger i alt', 'tall', 'SSB 06265', 'levekar'],
    ['fullf', 'Fullførte boliger', 'tall', 'SSB 05940'],
    ['kvpris', 'Kvadratmeterpris, brukte boliger', 'kr', 'SSB 14310'],
    ['gjeld3', 'Husholdninger med gjeld over tre ganger samlet inntekt', 'pst0', 'SSB 08781'],
  ]],
  ['Areal', [
    ['areal', 'Land og ferskvann', 'km2', 'SSB 09594'],
    ['bebygd', 'Bebygd areal', 'pst', 'SSB 09594'],
    ['jordbruk', 'Jordbruksareal', 'pst', 'SSB 09594'],
    ['vernet', 'Vernet areal på land', 'pst', 'SSB 08936'],
  ]],
  ['Samferdsel', [
    ['vei', 'Fylkesvei med dårlig eller svært dårlig dekke, andel av km', 'pst', 'SSB 11842 (KOSTRA)'],
  ]],
  ['Kommuneøkonomi', [
    ['ndr', 'Netto driftsresultat, kommunene samlet', 'pst', 'SSB 12134', 'refugees'],
    ['over175', 'Kommuner med netto driftsresultat over 1,75 %', 'andel', 'SSB 12134', 'refugees'],
    ['inv', 'Brutto investeringsutgifter i kommunene', 'mrd', 'SSB 13544'],
  ]],
];

const CSS = `
.fyt{margin:0 0 22px;border:1px solid var(--line2);background:var(--paper2)}
.fyt>summary{cursor:pointer;list-style:none;padding:14px 18px;font-family:var(--font-display);font-size:17px;font-weight:600;color:var(--ink);display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.fyt>summary::-webkit-details-marker{display:none}
.fyt>summary .fyt-h{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);font-weight:400}
.fyt[open]>summary .fyt-pil{transform:rotate(180deg)}
.fyt-pil{display:inline-block;transition:transform .15s;color:var(--ink3)}
.fyt-rull{overflow-x:auto;padding:0 18px 6px}
.fyt table{width:100%;border-collapse:collapse;font-size:13px;min-width:560px}
.fyt th{text-align:right;padding:8px 10px;color:var(--ink3);font-weight:600;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--line2)}
.fyt th:first-child{text-align:left}
.fyt td{padding:7px 10px;border-top:1px solid var(--line2);color:var(--ink2);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.fyt td:first-child{text-align:left;color:var(--ink);white-space:normal}
.fyt td.hoved{color:var(--ink);font-weight:600}
.fyt tr.gr td{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent-text);padding-top:14px;border-top:0}
.fyt .meta{display:block;font-size:11px;color:var(--ink3);margin-top:1px}
.fyt .meta a{color:var(--ink3)}
.fyt-kilde{padding:6px 18px 16px;font-size:11.5px;color:var(--ink3);line-height:1.5}
`;

const nb = (v, d = 0) => (v < 0 ? '−' : '') + Math.abs(v).toLocaleString('nb-NO', { minimumFractionDigits: d, maximumFractionDigits: d });

function verdi(F, key, kol, fmt) {
  const v = F.verdier[key] && F.verdier[key][kol];
  if (v == null) return '–';
  if (fmt === 'pst') return nb(v, 1) + ' %';
  if (fmt === 'pst0') return nb(v, 0) + ' %';   // SSB publiserer hele prosent (08781)
  if (fmt === 'kr') return 'kr ' + nb(v);
  if (fmt === 'km2') return nb(v) + ' km²';
  if (fmt === 'mrd') return nb(v, 1) + ' mrd. kr';
  if (fmt === 'andel') return v + ' av ' + F.verdier.antall_kommuner[kol];
  return nb(v);
}

// Sysselsetting 20–66 år fra SYSS_NIVAA (fetch_sysselsetting_nivaa.py), samme aldersgruppe som
// profilen på kommunesidene. Legges inn i kopien av FYLKE_TALL før tegning.
function medSysselsetting(F) {
  if (typeof SYSS_NIVAA === 'undefined') return F;
  const S = SYSS_NIVAA, navn = { 18: 'Nordland', 55: 'Troms', 56: 'Finnmark', NN: 'nord-norge', landet: 'landet' };
  const rate = x => (x.tot[x.tot.length - 1] ? x.syss[x.syss.length - 1] / x.tot[x.tot.length - 1] * 100 : null);
  const v = { syss2066: {}, syssInnv: {} };
  Object.entries(navn).forEach(([k, n]) => { const d = S.nivaa[k]; if (!d) return; v.syss2066[n] = rate(d); v.syssInnv[n] = rate(d.innv); });
  const a = S.aar[S.aar.length - 1];
  return { ...F, verdier: { ...F.verdier, ...v }, aar: { ...F.aar, syss2066: a, syssInnv: a } };
}

function tegn(el, F0, fylke) {
  const F = medSysselsetting(F0);
  const kol = fylke === 'nord-norge' ? ['nord-norge', 'landet'] : [fylke, 'nord-norge', 'landet'];
  const navn = { 'nord-norge': 'Nord-Norge', landet: 'Landet' };
  let h = '<table><thead><tr><th>Indikator</th>' + kol.map(k => '<th>' + (navn[k] || k) + '</th>').join('') + '</tr></thead><tbody>';
  RADER.forEach(([gruppe, rader]) => {
    h += '<tr class="gr"><td colspan="' + (kol.length + 1) + '">' + gruppe + '</td></tr>';
    rader.forEach(([key, tekst, fmt, kilde, sek]) => {
      const lenke = sek && document.querySelector('.nn-secnav button[data-sec="' + sek + '"]') ? ' · <a href="#" data-gaatil="' + sek + '">mer</a>' : '';
      h += '<tr><td>' + tekst + '<span class="meta">' + F.aar[key] + ' · ' + kilde + lenke + '</span></td>' +
        kol.map((k, i) => '<td' + (i === 0 ? ' class="hoved"' : '') + '>' + verdi(F, key, k, fmt) + '</td>').join('') + '</tr>';
    });
  });
  h += '</tbody></table>';
  const m = F.mangler_regnskap || [];
  const mangler = m.length ? ' Investeringsutgiftene mangler ' + (m.length > 1 ? m.slice(0, -1).join(', ') + ' og ' + m[m.length - 1] : m[0]) + ', som ikke hadde levert regnskap for 2025 til SSB.' : '';
  // lukket som standard (LAYOUT-VURDERING.md, anbefaling 06); valget huskes i nettleseren
  let åpen = '';
  try { åpen = localStorage.getItem('nn-fyt-aapen') === '1' ? ' open' : ''; } catch (e) { /* lagring ikke tilgjengelig */ }
  el.innerHTML = '<details class="fyt"' + åpen + '><summary><span>' + (fylke === 'nord-norge' ? 'Nord-Norge' : fylke) + ' i tall <span class="fyt-pil">▾</span></span><span class="fyt-h">' + RADER.reduce((n, g) => n + g[1].length, 0) + ' nøkkeltall · SSB</span></summary>' +
    '<div class="fyt-rull">' + h + '</div>' +
    '<p class="fyt-kilde">Alle tall er hentet fra SSBs statistikkbank. Nord-Norge er summen av de tre fylkene; andeler og priser er regnet av summene, lønn er veid med heltidsekvivalenter og kvadratmeterpris med antall omsetninger. Netto driftsresultat gjelder kommunekonsern, slik normen på 1,75 % måles.' + mangler + ' Ledige stillinger er SSBs utvalgsundersøkelse, avrundet til nærmeste hundre, og er ikke det samme som NAVs tall for utlyste stillinger. <a href="metode.html#fylketall">Metode og kontroll</a>.</p></details>';
  el.querySelector('.fyt').addEventListener('toggle', e => {
    try { localStorage.setItem('nn-fyt-aapen', e.target.open ? '1' : '0'); } catch (err) { /* ignorer */ }
  });
  el.querySelectorAll('[data-gaatil]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault();
    const b = document.querySelector('.nn-secnav button[data-sec="' + a.dataset.gaatil + '"]');
    if (b) { b.click(); b.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }));
}

export function initFylketall() {
  document.addEventListener('DOMContentLoaded', () => setTimeout(() => {
    if (typeof FYLKE_TALL === 'undefined') return;
    const el = document.querySelectorAll('[data-fylketall]');
    if (!el.length) return;
    const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    el.forEach(e => {
      let f = e.dataset.fylketall;
      if (f === 'auto') {
        // state er en let-variabel i assets/app.js og ligger derfor ikke på window
        f = typeof state !== 'undefined' ? state.fylke : null;
        if (!f || f === 'Alle') f = 'Nordland';
      }
      if (f === 'nord-norge' || FYLKE_TALL.verdier.syss[f] != null) tegn(e, FYLKE_TALL, f);
    });
  }, 0));
}
