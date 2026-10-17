// Laster datagrunnlaget utenfor nettleseren, for kontroll av tall i tekst.
// Bruk: const F = require('./tools/fasit.cjs'); F.DATA, F.K, F.AGG, F.NAERING_DATA ...
// Kjører assets/data.js og toppen av assets/app.js (K og AGG) i en sandkasse med minimale stubber.
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const rot = path.join(__dirname, '..');
const data = fs.readFileSync(path.join(rot, 'assets/data.js'), 'utf8');
const app = fs.readFileSync(path.join(rot, 'assets/app.js'), 'utf8');
// Ta med app.js til og med AGG-byggingen (før første funksjon som trenger DOM)
const slutt = app.indexOf('function resolveSel(');
const topp = app.slice(0, slutt);

const navn = ['DATA', 'K', 'AGG', 'state', 'REGIONS', 'KREGION', 'FY', 'SOURCES', 'ARBEID_DATA', 'BEFK_DATA', 'BEHOV_DATA', 'BOLIG_DATA',
  'GJELD_DATA', 'PENSJON_DATA', 'HUSH_DATA', 'KJONN_DATA', 'KOHORT_RET', 'LEIE_DATA', 'LEVEKAR_DATA', 'MARKED_DATA', 'NAERING_DATA', 'NAV_BEDRIFT',
  'RENTE_DATA', 'SSB_FLOWS', 'FYNR', 'SM', 'SGROUPS', 'AGES'];
const ctx = {
  window: { location: { search: '', pathname: '/' } },
  document: { getElementById: () => null, querySelector: () => null, querySelectorAll: () => [], addEventListener: () => {} },
  URLSearchParams, console, localStorage: { getItem: () => null, setItem: () => {} },
};
vm.createContext(ctx);
vm.runInContext(data + '\n' + topp + '\n;globalThis.__ut = {' + navn.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(',') + '};', ctx);
module.exports = ctx.__ut;

// Hjelpere
const sum = a => a.reduce((s, x) => s + (x || 0), 0);
module.exports.sum = sum;
module.exports.alderSum = (alder, fra, til = 105) => sum(alder.slice(fra, til + 1));
module.exports.nb = (v, d = 0) => v.toLocaleString('nb-NO', { minimumFractionDigits: d, maximumFractionDigits: d });

if (require.main === module) {
  const F = module.exports;
  console.log('Globale:', Object.keys(F).filter(k => F[k] !== undefined && typeof F[k] !== 'function').join(', '));
  console.log('Antall kommuner:', F.K.length, '· sum folketall (K.pop):', sum(F.K.map(k => k.pop)));
  console.log('AGG-nøkler:', Object.keys(F.AGG).join(', '));
  console.log('Felt i K[0]:', Object.keys(F.K[0]).join(', '));
  console.log('Felt i DATA:', Object.keys(F.DATA).join(', '));
}
