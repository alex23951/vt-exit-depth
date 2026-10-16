"""Addendum 14 Oct, part 3: read-only checks that need no new activation maps (saved v5 CSVs, His beats, network files)."""
import json, os, sys
import numpy as np, pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
sys.path.insert(0, 'code/ecg_depth_criteria')
from ecg_depth_criteria import measure_beat, from_leads
OUTD = 'analysis/audit_addendum_2026-10-14/part3'
H = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
L = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
R = {}
def auc(p, n):
    p = np.asarray(p, float); n = np.asarray(n, float); p, n = p[~np.isnan(p)], n[~np.isnan(n)]
    return round(float(((p[:, None] > n[None, :]).sum() + 0.5 * (p[:, None] == n[None, :]).sum()) / (len(p) * len(n))), 3), len(p), len(n)
# 3.1 Daniels MDI AUC, in-domain variants (true and detected onset), per heart
r31 = {}
for h in H:
    d = pd.read_csv(f'analysis/v5_adopted_2026-10-13/purk_{h}_v5.csv'); d = d[d.family != 'his']
    f, dp = d.family, d.depth_target
    pos = (f.isin(['lv_summit', 'lv_vein_course'])) & (dp == 0.9)
    cusp, rvot, endo = f == 'aortic_cusp', f == 'rvot', f.isin(['lv_free_wall', 'lv_septum']) & (dp == 0.1)
    for mode in ('true', 'detected'):
        c = f'{mode}_mdi_daniels'
        r31[f'{h} {mode}'] = {
            'A_epi_perivascular90 vs cusp+RVOT+LVendo10 (positives summit90+vein90)': auc(d[pos][c], d[cusp | rvot | endo][c]),
            'B_cusps_out (vs RVOT+LVendo10)': auc(d[pos][c], d[rvot | endo][c]),
            'C_vs_RVOT_10pct_only': auc(d[pos][c], d[rvot & (dp == 0.1)][c]),
            'D_vs_LVendo10_only': auc(d[pos][c], d[endo][c]),
            'E_positives_incl_cusps (summit90+vein90+cusp) vs RVOT+LVendo10': auc(d[pos | cusp][c], d[rvot | endo][c]),
            'out_of_domain_90v10_LVfw+septum+RVfw': auc(d[f.isin(['lv_free_wall', 'lv_septum', 'rv_free_wall']) & (dp == 0.9)][c], d[f.isin(['lv_free_wall', 'lv_septum', 'rv_free_wall']) & (dp == 0.1)][c])}
    r31[f'{h} summit_dist_left_sinus_mm'] = {r.id: r.dist_left_sinus_mm for _, r in d[f == 'lv_summit'].iterrows()}
R['3.1_daniels_auc (AUC, n_pos, n_neg)'] = r31
# 3.2 His 12-leads export + normal ECG items + LBBB items
r32 = {}
def notch_slur(x, on, off, thr=0.05):
    """heuristic: count interior local maxima (>= thr mV prominence) and slope plateaus inside the dominant wave."""
    seg = x[on:off + 1]; ds = np.diff(seg)
    sgn = np.sign(ds); peaks = np.where((sgn[:-1] > 0) & (sgn[1:] <= 0))[0] + 1
    peaks = [p for p in peaks if seg[p] > thr]
    notch = 0
    for a, b in zip(peaks[:-1], peaks[1:]):
        if min(seg[a], seg[b]) - seg[a:b + 1].min() >= thr: notch += 1
    mx = np.abs(ds).max(); slur = int(np.sum((np.abs(ds[1:-1]) < 0.15 * mx) & (np.abs(seg[1:-2]) > 0.3 * np.abs(seg).max()) & (np.sign(ds[:-2]) == np.sign(ds[2:]))) >= 3)
    return notch, slur
