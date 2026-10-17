"""Scan a municipality website for årsregnskap PDF links.
Usage: python -E -P verktoy/skann.py <base_url> [extra page urls...]
"""
import sys, re, urllib.request, ssl, html
from urllib.parse import urljoin

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'}

def get(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as r:
            return r.read().decode('utf-8', 'replace'), r.geturl()
    except Exception as e:
        return '', url

base = sys.argv[1].rstrip('/')
pages = list(sys.argv[2:])
sm, _ = get(base + '/sitemap.xml')
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
# nested sitemaps
for l in list(locs):
    if l.endswith('.xml'):
        s2, _ = get(l)
        locs += re.findall(r'<loc>([^<]+)</loc>', s2)
kw = re.compile(r'regnskap|arsrapport|arsmelding|arsberetning|aarsrapport|budsjett-og-regnskap|okonomi', re.I)
cand = [l for l in locs if kw.search(l) and 'sosial' not in l and 'radgivning' not in l]
print('sitemap urls', len(locs), 'candidates', len(cand))
for c in cand[:30]:
    print('  cand', c)
pages += cand[:30]
seen = set()
for p in pages:
    h, final = get(p)
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', h, re.S | re.I):
        href, text = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2))
        text = html.unescape(' '.join(text.split()))
        if re.search(r'regnskap|rsmelding|rsberetning|rsrapport|framsikt', href + ' ' + text, re.I):
            u = urljoin(final, html.unescape(href))
            if u not in seen and not re.search(r"sharer|twitter|linkedin|mailto", u):
                seen.add(u)
                print(text[:80], '->', u)
