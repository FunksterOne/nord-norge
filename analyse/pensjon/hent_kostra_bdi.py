"""BDI og sammensetningen av driftsinntektene (SSB 13551), samt BDI, frie inntekter og disposisjonsfond (SSB 12364),
kommunekonsern, 2020–2025, for de 80 kommunene, fylkene og landet. Skriver kostra_bdi.json (verdier i 1000 kr)."""
import json, os, urllib.request

HER = os.path.dirname(os.path.abspath(__file__))
grupper = json.load(open(os.path.join(HER, 'kommuner.json'), encoding='utf-8'))
REG = [k['nr'] for g in grupper for k in g] + ['EAK', 'EAKUO', 'EKA18', 'EKA55', 'EKA56']
AAR = ['2020', '2021', '2022', '2023', '2024', '2025']
A13551 = {'A800': 'rammetilskudd', 'AGD75': 'skatt_inntekt_formue', 'AG10': 'eiendomsskatt', 'AGD76': 'andre_skatter',
          'AGD77': 'andre_statlige_overforinger', 'AGD78': 'overforinger_fra_andre', 'A600': 'brukerbetalinger',
          'AGD96': 'salgs_og_leieinntekter', 'AGD45': 'sum_driftsinntekter', 'AG15': 'lonn', 'AG35': 'sosiale_utgifter'}
A12364 = {'AGD13': 'bdi', 'AG11': 'frie_inntekter', '56': 'disposisjonsfond', 'KG21': 'fri_egenkapital_drift'}


def post(tabell, query):
    req = urllib.request.Request(f'https://data.ssb.no/api/v0/no/table/{tabell}',
                                 data=json.dumps({'query': query, 'response': {'format': 'json-stat2'}}).encode(),
                                 headers={'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    ids, size = d['id'], d['size']
    cats = {k: list(d['dimension'][k]['category']['index']) for k in ids}
    for i, v in enumerate(d['value']):
        r, co = i, {}
        for j in range(len(ids) - 1, -1, -1):
            co[ids[j]] = cats[ids[j]][r % size[j]]; r //= size[j]
        yield co, v


ut = {}
for start in range(0, len(REG), 20):
    bit = REG[start:start + 20]
    for tabell, artkode, navn in (('13551', 'KOKart0000', A13551), ('12364', 'KOKartkap0000', A12364)):
        for co, v in post(tabell, [
                {'code': 'KOKkommuneregion0000', 'selection': {'filter': 'item', 'values': bit}},
                {'code': artkode, 'selection': {'filter': 'item', 'values': list(navn)}},
                {'code': 'ContentsCode', 'selection': {'filter': 'item', 'values': ['KOSbelop0000']}},
                {'code': 'Tid', 'selection': {'filter': 'item', 'values': AAR}}]):
            ut.setdefault(co['KOKkommuneregion0000'], {}).setdefault(co['Tid'], {})[navn[co[artkode]]] = v
    print('hentet', start + len(bit), 'av', len(REG), flush=True)
json.dump(ut, open(os.path.join(HER, 'kostra_bdi.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('lagret kostra_bdi.json')
