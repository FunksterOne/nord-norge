"""Download a PDF into pdf/<nr>/<name>, then scan it.
Usage: python -P verktoy2/hent.py <nr> <url> <filename>
"""
import sys, os, urllib.request, subprocess

sys.stdout.reconfigure(encoding="utf-8")
nr, url, name = sys.argv[1:4]
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = os.path.join(base, "pdf", nr)
os.makedirs(d, exist_ok=True)
path = os.path.join(d, name)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"})
with urllib.request.urlopen(req, timeout=120) as r:
    data = r.read()
    ct = r.headers.get("Content-Type")
with open(path, "wb") as f:
    f.write(data)
print("saved", path, len(data), "bytes", ct)
if data[:4] != b"%PDF":
    print("NOT A PDF; head:", data[:300])
    sys.exit()
subprocess.run([sys.executable, "-P", os.path.join(base, "verktoy2", "finn.py"), path, "scan"])
