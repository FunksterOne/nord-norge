// Generelt stolpediagram (loddrett, gruppert eller enkelt).
// Spesifikasjon: { kategorier:[…], serier:[{navn, data:[…], farge}], format:'tall'|'pst'|'endring',
//                  aksetekst:[…] (valgfri kortere x-etiketter; tom streng skjuler), hoyde, kilde, yTittel }
import { Plot, base, register, spec } from './core.js';
import { heltall, tall, endring } from '../lib/format.js';

const FARGE = f => (!f ? 'var(--muted-mark)' : f.startsWith('var(') ? f : ({ accent: 'var(--accent)', ink: 'var(--ink)', neg: 'var(--neg)', pos: 'var(--pos)', warn: 'var(--warn)', muted: 'var(--muted-mark)' })[f] || `var(--${f})`);
const FMT = { tall: v => heltall(v), pst: v => `${tall(v, 1)} %`, endring: v => endring(Math.round(v), 0) };

register('stolper', (el, width) => {
  const s = spec(el);
  const fmt = FMT[s.format || 'tall'];
  const rows = [];
  s.serier.forEach((se, si) => se.data.forEach((v, i) => { if (v != null) rows.push({ k: s.kategorier[i], v, serie: se.navn, si, i }); }));
  const grupper = s.serier.length > 1;
  const etikett = new Map(s.kategorier.map((k, i) => [k, s.aksetekst ? s.aksetekst[i] : k]));
  const fig = Plot.plot(base({
    width, height: s.hoyde || 260, marginRight: 16, marginBottom: 28,
    ...(grupper
      ? { fx: { label: null, tickSize: 0, padding: 0.18, tickFormat: k => etikett.get(k) ?? k, domain: s.kategorier }, x: { axis: null, domain: s.serier.map(se => se.navn), padding: 0.08 } }
      : { x: { domain: s.kategorier, padding: 0.25, tickFormat: k => etikett.get(k) ?? k } }),
    y: { nice: true, tickFormat: fmt },
    color: { domain: s.serier.map(se => se.navn), range: s.serier.map(se => FARGE(se.farge)) },
    marks: [
      Plot.ruleY([0], { stroke: 'var(--line)' }),
      grupper
        ? Plot.barY(rows, { fx: 'k', x: 'serie', y: 'v', fill: 'serie' })
        : Plot.barY(rows, { x: 'k', y: 'v', fill: d => FARGE(s.serier[0].farge) }),
      Plot.tip(rows, Plot.pointer({ ...(grupper ? { fx: 'k', x: 'serie' } : { x: 'k' }), y: 'v', title: d => `${d.k}\n${d.serie}: ${fmt(d.v)}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ],
  }));
  const out = [fig];
  if (grupper) {
    const leg = document.createElement('div'); leg.className = 'nn-legend';
    leg.innerHTML = s.serier.map(se => `<span><i style="background:${FARGE(se.farge)}"></i>${se.navn}</span>`).join('');
    out.push(leg);
  }
  if (s.yTittel) { const t = document.createElement('div'); t.className = 'nn-chart-note'; t.textContent = s.yTittel; out.unshift(t); }
  if (s.kilde) { const k = document.createElement('div'); k.className = 'nn-source'; k.textContent = s.kilde; out.push(k); }
  return out;
});
