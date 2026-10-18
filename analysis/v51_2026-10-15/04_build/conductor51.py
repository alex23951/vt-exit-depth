"""v5.1 volume conductor (v5.1 brief Step 4.5, C1-C8; audit F11-F13), before the lead fields.

C1-C2 Conductivities from the v5.1 target speeds (params/v51_speeds.json), never by rescaling the v5 cb values: fibre
      sigma_i 0.174, sigma_e 0.625 S/m (Clerc 1976); direction d: sigma_x,d = sigma_x,fibre (v_d / 0.60)^2 (equal
      anisotropy). Blood 0.7, torso 0.2 S/m. ECG source: sigma_i (Alex, 18 Oct 2026 13:22:54 UTC, "Intracellular").
C3    Check values (S/m, 4 decimals): Y5HYEDL4 sheet 0.0626 / 0.2250, normal 0.1114 / 0.4000; HF sheet 0.0327 / 0.1174,
      normal 0.0546 / 0.1960. The code uses full precision.
C5    sigma_m,d / sigma_m,fibre = (v_d / 0.60)^2 to 1e-6 (sigma_m = sigma_i sigma_e / (sigma_i + sigma_e)).
C6    Closed LV and RV cavity surfaces in torso coordinates: the endocardial surface (surfaces/<lv|rv>_endo.surf) plus a fan
      cap from the centroid of each boundary loop (the mitral / aortic, tricuspid / pulmonary rings), as the audit's
      a04_anatomy.py cavity(). Gate: enclosed volume within +-1 % of LV 172.0 / 157.8 / 172.8 and RV 197.9 / 107.2 /
      122.5 mL; each edge in 2 triangles, consistently oriented (reported: edges in 4 triangles, pinch points).
C7    Blood = every torso element (tag 100) whose centroid is inside a cavity surface: majority of three axis-parallel
      ray-parity tests (+x, +y, +z), only elements in the cavity's bounding box, in chunks. New tag 101.
C8    Gates per ventricle: blood volume within +-2 % of the cavity volume; torso (0.2 S/m) volume inside the surface
      < 1 % of it and no blood volume outside (both from one random interior point per element); >= 95 % of the
      endocardial faces border blood; blood stops at the valve planes (blood centroids beyond each cap plane, within
      the ring).
Files: data/biv/<H>/torso/full_nofast_blood_v51.elem (+ .pts link; .lon written by stage 'lon' with the v5.1 fibres
      rotated into the torso frame); params/v51_conductivities.json; analysis/v51_2026-10-15/04_build/conductor51_<H>.json.
Usage (repo root, venv): python -B .../conductor51.py tensors
                         HEART=<H> python -B .../conductor51.py blood     (C6-C8, about 2-4 min, < 3 GB)
                         HEART=<H> python -B .../conductor51.py lon
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v51_speeds.json')))['hearts']
SIG_I, SIG_E, V_REF, G_BLOOD, G_TORSO, TAG_BLOOD, TAG_TORSO = 0.174, 0.625, 0.60, 0.7, 0.2, 101, 100
C3 = {'Y5HYEDL4': {'sheet': (0.0626, 0.2250), 'normal': (0.1114, 0.4000)},
      '6G8DD8S5': {'sheet': (0.0327, 0.1174), 'normal': (0.0546, 0.1960)}}
C3['7D98EVAR'] = C3['6G8DD8S5']
CAVITY_ML = {'Y5HYEDL4': (172.0, 197.9), '6G8DD8S5': (157.8, 107.2), '7D98EVAR': (172.8, 122.5)}
CELL_MM = 1.0


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, *p)


def table(path, cols, dtype):
    return pd.read_csv(path, sep=' ', header=None, skiprows=1, usecols=cols, dtype=dtype).to_numpy()


# ------------------------------------------------------------------ C1-C5
def sigma(h):
    sp = SPEEDS[h]
    return {a: {'gi': SIG_I * (sp[a] / V_REF) ** 2, 'ge': SIG_E * (sp[a] / V_REF) ** 2} for a in ('fibre', 'sheet', 'normal')}


def tensors():
    out = {'version': 'v51-conductivities-1', 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'),
           'rule': 'sigma_x,d = sigma_x,fibre (v_d / 0.60)^2, fibre sigma_i 0.174, sigma_e 0.625 S/m (Clerc 1976); equal anisotropy',
           'blood_S_m': G_BLOOD, 'torso_S_m': G_TORSO, 'ecg_source': 'sigma_i (Alex, 18 Oct 2026 13:22:54 UTC)', 'hearts': {}}
    for h in SPEEDS:
        s = sigma(h)
        for a, (gi, ge) in C3[h].items():
            assert (round(s[a]['gi'], 4), round(s[a]['ge'], 4)) == (gi, ge), (h, a, s[a])
        sm = {a: s[a]['gi'] * s[a]['ge'] / (s[a]['gi'] + s[a]['ge']) for a in s}
        c5 = {a: abs(sm[a] / sm['fibre'] - (SPEEDS[h][a] / V_REF) ** 2) for a in s}
        assert max(c5.values()) <= 1e-6, c5
        out['hearts'][h] = {'speeds_m_s': SPEEDS[h], 'sigma_S_m': s, 'sigma_m_S_m': sm, 'C5_max_abs_error': max(c5.values())}
    json.dump(out, open(os.path.join(REPO, 'params', 'v51_conductivities.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ C6
def cavity_surface(P, Eh, name, h):
    """Endocardial faces oriented away from the myocardium owner tet... -> closed triangle set with fan caps."""
    F = table(hd(h, 'surfaces', f'{name}.surf'), [1, 2, 3], np.int64)
    N = len(P)
    fk = lambda T: np.sort(T, axis=1) @ np.array([N * N, N, 1], dtype=np.int64)
    faces = np.concatenate([Eh[:, [0, 1, 2]], Eh[:, [0, 1, 3]], Eh[:, [0, 2, 3]], Eh[:, [1, 2, 3]]])
    other = np.concatenate([Eh[:, 3], Eh[:, 2], Eh[:, 1], Eh[:, 0]])
    k = fk(faces); o = np.argsort(k); k = k[o]
    pos = np.searchsorted(k, fk(F))
    assert np.array_equal(k[pos], fk(F)), 'a surface face is not a tet face'
    fourth = other[o[pos]]
    c = P[F].mean(1); nrm = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    flip = np.sum(nrm * (P[fourth] - c), 1) > 0                  # normals point into the cavity (away from the myocardium)
    F[flip] = F[flip][:, [0, 2, 1]]
    ed = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    key = np.minimum(ed[:, 0], ed[:, 1]) * N + np.maximum(ed[:, 0], ed[:, 1])
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    be = ed[cnt[inv.ravel()] == 1]
    nb_all = np.unique(be); idx = {n: i for i, n in enumerate(nb_all)}
    A = coo_matrix((np.ones(len(be)), ([idx[a] for a in be[:, 0]], [idx[b] for b in be[:, 1]])), shape=(len(nb_all),) * 2)
    nl, lab = connected_components(A, directed=False)
    caps, loops = [], []
    for L in range(nl):
        nb = nb_all[lab == L]
        sel = np.isin(be[:, 0], nb)
        C = P[nb].mean(0)
        tri = np.stack([P[be[sel, 1]], P[be[sel, 0]], np.repeat(C[None], sel.sum(), 0)], 1)
        caps.append(tri)
        nrm_c = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]).sum(0)
        rims = {r: int(np.isin(nb, np.loadtxt(hd(h, 'surfaces', f'{r}.vtx'), skiprows=2, dtype=np.int64)).sum()) for r in ('mv_rim', 'av_rim', 'tv_rim', 'pv_rim')}
        loops.append({'nodes': int(len(nb)), 'rim_overlap_nodes': {r: v for r, v in rims.items() if v}, 'centroid': C,
                      'normal': nrm_c / np.linalg.norm(nrm_c), 'radius_mm': float(np.linalg.norm(P[nb] - C, axis=1).max()),
                      'planarity_rms_mm': float(np.sqrt(np.mean(((P[nb] - C) @ (nrm_c / np.linalg.norm(nrm_c))) ** 2)))})
    T = np.concatenate([P[F]] + caps)
    # closure: every undirected edge used by an even number of triangles, each direction as often as its reverse
    V = np.unique(T.reshape(-1, 3), axis=0, return_inverse=True)[1].ravel().reshape(-1, 3)
    de = np.concatenate([V[:, [0, 1]], V[:, [1, 2]], V[:, [2, 0]]])
    M = V.max() + 1
    dk = de[:, 0] * M + de[:, 1]; rk = de[:, 1] * M + de[:, 0]
    du, dc = np.unique(dk, return_counts=True)
    rc = np.zeros(len(du), int); ru, rcount = np.unique(rk, return_counts=True)
    m = np.isin(du, ru); rc[m] = rcount[np.searchsorted(ru, du[m])]
    undirected = np.unique(np.minimum(dk, rk), return_counts=True)[1]
    vol = float(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6)
    info = {'faces_endo': int(len(F)), 'cap_triangles': int(sum(len(c_) for c_ in caps)), 'boundary_loops': len(loops),
            'edges_in_2_triangles': int((undirected == 2).sum()), 'edges_in_4_triangles': int((undirected == 4).sum()),
            'edges_other_counts': int(((undirected != 2) & (undirected != 4)).sum()),
            'orientation_consistent': bool(np.array_equal(dc, rc)), 'volume_ml': abs(vol) / 1e3,
            'loops': [{k_: (v_.tolist() if isinstance(v_, np.ndarray) else v_) for k_, v_ in l.items()} for l in loops]}
    return T, info, loops, F


# ------------------------------------------------------------------ C7: ray parity
def parity(T, Q, axis, cell=CELL_MM):
    """Number of crossings (mod 2) of rays from points Q in +axis with the triangles T (m, 3, 3)."""
    a1, a2 = [k for k in range(3) if k != axis]
    tu, tv, tw = T[:, :, a1], T[:, :, a2], T[:, :, axis]
    lo = np.array([min(tu.min(), Q[:, a1].min()), min(tv.min(), Q[:, a2].min())]) - 1
    ci = lambda u, v: (np.floor((u - lo[0]) / cell).astype(np.int64), np.floor((v - lo[1]) / cell).astype(np.int64))
    nx = int(np.ceil((max(tu.max(), Q[:, a1].max()) - lo[0]) / cell)) + 2
    u0, v0 = ci(tu.min(1), tv.min(1)); u1, v1 = ci(tu.max(1), tv.max(1))
    reps = (u1 - u0 + 1) * (v1 - v0 + 1)
    tid = np.repeat(np.arange(len(T)), reps)
    off = np.arange(reps.sum()) - np.repeat(np.cumsum(reps) - reps, reps)
    w = np.repeat(u1 - u0 + 1, reps)
    cu, cv = np.repeat(u0, reps) + off % w, np.repeat(v0, reps) + off // w
    ck = cv * nx + cu
    o = np.argsort(ck, kind='stable'); ck, tid = ck[o], tid[o]
    qu, qv = ci(Q[:, a1], Q[:, a2]); qk = qv * nx + qu
    start = np.searchsorted(ck, qk, 'left'); stop = np.searchsorted(ck, qk, 'right')
    cnt = stop - start
    cross = np.zeros(len(Q), np.int64)
    for c0 in range(0, len(Q), 100000):
        sl = slice(c0, c0 + 100000)
        n_ = cnt[sl]
        if n_.sum() == 0:
            continue
        qi = np.repeat(np.arange(c0, c0 + len(n_)), n_)
        ti = tid[np.repeat(start[sl], n_) + (np.arange(n_.sum()) - np.repeat(np.cumsum(n_) - n_, n_))]
        pu, pv, pw = Q[qi, a1], Q[qi, a2], Q[qi, axis]
        x0, y0, x1, y1, x2, y2 = tu[ti, 0], tv[ti, 0], tu[ti, 1], tv[ti, 1], tu[ti, 2], tv[ti, 2]
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        ok = d != 0
        with np.errstate(divide='ignore', invalid='ignore'):
            l0 = ((y1 - y2) * (pu - x2) + (x2 - x1) * (pv - y2)) / d
            l1 = ((y2 - y0) * (pu - x2) + (x0 - x2) * (pv - y2)) / d
        l2 = 1 - l0 - l1
        ins = ok & (l0 >= 0) & (l1 >= 0) & (l2 > 0)                # half-open on one edge: shared edges count once
        zc = l0 * tw[ti, 0] + l1 * tw[ti, 1] + l2 * tw[ti, 2]
        hit = ins & (zc > pw)
        np.add.at(cross, qi[hit], 1)
    return cross % 2


def inside(T, Q):
    votes = sum(parity(T, Q, ax) for ax in range(3))
    return votes >= 2, int(((votes == 1) | (votes == 2)).sum())


# ------------------------------------------------------------------ C6-C8 driver
def blood():
    h = os.environ['HEART']
    t0 = time.time()
    tor = hd(h, 'torso')
    P = table(os.path.join(tor, 'full.pts'), [0, 1, 2], np.float64) / 1e3
    El = table(os.path.join(tor, 'full_nofast.elem'), [1, 2, 3, 4, 5], np.int64)
    E, tag = El[:, :4], El[:, 4]
    nh = int(open(hd(h, 'bivF.pts')).readline())
    Eh = E[tag == 1]
    assert len(Eh) == int(open(hd(h, 'bivF.elem')).readline()) and Eh.max() < nh
    res = {'heart': h}
    tor_idx = np.where(tag == TAG_TORSO)[0]
    newtag = tag.copy()
    cen_all = np.empty((len(tor_idx), 3))
    for c0 in range(0, len(tor_idx), 1_000_000):
        cen_all[c0:c0 + 1_000_000] = P[E[tor_idx[c0:c0 + 1_000_000]]].mean(1)

    def vol_el(idx):
        out = np.empty(len(idx))
        for c0 in range(0, len(idx), 1_000_000):
            x = P[E[idx[c0:c0 + 1_000_000]]]
            out[c0:c0 + 1_000_000] = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
        return out
    for side, name, ref in (('LV', 'lv_endo', CAVITY_ML[h][0]), ('RV', 'rv_endo', CAVITY_ML[h][1])):
        T, info, loops, F = cavity_surface(P[:nh], Eh, name, h)
        info['audit_volume_ml'] = ref
        info['volume_within_1pct'] = bool(abs(info['volume_ml'] / ref - 1) <= 0.01)
        info['C6_pass_as_written'] = bool(info['volume_within_1pct'] and info['edges_in_4_triangles'] == 0 and info['edges_other_counts'] == 0 and info['orientation_consistent'])
        lo, hi = T.reshape(-1, 3).min(0) - 0.5, T.reshape(-1, 3).max(0) + 0.5
        box = np.all((cen_all >= lo) & (cen_all <= hi), axis=1)
        cand = tor_idx[box]
        ins, split = inside(T, cen_all[box])
        bl = cand[ins]
        assert np.all(newtag[bl] == TAG_TORSO), 'an element is in both cavities'
        newtag[bl] = TAG_BLOOD
        vc = vol_el(cand)
        bvol = float(vc[ins].sum() / 1e3)
        # sampled partial volumes: one random interior point per element of the box (torso and blood)
        rng = np.random.default_rng(0)
        sp = np.empty((len(cand), 3))
        for c0 in range(0, len(cand), 1_000_000):
            w = rng.dirichlet(np.ones(4), len(cand[c0:c0 + 1_000_000]))
            sp[c0:c0 + 1_000_000] = np.einsum('ek,ekj->ej', w, P[E[cand[c0:c0 + 1_000_000]]])
        ins_s, _ = inside(T, sp)
        torso_inside = float(vc[(~ins) & ins_s].sum() / 1e3)
        blood_outside = float(vc[ins & (~ins_s)].sum() / 1e3)
        # endocardial faces bordered by blood: the torso tet that shares each endocardial face
        cand3 = tor_idx[(E[tor_idx] < nh).sum(1) >= 3]
        N = len(P)
        fk = lambda Tf: np.sort(Tf, axis=1) @ np.array([N * N, N, 1], dtype=np.int64)
        fs = np.concatenate([E[cand3][:, [0, 1, 2]], E[cand3][:, [0, 1, 3]], E[cand3][:, [0, 2, 3]], E[cand3][:, [1, 2, 3]]])
        owner = np.tile(cand3, 4)
        kk = fk(fs); o = np.argsort(kk); kk, owner = kk[o], owner[o]
        q = fk(F); pos = np.minimum(np.searchsorted(kk, q), len(kk) - 1); found = kk[pos] == q
        endo_blood = float(np.mean(newtag[owner[pos[found]]] == TAG_BLOOD)) if found.any() else 0.0
        # blood beyond the valve planes (cap planes), within each ring
        beyond = []
        bc = P[E[bl]].mean(1)
        for l in loops:
            d = -(bc - l['centroid']) @ l['normal']                      # cap normals point into the cavity: d > 0 is beyond the valve plane
            r = np.linalg.norm((bc - l['centroid']) - np.outer(d, l['normal']), axis=1)
            beyond.append({'rims': l['rim_overlap_nodes'], 'blood_centroids_beyond_plane_within_ring': int(((d > 0.5) & (r < l['radius_mm'])).sum()),
                           'ring_planarity_rms_mm': round(l['planarity_rms_mm'], 2)})
        res[side] = {'C6': info, 'C7': {'candidates_in_box': int(len(cand)), 'blood_elements': int(len(bl)), 'split_votes': split},
                     'C8': {'blood_ml': round(bvol, 2), 'cavity_ml': round(info['volume_ml'], 2), 'blood_over_cavity': round(bvol / info['volume_ml'], 4),
                            'blood_within_2pct': bool(abs(bvol / info['volume_ml'] - 1) <= 0.02),
                            'torso_volume_inside_ml_sampled': round(torso_inside, 3), 'torso_inside_pct_of_cavity': round(100 * torso_inside / info['volume_ml'], 3),
                            'torso_inside_lt_1pct': bool(torso_inside / info['volume_ml'] < 0.01),
                            'blood_volume_outside_ml_sampled': round(blood_outside, 3),
                            'endocardial_faces_with_torso_neighbour': int(found.sum()), 'endocardial_faces': int(len(F)),
                            'endocardial_faces_bordering_blood_frac': round(endo_blood, 4), 'endo_ge_95pct': bool(endo_blood >= 0.95),
                            'valve_planes': beyond,
                            'element_edge_mm_median_in_blood': round(float(np.median(np.linalg.norm(P[E[bl[:200000], 0]] - P[E[bl[:200000], 1]], axis=1))), 3)}}
        print(side, json.dumps({'C6': {k_: v_ for k_, v_ in info.items() if k_ != 'loops'}, 'C7': res[side]['C7'], 'C8': res[side]['C8']}, default=str), flush=True)
    out = os.path.join(tor, 'full_nofast_blood_v51')
    with open(out + '.elem', 'w') as f:
        f.write(f'{len(E)}\n')
        pd.DataFrame({'t': 'Tt', 'a': E[:, 0], 'b': E[:, 1], 'c': E[:, 2], 'd': E[:, 3], 'g': newtag}).to_csv(f, sep=' ', header=False, index=False)
    if not os.path.lexists(out + '.pts'):
        os.symlink('full.pts', out + '.pts')
    res['written'] = out + '.elem'
    res['wall_s'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(HERE, f'conductor51_{h}.json'), 'w'), indent=1, default=str)


def lon():
    """v5.1 fibres (data/biv/<H>/fibres_v51/bivF_v51.lon) rotated into the torso frame for the heart elements; torso rows
    copied from full.lon (as v5_adopted.py mesh())."""
    h = os.environ['HEART']
    R = np.loadtxt(os.path.join(REPO, 'data', 'torso', 'atria', f'{h}_to_g001_rigid.txt'))[:3]
    L = pd.read_csv(hd(h, 'fibres_v51', 'bivF_v51.lon'), sep=r'\s+', skiprows=1, header=None).to_numpy()
    Lt = np.hstack([L[:, :3] @ R.T, L[:, 3:] @ R.T])
    nh = int(open(hd(h, 'torso', 'heart.elem')).readline())
    assert nh == len(Lt)
    src = hd(h, 'torso', 'full.lon')
    out = hd(h, 'torso', 'full_nofast_blood_v51.lon')
    with open(src) as fi, open(out, 'w') as fo:
        fo.write(fi.readline())
        np.savetxt(fo, Lt, fmt='%.5f')
        for _ in range(nh):
            fi.readline()
        for line in fi:
            fo.write(line)
    print(json.dumps({'heart': h, 'heart_elements': nh, 'written': out}))


# ------------------------------------------------------------------ C9: lead fields and ECG weights
OPTS = os.path.join(REPO, 'analysis', 'axis_2026-10-10', 'ellip_amg_light.opts')
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def biv_module(name, fname, h):
    """sims/biv_model modules read HEART at import; sims/biv_model must be first on sys.path (site-packages 'common')."""
    import importlib.util
    os.environ['HEART'] = h
    B = os.path.join(REPO, 'sims', 'biv_model')
    if sys.path[0] != B:
        sys.path.insert(0, B)
    spec = importlib.util.spec_from_file_location(name, os.path.join(B, fname))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def lf_dir(h):
    return os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'leadfield_v51')


def leadfield(np_=2, min_mb=900):
    """As 15_conductor.py leadfield() (three openCARP runs of <= 3 leads, light AMG options, memory watchdog, aVR / aVL /
    aVF from I and II), with the v5.1 mesh (full_nofast_blood_v51) and v5.1 conductivities; heart tag 1, torso 100 at
    0.2 S/m, blood 101 at 0.7 S/m."""
    import signal
    import subprocess
    h = os.environ['HEART']
    CD = biv_module('cd', '15_conductor.py', h)
    from carputils.leadfield import leadfield_setup
    sg = json.load(open(os.path.join(REPO, 'params', 'v51_conductivities.json')))['hearts'][h]['sigma_S_m']
    rid = lf_dir(h)
    os.makedirs(os.path.join(rid, 'POSTPROC_DIR'), exist_ok=True)
    vm = CD.small_vm(rid)
    g = ['-num_gregions', 3, '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', sg['fibre']['gi'], '-gregion[0].g_el', sg['fibre']['ge'],
         '-gregion[0].g_it', sg['sheet']['gi'], '-gregion[0].g_et', sg['sheet']['ge'],
         '-gregion[0].g_in', sg['normal']['gi'], '-gregion[0].g_en', sg['normal']['ge'],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', TAG_TORSO, '-gregion[2].num_IDs', 1, '-gregion[2].ID[0]', TAG_BLOOD]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', G_TORSO, f'-gregion[1].g_e{k}', G_TORSO, f'-gregion[2].g_i{k}', G_BLOOD, f'-gregion[2].g_e{k}', G_BLOOD]
    phys = ['-num_phys_regions', 2, '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', 1, '-phys_region[0].ID[0]', 1,
            '-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', 3, '-phys_region[1].ID[0]', 1, '-phys_region[1].ID[1]', TAG_TORSO,
            '-phys_region[1].ID[2]', TAG_BLOOD]
    stim, elec, opts = leadfield_setup(12, hd(h, 'torso', 'electrodes'), lf_vmfile=vm, ecg_timedt=10)
    env = dict(os.environ, PATH='/usr/local/lib/opencarp/lib/petsc/bin:' + os.environ.get('PATH', ''))
    res = {'run': rid, 'mesh': hd(h, 'torso', 'full_nofast_blood_v51'), 'sigma_S_m': sg, 'g_blood': G_BLOOD, 'g_torso': G_TORSO, 'np': np_, 'parts': {}}
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        sub = os.path.join(rid, part)
        if all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            res['parts'][part] = 'exists'
            continue
        os.makedirs(sub, exist_ok=True)
        cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', hd(h, 'torso', 'full_nofast_blood_v51'), '-simID', sub,
               '-bidomain', 0, '-dt', 10, '-tend', 10, '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek',
               '-imp_region[0].num_IDs', 1, '-imp_region[0].ID[0]', 1] + g + phys \
            + CD.lead_subset(stim, elec, names) + opts + ['-ellip_options_file', OPTS]
        t0, peak, killed = time.time(), 0, False
        with open(os.path.join(sub, 'openCARP.log'), 'w') as log:
            p = subprocess.Popen([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            while p.poll() is None:
                mi = dict(l.split(':') for l in open('/proc/meminfo').read().splitlines() if ':' in l)
                av = int(mi['MemAvailable'].split()[0]) // 1024; peak = max(peak, int(mi['MemTotal'].split()[0]) // 1024 - av)
                if av < min_mb:
                    os.killpg(p.pid, signal.SIGKILL); killed = True
                    break
                time.sleep(2)
            p.wait()
        r = {'wall_s': round(time.time() - t0), 'peak_used_mb': peak, 'watchdog_killed': killed, 'returncode': p.returncode}
        res['parts'][part] = r
        print(part, r, flush=True)
        if killed or p.returncode or not all(os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{n}.igb')) for n in names):
            json.dump(res, open(os.path.join(HERE, f'leadfield51_{h}.json'), 'w'), indent=1, default=str)
            raise RuntimeError(json.dumps(res, default=str))
    pp = os.path.join(rid, 'POSTPROC_DIR')
    Z = {}
    for part, names in (('limb', ['I', 'II', 'III']), ('v13', ['V1', 'V2', 'V3']), ('v46', ['V4', 'V5', 'V6'])):
        for n in names:
            b = open(os.path.join(rid, part, 'POSTPROC_DIR', f'LF_{n}.igb'), 'rb').read()
            hdr, Z[n] = b[:1024], np.frombuffer(b[1024:], dtype='<f4').copy()
            open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(b)
            e = os.path.join(rid, part, 'POSTPROC_DIR', f'ECG_{n}.dat')
            if os.path.exists(e):
                open(os.path.join(pp, f'ECG_{n}.dat'), 'w').write(open(e).read())
    for n, z in (('aVR', -(Z['I'] + Z['II']) / 2), ('aVL', Z['I'] - Z['II'] / 2), ('aVF', Z['II'] - Z['I'] / 2)):
        open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(hdr + z.astype('<f4').tobytes())
    res['lf_files'] = sorted(f for f in os.listdir(pp) if f.startswith('LF_'))
    json.dump(res, open(os.path.join(HERE, f'leadfield51_{h}.json'), 'w'), indent=1, default=str)
    print(json.dumps(res, default=str), flush=True)


def weights():
    """C9: weights with sigma_m (c = -1) must reproduce openCARP's own ECG of the lead-field runs (first 10 ms of the
    heart's template beat) within 0.0002 mV in the 9 computed leads; then the v5.1 weights are written with sigma_i
    (Alex 13:22:54 UTC) to data/biv/<H>/ecgW_v51.npz."""
    h = os.environ['HEART']
    FE = biv_module('fe', '13_fast_ecg.py', h)
    sg = json.load(open(os.path.join(REPO, 'params', 'v51_conductivities.json')))['hearts'][h]['sigma_S_m']
    pair = [(sg[a]['gi'], sg[a]['ge']) for a in ('fibre', 'sheet', 'normal')]
    G = {'myo': pair, 'fast': pair}
    mesh = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'acceptance_c', 'mesh', 'biv51')   # biv.pts, bivF.elem, v5.1 fibres
    pp = os.path.join(lf_dir(h), 'POSTPROC_DIR')
    vm = FE.igb(os.path.join(lf_dir(h), 'vm_first10ms.igb'))
    out = {'heart': h, 'mesh': mesh, 'lf_dir': pp}
    Wm = FE.weights(mesh, pp, G, 'm', -1.0, True)
    mine = FE.project(Wm, vm)
    comp = {}
    for i, l in enumerate(LEADS):
        f = os.path.join(pp, f'ECG_{l}.dat')
        if os.path.exists(f):
            d = np.loadtxt(f)                          # columns t (ms), ECG (mV); output every ecg_timedt = 10 ms
            k = np.rint(d[:, 0] / 1.0).astype(int)     # Vm frames are 1 ms apart (inc_t 1), frame 0 at t = 0
            ok = k < len(mine)
            comp[l] = {'max_abs_err_mV': float(np.abs(mine[k[ok], i] - d[ok, 1]).max()), 'ref_peak_mV': float(np.abs(d[ok, 1]).max()),
                       'times_ms': d[ok, 0].tolist()}
    err = max(c['max_abs_err_mV'] for c in comp.values())
    out['C9_sigma_m_vs_openCARP'] = comp
    out['C9_max_abs_err_mV'] = err
    out['C9_pass_0.0002mV'] = bool(err <= 0.0002)
    Wi = FE.weights(mesh, pp, G, 'i', -1.0, True)
    ratio = float(np.median(np.abs(Wi[np.abs(Wm) > 1e-12] / Wm[np.abs(Wm) > 1e-12])))
    out['sigma_i_over_sigma_m_weight_ratio_median'] = ratio
    wf = hd(h, 'ecgW_v51.npz')
    np.savez(wf, W=Wi.astype(np.float32), sigma='i', c=-1.0, lf_dir=pp, mesh=mesh, nofast=True, conductor='v51 (C1-C8)',
             ecg_source='sigma_i, Alex 18 Oct 2026 13:22:54 UTC')
    out['written'] = wf
    json.dump(out, open(os.path.join(HERE, f'weights51_{h}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
    if not out['C9_pass_0.0002mV']:
        sys.exit('C9 failed')


if __name__ == '__main__':
    {'tensors': tensors, 'blood': blood, 'lon': lon, 'leadfield': leadfield, 'weights': weights}[sys.argv[1]]()
