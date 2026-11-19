#!/usr/bin/env python3
"""Legger hovedfunnene (godkjent 19.11.2026, analyse/HOVEDFUNN-UTKAST.md) inn under heroen på temasidene.

Hvert funn: (tekst, aktnummer i rekkefølgen på siden, etikett i lenken). Kjøres på nytt ved endringer; en eksisterende
boks (<aside class="nn-funn"> … </aside>) erstattes. Kontroll av tallene mot sidene: tools/sjekk_funn.py.
Kjør fra repo-roten:  python tools/legg_inn_funn.py
"""
import html, re
from pathlib import Path

FUNN = {
    "tema-flyktning.html": [
        ("Netto 75 347 flyttet sørover fra Nord-Norge i 2002–2025, nesten like mange som bor i Tromsø.", 1, "Akt 01"),
        ("Fem år etter bosetting bor fire av fem flyktninger fortsatt i kommunen: 82 % i Nordland, 81 % i Troms og 90 % i Finnmark.", 3, "Akt 03"),
        ("Etter ti år har sju av ti flyttet fra bosettingskommunen. Etter 20 år er netto bevaring for innvandrere fra ti flyktningland 19 %.", 4, "Akt 04"),
        ("Nord-Norge tok imot 18,6 % av flyktningene som ble bosatt i 2025. Flytteforbudet er varslet, men ikke foreslått.", 5, "Akt 05"),
        ("Innvandringen har veid opp for utflyttingen: uten flytting i noen retning ville folketallet vært om lag 12 750 lavere.", 6, "Akt 06"),
    ],
    "tema-o6.html": [
        ("Seks kommuner, 7,5 % av antallet, har 46,6 % av innbyggerne.", 1, "Akt 01"),
        ("Tromsø alene har flere innbyggere enn de 18 kommunene i Finnmark til sammen.", 1, "Akt 01"),
        ("De 74 mindre kommunene har fem år høyere medianalder og 3,6 prosentpoeng lavere sysselsetting enn de seks største.", 4, "Akt 04"),
        ("12 av de 74 mindre kommunene er i ROBEK, mot én av de seks største.", 4, "Akt 04"),
        ("Helsereformutvalget vil ha større kommuner. 74 av 80 kommuner i nord har under 15 000 innbyggere, mot 275 av 357 i landet.", 6, "Akt 06"),
    ],
    "tema-kvinneflukt.html": [
        ("I alderen 18–44 år bor det 108,8 menn per 100 kvinner i Nord-Norge, og om lag 7 100 kvinner mangler mot full balanse.", 1, "Akt 01"),
        ("50 av 80 kommuner har over 110 menn per 100 kvinner, og 21 har over 120.", 1, "Akt 01"),
        ("Jo mindre kommunen er, desto større er mannsoverskuddet.", 2, "Akt 02"),
        ("Skjevheten er størst i utdanningsårene: 113 menn per 100 kvinner i alderen 18–24 år.", 3, "Akt 03"),
    ],
    "tema-arbeidskraft.html": [
        ("Bedriftene i Nord-Norge mangler 5 850 personer i 2026. Det er 17,3 % av landets mangel, mens landsdelen har 8,7 % av befolkningen.", 1, "Akt 01"),
        ("To av næringene med størst mangel, helse og sosial og undervisning, er i hovedsak kommunale.", 2, "Akt 02"),
        ("Det kommunale underskuddet kan bli 11 797 stillinger i 2050, dobbelt så stort som dagens samlede mangel.", 4, "Akt 03½"),
        ("Teller man alle som ikke er i arbeid per sysselsatt i stedet for alder, ligger Nord-Norge på landsnivå.", 6, "Akt 04"),
        ("Troms og Nordland venter den høyeste sysselsettingsveksten i landet, mens gruppen i arbeidsfør alder blir mindre.", 7, "Akt 05"),
    ],
    "tema-aldring.html": [
        ("Forsørgerbrøken i OECD stiger fra 22 i 2000 til 52 i 2050. Norge ligger på 49 med samme grunnlag.", 1, "Akt 01"),
        ("Nord-Norge når om lag 51 i 2050, over landet (47), men under Innlandet og Telemark.", 3, "Akt 03"),
        ("Fram til 2035 er det bare Västerbotten og Nord-Österbotten som får flere i arbeidsfør alder. Aldringen er sterkere i Nord-Norge.", 3, "Akt 03"),
        ("Antallet over 80 år øker med 92 % fram mot 2050, mens gruppen 20–64 år går ned med 7,2 %.", 4, "Akt 04"),
        ("Eldreomsorgen kan trenge 8,7 årsverk per 100 i arbeidsfør alder i 2050, mot 5,9 i dag.", 4, "Akt 04"),
    ],
    "tema-scenarier.html": [
        ("Utgangspunktet er 489 778 innbyggere, en mangel på 5 850 arbeidstakere og en forsørgerbrøk som stiger til 51 i 2050.", 1, "Akt 01"),
        ("Tre veivalg avgjør framtiden: arbeidskraft i nord, mer fornybar energi og mer foredling og tjenester.", 2, "Akt 02"),
        ("De fire mulige framtidene i 2040 spenner fra «Pendlersamfunn» til «Det meste er Nord».", 3, "Akt 03"),
        ("Mange milepæler fram mot 2040 er allerede vedtatt eller planlagt, blant annet i kraftnett, kvoter, baser og industri.", 4, "Akt 03½"),
    ],
    "tema-bolig.html": [
        ("Igangsettingstillatelsene er på det laveste nivået siden 2000: 1 239 boliger de siste tolv månedene, 25 % færre enn året før.", 1, "Akt 01"),
        ("40 av 80 kommuner har ikke gitt én eneste igangsettingstillatelse hittil i 2026.", 1, "Akt 01"),
        ("Boligbehovet faller ikke med folketallet, fordi husholdningene blir mindre.", 2, "Akt 02"),
        ("Kvadratmeterprisen for brukte boliger er 27 % under landssnittet. Det gjør det vanskeligere å få nybygging til å lønne seg.", 3, "Akt 03"),
        ("28,5 % av husholdningene leier boligen, mot 27,3 % i landet.", 5, "Akt 05"),
    ],
    "tema-naering.html": [
        ("Arbeidslivet kan etterspørre 42 000 flere enn det finnes folk til i 2040, ifølge Samfunnsøkonomisk Analyse.", 1, "Akt 01"),
        ("Sjømat står for 4,7 % av sysselsettingen i nord, mot 1,0 % i landet.", 2, "Akt 02"),
        ("Sysselsettingen vokste 6,1 % fra 2015 til 2025, mot 10,6 % i landet. Havbruk og IKT trakk veksten.", 3, "Akt 03"),
        ("Når arbeidskraften blir knapp, får næringene med lavest lønnsevne, som reiselivet, dekket minst av behovet.", 6, "Akt 06"),
        ("Byggnæringen er den eneste med negative utsikter både i 2026 og 2027. Bygg og anlegg har mistet 5,1 % av de sysselsatte siden 2022.", 7, "Akt 07"),
    ],
    "tema-pensjon.html": [
        ("Kommunene har betalt 6,1 milliarder kroner mer i pensjonspremie enn de har ført som kostnad, 8,9 % av driftsinntektene.", 1, "Akt 01"),
        ("Etterslepet er størst i Troms, med 11,4 % av driftsinntektene, mot 7,7 % i Nordland og Finnmark.", 2, "Akt 02"),
        ("I 48 av 80 kommuner er premieavviket større enn disposisjonsfondet.", 2, "Akt 02"),
        ("Bodø, Tromsø og Harstad bærer risikoen i egne pensjonskasser. De andre 77 kommunene deler den i KLP.", 3, "Akt 03"),
        ("Pensjonskostnaden faller til 6,4 % av driftsinntektene i 2026 og er 7,6 % i 2030 i basisscenariet.", 4, "Akt 04"),
    ],
    "tema-ung.html": [
        ("68 % av de unge voksne tror de bor i Nord-Norge om fem år, men antallet 18–34-åringer faller med 17,6 % fram mot 2050.", 1, "Akt 01"),
        ("Fra 2031 blir det flere over 67 år enn unge voksne i landsdelen.", 1, "Akt 01"),
        ("80 % mener Nord-Norge er et godt sted å bo, men bare 54 % mener landsdelen gir gode karrieremuligheter.", 2, "Akt 02"),
        ("Bare én av tre mener kommunen jobber for innbyggernes beste, mot halvparten av de unge i sør.", 6, "Akt 06"),
        ("4 841 unge i alderen 15–24 år står utenfor arbeid og utdanning. Andelen har økt siden 2021 og er nå høyere enn i landet.", 7, "Akt 07"),
    ],
    "tema-nordomrade.html": [
        ("Tre regjeringer har lagt fram sju dokumenter siden 2006, men ingen satte et tallfestet mål for folketallet.", 4, "Akt 04"),
        ("Ordene for sikkerhet og forsvar forekom 139,1 ganger per 10 000 ord i 2025, mot 16,9 i 2006.", 3, "Akt 03"),
        ("Landsdelens andel av landets befolkning falt fra 9,97 % i 2006 til 8,70 % i 2026.", 5, "Akt 05"),
        ("All vekst kom fra innvandring: netto 80 934 fra utlandet, mens 64 151 flyttet netto til resten av landet.", 5, "Akt 05"),
        ("Nesten halvparten av de nye arbeidsplassene siden 2008 kom i helse og omsorg, ikke i satsingsnæringene.", 6, "Akt 06"),
    ],
    "tema-helse.html": [
        ("Aldringen alene gir 24,8 % flere liggedøgn fram mot 2045. Helse Nords plan regner med 7,3 %.", 2, "Akt 02"),
        ("Hele nettoveksten i sykepleiere siden 2019 kom fra utenlandsfødte.", 3, "Akt 03"),
        ("Fire av ti bor i kommuner med over én times kjøretid til nærmeste akuttsykehus.", 4, "Akt 04"),
        ("Pasientene i Helse Nord ventet i gjennomsnitt 65,8 dager før behandlingen startet, mot 61,5 dager i landet.", 6, "Akt 06"),
        ("Helsereformutvalgets flertall vil legge ned Helse Nord RHF og redusere antallet helseforetak i landet til 10–15.", 7, "Akt 07"),
    ],
}


