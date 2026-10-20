"""Manuelt avleste tall fra SSBs monitor for sekundærflytting (alle utgaver 2005–2025), Fafo 2025:14
og Kunnskapsbanken. Hvert tall er kontrollert mot tekstuttrekk (pdf_tekst.py / nn_rader.py /
pdf_rader.py) eller figurdata i artikkelens HTML (ssb_figurdata.py). «side» = side i PDF-fila.

Grunnlag («basis»):
  opprinnelig  = prosent av hele bosettingskohorten (utvandrede og døde inngår i nevneren)
  i_norge      = prosent av dem som fortsatt bodde i Norge (utvandrede og døde trukket fra)
"""

M = "SSB, Monitor for sekundærflytting"

# --- Fylkestabeller per kohort: bosted 1.1.(kohort+5). Basis: opprinnelig kohort -------------------
# felter: antall, første kommune, annen kommune i fylket, annet fylke utenom Oslo, Oslo, utvandret/død
FYLKE_KOHORT = {
    1998: dict(kilde=f"{M} 2005 (Notat 2005/13), tabell 3", fil="monitor_2005_notat2005-13.pdf", side=22,
               rader={"Hele landet": (3906, 53, 6, 16, 17, 8), "Nordland": (226, 21, 1, 50, 23, 5),
                      "Troms": (225, 26, 3, 25, 37, 9), "Finnmark": (86, 9, 6, 51, 28, 6)}),
    2000: dict(kilde=f"{M} 2006 (Notat 2006/31), tabell 5", fil="monitor_2006_notat2006-31.pdf", side=25,
               rader={"Hele landet": (6707, 53, 5, 18, 10, 13), "Nordland": (606, 32, 3, 36, 16, 13),
                      "Troms": (310, 27, 4, 36, 22, 12), "Finnmark": (169, 24, 2, 39, 17, 18)}),
    2001: dict(kilde=f"{M} 2007 (Notat 2007/35), tabell 13", fil="monitor_2007_notat2007-35.pdf", side=33,
               rader={"Hele landet": (7134, 60, 6, 18, 10, 6), "Nordland": (566, 39, 4, 31, 19, 8),
                      "Troms": (313, 34, 3, 40, 22, 2), "Finnmark": (160, 33, 3, 37, 21, 8)}),
    2002: dict(kilde=f"{M} 2008 (Notat 2008/43), tabell 9", fil="monitor_2008_notat2008-43.pdf", side=23,
               rader={"Hele landet": (8246, 65, 5, 17, 8, 5), "Nordland": (700, 37, 3, 38, 16, 6),
                      "Troms": (266, 37, 1, 48, 12, 3), "Finnmark": (163, 42, 4, 33, 19, 3)}),
    2003: dict(kilde=f"{M} 2009 (Notat 2009/50), tabell 10", fil="monitor_2009_notat2009-50.pdf", side=23,
               rader={"Hele landet": (6823, 69, 6, 13, 9, 3), "Nordland": (554, 49, 5, 24, 18, 4),
                      "Troms": (282, 52, 4, 26, 15, 3), "Finnmark": (165, 25, 3, 55, 16, 2)}),
    2004: dict(kilde=f"{M} 2010 (Rapporter 2010/41), tabell 4.3", fil="monitor_2010_rapp2010-41.pdf", side=21,
               rader={"Hele landet": (5770, 70, 6, 13, 9, 2), "Nordland": (408, 49, 5, 27, 18, 0),
                      "Troms": (260, 52, 4, 30, 12, 2), "Finnmark": (176, 54, 3, 24, 16, 2)}),
    2005: dict(kilde=f"{M} 2011 (Rapporter 2011/30), tabell 4.3", fil="monitor_2011_rapp2011-30.pdf", side=22,
               rader={"Hele landet": (4736, 73, 5, 13, 7, 2), "Nordland": (339, 45, 2, 35, 16, 3),
                      "Troms": (178, 47, 3, 37, 12, 0), "Finnmark": (79, 71, 3, 20, 5, 0)}),
    2006: dict(kilde=f"{M} 2013, tabell 4.3", fil="monitor_2013.pdf", side=24,
               rader={"Hele landet": (5120, 76, 4, 11, 7, 2), "Nordland": (392, 52, 2, 28, 17, 2),
                      "Troms": (199, 60, 4, 24, 11, 2), "Finnmark": (98, 58, 1, 31, 9, 0)}),
    2007: dict(kilde=f"{M} 2014, tabell 4.3", fil="monitor_2014.pdf", side=23,
               rader={"Hele landet": (5052, 77, 4, 11, 5, 3), "Nordland": (413, 66, 3, 23, 4, 3),
                      "Troms": (221, 61, 2, 27, 7, 4), "Finnmark": (148, 72, 3, 10, 14, 2)}),
    2008: dict(kilde=f"{M} 2014, tabell 4.5", fil="monitor_2014.pdf", side=28,
               rader={"Hele landet": (6015, 78, 4, 9, 5, 3), "Nordland": (588, 69, 1, 19, 9, 2),
                      "Troms": (218, 65, 1, 21, 11, 3), "Finnmark": (176, 70, 4, 17, 5, 5)}),
    2009: dict(kilde=f"{M} 2017 (Rapporter 2017/18), tabell 4.6", fil="monitor_2017_rapp2017-18.pdf", side=36,
               rader={"Hele landet": (7751, 78, 5, 9, 5, 3), "Nordland": (669, 61, 5, 21, 10, 3),
                      "Troms": (392, 71, 4, 14, 7, 3), "Finnmark": (257, 74, 3, 14, 7, 1)}),
    2010: dict(kilde=f"{M} 2017 (Rapporter 2017/18), tabell 4.7", fil="monitor_2017_rapp2017-18.pdf", side=37,
               rader={"Hele landet": (6913, 78, 5, 10, 5, 2), "Nordland": (601, 60, 5, 24, 9, 2),
                      "Troms": (294, 69, 3, 22, 5, 1), "Finnmark": (176, 71, 5, 15, 9, None)}),
    2011: dict(kilde=f"{M} 2020 (Rapporter 2020/36), tabell 4.3", fil="monitor_2020_rapp2020-36.pdf", side=33,
               rader={"Hele landet": (6933, 80, 5, 8, 5, 3), "Nordland": (618, 76, 4, 12, 6, 2),
                      "Troms": (324, 69, 5, 14, 10, 2), "Finnmark": (191, 58, 3, 30, 6, 2)}),
    2012: dict(kilde=f"{M} 2020 (Rapporter 2020/36), tabell 4.5", fil="monitor_2020_rapp2020-36.pdf", side=37,
               rader={"Hele landet": (7220, 81, 4, 8, 4, 3), "Nordland": (638, 69, 4, 18, 4, 4),
                      "Troms": (388, 74, 4, 13, 6, 3), "Finnmark": (183, 72, 2, 17, 7, 2)}),
    2015: dict(kilde="SSB, «Mer bofaste flyktninger» (2021), figur 4 (+ figur 3 for antall)",
               fil="web/mer-bofaste-flyktninger.html", side=None,
               rader={"Hele landet": (13330, 82, None, None, None, None), "Nordland": (1033, 65, 9, 18, 5, 2),
                      "Troms og Finnmark": (1026, 68, 5, 20, 6, 2)}),
    2019: dict(kilde="SSB, «Høy bofasthet blant flyktninger de første årene» (2024), figur 3",
               fil="web/hoy-bofasthet-blant-flyktninger-de-forste-arene.html", side=None,
               rader={"Hele landet": (5389, 86, None, None, 2, 1), "Nordland": (None, 82, 2, 13, 2, None),
                      "Troms": (None, 81, 2, 15, 1, 1), "Finnmark": (None, 90, None, 5, 1, 4)}),
}
# Merknad 2019: landet «11 prosent har flyttet internt i fylket eller til et annet fylke enn Oslo».
# Merknad 2010 Finnmark: utvandret/død skjult («:»). 2019: tomme celler i figuren = ikke vist (små tall).

