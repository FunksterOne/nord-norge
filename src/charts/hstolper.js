// Liggende stolper, eventuelt i grupper med egen tittel.
// Spesifikasjon: { grupper:[{tittel, rader:[{l, v, farge, uthev, note}] , ref:{v, tekst}}],
//                  format:'tall'|'pst'|'pst0'|'pst2', maks, farge, etikettBredde }
// Stolpetykkelsen er fast (rundt 14 px) uansett antall rader, slik at figurene ser like ut på tvers av sidene.
// Negative verdier tegnes mot venstre fra en nullinje. Verdien står til venstre for stolpen, men når
// etiketten ligger over stolpen, står den til høyre for nullinjen så den ikke kolliderer med etiketten.
import { Plot, register, spec } from './core.js';
import { heltall, tall } from '../lib/format.js';

const FARGE = f => (!f ? 'var(--muted-mark)' : f.startsWith('var(') || f.startsWith('color-mix') ? f : ({ accent: 'var(--accent)', ink: 'var(--ink)', neg: 'var(--neg)', pos: 'var(--pos)', warn: 'var(--warn)', muted: 'var(--muted-mark)' })[f] || `var(--${f})`);
const MINUS = '−';
const FMT = {
  tall1: v => tall(v, 1), tall: v => heltall(v), kr: v => `${heltall(v)} kr`,
  pst: v => `${tall(v, 1)} %`, pst0: v => `${tall(v, 0)} %`, pst2: v => `${tall(v, 2)} %`,
};
const tekstBredde = (s, px) => String(s).length * px * 0.56;

