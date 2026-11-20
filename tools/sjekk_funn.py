#!/usr/bin/env python3
"""Kontrollerer at hvert tall i hovedfunnene (aside.nn-funn) står i teksten til akten funnet lenker til.

Kjøres etter hver dataoppdatering: et funn som ikke lenger stemmer med siden, skrives ut som AVVIK.
Kode 0 = ingen avvik, 1 = avvik (også en side uten funnboks), 2 = serveren svarer ikke.
Bruk: python tools/sjekk_funn.py http://localhost:8123/   (eller https://nord-norge.vercel.app/)
"""
import asyncio, json, os, re, subprocess, sys, tempfile, time, urllib.request
import websockets
sys.stdout.reconfigure(encoding="utf-8")

BASE = sys.argv[1]
SIDER = [f"tema-{s}.html" for s in ["flyktning", "o6", "kvinneflukt", "arbeidskraft", "aldring", "scenarier", "bolig", "naering",
                                     "pensjon", "ung", "nordomrade", "helse"]]
exe = os.path.join(os.environ["LOCALAPPDATA"], "ms-playwright", "chromium-1234", "chrome-win64", "chrome.exe")
PORT = 9345
JS = r"""(() => {
  const norm = s => s.replace(/[   ]/g, ' ').replace(/\s+/g, ' ');
  const akter = [...document.querySelectorAll('section.akt')];
  return [...document.querySelectorAll('.nn-funn li')].map(li => {
    const a = li.querySelector('a[data-akt]'); const n = Number(a.dataset.akt);
    const tekst = norm(li.innerText.replace(a.innerText, ''));
    const akt = akter[n - 1];
    return {tekst, n, akt: akt ? norm(akt.textContent) : ''};   // textContent: også tekst i lukkede «Les mer»-bokser
  });
})()"""
TALL = re.compile(r"(?<![\d,])\d{1,3}(?: \d{3})+(?:,\d+)?|\d+(?:,\d+)?")
IGNORER = {"2000", "2006", "2008", "2015", "2019", "2021", "2022", "2025", "2026", "2027", "2030", "2031", "2035", "2040",
           "2042", "2045", "2050", "18", "44", "24", "15", "34", "64", "67", "20", "80", "100", "10"}


def server_svarer():
    try:
        with urllib.request.urlopen(BASE + SIDER[0], timeout=10) as r:
            return r.status == 200
    except OSError:
        return False


async def main():
    proc = subprocess.Popen([exe, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}", f"--user-data-dir={tempfile.mkdtemp()}",
                             "--window-size=1280,900", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            ws_url = next(t["webSocketDebuggerUrl"] for t in json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read()) if t["type"] == "page")
            break
        except Exception:
            time.sleep(0.2)
    avvik = 0
    async with websockets.connect(ws_url, max_size=50_000_000) as ws:
        n = 0
        async def cmd(m, **p):
            nonlocal n
            n += 1; i = n
            await ws.send(json.dumps({"id": i, "method": m, "params": p}))
            while True:
                r = json.loads(await ws.recv())
                if r.get("id") == i:
                    return r.get("result", {})
        for s in SIDER:
            await cmd("Page.navigate", url=BASE + s); await asyncio.sleep(4)
            for y in range(0, 25000, 1500):
                await cmd("Runtime.evaluate", expression=f"window.scrollTo(0,{y})"); await asyncio.sleep(0.05)
            await asyncio.sleep(1)
            funn = (await cmd("Runtime.evaluate", expression=JS, returnByValue=True))["result"]["value"]
            for f in funn:
                mangler = [t for t in TALL.findall(f["tekst"]) if t not in IGNORER and t not in f["akt"]]
                if not f["akt"]:
                    mangler = ["(akten finnes ikke)"]
                if mangler:
                    avvik += 1
                    print(f"AVVIK {s} akt {f['n']}: {mangler} — «{f['tekst'][:90]}»")
            if not funn:   # ingen funnboks betyr at siden ikke lastet, ikke at alt stemmer
                avvik += 1
                print(f"AVVIK {s}: fant ingen hovedfunn — lastet siden?")
            print(f"{s:24} {len(funn)} funn kontrollert")
    proc.kill()
    print("Ingen avvik." if not avvik else f"{avvik} funn med tall som ikke står i akten.")
    sys.exit(1 if avvik else 0)


if not server_svarer():
    print(f"FEIL: {BASE} svarer ikke. Start utviklingsserveren (npm run dev) eller kontroller adressen.")
    sys.exit(2)
asyncio.run(main())
