// NAV-statistikk på kommunesiden (fase 4 i analyse/PLAN-NAV.md).
// Dataene ligger i data/nav/<kommunenr>.json (fetch_nav.py) og hentes først når fanen Arbeid tegnes.
// All fortolkningstekst lages av regler fra tallene. Ingen tekst er skrevet for hånd per kommune.
import { placeholder } from '../charts/core.js';
import { tall, heltall, kortNavn } from './format.js';

const MND = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember'];
const cache = new Map();
const hent = nr => {
  if (!cache.has(nr)) cache.set(nr, fetch(`/data/nav/${encodeURIComponent(nr)}.json`).then(r => (r.ok ? r.json() : Promise.reject(new Error(r.status)))));
  return cache.get(nr);
};

const p1 = v => (v == null ? '–' : `${tall(v, 1)} %`);
const pp = v => `${tall(Math.abs(v), 1)} prosentpoeng`;
// «over», «under» eller «om lag som»: forskjeller under 0,2 prosentpoeng regnes som like
const ord = (a, b) => (Math.abs(a - b) < 0.2 ? 'om lag som' : a > b ? 'over' : 'under');

// År → verdi, bare der verdien kan vises (ikke skjult/brudd)
function kart(s, felt = 'pst', nokkel = 'aar') {
  const m = new Map();
  if (!s) return m;
  s[nokkel].forEach((a, i) => { if (s[felt][i] != null) m.set(a, s[felt][i]); });
  return m;
}
const harFlagg = (s, i, f) => (s.f[i] || []).includes(f);
const sisteHele = s => {
  for (let i = s.aar.length - 1; i >= 0; i--) if (s.n[i] === 12 && s.pst[i] != null) return i;
  return -1;
};
// Uføredatoer: desember = år, september = år + 0,75 (to siste år uten desembertall)
const uX = d => +d.slice(0, 4) + (d.slice(5) === '12' ? 0 : (+d.slice(5) - 1) / 12 - 0.25);
const uEtikett = d => `${MND[+d.slice(5) - 1]} ${d.slice(0, 4)}`;

function linjer(x, serier, opts = {}) {
  return placeholder('linjer', { x, serier, format: 'pst', brudd: true, hoyde: 260, ...opts }, 270);
}

function serieData(x, m) { return x.map(a => (m.has(a) ? m.get(a) : null)); }

function figur(tittel, undertekst, graf, kilde) {
  return `<div class="card nav-fig"><div class="ch"><h3 class="serif">${tittel}</h3></div>` +
    (undertekst ? `<p class="hint">${undertekst}</p>` : '') + graf +
    (kilde ? `<p class="nn-kilde">${kilde}</p>` : '') + '</div>';
}