# --- Fylke × kohort, basis i_norge ------------------------------------------------------------------
FORSTE_KOMMUNE_I_NORGE = dict(  # andel i første bostedskommune etter fem år, av dem fortsatt i Norge
    kilde=f"{M} 2009 (Notat 2009/50), tabell 11 (1997–2003) og {M} 2017, vedleggstabell 4.3 (2000–2010)",
    fil="monitor_2009_notat2009-50.pdf s. 25; monitor_2017_rapp2017-18.pdf s. 91",
    serier={
        "Hele landet": {1997: 67, 1998: 64, 1999: 59, 2000: 62, 2001: 64, 2002: 68, 2003: 71, 2004: 72, 2005: 75,
                        2006: 78, 2007: 80, 2008: 81, 2009: 80, 2010: 79},
        "Nordland": {1997: 35, 1998: 23, 1999: 27, 2000: 37, 2001: 42, 2002: 39, 2003: 51, 2004: 50, 2005: 46,
                     2006: 53, 2007: 68, 2008: 71, 2009: 63, 2010: 61},
        "Troms": {1997: 12, 1998: 45, 1999: 39, 2000: 31, 2001: 34, 2002: 38, 2003: 54, 2004: 53, 2005: 47,
                  2006: 61, 2007: 63, 2008: 67, 2009: 74, 2010: 70},
        "Finnmark": {1997: 21, 1998: 13, 1999: 35, 2000: 28, 2001: 35, 2002: 43, 2003: 25, 2004: 55, 2005: 72,
                     2006: 59, 2007: 73, 2008: 73, 2009: 75, 2010: 71},
    })
