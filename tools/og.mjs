// Delekort (Open Graph) for Facebook, Messenger og andre: lager og/<side>.png (1200 × 630) og skriver
// merkene inn i <head> på hver side mellom <!-- OG BEGIN --> og <!-- OG END -->. Kjør: node tools/og.mjs
// Teksten står til venstre og kartet til høyre; adressen vises ikke i bildet (den ligger i og:url).
// Kortene er bevisst beskrivende, uten tekniske mål: de skal fortelle hva leseren finner.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { createHash } from 'node:crypto';
import { geoTransverseMercator, geoPath } from 'd3-geo';
import { feature } from 'topojson-client';

const require = createRequire(import.meta.url);
const ROT = resolve(import.meta.dirname, '..');
const F = require('./fasit.cjs');
const URL = 'https://nord-norge.vercel.app';
const SITE = 'Nord-Norge mot 2050';

// ── Sidene ──
const S = [
  { fil: 'index.html', bilde: 'forside', farget: true,
    tittel: 'Hva skjer i Nord-Norge? Flere eldre, færre hender',
    tekst: 'Nord-Norge blir eldre, og det blir færre til å bære velferden. Se hva det betyr for landsdelen, fylkene og din kommune fram mot 2050.',
    kicker: SITE, h: 'Flere eldre,<br>færre hender', sub: 'Hva aldringen betyr for de 80 kommunene i Nordland, Troms og Finnmark' },
  { fil: 'nord-norge.html', bilde: 'landsdelen',
    tittel: 'Nord-Norge mot 2050: hele landsdelen',
    tekst: 'Hvordan befolkningen, arbeidskraften og kommuneøkonomien i Nordland, Troms og Finnmark utvikler seg fram mot 2050.',
    kicker: SITE, h: 'Hele landsdelen', sub: 'Befolkning, arbeid og økonomi samlet for Nord-Norge' },
  { fil: 'fylke.html', bilde: 'fylkene',
    tittel: 'Nordland, Troms og Finnmark mot 2050',
    tekst: 'Hvert fylke for seg: hvem som bor der, hvem som jobber, og hvordan kommunene står seg fram mot 2050.',
    kicker: SITE, h: 'Tre fylker,<br>80 kommuner', sub: 'Nordland, Troms og Finnmark, hvert for seg' },
  { fil: 'kommune.html', bilde: 'kommune',
    tittel: 'Hvordan går det med din kommune mot 2050?',
    tekst: 'Slik ser framtiden ut for kommunen din: hvem som bor der, hvem som jobber, og hvor presset økonomien blir fram mot 2050.',
    kicker: SITE, h: 'Din kommune<br>mot 2050', sub: 'Alle 80 kommuner i Nord-Norge, én for én' },
  { fil: 'sammenlign.html', bilde: 'sammenlign',
    tittel: 'Sammenlign kommunene i Nord-Norge',
    tekst: 'Still kommuner opp mot hverandre og se hvordan de utvikler seg fram mot 2050.',
    kicker: SITE, h: 'Sammenlign<br>kommunene', sub: 'Still kommunene opp mot hverandre' },
  { fil: 'metode.html', bilde: 'metode',
    tittel: 'Metode og kilder · Nord-Norge mot 2050',
    tekst: 'Hvor tallene kommer fra — SSB, NAV, KOSTRA og andre åpne kilder — og forbeholdene som gjelder.',
    kicker: SITE, h: 'Metode og kilder', sub: 'Åpne kilder og tall som kan etterprøves' },
  { fil: 'tema-flyktning.html', bilde: 'tema-01', tittel: 'Hvem blir værende? Flyttestrømmene i Nord-Norge',
    tekst: 'Mange flytter til Nord-Norge, men mange flytter også videre. Hvem blir værende, og hvor lenge?',
    kicker: 'Tema 01 · Flyttestrømmer', h: 'Hvem blir<br>værende?', sub: 'Flyktninger, innvandrere og de som flytter sørover' },
  { fil: 'tema-o6.html', bilde: 'tema-02', tittel: '6 store mot 74 små kommuner i Nord-Norge',
    tekst: 'Noen få byer vokser, mens de fleste kommunene får færre innbyggere. Hva skjer når de små telles like mye som de store?',
    kicker: 'Tema 02 · Senter mot periferi', h: '6 store mot<br>74 små', sub: 'Byene vokser, distriktene får færre innbyggere' },
  { fil: 'tema-kvinneflukt.html', bilde: 'tema-03', tittel: 'Kvinneflukten: de flytter i ung alder',
    tekst: 'Unge kvinner flytter ut tidligere enn menn. Det gir skjeve kjønnsforhold og færre barn i mange kommuner.',
    kicker: 'Tema 03 · Kjønnsmønsteret', h: 'Kvinneflukten', sub: 'Unge kvinner flytter først' },
  { fil: 'tema-arbeidskraft.html', bilde: 'tema-04', tittel: 'Hvem skal bære? Arbeidskraften i Nord-Norge mot 2050',
    tekst: 'Det mangler allerede folk i nord, og gruppen i arbeidsfør alder blir mindre. Hvem skal ta jobbene i helse, skole og næringsliv?',
    kicker: 'Tema 04 · Arbeidskraft og aldring', h: 'Hvem skal<br>bære?', sub: 'Færre i arbeid, flere som trenger hjelp' },
  { fil: 'tema-aldring.html', bilde: 'tema-05', tittel: 'Hvor står Nord-Norge globalt? Aldringen mot 2050',
    tekst: 'Hele den vestlige verden eldes. Slik ligger Nord-Norge an mot resten av Norge og andre land, og hva det betyr for eldreomsorgen.',
    kicker: 'Tema 05 · Aldring', h: 'Hvor står vi<br>globalt?', sub: 'Nord-Norge mot Norge og verden' },
  { fil: 'tema-scenarier.html', bilde: 'tema-06', tittel: 'Fire fremtider for Nord-Norge mot 2040',
    tekst: 'Tre veivalg og fire scenarier for næringslivet i nord, fra Business Index North 2023.',
    kicker: 'Tema 06 · Scenarier', h: 'Fire fremtider<br>mot 2040', sub: 'Tre veivalg, fire mulige framtider' },
  { fil: 'tema-bolig.html', bilde: 'tema-07', tittel: 'Bygges det nok der folk skal bo?',
    tekst: 'Det bygges færre boliger i nord enn på mange år. Bygges det nok der folk faktisk skal bo?',
    kicker: 'Tema 07 · Boligmarkedet', h: 'Bygges<br>det nok?', sub: 'Den laveste byggetakten siden 2000' },
  { fil: 'tema-naering.html', bilde: 'tema-08', tittel: 'Hva skal Nord-Norge leve av?',
    tekst: 'Sjømat, reiseliv, kraftforedlende industri, energi og forsvar: landsdelen har flere muligheter enn folk til å ta dem.',
    kicker: 'Tema 08 · Næringslivet mot 2040', h: 'Hva skal vi<br>leve av?', sub: 'Flere muligheter enn folk' },
  { fil: 'tema-pensjon.html', bilde: 'tema-09', tittel: 'Pensjonsetterslepet i nordnorske kommuner',
    tekst: 'Kommunene har betalt mer i pensjon enn regnskapet viser. Hva betyr det for handlingsrommet i årene som kommer?',
    kicker: 'Tema 09 · Kommunale pensjoner', h: 'Pensjons-<br>etterslepet', sub: 'Penger som er betalt, men ikke ført som kostnad' },
  { fil: 'tema-ung.html', bilde: 'tema-10', tittel: 'Sju av ti unge regner med å bli. Likevel blir de stadig færre.',
    tekst: 'De fleste unge i Nord-Norge vil bli boende, men det blir stadig færre av dem. Hva sier de unge selv om bolig, jobb og framtid?',
    kicker: 'Tema 10 · Ung i nord', h: 'Sju av ti unge<br>regner med å bli', sub: 'Det de unge sier, og det tallene viser' },
  { fil: 'tema-nordomrade.html', bilde: 'tema-11', tittel: '20 år med nordområdepolitikk — hva som ble sagt, og hva som skjedde',
    tekst: 'Regjeringene har kalt nordområdene sitt viktigste satsingsområde i 20 år. Hva ble lovet, og hva skjedde med folketallet i nord?',
    kicker: 'Tema 11 · Nordområdepolitikken', h: '20 år med<br>nordområdepolitikk', sub: 'Hva som ble sagt, og hva som skjedde' },
];