function bygg(d, opt) {
  const navn = kortNavn(d.navn);
  const fy = d.ref.fylke, nn = d.ref.NN, la = d.ref.landet;
  const fyNavn = fy.navn;
  const K = { ledige: d.ledige, aap: d.aap, nedsatt: d.nedsatt };

  // ------------------------------------------------------------ nøkkeltall
  const iL = sisteHele(d.ledige), iA = sisteHele(d.aap), iN = sisteHele(d.nedsatt);
  const aL = d.ledige.aar[iL], aA = d.aap.aar[iA], aN = d.nedsatt.aar[iN];
  const fyL = kart(fy.ledige), fyA = kart(fy.aap), fyN = kart(fy.nedsatt), laL = kart(la.ledige);
  const u = d.ufore, iU = u.pst.length - 1;
  const fyU = kart(fy.ufore, 'pst', 'dato'), laU = kart(la.ufore, 'pst', 'dato');
  const pe = d.pensjon, iP = pe.pst.length - 1;
  const fyP = kart(fy.pensjon), laP = kart(la.pensjon);
  const kpi = (v, l, h, ned) => `<div class="k"><div class="v${ned ? ' down' : ''}">${v}</div><div class="l">${l}</div><div class="h">${h}</div></div>`;
  const kpis = '<div class="bf-kpis">' +
    kpi(iL >= 0 ? p1(d.ledige.pst[iL]) + (harFlagg(d.ledige, iL, 'anslatt') ? '†' : '') : 'skjult', `Helt ledige ${iL >= 0 ? aL : ''}`, `av arbeidsstyrken · ${fyNavn} ${p1(fyL.get(aL))} · landet ${p1(laL.get(aL))}`) +
    kpi(p1(d.aap.pst[iA]), `AAP ${aA}`, `av befolkningen 18–66 år · ${fyNavn} ${p1(fyA.get(aA))}`) +
    kpi(p1(d.nedsatt.pst[iN]), `Nedsatt arbeidsevne ${aN}`, `av befolkningen 18–66 år · ${fyNavn} ${p1(fyN.get(aN))}`) +
    kpi(p1(u.pst[iU]), `Uføretrygd, ${uEtikett(u.dato[iU])}`, `av befolkningen 18–67 år (NAV) · ${fyNavn} ${p1(fyU.get(u.dato[iU]))}`) +
    kpi(p1(pe.pst[iP]), `Minstepensjon ${pe.aar[iP]}`, `av alderspensjonistene · ${fyNavn} ${p1(fyP.get(pe.aar[iP]))} · landet ${p1(laP.get(pe.aar[iP]))}`) +
    '</div>';

  // ------------------------------------------------------------ tekst
  const s = [];
  const avsnitt = [];
  const nyttAvsnitt = () => { if (s.length) avsnitt.push(s.splice(0).join(' ')); };
  if (iL >= 0) {
    const vL = d.ledige.pst[iL];
    s.push(`I ${aL} var <b>${p1(vL)}</b> av arbeidsstyrken i ${navn} helt ledige, ${ord(vL, fyL.get(aL))} ${fyNavn} (${p1(fyL.get(aL))}) og ${ord(vL, laL.get(aL))} landet (${p1(laL.get(aL))}).`);
    let over = 0, n = 0;
    d.ledige.aar.forEach((a, i) => { const v = d.ledige.pst[i], f = fyL.get(a); if (v != null && f != null && d.ledige.n[i] === 12) { n++; if (v - f >= 0.2) over++; } });
    const fra = d.ledige.aar.find((a, i) => d.ledige.pst[i] != null);
    if (n >= 5) s.push(over === 0 ? `Ledigheten har ikke vært tydelig over fylkets i noen av de ${n} hele årene med tall siden ${fra}.`
      : `Ledigheten har vært tydelig over fylkets i ${over} av ${n} hele år med tall siden ${fra}.`);
    const mnd = (d.ledige.mnd[aL] || []).map(p => (p && typeof p[1] === 'number' ? p[1] : null));
    const maks = Math.max(...mnd.filter(v => v != null));
    const topp = mnd.map((v, i) => (v === maks ? MND[i] : null)).filter(Boolean);
    if (topp.length && topp.length <= 3) s.push(`Høyest var den i ${topp.join(' og ')} (${p1(maks)}).`);
  } else {
    s.push(`NAV har skjult ledighetstallene for ${navn} i de fleste månedene, fordi færre enn fire personer var helt ledige.`);
  }
  nyttAvsnitt();
  const vA = d.aap.pst[iA];
  const i16 = d.aap.aar.indexOf(2016);
  s.push(`Andelen med arbeidsavklaringspenger var <b>${p1(vA)}</b> i ${aA}, ${ord(vA, fyA.get(aA))} ${fyNavn} (${p1(fyA.get(aA))})` +
    (i16 >= 0 && d.aap.pst[i16] != null ? `, mot ${p1(d.aap.pst[i16])} i 2016.` : '.'));
  const vN = d.nedsatt.pst[iN], uten = d.nedsatt.uten_aap[aN];
  s.push(`Andelen med nedsatt arbeidsevne var <b>${p1(vN)}</b> i ${aN}, ${ord(vN, fyN.get(aN))} ${fyNavn} (${p1(fyN.get(aN))}).` +
    (uten != null ? ` Av dem hadde ${tall(uten, 0)} % ikke AAP.` : ''));
  nyttAvsnitt();
  const vU = u.pst[iU];
  s.push(`Ifølge NAV mottok <b>${p1(vU)}</b> uføretrygd i ${uEtikett(u.dato[iU])}, ${ord(vU, fyU.get(u.dato[iU]))} ${fyNavn} (${p1(fyU.get(u.dato[iU]))}) og ${ord(vU, laU.get(u.dato[iU]))} landet (${p1(laU.get(u.dato[iU]))}).` +
    (opt.ssbUfore != null ? ` Nøkkeltallet over (${p1(opt.ssbUfore)}) er fra SSB, som teller på et annet tidspunkt og med et annet befolkningsgrunnlag. Tallene er derfor ikke like.` : ''));
  nyttAvsnitt();
  const vP = pe.pst[iP], i20 = pe.aar.indexOf(2020);
  const lP = laP.get(pe.aar[iP]);
  s.push(`Blant alderspensjonistene hadde <b>${p1(vP)}</b> minstepensjon i ${pe.aar[iP]}, ${ord(vP, fyP.get(pe.aar[iP]))} ${fyNavn} (${p1(fyP.get(pe.aar[iP]))})` +
    (lP != null ? ` og ${ord(vP, lP)} landet (${p1(lP)})` : '') +
    (i20 >= 0 && pe.pst[i20] != null ? `, mot ${p1(pe.pst[i20])} i 2020.` : '.'));
  nyttAvsnitt();
  // forbehold
  const nevner = iL >= 0 && d.ledige.pst[iL] ? d.ledige.antall[iL] / d.ledige.pst[iL] * 100 : null;
  const forb = [];
  if (nevner != null && nevner < 1000) forb.push(`Arbeidsstyrken er om lag ${heltall(Math.round(nevner / 10) * 10)} personer, så noen få personer gir store utslag fra år til år.`);
  const ansl = d.ledige.aar.filter((a, i) => harFlagg(d.ledige, i, 'anslatt'));
  const skj = d.ledige.aar.filter((a, i) => harFlagg(d.ledige, i, 'skjult'));
  if (ansl.length) forb.push(`Årssnittet for ledighet er anslått i ${ansl.length === 1 ? ansl[0] : ansl.length + ' år'} (merket †), fordi NAV har skjult måneder med færre enn fire ledige; de er regnet som 1,5.`);
  if (skj.length) forb.push(`For ${skj.length === 1 ? skj[0] : skj.length + ' år'} vises ikke snitt, fordi mer enn halvparten av månedene er skjult.`);
  const brudd = d.ledige.aar.some((a, i) => harFlagg(d.ledige, i, 'brudd'));
  if (brudd) forb.push(d.meta.brudd);
  if (d.ledige.f.some(f => f.includes('beregnet')) || d.ufore.f.some(f => f.includes('beregnet'))) forb.push(`Tallene før 2020 er summert fra kommunene som ble slått sammen til ${navn}.`);

  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hva viser NAV-tallene?</h3><span class="tag">NAV · regelbasert tekst</span></div>' +
    avsnitt.map(a => `<p>${a}</p>`).join('') + (forb.length ? `<p class="hint" style="margin:8px 0 0">${forb.join(' ')}</p>` : '') + '</div>';

  // ------------------------------------------------------------ figurer
  const kom = { navn, kort: navn, farge: 'accent', uthev: true };
  const fyl = { navn: fyNavn, kort: fyNavn, farge: 'ink' };
  const nns = { navn: 'Nord-Norge', kort: 'Nord-Norge', farge: 'var(--ink-3)', stil: 'stiplet' };
  const lan = { navn: 'Landet', kort: 'Landet', farge: 'var(--ink-3)', stil: 'stiplet' };
  const delAar = (s2) => { const i = s2.aar.length - 1; return s2.n[i] && s2.n[i] < 12 ? `${s2.aar[i]} gjelder januar–${MND[s2.n[i] - 1]}.` : ''; };

  const xL = d.ledige.aar;
  const f1 = figur(`Helt ledige i ${navn}, ${fyNavn} og landet`, `Prosent av arbeidsstyrken, årssnitt av månedstall. ${delAar(d.ledige)}`,
    linjer(xL, [{ ...kom, data: serieData(xL, kart(d.ledige)) }, { ...fyl, data: serieData(xL, fyL) }, { ...lan, data: serieData(xL, laL) }]),
    'Kilde: NAV, HL060 Helt ledige. Fylke og kommune.');
  const xA = d.aap.aar;
  const f2 = figur(`Mottakere av arbeidsavklaringspenger (AAP)`, `Prosent av befolkningen 18–66 år. 2010–2015 er NAVs årsgjennomsnitt, fra 2016 snitt av månedstall. ${delAar(d.aap)}`,
    linjer(xA, [{ ...kom, data: serieData(xA, kart(d.aap)) }, { ...fyl, data: serieData(xA, fyA) }, { ...nns, data: serieData(xA, kart(nn.aap)) }], { markor: [{ x: 2015.5, tekst: 'Månedstall' }] }),
    'Kilde: NAV, AAP-mottakere per kommune 2010–2015 og AAP155. NAV har ikke landstall per kommunefil fra 2016.');
  const xN = d.nedsatt.aar;
  const f3 = figur(`Personer med nedsatt arbeidsevne`, `Prosent av befolkningen 18–66 år, snitt av månedstall. Omfatter både dem med AAP og dem som får annen oppfølging fra NAV. ${delAar(d.nedsatt)}`,
    linjer(xN, [{ ...kom, data: serieData(xN, kart(d.nedsatt)) }, { ...fyl, data: serieData(xN, fyN) }, { ...nns, data: serieData(xN, kart(nn.nedsatt)) }]),
    'Kilde: NAV, NED155 Personer med nedsatt arbeidsevne.');
  const xU = u.dato.map(uX);
  const ux = m => u.dato.map(dt => (m.has(dt) ? m.get(dt) : null));
  const f4 = figur(`Mottakere av uføretrygd`, `Prosent av befolkningen 18–67 år, desember hvert år${u.dato.some(dt => dt.endsWith('-09')) ? ' og september de siste årene' : ''}. Til og med 2012 gjelder tallene uførepensjon.`,
    linjer(xU, [{ ...kom, data: ux(kart(u, 'pst', 'dato')) }, { ...fyl, data: ux(fyU) }, { ...lan, data: ux(laU) }], { xEtikett: u.dato.map(uEtikett) }),
    'Kilde: NAV, uføretrygd per kommune (Tabell 20/PST220 og eldre kommunetabeller). Nyeste utgave per tellingsdato.');
  const iP20 = pe.aar.findIndex(a => a >= 2020);
  const xP = pe.aar.slice(iP20);
  const f5 = figur(`Alderspensjonister med minstepensjon`, 'Prosent av alderspensjonistene, september hvert år. Tallene før 2020 vises ikke, fordi NAV oppgir feil i dem.',
    linjer(xP, [{ ...kom, data: serieData(xP, kart(pe)) }, { ...fyl, data: serieData(xP, fyP) }, { ...lan, data: serieData(xP, laP) }]),
    'Kilde: NAV, PST011 og PST062 (dagens kommuneinndeling).');

  // ------------------------------------------------------------ tabell
  const aarene = [...new Set([...d.ledige.aar, ...d.aap.aar, ...d.nedsatt.aar, ...pe.aar, ...u.dato.map(dt => +dt.slice(0, 4))])].sort((a, b) => b - a);
  const celle = (sr, a) => {
    if (!sr) return '–';
    const i = sr.aar.indexOf(a);
    if (i < 0) return '–';
    if (harFlagg(sr, i, 'brudd')) return 'brudd';
    if (harFlagg(sr, i, 'skjult')) return 'skjult';
    return sr.pst[i] == null ? '–' : tall(sr.pst[i], 1) + (harFlagg(sr, i, 'anslatt') ? '†' : '');
  };
  const ufCelle = a => {
    const i = u.dato.indexOf(`${a}-12`), j = u.dato.indexOf(`${a}-09`);
    const k = i >= 0 ? i : j;
    if (k < 0) return '–';
    if (harFlagg(u, k, 'brudd')) return 'brudd';
    return u.pst[k] == null ? '–' : tall(u.pst[k], 1) + (i < 0 ? ' (sept.)' : '');
  };
  const rader = aarene.map(a => `<tr><td>${a}</td><td class="num">${celle(K.ledige, a)}</td><td class="num">${celle(K.aap, a)}</td><td class="num">${celle(K.nedsatt, a)}</td>` +
    `<td class="num">${d.nedsatt.uten_aap[a] != null ? tall(d.nedsatt.uten_aap[a], 0) : '–'}</td><td class="num">${ufCelle(a)}</td>` +
    `<td class="num">${a >= 2020 ? celle(pe, a) : '–'}</td></tr>`).join('');
  const tabell = `<div class="card nav-fig"><div class="ch"><h3 class="serif">NAV-tallene for ${navn} år for år</h3></div>` +
    `<p class="hint">Prosent. Helt ledige av arbeidsstyrken; AAP og nedsatt arbeidsevne av befolkningen 18–66 år; «uten AAP» er andelen av dem med nedsatt arbeidsevne; uføre av befolkningen 18–67 år (desember, ellers september); minstepensjon av alderspensjonistene. † = anslått. ${delAar(d.ledige)}</p>` +
    '<div class="nn-tabell-rull"><table class="nn-tabell"><thead><tr><th>År</th><th class="num">Helt ledige</th><th class="num">AAP</th><th class="num">Nedsatt arbeidsevne</th><th class="num">Uten AAP</th><th class="num">Uføre</th><th class="num">Minstepensjon</th></tr></thead>' +
    `<tbody>${rader}</tbody></table></div></div>`;

  const mer = '<details class="nn-mer"><summary>Hva tallene måler</summary>' +
    '<p><b>Helt ledige</b> er registrert hos NAV som arbeidssøkere uten arbeid, i prosent av arbeidsstyrken. <b>AAP</b> gis til personer som får behandling eller arbeidsrettede tiltak for å komme i arbeid. <b>Nedsatt arbeidsevne</b> omfatter alle NAV har vurdert til å ha behov for særlig tilpasset innsats, med eller uten AAP. <b>Uføretrygd</b> erstatter uførepensjon fra 2015; NAV har regnet om tallene for 2013–2014. <b>Minstepensjon</b> betyr at alderspensjonen er avkortet til garantinivået.</p>' +
    `<p>${d.meta.prikking} Fylkestallene er summen av kommunene. Mer på <a href="metode.html#nav">metodesiden</a>.</p></details>`;

  return '<div class="nav-blokk"><h3 class="nn-h3" style="margin:26px 0 4px">NAV-statistikk: ledighet, helse og trygd</h3>' +
    `<p class="hint" style="margin:0 0 10px">Tidsserier fra NAV for ${navn}, sammenlignet med ${fyNavn} og landet eller Nord-Norge.</p>` +
    kpis + tekst +
    // Diagrammene og årstabellen står i en utfoldbar boks, så fanen ikke blir for lang
    '<details class="nn-mer nav-detaljer"><summary>Vis fem diagrammer og tabell år for år</summary>' + f1 + f2 + f3 + f4 + f5 + tabell + '</details>' +
    mer + '</div>';
}

