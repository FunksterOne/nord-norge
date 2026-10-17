# python -P verktoy3/elements_h.py host tenant handlingId
import json, sys, urllib.request, re
host, tenant, hid = sys.argv[1:4]
def get(path):
    r = urllib.request.Request(f'https://{host}/publikum/api/{path}', headers={'Tenant': tenant, 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(r, timeout=60))
h = get(f'DmbHandlings/{hid}')
m = get(f'Meetings/{h["MeetingId"]}')
s = json.dumps(m)
print('guids', set(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', s)), 'db', m.get('Database'))
re_ = h.get('RegistryEntry') or {}
print('RE', re_.get('Id'))
for d in re_.get('Documents', []):
    dd = d['DocumentDescription']; print(dd['Id'], d['DocumentLinkTypeId'], dd['DocumentTitle'])
