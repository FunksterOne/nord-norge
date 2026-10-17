import os, json
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'regnskap_gruppe4.json')
k = [("5544","Nordreisa"),("5546","Kvænangen"),("5601","Alta"),("5603","Hammerfest"),("5605","Sør-Varanger"),("5607","Vadsø"),("5610","Karasjok"),("5612","Kautokeino"),("5614","Loppa"),("5616","Hasvik"),("5618","Måsøy"),("5620","Nordkapp"),("5622","Porsanger"),("5624","Lebesby"),("5626","Gamvik"),("5628","Tana"),("5630","Berlevåg"),("5632","Båtsfjord"),("5634","Vardø"),("5636","Nesseby")]
data = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
have = {d['nr'] for d in data}
for nr, navn in k:
    if nr in have: continue
    data.append({"nr":nr,"navn":navn,"regnskapsaar":None,"kilde_url":None,"kilde_side":None,"konsern_eller_kasse":None,"leverandorer":[],
      "brutto_pensjonsforpliktelse":None,"pensjonsmidler":None,"netto_forpliktelse":None,"netto_inkl_aga":None,"aarets_pensjonskostnad":None,
      "innbetalt_premie":None,"aarets_premieavvik":None,"akkumulert_premieavvik":None,"akkumulert_premieavvik_inkl_aga":None,"amortisering_aar":None,
      "reguleringspremie":None,"egenkapitaltilskudd_klp":None,"premiefond_bruk":None,
      "forutsetninger":{"diskonteringsrente":None,"avkastning":None,"lonnsvekst":None,"g_regulering":None,"pensjonsregulering":None},
      "sykepleiere_separat":None,"merknader":"ikke behandlet ennå"})
data.sort(key=lambda d: d['nr'])
json.dump(data, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(len(data))
