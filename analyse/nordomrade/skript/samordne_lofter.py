"""Samordnet koding av løfter i sju nordområdedokumenter.

Kode per tiltak (indeks i opprinnelig liste):
  første tegn: K = konkret, V = vagt, - = verken eller, R = rapportert resultat
  valgfri bokstav etter mellomrom: n/e/u = beløpstype nytt/eksisterende/uklart
     (uten bokstav: 'ingen' når belop_mill_kr er null; feil hvis beløp finnes)
  'D<idx>' = dublett av tiltak <idx> (tas ut)
  R kan kombineres med K/V for selve tiltakskarakteren, men R-punkter telles ikke.
"""
import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
NOT = r'C:\Users\HalvardNordang\Github\nord-norge\analyse\nordomrade\notater'

KODER = {
'2006': {
 0:'K',1:'K',2:'K',3:'K',4:'K',5:'K',6:'K',7:'K',8:'K n',9:'K',
 10:'V',11:'K',12:'K n',13:'K e',14:'K n',15:'K',16:'V',17:'K',18:'K n',19:'K',
 20:'K',21:'K',22:'-',23:'K n',24:'K',25:'K',26:'V',27:'K',28:'-',29:'-',
 30:'K',31:'V',32:'V',33:'K e',34:'K',35:'K e',36:'K',37:'K',38:'K',39:'K',
 40:'K',41:'R e',42:'K',43:'K',44:'K',45:'K',46:'V',47:'V',48:'V',49:'V',
 50:'V',51:'K',52:'V',53:'-',54:'V'},
'2009': {
 0:'K',1:'V',2:'V',3:'K',4:'V',5:'K',6:'K e',7:'K',8:'V',9:'V',
 10:'V',11:'K',12:'K',13:'V',14:'K',15:'V',16:'K',17:'K',18:'V',19:'V',
 20:'V',21:'K',22:'V',23:'K',24:'K',25:'K e',26:'V',27:'K',28:'K',29:'K',
 30:'K',31:'K',32:'V',33:'V',34:'V',35:'V',36:'K',37:'K',38:'K',39:'V',
 40:'K',41:'K',42:'K',43:'K e',44:'K',45:'K',46:'K',47:'K e',48:'K',49:'K',
 50:'K',51:'K',52:'K',53:'K',54:'K',55:'K',56:'K',57:'K e',58:'K',59:'K',
 60:'K e',61:'K e',62:'K e'},
'2011': {
 0:'-',1:'K',2:'K',3:'K',4:'K e',5:'V',6:'K',7:'K',8:'K',9:'V',
 10:'K',11:'K',12:'K',13:'K',14:'K',15:'K',16:'K',17:'V',18:'K n',19:'K',
 20:'K',21:'K',22:'K',23:'K',24:'V',25:'K',26:'K',27:'K',28:'K',29:'K',
 30:'V',31:'K',32:'K',33:'K',34:'K',35:'K',36:'V',37:'K',38:'K',39:'K',
 40:'K',41:'K',42:'K',43:'K',44:'V',45:'K',46:'V',47:'K',48:'K',49:'-',
 50:'K',51:'R',52:'V',53:'K',54:'- e',55:'K',56:'V',57:'K',58:'K',59:'K'},
'2014': {
 0:'K n',1:'R',2:'R',3:'V',4:'R',5:'V',6:'K',7:'K',8:'R',9:'V',
 10:'K',11:'V',12:'R',13:'R',14:'R',15:'R e',16:'K',17:'R',18:'K e',19:'-',
 20:'K e',21:'R',22:'R',23:'V',24:'K',25:'K',26:'K',27:'K',28:'K e',29:'K',
 30:'R',31:'R',32:'V',33:'R',34:'K e',35:'-',36:'R',37:'K',38:'K',39:'K',
 40:'R',41:'R',42:'K',43:'-',44:'V',45:'R',46:'-',47:'K',48:'-',49:'-',
 50:'R',51:'K u',52:'R e',53:'R',54:'V',55:'K',56:'K e',57:'K',58:'R',59:'K',
 60:'K',61:'K',62:'R',63:'K',64:'K e',65:'-',66:'K',67:'K',68:'V',69:'K',
 70:'R',71:'R',72:'K',73:'K',74:'K',75:'V',76:'K',77:'K',78:'V',79:'K',
 80:'V',81:'V',82:'V',83:'V',84:'V',85:'K',86:'K',87:'K',88:'-',89:'K',
 90:'K',91:'K'},
'2017': {
 0:'K e',1:'D0',2:'K',3:'K e',4:'K e',5:'K',6:'K',7:'K e',8:'K',9:'K',
 10:'V',11:'K',12:'K',13:'V',14:'K',15:'K',16:'K',17:'K',18:'V',19:'K e',
 20:'K e',21:'K',22:'V',23:'K',24:'V',25:'K',26:'V',27:'K',28:'K',29:'K',
 30:'K',31:'K',32:'K',33:'K',34:'K',35:'K',36:'V',37:'K',38:'-',39:'K',
 40:'K',41:'-',42:'V',43:'-',44:'K',45:'K',46:'K',47:'K',48:'V',49:'V',
 50:'K e',51:'K',52:'K',53:'K',54:'K',55:'K',56:'K',57:'V'},
'2020': {
 0:'K n',1:'K',2:'K',3:'K',4:'K n',5:'V',6:'-',7:'K n',8:'V',9:'K',
 10:'K n',11:'K',12:'K n',13:'K n',14:'K n',15:'K n',16:'K',17:'V',18:'K',19:'K',
 20:'K',21:'V',22:'V',23:'-',24:'K n',25:'K',26:'K',27:'K',28:'K u',29:'K e',
 30:'K e',31:'- e',32:'-',33:'K n',34:'K',35:'- e',36:'-',37:'V',38:'V',39:'K',
 40:'K',41:'K',42:'K e',43:'-',44:'K',45:'V',46:'K',47:'V',48:'K',49:'K n',
 50:'K n',51:'K',52:'K n',53:'K',54:'K',55:'K',56:'K',57:'K',58:'K',59:'V',
 60:'K',61:'K',62:'V',63:'V',64:'K',65:'K',66:'K n',67:'K e',68:'K',69:'K',
 70:'K n',71:'K',72:'K',73:'K',74:'V',75:'K'},
'2025': {
 0:'K e',1:'K u',2:'K',3:'K',4:'K e',5:'D4',6:'K',7:'K',8:'K',9:'K',
 10:'K',11:'V',12:'K',13:'V',14:'K',15:'K',16:'V',17:'K',18:'-',19:'V',
 20:'K',21:'K',22:'K e',23:'R',24:'K',25:'V',26:'K',27:'K',28:'K',29:'R',
 30:'K',31:'K',32:'V',33:'K e',34:'K e',35:'K',36:'-',37:'V',38:'K',39:'K',
 40:'K',41:'K',42:'K',43:'V',44:'K',45:'K',46:'R',47:'K',48:'V',49:'K',
 50:'K',51:'K e',52:'-',53:'R',54:'V',55:'K',56:'V',57:'-'},
}

