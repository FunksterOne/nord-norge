import './styles/tokens.css';
import './styles/base.css';
import './styles/charts.css';
import { initTheme } from './lib/theme.js';
import { initSearch } from './lib/search.js';
import { initScrolly } from './lib/scrolly.js';
import { startCharts, placeholder } from './charts/core.js';
import './charts/proj.js';
import './charts/map.js';
import './charts/plassering.js';
import './charts/trykk.js';
import './charts/skjebner.js';
import './charts/gap.js';
import './charts/linjer.js';
import './charts/spredning.js';
import './charts/stolper.js';
import './charts/hstolper.js';
import './charts/mini.js';
import './charts/stablet.js';
import './charts/backtest.js';
import './charts/rang.js';
import './charts/naering.js';
import './charts/pyramide.js';

initTheme();
initSearch();
// Gammel kode (assets/app.js) bruker NN.placeholder() for å be om nye diagrammer.
window.NN = { placeholder };
startCharts();
initScrolly();

// Ferskeste folketallsdato (01222) fylles inn der siden ber om det.
document.addEventListener('DOMContentLoaded', () => {
  const d = typeof BEFK_DATA !== 'undefined' ? BEFK_DATA.dato_norsk : null; // eslint-disable-line no-undef
  if (d) document.querySelectorAll('[data-befk-dato]').forEach(el => { el.textContent = d; });
});
