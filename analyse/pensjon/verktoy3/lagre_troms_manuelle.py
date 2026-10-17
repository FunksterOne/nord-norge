"""Manuelt leste pensjonsnoter for fire Troms-kommuner (2025), hentet fra åpne kilder på kommunenes egne nettsider.
Skriver manuelle/<nr>.json etter SKJEMA.md."""
import json, os

HER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLP3 = [{"ordning": "Fellesordningen", "leverandor": "KLP", "gruppe": "fellesordning"},
        {"ordning": "Sykepleiere", "leverandor": "KLP", "gruppe": "sykepleiere"},
        {"ordning": "Folkevalgte", "leverandor": "KLP", "gruppe": "folkevalgte"},
        {"ordning": "Lærere", "leverandor": "SPK", "gruppe": "laerere"}]
FORUT = {"diskonteringsrente": 4.0, "avkastning": 4.5, "lonnsvekst": 2.97, "g_regulering": 2.97, "pensjonsregulering": 2.2}

poster = [
    {"nr": "5522", "navn": "Salangen", "regnskapsaar": 2025,
     "kilde_url": "https://www.salangen.kommune.no/download/18.628541b919d9a49ccc2b986/1777467945048/Salangen%20kommune%20-%20innkalling%20til%20m%C3%B8te%20i%20kontrollutvalget%2006.05.2026%20-%20samlet.pdf",
     "kilde_side": "note 11, PDF-side 38–39 (skannet, lest av sidebilde); årsberetning s. 19–20",
     "konsern_eller_kasse": "kommunekasse", "leverandorer": KLP3,
     "brutto_pensjonsforpliktelse": 583143988, "pensjonsmidler": 598925746, "netto_forpliktelse": -15781758,
     "netto_inkl_aga": -15855174, "aarets_pensjonskostnad": 23857058, "innbetalt_premie": 43556490,
     "aarets_premieavvik": 19699432, "akkumulert_premieavvik": 56190969, "akkumulert_premieavvik_inkl_aga": 59056711,
     "amortisering_aar": 7, "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": 5974420,
     "forutsetninger": FORUT, "sykepleiere_separat": True,
     "merknader": "Kontrollutvalgets samlede møtedokumenter 6. mai 2026 på kommunens nettside; regnskapet er skannet og tallene lest av sidebilder. Amortisering 2025: 10 056 668. AGA 5,1 % på akkumulert premieavvik (2 865 742). Premiefond 01.01: 19 659 034, tilført 25 558 347, brukt 5 974 420, 31.12: 39 242 961. Per ordning: KLP felles −6 986 122, KLP sykepleiere −8 172 470, KLP folkevalgte −2 062 713, SPK +1 439 548 (netto). Estimatavvik 2025: forpliktelse +46 045 902, midler +31 615 550. SPK pensjonsregulering oppgitt 0,00 %. Årsberetningen: premieavviket økte med 9,6 mill. kr inkl. AGA; likviditetsutfordringer knyttes til premieavvik, amortiseringsvalg og bruk av premiefond. Stemmer med KOSTRA 13545 (59,1 mill. kr)."},
    {"nr": "5526", "navn": "Sørreisa", "regnskapsaar": 2025,
     "kilde_url": "https://www.sorreisa.kommune.no/download/18.25c6ef6919e48e7478821/1779343816136/Kontrollutvalget%20innkalling%20270526.pdf",
     "kilde_side": "balanse PDF-side 34, note 11 PDF-side 44–45 (bilde), revisors brev s. 15, årsmelding s. 57–58",
     "konsern_eller_kasse": "kommunekasse",
     "leverandorer": [{"ordning": "Fellesordningen og sykepleiere", "leverandor": "KLP", "gruppe": "fellesordning"},
                      {"ordning": "Lærere", "leverandor": "SPK", "gruppe": "laerere"}],
     "brutto_pensjonsforpliktelse": 638121825, "pensjonsmidler": 714827471, "netto_forpliktelse": -76705646,
     "netto_inkl_aga": -76619538, "aarets_pensjonskostnad": 23234733, "innbetalt_premie": 45153361,
     "aarets_premieavvik": 21918628, "akkumulert_premieavvik": 74856570, "akkumulert_premieavvik_inkl_aga": 78674255,
     "amortisering_aar": 7, "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": 6400000,
     "forutsetninger": FORUT, "sykepleiere_separat": True,
     "merknader": "Kontrollutvalgets møtedokumenter 27. mai 2026 på kommunens nettside; notetabellene er bilder og lest visuelt. Summert KLP (felles+sykepleiere) og SPK: netto kostnad 20 662 430 + 2 572 303; premie 42 804 513 + 2 348 848; årets premieavvik 22 142 083 − 223 455; amortisering 15 022 210 + 144 221 = 15 166 431. Akkumulert premieavvik inkl. AGA: KLP 77 821 741, SPK 852 514. Balansen viser premieavvik 77 821 737 som eiendel og 1 322 229 under kortsiktig gjeld med positivt fortegn; revisor påpeker at årets SPK-premieavvik er ført feil vei (446 912 for mye inntektsført), rettes i 2026. KOSTRA (76,5 mill.) = eiendel minus gjeldsposten. AGA 5,1 %. Premiefond 01.01: 74 625 372, tilført 32 571 871, brukt 6 400 000, 31.12: 100 797 247. Estimatavvik 2025: KLP forpliktelse +61 842 047, midler +41 024 087. Per ordning: KLP felles −67 942 988, KLP sykepleiere −10 451 041, SPK +1 688 383. Disposisjonsfond bare 3 255 691 (7 318 882 i 2024)."},
    {"nr": "5538", "navn": "Storfjord", "regnskapsaar": 2025,
     "kilde_url": "https://www.storfjord.kommune.no/download/18.78b8d2c51a08633d475db3/1789124091715/Avlagt+a%CC%8Arsregnskap+2025+Storfjord+kommune.pdf",
     "kilde_side": "note 10, PDF-side 11–13 (bilde), balanse s. 27",
     "konsern_eller_kasse": "kommunekasse", "leverandorer": KLP3,
     "brutto_pensjonsforpliktelse": 430268077, "pensjonsmidler": 429907018, "netto_forpliktelse": 361059,
     "netto_inkl_aga": 361059, "aarets_pensjonskostnad": 17086415, "innbetalt_premie": 22933266,
     "aarets_premieavvik": 5846851, "akkumulert_premieavvik": 24667958, "akkumulert_premieavvik_inkl_aga": 24667958,
     "amortisering_aar": 7, "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": 12206629,
     "forutsetninger": FORUT, "sykepleiere_separat": True,
     "merknader": "«Avlagt årsregnskap 2025» på kommunens årsregnskapsside, publisert etter at gruppeagenten søkte (den fant bare en versjon uten note 10). Notesidene er bilder og lest visuelt. AGA-sone 5 (0 %). Noten oppgir årets premieavvik som −5 846 851 i én tabell, men B−A = +5 846 851 og akkumulert premieavvik øker tilsvarende. Amortisering 6 088 248. Sum gjenstående premieavvik 01.01 korrigert til 24 909 355 (noten sier fjorårets tall var feil). Premiefond 01.01: 10 923 717, tilført 17 154 195, brukt 12 206 629, 31.12: 15 871 283. Estimatavvik 2025: forpliktelse +36 809 418, midler +27 215 679. Per ordning: KLP felles +6 723 979, KLP sykepleiere −6 425 651, KLP folkevalgte −1 209 384, SPK +1 272 115. Disposisjonsfond 10 498 831. Stemmer med balansen og KOSTRA (24,7 mill.)."},
    {"nr": "5542", "navn": "Skjervøy", "regnskapsaar": 2025,
     "kilde_url": "https://www.skjervoy.kommune.no/download/18.559dad6619ed43a91867388/1782826466890/Innkalling%20til%20m%C3%B8te%20i%20kontrollutvalget%20i%20Skjerv%C3%B8y%20kommune%20-%20onsdag%2013.05.2026.pdf",
     "kilde_side": "balanse PDF-side 37, note 5 PDF-side 46–47",
     "konsern_eller_kasse": "kommunekasse",
     "leverandorer": [{"ordning": "Fellesordningen og sykepleiere", "leverandor": "KLP", "gruppe": "fellesordning"},
                      {"ordning": "Lærere", "leverandor": "SPK", "gruppe": "laerere"}],
     "brutto_pensjonsforpliktelse": 651644102, "pensjonsmidler": 664603361, "netto_forpliktelse": -12959259,
     "netto_inkl_aga": -12959259, "aarets_pensjonskostnad": 25831714, "innbetalt_premie": 40835751,
     "aarets_premieavvik": 13998662, "akkumulert_premieavvik": 55997960, "akkumulert_premieavvik_inkl_aga": 55997960,
     "amortisering_aar": 7, "reguleringspremie": None, "egenkapitaltilskudd_klp": None, "premiefond_bruk": None,
     "forutsetninger": FORUT, "sykepleiere_separat": False,
     "merknader": "Kontrollutvalgets møtedokumenter 13. mai 2026 på kommunens nettside; tekstbasert PDF. Summert KLP-sumside og SPK: brutto 615 248 221 + 36 395 881 (= balansen), midler 630 386 713 + 34 216 648 (= balansen), netto kostnad 22 235 333 + 3 596 381, premie 37 175 496 + 3 660 255, årets premieavvik 14 058 304 − 59 642, amortisering 11 315 549 + 392 065 = 11 707 614. Akkumulert premieavvik i balansen 55 997 960 (note: KLP 54 495 603 + SPK 1 502 344). AGA-sone 5 (0 %). KLP-forpliktelsen fikk estimatavvik 56 771 407, hvorav planendring 36 051 741 (trolig AFP og særaldersregler). SPK-noten har «#REF!» i én celle. KLP-medlemmer 01.01.2025: 402 aktive, 724 oppsatte, 368 pensjoner. Disposisjonsfond 96 207 629. Premiefond ikke oppgitt i de leste sidene. Stemmer med KOSTRA (56,0 mill.)."},
]

for p in poster:
    with open(os.path.join(HER, 'manuelle', p['nr'] + '.json'), 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    print('lagret', p['nr'], p['navn'])
