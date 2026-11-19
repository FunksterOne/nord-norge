"""Kontroll av temasidene (PLAN-LAYOUT-1-3.md): diagrammer utenfor nummerert figur, gamle klassenavn, hint-avsnitt og skriptfeil.
bruk: python tools/sjekk_layout.py http://localhost:8123/   (eller https://nord-norge.vercel.app/)"""
import asyncio, json, os, subprocess, sys, tempfile, time, urllib.request
import websockets
BASE = sys.argv[1]
SIDER = [f'tema-{s}.html' for s in ['flyktning', 'o6', 'kvinneflukt', 'arbeidskraft', 'aldring', 'scenarier', 'bolig', 'naering', 'pensjon', 'ung', 'nordomrade', 'helse']]
exe = os.path.join(os.environ['LOCALAPPDATA'], 'ms-playwright', 'chromium-1234', 'chrome-win64', 'chrome.exe')
PORT = 9343
proc = subprocess.Popen([exe, '--headless=new', '--disable-gpu', f'--remote-debugging-port={PORT}', f'--user-data-dir={tempfile.mkdtemp()}', '--window-size=1280,900', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
JS = r"""(() => {
  const svgs = [...document.querySelectorAll('section.akt svg')].filter(s => s.getBoundingClientRect().width > 120 && s.getBoundingClientRect().height > 60);
  const uten = svgs.filter(s => !s.closest('.nn-fig, .card, .exhibit, .nn-boks')).map(s => { const p = s.closest('[id]'); return p ? '#' + p.id : s.parentElement.className; });
  const figs = [...document.querySelectorAll('.nn-fig')];
  const nummer = figs.map(f => { const h = f.querySelector(':scope > h3, :scope > .nn-fig-h > h3'); return h ? getComputedStyle(h, '::before').content : 'mangler h3'; });
  const legacy = ['hs-boks','ug-boks','graf-kort','fylke-graf','land-graf','arbeid-graf-wrap','duo-graph','trakt-wrap','scatter-wrap','bf-fig','el-fig','hs-tabell','konj-tabell','norden-tabell','hs-merke','ug-merke','np-merke','pj-merke','kildeboks'].filter(c => document.querySelector('.' + c));
  return {svg: svgs.length, uten_figur: [...new Set(uten)], figurer: figs.length, siste: nummer.slice(-1)[0], uten_nummer: nummer.filter(n => !/Figur/.test(n)).length, legacy, hint: document.querySelectorAll('section.akt p.hint').length, feil: window.__feil || []};
})()"""
async def main():
    for _ in range(50):
        try:
            ws_url = next(t['webSocketDebuggerUrl'] for t in json.loads(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json').read()) if t['type'] == 'page'); break
        except Exception: time.sleep(0.2)
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
            await cmd('Page.navigate', url=BASE + s); await asyncio.sleep(4)
            for y in range(0, 25000, 900):
                await cmd('Runtime.evaluate', expression=f'window.scrollTo(0,{y})'); await asyncio.sleep(0.05)
            await asyncio.sleep(1)
            v = (await cmd('Runtime.evaluate', expression=JS, returnByValue=True))['result']['value']
            print(f"{s:24} svg {v['svg']:3} figurer {v['figurer']:3} siste {v.get('siste')} uten nr {v['uten_nummer']} | uten figur {v['uten_figur']} | gamle {v['legacy']} | hint {v['hint']} | feil {v['feil']}")
asyncio.run(main()); proc.kill()