for h in H:
    E = np.load(f'analysis/v5_adopted_2026-10-13/grid/{h}/his_ecg.npy').astype(float); T = np.load(f'analysis/v5_adopted_2026-10-13/grid/{h}/his_T.npy').astype(float)
    t = np.arange(E.shape[0])
    pd.DataFrame(np.c_[t, E], columns=['t_ms_from_His'] + L).to_csv(f'{OUTD}/his_ecg_{h}.csv', index=False, float_format='%.6g')
    pad = 60
    leads = {l: np.concatenate([np.full(pad, E[0, L.index(l)]), E[:, L.index(l)]]) for l in ('I', 'II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')}
    X = from_leads(leads); m = measure_beat(X, 1000.0, baseline_window_ms=(pad - 45.0, pad - 5.0))
    on, off = int(round(m['onset_ms'])), int(round(m['onset_ms'] + m['qrs_duration_any_lead_ms']))
    Xb = X - np.median(X[:, pad - 45:pad - 5], axis=1, keepdims=True)
    rS = {l: (round(float(Xb[L.index(l), on:off + 1].max()), 2), round(float(-Xb[L.index(l), on:off + 1].min()), 2)) for l in L}
    trans = next((l for l in ('V1', 'V2', 'V3', 'V4', 'V5', 'V6') if rS[l][0] > rS[l][1]), None)
    rpt = {l: int(np.argmax(Xb[L.index(l), on:off + 1])) for l in ('V1', 'V2', 'V5', 'V6', 'I', 'aVL')}
    ns = {l: notch_slur(Xb[L.index(l)], on, off) for l in ('V1', 'V2', 'V5', 'V6', 'I', 'aVL')}
    msk = (t >= T.min()) & (t <= T.max() + 3); ang = np.radians([0, 60, 120, -150, -30, 90]); A = np.c_[np.cos(ang), np.sin(ang)]
    ax = {nm: int(round(np.degrees(np.arctan2(*np.linalg.lstsq(A, np.array([fn(E[:, j] - E[0, j]) for j in range(6)]), rcond=None)[0][::-1]))))
          for nm, fn in (('net', lambda y: y[msk].max() + y[msk].min()), ('area', lambda y: y[msk].sum()))}
    o = {'detected_qrs_ms(precordial / any lead)': [m['qrs_duration_ms'], m['qrs_duration_any_lead_ms']], 'detected_onset_after_His_ms': m['onset_ms'] - pad,
         'axis_net_area_deg': ax, 'R_S_mV_by_lead': rS, 'transition_lead(R>S)': trans,
         'initial_polarity': m['initial_polarity'], 'q_in_I_aVL_V5_V6': {l: m['initial_polarity'][l] < 0 for l in ('I', 'aVL', 'V5', 'V6')},
         'R_peak_time_ms_from_onset': rpt, 'notch_count_and_slur_flag(heuristic)': ns,
         'QRS_peak_to_peak_limb_precordial_mV': [round(float(np.ptp(Xb[:6, on:off + 1], axis=1).max()), 2), round(float(np.ptp(Xb[6:, on:off + 1], axis=1).max()), 2)]}
    if h == '6G8DD8S5':
        qrs = m['qrs_duration_any_lead_ms']
        v12 = all(rS[l][1] > rS[l][0] and rS[l][0] < 0.25 * rS[l][1] for l in ('V1', 'V2'))
        nl = sum(1 for l, (n_, s_) in ns.items() if n_ or s_)
        o['Strauss_2011 (women: QRS>=130; QS/rS V1-V2; mid-QRS notch/slur in >=2 of V1,V2,V5,V6,I,aVL)'] = {'QRS>=130': qrs >= 130, 'QS_or_rS_V1_V2': v12, 'leads_with_notch_or_slur': nl, 'all_met': bool(qrs >= 130 and v12 and nl >= 2)}
        o['AHA_ACCF_HRS_2009 (QRS>=120; notched/slurred R in I,aVL,V5,V6; no q in I,V5,V6; R peak time V5-V6 > 60 ms)'] = {
            'QRS>=120': qrs >= 120, 'broad_notched_slurred_R_I_aVL_V5_V6': {l: bool(sum(ns[l]) > 0) for l in ('I', 'aVL', 'V5', 'V6')},
            'absent_q_I_V5_V6': all(m['initial_polarity'][l] >= 0 for l in ('I', 'V5', 'V6')), 'R_peak_time_V5_V6_gt_60': {l: rpt[l] > 60 for l in ('V5', 'V6')},
            'ST_T': 'not assessable (template has no repolarisation)'}
    r32[h] = o
