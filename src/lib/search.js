// Kommandopalett: Ctrl/Cmd+K eller «/» åpner søk etter kommuner, fylker, regioner og sider.
import { L } from './legacy.js';
import { heltall, kortNavn } from './format.js';

const SIDER = [
  ['Hele landsdelen', 'nord-norge.html', 'Oversikt'],
  ['Sammenlign kommuner', 'sammenlign.html', 'Verktøy'],
  ['Hvem blir værende? Flyktningstrømmen, bofasthet og flytteforbud', 'tema-flyktning.html', 'Tema 01'],
  ['Store mot små: 6 mot 74 kommuner', 'tema-o6.html', 'Tema 02'],
  ['Kvinneflukten', 'tema-kvinneflukt.html', 'Tema 03'],
  ['Hvem skal bære? Arbeidskraft, aldring og forsørgerbyrde', 'tema-arbeidskraft.html', 'Tema 04'],
  ['Aldring i internasjonalt perspektiv og eldreomsorgen mot 2050', 'tema-aldring.html', 'Tema 05'],
  ['Fire fremtider mot 2040', 'tema-scenarier.html', 'Tema 06'],
  ['Bygges det nok? Boligmarkedet', 'tema-bolig.html', 'Tema 07'],
  ['Hva skal vi leve av? Næringslivet, sjømat, reiseliv, forsvar', 'tema-naering.html', 'Tema 08'],
  ['Pensjonsetterslepet: kommunale pensjoner og premieavvik', 'tema-pensjon.html', 'Tema 09'],
  ['Ung i nord: unge voksne, bosted, arbeid, bolig og barn', 'tema-ung.html', 'Tema 10'],
  ['20 år med nordområdepolitikk: strategier, stortingsmeldinger og utviklingen 2006–2026', 'tema-nordomrade.html', 'Tema 11'],
  ['Metode og kilder', 'metode.html', 'Referanse'],
];

const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/ø/g, 'o').replace(/æ/g, 'ae').replace(/å/g, 'a').replace(/ŋ/g, 'n').replace(/đ/g, 'd').replace(/ŧ/g, 't');

function items() {
  const out = [];
  for (const k of L.K) out.push({ t: k.navn, s: `${k.fylke} · ${heltall(k.pop)} innbyggere`, href: `kommune.html?k=${k.nr}`, w: 3, key: norm(k.navn + ' ' + kortNavn(k.navn)) });
  for (const f of ['Nordland', 'Troms', 'Finnmark']) out.push({ t: f, s: 'Fylke', href: `fylke.html?f=${f}`, w: 4, key: norm(f) });
  for (const r of L.REGIONS) {
    const ks = L.K.filter(k => k.region === r.id);
    out.push({ t: `Region ${r.navn}`, s: `${r.fylke} · ${ks.length} kommuner — ${ks.slice(0, 4).map(k => kortNavn(k.navn)).join(', ')}${ks.length > 4 ? ' …' : ''}`, href: `tema-arbeidskraft.html#regionlag`, w: 1, key: norm(r.navn + ' region') });
  }
  for (const [t, href, s] of SIDER) out.push({ t, s, href, w: 2, key: norm(t + ' ' + s) });
  return out;
}

function score(it, q) {
  if (!q) return it.w;
  const i = it.key.indexOf(q);
  if (i === 0) return 100 + it.w;
  if (i > 0) return 60 - i + it.w;
  // forbokstav-treff på ord
  const words = q.split(/\s+/);
  return words.every(w => it.key.includes(w)) ? 30 + it.w : -1;
}

export function initSearch() {
  const dlg = document.createElement('dialog');
  dlg.className = 'nn-palett';
  dlg.innerHTML = `<form method="dialog" class="nn-palett-f">
      <label class="nn-sr" for="nnSok">Søk</label>
      <input id="nnSok" type="search" autocomplete="off" placeholder="Søk etter kommune, fylke, region eller tema" />
      <ul class="nn-palett-l" role="listbox" aria-label="Treff"></ul>
      <div class="nn-palett-hint"><span>Pil opp/ned for å velge</span><span>Enter for å åpne</span><span>Esc for å lukke</span></div>
    </form>`;
  document.body.appendChild(dlg);
  const inp = dlg.querySelector('input');
  const ul = dlg.querySelector('ul');
  let list = [], sel = 0, all = null;

  const draw = () => {
    const q = norm(inp.value.trim());
    all = all || items();
    list = all.map(it => [score(it, q), it]).filter(x => x[0] >= 0).sort((a, b) => b[0] - a[0]).slice(0, 9).map(x => x[1]);
    sel = Math.min(sel, Math.max(0, list.length - 1));
    ul.innerHTML = list.length ? list.map((it, i) =>
      `<li role="option" aria-selected="${i === sel}" data-i="${i}"><span class="t">${it.t}</span><span class="s">${it.s}</span></li>`).join('')
      : '<li class="tom">Ingen treff. Prøv et kommunenavn, for eksempel «Vardø».</li>';
  };
  const go = i => { const it = list[i]; if (it) location.href = it.href; };
  const open = () => { if (!dlg.open) { all = null; inp.value = ''; sel = 0; draw(); dlg.showModal(); inp.focus(); } };

  inp.addEventListener('input', () => { sel = 0; draw(); });
  inp.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { sel = Math.min(list.length - 1, sel + 1); draw(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { sel = Math.max(0, sel - 1); draw(); e.preventDefault(); }
    else if (e.key === 'Enter') { go(sel); e.preventDefault(); }
  });
  ul.addEventListener('click', e => { const li = e.target.closest('li[data-i]'); if (li) go(+li.dataset.i); });
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  document.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '');
    if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !typing)) { e.preventDefault(); open(); }
  });

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'nn-sokknapp';
  btn.innerHTML = 'Søk <kbd>Ctrl K</kbd>';
  btn.addEventListener('click', open);
  const mount = () => {
    const host = document.querySelector('.nn-stripe .nn-verktoy');
    if (host) host.prepend(btn);
    else { btn.classList.add('nn-sokknapp-fast'); document.body.appendChild(btn); }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  // Knapper med data-sok (for eksempel «Bytt kommune») åpner søket.
  document.addEventListener('click', e => { if (e.target.closest('[data-sok]')) { e.preventDefault(); open(); } });
  return open;
}
