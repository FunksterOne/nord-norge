"""Pensjonsinnskudd (art 090), arbeidsgiveravgift (099) og lønn (AG16) summert over tjenesteområdene (FGK-gruppene)
fra SSB 12367, kommunekonsern, 2020–2025. Skriver kostra_drift.json."""
import json, os, urllib.request

HER = os.path.dirname(os.path.abspath(__file__))
grupper = json.load(open(os.path.join(HER, 'kommuner.json'), encoding='utf-8'))
REG = [k['nr'] for g in grupper for k in g] + ['EAK', 'EAKUO', 'EKA18', 'EKA55', 'EKA56']
AAR = ['2020', '2021', '2022', '2023', '2024', '2025']
meta = json.load(urllib.request.urlopen('https://data.ssb.no/api/v0/no/table/12367', timeout=60))
FUNK = [c for c in next(v for v in meta['variables'] if v['code'] == 'KOKfunksjon0000')['values'] if c.startswith('FGK')]
ART = {'A090': 'pensjon', 'A099': 'aga', 'AG16': 'lonn'}


def post(query):
    req = urllib.request.Request('https://data.ssb.no/api/v0/no/table/12367',
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
    for co, v in post([
            {'code': 'KOKkommuneregion0000', 'selection': {'filter': 'item', 'values': bit}},
            {'code': 'KOKregnskapsomfa0000', 'selection': {'filter': 'item', 'values': ['A']}},
            {'code': 'KOKfunksjon0000', 'selection': {'filter': 'item', 'values': FUNK}},
            {'code': 'KOKart0000', 'selection': {'filter': 'item', 'values': list(ART)}},
            {'code': 'ContentsCode', 'selection': {'filter': 'item', 'values': ['KOSbelop0000']}},
            {'code': 'Tid', 'selection': {'filter': 'item', 'values': AAR}}]):
        if v is None: continue
        rec = ut.setdefault(co['KOKkommuneregion0000'], {}).setdefault(co['Tid'], {})
        k = ART[co['KOKart0000']]
        rec[k] = rec.get(k, 0) + v
    print('hentet', start + len(bit), 'av', len(REG), flush=True)
json.dump({'funksjonsgrupper': FUNK, 'data': ut}, open(os.path.join(HER, 'kostra_drift.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('lagret kostra_drift.json')