R['3.2_his_beats'] = r32
# 3.3 Durrer time zero (solver clock, ms from His activation at 0)
r33 = {}
for h in H:
    B = f'data/biv/{h}/'; T = np.load(f'analysis/v5_adopted_2026-10-13/grid/{h}/his_T.npy').astype(float)
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi'); v = np.loadtxt(B + 'uvc/v.dat')
    s = json.load(open(B + 'purkinje/summary.json'))
    r33[h] = {'His_stimulus_ms': 0.0, 'first_muscle_ms': round(T.min(), 1), 'first_LV_endo_ms': round(T[lv].min(), 1), 'first_RV_endo_ms': round(T[rv].min(), 1),
              'RV_epi_breakthrough_ms': round(T[epi[v[epi] == 1]].min(), 1), 'latest_ms': round(T.max(), 1),
              'network_His_to_first_LV_site_ms (built, shortest path at 2.0 m/s)': s['his_to_lv_sites_ms'],
              'calibration_targets': 'LV Durrer sites anterior 0 / septal +2.5 / posterior +5 ms after the first (14_purkinje.py:95, 331-346); RV moderator-band end +7.5 ms after the first LV site; absolute His->first-LV-site time set by the shortest path at 2.0 m/s + 4 ms exit delay; no target for latest activation, RV breakthrough or total QRS'}
R['3.3_durrer_time_zero'] = r33
# 3.4 network geometry
r34 = {}
for h in H:
    B = f'data/biv/{h}/'; P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    net = dict(np.load(B + 'purkinje/network.npz')); nodes, edges, spd, kind = net['nodes'], net['edges'], net['edge_speed'], net['kind']
    M = len(nodes); Lg = np.linalg.norm(P[nodes[edges[:, 0]]] - P[nodes[edges[:, 1]]], axis=1)
    G = coo_matrix((np.r_[Lg, Lg] + 1e-9, (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])), shape=(M, M)).tocsr()
    his = int(net['his']); dl = dijkstra(G, indices=his)
    pm = net['pmj']; reach = np.isfinite(dl[pm])
    eu = np.linalg.norm(P[nodes[pm]] - P[nodes[his]], axis=1)
    tort = dl[pm][reach] / eu[reach]
    # distal tortuosity: from each root (proximal-distal joint) to its junctions
    dist_e = np.char.startswith(kind[edges[:, 0]], 'distal') & np.char.startswith(kind[edges[:, 1]], 'distal')
    Gd = coo_matrix((np.r_[Lg[dist_e], Lg[dist_e]] + 1e-9, (np.r_[edges[dist_e, 0], edges[dist_e, 1]], np.r_[edges[dist_e, 1], edges[dist_e, 0]])), shape=(M, M)).tocsr()
    roots = np.unique(np.concatenate([edges[~np.char.equal(kind[edges[:, 0]], kind[edges[:, 1]]), 0], edges[~np.char.equal(kind[edges[:, 0]], kind[edges[:, 1]]), 1]]))
    roots = roots[np.char.startswith(kind[roots], 'distal')]
    S = M
    Gs = coo_matrix((np.r_[Lg[dist_e], Lg[dist_e], np.full(len(roots), 1e-9)] + 1e-9, (np.r_[edges[dist_e, 0], edges[dist_e, 1], np.full(len(roots), S)], np.r_[edges[dist_e, 1], edges[dist_e, 0], roots])), shape=(M + 1, M + 1)).tocsr()
    dd, pred = dijkstra(Gs, indices=S, return_predecessors=True)
    src = np.full(M + 1, -1)
    def root_of(n):
        path = []
        while n >= 0 and n != S and src[n] < 0 and pred[n] != S and pred[n] >= 0:
            path.append(n); n = pred[n]
        r = src[n] if (n >= 0 and src[n] >= 0) else (n if (n >= 0 and pred[n] == S) else -1)
        for q in path: src[q] = r
        if n >= 0 and n != S and src[n] < 0: src[n] = r
        return r
    for n in pm: root_of(int(n))
    src = src[:M]; dd = dd[:M]
    ok = np.isfinite(dd[pm]) & (src[pm] >= 0)
    eud = np.linalg.norm(P[nodes[pm[ok]]] - P[nodes[src[pm[ok]]]], axis=1)
    td = dd[pm[ok]] / np.maximum(eud, 1e-6)
    r34[h] = {'distal_speed': 'per edge: edge length (straight segment between adjacent endocardial surface nodes, ~1 mm) / 2.0 mm/ms; the path follows the grown tree, not a straight line',
              'junction_depth_mm': 0.0, 'junctions_on_endocardial_surface': True,
              'His_to_junction_network_path / straight_line (median, p10-p90)': [round(float(np.median(tort)), 2), np.percentile(tort, [10, 90]).round(2).tolist()],
              'root_to_junction_distal_path / straight_line (median, p10-p90) [junctions > 5 mm from root]': [round(float(np.median(td[eud > 5])), 2), np.percentile(td[eud > 5], [10, 90]).round(2).tolist()],
              'effective_straight_line_distal_speed_m_s (2.0 / tortuosity, median)': round(2.0 / float(np.median(td[eud > 5])), 2),
              'junctions_reachable_from_His': f'{int(reach.sum())}/{len(pm)}'}
