"""Network grids (jobs 8-10): criteria with the study's lead fields vs the cb conductor (heart at Clerc scale + blood),
10 Oct 2026. Same activation maps; only the ECG weights differ.
Usage: python compare_cb.py  -> compare_cb.md here"""
import csv
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', 'grids_2026-10-07')
HEARTS = ['Y5HYEDL4', '7D98EVAR', '6G8DD8S5']
MEAS = ['qrs_duration_ms', 'pseudo_delta_ms', 'idt_v2_ms', 'srs_ms', 'mdi_daniels']
CALLS = ['berruezo_pdw_ge_34', 'berruezo_idt_ge_85', 'berruezo_srs_ge_121', 'daniels_mdi_ge_055', 'valles_q_lead_I']


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def b(x):
    return {'True': True, 'False': False}.get(x)


def med(xs, nd=1):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), nd) if xs else None


def auc(pos, neg):
    pos, neg = [x for x in pos if x is not None], [x for x in neg if x is not None]
    if not pos or not neg:
        return None
    return round(sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg)), 2)


def dep(r):
    return int(round(float(r['depth_target']) * 100))


out = ['# Network grids: study lead fields vs cb conductor (heart at Clerc scale + blood), same activation maps', '']
for h in HEARTS:
    A = {r['id']: r for r in csv.DictReader(open(os.path.join(G, f'purk_{h}.csv')))}
    C = {r['id']: r for r in csv.DictReader(open(os.path.join(G, f'purk_{h}_cb.csv')))}
    ids = [i for i in A if i in C]
    out += [f'## {h} ({len(ids)} sites)', '', '| measure (onset mode) | study median | cb median | median change | median abs change | max abs change |',
            '|---|---|---|---|---|---|']
    for mode in ('true', 'detected'):
        for k in MEAS:
            a = [f(A[i][f'{mode}_{k}']) for i in ids]; c = [f(C[i][f'{mode}_{k}']) for i in ids]
            d = [y - x for x, y in zip(a, c) if x is not None and y is not None]
            nd = 2 if k == 'mdi_daniels' else 1
            out.append(f'| {k} ({mode}) | {med(a, nd)} | {med(c, nd)} | {med(d, nd)} | {med([abs(x) for x in d], nd)} | '
                       f'{round(max(abs(x) for x in d), nd) if d else None} |')
    out += ['', '| epicardial call (onset mode) | study n true | cb n true | sites that changed |', '|---|---|---|---|']
    for mode in ('true', 'detected'):
        for k in CALLS:
            a = [b(A[i].get(f'{mode}_{k}')) for i in ids]; c = [b(C[i].get(f'{mode}_{k}')) for i in ids]
            out.append(f'| {k} ({mode}) | {sum(x is True for x in a)} | {sum(x is True for x in c)} | '
                       f'{sum(x != y for x, y in zip(a, c))} |')
    out += ['', 'Depth signal, all sites with a depth truth (cusps out), AUC 90 % vs 10 % (true / detected onset), study -> cb:', '']
    for k in MEAS[1:]:
        s = []
        for D in (A, C):
            R = [D[i] for i in ids if D[i].get('epi_endo_truth') == 'True']
            s.append(f"{auc([f(r['true_' + k]) for r in R if dep(r) == 90], [f(r['true_' + k]) for r in R if dep(r) == 10])} / "
                     f"{auc([f(r['detected_' + k]) for r in R if dep(r) == 90], [f(r['detected_' + k]) for r in R if dep(r) == 10])}")
        out.append(f'- {k}: {s[0]} -> {s[1]}')
    out.append('')
open(os.path.join(HERE, 'compare_cb.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
