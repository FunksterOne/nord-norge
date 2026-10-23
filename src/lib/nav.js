// Felles navigasjon for alle sider: klebrig toppstripe med temameny, aktrad på lange sider,
// temanivå i brødsmulen og forrige/neste nederst på temasidene. Én kilde for listen over temaer.
export const TEMAER = [
  { nr: '01', fil: 'tema-flyktning.html', tittel: 'Hvem blir værende?', sub: 'Flyttestrømmer og bofasthet', metode: 'bofasthet' },
  { nr: '02', fil: 'tema-o6.html', tittel: 'Store mot små', sub: '6 store mot 74 mindre kommuner', metode: 'framskriving' },
  { nr: '03', fil: 'tema-kvinneflukt.html', tittel: 'Kvinneflukten', sub: 'De flytter i ung alder', metode: 'ssb' },
  { nr: '04', fil: 'tema-arbeidskraft.html', tittel: 'Hvem skal bære?', sub: 'Arbeidskraft og aldring', metode: 'forsorgerbyrde' },
  { nr: '05', fil: 'tema-aldring.html', tittel: 'Hvor står vi globalt?', sub: 'Aldring og eldreomsorg', metode: 'eldreomsorg' },
  { nr: '06', fil: 'tema-scenarier.html', tittel: 'Fire fremtider mot 2040', sub: 'Scenarier for næringslivet', metode: 'framskriving' },
  { nr: '07', fil: 'tema-bolig.html', tittel: 'Bygges det nok?', sub: 'Boligmarkedet', metode: 'boligbehov' },
  { nr: '08', fil: 'tema-naering.html', tittel: 'Hva skal vi leve av?', sub: 'Næringslivet mot 2040', metode: 'ssb' },
  { nr: '09', fil: 'tema-pensjon.html', tittel: 'Pensjonsetterslepet', sub: 'Kommunale pensjoner', metode: 'pensjon' },
  { nr: '10', fil: 'tema-ung.html', tittel: 'Ung i nord', sub: 'Unge voksne 18–34 år', metode: 'barometer' },
  { nr: '11', fil: 'tema-nordomrade.html', tittel: '20 år med nordområdepolitikk', sub: 'Hva som ble sagt, og hva som skjedde', metode: 'nordomradepolitikk' },
];
const METODE = { 'sammenlign.html': 'normer', 'nord-norge.html': 'framskriving', 'fylke.html': 'framskriving', 'kommune.html': 'framskriving' };
const MOBIL = '(max-width: 720px)';

const fil = () => (location.pathname.split('/').pop() || 'index.html').replace(/^$/, 'index.html');
const el = (tag, attrs = {}, html = '') => { const e = document.createElement(tag); Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v)); if (html) e.innerHTML = html; return e; };

function temaLenker(aktiv) {
  return TEMAER.map(t => `<a href="${t.fil}"${t.fil === aktiv ? ' aria-current="page"' : ''}><span class="nr">${t.nr}</span><span class="tt">${t.tittel}</span><span class="st">${t.sub}</span></a>`).join('');
}

function lagStripe(side, tema) {
  const metode = `metode.html${tema ? '#' + tema.metode : METODE[side] ? '#' + METODE[side] : ''}`;
  const lenke = (href, tekst, filnavn) => `<a class="nn-sl" href="${href}"${side === filnavn ? ' aria-current="page"' : ''}>${tekst}</a>`;
  const hode = el('div', { class: 'nn-hode', id: 'nnHode' });
  hode.innerHTML = `
    <a class="nn-hopp" href="#innhold">Hopp til innholdet</a>
    <nav class="nn-stripe" aria-label="Hovedmeny"><div class="nn-stripe-i">
      <button type="button" class="nn-menyknapp" aria-expanded="false" aria-controls="nnMobilmeny">Meny</button>
      <a class="nn-merke" href="index.html"${side === 'index.html' ? ' aria-current="page"' : ''}>Nord-Norge mot 2050</a>
      <div class="nn-lenker">
        <div class="nn-temaer">
          <button type="button" class="nn-sl nn-temaknapp" aria-expanded="false" aria-controls="nnTemapanel"${tema ? ' data-aktiv="true"' : ''}>Temaer <span aria-hidden="true">▾</span></button>
          <div class="nn-temapanel" id="nnTemapanel" hidden><div class="nn-temagrid">${temaLenker(side)}</div></div>
        </div>
        ${lenke('nord-norge.html', 'Landsdelen', 'nord-norge.html')}
        ${lenke('sammenlign.html', 'Sammenlign', 'sammenlign.html')}
        ${lenke(metode, 'Metode', 'metode.html')}
      </div>
      <div class="nn-verktoy"></div>
    </div></nav>
    <div class="nn-mobilmeny" id="nnMobilmeny" hidden>
      <div class="nn-mm-lenker">${lenke('index.html', 'Forsiden', 'index.html')}${lenke('nord-norge.html', 'Landsdelen', 'nord-norge.html')}${lenke('sammenlign.html', 'Sammenlign', 'sammenlign.html')}${lenke(metode, 'Metode', 'metode.html')}</div>
      <div class="nn-mm-tittel">Temaer</div>
      <div class="nn-temagrid">${temaLenker(side)}</div>
    </div>
    <div class="nn-aktrad" hidden></div>`;
  return hode;
}