R['3.4_network'] = r34
P14 = {'v_mm_per_ms 2.0': 'distal (and LBB, anterior division) speed; cited Sahli Costabal 2016, Berg 2023, Choi 2023 (Choi: rabbit insulated fibres > 2 m/s)',
       'd_ant_ms 4.0': 'Purkinje->muscle; cited Berg 2023 (3-5 ms), Choi 2023 (3.4 +- 0.8 / 7.8 +- 2.4 ms, rabbit)',
       'd_ret_ms 2.0': 'muscle->Purkinje; ASSUMPTION, not sourced (docstring)', 'pmj_per_cm2 15.0': 'cited Bayer 2025 (not in its abstract)',
       'branch_mm 8.0, branch_sd_mm sqrt(0.4), angle_rad 0.15, repulsion 0.1, seg_mm 1.0': 'cited Sahli Costabal 2016 fractal-tree parameters (not in its abstract)',
       'z_max 0.90': 'v3 rule, "like the frozen fast layer" (frozen layer 10-90 % apex-base); not sourced',
       'rv_septum_z_max 0.35, mb_z 0.35': 'RBB unbranched to the apex (Sahli Costabal 2016), Bayer 2025 (no junctions on the mid-upper RV septum); level 0.35 not sourced',
       'lbb_drop_z 0.10': 'LBB ~10 mm before branching (Elizari 2017 for the origin); 0.10 of z not sourced', 'max_gen 40, seed 20261007, bud_mm 10.0, rv_apex_z 0.12': 'implementation choices',
       'divisions (phi, z) waypoints': 'Durrer 1970 three earliest LV areas (60, 0.80), (0, 0.50), (-60, 0.33) then onward to papillary / apex: UVC translation is an assumption',
       'durrer_offset_ms 0 / 2.5 / 5; rv_after_lv_ms 7.5': 'Durrer 1970 (0-5 ms between the three sites; RV 5-10 ms after LV); the values within the ranges are choices -> proximal speeds tuned',
       'stim_bin_ms 0.25, bridge_mm 6.0, v_bridge 0.4, couple_tol_ms 1.0, max_pass 4': 'openCARP coupling / unused bridges (v3 only)',
       'lbbb_cut_hearts [6G8DD8S5]': 'Upadhyay 2019 (proximal LBB block in 64 % of LBBB-pattern patients); Alex 9 Oct',
       'network_version v3; durrer_lv_endo_pct 95, durrer_window_ms 30, v_distal_max 12': 'v4 only (rejected)',
       'graph scale k 1.0685 / 1.0658 / 1.0682': 'fitted (graph vs openCARP no-layer fields, v3 speeds)', 'stimulus ball 1.5 mm': 'choice (12_eikonal.py:81 / v5_grid.py:157)'}
