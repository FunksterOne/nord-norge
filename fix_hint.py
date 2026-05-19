"""Surgical replacement of projection hint text. File mixes literal Unicode
chars (« » – etc.) with literal backslash-escape sequences (\\u00e5 etc.) so
we use explicit codepoint composition."""
import sys
from pathlib import Path

HTML = Path(__file__).parent / "index.html"
html = HTML.read_text(encoding="utf-8")

BACK = chr(92)
old = (
    "'Linje = hovedalternativet (MMMM); skygget b"
    + BACK + "u00e5nd = lav (LLML) til h"
    + BACK + "u00f8y (HHMH) nasjonal vekst. SSB og Telemarksforskning vises sammen "
    + BACK + "u2014 se forklaringskortet «SSB vs. Telemarksforskning» nederst.'"
)

new = (
    "'Den m" + BACK + "u00f8rke linja viser <b>faktisk folketall 1.1.2000"
    + BACK + "u20132025</b> (SSB tabell 07459, kommuner 2024-sammensl"
    + BACK + "u00e5tte tidsserier). Den vertikale streken markerer <b>i dag</b>. "
    + "F.o.m. 2024 starter framskrivingen: SSB MMMM som heltrukken aurora-linje "
    + "med <i>lav" + BACK + "u2013h" + BACK + "u00f8y</i>-b" + BACK + "u00e5nd, "
    + "samt TF-MVP og TF-ATTR. Den lange trenden gir kontekst " + BACK + "u2014 "
    + "har kommunen vokst eller krympet de siste 25 " + BACK + "u00e5rene, "
    + "og hvordan ser banen mot 2050 ut sammenlignet med det?'"
)

n = html.count(old)
print(f"Occurrences of old: {n}")
if n != 1:
    print("Aborting — expected exactly 1 occurrence.")
    sys.exit(1)

new_html = html.replace(old, new)
HTML.write_text(new_html, encoding="utf-8")
print(f"Replaced. Length change: {len(new_html) - len(html):+d}")
