// Hovedfunn-boksen øverst på temasidene (aside.nn-funn): lenkene peker på akt nr. N i rekkefølgen på siden
// (data-akt="N"), fordi noen akter («03½») ikke har fast id. Når aktmenyen har gitt aktene id, settes href til den.

export function initFunn() {
  document.addEventListener('DOMContentLoaded', () => setTimeout(() => {
    const akter = [...document.querySelectorAll('section.akt')];
    document.querySelectorAll('.nn-funn a[data-akt]').forEach(a => {
      const akt = akter[Number(a.dataset.akt) - 1];
      if (!akt) return;
      if (akt.id) a.setAttribute('href', '#' + akt.id);
      a.addEventListener('click', e => {
        e.preventDefault();
        akt.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (akt.id) history.replaceState(null, '', '#' + akt.id);
      });
    });
  }, 0));
}
