// Seks kart på forsiden: faner bytter indikator og forklarende tekst side om side med kartet.
// Fane 06 (NAV) har egne valg (s.valg) som bytter kartlag og tekst innenfor fanen.
// <section class="nn-scrolly" data-scrolly="fire-kart"></section>
import { L } from './legacy.js';
import { tall, prosent, endringPst, kortNavn } from './format.js';
import { redraw } from '../charts/core.js';

const median = a => { const b = [...a].sort((x, y) => x - y); const m = b.length / 2; return b.length % 2 ? b[Math.floor(m)] : (b[m - 1] + b[m]) / 2; };

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

// Fane 06: NAV-statistikk. Hvert valg har eget kartlag og egen tekst, regnet fra NAV_KART.
function navSteg() {
  const N = L.NAVK;
  if (!N) return null;
  const M = N.meta, ref = N.ref, nn = ref.NN, la = ref.landet;
  const ks = L.K.map(k => ({ k, navn: kortNavn(k.navn), v: N.kommuner[String(k.nr)] || {} }));
  const p1 = v => prosent(v, 1);
  const rang = f => ks.filter(x => x.v[f] != null).sort((a, b) => b.v[f] - a.v[f]);
  const smaa = xs => (xs.every(x => x.k.pop < 1500) ? ' Begge er små kommuner, der noen få personer gir store utslag.' : '');
  const md = f => p1(median(ks.filter(x => x.v[f] != null).map(x => x.v[f])));
  const uMnd = M.ufore.slice(5) === '09' ? 'september' : 'desember';
  const lag = [];
  {
    const r = rang('ledige'), over = r.filter(x => x.v.ledige > la.ledige).length;
    lag.push({ ind: 'navLedige', knapp: 'Helt ledige',
      h: `${over} av ${r.length} kommuner${r.length < 80 ? " med tall" : ""} har høyere ledighet enn landet`,
      p: `I ${M.ledige} var ${p1(nn.ledige)} av arbeidsstyrken i Nord-Norge helt ledige, mot ${p1(la.ledige)} i landet. Høyest var ledigheten i ${r[0].navn} (${p1(r[0].v.ledige)}) og ${r[1].navn} (${p1(r[1].v.ledige)}).${smaa(r.slice(0, 2))} NAV skjuler tall under fire personer; der er måneden regnet som 1,5.` });
  }
  {
    const r = rang('aap');
    lag.push({ ind: 'navAap', knapp: 'AAP',
      h: `${p1(nn.aap)} av befolkningen 18–66 år mottok arbeidsavklaringspenger`,
      p: `Årssnittet for Nord-Norge i ${M.aap}. Medianen blant kommunene er ${md('aap')}; høyest er ${r[0].navn} (${p1(r[0].v.aap)}) og ${r[1].navn} (${p1(r[1].v.aap)}), lavest ${r[r.length - 1].navn} (${p1(r[r.length - 1].v.aap)}).${smaa(r.slice(0, 2))}` });
  }
  {
    const r = rang('nedsatt');
    lag.push({ ind: 'navNedsatt', knapp: 'Nedsatt arbeidsevne',
      h: `${p1(nn.nedsatt)} har nedsatt arbeidsevne etter NAVs vurdering`,
      p: `Årssnittet for Nord-Norge i ${M.nedsatt}, med eller uten arbeidsavklaringspenger. Medianen blant kommunene er ${md('nedsatt')}; høyest er ${r[0].navn} (${p1(r[0].v.nedsatt)}) og ${r[1].navn} (${p1(r[1].v.nedsatt)}).${smaa(r.slice(0, 2))}` });
  }
  {
    const r = rang('ufore'), over = r.filter(x => x.v.ufore > la.ufore).length;
    lag.push({ ind: 'navUfore', knapp: 'Uføretrygd',
      h: `${over} av ${r.length} kommuner har flere uføretrygdede enn landet`,
      p: `I ${uMnd} ${M.ufore.slice(0, 4)} mottok ${p1(nn.ufore)} av befolkningen 18–67 år i Nord-Norge uføretrygd, mot ${p1(la.ufore)} i landet. Høyest er ${r[0].navn} (${p1(r[0].v.ufore)}) og ${r[1].navn} (${p1(r[1].v.ufore)}).${smaa(r.slice(0, 2))} NAVs tall avviker noe fra SSBs, som telles på et annet tidspunkt.` });
  }
  {
    const r = rang('minstepensjon'), over = r.filter(x => x.v.minstepensjon > la.minstepensjon).length;
    lag.push({ ind: 'navMinstepensjon', knapp: 'Minstepensjon',
      h: `${p1(nn.minstepensjon)} av alderspensjonistene har minstepensjon`,
      p: `Andelen i Nord-Norge i september ${M.minstepensjon}, mot ${p1(la.minstepensjon)} i landet. ${over} av ${r.length} kommuner ligger over landet; høyest er ${r[0].navn} (${p1(r[0].v.minstepensjon)}) og ${r[1].navn} (${p1(r[1].v.minstepensjon)}).${smaa(r.slice(0, 2))}` });
  }
  return { ind: lag[3].ind, kicker: '06 · NAV', valg: lag, start: 3 };
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
      p: `SSBs hovedalternativ gir landsdelen nesten uendret folketall samlet, men fordelingen er skjev. Størst nedgang ventes i ${n1.navn} (${endringPst(n1.endr, 0)}) og ${n2.navn} (${endringPst(n2.endr, 0)}). De høyeste vekstratene ventes i ${v1.navn} og ${v2.navn}${v1.k.pop < 5000 && v2.k.pop < 5000 ? ', der små tall gir store prosentutslag' : ''}.` },
    { ind: 'eldre', kicker: '02 · Aldring i dag',
      h: `I den typiske kommunen er hver fjerde innbygger 65 år eller eldre`,
      p: `Medianen er ${prosent(median(f.ks.map(x => x.a65)), 1)}. Høyest er ${e1.navn} med ${prosent(e1.a65, 1)}; lavest er ${u1.navn} og ${u2.navn}, ${prosent(u1.a65, 1) === prosent(u2.a65, 1) ? `begge med ${prosent(u1.a65, 1)}` : `med ${prosent(u1.a65, 1)} og ${prosent(u2.a65, 1)}`}. Byene trekker til seg de unge — distriktene eldes først.` },
    { ind: 'forsorg', kicker: '03 · Forsørgerbrøk 2050',
      h: `Fra ${tall(median(f.ks.map(x => x.fb0)), 0)} til ${tall(median(f.ks.map(x => x.fb)), 0)} eldre per 100 i alderen 20–64`,
      p: `Slik endres medianen fra 2026 til 2050 i SSBs hovedalternativ. I ${over70} kommuner passerer forholdet 70 eldre per 100 i alderen 20–64; høyest i ${b1.navn} med ${tall(b1.fb, 0)}. Det er her det blir vanskeligst å skaffe nok ansatte i pleie og omsorg.` },
    { ind: 'innv', kicker: '04 · Innvandring',
      h: `Innvandring holder folketallet oppe i mange småsamfunn`,
      p: `Medianandelen med innvandrerbakgrunn er ${prosent(median(f.ks.map(x => x.innv)), 1)}. Høyest er ${i1.navn} (${prosent(i1.innv, 1)}), ${i2.navn} og ${i3.navn}. Uten innvandringen siden 2002 ville nedgangen vært langt større — se temasiden «Hvem blir værende?».` },
    { ind: 'robek', kicker: '05 · Kommuneøkonomi',
      h: `${f.robekNavn.length} kommuner står under statlig økonomisk kontroll`,
      p: `Per ${dato} er ${f.robekNavn.length} av de 80 kommunene registrert i ROBEK: ${f.robekNavn.join(', ')}. Når folketallet går ned og omsorgsbehovet øker, blir handlingsrommet trangere.` },
  ].concat(navSteg() || []);
}