SAMME_FYLKE_I_NORGE = dict(  # andel i første bostedsfylke etter fem år, av dem fortsatt i Norge
    kilde=f"{M} 2009 (Notat 2009/50), tabell 12", fil="monitor_2009_notat2009-50.pdf s. 26",
    serier={
        "Hele landet": {1997: 72, 1998: 68, 1999: 66, 2000: 68, 2001: 70, 2002: 73, 2003: 77},
        "Nordland": {1997: 37, 1998: 24, 1999: 30, 2000: 41, 2001: 46, 2002: 42, 2003: 57},
        "Troms": {1997: 12, 1998: 49, 1999: 43, 2000: 35, 2001: 37, 2002: 39, 2003: 58},
        "Finnmark": {1997: 21, 1998: 16, 1999: 38, 2000: 31, 2001: 38, 2002: 47, 2003: 28},
    })

# --- Landet: andel som hadde forlatt første bostedskommune etter botid (år 1 = bosettingsåret) -------
LANDET_FORLATT = [
    dict(kilde="SSB, «Mer bofaste flyktninger» (2021), figur 2", fil="web/mer-bofaste-flyktninger.html",
         definisjon="forlatt første bostedskommune (inkl. utvandret)",
         kohorter={2003: [2, 8, 14, 23, 31, 37, 42, 45, 48, 52], 2005: [2, 6, 13, 21, 27, 33, 36, 40, 44, 46]}),
    dict(kilde=f"{M} 2020 (Rapporter 2020/36), tabell 3.1", fil="monitor_2020_rapp2020-36.pdf", side=19,
         definisjon="forlatt første bostedskommune, omfatter også utvandrede (fotnote 1)",
         kohorter={2007: [2, 6, 11, 17, 23, 28, 33, 36, 40, 43], 2008: [2, 5, 10, 16, 22, 28, 32, 37, 40],
                   2009: [1, 4, 9, 16, 22, 28, 33, 37], 2011: [1, 4, 7, 14, 20, 27], 2013: [1, 3, 8, 15]}),
    dict(kilde="SSB, «Høy bofasthet blant flyktninger de første årene» (28.11.2024), figur 2",
         fil="web/hoy-bofasthet-blant-flyktninger-de-forste-arene.html",
         definisjon="forlatt første bostedskommune (teksten om ukrainere viser at utvandring inngår)",
         kohorter={2010: [1, 3, 8, 16, 22, 30, 35, 40, 44, 47, 50, 53, 55, 57],
                   2012: [1, 2, 6, 13, 18, 25, 31, 36, 40, 44, 48, 50],
                   2014: [1, 3, 7, 13, 19, 28, 35, 39, 44, 47], 2016: [1, 3, 6, 11, 19, 27, 34, 39],
                   2018: [1, 2, 5, 9, 14, 20], 2020: [1, 2, 5, 10], 2022: [2, 8]}),
    dict(kilde="SSB, «Høy innflytting til mange sentrale kommuner» (16.12.2025), figur 1",
         fil="web/hoy-bofasthet-blant-flyktninger-de-forste-arene-copy.html",
         definisjon="flyttet fra første bostedskommune (sekundærflytting; lavere enn 2024-figuren, trolig uten utvandrede)",
         kohorter={2010: [1, 3, 8, 14, 21, 28, 33, 37, 41, 44, 47, 49, 51, 53],
                   2011: [1, 3, 6, 12, 18, 24, 30, 35, 39, 42, 45, 48, 49],
                   2012: [1, 2, 5, 11, 16, 23, 29, 34, 38, 41, 44, 45],
                   2013: [1, 3, 7, 13, 19, 27, 34, 39, 43, 46, 48], 2014: [1, 2, 6, 11, 17, 26, 33, 37, 41, 44],
                   2015: [1, 2, 5, 10, 18, 27, 34, 39, 42], 2016: [1, 2, 5, 11, 17, 26, 32, 37],
                   2017: [1, 3, 6, 11, 18, 25, 31], 2018: [1, 2, 5, 8, 13, 18], 2019: [1, 2, 4, 8, 12]}),
]

