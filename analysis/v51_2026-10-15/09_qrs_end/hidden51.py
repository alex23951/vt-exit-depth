"""Hidden late-QRS check (19 Oct 2026, read-only; brief PC-HIDDEN-LATE-QRS-BRIEF from the cloud thread "QRS end measurement
problem", Alex chose "Run check" 19 Oct 2026 09:16 UTC). No simulation; no v5.1 file is changed; nothing is tuned.

Beats (v5.1 network beats, runs/v51_2026-10-15/06_pilot_rerun/maps, control heart Y5HYEDL4): target = the 16 LV summit and
aortic-cusp beats behind gate 1; contrast = the 10 LV free-wall 10 % / 90 % pairs (20 beats).
Surface QRS end t_se = the Step 6 0.4.0 offset in any lead under gate 1's primary convention (detected onset, 10 uV noise,
median of seeds 0-9; rescore/per_site.csv), used for target and contrast alike; the precordial offset and the clean
(noise-free) offsets are reported beside it. True end = latest node activation. Hidden window = [t_se, true end].
Hidden tissue = nodes activated at or after t_se; nodal volume = 1/4 of each incident tet (all ventricular tags 1, 2, 25,
28, 29); LV / RV from UVC v; AHA segment from 05_aha_labels/aha51.py Frame (the adopted placement frame, evaluated per
node with the frame of the node's 1 mm height band); RV nodes get RV + level; depth third from UVC rho (0 endo, 1 epi).
ECG = the Step 6 lead-field computation (data/biv/<H>/ecgW_v51.npz sigma_i weights, 15_conductor.py template; the stored
clean Step 6 ECG). Contributions use Vm minus the resting value (the weights sum to zero per lead, so the full ECG is
unchanged): hidden c_S(t) = sum over hidden nodes, per AHA region c_r(t) the same over the region's hidden nodes;
early-tissue (overlap) signal o(t) = full ECG - c_S(t), i.e. everything not hidden. Peaks are of the change from t_se,
within the hidden window. Cancellation: plain-sum peak vs the peak of the sum of absolute regional changes. Spatial velocity
= ecg_depth_criteria 0.4.0 offset velocity (6 ms smoothing, leads I, II, V1-V6), against 10 % of the full ECG's peak.
Template (Tomek pseudo-Vm, 15_conductor.py): -60 to +80 ms around activation (upstroke, plateau dome to ~21 mV at 20-30 ms,
decline to 13.9 mV at 80 ms), held after 80 ms: early plateau included, no repolarisation (no T wave).
Usage (repo root, venv): python -B analysis/v51_2026-10-15/09_qrs_end/hidden51.py
Writes hidden/hidden51.csv and hidden/REPORT.md in this folder.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '05_aha_labels'))
sys.path.insert(0, os.path.join(REPO, 'code', 'ecg_depth_criteria'))
import aha51                                                          # noqa: E402
import conductor51 as C51                                             # noqa: E402
from ecg_depth_criteria.fiducials import slopes, spatial_velocity     # noqa: E402

H = 'Y5HYEDL4'
MAPS = os.path.join(REPO, 'runs', 'v51_2026-10-15', '06_pilot_rerun', 'maps', H)
OUTD = os.path.join(HERE, 'hidden')
L12 = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
IND = [0, 1, 6, 7, 8, 9, 10, 11]                                      # I, II, V1-V6
SMOOTH_OFF_MS = 6.0                                                   # Settings.offset_smooth_ms (0.4.0)


def node_labels(F, v, rho):
    """Region per node: 'LV <AHA number>' (aha51 Frame rules, frame of the node's 1 mm height band), 'RV <level>'; depth third."""
    P = F.P
    f = F.f(P)
    a = np.round(f * F.Lax).astype(int)
    c_ = F.cap_f
    level = np.where(f < c_ + (1 - c_) / 3, 'apical', np.where(f < c_ + 2 * (1 - c_) / 3, 'mid', 'basal'))
    region = np.empty(len(P), dtype=object)
    rv = v > 0.5
    region[rv] = np.char.add('RV ', level[rv].astype(str))
    lv = np.where(~rv)[0]
    cap = lv[f[lv] < c_]
    region[cap] = 'LV 17'
    rest = lv[f[lv] >= c_]
    frames = {}
    for b in np.unique(a[rest]):
        loc, a_use = F.local(float(b)), float(b)
        while loc is None or np.isnan(loc[3]) or np.isnan(loc[4]):
            a_use -= 1.0
            if a_use < 0:
                loc = None
                break
            loc = F.local(a_use)
        frames[b] = loc
    for b, loc in frames.items():
        idx = rest[a[rest] == b]
        if loc is None:
            region[idx] = 'LV n/a'
            continue
        c, e1, e2, ia, ii = loc
        th = np.degrees(np.arctan2((P[idx] - c) @ e2, (P[idx] - c) @ e1))
        for k, n in enumerate(idx):
            lev = level[n]
            if ii <= th[k] <= ia:
                seg = 'septal' if lev == 'apical' else ('anteroseptal' if th[k] >= (ia + ii) / 2 else 'inferoseptal')
            else:
                fw = ((th[k] - ia) % 360) / ((ii - ia) % 360)
                seg = (['anterior', 'lateral', 'inferior'][min(2, int(fw * 3))] if lev == 'apical'
                       else ['anterior', 'anterolateral', 'inferolateral', 'inferior'][min(3, int(fw * 4))])
            region[n] = f'LV {aha51.SEG_NO[(lev, seg)]}'
    third = np.where(rho < 1 / 3, 'endo', np.where(rho < 2 / 3, 'mid', 'epi'))
    return region, third


def nodal_volume(P, E):
    x0 = P[E[:, 0]]
    vol = np.abs(np.einsum('ij,ij->i', P[E[:, 1]] - x0, np.cross(P[E[:, 2]] - x0, P[E[:, 3]] - x0))) / 6
    return np.bincount(E.ravel(), weights=np.repeat(vol / 4, 4), minlength=len(P))


def vm_minus_rest(t, T, tm, step=20000):
    """(len(t), len(T)) template Vm minus resting value, chunked."""
    out = np.empty((len(t), len(T)))
    for i0 in range(0, len(T), step):
        sl = slice(i0, i0 + step)
        rel = t[:, None] - T[None, sl]
        out[:, sl] = np.interp(rel.ravel(), tm.t, tm.v, left=tm.v[0], right=tm.v[-1]).reshape(rel.shape) - tm.v[0]
    return out


def sv(x_t12):
    return spatial_velocity(slopes(x_t12.T, 1000.0, SMOOTH_OFF_MS)[IND])


def main():
    os.makedirs(OUTD, exist_ok=True)
    B = os.path.join(REPO, 'data', 'biv', H)
    F = aha51.Frame(H)
    P = F.P
    E = np.loadtxt(os.path.join(B, 'biv.elem'), skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    vol = nodal_volume(P, E)
    v = np.loadtxt(os.path.join(B, 'uvc', 'v.dat')); rho = np.loadtxt(os.path.join(B, 'uvc', 'rho.dat'))
    region, third = node_labels(F, v, rho)
    W = np.load(os.path.join(B, 'ecgW_v51.npz'))['W'].astype(float)
    sys.modules.pop('common', None)
    CD = C51.biv_module('cd', '15_conductor.py', H)
    assert CD.HEART == H
    tm = CD.Template()
    ps = pd.read_csv(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '06_pilot_rerun', 'rescore', 'per_site.csv'))
    y = ps[(ps.heart == H) & (ps.network == 'net')]
    agg = y.groupby(['site', 'mode', 'noise'])[['onset_ms', 'offset_any_lead_ms', 'qrs_duration_ms', 'qrs_duration_any_lead_ms']].median()
    target = sorted(y[y.family.isin(['lv_summit', 'aortic_cusp'])].site.unique())
    contrast = sorted(y[(y.family == 'lv_free_wall') & y.depth.isin([0.1, 0.9])].site.unique())
    sites = {s['id']: s for s in json.load(open(os.path.join(B, 'sites.json')))}
    total_ml = vol.sum() / 1e3
    rows, locs = [], []
    for role, lst in (('target', target), ('contrast', contrast)):
        for s in lst:
            T = np.load(os.path.join(MAPS, s + '.T.npy')).astype(float)
            ecg = np.load(os.path.join(MAPS, s + '.ecg.npy')).astype(float)
            t = np.arange(len(ecg), dtype=float)
            a, c = agg.loc[(s, 'detected', 'plan10')], agg.loc[(s, 'detected', 'clean')]
            t_se, t_end = float(a.offset_any_lead_ms), float(T.max())
            i0, i1 = int(round(t_se)), int(np.ceil(t_end))
            assert i1 < len(t)
            S = np.where(T >= t_se)[0]
            r = {'site': s, 'role': role, 'family': sites[s]['family'], 'depth_target': sites[s]['depth_target'],
                 'onset_ms': a.onset_ms, 'surface_end_any_lead_ms': t_se, 'surface_end_precordial_ms': a.onset_ms + a.qrs_duration_ms,
                 'surface_end_any_lead_clean_ms': c.offset_any_lead_ms, 'surface_qrs_any_lead_ms': a.qrs_duration_any_lead_ms,
                 'true_end_ms': round(t_end, 2), 'hidden_window_ms': round(t_end - t_se, 2),
                 'hidden_ml': vol[S].sum() / 1e3, 'hidden_pct_myocardium': 100 * vol[S].sum() / 1e3 / total_ml, 'hidden_nodes': len(S)}
            vs = vol[S]
            r['hidden_pct_LV'] = 100 * vs[v[S] < 0.5].sum() / vs.sum()
            for th_ in ('endo', 'mid', 'epi'):
                r[f'hidden_pct_{th_}'] = 100 * vs[third[S] == th_].sum() / vs.sum()
            regs = pd.Series(vs, index=region[S]).groupby(level=0).sum().sort_values(ascending=False)
            r['hidden_regions_pct'] = '; '.join(f'{k} {100 * x / vs.sum():.0f}%' for k, x in regs.items() if 100 * x / vs.sum() >= 1)
            edges = np.arange(5 * np.floor(t_se / 5), t_end + 5, 5.0)
            hist, _ = np.histogram(T[S], bins=edges, weights=vs / 1e3)
            r['hidden_ml_per_5ms'] = '; '.join(f'{e0:.0f}-{e0 + 5:.0f}: {h_:.2f}' for e0, h_ in zip(edges[:-1], hist))
            # contributions
            dV = vm_minus_rest(t, T[S], tm)                           # (nt, nS)
            cS = dV @ W[:, S].T                                       # (nt, 12)
            regs_all = np.unique(region[S])
            cr = np.stack([dV[:, region[S] == g_] @ W[:, S[region[S] == g_]].T for g_ in regs_all])   # (nreg, nt, 12)
            assert np.abs(cr.sum(0) - cS).max() < 1e-6
            full = ecg - ecg[0]
            o = ecg - cS
            win = slice(i0, i1 + 1)
            d_cS = np.abs(cS[win] - cS[i0]).max(0)
            d_abs = np.abs(cr[:, win] - cr[:, i0:i0 + 1]).sum(0).max(0)
            d_o = np.abs(o[win] - o[i0]).max(0)
            qrs_pk = np.abs(full[:i0 + 1]).max(0)
            for j, l in enumerate(L12):
                r[f'hidden_peak_mV_{l}'] = d_cS[j]; r[f'hidden_abs_regions_peak_mV_{l}'] = d_abs[j]
                r[f'overlap_peak_mV_{l}'] = d_o[j]; r[f'qrs_peak_mV_{l}'] = qrs_pk[j]
            sv_full, sv_h, sv_o = sv(full), sv(cS), sv(o)
            thr = 0.1 * sv_full.max()
            r |= {'sv_full_peak_mV_ms': sv_full.max(), 'sv_threshold_10pct': thr, 'sv_full_max_in_window': sv_full[win].max(),
                  'sv_full_at_true_end': sv_full[int(round(t_end))], 'sv_hidden_max_in_window': sv_h[win].max(),
                  'sv_overlap_max_in_window': sv_o[win].max()}
            # summary columns
            r['hidden_peak_max_lead_mV'] = d_cS.max(); r['qrs_peak_max_lead_mV'] = qrs_pk.max()
            r['hidden_over_qrs_peak_max'] = d_cS.max() / qrs_pk.max()
            r['cancellation_ratio_median_lead'] = float(np.median(d_cS / d_abs))
            r['overlap_peak_max_lead_mV'] = d_o.max()
            rows.append(r)
            if role == 'target':
                locs.append({'site': s, 'hidden_ml': r['hidden_ml'], 'pct_LV': r['hidden_pct_LV'], 'endo_mid_epi_pct': f"{r['hidden_pct_endo']:.0f} / {r['hidden_pct_mid']:.0f} / {r['hidden_pct_epi']:.0f}",
                             'regions': '; '.join(f'{k} {100 * x / vs.sum():.0f}%' for k, x in list(regs.items())[:4])})
            print(role, s, f"t_se {t_se} end {t_end:.1f} hidden {r['hidden_ml']:.1f} mL ({r['hidden_pct_myocardium']:.1f} %) peak {d_cS.max():.3f} mV vs QRS {qrs_pk.max():.2f}; "
                  f"SV hidden {sv_h[win].max():.4f} full-in-window {sv_full[win].max():.4f} thr {thr:.4f}; canc {r['cancellation_ratio_median_lead']:.2f}; overlap {d_o.max():.3f}", flush=True)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUTD, 'hidden51.csv'), index=False, float_format='%.5g')
    pd.DataFrame(locs).to_csv(os.path.join(OUTD, 'target_locations.csv'), index=False, float_format='%.3g')
    print('total myocardium mL', round(total_ml, 1))


if __name__ == '__main__':
    main()
