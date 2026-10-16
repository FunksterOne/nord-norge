#!/usr/bin/env python3
"""Oppdaterer DATA.proj.robek i assets/data.js fra ROBEK-registeret paa
regjeringen.no (KDD, "Kommuner som er oppfoert i ROBEK").

- `kommuner`: kommunenr -> hjemmelsbokstaver i kommuneloven § 28-1 foerste ledd
  (samme format som foer: "c,d").
- `oppdatert`: datoen registeret selv oppgir ("sist oppdatert DD.MM.AAAA").
- `pending`: innmeldinger under behandling. Kommuner som naa er innfoert i
  registeret fjernes; de oevrige beholdes uendret (maa vurderes manuelt).
- Nye metadatafelt: retrieved_at, url, antall_nasjonalt, siste_endringer.

Kun de 80 nordnorske kommunene (18xx, 55xx, 56xx) tas med.
"""
import datetime
import html
import re
import sys
import urllib.request

from datajs import load_data, save_data

URL = ("https://www.regjeringen.no/no/tema/kommuner-og-regioner/kommuneokonomi/"
       "robek-2/kommuner-som-er-oppfort-i-registeret/id415422/")


def hent_tekst():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read().decode("utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"</(tr|p|h\d|li|div)>", "\n", t)
    t = re.sub(r"</t[dh]>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).replace("\xa0", " ")
    return [l.strip() for l in t.split("\n") if l.strip()]


def bokstaver(s):
    s = s.replace(" og ", ",").replace(" ", "")
    return ",".join(b for b in s.split(",") if b)


def main():
    linjer = hent_tekst()
    tekst = "\n".join(linjer)
    m = re.search(r"sist oppdatert (\d{2}\.\d{2}\.\d{4})", tekst)
    if not m:
        sys.exit("Fant ikke oppdateringsdato paa registersiden")
    oppdatert = m.group(1)
    m = re.search(r"Antall registrerte kommuner nå:\s*(\d+)", tekst)
    antall = int(m.group(1)) if m else None

    # Rader: kommunenummer (4 siffer) etterfulgt av navn og hjemmel
    nye = {}
    navn = {}
    for i, l in enumerate(linjer):
        if re.fullmatch(r"\d{4}", l) and i + 2 < len(linjer):
            nr = l
            if nr[:2] in ("18", "55", "56"):
                hj = linjer[i + 2]
                if not re.fullmatch(r"[a-g](,\s*[a-g])*(\s*og\s*[a-g])?", hj):
                    sys.exit(f"Uventet hjemmelsformat for {nr}: {hj!r}")
                nye[nr] = bokstaver(hj)
                navn[nr] = linjer[i + 1]

    # Siste endringer (Inn/Ut/Endringer)
    endr = {}
    m = re.search(r"Siste endringer:\s*(.*?)§ 28-1", tekst, flags=re.S)
    if m:
        for typ in ("Inn", "Ut", "Endringer"):
            mm = re.search(typ + r":(.*?)(?:\n(?:Inn|Ut|Endringer):|\Z)", m.group(1), flags=re.S)
            if mm:
                endr[typ.lower()] = [f"{d} {n.strip()}" for d, n in
                                     re.findall(r"(\d{2}\.\d{2}\.\d{4}):?\s*([^\d\n]+)", mm.group(1))]

    D = load_data()
    rb = D["proj"]["robek"]
    gamle = rb["kommuner"]
    print(f"Register oppdatert {oppdatert}; {antall} kommuner nasjonalt; "
          f"{len(nye)} i Nord-Norge (foer: {len(gamle)}, per {rb['oppdatert']}).")
    for nr in sorted(set(gamle) | set(nye)):
        a, b = gamle.get(nr), nye.get(nr)
        if a != b:
            print(f"  {nr} {navn.get(nr, '')}: {a or '-'} -> {b or '- (ut)'}")
    pend = rb.get("pending", {}) or {}
    for nr in list(pend):
        if nr in nye:
            print(f"  pending {nr} fjernet (naa innfoert med {nye[nr]})")
            del pend[nr]
    if pend:
        print(f"  pending beholdt (vurder manuelt): {sorted(pend)}")

    rb["kommuner"] = {k: nye[k] for k in sorted(nye)}
    rb["oppdatert"] = oppdatert
    rb["pending"] = pend
    rb["retrieved_at"] = datetime.date.today().isoformat()
    rb["url"] = URL
    rb["antall_nasjonalt"] = antall
    if endr:
        rb["siste_endringer"] = endr
    save_data(D)
    print("Skrev DATA.proj.robek.")


if __name__ == "__main__":
    main()
