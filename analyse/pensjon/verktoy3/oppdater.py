# usage: python -I verktoy3/oppdater.py patch.json   (patch = object with nr + fields)
import json, sys
out = 'regnskap_gruppe3.json'
lst = json.load(open(out, encoding='utf-8'))
p = json.load(open(sys.argv[1], encoding='utf-8'))
for o in lst:
    if o['nr'] == p['nr']:
        for k, v in p.items():
            if k == 'forutsetninger':
                o['forutsetninger'].update(v)
            else:
                o[k] = v
        print('oppdatert', o['nr'], o['navn'])
json.dump(lst, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
