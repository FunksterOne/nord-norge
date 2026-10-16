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

// Grådig etikettplassering uten kollisjon. items: [{x, y, r, text}] i dataenheter.
// Bruker skalaene fra en ferdig tegnet figur; returnerer [{x, y, text, anchor}] i dataenheter.
export function placeLabels(fig, items, { font = 11, pad = 3 } = {}) {
  const sx = fig.scale('x'), sy = fig.scale('y');
  if (!sx || !sy) return [];
  const boxes = [];
  const hit = b => boxes.some(o => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0);
  // punktene selv er hindringer
  for (const it of items) {
    const px = sx.apply(it.x), py = sy.apply(it.y), r = it.r || 4;
    boxes.push({ x0: px - r, x1: px + r, y0: py - r, y1: py + r });
  }
  const out = [];
  const sorted = [...items].sort((a, b) => (b.prio || 0) - (a.prio || 0));
  for (const it of sorted) {
    const px = sx.apply(it.x), py = sy.apply(it.y), r = (it.r || 4) + pad;
    const w = it.text.length * font * 0.58, h = font + 2;
    const cand = [
      { cx: px, cy: py - r - h / 2, anchor: 'middle' },
      { cx: px, cy: py + r + h / 2, anchor: 'middle' },
      { cx: px + r + w / 2, cy: py, anchor: 'start' },
      { cx: px - r - w / 2, cy: py, anchor: 'end' },
    ];
    for (const c of cand) {
      const b = { x0: c.cx - w / 2, x1: c.cx + w / 2, y0: c.cy - h / 2, y1: c.cy + h / 2 };
      if (hit(b)) continue;
      boxes.push(b);
      const ax = c.anchor === 'start' ? b.x0 : c.anchor === 'end' ? b.x1 : c.cx;
      out.push({ x: sx.invert ? sx.invert(ax) : it.x, y: sy.invert(c.cy), text: it.text, anchor: c.anchor });
      break;
    }
  }
  return out;
}