def boks(funn):
    # hardt mellomrom i tall («11 797», «24,8 %»), så de ikke brekkes over to linjer
    hardt = lambda s: re.sub(r"(?<=\d) (?=\d{3}\b)|(?<=\d) (?=%)", "&nbsp;", s)
    li = "\n".join(f'    <li>{hardt(html.escape(t, quote=False))} <a href="#" data-akt="{n}">→&nbsp;{e}</a></li>' for t, n, e in funn)
    return f'<aside class="nn-funn" aria-labelledby="funn-h">\n  <h2 id="funn-h">Hovedfunn</h2>\n  <ol>\n{li}\n  </ol>\n</aside>'


def main():
    rot = Path(__file__).resolve().parents[1]
    for fil, funn in FUNN.items():
        p = rot / fil
        t = p.read_text(encoding="utf-8")
        ny = boks(funn)
        if '<aside class="nn-funn"' in t:
            t = re.sub(r'<aside class="nn-funn".*?</aside>', lambda _m: ny, t, flags=re.S)
        else:
            m = re.search(r'(<section class="tema-hero"[^>]*>.*?</section>)', t, flags=re.S)
            assert m, f"fant ikke tema-hero i {fil}"
            t = t[:m.end()] + "\n\n" + ny + t[m.end():]
        p.write_text(t, encoding="utf-8")
        print(f"{fil}: {len(funn)} funn")


if __name__ == "__main__":
    main()