# Beløp som rettes (mill. kr). Satser per enhet (øre/kWh, kr per barn/lærer) har null her,
# men får beløpstype fordi teksten oppgir et kronebeløp.
BELOP_RETT = {('2011', 52): None, ('2020', 31): 4100}
SATS = {('2006', 35), ('2020', 30), ('2025', 22)}
TYPE = {'n': 'nytt', 'e': 'eksisterende', 'u': 'uklart'}

REGEL = ("Et tiltak er konkret når det har et tall (beløp, antall, prosent) og en frist eller et tidspunkt, "
         "eller når det har en avgrenset leveranse som kan kontrolleres i ettertid (noe opprettes, vedtas, bygges, "
         "legges fram, utredes eller kartlegges). Et tiltak er vagt når det i hovedsak bæres av verb som «vurdere», "
         "«arbeide for», «legge til rette for», «bidra til», «styrke», «videreutvikle», «følge opp», «stimulere», "
         "«prioritere» eller tilsvarende retningsverb («øke», «redusere», «ta stilling til») uten avgrenset leveranse; "
         "videreføring av eksisterende ordninger uten tall og frist er verken konkret eller vagt. Beløp er «nytt» når "
         "dokumentet presenterer det som ny bevilgning eller økning som ikke allerede var vedtatt da dokumentet kom, og "
         "«eksisterende» når det stammer fra NTP, langtidsplan for forsvaret, et allerede vedtatt budsjett, tidligere "
         "vedtak eller beskriver nivået i en eksisterende ordning. Punkter dokumentet rapporterer som allerede gjort, "
         "og dubletter innen samme dokument, telles ikke som løfter.")

