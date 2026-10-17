"""KOSTRA-balansens pensjonsposter (SSB 13202, kommunekonsern) og BDI (SSB 12143) for de 80 kommunene,
fylkene og landet, 2020–2025. Skriver kostra_pensjon.json i samme mappe."""
import json, os, urllib.request

HER = os.path.dirname(os.path.abspath(__file__))
grupper = json.load(open(os.path.join(HER, 'kommuner.json'), encoding='utf-8'))
KOMM = [k['nr'] for g in grupper for k in g]
REG = KOMM + ['EAK', 'EAKUO', 'EKA18', 'EKA55', 'EKA56']
AAR = ['2020', '2021', '2022', '2023', '2024', '2025']
BAL = {'KG50': 'pensjonsmidler', 'KG82': 'pensjonsforpliktelse', 'KG61': 'premieavvik_eiendel',
       'KG89': 'premieavvik_gjeld', 'KG62': 'sum_eiendeler', 'KG64': 'egenkapital_drift'}


def post(tabell, query):
    req = urllib.request.Request(f'https://data.ssb.no/api/v0/no/table/{tabell}',
                                 data=json.dumps({'query': query, 'response': {'format': 'json-stat2'}}).encode(),
                                 headers={'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    ids, size = d['id'], d['size']
    cats = {k: list(d['dimension'][k]['category']['index']) for k in ids}
    for i, v in enumerate(d['value']):
        r, co = i, {}
        for j in range(len(ids) - 1, -1, -1):
            co[ids[j]] = cats[ids[j]][r % size[j]]; r //= size[j]
        yield co, v


ut = {}
for start in range(0, len(REG), 40):
    bit = REG[start:start + 40]
    for co, v in post('13202', [
            {'code': 'KOKkommuneregion0000', 'selection': {'filter': 'item', 'values': bit}},
            {'code': 'KOKkapittel0000', 'selection': {'filter': 'item', 'values': list(BAL)}},
            {'code': 'ContentsCode', 'selection': {'filter': 'item', 'values': ['KOSbelop0000']}},
            {'code': 'Tid', 'selection': {'filter': 'item', 'values': AAR}}]):
        ut.setdefault(co['KOKkommuneregion0000'], {}).setdefault(co['Tid'], {})[BAL[co['KOKkapittel0000']]] = v
    # BDI fra 12143: langsiktig gjeld i kroner og i prosent av BDI
    kr = {}; pct = {}
    for cc, mål in (('KOSbelop0000', kr), ('KOSbelopbrinv0000', pct)):
        for co, v in post('12143', [
                {'code': 'KOKkommuneregion0000', 'selection': {'filter': 'item', 'values': bit}},
                {'code': 'KOKartkap0000', 'selection': {'filter': 'item', 'values': ['KG25']}},
                {'code': 'ContentsCode', 'selection': {'filter': 'item', 'values': [cc]}},
                {'code': 'Tid', 'selection': {'filter': 'item', 'values': AAR}}]):
            mål[(co['KOKkommuneregion0000'], co['Tid'])] = v
    for (r, t), v in kr.items():
        p = pct.get((r, t))
        if v and p:
            ut.setdefault(r, {}).setdefault(t, {})['bdi'] = round(v / (p / 100))
    print('hentet', start + len(bit), 'av', len(REG), flush=True)

json.dump(ut, open(os.path.join(HER, 'kostra_pensjon.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('lagret kostra_pensjon.json')
