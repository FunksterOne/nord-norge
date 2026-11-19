// Tabeller på smale skjermer (LAYOUT-VURDERING.md, anbefaling 04): tabeller i en sidelengs rullende boks får
// låst første kolonne og et synlig tegn på at de kan rulles (skygge i kanten + «Rull sidelengs»-linje).
// Gjelder alle temasider, uansett hvilken rulleboks sidene bruker (nn-tabell-rull, pj-scroll, fb-scroll m.fl.).

function rullbar(el) {
  const o = getComputedStyle(el).overflowX;
  return o === 'auto' || o === 'scroll';
}

function oppdater(boks) {
  const kan = boks.scrollWidth > boks.clientWidth + 4;
  boks.classList.toggle('nn-kan-rulle', kan);
  boks.classList.toggle('nn-ved-start', boks.scrollLeft < 4);
  boks.classList.toggle('nn-ved-slutt', boks.scrollLeft + boks.clientWidth >= boks.scrollWidth - 4);
  const hint = boks.previousElementSibling;
  if (hint && hint.classList.contains('nn-rull-hint')) hint.hidden = !kan;
}

function klargjor(tabell) {
  const boks = tabell.parentElement;
  if (!boks || !rullbar(boks) || boks.dataset.nnRull) return;
  boks.dataset.nnRull = '1';
  boks.classList.add('nn-rulleboks');
  tabell.classList.add('nn-laas-kol');
  const hint = document.createElement('div');
  hint.className = 'nn-rull-hint';
  hint.textContent = 'Rull sidelengs for flere kolonner →';
  hint.hidden = true;
  boks.insertAdjacentElement('beforebegin', hint);
  boks.addEventListener('scroll', () => oppdater(boks), { passive: true });
  oppdater(boks);
}

export function initTabeller() {
  const kjor = () => document.querySelectorAll('section.akt table').forEach(klargjor);
  document.addEventListener('DOMContentLoaded', () => {
    // tabeller fylles av sidenes skript; vent til de er tegnet, og hold følge med endrede bredder
    setTimeout(kjor, 50);
    setTimeout(kjor, 1500);
    window.addEventListener('resize', () => document.querySelectorAll('.nn-rulleboks').forEach(oppdater));
  });
}
