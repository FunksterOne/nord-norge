"""Find årsregnskap documents in Elements Publikum. Usage: python -P verktoy/elements4.py <orgnr> [year] [regex]"""
import sys, json, re, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
org = sys.argv[1]; year = sys.argv[2] if len(sys.argv) > 2 else '2026'
pat = re.compile(sys.argv[3] if len(sys.argv) > 3 else r'regnskap|årsberetning|årsmelding', re.I)
B = 'https://prod01.elementscloud.no/publikum/'
def get(p):
    req = urllib.request.Request(B + p, headers={'User-Agent': 'Mozilla/5.0', 'tenant': org, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8-sig'))
ms = get(f'api/PredefinedQuery/DmbMeetings?year={year}')
for m in sorted(ms, key=lambda m: m['MO_START']):
    if not re.search(r'kommunestyre|kontrollutvalg|formannskap', m['UT_NAVN'], re.I):
        continue
    try:
        hs = get(f"api/DmbHandlings/GetByMeetingId/{m['MO_ID']}")
    except Exception as e:
        print('ERR', m['MO_ID'], e); continue
    for h in hs:
        if pat.search(h['Title'] or ''):
            print(f"\n{m['MO_START'][:10]} {m['UT_NAVN']} mote {m['MO_ID']} sak {h['Id']}: {h['Title']}")
            try:
                d = get(f"api/DmbHandlings/{h['Id']}")
            except Exception as e:
                print('  ERR', e); continue
            re_ = d.get('RegistryEntry')
            if not re_:
                continue
            for doc in re_.get('Documents', []):
                dd = doc['DocumentDescription']
                print(f"  {dd['DocumentTitle']} | pub={dd['IsPublished']} | {B}Documents/ShowDocument/{re_['Database']}/{re_['Id']}/{dd['Id']}")
