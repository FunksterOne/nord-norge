import json, subprocess, sys
d = {'KG50': {'5524': 1256228, '5526': 714827, '5532': 967548, '5536': 619975, '5540': 521715, '5542': 664603, '5522': 598926},
     'KG61': {'5524': 138834, '5526': 77822, '5532': 64257, '5536': 30974, '5540': 29011, '5542': 55998, '5522': 59057},
     'KG82': {'5524': 1168927, '5526': 638208, '5532': 973661, '5536': 635776, '5540': 535747, '5542': 651644, '5522': 583217},
     'KG89': {'5524': 0, '5526': -1322, '5532': 0, '5536': 0, '5540': 6276, '5542': 0, '5522': 0}}
ejn = {'5524': 'jp_01kw84xzb2es6s33c03afmv88b (journalført 15.06.2026)', '5526': 'jp_01kwwr5vn8edb9wk52t9vnwgec (23.06.2026)',
       '5532': 'jp_01m1cyrfdje7yt5694gjdydffx (18.08.2026)', '5536': 'jp_01kx1xqvjre7d8x9rddzxq7yvk (25.06.2026)',
       '5540': 'jp_01kwt6ped2e3htbvmrbha18dsy (22.06.2026)', '5542': 'jp_01kwfvz51ner6tbwzqmbtc7pge (18.06.2026)',
       '5522': 'jp_01kxer5y86erpbtncyqabbrnbh (30.06.2026)'}
for nr in d['KG50']:
    m, f, pa, pg = d['KG50'][nr]*1000, d['KG82'][nr]*1000, d['KG61'][nr]*1000, d['KG89'][nr]*1000
    gjeld = abs(pg)
    akk = pa - gjeld if gjeld else pa
    extra = (f' Balansen har i tillegg premieavvik som gjeld (E.1.6) {gjeld:,} kr (SSB-fortegn {pg:,}); akkumulert premieavvik inkl. AGA er satt til netto eiendel − gjeld = {akk:,} kr (eiendel alene {pa:,} kr).'.replace(',', ' ')) if gjeld else ''
    p = {'nr': nr, 'regnskapsaar': 2025,
         'kilde_url': 'https://data.ssb.no/api/pxwebapi/v2/tables/13545 (KOSTRA, kommunekasse, 2025)',
         'kilde_side': 'SSB tabell 13545, balansedata KG50 / KG61 / KG82 / KG89, regnskapsomfang B (kommunekasse); ikke fra pensjonsnoten',
         'konsern_eller_kasse': 'kommunekasse (KOSTRA)',
         'leverandorer': [],
         'brutto_pensjonsforpliktelse': f, 'pensjonsmidler': m, 'netto_forpliktelse': f - m,
         'akkumulert_premieavvik_inkl_aga': akk,
         'merknader': ('DELVIS – årsregnskapet ble ikke hentet. Kommunens møtedokumenter ligger i ACOS Innsyn Pluss (innsynpluss.onacos.no), der fil-nedlastingen er beskyttet av en Azure WAF-botsjekk (curl får 403 med JS-utfordring); den er ikke forsøkt omgått. '
                       f'Statsforvalteren har journalført årsregnskapet i eInnsyn ({ejn[nr]}), men dokumentet er ikke tilgjengelig der. '
                       'Tallene er i stedet hentet fra KOSTRA-balansen (SSB 13545, kommunekasse 2025), oppgitt i hele tusen kroner og her ganget med 1 000 (avrundet til nærmeste tusen). '
                       'KG82 Pensjonsforpliktelse inkluderer arbeidsgiveravgift av netto forpliktelse for ordninger med underdekning, slik at brutto ekskl. AGA kan være noe lavere; netto er beregnet som KG82 − KG50 med samme forbehold. '
                       'Premieavvik i balansen (KG61) er inkl. AGA. Kontrollert for Bardu, Ibestad, Lavangen og Storfjord: KOSTRA-tallene er identiske med balansen i årsregnskapet. '
                       'Leverandører, kostnad, premie, årets premieavvik, amortiseringstid og forutsetninger kan ikke avledes fra KOSTRA-balansen.' + extra)}
    json.dump(p, open('verktoy3/p.json', 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run([sys.executable, '-P', 'verktoy3/oppdater.py', 'verktoy3/p.json'])
