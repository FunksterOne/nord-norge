import json,glob,statistics as st
rec={}
for f in sorted(glob.glob('regnskap_gruppe*.json')):
    for r in json.load(open(f,encoding='utf-8')): rec[r['nr']]=r
for f in glob.glob('manuelle/*.json'):
    r=json.load(open(f,encoding='utf-8')); rec[r['nr']]=r
K=json.load(open('kostra_pensjon.json',encoding='utf-8'))
D=json.load(open('kostra_drift.json',encoding='utf-8'))['data']
grp=json.load(open('kommuner.json',encoding='utf-8'))
fylke=lambda nr: 'Nordland' if nr.startswith('18') else ('Troms' if nr.startswith('55') or nr in('5544','5546') else 'Finnmark')
rows=[]
for g in grp:
  for k in g:
    nr=k['nr']; r=rec[nr]; k25=K[nr]['2025']; k24=K[nr].get('2024',{})
    pa=(k25['premieavvik_eiendel'] or 0)-(k25['premieavvik_gjeld'] or 0)
    pa24=((k24.get('premieavvik_eiendel') or 0)-(k24.get('premieavvik_gjeld') or 0)) if k24.get('premieavvik_eiendel') is not None else None
    bdi=k25.get('bdi'); d=D.get(nr,{}).get('2025',{})
    rows.append(dict(nr=nr,navn=k['navn'].split(' - ')[0] if not k['navn'].startswith(('Aarborte','Dielddanuorri','Loabák','Gáivuotna','Unjárga','Deatnu','Guovdageaidnu','Kárásjohka','Hábmer')) else k['navn'].split(' - ')[-1],
      fylke=fylke(nr), bdi=bdi, pa=pa, pa24=pa24, pa_bdi=pa/bdi*100 if bdi else None, pa24_bdi=(pa24/K[nr]['2024']['bdi']*100) if pa24 is not None and K[nr]['2024'].get('bdi') else None,
      ek=k25.get('egenkapital_drift'), forpl=k25['pensjonsforpliktelse'], midler=k25['pensjonsmidler'],
      premie=r.get('innbetalt_premie'), kost=r.get('aarets_pensjonskostnad'), aavvik=r.get('aarets_premieavvik'),
      pf=r.get('premiefond_bruk'), amort=r.get('amortisering_aar'), lev=sorted({l['leverandor'] for l in r.get('leverandorer') or []}),
      pens=d.get('pensjon'), lonn=d.get('lonn')))
json.dump(rows,open('fase3_samlet.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
f=lambda x:f"{x:,.1f}".replace(',',' ').replace('.',',')
tot=lambda key,sel=rows: sum(r[key] or 0 for r in sel)
print('NN 80: forpl',f(tot('forpl')/1e6),'mrd; midler',f(tot('midler')/1e6),'mrd; premieavvik',f(tot('pa')/1e3),'mill; BDI',f(tot('bdi')/1e6),'mrd; pa/bdi',f(tot('pa')/tot('bdi')*100),'%')
for fy in ('Nordland','Troms','Finnmark'):
    s=[r for r in rows if r['fylke']==fy]; print(fy,len(s),'pa',f(tot('pa',s)/1e3),'mill; pa/bdi',f(tot('pa',s)/tot('bdi',s)*100),'%; 2024',f(sum(r['pa24'] or 0 for r in s)/sum(K[r['nr']]['2024'].get('bdi') or 0 for r in s if r['pa24'] is not None)*100))
v=sorted([r for r in rows if r['pa_bdi'] is not None],key=lambda r:-r['pa_bdi'])
print('median pa/bdi',f(st.median(r['pa_bdi'] for r in v)))
print('TOPP 12:'); [print(' ',r['nr'],r['navn'],f(r['pa_bdi']),'% |',f(r['pa']/1e3),'mill | EK drift',f((r['ek'] or 0)/1e3),'| pa/EK',f(r['pa']/r['ek']) if r['ek'] else '-', '| amort',r['amort']) for r in v[:12]]
print('BUNN 8:'); [print(' ',r['nr'],r['navn'],f(r['pa_bdi']),'% amort',r['amort']) for r in v[-8:]]
print('>10 %:',sum(1 for r in v if r['pa_bdi']>10),' >15 %:',sum(1 for r in v if r['pa_bdi']>15),' <3 %:',sum(1 for r in v if r['pa_bdi']<3))
print('premieavvik > egenkapital drift:',[(r['navn'],f(r['pa']/1e3),f((r['ek'] or 0)/1e3)) for r in rows if r['ek'] is not None and r['pa']>r['ek']])
s=[r for r in rows if r['premie'] and r['kost'] and r['aavvik'] is not None]
print('Flyt 2025 n=',len(s),'premie',f(tot('premie',s)/1e6),'kost',f(tot('kost',s)/1e6),'årets pa',f(tot('aavvik',s)/1e6),'mill; premiefond brukt (n=%d)'%sum(1 for r in rows if r['pf']),f(tot('pf')/1e6))
print('amort:',{a:sum(1 for r in rows if r['amort']==a) for a in (1,7,None)})
print('egen kasse:',[r['navn'] for r in rows if any('kasse' in l.lower() and 'KLP' not in l and 'SPK' not in l for l in r['lev'])])
print('netto underdekning (KOSTRA forpl>midler):',sum(1 for r in rows if r['forpl']>r['midler']),'av 80')
# pension cost share of wages
for fy in ('Nordland','Troms','Finnmark'):
    s=[r for r in rows if r['fylke']==fy and r['pens'] and r['lonn']]; print('pensjon/lønn',fy,f(tot('pens',s)/tot('lonn',s)*100))
