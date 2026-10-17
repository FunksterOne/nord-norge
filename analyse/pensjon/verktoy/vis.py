"""Print given pages from extracted text. Usage: python -I verktoy/vis.py <txtpath> <page> [<page> ...]"""
import sys, re
txt = open(sys.argv[1], encoding='utf-8').read()
parts = re.split(r'\n=====PAGE (\d+)=====\n', txt)
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
for a in sys.argv[2:]:
    if '-' in a:
        lo, hi = map(int, a.split('-'))
        rng = range(lo, hi + 1)
    else:
        rng = [int(a)]
    for p in rng:
        print(f'----- side {p} -----')
        print(pages.get(p, '(mangler)'))