// Åpne/lukke-logikk for nedtrekkspanelene (Esc og klikk utenfor lukker)
function panel(knapp, boks, andre = []) {
  const settÅpen = åpen => { knapp.setAttribute('aria-expanded', String(åpen)); boks.hidden = !åpen; if (åpen) andre.forEach(f => f()); };
  knapp.addEventListener('click', e => { e.stopPropagation(); settÅpen(boks.hidden); });
  document.addEventListener('click', e => { if (!boks.hidden && !boks.contains(e.target) && e.target !== knapp) settÅpen(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !boks.hidden) { settÅpen(false); knapp.focus(); } });
  return () => settÅpen(false);
}

// Aktrad: tema-sidenes akter, eller metodekortene på metodesiden
function seksjoner(side) {
  if (side === 'metode.html') {
    return [...document.querySelectorAll('.metode-card')].map((s, i) => {
      const h = s.querySelector('h2'); if (!h) return null;
      if (!s.id) s.id = 'avsnitt-' + (i + 1);
      return { el: s, nr: String(i + 1).padStart(2, '0'), tittel: h.textContent.trim() };
    }).filter(Boolean);
  }
  return [...document.querySelectorAll('section.akt')].map((s, i) => {
    const n = s.querySelector('.akt-num'); if (!n) return null;
    const m = n.textContent.trim().match(/^Akt\s+(\d+)\s*·\s*(.+)$/i);
    const nr = m ? m[1] : String(i + 1).padStart(2, '0'), tittel = m ? m[2] : n.textContent.trim();
    if (!s.id) s.id = 'akt-' + nr;
    return { el: s, nr, tittel };
  }).filter(Boolean);
}