// ── Kartet (samme projeksjon som i src/charts/map.js), fargelagt med forsørgerbrøken 2050 på forsidekortet ──
const P = F.DATA.proj;
const topo = JSON.parse(readFileSync(join(ROT, 'geo/nn-kommuner.json'), 'utf8'));
const geo = feature(topo, topo.objects.nn);
const proj = geoTransverseMercator().rotate([-17, -66]).fitSize([500, 540], geo);
const sti = geoPath(proj);
const fbK = {};
F.K.forEach(k => { const o = P.kommuner[k.nr]; if (o) fbK[k.nr] = o.a65[o.a65.length - 1] / o.a2064[o.a2064.length - 1] * 100; });
const verdier = Object.values(fbK).sort((a, b) => a - b), lo = verdier[2], hi = verdier[verdier.length - 3];
const blandet = t => { const a = [0x1D, 0x3D, 0x55], b = [0x5C, 0x82, 0xFF]; return `rgb(${a.map((x, i) => Math.round(x + (b[i] - x) * t)).join(',')})`; };
const kart = farget => `<svg width="500" height="540" viewBox="0 0 500 540">${geo.features.map(f => {
  const v = fbK[+f.properties.nr];
  const fyll = farget && v != null ? blandet(Math.max(0, Math.min(1, (v - lo) / (hi - lo)))) : '#16405F';
  return `<path d="${sti(f)}" fill="${fyll}" stroke="#051C2C" stroke-width="0.7"/>`;
}).join('')}</svg>`;

