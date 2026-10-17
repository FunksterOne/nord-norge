"""Download a PDF into pdf/<nr>/ and extract text with PyMuPDF.

Usage: python -I verktoy/hent.py <nr> <url> [filename]
Prints page count and pages mentioning pension keywords.
"""
import sys, os, re, urllib.request, ssl
import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    nr, url = sys.argv[1], sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else re.sub(r'[^A-Za-z0-9._-]', '_', url.rstrip('/').split('/')[-1].split('?')[0])[:80]
    if not name.lower().endswith('.pdf'):
        name += '.pdf'
    d = os.path.join(BASE, 'pdf', nr)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
            data = r.read()
        with open(path, 'wb') as f:
            f.write(data)
    with open(path, 'rb') as f:
        head = f.read(5)
    if head != b'%PDF-':
        print('NOT A PDF:', head, os.path.getsize(path))
        return
    doc = fitz.open(path)
    txtpath = path[:-4] + '.txt'
    hits = []
    with open(txtpath, 'w', encoding='utf-8') as out:
        for i, p in enumerate(doc):
            t = p.get_text()
            out.write(f'\n=====PAGE {i+1}=====\n{t}')
            low = t.lower()
            score = sum(low.count(k) for k in ['premieavvik', 'pensjonsforpliktelse', 'pensjonsmidler', 'diskonteringsrente', 'amortiser'])
            if score:
                hits.append((i + 1, score))
    print('file', path, 'pages', len(doc), 'chars', os.path.getsize(txtpath))
    print('first page:', doc[0].get_text()[:300].replace('\n', ' | ') if len(doc) else '')
    print('hits', hits)

main()