// Kartet og teksten står side om side (under hverandre på mobil). Fanene 01–05 bytter indikator og tekst
// samtidig, så leseren aldri må rulle for å se hva kartet viser. Piltastene flytter mellom fanene.
function build(sec) {
  // Ingressen ligger i HTML-en som .nn-sk-oversikt og blir første fane («Oversikt»). Selve noden flyttes
  // inn i tekstfeltet, slik at tallene som siden fyller inn (#ingress80, #ingress2064), følger med.
  const ov = sec.querySelector('.nn-sk-oversikt');
  if (ov) ov.remove();
  const steps = (ov ? [{ ind: ov.dataset.ind || 'endring', kicker: 'Oversikt', node: ov }] : []).concat(steg());
  const smal = window.innerWidth < 860;
  const h = smal ? Math.round(Math.min(380, window.innerWidth * 1.05)) : Math.round(Math.min(540, Math.max(440, window.innerHeight - 220)));
  const kort = s => s.kicker.replace(/^\d+\s*·\s*/, '');
  const nr = s => (s.kicker.match(/^(\d+)/) || [])[1];
  sec.innerHTML = `
    <div class="nn-sk-faner" role="tablist" aria-label="Velg kart">${steps.map((s, i) => `
      <button type="button" role="tab" id="skFane${i}" aria-controls="skTekst" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}">${nr(s) ? `<span class="nr">${nr(s)}</span> ` : ''}${kort(s)}</button>`).join('')}
    </div>
    <div class="nn-sk-grid">
      <div class="nn-sk-kart"><div data-nnchart="kart" data-spec='${JSON.stringify({ ind: steps[0].ind, side: false, height: h })}' style="min-height:${h + 40}px"></div></div>
      <div class="nn-sk-tekst" id="skTekst" role="tabpanel" aria-live="polite"></div>
    </div>`;
  const chart = sec.querySelector('[data-nnchart]');
  const faner = [...sec.querySelectorAll('[role=tab]')];
  const tekst = sec.querySelector('.nn-sk-tekst');
  let aktiv = -1;
  const vis = (i, fokus) => {
    if (i === aktiv) return;
    aktiv = i;
    const s = steps[i], neste = steps[i + 1], forrige = steps[i - 1];
    faner.forEach((f, j) => { f.setAttribute('aria-selected', String(j === i)); f.tabIndex = j === i ? 0 : -1; });
    if (fokus) faner[i].focus();
    tekst.setAttribute('aria-labelledby', faner[i].id);
    const nav = `<div class="nn-sk-nav">
        ${forrige ? `<button type="button" data-gaa="${i - 1}">← ${kort(forrige)}</button>` : '<span></span>'}
        ${neste ? `<button type="button" class="neste" data-gaa="${i + 1}">${s.node ? 'Start' : 'Neste'}: ${nr(neste) ? nr(neste) + ' ' : ''}${kort(neste)} →</button>` : `<a class="neste" href="nord-norge.html">Hele landsdelen →</a>`}
      </div>`;
    if (s.node) { tekst.replaceChildren(s.node); s.node.insertAdjacentHTML('beforeend', nav); s.node.querySelectorAll('.nn-sk-nav').forEach((n, j, a) => { if (j < a.length - 1) n.remove(); }); }
    else if (s.valg) visValg(s, s.valgt ?? s.start ?? 0, nav);
    else tekst.innerHTML = `
      <div class="kicker">${s.kicker}</div>
      <h3>${s.h}</h3>
      <p>${s.p}</p>${nav}`;
    if (!s.valg) settInd(s.ind);
  };
  const settInd = ind => {
    const sp = JSON.parse(chart.dataset.spec);
    if (sp.ind !== ind) {
      sp.ind = ind; chart.dataset.spec = JSON.stringify(sp);
      chart.classList.add('bytter');
      setTimeout(() => { redraw(chart); chart.classList.remove('bytter'); }, 120);
    }
  };
  const visValg = (s, j, nav) => {
    s.valgt = j;
    const v = s.valg[j];
    tekst.innerHTML = `
      <div class="kicker">${s.kicker}</div>
      <div class="minseg nn-sk-valg" role="group" aria-label="Velg kartlag">${s.valg.map((x, i) => `<button type="button" data-skvalg="${i}" aria-pressed="${i === j}" aria-selected="${i === j}">${x.knapp}</button>`).join('')}</div>
      <h3>${v.h}</h3>
      <p>${v.p}</p>${nav ?? s.nav ?? ''}`;
    if (nav) s.nav = nav;
    settInd(v.ind);
  };
  sec.addEventListener('click', e => {
    const sv = e.target.closest('[data-skvalg]'); if (sv) return visValg(steps[aktiv], +sv.dataset.skvalg);
    const f = e.target.closest('[role=tab]'); if (f) return vis(faner.indexOf(f));
    const g = e.target.closest('[data-gaa]'); if (g) vis(+g.dataset.gaa);
  });
  sec.querySelector('.nn-sk-faner').addEventListener('keydown', e => {
    const d = { ArrowRight: 1, ArrowLeft: -1, Home: -99, End: 99 }[e.key];
    if (d == null) return;
    e.preventDefault();
    vis(Math.max(0, Math.min(steps.length - 1, d === -99 ? 0 : d === 99 ? steps.length - 1 : aktiv + d)), true);
  });
  vis(0);
}

export function initScrolly() {
  const go = () => document.querySelectorAll('.nn-scrolly[data-scrolly]').forEach(build);
  if (document.readyState === 'complete') go();
  else document.addEventListener('DOMContentLoaded', go, { once: true });
}
