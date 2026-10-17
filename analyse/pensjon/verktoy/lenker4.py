"""Fetch a page and print links whose text/href matches a regex. Usage: python -I verktoy/lenker4.py <url> [regex]"""
import sys, re, urllib.request, ssl, html
from urllib.parse import urljoin
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
url = sys.argv[1]
pat = re.compile(sys.argv[2] if len(sys.argv) > 2 else r'regnskap|rsmeld|rsberetn|rsrapport|konomi|budsjett', re.I)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'})
ctx = ssl.create_default_context()
with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
    final = r.geturl()
    s = r.read().decode('utf-8', 'replace')
print('final', final, len(s))
seen = set()
for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', s, re.I | re.S):
    href, text = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2))
    text = ' '.join(html.unescape(text).split())
    full = urljoin(final, html.unescape(href))
    if (pat.search(text) or pat.search(full)) and full not in seen:
        seen.add(full)
        print(text[:90], '|', full)