const html = s => `<!doctype html><html lang="no"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,600&display=block" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#051C2C;color:#EEF3F8;font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden}
.kart{position:absolute;right:40px;top:45px;opacity:${s.farget ? 1 : .85}}
.tekst{position:absolute;left:84px;top:0;bottom:0;width:640px;display:flex;flex-direction:column;justify-content:center;gap:30px}
.kicker{font:500 21px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#8AA6FF}
h1{font:600 ${s.h.replace(/<br>/g, '').length > 24 ? 68 : 82}px/1.04 'Source Serif 4',serif;letter-spacing:-.01em}
.sub{font:400 30px/1.35 'IBM Plex Sans',sans-serif;color:#B5C3D2;max-width:600px}
.strek{position:absolute;left:84px;top:0;width:120px;height:8px;background:#5C82FF}
</style></head><body>
<div class="kart">${kart(!!s.farget)}</div>
<div class="strek"></div>
<div class="tekst"><div class="kicker">${s.kicker}</div><h1>${s.h}</h1>
${s.sub ? `<div class="sub">${s.sub}</div>` : ''}</div>
</body></html>`;

// ── Bilder ──
const chrome = join(process.env.LOCALAPPDATA || '', 'ms-playwright', 'chromium-1234', 'chrome-win64', 'chrome.exe');
if (!existsSync(chrome)) throw new Error(`Fant ikke Chromium: ${chrome}`);
mkdirSync(join(ROT, 'og'), { recursive: true });
const tmp = join(tmpdir(), 'nn-og'); mkdirSync(tmp, { recursive: true });
for (const s of S) {
  const f = join(tmp, `${s.bilde}.html`); writeFileSync(f, html(s));
  execFileSync(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1200,630',
    '--virtual-time-budget=6000', `--screenshot=${join(ROT, 'og', s.bilde + '.png')}`, 'file:///' + f.replace(/\\/g, '/')], { stdio: 'ignore' });
  console.log('bilde', s.bilde);
}

// ── Merker i <head> ──
const esc = t => t.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
for (const s of S) {
  const p = join(ROT, s.fil); let h = readFileSync(p, 'utf8');
  const adr = s.fil === 'index.html' ? `${URL}/` : `${URL}/${s.fil}`;
  // Versjonsmerke fra bildets innhold: Facebook og Messenger henter et nytt bilde når kortet endres.
  const v = createHash('md5').update(readFileSync(join(ROT, 'og', s.bilde + '.png'))).digest('hex').slice(0, 8);
  const bildeUrl = `${URL}/og/${s.bilde}.png?v=${v}`;
  const alt = `${s.kicker}: ${s.h.replace(/-<br>/g, '').replace(/<br>/g, ' ')}. ${s.sub}`;
  const blokk = `<!-- OG BEGIN (tools/og.mjs) -->
<meta name="description" content="${esc(s.tekst)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="${SITE}">
<meta property="og:locale" content="nb_NO">
<meta property="og:url" content="${adr}">
<meta property="og:title" content="${esc(s.tittel)}">
<meta property="og:description" content="${esc(s.tekst)}">
<meta property="og:image" content="${bildeUrl}">
<meta property="og:image:secure_url" content="${bildeUrl}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(s.tittel)}">
<meta name="twitter:description" content="${esc(s.tekst)}">
<meta name="twitter:image" content="${bildeUrl}">
<link rel="icon" href="og/ikon.svg" type="image/svg+xml">
<!-- OG END -->`;
  if (h.includes('<!-- OG BEGIN')) h = h.replace(/<!-- OG BEGIN[\s\S]*?<!-- OG END -->/, blokk);
  else h = h.replace(/(<title>[^<]*<\/title>\r?\n)/, `$1${blokk}\n`);
  if (!h.includes('<!-- OG BEGIN')) throw new Error(`Fant ikke <title> i ${s.fil}`);
  writeFileSync(p, h);
  console.log('merker', s.fil, `${s.tittel.length}/${s.tekst.length} tegn`);
}
writeFileSync(join(ROT, 'og', 'ikon.svg'), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#051C2C"/><rect x="8" y="8" width="20" height="4" fill="#5C82FF"/><text x="8" y="50" font-family="Georgia,serif" font-weight="700" font-size="34" fill="#EEF3F8">NN</text></svg>');
