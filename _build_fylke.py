#!/usr/bin/env python3
"""Build fylke.html (template, ?f=Nordland|Troms|Finnmark)."""
import io
import re

with io.open('index.html', 'r', encoding='utf-8') as fh:
    lines = fh.readlines()

# Use same sections as nord-norge but with fylke-filtering
keep = ['intro', 'model', 'nat', 'levekar', 'refugees', 'robek']
sections = {}
for i, ln in enumerate(lines):
    if '<section class="tab' in ln:
        m = re.search(r'data-tab="([^"]+)"', ln)
        if m:
            sections[m.group(1)] = {'start': i}
for name, b in sections.items():
    depth = 1
    for j in range(b['start']+1, len(lines)):
        if '<section' in lines[j]:
            depth += 1
        if '</section>' in lines[j]:
            depth -= 1
            if depth == 0:
                b['end'] = j
                break

content_parts = []
for name in keep:
    b = sections[name]
    chunk = ''.join(lines[b['start']:b['end']+1])
    chunk = chunk.replace(' class="tab active"', ' class="tab"')
    content_parts.append(chunk)
content = '\n'.join(content_parts)
content_active = content.replace('class="tab" data-tab="intro"', 'class="tab active" data-tab="intro"', 1)

PAGE_HEAD = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fylke - Nord-Norge dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,800&family=Hanken+Grotesk:wght@400;500;600;700&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/styles.css">
<style>
.nn-top{display:flex;align-items:center;gap:16px;padding:14px 0 18px;border-bottom:1px solid var(--line2);margin-bottom:24px;flex-wrap:wrap}
.nn-bc{font-size:13px;color:var(--ink2);font-family:'Hanken Grotesk',sans-serif}
.nn-bc a{color:var(--ink2);text-decoration:none;border-bottom:1px solid var(--line2);padding-bottom:1px}
.nn-bc a:hover{color:var(--ink);border-color:var(--ink2)}
.nn-bc .sep{margin:0 6px;color:var(--ink3)}
.nn-bc .now{color:var(--ink);font-weight:600}
.nn-actions{margin-left:auto;display:flex;gap:10px;align-items:center}
.nn-actions select,.nn-actions input{font-family:inherit;font-size:13px;padding:6px 10px;border:1px solid var(--line2);border-radius:6px;background:var(--paper);color:var(--ink)}
.nn-actions a.btn{padding:6px 12px;font-size:13px;text-decoration:none;color:var(--ink);border:1px solid var(--line2);border-radius:6px}
.nn-actions a.btn:hover{background:var(--paper2)}
.nn-secnav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;padding-bottom:14px;border-bottom:1px solid var(--line2)}
.nn-secnav button{font-family:inherit;font-size:12.5px;padding:6px 12px;border:1px solid var(--line2);border-radius:999px;background:var(--paper);color:var(--ink2);cursor:pointer}
.nn-secnav button[aria-current="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.nn-secnav button:hover:not([aria-current="true"]){border-color:var(--ink2);color:var(--ink)}
.tab{display:none}
.tab.active{display:block}
.fylke-kommuneliste{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin-top:14px}
.fylke-kommuneliste a{display:flex;justify-content:space-between;align-items:baseline;padding:8px 12px;border:1px solid var(--line2);border-radius:6px;text-decoration:none;color:var(--ink);font-size:13px}
.fylke-kommuneliste a:hover{border-color:var(--ink2);background:var(--paper2)}
.fylke-kommuneliste .pop{color:var(--ink3);font-size:11.5px;font-family:'Spline Sans Mono',monospace}
</style>
</head>
<body>
<div class="wrap">

<header class="nn-top">
  <nav class="nn-bc" aria-label="Brodsmuler">
    <a href="index.html">Hjem</a>
    <span class="sep">&rsaquo;</span>
    <a href="nord-norge.html">Nord-Norge</a>
    <span class="sep">&rsaquo;</span>
    <span class="now" id="bcFylke">Fylke</span>
  </nav>
  <div class="nn-actions">
    <select id="fylkePicker" aria-label="Bytt fylke">
      <option value="">Bytt fylke&hellip;</option>
      <option value="Nordland">Nordland</option>
      <option value="Troms">Troms</option>
      <option value="Finnmark">Finnmark</option>
    </select>
    <select id="kommunePicker" aria-label="Velg kommune"></select>
    <a class="btn" href="metode.html">Metode</a>
  </div>
</header>

<div style="margin-bottom:20px">
  <div class="kicker" id="fkicker">Fylkesoversikt &middot; SSB &middot; Folketall 1.1.2026</div>
  <h1 class="serif" style="margin:6px 0 12px" id="ftitle">Fylke</h1>
  <p class="essence" id="fessence">Velg seksjon nedenfor for � se hvordan dette fylket utvikler seg mot 2050.</p>
</div>

<nav class="nn-secnav" id="secnav">
  <button data-sec="intro" aria-current="true">1.1 Det store bildet</button>
  <button data-sec="model" aria-current="false">2.1 Befolkningssammensetningen</button>
  <button data-sec="nat" aria-current="false">2.2 Forsorgerbyrden</button>
  <button data-sec="levekar" aria-current="false">2.3 Levekar</button>
  <button data-sec="refugees" aria-current="false">3.1 Okonomien i dag</button>
  <button data-sec="robek" aria-current="false">3.2 Indikatorer 2050</button>
</nav>

"""

PAGE_FOOT = """

<div class="card" style="margin-top:32px">
  <div class="ch"><h3 class="serif">Kommunene i fylket</h3></div>
  <p class="hint">Klikk en kommune for dybdeanalyse.</p>
  <div class="fylke-kommuneliste" id="fylkeKommuner"></div>
</div>

<footer style="margin-top:48px;padding-top:24px;border-top:1px solid var(--line2);color:var(--ink3);font-size:12px;text-align:center">
  Nord-Norge dashboard &middot; Data fra SSB, KOSTRA, KS &middot; <a href="metode.html" style="color:var(--ink2)">Metode og kilder</a>
</footer>
</div>

<script src="assets/data.js"></script>
<script src="assets/app.js" defer></script>
<script defer>
document.addEventListener('DOMContentLoaded', function(){
  // Hent fylke fra URL
  var fylke = state.fylke;
  if(!fylke || fylke === 'Alle'){
    fylke = 'Nordland';
    state.fylke = fylke;
  }
  // Oppdater brodsmuler + headere
  document.getElementById('bcFylke').textContent = fylke;
  document.getElementById('ftitle').innerHTML = fylke + ' &mdash; <em>de neste 25 årene</em>';
  document.getElementById('fkicker').textContent = 'Fylkesoversikt · ' + fylke + ' · SSB · Folketall 1.1.2026';
  document.title = fylke + ' - Nord-Norge dashboard';

  // Seksjons-nav
  var secnav = document.getElementById('secnav');
  if(secnav){
    secnav.querySelectorAll('button').forEach(function(btn){
      btn.onclick = function(){
        var sec = this.dataset.sec;
        var self = this;
        secnav.querySelectorAll('button').forEach(function(x){
          x.setAttribute('aria-current', x===self ? 'true':'false');
        });
        document.querySelectorAll('.tab').forEach(function(t){
          t.classList.toggle('active', t.dataset.tab===sec);
        });
        window.scrollTo({top:0, behavior:'smooth'});
      };
    });
  }
  // Fylke-velger
  var fp = document.getElementById('fylkePicker');
  if(fp){
    fp.value = fylke;
    fp.onchange = function(){
      if(this.value) window.location.search = '?f=' + encodeURIComponent(this.value);
    };
  }
  // Kommune-velger: kun kommuner i dette fylket
  var kp = document.getElementById('kommunePicker');
  if(kp && typeof K !== 'undefined'){
    var fk = K.filter(function(x){return x.fylke===fylke;}).sort(function(a,b){return a.navn.localeCompare(b.navn,'nb');});
    kp.innerHTML = '<option value="">Velg kommune…</option>' +
      fk.map(function(x){return '<option value="' + x.nr + '">' + x.navn + '</option>';}).join('');
    kp.onchange = function(){ if(this.value) window.location.href = 'kommune.html?k=' + this.value; };
  }
  // Kommune-liste
  var klista = document.getElementById('fylkeKommuner');
  if(klista && typeof K !== 'undefined'){
    var fk = K.filter(function(x){return x.fylke===fylke;}).sort(function(a,b){return b.pop-a.pop;});
    klista.innerHTML = fk.map(function(x){
      return '<a href="kommune.html?k=' + x.nr + '"><span>' + x.navn + '</span><span class="pop">' + fmt(x.pop) + '</span></a>';
    }).join('');
  }
  // Reroute nextstep-buttons
  document.querySelectorAll('.nextstep[data-next="explore"]').forEach(function(b){
    b.onclick = function(){
      var fk = K.filter(function(x){return x.fylke===fylke;}).sort(function(a,b){return b.pop-a.pop;});
      window.location.href = 'kommune.html?k=' + (fk[0] ? fk[0].nr : '1804');
    };
  });
  document.querySelectorAll('.nextstep[data-next="summary"]').forEach(function(b){ b.style.display='none'; });
});
</script>
</body>
</html>
"""

with io.open('fylke.html', 'w', encoding='utf-8') as fh:
    fh.write(PAGE_HEAD + content_active + PAGE_FOOT)

import os
print('Wrote fylke.html:', os.path.getsize('fylke.html'), 'bytes')
