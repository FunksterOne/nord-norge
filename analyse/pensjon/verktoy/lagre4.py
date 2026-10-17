"""Upsert one municipality record into regnskap_gruppe4.json.
Usage: python -I verktoy/lagre.py <record.json>
"""
import sys, os, json
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'regnskap_gruppe4.json')
rec = json.load(open(sys.argv[1], encoding='utf-8'))
data = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
data = [d for d in data if d['nr'] != rec['nr']] + [rec]
data.sort(key=lambda d: d['nr'])
json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('saved', rec['nr'], len(data))