// Tegner NAV-blokken i host. opt: { ssbUfore, ferdig(host) }
export function navKort(nr, host, opt = {}) {
  if (!host || !(+nr > 0)) return;
  host.innerHTML = '<p class="hint">Henter NAV-statistikk …</p>';
  return hent(String(nr)).then(d => {
    host.innerHTML = bygg(d, opt);
    if (opt.ferdig) opt.ferdig(host);
  }).catch(() => { host.innerHTML = '<p class="hint">NAV-statistikken kunne ikke lastes.</p>'; });
}

// ---------------------------------------------------------------------------------------------
// Fylke og landsdel (fase 5): fylkets tall mot Nord-Norge og landet, eller landsdelen mot de tre
// fylkene og landet. Kart over kommunene med fire NAV-indikatorer.
const FYLKER = { 18: 'Nordland', 55: 'Troms', 56: 'Finnmark' };
const FYLKEFARGE = { 18: 'var(--nl)', 55: 'var(--tr)', 56: 'var(--fi)' };
const KARTIND = [['navLedige', 'Helt ledige'], ['navAap', 'AAP'], ['navNedsatt', 'Nedsatt arbeidsevne'], ['navUfore', 'Uføretrygd'], ['navMinstepensjon', 'Minstepensjon']];

function byggNivaa(kode, d, andre) {
  const erNN = kode === 'NN';
  const navn = d.navn, la = d.landet;
  const iL = sisteHele(d.ledige), iA = sisteHele(d.aap), iN = sisteHele(d.nedsatt);
  const aL = d.ledige.aar[iL], aA = d.aap.aar[iA], aN = d.nedsatt.aar[iN];
  const u = d.ufore, iU = u.pst.length - 1, du = u.dato[iU];
  const pe = d.pensjon, iP = pe.pst.length - 1, aP = pe.aar[iP];
  const laL = kart(la.ledige), laU = kart(la.ufore, 'pst', 'dato'), laP = kart(la.pensjon);
  const nn = andre.NN;
  const kpi = (v, l, h) => `<div class="k"><div class="v">${v}</div><div class="l">${l}</div><div class="h">${h}</div></div>`;
  const ref = (s, a, nokkel = 'aar') => (s ? p1(kart(s, 'pst', nokkel).get(a)) : '–');
  const kpis = '<div class="bf-kpis">' +
    kpi(p1(d.ledige.pst[iL]), `Helt ledige ${aL}`, `av arbeidsstyrken · landet ${p1(laL.get(aL))}`) +
    kpi(p1(d.aap.pst[iA]), `AAP ${aA}`, `av befolkningen 18–66 år${erNN ? '' : ` · Nord-Norge ${ref(nn.aap, aA)}`}`) +
    kpi(p1(d.nedsatt.pst[iN]), `Nedsatt arbeidsevne ${aN}`, `av befolkningen 18–66 år${erNN ? '' : ` · Nord-Norge ${ref(nn.nedsatt, aN)}`}`) +
    kpi(p1(u.pst[iU]), `Uføretrygd, ${uEtikett(du)}`, `av befolkningen 18–67 år · landet ${p1(laU.get(du))}`) +
    kpi(p1(pe.pst[iP]), `Minstepensjon ${aP}`, `av alderspensjonistene · landet ${p1(laP.get(aP))}`) + '</div>';

  // tekst: nivå mot landet, og for landsdelen spennet mellom fylkene
  const avs = [];
  const vL = d.ledige.pst[iL];
  const spenn = (felt, a, nokkel = 'aar') => {
    const v = Object.entries(FYLKER).map(([k, n]) => [n, kart(andre[k][felt], 'pst', nokkel).get(a)]).filter(x => x[1] != null).sort((x, y) => y[1] - x[1]);
    return v.length === 3 ? `høyest i ${v[0][0]} (${p1(v[0][1])}) og lavest i ${v[2][0]} (${p1(v[2][1])})` : '';
  };
  avs.push(`I ${aL} var <b>${p1(vL)}</b> av arbeidsstyrken i ${navn} helt ledige, ${ord(vL, laL.get(aL))} landet (${p1(laL.get(aL))})` +
    (erNN ? `, ${spenn('ledige', aL)}.` : '.'));
  const sm = (felt, v, a) => (erNN ? `, ${spenn(felt, a)}` : `, ${ord(v, kart(nn[felt]).get(a))} Nord-Norge samlet (${ref(nn[felt], a)})`);
  avs.push(`Andelen med arbeidsavklaringspenger var <b>${p1(d.aap.pst[iA])}</b> i ${aA}${sm('aap', d.aap.pst[iA], aA)}. ` +
    `Andelen med nedsatt arbeidsevne var <b>${p1(d.nedsatt.pst[iN])}</b> i ${aN}${sm('nedsatt', d.nedsatt.pst[iN], aN)}.`);
  avs.push(`Ifølge NAV mottok <b>${p1(u.pst[iU])}</b> uføretrygd i ${uEtikett(du)}, ${ord(u.pst[iU], laU.get(du))} landet (${p1(laU.get(du))})` +
    (erNN ? `, ${spenn('ufore', du, 'dato')}.` : '.') +
    ` Blant alderspensjonistene hadde <b>${p1(pe.pst[iP])}</b> minstepensjon i ${aP}, ${ord(pe.pst[iP], laP.get(aP))} landet (${p1(laP.get(aP))}).`);
  const tekst = '<div class="bf-diagnose nav-tekst"><div class="h-row"><h3>Hva viser NAV-tallene?</h3><span class="tag">NAV · regelbasert tekst</span></div>' +
    avs.map(a => `<p>${a}</p>`).join('') +
    `<p class="hint" style="margin:8px 0 0">${erNN ? 'Landsdelens' : 'Fylkets'} tall er summen av kommunene. Måneder NAV har skjult i små kommuner er regnet som 1,5 i summen. NAV har ikke landstall for AAP og nedsatt arbeidsevne i kommunefilene fra 2016.</p></div>`;

  // figurer
  const hoved = { navn, kort: navn, farge: 'accent', uthev: true };
  const lan = { navn: 'Landet', kort: 'Landet', farge: 'var(--ink-3)', stil: 'stiplet' };
  const linjeserier = (felt, x, nokkel = 'aar', medLand = true) => {
    const se = [{ ...hoved, data: x.map(a => kart(d[felt], 'pst', nokkel).get(a) ?? null) }];
    if (erNN) Object.entries(FYLKER).forEach(([k, n]) => se.push({ navn: n, kort: n, farge: FYLKEFARGE[k], data: x.map(a => kart(andre[k][felt], 'pst', nokkel).get(a) ?? null) }));
    else se.push({ navn: 'Nord-Norge', kort: 'Nord-Norge', farge: 'ink', data: x.map(a => kart(nn[felt], 'pst', nokkel).get(a) ?? null) });
    if (medLand && la[felt]) se.push({ ...lan, data: x.map(a => kart(la[felt], 'pst', nokkel).get(a) ?? null) });
    return se;
  };
  const delAar = s2 => { const i = s2.aar.length - 1; return s2.n[i] && s2.n[i] < 12 ? `${s2.aar[i]} gjelder januar–${MND[s2.n[i] - 1]}.` : ''; };
  const sml = erNN ? 'fylkene og landet' : 'Nord-Norge og landet';
  const f1 = figur(`Helt ledige i ${navn}, ${sml}`, `Prosent av arbeidsstyrken, årssnitt av månedstall. ${delAar(d.ledige)}`, linjer(d.ledige.aar, linjeserier('ledige', d.ledige.aar)), 'Kilde: NAV, HL060.');
  const f2 = figur('Mottakere av arbeidsavklaringspenger (AAP)', `Prosent av befolkningen 18–66 år. 2010–2015 er NAVs årsgjennomsnitt, fra 2016 snitt av månedstall. ${delAar(d.aap)}`, linjer(d.aap.aar, linjeserier('aap', d.aap.aar, 'aar', false), { markor: [{ x: 2015.5, tekst: 'Månedstall' }] }), 'Kilde: NAV, AAP-mottakere per kommune 2010–2015 og AAP155.');
  const f3 = figur('Personer med nedsatt arbeidsevne', `Prosent av befolkningen 18–66 år, snitt av månedstall. ${delAar(d.nedsatt)}`, linjer(d.nedsatt.aar, linjeserier('nedsatt', d.nedsatt.aar, 'aar', false)), 'Kilde: NAV, NED155.');
  const f4 = figur('Mottakere av uføretrygd', 'Prosent av befolkningen 18–67 år, desember hvert år og september de siste årene. Til og med 2012 gjelder tallene uførepensjon.',
    linjer(u.dato.map(uX), linjeserier('ufore', u.dato, 'dato'), { xEtikett: u.dato.map(uEtikett) }), 'Kilde: NAV, uføretrygd per kommune (Tabell 20/PST220 og eldre kommunetabeller).');
  const xP = pe.aar.filter(a => a >= 2020);
  const f5 = figur('Alderspensjonister med minstepensjon', 'Prosent av alderspensjonistene, september hvert år. Tallene før 2020 vises ikke, fordi NAV oppgir feil i dem.', linjer(xP, linjeserier('pensjon', xP)), 'Kilde: NAV, PST011 og PST062.');

  const kartDel = `<div class="card nav-fig"><div class="ch"><h3 class="serif">Kommunene i ${navn}</h3>` +
    `<div class="minseg nav-kartvalg">${KARTIND.map(([k, n], i) => `<button type="button" data-navind="${k}" aria-selected="${i === 0}">${n}</button>`).join('')}</div></div>` +
    '<p class="hint">Siste hele år for ledighet, AAP og nedsatt arbeidsevne; siste tellingsdato for uføretrygd og minstepensjon. Pek for tall, klikk for kommunesiden.</p><div class="nav-kart"></div></div>';

  return '<div class="nav-blokk">' +
    '<div class="ch" style="margin-top:32px;padding-top:18px;border-top:1px solid var(--line2)"><h3 class="serif" style="font-size:18px">NAV-statistikk: ledighet, helse og trygd</h3></div>' +
    `<p class="sub">Tidsserier fra NAV for ${navn}, sammenlignet med ${sml}. Kommunetallene finnes på hver kommuneside under «Arbeid og næring».</p>` +
    kpis + tekst + kartDel + f1 + f2 + f3 + f4 + f5 + '</div>';
}

