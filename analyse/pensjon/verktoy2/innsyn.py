"""ACOS innsyn: list meetings for an utvalg and documents matching a regex.
Usage: python -P verktoy2/innsyn.py <moteplan_utvalg-url> [regex] [maxmeetings]
"""
import sys, re, urllib.request, html
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def links(base, body):
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', body, re.I | re.S):
        txt = html.unescape(" ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split()))
        yield txt, urljoin(base, html.unescape(m.group(1)))


url = sys.argv[1]
rx = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"regnskap|årsmeld|årsberetning|årsrapport", re.I)
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 12
final, body = get(url)
meetings = []
for txt, href in links(final, body):
    if "response=mote&" in href and href not in [m[1] for m in meetings]:
        meetings.append((txt, href))
print(f"# {len(meetings)} meetings")
for txt, href in meetings[:mx]:
    try:
        f2, b2 = get(href)
    except Exception as e:
        print("ERR", txt, e)
        continue
    hits = [(t, h) for t, h in links(f2, b2) if rx.search(t)]
    print(f"== {txt}  {href}")
    seen = set()
    for t, h in hits:
        if h in seen:
            continue
        seen.add(h)
        print("   ", t[:110], "->", h)