R['3.4_parameters_14_purkinje'] = P14
# 3.5 RVOT beats (from v5 CSV) + heights below PV (audit a04) + His/first-LV from audit a03b (septal 10 % only)
a4 = json.load(open('analysis/audit_2026-10-13/a04_anatomy.json')); a3b = json.load(open('analysis/audit_2026-10-13/a03b_paced_exits.json'))
r35 = {}
for h in H:
    d = pd.read_csv(f'analysis/v5_adopted_2026-10-13/purk_{h}_v5.csv'); d = d[d.family == 'rvot']
    rows = []
    for _, s in d.iterrows():
        rows.append({'id': s.id, 'stim_to_pseudo_delta_end(rapid onset)_ms': s.true_pseudo_delta_ms, 'stim_to_largest_deflection_ms': round(s.true_mdi_daniels * s.true_qrs_duration_any_lead_ms, 1),
                     'stim_to_QRS_end_true(last activation)_ms': s.true_qrs_duration_ms, 'stim_to_detected_onset_ms(clean)': s.detected_onset_ms,
                     'stim_to_detected_QRS_end_ms(clean)': round(s.detected_onset_ms + s.detected_qrs_duration_any_lead_ms, 1),
                     'height_vs_PV_plane_mm(- = below)': a4[h]['sites_outflow_summit_vein'].get(s.id, {}).get('height_vs_PV_plane_mm'),
                     'dist_PV_rim_mm': a4[h]['sites_outflow_summit_vein'].get(s.id, {}).get('dist_PV_rim_mm')})
    r35[h] = {'sites': rows, 'septal_10pct_first_His_ms (audit a03b)': a3b[f'{h}_rvot_septal_z_d10']['his_ms'],
              'septal_10pct_first_network_entry_ms': a3b[f'{h}_rvot_septal_z_d10']['first_network_entry_ms'],
              'path_to_LV': 'rvot_anatomy_2026-10-12: outflow sleeve continuous with LV myocardium in all three meshes (no cavity or aortic-root gap); septal RVOT myocardium-only time to LV endocardium 34-35 / 20-21 / 25-27 ms, path 1.05-1.1 x straight line'}
R['3.5_rvot'] = r35
R['3.6_conductivities'] = 'see analysis/audit_2026-10-13/a08_ecg_conductivity.txt (per heart gi/ge x 3 directions, calibration and cb); blood 0.7 S/m = tag 101 (voxel enclosure; 258.5 / 148.5 / 208.0 mL = 70 / 56 / 70 % of the cavities), cited Geddes & Baker 1967 and Keller 2010 (15_conductor.py:15); graph vs openCARP on v5 sites: impossible (no openCARP v5 runs); v3 comparison and the direction-dependent speed error in audit F01 / a03'
R['3.7_v5_commit'] = 'none: v5 code and outputs are uncommitted; no git remote exists (nothing pushed). Last commit 47808c6 (10 Oct 12:20).'
json.dump(R, open(f'{OUTD}/part3.json', 'w'), indent=1, default=str)
print(json.dumps(R, indent=1, default=str))
