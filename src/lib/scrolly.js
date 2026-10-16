// Rullestyrt fortelling: kartet står fast, tekststegene ruller forbi og bytter indikator.
// <section class="nn-scrolly" data-scrolly="fire-kart"></section>
import { L } from './legacy.js';
import { tall, prosent, endringPst, kortNavn } from './format.js';
import { redraw } from '../charts/core.js';

const median = a => { const b = [...a].sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };

function fakta() {
  const P = L.DATA.proj;
  const ks = L.K.map(k => {
    const o = P.kommuner[k.nr]; const n = o.a65.length - 1;
    return {
      k, navn: kortNavn(k.navn),
      endr: (o.main[o.main.length - 1] / o.main[0] - 1) * 100,
      a65: k.alder.slice(65).reduce((a, b) => a + b, 0) / k.pop * 100,
      fb: o.a65[n] / o.a2064[n] * 100, fb0: o.a65[0] / o.a2064[0] * 100,
      innv: k.andel,
    };
  });
  const top = (f, n = 2, asc = false) => [...ks].sort((a, b) => asc ? a[f] - b[f] : b[f] - a[f]).slice(0, n);
  const R = P.robek || { kommuner: {} };
  const robekNavn = Object.keys(R.kommuner).map(nr => kortNavn(L.K.find(k => k.nr === +nr)?.navn || nr));
  return { ks, top, R, robekNavn };
}

function steg() {
  const f = fakta();
  const ned = f.ks.filter(x => x.endr < 0).length;
  const [v1, v2] = f.top('endr'); const [n1, n2] = f.top('endr', 2, true);
  const [e1] = f.top('a65'); const [u1, u2] = f.top('a65', 2, true);
  const [b1] = f.top('fb');
  const over70 = f.ks.filter(x => x.fb > 70).length;
  const [i1, i2, i3] = f.top('innv', 3);
  const fyNavn = f.R.oppdatert ? f.R.oppdatert.split('.').map(Number) : null;
  const dato = fyNavn ? new Date(fyNavn[2], fyNavn[1] - 1, fyNavn[0]).toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' }) : '';
  return [
    { ind: 'endring', kicker: '01 · Folketall',
      h: `${ned} av 80 kommuner får færre innbyggere mot 2050`,
      p: `SSBs hovedalternativ gir landsdelen nesten uendret folketall samlet, men fordelingen er skjev. Størst nedgang ventes i ${n1.navn} (${endringPst(n1.endr, 0)}) og ${n2.navn} (${endringPst(n2.endr, 0)}). De høyeste vekstratene ventes i små kommuner som ${v1.navn} og ${v2.navn}, der små tall gir store prosentutslag.` },
    { ind: 'eldre', kicker: '02 · Aldring i dag',
      h: `I den typiske kommunen er hver fjerde innbygger 65 år eller eldre`,
      p: `Medianen er ${prosent(median(f.ks.map(x => x.a65)), 1)}. Høyest er ${e1.navn} med ${prosent(e1.a65, 1)}; lavest er ${u1.navn} og ${u2.navn} med ${prosent(u1.a65, 1)}. Byene trekker til seg de unge — distriktene eldes først.` },
    { ind: 'forsorg', kicker: '03 · Forsørgerbyrde 2050',
      h: `Fra ${tall(median(f.ks.map(x => x.fb0)), 0)} til ${tall(median(f.ks.map(x => x.fb)), 0)} eldre per 100 i yrkesaktiv alder`,
      p: `Slik endres medianen fra 2026 til 2050 i SSBs hovedalternativ. I ${over70} kommuner passerer forholdet 70 eldre per 100 yrkesaktive; høyest i ${b1.navn} med ${tall(b1.fb, 0)}. Det er her bemanningen i pleie og omsorg blir hardest å løse.` },
    { ind: 'innv', kicker: '04 · Innvandring',
      h: `Innvandring holder folketallet oppe i mange småsamfunn`,
      p: `Medianandelen med innvandrerbakgrunn er ${prosent(median(f.ks.map(x => x.innv)), 1)}. Høyest er ${i1.navn} (${prosent(i1.innv, 1)}), ${i2.navn} og ${i3.navn}. Uten innvandringen siden 2002 ville nedgangen vært langt større — se temasiden om flytting.` },
    { ind: 'robek', kicker: '05 · Kommuneøkonomi',
      h: `${f.robekNavn.length} kommuner står under statlig økonomisk kontroll`,
      p: `Per ${dato} er ${f.robekNavn.length} av de 80 kommunene registrert i ROBEK: ${f.robekNavn.join(', ')}. Når folketallet krymper og omsorgsbehovet vokser, blir handlingsrommet trangere.` },
  ];
}