# --- Landet: bosted fem år etter, basis i_norge (tabell 4.1 i 2020-rapporten, 1995–2012) ----------
LANDET_5AAR = dict(kilde=f"{M} 2020 (Rapporter 2020/36), tabell 4.1", fil="monitor_2020_rapp2020-36.pdf", side=29,
                   # kohort: (opprinnelig, utvandret/død, i Norge, første kommune, annen kommune i fylket, annet fylke, Oslo)
                   rader={1995: (5583, 387, 5196, 72, 4, 18, 5), 1996: (2505, 234, 2271, 66, 6, 17, 10),
                          1997: (2662, 224, 2438, 67, 4, 16, 13), 1998: (2969, 203, 2766, 64, 4, 15, 16),
                          1999: (6754, 875, 5879, 59, 7, 22, 12), 2000: (6622, 876, 5746, 62, 6, 20, 12),
                          2001: (7073, 450, 6623, 65, 6, 19, 10), 2002: (8246, 374, 7872, 68, 5, 18, 9),
                          2003: (6823, 197, 6626, 71, 7, 14, 9), 2004: (5770, 115, 4062, 72, 6, 13, 9),
                          2005: (4736, 112, 4619, 75, 6, 13, 7), 2006: (5120, 104, 5016, 78, 4, 11, 7),
                          2007: (5052, 157, 4895, 80, 4, 11, 5), 2008: (6015, 200, 5815, 81, 5, 9, 5),
                          2009: (7751, 218, 7533, 80, 5, 10, 5), 2010: (6913, 151, 6762, 79, 5, 10, 6),
                          2011: (6933, 198, 6735, 82, 5, 9, 5), 2012: (7220, 188, 7032, 83, 4, 8, 4)})
LANDET_5AAR_2025 = dict(kilde="SSB (16.12.2025), figur 2", fil="web/hoy-bofasthet-blant-flyktninger-de-forste-arene-copy.html",
                        rader={2010: (79, 6, 9, 6), 2011: (82, 5, 8, 5), 2012: (84, 4, 8, 4), 2013: (81, 5, 9, 5),
                               2014: (83, 6, 8, 4), 2015: (82, 7, 8, 3), 2016: (83, 6, 9, 3), 2017: (82, 6, 10, 2),
                               2018: (87, 4, 7, 2), 2019: (88, 4, 7, 2)})  # første kommune, annen i fylket, annet fylke, Oslo

# --- Landbakgrunn, landet, fem år etter (kohortene 2010–2019, basis opprinnelig) ------------------
LANDBAKGRUNN_5AAR = dict(kilde="SSB (28.11.2024), figur 4", fil="web/hoy-bofasthet-blant-flyktninger-de-forste-arene.html",
                         rader={"Eritrea": (83, 7, 7, 2, 1), "Somalia": (82, 4, 6, 5, 3), "Sudan": (82, 5, 7, 3, 3),
                                "Syria": (82, 5, 9, 2, 2), "Afghanistan": (75, 8, 11, 5, 2)})

