// Felles diagrammotor. Gammel kode setter inn plassholdere:
//   <div data-nnchart="navn" data-...></div>
// En MutationObserver finner dem, tegner med Observable Plot og tegner på nytt
// når bredden endres. Farger er CSS-variabler, så temabytte krever ingen omtegning.
import * as Plot from '@observablehq/plot';
import { akse } from '../lib/format.js';

const registry = new Map();
export function register(name, render) { registry.set(name, render); }

// McHalvard-standard for alle Plot-figurer
export function base(opts = {}) {
  return {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: '12px',
      color: 'var(--ink-3)',
      background: 'transparent',
      overflow: 'visible',
    },
    marginLeft: 56,
    marginRight: 76,
    marginTop: 22,
    marginBottom: 30,
    ...opts,
    y: { tickFormat: akse, ticks: 5, grid: false, label: null, tickSize: 0, ...(opts.y || {}) },
    x: { label: null, tickSize: 0, ...(opts.x || {}) },
  };
}
export { Plot };

function draw(el) {
  const render = registry.get(el.dataset.nnchart);
  if (!render) return;
  const width = Math.max(280, Math.floor(el.clientWidth || el.parentElement?.clientWidth || 720));
  if (el.__w === width && el.__drawn) return;
  el.__w = width;
  try {
    const node = render(el, width);
    el.replaceChildren(...(Array.isArray(node) ? node : [node]).filter(Boolean));
    el.__drawn = true;
  } catch (err) {
    console.error('Diagramfeil', el.dataset.nnchart, err);
    el.textContent = 'Diagrammet kunne ikke tegnes.';
  }
}

const ro = new ResizeObserver(entries => {
  for (const e of entries) {
    const el = e.target;
    clearTimeout(el.__t);
    el.__t = setTimeout(() => draw(el), 80);
  }
});

function scan(root) {
  const list = root.matches?.('[data-nnchart]') ? [root] : [];
  root.querySelectorAll?.('[data-nnchart]').forEach(n => list.push(n));
  for (const el of list) {
    if (el.__mounted) continue;
    el.__mounted = true;
    draw(el);
    ro.observe(el);
  }
}

export function redraw(el) { el.__drawn = false; el.__w = 0; draw(el); }

export function startCharts() {
  const go = () => {
    scan(document.body);
    new MutationObserver(muts => {
      for (const m of muts) for (const n of m.addedNodes) if (n.nodeType === 1) scan(n);
    }).observe(document.body, { childList: true, subtree: true });
  };
  // Vent til de utsatte klassiske skriptene (app.js) har kjørt: de bygger K og AGG.
  if (document.readyState === 'complete') go();
  else document.addEventListener('DOMContentLoaded', go, { once: true });
}

// Hjelper for gammel kode: lag plassholder-HTML med JSON-spesifikasjon
export function placeholder(name, spec = {}, height = 300) {
  const json = JSON.stringify(spec).replace(/'/g, '&#39;');
  return `<div class="nnchart" data-nnchart="${name}" data-spec='${json}' style="min-height:${height}px"></div>`;
}
export function spec(el) {
  try { return JSON.parse(el.dataset.spec || '{}'); } catch { return {}; }
}
