"""Search a PDF for pension-related pages and print them.
Usage: python -P verktoy2/finn.py <pdf> [mode]
 mode: 'scan' (list pages with hits, default) | 'pages:12,13' (print full text of pages, 1-based)
       | 'grep:regex' (print lines matching with context)
"""
import sys, re
import fitz

pdf = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "scan"
doc = fitz.open(pdf)
sys.stdout.reconfigure(encoding="utf-8")
print(f"# {pdf}: {doc.page_count} pages")
texts = [p.get_text() for p in doc]
tot = sum(len(t) for t in texts)
print(f"# total chars {tot}")
if mode == "scan":
    kw = re.compile(r"(pensjonsforpliktelse|premieavvik|pensjonsmidler|diskonteringsrente|pensjonskostnad)", re.I)
    for i, t in enumerate(texts):
        hits = kw.findall(t)
        if hits:
            first = t.strip().splitlines()[:2]
            print(i + 1, len(hits), sorted(set(h.lower() for h in hits)), "|", " / ".join(first)[:100])
elif mode.startswith("pages:"):
    for s in mode[6:].split(","):
        if "-" in s:
            a, b = map(int, s.split("-"))
            rng = range(a, b + 1)
        else:
            rng = [int(s)]
        for n in rng:
            print(f"\n======== PAGE {n} ========")
            print(texts[n - 1])
elif mode.startswith("grep:"):
    rx = re.compile(mode[5:], re.I)
    for i, t in enumerate(texts):
        lines = t.splitlines()
        for j, l in enumerate(lines):
            if rx.search(l):
                ctx = " | ".join(lines[j:j + 4])
                print(f"p{i+1}: {ctx[:250]}")
