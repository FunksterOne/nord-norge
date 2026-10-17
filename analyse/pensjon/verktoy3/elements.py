# python -P verktoy3/elements.py host tenant query
import json, sys, urllib.request, urllib.parse
host, tenant, q = sys.argv[1], sys.argv[2], sys.argv[3]
def get(path):
    r = urllib.request.Request(f'https://{host}/publikum/api/{path}', headers={'Tenant': tenant, 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(r, timeout=60))
res = get('DmbSearch/MeetingsSearch?' + urllib.parse.urlencode({'Query': q, 'OrderBy': 'DATE', 'SortOrder': 1, 'filters': 'case,handling,handlingdesc,decision'}))
for m in res.get('Meetings', [])[:12]:
    for h in m.get('DmbHandlings', []):
        print(m['StartDate'][:10], m['DMB']['Name'], '| handling', h['Id'], h['Title'], '| db', h.get('Database') or m.get('Database'))
