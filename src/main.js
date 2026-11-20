import './styles/tokens.css';
import './styles/base.css';
import './styles/charts.css';
import './styles/nav.css';
import './styles/komponenter.css';
import { initTheme } from './lib/theme.js';
import { initNav } from './lib/nav.js';
import { initSearch } from './lib/search.js';
import { initScrolly } from './lib/scrolly.js';
import { initFylketall } from './lib/fylketall.js';
import { initFunn } from './lib/funn.js';
import { initIngress } from './lib/ingress.js';
import { initTabeller } from './lib/tabeller.js';
import { startCharts, placeholder } from './charts/core.js';
import { kortNavn } from './lib/format.js';
import { navKort, navNivaa } from './lib/navkort.js';
import { skattKort, pendlingKort, naeringKort } from './lib/okonomikort.js';
import { profilHTML, rangLinjer } from './lib/profil.js';
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
import './charts/tidslinje.js';
import './charts/pyramide.js';
import './charts/politikk.js';

initNav();
initTheme();
const sok = initSearch();
// Gammel kode (assets/app.js) bruker NN.placeholder() for å be om nye diagrammer.
window.NN = { placeholder, kortNavn, sok, navKort, navNivaa, skattKort, pendlingKort, naeringKort, profilHTML, rangLinjer };
startCharts();
initScrolly();
initFylketall();
initFunn();
initIngress();
initTabeller();

// Ferskeste folketallsdato (01222) fylles inn der siden ber om det.
document.addEventListener('DOMContentLoaded', () => {
  const d = typeof BEFK_DATA !== 'undefined' ? BEFK_DATA.dato_norsk : null; // eslint-disable-line no-undef
  if (d) document.querySelectorAll('[data-befk-dato]').forEach(el => { el.textContent = d; });
});