function lagAktrad(hode, side) {
  const S = seksjoner(side);
  const rad = hode.querySelector('.nn-aktrad');
  if (S.length < 3) return null;
  const ord = side === 'metode.html' ? 'Avsnitt' : 'Akt';
  rad.innerHTML = `
    <div class="nn-ar-i">
      <button type="button" class="nn-ar-knapp" aria-expanded="false" aria-controls="nnArListe"><span class="nn-ar-status"></span> <span aria-hidden="true">▾</span></button>
      <ol class="nn-ar-liste" id="nnArListe">${S.map(s => `<li><a href="#${s.el.id}"><span class="nr">${s.nr}</span> ${s.tittel}</a></li>`).join('')}</ol>
    </div>
    <div class="nn-ar-fram"><span></span></div>`;
  const lenker = [...rad.querySelectorAll('.nn-ar-liste a')];
  const status = rad.querySelector('.nn-ar-status'), fram = rad.querySelector('.nn-ar-fram span');
  const knapp = rad.querySelector('.nn-ar-knapp'), liste = rad.querySelector('.nn-ar-liste');
  knapp.addEventListener('click', e => { e.stopPropagation(); const å = knapp.getAttribute('aria-expanded') !== 'true'; knapp.setAttribute('aria-expanded', String(å)); rad.classList.toggle('apen', å); });
  const lukk = () => { knapp.setAttribute('aria-expanded', 'false'); rad.classList.remove('apen'); };
  document.addEventListener('click', e => { if (!rad.contains(e.target)) lukk(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') lukk(); });
  lenker.forEach(a => a.addEventListener('click', lukk));
  let aktiv = -1;
  const oppdater = hodeH => {
    const start = S[0].el.getBoundingClientRect().top;
    const synlig = start < hodeH + 40;
    if (rad.hidden === synlig) { rad.hidden = !synlig; }
    let i = 0;
    S.forEach((s, j) => { if (s.el.getBoundingClientRect().top <= hodeH + 90) i = j; });
    if (i !== aktiv) {
      aktiv = i;
      lenker.forEach((a, j) => a.toggleAttribute('aria-current', j === i));
      status.textContent = `${ord} ${i + 1} av ${S.length} · ${S[i].tittel}`;
      const a = lenker[i];
      if (!window.matchMedia(MOBIL).matches && liste.scrollWidth > liste.clientWidth) liste.scrollTo({ left: a.offsetLeft - liste.clientWidth / 3, behavior: 'smooth' });
    }
    const topp = window.scrollY + start, total = document.documentElement.scrollHeight - window.innerHeight - topp;
    fram.style.width = `${Math.max(0, Math.min(100, ((window.scrollY - topp + hodeH) / Math.max(1, total)) * 100))}%`;
  };
  return oppdater;
}

function brødsmule(tema) {
  const bc = document.querySelector('.nn-top .nn-bc');
  if (!bc || !tema || bc.querySelector('.nn-bc-tema')) return;
  const hjem = bc.querySelector('a[href="index.html"]');
  if (!hjem) return;
  const sep = el('span', { class: 'sep' }, '›');
  const a = el('a', { href: 'index.html#temasider', class: 'nn-bc-tema' }, 'Temaer');
  hjem.after(sep, a);
  const now = bc.querySelector('.now');
  if (now) now.textContent = `${tema.nr} · ${now.textContent}`;
}

function forrigeNeste(side) {
  const i = TEMAER.findIndex(t => t.fil === side);
  if (i < 0 || document.querySelector('.nn-forneste')) return;
  const f = TEMAER[i - 1], n = TEMAER[i + 1];
  const blokk = el('nav', { class: 'nn-forneste', 'aria-label': 'Forrige og neste tema' });
  blokk.innerHTML = (f ? `<a class="f" href="${f.fil}"><span class="r">← Forrige tema</span><span class="t"><span class="nr">${f.nr}</span> ${f.tittel}</span></a>` : '<span></span>')
    + `<a class="alle" href="index.html#temasider">Alle temaer</a>`
    + (n ? `<a class="n" href="${n.fil}"><span class="r">Neste tema →</span><span class="t"><span class="nr">${n.nr}</span> ${n.tittel}</span></a>` : '<span></span>');
  const fot = document.querySelector('.nn-footer');
  if (fot) fot.before(blokk); else document.querySelector('.wrap')?.append(blokk);
}

export function initNav() {
  const side = fil();
  const tema = TEMAER.find(t => t.fil === side);
  const hode = lagStripe(side, tema);
  document.body.prepend(hode);

  // Hoppelenke: første innhold etter sidehodet
  const mål = document.querySelector('.nn-top')?.nextElementSibling || document.querySelector('.wrap > *');
  if (mål && !mål.id) mål.id = 'innhold'; else if (mål) hode.querySelector('.nn-hopp').href = '#' + mål.id;

  const lukkTema = panel(hode.querySelector('.nn-temaknapp'), hode.querySelector('.nn-temapanel'));
  panel(hode.querySelector('.nn-menyknapp'), hode.querySelector('.nn-mobilmeny'), [lukkTema]);

  brødsmule(tema);
  forrigeNeste(side);
  // Fanebytte langt nede på siden: rull til starten av den nye fanen, rett under fanene.
  document.addEventListener('click', e => {
    const knapp = e.target.closest('.nn-secnav button');
    if (!knapp) return;
    setTimeout(() => {
      const fane = document.querySelector('.tab.active'), nav = knapp.closest('.nn-secnav');
      if (!fane) return;
      const topp = fane.getBoundingClientRect().top, bunn = nav.getBoundingClientRect().bottom;
      if (topp < bunn) window.scrollBy({ top: topp - bunn - 8 });
    }, 0);
  });
  const f = new URLSearchParams(location.search).get('f');
  document.querySelectorAll('.nn-fylkevalg a').forEach(a => { if (f && a.href.endsWith('f=' + encodeURIComponent(f))) a.setAttribute('aria-current', 'page'); });

  const stripe = hode.querySelector('.nn-stripe');
  const oppdaterAkt = document.readyState === 'loading' ? null : lagAktrad(hode, side);
  let akt = oppdaterAkt;
  if (!akt) document.addEventListener('DOMContentLoaded', () => { akt = lagAktrad(hode, side); tikk(); });

  // Mobil: stripen skjules når en ruller ned og kommer tilbake når en ruller opp.
  let sistY = window.scrollY, ventende = false;
  const tikk = () => {
    ventende = false;
    const y = window.scrollY, mobil = window.matchMedia(MOBIL).matches;
    const menyÅpen = !hode.querySelector('.nn-mobilmeny').hidden || !hode.querySelector('.nn-temapanel').hidden;
    if (mobil && !menyÅpen && y > 140 && y > sistY + 6) hode.classList.add('skjult');
    else if (!mobil || y < sistY - 6 || y <= 140) hode.classList.remove('skjult');
    sistY = y;
    const h = hode.offsetHeight - (hode.classList.contains('skjult') ? stripe.offsetHeight : 0);
    document.documentElement.style.setProperty('--nn-hode-h', `${h}px`);
    if (akt) akt(h);
  };
  const plan = () => { if (!ventende) { ventende = true; requestAnimationFrame(tikk); } };
  window.addEventListener('scroll', plan, { passive: true });
  window.addEventListener('resize', plan);
  new ResizeObserver(plan).observe(hode);
  tikk();
}

// Søk og lys/mørk-bryteren monteres i stripen (søket og tema.js kaller denne).
export function verktøyPlass() {
  return document.querySelector('.nn-stripe .nn-verktoy');
}
