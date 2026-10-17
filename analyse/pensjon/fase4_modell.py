"""Fase 4: fremskriving av kommunale pensjonskostnader i Nord-Norge, 2026–2050.

Modell per kommune (alle beløp nominelle kroner, andeler i prosent av brutto driftsinntekter, BDI):
  K_t  netto pensjonskostnad (aktuarberegnet, ekskl. AGA)   = K_2025 * v_t * U_t * M_t
  P_t  pensjonspremie (normalisert, ekskl. AGA)             = K_2025 * (1+gamma) * v_t * M_t
  N_t  nytt premieavvik (inkl. AGA)                         = (P_t - K_t) * (1+aga)
  A_t  amortisering (inkl. AGA): beholdningen per 2025 i jevne lag (7/28, 6/28 … 1/28), nye lag 1/7 per år
       fra året etter; kommuner med 1-årsregel amortiserer alt året etter
  R_t  regnskapsført pensjonskostnad (inkl. AGA)            = K_t * (1+aga) + A_t
  S_t  akkumulert premieavvik                               = S_{t-1} + N_t - A_t
  v_t  = (1+g)^(t-2025), g = nominell vekst i lønn og BDI (lik, så andelene påvirkes ikke av lønnsveksten)
  U_t  = økning i beregnet kostnad når forholdstallet senkes (1,0 -> 0,88 i 2026 -> 0,75 fra 2027)
  M_t  = strukturell modning (flere pensjonister, regulering) ut over lønnsveksten, fra 2028
Grunnlag: årsregnskap 2025 (pensjonsnoter), SSB 13202 (premieavvik), 12364 (BDI, disposisjonsfond), 12367 (lønn, AGA).
"""
import json, glob, os, statistics as st

HER = os.path.dirname(os.path.abspath(__file__))
L = lambda f: json.load(open(os.path.join(HER, f), encoding='utf-8'))
rec = {}
for f in sorted(glob.glob(os.path.join(HER, 'regnskap_gruppe*.json'))):
    for r in json.load(open(f, encoding='utf-8')): rec[r['nr']] = r
for f in glob.glob(os.path.join(HER, 'manuelle', '*.json')):
    r = json.load(open(f, encoding='utf-8')); rec[r['nr']] = r
KP, KB, KD = L('kostra_pensjon.json'), L('kostra_bdi.json'), L('kostra_drift.json')['data']
grupper = L('kommuner.json')

G = 0.035                      # nominell vekst i lønn og BDI
AAR = list(range(2025, 2051))
SCEN = {  # U2026, U2027+, strukturell vekst per år fra 2028, premiefondets dekning fra 2027 (1 = som i 2025)
    'lav':   {'u26': 1.025, 'u27': 1.05, 'm': 0.000, 'pf': 1.00},
    'basis': {'u26': 1.05,  'u27': 1.10, 'm': 0.005, 'pf': 0.75},
    'hoy':   {'u26': None,  'u27': None, 'm': 0.010, 'pf': 0.25},   # kostnaden tar igjen premien (KDDs mål), settes fra gamma
}
W7 = [7, 6, 5, 4, 3, 2, 1]


def fylke(nr):
    return 'Nordland' if nr.startswith('18') else ('Troms' if nr.startswith('55') else 'Finnmark')


