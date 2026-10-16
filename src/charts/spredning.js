// Spredningsdiagram for kommuner: x (gjerne log), y, sirkelstørrelse = folketall, farge = fylke.
// Spesifikasjon: { pts:[{nr,navn,fylke,x,y,pop,merk}], xLog, xTittel, yTittel, refY, refTekst, yFmt:'tall1'|'pst' }
import { Plot, base, register, spec, placeLabels } from './core.js';
import { heltall, tall, kortNavn } from '../lib/format.js';

const FY = { Nordland: 'var(--fy-nordland)', Troms: 'var(--fy-troms)', Finnmark: 'var(--fy-finnmark)' };

register('spredning', (el, width) => {
  const s = spec(el);
  const yF = s.yFmt === 'pst' ? (v => `${tall(v, 1)} %`) : (v => tall(v, 1));
  const pts = s.pts.map(p => ({ ...p, kort: kortNavn(p.navn) }));
  const merk = pts.filter(p => p.merk);
  const opts = (labels) => base({
    width, height: Math.max(380, Math.min(500, width * 0.55)), marginLeft: 50, marginTop: 34, marginRight: 24, marginBottom: 44,
    x: { type: s.xLog ? 'log' : 'linear', label: s.xTittel ? `${s.xTittel} →` : null, labelAnchor: 'right', labelOffset: 36, tickFormat: v => heltall(v), ticks: s.xLog ? [500, 1000, 2000, 5000, 10000, 20000, 50000] : 6 },
    y: { label: s.yTittel ? `↑ ${s.yTittel}` : null, labelAnchor: 'top', tickFormat: v => tall(v, 0), nice: true },
    r: { range: [2.5, 16] },
    marks: [
      s.refY != null && Plot.ruleY([s.refY], { stroke: 'var(--ink-3)', strokeDasharray: '5,3' }),
      s.refY != null && Plot.text([s.refY], { y: d => d, frameAnchor: 'left', dx: 4, dy: 10, text: () => s.refTekst || '', fill: 'var(--ink-2)', fontSize: 11, textAnchor: 'start' }),
      Plot.dot(pts, { x: 'x', y: 'y', r: 'pop', fill: d => FY[d.fylke], fillOpacity: 0.7, stroke: 'var(--bg)', strokeWidth: 1 }),
      ...(labels ? ['start', 'middle', 'end'].map(a => Plot.text(labels.filter(l => l.anchor === a), { x: 'x', y: 'y', text: 'text', textAnchor: a, fill: 'var(--ink)', fontSize: 11, fontWeight: 600 })) : []),
      Plot.tip(pts, Plot.pointer({ x: 'x', y: 'y', title: d => `${d.kort} (${d.fylke})\n${s.yTittel || 'Verdi'}: ${yF(d.y)}\nFolketall: ${heltall(d.pop)}`, fill: 'var(--raised)', stroke: 'var(--line)' })),
    ].filter(Boolean),
  });
  const first = Plot.plot(opts(null));
  const rr = first.scale('r');
  const labels = placeLabels(first, merk.map(p => ({ x: p.x, y: p.y, r: rr ? rr.apply(p.pop) : 5, text: p.kort, prio: p.pop })));
  const fig = Plot.plot(opts(labels));

  fig.style.cursor = 'pointer';
  fig.addEventListener('click', () => { const v = fig.value; if (v && v.nr) location.href = `kommune.html?k=${v.nr}`; });
  const leg = document.createElement('div'); leg.className = 'nn-legend';
  leg.innerHTML = Object.entries(FY).map(([f, c]) => `<span><i style="background:${c};border-radius:50%;width:10px"></i>${f}</span>`).join('') + '<span class="nn-legend-note">Sirkelflate = folketall. Klikk en sirkel for kommunesiden.</span>';
  return [fig, leg];
});
