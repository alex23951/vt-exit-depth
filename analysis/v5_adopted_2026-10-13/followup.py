#!/usr/bin/env python
"""
Aim 1 verdict follow-up on the existing v5 beats (13 Oct 2026, coordinator 19:11 UTC; read only, no new beats).
  1 relative QRS, LV free wall 90 vs 10 % at matched positions: ratio of median QRS and median of per-pair ratios
  2 Durrer on the v5 His beats (control heart, 7D98EVAR beside it): (a) Durrer's three LV areas in the first 5 ms,
    (b) LV endocardium outside the posterobasal region active by 37.5 ms, (c) first RV epicardial breakthrough location,
    (d) last 5 % of the volume by region
  3 Bazan 2007 per region, pooled over the three hearts (LV free wall, vein course, summit sites), q at 0.05 mV (package
    rule) and 0.10 mV (approximation: package q present AND its depth >= 0.10 mV, from the saved q amplitudes; can only
    under-call a full 0.10 mV rescoring); difference 90 - 10 % with a Newcombe hybrid-score 95 % CI vs Bazan's difference
  4 Berruezo direction, 6G8DD8S5: median paired difference (ms) of QRS, pseudo-delta, IDT, shortest RS
Output: gates_followup.md (this folder).
"""

import json
import math
import os

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
L = []


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def load(h):
    d = pd.read_csv(os.path.join(HERE, f'purk_{h}_v5.csv'))
    d = d[d.family != 'his'].copy(); d['depth_target'] = d.depth_target.astype(float)
    return d


def pairs(d, fam='lv_free_wall'):
    x = d[d.family == fam]
    a = x[x.depth_target == 0.9].set_index(['position', 'level_z']); b = x[x.depth_target == 0.1].set_index(['position', 'level_z'])
    return a.join(b, lsuffix='_90', rsuffix='_10', how='inner')


def wilson(k, n, z=1.96):
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return c - hw, c + hw


