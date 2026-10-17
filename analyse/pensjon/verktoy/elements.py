"""Elements Publikum helper.
List:     python -E -P verktoy/elements.py list <host> <tenant> [query]
Download: python -E -P verktoy/elements.py get <host> <tenant> <db> <regentry> <docid> <nr> <filename>
host e.g. prod01.elementscloud.no
"""
import sys, json, urllib.request, urllib.parse, ssl, os

def req(url, tenant):
    r = urllib.request.Request(url, headers={'Tenant': tenant, 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(r, timeout=120, context=ssl.create_default_context()) as f:
        return f.read()

mode, host, tenant = sys.argv[1:4]
api = f'https://{host}/publikum/api'
if mode == 'list':
    q = sys.argv[4] if len(sys.argv) > 4 else 'årsregnskap'
    d = json.loads(req(f'{api}/DmbSearch/MeetingsSearch?Query={urllib.parse.quote(q)}', tenant))
    hs = []
    for m in d.get('Meetings', []):
        for h in m.get('DmbHandlings') or []:
            hs.append((m['StartDate'][:10], m['DMB']['Name'] if m.get('DMB') else '', h['Id'], h['Title']))
    hs.sort(reverse=True)
    for x in hs[:25]:
        print(*x)
    # details for top handlings that look like 2025/2024 accounts
    shown = 0
    for date, board, hid, title in hs:
        t = title.lower()
        if ('regnskap' in t or 'årsmelding' in t or 'årsrapport' in t or 'årsberetning' in t) and ('2025' in t or '2024' in t or date >= '2026-01') and shown < 4:
            shown += 1
            h = json.loads(req(f'{api}/DmbHandlings/{hid}', tenant))
            re_ = h.get('RegistryEntry') or {}
            print(f'--- handling {hid} {title} | db={re_.get("Database")} regentry={re_.get("Id")}')
            for doc in re_.get('Documents') or []:
                dd = doc['DocumentDescription']
                print('    doc', dd['Id'], dd['DocumentTitle'], dd.get('IsPublished'))
elif mode == 'h':
    for hid in sys.argv[4:]:
        h = json.loads(req(f'{api}/DmbHandlings/{hid}', tenant))
        re_ = h.get('RegistryEntry') or {}
        print(f'--- handling {hid} {h.get("Title")} | db={re_.get("Database")} regentry={re_.get("Id")}')
        for doc in re_.get('Documents') or []:
            dd = doc['DocumentDescription']
            print('    doc', dd['Id'], dd['DocumentTitle'], dd.get('IsPublished'))
else:
    db, reg, docid, nr, fn = sys.argv[4:9]
    data = req(f'https://{host}/publikum/Documents/ShowDocument/{db}/{reg}/{docid}', tenant)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(base, 'pdf', nr)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, fn)
    open(p, 'wb').write(data)
    print('saved', p, len(data), data[:5])
