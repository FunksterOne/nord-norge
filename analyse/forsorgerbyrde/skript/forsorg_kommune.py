import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
H = Path(__file__).parent; sys.path.insert(0, str(H))
from forsorg import S, P, KODER  # noqa
navn = {}
dj = (Path(r"C:\Users\HalvardNordang\Github\nord-norge\assets\data.js")).read_text(encoding='utf-8')
import re
for m in re.finditer(r'"(\d{4})":\{"navn":"([^"]+)"', dj): navn.setdefault(m.group(1), m.group(2).split(' - ')[-1])
rows = []
for k in KODER:
    pop = lambda lo, hi: sum(P.get((k, a), 0) for a in range(lo, hi + 1))
    tot, a65, a2064 = pop(0, 120), pop(65, 120), pop(20, 64)
    syss = S.get((k, "A.01", "15+"), 0)
    aapu = S.get((k, "U.04-U.05", "20-66"), 0) / S.get((k, "TOT", "20-66"), 1) * 100
    rows.append((k, navn.get(k, k), a65 / a2064 * 100, (tot - syss) / syss * 100, aapu, S.get((k, "A.01", "20-66"), 0) / S.get((k, "TOT", "20-66"), 1) * 100))
rd = {r[0]: i + 1 for i, r in enumerate(sorted(rows, key=lambda r: -r[2]))}
re_ = {r[0]: i + 1 for i, r in enumerate(sorted(rows, key=lambda r: -r[3]))}
import statistics as st
xs, ys = [r[2] for r in rows], [r[3] for r in rows]
mx, my = st.mean(xs), st.mean(ys)
corr = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** .5
print(f"korrelasjon demografisk/økonomisk over 80 kommuner: {corr:.2f}")
print("Størst rangendring (plass demografisk -> økonomisk, 1 = tyngst):")
for r in sorted(rows, key=lambda r: -abs(rd[r[0]] - re_[r[0]]))[:10]:
    print(f"  {r[1]:<14} demogr {r[2]:5.1f} (#{rd[r[0]]:>2})  økon {r[3]:6.1f} (#{re_[r[0]]:>2})  AAP/uføre 20-66 {r[4]:4.1f} %  syssrate 20-66 {r[5]:4.1f} %")
print("Tyngst økonomisk:", [(r[1], round(r[3], 1)) for r in sorted(rows, key=lambda r: -r[3])[:6]])
print("Lettest økonomisk:", [(r[1], round(r[3], 1)) for r in sorted(rows, key=lambda r: r[3])[:6]])
print("Høyest AAP/uføre:", [(r[1], round(r[4], 1)) for r in sorted(rows, key=lambda r: -r[4])[:6]])
