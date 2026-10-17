import json, sys, urllib.request, urllib.parse
q = sys.argv[1]; extra = dict(a.split('=',1) for a in sys.argv[2:])
p = {'query': q, 'limit': 25}; p.update(extra)
u = 'https://api.einnsyn.no/search?' + urllib.parse.urlencode(p)
d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}), timeout=60))
for i in d.get('items', []):
    t = i.get('offentligTittel') or i.get('tittel') or i.get('offentligTittelSensitiv') or ''
    print(i['entity'], i['id'], i.get('journalenhet','')[:30], (i.get('moetedato') or i.get('journaldato') or ''), t[:100])
