"""Kontroll av temasidene (PLAN-LAYOUT-1-3.md): diagrammer utenfor nummerert figur, gamle klassenavn, hint-avsnitt og skriptfeil.
bruk: python tools/sjekk_layout.py http://localhost:8123/   (eller https://nord-norge.vercel.app/)

Avslutter med kode 0 når alt er i orden, 1 ved avvik og 2 når serveren ikke svarer. En side som ikke lastet (ingen akter
eller ingen figurer), regnes som avvik, slik at kontrollen aldri gir grønt lys for sider den ikke har sett.
"""
import asyncio, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request
import websockets
sys.stdout.reconfigure(encoding="utf-8")

BASE = sys.argv[1]
SIDER = [f'tema-{s}.html' for s in ['flyktning', 'o6', 'kvinneflukt', 'arbeidskraft', 'aldring', 'scenarier', 'bolig', 'naering', 'pensjon', 'ung', 'nordomrade', 'helse']]
# Kjente unntak uten figurnummer (avklart i layoutrunden): sparklinjen i tema 01 og stolpene i regiontabellen i tema 04
UNNTAK = {'tema-flyktning.html': {'#ukrSparkline'}, 'tema-arbeidskraft.html': {'#regionlag'}}
exe = os.path.join(os.environ['LOCALAPPDATA'], 'ms-playwright', 'chromium-1234', 'chrome-win64', 'chrome.exe')
PORT = 9343
JS = r"""(() => {
  const svgs = [...document.querySelectorAll('section.akt svg')].filter(s => s.getBoundingClientRect().width > 120 && s.getBoundingClientRect().height > 60);
  const uten = svgs.filter(s => !s.closest('.nn-fig, .card, .exhibit, .nn-boks')).map(s => { const p = s.closest('[id]'); return p ? '#' + p.id : s.parentElement.className; });
  const figs = [...document.querySelectorAll('.nn-fig')];
  const nummer = figs.map(f => { const h = f.querySelector(':scope > h3, :scope > .nn-fig-h > h3'); return h ? getComputedStyle(h, '::before').content : 'mangler h3'; });
  const legacy = ['hs-boks','ug-boks','graf-kort','fylke-graf','land-graf','arbeid-graf-wrap','duo-graph','trakt-wrap','scatter-wrap','bf-fig','el-fig','hs-tabell','konj-tabell','norden-tabell','hs-merke','ug-merke','np-merke','pj-merke','kildeboks'].filter(c => document.querySelector('.' + c));
  return {akter: document.querySelectorAll('section.akt').length, svg: svgs.length, uten_figur: [...new Set(uten)], figurer: figs.length, siste: nummer.slice(-1)[0],
          uten_nummer: nummer.filter(n => !/Figur/.test(n)).length, legacy, hint: document.querySelectorAll('section.akt p.hint').length, feil: window.__feil || []};
})()"""


def server_svarer():
    try:
        with urllib.request.urlopen(BASE + SIDER[0], timeout=10) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


async def main():
    for _ in range(50):
        try:
            ws_url = next(t['webSocketDebuggerUrl'] for t in json.loads(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json').read()) if t['type'] == 'page'); break
        except Exception: time.sleep(0.2)
    avvik = []
    async with websockets.connect(ws_url, max_size=50_000_000) as ws:
        n = 0
        async def cmd(m, **p):
            nonlocal n; n += 1; i = n
            await ws.send(json.dumps({'id': i, 'method': m, 'params': p}))
            while True:
                r = json.loads(await ws.recv())
                if r.get('id') == i: return r.get('result', {})
        await cmd('Page.enable')
        await cmd('Page.addScriptToEvaluateOnNewDocument', source="window.__feil=[];window.addEventListener('error',e=>window.__feil.push(String(e.message)));")
        for s in SIDER:
            nav = await cmd('Page.navigate', url=BASE + s); await asyncio.sleep(4)
            if nav.get('errorText'):
                avvik.append(f'{s}: lastet ikke ({nav["errorText"]})'); print(f'{s:24} LASTET IKKE: {nav["errorText"]}'); continue
            for y in range(0, 25000, 900):
                await cmd('Runtime.evaluate', expression=f'window.scrollTo(0,{y})'); await asyncio.sleep(0.05)
            await asyncio.sleep(1)
            v = (await cmd('Runtime.evaluate', expression=JS, returnByValue=True))['result']['value']
            print(f"{s:24} akter {v['akter']:2} svg {v['svg']:3} figurer {v['figurer']:3} uten nr {v['uten_nummer']} | uten figur {v['uten_figur']} | gamle {v['legacy']} | hint {v['hint']} | feil {v['feil']}")
            if not v['akter'] or not v['figurer']:
                avvik.append(f"{s}: siden ser ikke ut til å ha lastet ({v['akter']} akter, {v['figurer']} figurer)")
            if v['feil']:
                avvik.append(f"{s}: skriptfeil {v['feil']}")
            if v['uten_nummer']:
                avvik.append(f"{s}: {v['uten_nummer']} figurer uten nummer")
            if v['legacy']:
                avvik.append(f"{s}: gamle klassenavn {v['legacy']}")
            nye = set(v['uten_figur']) - UNNTAK.get(s, set())
            if nye:
                avvik.append(f"{s}: diagram utenfor nummerert figur {sorted(nye)}")
    return avvik


if not server_svarer():
    print(f'FEIL: {BASE} svarer ikke. Start utviklingsserveren (npm run dev) eller kontroller adressen.')
    sys.exit(2)
proc = subprocess.Popen([exe, '--headless=new', '--disable-gpu', f'--remote-debugging-port={PORT}', f'--user-data-dir={tempfile.mkdtemp()}', '--window-size=1280,900', 'about:blank'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    avvik = asyncio.run(main())
finally:
    proc.kill()
if avvik:
    print(f'\n{len(avvik)} avvik:'); [print('  - ' + a) for a in avvik]
    sys.exit(1)
print(f'\nIngen avvik på {len(SIDER)} sider.')