// kode: '18', '55', '56' eller 'NN'. opt: { ferdig(host) }
export function navNivaa(kode, host, opt = {}) {
  if (!host) return null;
  host.innerHTML = '<p class="hint">Henter NAV-statistikk …</p>';
  const koder = ['NN', '18', '55', '56'];
  return Promise.all(koder.map(k => hent(`fylke-${k}`))).then(alle => {
    const andre = Object.fromEntries(koder.map((k, i) => [k, alle[i]]));
    host.innerHTML = byggNivaa(kode, andre[kode], andre);
    const kartHost = host.querySelector('.nav-kart');
    const fylke = FYLKER[kode];
    const tegn = ind => { kartHost.innerHTML = placeholder('kart', fylke ? { ind, fylke, height: 520 } : { ind, height: 520 }, 520); };
    tegn(KARTIND[0][0]);
    host.querySelectorAll('[data-navind]').forEach(b => b.addEventListener('click', () => {
      host.querySelectorAll('[data-navind]').forEach(x => x.setAttribute('aria-selected', String(x === b)));
      tegn(b.dataset.navind);
    }));
    if (opt.ferdig) opt.ferdig(host);
  }).catch(() => { host.innerHTML = '<p class="hint">NAV-statistikken kunne ikke lastes.</p>'; });
}
