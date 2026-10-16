// Norsk tallformat: mellomrom som tusenskille, komma som desimaltegn, ekte minus.
const nf0 = new Intl.NumberFormat('nb-NO', { maximumFractionDigits: 0 });
const nfCache = new Map();

export function tall(v, des = 0) {
  if (v == null || Number.isNaN(v)) return '–';
  let f = nfCache.get(des);
  if (!f) { f = new Intl.NumberFormat('nb-NO', { minimumFractionDigits: des, maximumFractionDigits: des }); nfCache.set(des, f); }
  return f.format(v).replace(/[   ]/g, ' ').replace('-', '−');
}
export const heltall = v => (v == null ? '–' : nf0.format(Math.round(v)).replace(/[   ]/g, ' ').replace('-', '−'));
export const prosent = (v, des = 1) => (v == null ? '–' : `${tall(v, des)} %`);
export const endring = (v, des = 1) => (v == null ? '–' : `${v > 0 ? '+' : ''}${tall(v, des)}`);
export const endringPst = (v, des = 1) => (v == null ? '–' : `${endring(v, des)} %`);

// Kompakt akseformat: 12 000 → «12 000», 1 250 000 → «1,25 mill.»
export function akse(v) {
  const a = Math.abs(v);
  if (a >= 1e6) return `${tall(v / 1e6, a >= 1e7 ? 0 : 1)} mill.`;
  return heltall(v);
}

// Kort visningsnavn for tospråklige kommunenavn i trange lister:
// velg den delen som ikke har samiske/kvenske spesialtegn; ellers første del.
const UNNTAK = { 'Aarborte - Hattfjelldal': 'Hattfjelldal', 'Guovdageaidnu - Kautokeino': 'Kautokeino', 'Deatnu - Tana': 'Tana', 'Dielddanuorri - Tjeldsund': 'Tjeldsund' };
const SAMISK = /[áčđŋšŧžÁČĐŊŠŦŽäÄ]/;
export function kortNavn(n) {
  n = String(n);
  if (UNNTAK[n]) return UNNTAK[n];
  const deler = n.split(' - ');
  if (deler.length === 1) return n;
  return deler.find(d => !SAMISK.test(d)) || deler[0];
}
