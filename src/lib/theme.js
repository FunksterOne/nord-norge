// Mørk er standard. Lys lagres som valg i localStorage («nn-tema»).
const KEY = 'nn-tema';

export function currentTheme() {
  return document.documentElement.getAttribute('data-tema') === 'light' ? 'light' : 'dark';
}

function setTheme(t) {
  const html = document.documentElement;
  if (t === 'light') html.setAttribute('data-tema', 'light');
  else html.removeAttribute('data-tema');
  try { localStorage.setItem(KEY, t); } catch (_) { /* privat modus */ }
  window.dispatchEvent(new CustomEvent('nn:tema', { detail: t }));
}

function label(btn) {
  const t = currentTheme();
  btn.querySelector('.tb-txt').textContent = t === 'dark' ? 'Lys visning' : 'Mørk visning';
  btn.setAttribute('aria-pressed', String(t === 'light'));
}

export function initTheme() {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'tema-bryter';
  btn.innerHTML = '<span class="tb-dot" aria-hidden="true"></span><span class="tb-txt"></span>';
  btn.addEventListener('click', () => { setTheme(currentTheme() === 'dark' ? 'light' : 'dark'); label(btn); });
  label(btn);
  const mount = () => {
    const host = document.querySelector('.nn-top .nn-actions');
    if (host) host.appendChild(btn);
    else { btn.classList.add('tema-bryter-fast'); document.body.appendChild(btn); }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
}
