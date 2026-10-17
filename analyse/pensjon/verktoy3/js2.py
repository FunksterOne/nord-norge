import json, itertools, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
ids = d['id']
cats = []
for i in ids:
    idx = d['dimension'][i]['category']['index']
    cats.append(sorted(idx, key=lambda k: idx[k]) if isinstance(idx, dict) else idx)
for n, combo in enumerate(itertools.product(*cats)):
    print(combo, d['value'][n])