function build(sec) {
  const steps = steg();
  const h = window.innerWidth < 860 ? Math.round(Math.min(340, window.innerHeight * 0.42)) : Math.round(Math.min(560, Math.max(460, window.innerHeight - 120)));
  sec.innerHTML = `
    <div class="nn-scrolly-graf"><div data-nnchart="kart" data-spec='${JSON.stringify({ ind: steps[0].ind, side: false, height: h })}' style="min-height:${h}px"></div></div>
    <div class="nn-scrolly-steg">${steps.map((s, i) => `
      <article class="nn-steg${i === 0 ? ' aktiv' : ''}" data-ind="${s.ind}">
        <div class="kicker">${s.kicker}</div>
        <h3>${s.h}</h3>
        <p>${s.p}</p>
      </article>`).join('')}
    </div>`;
  const chart = sec.querySelector('[data-nnchart]');
  const graf = sec.querySelector('.nn-scrolly-graf');
  const artikler = [...sec.querySelectorAll('.nn-steg')];
  let current = steps[0].ind;
  let aktiv = 0;

  // Kartflaten skal ikke hoppe når forklaringen bytter høyde (ROBEK har lavere forklaring enn fargeskalaene).
  // På smal skjerm kan forklaringsteksten brytes over to linjer for enkelte indikatorer; den plassen settes av fra start.
  // Flaten måles etter at kartet er tegnet. Tillegget for smal skjerm legges bare på én gang, så sløyfen
  // ResizeObserver → minstehøyde → ResizeObserver stopper av seg selv (ny høyde = lagret høyde).
  let størst = 0;
  const lås = () => {
    if (!chart.querySelector('svg')) return; // plassholderen før tegning skal ikke telle
    const h0 = graf.getBoundingClientRect().height + (størst === 0 && window.innerWidth < 860 ? 26 : 0);
    if (h0 > størst + 1) { størst = h0; graf.style.minHeight = `${Math.ceil(h0)}px`; }
  };
  new MutationObserver(lås).observe(chart, { childList: true });
  new ResizeObserver(lås).observe(graf);

  const bytt = i => {
    if (i === aktiv) return;
    aktiv = i;
    artikler.forEach((a, j) => a.classList.toggle('aktiv', j === i));
    const ind = artikler[i].dataset.ind;
    if (ind === current) return;
    current = ind;
    const sp = JSON.parse(chart.dataset.spec); sp.ind = ind;
    chart.dataset.spec = JSON.stringify(sp);
    chart.classList.add('bytter');
    setTimeout(() => { redraw(chart); chart.classList.remove('bytter'); }, 140);
  };

  // Et kapittel er aktivt når overskriften har passert lesestreken. På bred skjerm ligger streken
  // på 55 % av vinduet; på smal skjerm står kartet øverst, og streken legges i tekstfeltet under kartet.
  const lesestrek = () => {
    const H = window.innerHeight;
    if (window.innerWidth >= 860) return H * 0.55;
    const gb = Math.max(0, graf.getBoundingClientRect().bottom);
    return gb + (H - gb) * 0.4;
  };
  let venter = false;
  const sjekk = () => {
    venter = false;
    const linje = lesestrek();
    let i = 0;
    artikler.forEach((a, j) => { if (a.querySelector('.kicker').getBoundingClientRect().top <= linje) i = j; });
    bytt(i);
  };
  const påRull = () => { if (!venter) { venter = true; requestAnimationFrame(sjekk); } };
  window.addEventListener('scroll', påRull, { passive: true });
  window.addEventListener('resize', påRull, { passive: true });
  sjekk();
}

export function initScrolly() {
  const go = () => document.querySelectorAll('.nn-scrolly[data-scrolly]').forEach(build);
  if (document.readyState === 'complete') go();
  else document.addEventListener('DOMContentLoaded', go, { once: true });
}
