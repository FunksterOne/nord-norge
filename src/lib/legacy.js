// Tilgang til globale strukturer fra de klassiske skriptene (assets/data.js, assets/app.js).
// Toppnivå-const/let i klassiske skript blir ikke egenskaper på window, men er
// synlige som globale navn – derfor typeof-vakter i stedet for window.X.
/* global DATA, K, AGG, state, REGIONS, KREGION, NAV_BEDRIFT, BEFK_DATA, BOLIG_DATA, BEHOV_DATA, MARKED_DATA, SSB_FLOWS, ARBEID_DATA, LEVEKAR_DATA, GJELD_DATA, PENSJON_DATA, UNG_DATA, BOFAST_DATA, ELDRE_DATA */
export const L = {
  get DATA() { return typeof DATA !== 'undefined' ? DATA : null; },
  get K() { return typeof K !== 'undefined' ? K : []; },
  get AGG() { return typeof AGG !== 'undefined' ? AGG : {}; },
  get state() { return typeof state !== 'undefined' ? state : {}; },
  get REGIONS() { return typeof REGIONS !== 'undefined' ? REGIONS : []; },
  get KREGION() { return typeof KREGION !== 'undefined' ? KREGION : {}; },
  get NAV() { return typeof NAV_BEDRIFT !== 'undefined' ? NAV_BEDRIFT : null; },
  get BEFK() { return typeof BEFK_DATA !== 'undefined' ? BEFK_DATA : null; },
  get BOLIG() { return typeof BOLIG_DATA !== 'undefined' ? BOLIG_DATA : null; },
  get BEHOV() { return typeof BEHOV_DATA !== 'undefined' ? BEHOV_DATA : null; },
  get MARKED() { return typeof MARKED_DATA !== 'undefined' ? MARKED_DATA : null; },
  get FLOWS() { return typeof SSB_FLOWS !== 'undefined' ? SSB_FLOWS : null; },
  get ARBEID() { return typeof ARBEID_DATA !== 'undefined' ? ARBEID_DATA : null; },
  get LEVEKAR() { return typeof LEVEKAR_DATA !== 'undefined' ? LEVEKAR_DATA : null; },
  get GJELD() { return typeof GJELD_DATA !== 'undefined' ? GJELD_DATA : null; },
  get PENSJON() { return typeof PENSJON_DATA !== 'undefined' ? PENSJON_DATA : null; },
  get UNG() { return typeof UNG_DATA !== 'undefined' ? UNG_DATA : null; },
  get BOFAST() { return typeof BOFAST_DATA !== 'undefined' ? BOFAST_DATA : null; },
  get ELDRE() { return typeof ELDRE_DATA !== 'undefined' ? ELDRE_DATA : null; },
  get NAERING() { return typeof NAERING_DATA !== 'undefined' ? NAERING_DATA : null; }, // eslint-disable-line no-undef
  MW(o) { return typeof window.MW === 'function' ? window.MW(o) : null; },
};