# ---- grunnlag per kommune ------------------------------------------------------------------------------
grunn = []
for g in grupper:
    for k in g:
        nr = k['nr']; r = rec[nr]
        b25, b24 = KB[nr]['2025'], KB[nr].get('2024', {})
        p25, p24 = KP[nr]['2025'], KP[nr].get('2024', {})
        d25 = KD.get(nr, {}).get('2025', {})
        bdi = b25['bdi'] * 1000
        aga = (d25.get('aga') or 0) / d25['lonn'] if d25.get('lonn') else 0.0
        S25 = ((p25.get('premieavvik_eiendel') or 0) - (p25.get('premieavvik_gjeld') or 0)) * 1000
        S24 = None
        if p24.get('premieavvik_eiendel') is not None:
            S24 = ((p24['premieavvik_eiendel'] or 0) - (p24.get('premieavvik_gjeld') or 0)) * 1000
        K, P, N = r.get('aarets_pensjonskostnad'), r.get('innbetalt_premie'), r.get('aarets_premieavvik')
        kilde = 'note'
        if K and P and N is not None and abs((P - N) - K) > 0.05 * K:
            K = P - N; kilde = 'note (K = premie − premieavvik)'
        if not K and P and N is not None:
            K = P - N; kilde = 'note (K = premie − premieavvik)'
        art090 = (d25.get('pensjon') or 0) * 1000
        A_impl = None
        if N is not None and S24 is not None:
            A_impl = N * (1 + aga) - (S25 - S24)
        grunn.append(dict(nr=nr, navn=r['navn'].split(' - ')[-1] if ' - ' in r['navn'] and nr in (
            '1826', '5512', '5518', '5540', '5610', '5612', '5628', '5636', '1875') else r['navn'].split(' - ')[0],
            fylke=fylke(nr), bdi=bdi, aga=aga, S25=S25, S24=S24, K=K, P=P, N=N, art090=art090, A_impl=A_impl,
            amort=r.get('amortisering_aar') or 7, kilde=kilde, PF=r.get('premiefond_bruk'),
            dispfond=(b25.get('disposisjonsfond') or 0) * 1000, fri_ek=(b25.get('fri_egenkapital_drift') or 0) * 1000,
            lonn13551=(b25.get('lonn') or 0) * 1000))

# gamma: normalisert premie over kostnad, Nord-Norge 2025 (bare kommuner med fullstendig note)
ok = [x for x in grunn if x['K'] and x['P']]
GAMMA = sum(x['P'] for x in ok) / sum(x['K'] for x in ok) - 1
SCEN['hoy']['u26'] = (1 + GAMMA) ** 0.5
SCEN['hoy']['u27'] = 1 + GAMMA

# kommuner uten note: K fra art 090 minus anslått amortisering, kalibrert på kommunene med note
ratio = st.median(x['K'] * (1 + x['aga']) / x['art090'] for x in ok if x['art090'])
for x in grunn:
    if not x['K']:
        x['K'] = x['art090'] * ratio / (1 + x['aga']); x['kilde'] = 'KOSTRA art 090 × median K/art090 (%.2f)' % ratio


pfr = st.median(x['PF'] / x['K'] for x in grunn if x['PF'] and x['K'])
for x in grunn:
    if x['PF'] is None:
        x['PF'] = x['K'] * pfr; x['pf_kilde'] = 'median PF/K (%.2f)' % pfr
    else:
        x['pf_kilde'] = 'note'