# --- Kommunestørrelse, landet, fem år etter (2020-rapporten tabell 4.10, basis opprinnelig) ------
KOMMUNESTORRELSE = dict(kilde=f"{M} 2020, tabell 4.10", fil="monitor_2020_rapp2020-36.pdf", side=46,
                        kohorter=[2012, 2011, 2010, 2009, 2008, 2007],
                        rader={"Hele landet": (82, 81, 79, 79, 80, 78), "100 000+": (92, 90, 91, 91, 89, 90),
                               "50 000–99 999": (87, 85, 85, 85, 84, 80), "30 000–49 999": (89, 84, 86, 83, 85, 86),
                               "20 000–29 999": (82, 83, 82, 83, 77, 76), "15 000–19 999": (82, 78, 82, 81, 78, 73),
                               "10 000–14 999": (77, 76, 69, 76, 78, 76), "5 000–9 999": (72, 73, 69, 70, 68, 68),
                               "2 000–4 999": (73, 69, 64, 59, 70, 59), "Under 2 000": (61, 70, 51, 48, 71, 73)})

# --- Kommuner i Nord-Norge (gammel inndeling) --------------------------------------------------------
# 2017-rapporten vedleggstabell 4.9 (side 92): bosatt år X / fortsatt bosatt X+5 / prosent.
# 2008-kolonnen er forskjøvet i selve PDF-en (f.eks. Askim 566 bosatt) og er IKKE brukt.
KOMMUNE_2009_2010 = dict(kilde=f"{M} 2017, vedleggstabell 4.9", fil="monitor_2017_rapp2017-18.pdf", side=92,
                         rader={"Alta": ((33, 32), (45, 43)), "Bodø": ((85, 53), (126, 102)),
                                "Hammerfest": ((33, 26), (72, 59)), "Harstad": ((76, 66), (103, 86)),
                                "Lenvik": ((27, 11), (38, 20)), "Narvik": ((43, 30), (47, 36)),
                                "Nesna": ((24, 10), (24, 13)), "Rana": ((39, 33), (39, 32)),
                                "Sortland": ((45, 26), (32, 14)), "Tromsø": ((93, 67), (127, 106)),
                                "Vadsø": ((65, 45), (116, 83))})  # (2010-kohort), (2009-kohort)
# 2021-artikkelen figur 5: bosatt 2015 og bosatte fra samme kohort i kommunen 1.1.2020 (netto, inkl. innflyttere)
KOMMUNE_2015_NETTO = dict(kilde="SSB, «Mer bofaste flyktninger» (2021), figur 5", fil="web/mer-bofaste-flyktninger.html",
                          rader={"Tromsø": (200, 211), "Bodø": (141, 150), "Senja": (129, 95), "Vågan": (103, 86),
                                 "Vadsø": (102, 46)})

# --- Fafo-rapport 2025:14 «Flytting etter bosetting» ---------------------------------------------------
FAFO = dict(kilde="Fafo-rapport 2025:14 (Kjeøy mfl.), Flytting etter bosetting", fil="fafo_2025-14_flytting_etter_bosetting.pdf",
            nn_flyttet_10aar=dict(verdi=70, tekst="«nært 70 prosent» av flyktninger bosatt i kommuner i Nord-Norge har flyttet fra bosettingskommunen ti år etter bosetting; Trøndelag «rett under 50 prosent»", side=36),
            tabell3=dict(side=46, tekst="Flyktninger bosatt 2010–2016: første bostedskommune vs. bostedskommune 1.1.2023",
                         rader={"Nord-Norge": (8367, 3746), "Sørlandet": (4638, 3887), "Trøndelag": (5860, 4239),
                                "Vestlandet": (12996, 10522), "Østlandet": (21628, 28591), "I alt": (53489, 50985)}),
            flyttere_fra_nn_til_ostlandet=dict(verdi=64, side=42),
            sju_aar_landet=dict(verdi=35, tekst="35 prosent av dem bosatt 2010–2016 har flyttet innen sju år", side=None))

KBNN = dict(kilde="Kunnskapsbanken for Nord-Norge, «Flyttestrømmene: Innvandrerne forlater Nord-Norge» (2025)",
            fil="web/kbnn_innvandrerne_forlater.html",
            flukt=dict(innvandret=32000, flyttet_sor=27000, tekst="Fra 2000 til 2024 innvandret over 32 000 fra typiske flyktningland (ekskl. Ukraina); over 27 000 har flyttet til Sør-Norge (flyttestrøm, ikke personoppfølging)"),
            schengen=dict(innvandret=29180, fortsatt=20378, tekst="Arbeidsinnvandrere fra Schengen (utenom Norden) siden 2000: 29 180 kom, 20 378 bor fortsatt i Nord-Norge (2025)"))
