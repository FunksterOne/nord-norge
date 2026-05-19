#!/usr/bin/env python3
"""Build nord-norge.html by copying sections from index.html."""
import io
import re

with io.open('index.html', 'r', encoding='utf-8') as fh:
    lines = fh.readlines()

# Find section boundaries
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

# Make first section active
content_active = content.replace('class="tab" data-tab="intro"', 'class="tab active" data-tab="intro"', 1)

PAGE_HEAD = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nord-Norge - landsdelsoversikt</title>
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
</style>
</head>
<body>
<div class="wrap">

<header class="nn-top">
  <nav class="nn-bc" aria-label="Brodsmuler">
    <a href="index.html">Hjem</a>
    <span class="sep">&rsaquo;</span>
    <span class="now">Nord-Norge</span>
  </nav>
  <div class="nn-actions">
    <select id="fylkePicker" aria-label="Velg fylke">
      <option value="">Velg fylke for detaljer&hellip;</option>
      <option value="Nordland">Nordland</option>
      <option value="Troms">Troms</option>
      <option value="Finnmark">Finnmark</option>
    </select>
    <select id="kommunePicker" aria-label="Velg kommune"></select>
    <a class="btn" href="metode.html">Metode</a>
  </div>
</header>

<div style="margin-bottom:20px">
  <div class="kicker">Landsdelsoversikt &middot; SSB &middot; Folketall 1.1.2026 &middot; 80 kommuner</div>
  <h1 class="serif" style="margin:6px 0 12px">Hva skjer i Nord-Norge - og <em>hvem blir igjen?</em></h1>
  <p class="essence">To av tre kommuner mister mer enn 15 % av befolkningen og den arbeidsfore gruppen mot 2050. <em>Sporsmalet er ikke hvilke som forsvinner, men hvor lenge dagens system baerer.</em></p>
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

<footer style="margin-top:48px;padding-top:24px;border-top:1px solid var(--line2);color:var(--ink3);font-size:12px;text-align:center">
  Nord-Norge dashboard &middot; Data fra SSB, KOSTRA, KS &middot; <a href="metode.html" style="color:var(--ink2)">Metode og kilder</a>
</footer>
</div>

<script src="assets/data.js"></script>
<script src="assets/app.js" defer></script>
<script defer>
document.addEventListener('DOMContentLoaded', function(){
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
    fp.onchange = function(){
      if(this.value) window.location.href = 'fylke.html?f=' + encodeURIComponent(this.value);
    };
  }
  // Kommune-velger
  var kp = document.getElementById('kommunePicker');
  if(kp && typeof K !== 'undefined'){
    var sortedK = K.slice().sort(function(a,b){ return a.navn.localeCompare(b.navn,'nb'); });
    kp.innerHTML = '<option value="">Velg kommune' + String.fromCharCode(8230) + '</option>' +
      sortedK.map(function(x){
        return '<option value="' + x.nr + '">' + x.navn + ' (' + x.fylke + ')</option>';
      }).join('');
    kp.onchange = function(){
      if(this.value) window.location.href = 'kommune.html?k=' + this.value;
    };
  }
  // Rerout nextstep-buttons
  document.querySelectorAll('.nextstep[data-next="explore"]').forEach(function(b){
    b.onclick = function(){ window.location.href = 'kommune.html?k=1804'; };
  });
  document.querySelectorAll('.nextstep[data-next="summary"]').forEach(function(b){
    b.style.display = 'none';
  });
});
</script>
</body>
</html>
"""

with io.open('nord-norge.html', 'w', encoding='utf-8') as fh:
    fh.write(PAGE_HEAD + content_active + PAGE_FOOT)

import os
print('Wrote nord-norge.html:', os.path.getsize('nord-norge.html'), 'bytes')
