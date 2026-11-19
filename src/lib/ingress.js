// Kortere ingresser (PLAN-LAYOUT-1-3.md, fase C): innledningen i hver akt (.akt-intro) kortes til høyst 80 ord og
// heroens ingress til høyst 60, ved slutten av en setning. Resten flyttes uendret til en lukket «Les mer»-boks rett
// under, så ingen tall eller formuleringer forsvinner. Elementer med data-ingress="hel" (akter om grunnlaget, som
// bare består av forbehold) røres ikke, og en rest på 15 ord eller mindre blir stående.
// Kjøres etter sidens egne skript, som fyller mange av ingressene.

const GRENSE_AKT = 80;
const GRENSE_HERO = 60;
const MINSTE_REST = 15;
const ord = html => html.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').split(/\s+/).filter(Boolean).length;

// Deler HTML i setninger: punktum, spørsmåls- eller utropstegn (eventuelt etter » eller lukkende tagg),
// fulgt av mellomrom og stor bokstav, «, ( eller en åpnende tagg. Tall etter punktum («s. 16») deler ikke.
function setninger(html) {
  return html.split(/(?<=[.!?](?:»|<\/[a-z]+>)?)\s+(?=[A-ZÆØÅÄÖ«(]|<(?:b|i|em|strong|a)\b)/);
}

function kort(el, grense) {
  if (!el || el.dataset.ingress === 'hel' || el.dataset.ingressKortet) return;
  const html = el.innerHTML.trim();
  if (ord(html) <= grense) return;
  const deler = setninger(html);
  if (deler.length < 2) return;
  let n = 0, i = 0;
  while (i < deler.length && (i === 0 || n + ord(deler[i]) <= grense)) { n += ord(deler[i]); i++; }
  if (i >= deler.length) return;
  // en rest på 15 ord eller mindre gir ingen egen «Les mer»-boks; teksten blir stående samlet
  if (ord(deler.slice(i).join(' ')) <= MINSTE_REST) return;
  el.innerHTML = deler.slice(0, i).join(' ');
  el.dataset.ingressKortet = '1';
  const mer = document.createElement('details');
  mer.className = 'nn-mer';
  mer.innerHTML = '<summary>Les mer</summary><p>' + deler.slice(i).join(' ') + '</p>';
  el.insertAdjacentElement('afterend', mer);
}

export function initIngress() {
  document.addEventListener('DOMContentLoaded', () => setTimeout(() => {
    if (!document.body.classList.contains('tema-page')) return;
    document.querySelectorAll('section.akt .akt-intro').forEach(el => kort(el, GRENSE_AKT));
    kort(document.querySelector('.tema-hero .lede'), GRENSE_HERO);
  }, 0));
}
