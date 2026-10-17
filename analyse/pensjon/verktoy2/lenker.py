"""Fetch a web page and list links (href + text) matching a regex.
Usage: python -P verktoy2/lenker.py <url> [regex]
"""
import sys, re, urllib.request, html
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding="utf-8")
url = sys.argv[1]
rx = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"regnskap|årsmeld|arsmeld|beretning|pdf", re.I)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"})
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        final = r.geturl()
        body = r.read().decode("utf-8", "replace")
except Exception as e:
    print("ERR", e)
    sys.exit()
print("# final:", final, "len", len(body))
seen = set()
for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', body, re.I | re.S):
    href, txt = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
    txt = html.unescape(" ".join(txt.split()))
    full = urljoin(final, html.unescape(href))
    if (rx.search(full) or rx.search(txt)) and full not in seen:
        seen.add(full)
        print(txt[:90], "->", full)