ut = {'regel': REGEL, 'dokumenter': {}}
tabell = []
for aar, koder in KODER.items():
    d = json.load(open(f'{NOT}\\{aar}.json', encoding='utf-8'))
    L = d['lofter']
    assert set(koder) == set(range(len(L))), (aar, len(L), sorted(set(range(len(L))) ^ set(koder)))
    lofter, dubletter = [], []
    for i, l in enumerate(L):
        k = koder[i]
        if k.startswith('D'):
            dubletter.append((i, int(k[1:])))
            continue
        deler = k.split()
        hoved = deler[0]
        bel = BELOP_RETT.get((aar, i), l.get('belop_mill_kr'))
        if len(deler) > 1:
            btype = TYPE[deler[1]]
        else:
            assert bel is None and (aar, i) not in SATS, (aar, i, l['tiltak'], bel)
            btype = 'ingen'
        if bel is None and btype != 'ingen':
            assert (aar, i) in SATS or btype in ('eksisterende', 'nytt', 'uklart'), (aar, i)
        lofter.append({
            'tiltak': l['tiltak'], 'tema': l['tema'], 'side': l['side'],
            'konkret': hoved == 'K', 'vagt': hoved == 'V',
            'belop_mill_kr': bel, 'belop_type': btype, 'frist': l.get('frist'),
            'rapportert_resultat': hoved == 'R',
        })
    # sjekk: tiltak med beløp uten type, og gjenstående kr-omtaler uten beløp
    tell = [x for x in lofter if not x['rapportert_resultat']]
    c = collections.Counter
    doc = {
        'n': len(tell),
        'konkret': sum(x['konkret'] for x in tell),
        'vagt': sum(x['vagt'] for x in tell),
        'belop_nytt': sum(x['belop_type'] == 'nytt' for x in tell),
        'belop_eksisterende': sum(x['belop_type'] == 'eksisterende' for x in tell),
        'rapportert': sum(x['rapportert_resultat'] for x in lofter),
        'dubletter_fjernet': len(dubletter),
        'tema': dict(sorted(c(x['tema'] for x in tell).items(), key=lambda kv: (-kv[1], kv[0]))),
        'lofter': lofter,
    }
    ut['dokumenter'][aar] = doc
    tabell.append((aar, len(L), doc['n'], doc['konkret'], doc['vagt'], doc['belop_nytt'],
                   doc['belop_eksisterende'], sum(x['belop_type'] == 'uklart' for x in tell),
                   doc['rapportert'], len(dubletter)))
    for x in tell:
        if x['belop_type'] == 'ingen' and any(s in x['tiltak'] for s in (' kr', 'kroner', 'øre', 'mrd', 'mill')):
            print('KONTROLL kr-omtale uten beløpstype:', aar, x['tiltak'])

json.dump(ut, open(f'{NOT}\\lofter-samordnet.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('år  inn  n  konkret  andel  vagt  nytt  eks  uklart  rapp  dubl')
for r in tabell:
    print(f'{r[0]} {r[1]:4d} {r[2]:3d} {r[3]:6d} {100*r[3]/r[2]:6.1f} {r[4]:5d} {r[5]:5d} {r[6]:4d} {r[7]:6d} {r[8]:5d} {r[9]:5d}')
