#!/usr/bin/env python3
"""Flytter en temaside over til de felles komponentene i src/styles/komponenter.css (PLAN-LAYOUT-1-3.md, fase A).

Bruk: python tools/migrer_komponenter.py <side.html> <boks-klasse> [prefiks]
  boks-klasse  sidens figurbeholder, f.eks. hs-boks, ug-boks, graf-kort
  prefiks      sidens prefiks for tabell/merke/mellomtittel, f.eks. hs eller ug (valgfritt)

Figurbeholder med tittel  → <figure class="nn-fig"><h3>…</h3> … </figure>
Figurbeholder uten tittel → <div class="nn-boks"> … </div>
<prefiks>-tabell → nn-tabell, <prefiks>-rull → nn-tabell-rull, <prefiks>-merke → nn-etikett,
<prefiks>-h3 → nn-h3, <prefiks>-p → nn-p. Stilregler for de gamle klassene fjernes fra sidens <style>.
Skriptet er idempotent: kjøres det på nytt, endres ingenting.
"""
import re, sys
from pathlib import Path

side, boks = Path(sys.argv[1]), sys.argv[2]
pre = sys.argv[3] if len(sys.argv) > 3 else None
t = side.read_text(encoding="utf-8")
linjer = t.split("\n")
ut, i, nfig, nboks = [], 0, 0, 0
apne = re.compile(r'^(\s*)<(div|section) class="' + re.escape(boks) + r'"( [^>]*)?>\s*$')
while i < len(linjer):
    m = apne.match(linjer[i])
    if not m:
        ut.append(linjer[i]); i += 1; continue
    innrykk, tag, attr = m.group(1), m.group(2), m.group(3) or ""
    # finn avsluttende tagg på samme innrykk
    j = i + 1
    while j < len(linjer) and not re.match(r"^" + innrykk + r"</" + tag + r">\s*$", linjer[j]):
        j += 1
    indre = linjer[i + 1:j]
    # tittel: <div class="tittel">, <h3>/<h4>, eller en div/h3 med display-font i inline-stil
    tittel = re.match(r'^(\s*)<(div|h3|h4)( class="(tittel|' + re.escape(boks) + r'-tittel)"| style="[^"]*font-family:var\(--font-display\)[^"]*")?>(.*)</\2>\s*$',
                      indre[0]) if indre else None
    if tittel and (tittel.group(3) or tittel.group(2) in ("h3", "h4")):
        ut.append(f'{innrykk}<figure class="nn-fig"{attr}>')
        ut.append(f'{tittel.group(1)}<h3>{tittel.group(5)}</h3>')
        ut.extend(indre[1:])
        ut.append(f"{innrykk}</figure>")
        nfig += 1
    else:
        ut.append(f'{innrykk}<div class="nn-boks"{attr}>')
        ut.extend(indre)
        ut.append(f"{innrykk}</div>")
        nboks += 1
    i = j + 1
t = "\n".join(ut)

if pre:
    for gammel, ny in ((f"{pre}-tabell", "nn-tabell"), (f"{pre}-rull", "nn-tabell-rull"), (f"{pre}-merke", "nn-etikett"),
                       (f"{pre}-h3", "nn-h3"), (f"{pre}-p", "nn-p")):
        t = re.sub(r'(class="[^"]*?)\b' + re.escape(gammel) + r'\b', lambda m: m.group(1) + ny, t)
        t = re.sub(r"'" + re.escape(gammel) + r"'", f"'{ny}'", t)

# små forklarings- og kildetekster med inline-stil → felles klasser (bare i markup, ikke i skriptstrenger)
def hint(m):
    innrykk, stil, rest = m.group(1), m.group(2), m.group(3)
    if "12.5px" in stil:
        ny = "nn-p"                      # brødtekst («Pedagogisk poeng» o.l.)
    elif "11.5px" in stil or "margin-top" in stil:
        ny = "nn-kilde"                  # kilde- og forbeholdslinje under figuren
    elif "12px" in stil:
        ny = "nn-fig-enhet"              # forklaring rett under figurtittelen
    else:
        return m.group(0)
    return f'{innrykk}<p class="{ny}"{rest}>'


t = re.sub(r'(?m)^(\s*)<p class="hint" style="([^"]*)"([^>]*)>', hint, t)

# fjern stilregler for klasser som ikke lenger brukes i markup eller skript
stil = re.search(r"<style>(.*?)</style>", t, re.S)
if stil:
    regler = stil.group(1).split("\n")
    behold = []
    resten = t.replace(stil.group(0), "")
    i_bruk = lambda k: re.search(r'(class="[^"]*\b' + re.escape(k) + r'\b|\'' + re.escape(k) + r'\b)', resten)

    def foreldet(sel):
        kl = re.findall(r"\.([a-zA-Z][\w-]*)", sel)
        return any((k == boks or (pre and k.startswith(pre + "-") and k.split("-", 1)[1] in ("tabell", "rull", "merke", "h3", "p", "boks")))
                   and not i_bruk(k) for k in kl)

    for r in regler:
        if "{" not in r:
            behold.append(r); continue
        sel, kropp = r.split("{", 1)
        deler = [s for s in sel.split(",") if s.strip()]
        igjen = [s for s in deler if not foreldet(s)]
        if not igjen:
            continue          # hele regelen gjelder utgåtte klasser
        # regler med flere selektorer beholder de som fortsatt er i bruk
        behold.append(",".join(igjen) + "{" + kropp if len(igjen) < len(deler) else r)
    t = t.replace(stil.group(1), "\n".join(behold))
side.write_text(t, encoding="utf-8")
print(f"{side}: {nfig} figurer, {nboks} notisbokser")