def newcombe(k1, n1, k2, n2):
    """Difference p1 - p2 with Newcombe's hybrid-score 95 % CI (method 10)."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


# ------------------------------------------------------------------ 1
L.append('# Aim 1 verdict follow-up, model v5 (13 Oct 2026; existing v5 beats, true onset)\n')
L.append('## 1 Relative QRS, LV free wall 90 % vs 10 % at matched positions (pass 206/191 = 1.0785 to 219/189 = 1.1587)\n')
L.append('| heart | pairs | median QRS 90 / 10 % (ms) | ratio of medians | median of per-pair ratios | pass (ratio of medians / per-pair) |')
L.append('|---|---|---|---|---|---|')
for h in HEARTS:
    p = pairs(load(h))
    a, b = p.true_qrs_duration_ms_90, p.true_qrs_duration_ms_10
    rm, rp = a.median() / b.median(), (a / b).median()
    ok = lambda r: 1.0785 <= r <= 1.1587
    L.append(f'| {h} | {len(p)} | {a.median():.1f} / {b.median():.1f} | {rm:.4f} | {rp:.4f} | {ok(rm)} / {ok(rp)} |')
L.append('\nThe "medians 1.096" of the v5 gate table is the ratio of median QRSs (median over the 10 positions at 90 % divided by the median at 10 %), the 12 Oct statistic.\n')

# ------------------------------------------------------------------ 2
L.append('## 2 Durrer on the v5 His beat (times after the first LV endocardial activation)\n')
for h in ('Y5HYEDL4', '7D98EVAR'):
    T = np.load(os.path.join(HERE, 'grid', h, 'his_T.npy')).astype(float)
    pts = pd.read_csv(hd(h, 'biv.pts'), sep=r'\s+', skiprows=1, header=None).to_numpy() / 1e3
    z, phi, v = (np.loadtxt(hd(h, 'uvc', n + '.dat')) for n in ('z', 'phi', 'v')); ph = np.degrees(phi)
    rd = lambda n: np.loadtxt(hd(h, 'surfaces', n + '.vtx'), skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    t0 = float(T[lv].min())
    early = lv[T[lv] <= t0 + 5]
    tg = {'high anterior paraseptal (phi +60, z 0.80)': (60.0, 0.80), 'central left septum (phi 0, z 0.50)': (0.0, 0.50),
          'posterior paraseptal at 1/3 apex-base (phi -60, z 0.33)': (-60.0, 0.33)}
    L.append(f'### {h}\n- (a) first 5 ms of LV endocardial activation ({len(early)} nodes):')
    for k, (p_, zz) in tg.items():
        n = int(lv[np.argmin((z[lv] - zz) ** 2 + (np.abs(np.angle(np.exp(1j * np.radians(ph[lv] - p_)))) / np.pi) ** 2)])
        on = float(T[lv][np.linalg.norm(pts[lv] - pts[n], axis=1) <= 10].min() - t0)
        within = int((np.linalg.norm(pts[early] - pts[n], axis=1) <= 15).sum())
        L.append(f'  - {k}: earliest activation within 10 mm at {on:.1f} ms -> {"inside" if on <= 5 else "outside"} the first 5 ms; {within} of the first-5-ms nodes within 15 mm')
    tri = np.loadtxt(hd(h, 'surfaces', 'lv_endo.surf'), skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    ta = 0.5 * np.linalg.norm(np.cross(pts[tri[:, 1]] - pts[tri[:, 0]], pts[tri[:, 2]] - pts[tri[:, 0]]), axis=1)
    na = np.bincount(tri.ravel(), weights=np.repeat(ta / 3, 3), minlength=len(pts))
    keep = lv[~((z >= 2 / 3) & (ph >= -150) & (ph <= -30))[lv]]
    L.append(f'- (b) LV endocardium outside the posterobasal region (UVC z >= 2/3, phi -150..-30 deg) active by 37.5 ms: '
             f'{100 * na[keep][T[keep] <= t0 + 37.5].sum() / na[keep].sum():.1f} % (by 30 ms {100 * na[keep][T[keep] <= t0 + 30].sum() / na[keep].sum():.1f} %)')
    rve = epi[v[epi] == 1]; i = int(rve[np.argmin(T[rve])])
    mb = json.load(open(hd(h, 'purkinje', 'summary.json')))['landmarks']['mb_end']
    dmb = float(np.linalg.norm(pts[i] - pts[mb]))
    side = 'anterior' if ph[i] > 20 else ('inferior' if ph[i] < -20 else 'lateral')
    L.append(f'- (c) first RV epicardial breakthrough at {T[i] - t0:.1f} ms, UVC z {z[i]:.2f}, phi {ph[i]:.0f} deg ({side} RV free wall, mid level), '
             f'{dmb:.1f} mm from the moderator-band insertion: consistent with the area pretrabecularis (anterior RV free wall at the '
             f'moderator-band insertion) if that proxy is accepted; the mesh has no trabecular labels, so this is a geometric proxy')
    el = pd.read_csv(hd(h, 'biv.elem'), sep=r'\s+', skiprows=1, header=None, usecols=[1, 2, 3, 4]).to_numpy()
    a_, b_, c_, d_ = (pts[el[:, k]] for k in range(4))
    nvol = np.bincount(el.ravel(), weights=np.repeat(np.abs(np.einsum('ij,ij->i', np.cross(b_ - a_, c_ - a_), d_ - a_)) / 24, 4), minlength=len(pts))
    o = np.argsort(T); last = o[np.cumsum(nvol[o]) / nvol.sum() > 0.95]
    dpv = cKDTree(pts[rd('pv_rim')]).query(pts[last])[0]; dtv = cKDTree(pts[rd('tv_rim')]).query(pts[last])[0]
    zl, pl, vl, wl = z[last], ph[last], v[last], nvol[last]
    reg = np.full(len(last), 'other (anterior / septal base)', dtype=object)
    for name, m in [('LV posterolateral base', (vl == 0) & (zl >= 2 / 3) & (np.abs(pl) > 150)),
                    ('LV posterobasal', (vl == 0) & (zl >= 2 / 3) & (pl >= -150) & (pl <= -30)),
                    ('RV posterobasal', (vl == 1) & (zl >= 2 / 3) & (pl < -20)),
                    ('RV A-V sulcus (<= 10 mm from the tricuspid rim)', (vl == 1) & (dtv <= 10)),
                    ('pulmonary conus (<= 20 mm from the pulmonary rim)', (vl == 1) & (dpv <= 20))]:
        reg[m] = name
    br = {r: round(100 * float(wl[reg == r].sum() / wl.sum()), 1) for r in pd.unique(reg)}
    L.append(f'- (d) last 5 % of the volume (from {T[last].min() - t0:.1f} ms): ' + ', '.join(f'{k} {v_} %' for k, v_ in sorted(br.items(), key=lambda x: -x[1]))
             + ". Durrer's late areas: posterobasal LV, pulmonary conus, RV posterobasal / A-V sulcus.\n")

# ------------------------------------------------------------------ 3
L.append('## 3 Bazan 2007 per region, pooled over the three hearts (LV free wall, vein-course and summit positions; true onset)\n')
L.append('Bazan 2007 (abstract): epi vs endo q in I basal superior 90 vs 16 %, apical superior 88 vs 26 %; Q in II/III/aVF basal inferior 81 vs 37 %, '
         'apical inferior 92 vs 33 %; basal superior: absence of inferior Q identifies epicardium (P .002, no % given). Gate: per-region 95 % CI, >= 20 pooled positions.\n')
L.append('| region / feature | threshold | positions | 90 % | 10 % | difference (95 % CI), pp | Bazan difference, pp | verdict |')
L.append('|---|---|---|---|---|---|---|---|')
D = pd.concat([load(h).assign(heart=h) for h in HEARTS])
D = D[D.family.isin(['lv_free_wall', 'lv_vein_course', 'lv_summit']) & D.depth_target.isin([0.1, 0.9])]
qI = lambda d, t: d.true_q_lead_I.astype(str).str.lower().eq('true') & (d.true_q_amp_I.astype(float) >= t)
qinf = lambda d, t: d.true_inferior_q_any.astype(str).str.lower().eq('true') & ((d[['true_q_amp_II', 'true_q_amp_III', 'true_q_amp_aVF']].astype(float) >= t).any(axis=1))
REG = [('basal superior: q in I', 'lv_basal_superior', qI, 74), ('basal superior: no Q in II/III/aVF', 'lv_basal_superior', None, None),
       ('apical superior: q in I', 'lv_apical_superior', qI, 62), ('basal inferior: Q in II/III/aVF', 'lv_basal_inferior', qinf, 44),
       ('apical inferior: Q in II/III/aVF', 'lv_apical_inferior', qinf, 59)]
for name, reg, fn, bz in REG:
    d = D[D.bazan_region == reg]
    for t in (0.05, 0.10):
        call = (~qinf(d, t)) if fn is None else fn(d, t)
        k9, n9 = int(call[d.depth_target == 0.9].sum()), int((d.depth_target == 0.9).sum())
        k1, n1 = int(call[d.depth_target == 0.1].sum()), int((d.depth_target == 0.1).sum())
        df_, lo, hi = newcombe(k9, n9, k1, n1)
        if n9 < 20:
            verdict = 'not evaluable (< 20 positions)'
        elif bz is None:
            verdict = 'direction ' + ('as Bazan (more at epi)' if df_ > 0 else 'opposite to Bazan') + '; no Bazan % to compare'
        else:
            verdict = 'consistent (Bazan inside CI)' if lo * 100 <= bz <= hi * 100 else 'fail (Bazan outside CI)'
        L.append(f'| {name} | {t:.2f} mV | {n9} | {k9}/{n9} ({100 * k9 / n9:.0f} %) | {k1}/{n1} ({100 * k1 / n1:.0f} %) | '
                 f'{100 * df_:+.0f} ({100 * lo:+.0f} to {100 * hi:+.0f}) | {"+" + str(bz) if bz is not None else "n/a"} | {verdict} |')
L.append('\n0.10 mV = package q present and q depth >= 0.10 mV (saved amplitudes; no ECGs were saved for the v5 grid, so no full rescoring).\n')

# ------------------------------------------------------------------ 4
L.append('## 4 Berruezo direction, 6G8DD8S5 LV free wall, median paired difference 90 - 10 % (ms, true onset)\n')
p = pairs(load('6G8DD8S5'))
for k, c in (('QRS', 'true_qrs_duration_ms'), ('pseudo-delta', 'true_pseudo_delta_ms'), ('IDT', 'true_idt_v2_ms'), ('shortest RS', 'true_srs_ms')):
    dd = (p[c + '_90'] - p[c + '_10']).dropna()
    L.append(f'- {k}: {dd.median():+.1f} ms (positive in {int((dd > 0).sum())} / {len(dd)} pairs, zero {int((dd == 0).sum())})')
open(os.path.join(HERE, 'gates_followup.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
