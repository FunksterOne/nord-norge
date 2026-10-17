"""Nøkkeltall per kommune fra fase4_resultat.json → fase4_kommuner.csv (semikolonseparert) og fase4_kommuner.json.
Kjør etter fase4_modell.py."""
import csv, json, os

HER = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HER, 'fase4_resultat.json'), encoding='utf-8'))
G = {x['nr']: x for x in D['grunnlag']}
R = D['resultat']


def andel(s, t, k='R'):
    return round(s[str(t)][k] / s[str(t)]['bdi'] * 100, 2)


rader = []
for nr, x in G.items():
    b, l, h = R[nr]['basis'], R[nr]['lav'], R[nr]['hoy']
    rader.append(dict(
        nr=nr, navn=x['navn'], fylke=x['fylke'], amort_aar=x['amort'],
        premieavvik_2025_pst=round(x['S25'] / x['bdi'] * 100, 2), dispfond_2025_pst=round(x['dispfond'] / x['bdi'] * 100, 2),
        R2025=andel(b, 2025),
        R2030_lav=andel(l, 2030), R2030_basis=andel(b, 2030), R2030_hoy=andel(h, 2030),
        R2033_basis=andel(b, 2033),
        R2040_lav=andel(l, 2040), R2040_basis=andel(b, 2040), R2040_hoy=andel(h, 2040),
        R2050_lav=andel(l, 2050), R2050_basis=andel(b, 2050), R2050_hoy=andel(h, 2050),
        premie2025=andel(b, 2025, 'P'), premie2030_basis=andel(b, 2030, 'P'), premie2030_hoy=andel(h, 2030, 'P'),
        endring_R_2025_2050_basis_mill_2025kr=round((andel(b, 2050) - andel(b, 2025)) / 100 * x['bdi'] / 1e6, 1),
        kilde_kostnad=x['kilde'], kilde_premiefond=x['pf_kilde']))
with open(os.path.join(HER, 'fase4_kommuner.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rader[0]), delimiter=';')
    w.writeheader(); w.writerows(rader)
json.dump(rader, open(os.path.join(HER, 'fase4_kommuner.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('skrev', len(rader), 'kommuner')
