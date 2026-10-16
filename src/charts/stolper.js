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
  // Stolpene skal aldri bli bredere enn MAKS_BREDDE px, uansett hvor få kategorier det er.
  const MAKS_BREDDE = 48;
  const plotW = width - 16 - (s.ingenY ? 6 : 56);
  const nk = s.kategorier.length, ns = s.serier.length;
  const fxPad = 0.18;
  const fw = (plotW / nk) * (1 - fxPad);
  const grPi = 0.12, grStep = Math.min(fw / ns, MAKS_BREDDE / (1 - grPi));
  const grPo = Math.max(0, (fw / grStep - ns + grPi) / 2);
  const pad = grupper
    ? 0
    : Math.min(0.88, Math.max(0.25, 1 - (MAKS_BREDDE * nk) / plotW));
  const fig = Plot.plot(base({
    width, height: s.hoyde || 260, marginRight: 16, marginBottom: s.ingenAkse ? 6 : 28, marginLeft: s.ingenY ? 6 : 56, marginTop: s.verdier ? 22 : 22,
    ...(grupper
      ? { fx: { label: null, tickSize: 0, padding: fxPad, tickFormat: k => etikett.get(k) ?? k, domain: s.kategorier }, x: { axis: null, domain: s.serier.map(se => se.navn), paddingInner: grPi, paddingOuter: grPo } }
      : { x: { domain: s.kategorier, padding: pad, tickFormat: k => etikett.get(k) ?? k, axis: s.ingenAkse ? null : undefined } }),
    y: s.ingenY ? { axis: null, nice: true } : { nice: true, tickFormat: fmt },
    color: { domain: s.serier.map(se => se.navn), range: s.serier.map(se => FARGE(se.farge)) },
    marks: [
      Plot.ruleY([0], { stroke: 'var(--line)' }),
      grupper
        ? Plot.barY(rows, { fx: 'k', x: 'serie', y: 'v', fill: 'serie' })
        : Plot.barY(rows, { x: 'k', y: 'v', fill: d => FARGE((s.serier[0].fargePer && s.serier[0].fargePer[d.i]) || s.serier[0].farge) }),
      s.verdier && !grupper && Plot.text(rows, { x: 'k', y: 'v', text: d => fmt(d.v), dy: -8, fill: 'var(--ink-2)', fontSize: 11 }),
      Plot.tip(rows, Plot.pointer({ ...(grupper ? { fx: 'k', x: 'serie' } : { x: 'k' }), y: 'v', title: d => `${d.k}\n${d.serie}: ${fmt(d.v)}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
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
