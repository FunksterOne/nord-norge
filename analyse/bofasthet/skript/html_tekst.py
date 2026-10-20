"""Trekk ut lesbar tekst, tabeller og lenker fra nedlastede SSB/IMDi-HTML-sider.

Bruk: python html_tekst.py fil.html [--lenker]
"""
import re, sys, html
from html.parser import HTMLParser


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip, self.links = [], 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in ("p", "br", "h1", "h2", "h3", "h4", "li", "tr", "div", "table"):
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")
        if tag == "a":
            h = dict(attrs).get("href")
            if h:
                self.links.append(h)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


f = sys.argv[1]
p = P()
p.feed(open(f, encoding="utf-8", errors="replace").read())
txt = html.unescape("".join(p.out))
txt = re.sub(r"[ \t\r\f\v]+", " ", txt)
txt = re.sub(r"\n\s*\n+", "\n", txt)
print(txt)
if "--lenker" in sys.argv:
    print("\n=== LENKER ===")
    for l in sorted(set(p.links)):
        print(l)
