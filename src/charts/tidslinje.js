// Tidslinje med ett felt per kategori: nummererte punkter, og perioder som tykke streker.
// Spesifikasjon: { fra, til, kategorier:[{id, navn, farge}], punkter:[{nr, kat, aar, til?, tekst, etikett}], hoyde }
// «aar» kan ha desimaler (2026.3 = våren 2026). «til» gir en periode fra aar til til; nummeret står ved starten.
import { Plot, register, spec } from './core.js';

register('tidslinje', (el, width) => {
  const s = spec(el);
  const kat = s.kategorier;
  const farge = new Map(kat.map(k => [k.id, k.farge]));
  const navn = new Map(kat.map(k => [k.id, k.navn]));
  const smal = width < 560;
  const left = smal ? 4 : 120;
  const rh = smal ? 46 : 36;
  const p = s.punkter;
  const perioder = p.filter(d => d.til);
  const fig = Plot.plot({
    width, height: kat.length * rh + 34, marginLeft: left, marginRight: 18, marginTop: 6, marginBottom: 28,
    style: { background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: '11.5px', color: 'var(--ink-2)', overflow: 'visible' },
    x: { domain: [s.fra, s.til], ticks: smal ? [2026, 2030, 2035, 2040] : [2026, 2028, 2030, 2032, 2034, 2036, 2038, 2040], tickFormat: d => String(d), label: null },
    y: { domain: kat.map(k => k.id), tickFormat: k => navn.get(k), tickSize: 0, padding: 0.5, label: null, axis: smal ? null : 'left' },
    marks: [
      Plot.ruleY(kat.map(k => k.id), { stroke: 'var(--line-soft)' }),
      smal && Plot.text(kat, { y: 'id', x: s.fra, text: 'navn', dy: -15, textAnchor: 'start', fill: 'var(--ink-3)', fontSize: 11 }),
      Plot.ruleY(perioder, { y: 'kat', x1: 'aar', x2: 'til', stroke: d => farge.get(d.kat), strokeWidth: 6, strokeOpacity: 0.45 }),
      Plot.dot(p, { x: 'aar', y: 'kat', r: 9.5, fill: d => farge.get(d.kat), stroke: 'var(--panel)', strokeWidth: 1.5 }),
      Plot.dot(perioder, { x: 'til', y: 'kat', r: 4, fill: d => farge.get(d.kat) }),
      Plot.text(p, { x: 'aar', y: 'kat', text: d => String(d.nr), fill: '#fff', stroke: 'rgba(5,28,44,0.75)', strokeWidth: 2.5, paintOrder: 'stroke', fontWeight: 700, fontSize: 10.5 }),
      Plot.tip(p, Plot.pointer({ x: 'aar', y: 'kat', title: d => `${d.nr}. ${d.etikett}\n${d.tekst}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
  });
  return fig;
});