register('hstolper', (el, width) => {
  const s = spec(el);
  const fmt0 = FMT[s.format || 'tall'];
  const fmt = v => (v < 0 ? MINUS + fmt0(-v) : fmt0(v));
  const alle = s.grupper.flatMap(g => g.rader).filter(r => r.v != null);
  const refs = s.grupper.flatMap(g => [g.ref, ...(g.refs || [])].filter(Boolean));
  const neg = alle.some(r => r.v < 0);
  const maks = s.maks || Math.max(neg ? 0 : 1, ...alle.map(r => r.v), ...refs.map(r => r.v));
  const min = neg ? Math.min(...alle.map(r => r.v)) : 0;
  const longest = Math.max(4, ...s.grupper.flatMap(g => g.rader.map(r => String(r.l).length)));
  // Etiketten legges over stolpen når diagrammet har merknader (merknaden står da på etikettlinjen,
  // så stolpene får hele bredden), og på smale skjermer når lange etiketter ikke får plass til venstre.
  const harNoter = alle.some(r => r.note);
  const smal = width < 600;
  const over = !s.etikettBredde && (harNoter || (smal && 14 + longest * 6.6 > width * 0.42));
  const left = over ? 4 : s.etikettBredde || Math.min(Math.round(width * 0.42), 14 + longest * 6.6);
  // Bred skjerm: merknaden høyrejusteres på etikettlinjen. Smal skjerm: den henges på etter etiketten.
  const etikett = r => fmt(r.v) + (r.note && !over ? `  ${r.note}` : '');
  // Smal skjerm: får ikke etikett og merknad plass på én linje, legges merknaden på en egen linje under stolpen.
  const toLinjer = over && smal && harNoter && alle.some(r => r.note && tekstBredde(`${r.l} · ${r.note}`, 11.5) > width - 8);
  const radTekst = r => r.l + (r.note && over && smal && !toLinjer ? ` · ${r.note}` : '');
  const noteHøyre = over && harNoter && !smal;
  const høyreTekst = Math.max(40, ...alle.filter(r => r.v >= 0).map(r => tekstBredde(etikett(r), 11.5)));
  const venstreTekst = neg && !over ? Math.max(40, ...alle.filter(r => r.v < 0).map(r => tekstBredde(etikett(r), 11.5))) : 0;
  const right = Math.min(Math.round(width * 0.38), Math.round(høyreTekst + 18));
  const out = [];
  for (const g of s.grupper) {
    const n = g.rader.length;
    const tett = n > 40;
    const overHer = over && !tett;
    const rh = tett ? 15 : overHer ? (toLinjer ? 48 : 34) : 22;
    const harRef = !!(g.ref || g.refs);
    const rader = g.rader.map((r, i) => ({ ...r, key: `${i}\u0000${r.l}` }));
    const vals = rader.filter(r => r.v != null);
    const tom = rader.filter(r => r.v == null);
    if (g.tittel) {
      const t = document.createElement('div'); t.className = 'nn-hst-tittel'; t.textContent = g.tittel; out.push(t);
    }
    const fig = Plot.plot({
      width, height: n * rh + (harRef ? 30 : 12), marginLeft: overHer ? 4 : left, marginRight: right, marginTop: harRef ? 22 : 4, marginBottom: 6,
      style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: tett ? '10px' : '12px', color: 'var(--ink-2)', overflow: 'visible' },
      x: { domain: [min, maks], axis: null, insetLeft: venstreTekst ? venstreTekst + 16 : 0 },
      y: { domain: rader.map(r => r.key), tickFormat: k => k.split('\u0000')[1], tickSize: 0, paddingInner: tett ? 0.12 : overHer ? (toLinjer ? 0.7 : 0.6) : 0.36, paddingOuter: overHer ? 0.5 : 0.18, label: null, axis: overHer ? null : undefined },
      marks: [
        !neg && Plot.barX(rader, { x: maks, y: 'key', fill: 'var(--line-soft)' }),
        neg && Plot.ruleX([0], { stroke: 'var(--line)' }),
        Plot.barX(vals, { x: 'v', y: 'key', fill: r => FARGE(r.farge || (r.uthev ? 'accent' : s.farge)) }),
        ...[g.ref, ...(g.refs || [])].filter(Boolean).flatMap((r, ri) => [
          Plot.ruleX([r.v], { stroke: r.farge || 'var(--ink-3)', strokeDasharray: '3,3' }),
          Plot.text([r.v], { x: d => d, frameAnchor: 'top', dy: ri % 2 ? -2 : -12, text: () => r.tekst, fill: r.farge || 'var(--ink-3)', fontSize: 11 }),
        ]),
        Plot.text(vals.filter(r => r.v >= 0), { x: 'v', y: 'key', text: etikett, dx: 6, textAnchor: 'start', fill: r => (r.uthev ? 'var(--ink)' : 'var(--ink-2)'), fontWeight: r => (r.uthev ? 600 : 400), fontSize: tett ? 10 : 11.5 }),
        Plot.text(vals.filter(r => r.v < 0), { x: overHer ? 0 : 'v', y: 'key', text: etikett, dx: overHer ? 6 : -6, textAnchor: overHer ? 'start' : 'end', fill: r => (r.uthev ? 'var(--ink)' : 'var(--ink-2)'), fontWeight: r => (r.uthev ? 600 : 400), fontSize: tett ? 10 : 11.5 }),
        overHer && Plot.text(rader, { y: 'key', frameAnchor: 'left', text: radTekst, dy: -14, textAnchor: 'start', fill: r => (r.uthev ? 'var(--ink)' : 'var(--ink-2)'), fontWeight: r => (r.uthev ? 600 : 400), fontSize: 11.5 }),
        overHer && toLinjer && Plot.text(rader.filter(r => r.note), { y: 'key', frameAnchor: 'left', text: 'note', dy: 15, textAnchor: 'start', fill: 'var(--ink-3)', fontSize: 10.5 }),
        overHer && noteHøyre && Plot.text(rader.filter(r => r.note), { y: 'key', frameAnchor: 'right', text: 'note', dy: -14, textAnchor: 'end', fill: 'var(--ink-3)', fontSize: 11 }),
        tom.length && Plot.text(tom, { x: 0, y: 'key', text: () => 'undertrykt', dx: 6, textAnchor: 'start', fill: 'var(--ink-3)', fontSize: 11 }),
        Plot.tip(vals, Plot.pointerY({ x: 'v', y: 'key', title: r => `${r.l}\n${fmt(r.v)}${r.note ? `\n${r.note}` : ''}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
      ].filter(Boolean),
    });
    out.push(fig);
  }
  if (s.kilde) { const k = document.createElement('div'); k.className = 'nn-source'; k.textContent = s.kilde; out.push(k); }
  return out;
});