def fremskriv(x, sc):
    p = SCEN[sc]
    lag = {}  # år -> amortisering fra beholdningen og nye lag
    if x['amort'] == 1:
        lag[2026] = x['S25']
    else:
        # Beholdningen per 2025 amortiseres med lineært fallende beløp over sju år. Første års beløp kalibreres mot
        # observert amortisering i 2025, avgrenset til [S/7, S/4] (S/7 = like lag i ett år, S/4 = like store årlige lag).
        S = x['S25']
        a1 = x['A_impl'] if x['A_impl'] is not None else S * 7 / 28
        a1 = min(max(a1, S / 7), S / 4) if S > 0 else S / 7
        d = (7 * a1 - S) / 21
        for i in range(7):
            lag[2026 + i] = lag.get(2026 + i, 0) + a1 - i * d
    S = x['S25']; ut = {}
    for t in AAR:
        v = (1 + G) ** (t - 2025)
        U = 1.0 if t == 2025 else (p['u26'] if t == 2026 else p['u27'])
        M = (1 + p['m']) ** max(0, t - 2027)
        K = x['K'] * v * U * M
        dekn = 1.0 if t <= 2026 else p['pf']
        P = (x['K'] * (1 + GAMMA) + x['PF'] * (1 - dekn)) * v * M
        bdi = x['bdi'] * v
        if t == 2025:
            A = x['A_impl'] if x['A_impl'] is not None else 0.206 * (x['S24'] or x['S25'])
            N = (x['N'] if x['N'] is not None else (P - K)) * (1 + x['aga'])
            R = x['K'] * (1 + x['aga']) + A
            ut[t] = dict(R=R, A=A, N=N, S=S, bdi=bdi, K=K * (1 + x['aga']), P=P * (1 + x['aga']))
            continue
        N = (P - K) * (1 + x['aga'])
        A = lag.get(t, 0)
        if x['amort'] == 1:
            lag[t + 1] = lag.get(t + 1, 0) + N
        else:
            for i in range(1, 8):
                lag[t + i] = lag.get(t + i, 0) + N / 7
        S = S + N - A
        R = K * (1 + x['aga']) + A
        ut[t] = dict(R=R, A=A, N=N, S=S, bdi=bdi, K=K * (1 + x['aga']), P=P * (1 + x['aga']))
    return ut


res = {}
for x in grunn:
    res[x['nr']] = {sc: fremskriv(x, sc) for sc in SCEN}

json.dump({'parametre': {'G': G, 'GAMMA': GAMMA, 'scenarier': SCEN, 'median_K_art090': ratio, 'median_PF_K': pfr},
           'grunnlag': grunn,
           'resultat': {nr: {sc: {str(t): v for t, v in s.items()} for sc, s in r.items()} for nr, r in res.items()}},
          open(os.path.join(HER, 'fase4_resultat.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# ---- sammendrag ----------------------------------------------------------------------------------------
pct = lambda a, b: a / b * 100 if b else float('nan')
fmt = lambda v, d=1: f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
print('gamma (premie/kostnad − 1, n=%d): %s' % (len(ok), fmt(GAMMA * 100)), '%;  median K/art090:', fmt(ratio, 2))
print('median PF/K:', fmt(pfr, 2), '; PF fra note:', sum(1 for x in grunn if x['pf_kilde'] == 'note'))
print('kilder K:', {k: sum(1 for x in grunn if x['kilde'].startswith(k)) for k in ('note (', 'note', 'KOSTRA')})
for omr in ('Nord-Norge', 'Nordland', 'Troms', 'Finnmark'):
    sel = [x for x in grunn if omr == 'Nord-Norge' or x['fylke'] == omr]
    for sc in SCEN:
        row = []
        for t in (2025, 2026, 2027, 2030, 2033, 2040, 2050):
            R = sum(res[x['nr']][sc][t]['R'] for x in sel); B = sum(res[x['nr']][sc][t]['bdi'] for x in sel)
            row.append(fmt(pct(R, B)))
        S30 = sum(res[x['nr']][sc][2030]['S'] for x in sel); B30 = sum(res[x['nr']][sc][2030]['bdi'] for x in sel)
        P30 = sum(res[x['nr']][sc][2030]['P'] for x in sel); P25 = sum(res[x['nr']][sc][2025]['P'] for x in sel); B25 = sum(x['bdi'] for x in sel)
        print(f'{omr:10} {sc:5} R/BDI 2025,26,27,30,33,40,50:', ' | '.join(row), '| S/BDI 2030', fmt(pct(S30, B30)), '| premie/BDI 2025→2030', fmt(pct(P25, B25)), '→', fmt(pct(P30, B30)))
# observert sosiale utgifter-andel for kontroll
art = sum(x['art090'] * (1 + x['aga']) for x in grunn); B = sum(x['bdi'] for x in grunn)
print('kontroll: art090×(1+aga)/BDI 2025 =', fmt(pct(art, B)), '%')
