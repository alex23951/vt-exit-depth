"""v5.2 step 5 (LOCK.md 15.2): fixes 2 and 3 on a new heart-torso mesh at the CT pose, then lead fields and C9.

Released for the primary only (T13, CT pose; lock thread "Fix heart position in the torso", relayed 2 Nov 2026 01:22 UTC).
No arm-pose mesh (A32, A33, A37) and no report-8 mesh is built here.

Stages (one heart at a time, HEART=<H>; run alone):
  tensors     params/v52_conductivities.json: R2.1 sigma_e; R2.2 sigma_i solved at full precision so that
              sigma_m,d = sigma_m,f (v_d / 0.80)^2; section 3's table as a check to its printed decimals; R2.3's assertion
              to 1e-6; R3.3's atrial value sigma_i + sigma_e cross-fibre (0.248 / 0.242 S/m printed).
  build       mesh: the cohort heart (data/cohort/<H>/<H>/myocardium_AV_FEC_BB_lvrv, every tag) with v5.2's tags (pulmonary
              sleeve elements 2, crescent elements 1; outflow52.npz), moved by pose52's t' (rotation identity, 9.1);
              biv52's nodes and elements first, in biv52's order, so the intracellular region is biv52. Torso: meshtool
              between the T13 skin (resampled to 8 mm, as v5.1's 08_torso.py) and the heart's outer boundary (a hole),
              tag 100. The four chamber cavities are closed boundary components of the cohort mesh (LV, RV, LA, RA;
              capped by the valve discs 7-10 and the vein rings, step 0's cavities.json): each is meshed by meshtool as
              blood (101-104). The aortic root and pulmonary artery lumens open at the vessels' cut ends, so meshtool
              fills them as torso; their luminal surface (the outer-boundary faces on the valve side of a plane normal to
              the cut end, 1-5 mm before its lowest point, connected to the valve disc's upper face) is capped by a fan
              where that plane cuts it, and torso elements inside it become blood (105, 106) by conductor51's
              ray-parity test (C7). Nodes are merged by coordinates (1 um).
              R3.2 gates for all six (closed and consistently oriented, pinch edges counted; blood within +-2 % of the
              enclosed volume; no blood outside; >= 95 % of the luminal faces border blood; volumes). v5.1's
              "blood centroids beyond plane within ring" count (C8; C69: v5.1's formula for now) at every loop where a
              chamber's wall faces meet its valve-disc faces. lon: biv52.lon rows (rotation identity), others isotropic.
              C66's table: every tag with its conductivity and element count beside v5.1's value; tag 26's count and
              placement. Electrodes: the resampled skin node nearest each T13 electrode (as 08_torso.py).
  leadfield   openCARP lead fields, one lead per run, single process (section 13), light AMG options, memory watchdog
              (900 MB available); aVR / aVL / aVF from I and II (as v5.1).
  weights     C9: weights with sigma_m reproduce openCARP's own ECG of the lead-field runs (v5.1's test Vm, the first 10 ms
              of v5.1's template beat, appended nodes at their nearest v5.1 node's value) within 0.0002 mV; then the
              sigma_i weights -> data/biv/<H>/v52/ecgW_v52.npz.
Conductors: myocardium (tags 1, 2, 25, 28, 29) sigma_i + sigma_e on biv52's fibres; blood 0.7; atrial muscle (3, 4, 26;
C66) 0.248 / 0.242 isotropic; torso 0.2 and, at the torso's value, the vessel walls (5, 6; R3.3), the valve discs, vein
rings and AV plane (7-24, 27; C66). The sleeves' fibrous layer is a set of luminal-face nodes (outflow52.py), not
elements, so no element takes its 0.2 S/m here (reported; the control heart has no sleeve).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/05_conductor/conductor52.py tensors
                         HEART=<H> python -B .../conductor52.py build | leadfield | weights
"""
import importlib.util
import json
import os
import resource
import signal
import subprocess
import sys
import time

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'analysis', 'v52_2026-10-20', '02_geometry'))
import geom52 as G                                                                          # noqa: E402
import pose52 as PO                                                                         # noqa: E402
from common import read_elem, read_lon, read_pts                                            # noqa: E402

B51 = os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build')
_spec = importlib.util.spec_from_file_location('conductor51', os.path.join(B51, 'conductor51.py'))
C51 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C51)

SPEEDS = json.load(open(os.path.join(REPO, 'params', 'v52_speeds.json')))['hearts']
SIG_I_F, SIG_E_F, SIG_E_X, V_F = 0.174, 0.625, 0.236, 0.80
G_BLOOD, G_TORSO, TAG_TORSO = 0.7, 0.2, 100
BLOOD = {'LV': 101, 'RV': 102, 'LA': 103, 'RA': 104, 'aortic_root': 105, 'pulmonary_artery': 106}
MYO, ATRIAL = [1, 2, 25, 28, 29], [3, 4, 26]
AT_TORSO = [5, 6] + list(range(7, 25)) + [27]
DISC = {7: 'mitral', 8: 'tricuspid', 9: 'aortic', 10: 'pulmonary'}
TABLE3 = {'Y5HYEDL4': {'sheet': 0.01181, 'normal': 0.06184}, '6G8DD8S5': {'sheet': 0.00608, 'normal': 0.02673},
          '7D98EVAR': {'sheet': 0.00608, 'normal': 0.02673}}
ATRIAL_PRINTED = {'Y5HYEDL4': 0.248, '6G8DD8S5': 0.242, '7D98EVAR': 0.242}
AVG_EDGE, MIN_MB, MATCH_MM = 8.0, 900, 1e-3
T13 = os.path.join(REPO, 'data', 'torso', 'torsoModels', 'T_13')
OPTS = os.path.join(REPO, 'analysis', 'axis_2026-10-10', 'ellip_amg_light.opts')
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
RUNS = ['I', 'II', 'III', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def hd(h, *p):
    return os.path.join(REPO, 'data', 'biv', h, 'v52', *p)


def tdir(h, *p):
    return hd(h, 'torso52', *p)


def lf_dir(h):
    return os.path.join(REPO, 'runs', 'v52_2026-10-20', '05_conductor', h, 'leadfield52')


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


# ------------------------------------------------------------------ R2.1-R2.3, R3.3
def sigma(h):
    sp = SPEEDS[h]
    smf = SIG_I_F * SIG_E_F / (SIG_I_F + SIG_E_F)
    out = {'fibre': {'gi': SIG_I_F, 'ge': SIG_E_F}}
    for a in ('sheet', 'normal'):
        smd = smf * (sp[a] / V_F) ** 2
        out[a] = {'gi': smd * SIG_E_X / (SIG_E_X - smd), 'ge': SIG_E_X}
    return out


def tensors():
    out = {'version': 'v52-conductivities-1', 'written': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'lock_sha256': G.LOCK_SHA,
           'rule': 'R2.1 sigma_e 0.625 / 0.236 / 0.236; R2.2 sigma_i fibre 0.174, cross-fibre and transmural solved so that '
                   'sigma_m,d = sigma_m,f (v_d / 0.80)^2, sigma_m = sigma_i sigma_e / (sigma_i + sigma_e)',
           'blood_S_m': G_BLOOD, 'torso_S_m': G_TORSO, 'ecg_source': 'sigma_i (R2.3)', 'hearts': {}}
    smf = SIG_I_F * SIG_E_F / (SIG_I_F + SIG_E_F)
    assert round(smf, 5) == 0.13611, smf
    for h in SPEEDS:
        s = sigma(h)
        for a, v in TABLE3[h].items():
            assert round(s[a]['gi'], 5) == v, (h, a, s[a])
        sm = {a: s[a]['gi'] * s[a]['ge'] / (s[a]['gi'] + s[a]['ge']) for a in s}
        r23 = {a: abs(sm[a] / sm['fibre'] - (SPEEDS[h][a] / V_F) ** 2) for a in s}
        assert max(r23.values()) <= 1e-6, r23
        atr = s['sheet']['gi'] + s['sheet']['ge']
        assert round(atr, 3) == ATRIAL_PRINTED[h], (h, atr)
        out['hearts'][h] = {'speeds_m_s': SPEEDS[h], 'sigma_S_m': s, 'sigma_m_S_m': sm, 'R2.3_max_abs_error': max(r23.values()),
                            'atrial_muscle_S_m (R3.3; tags 3, 4, 26 by C66)': atr,
                            'bulk_sigma_i_plus_sigma_e_S_m (R2.6 report)': {a: s[a]['gi'] + s[a]['ge'] for a in s}}
    json.dump(out, open(os.path.join(REPO, 'params', 'v52_conductivities.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ mesh helpers
def write_mesh(base, P_um, E, kind, tags):
    with open(base + '.pts', 'w') as f:
        f.write(f'{len(P_um)}\n')
        pd.DataFrame(P_um).to_csv(f, sep=' ', header=False, index=False, float_format='%.3f')
    with open(base + '.elem', 'w') as f:
        f.write(f'{len(E)}\n')
        cols = {'t': kind, **{f'n{i}': E[:, i] for i in range(E.shape[1])}, 'g': np.asarray(tags)}
        pd.DataFrame(cols).to_csv(f, sep=' ', header=False, index=False)


def match_rows(A, B, N):
    """Index into A of each row of B (rows as node sets), -1 if absent."""
    def keys(X):
        s = np.sort(X, axis=1).astype(np.int64)
        return pd.DataFrame({'k1': s[:, 0] * N + s[:, 1], 'k2': s[:, 2] * N + s[:, 3]})
    ka, kb = keys(A), keys(B)
    ka['ia'] = np.arange(len(A)); kb['ib'] = np.arange(len(B))
    m = kb.merge(ka, on=['k1', 'k2'], how='left')
    out = np.full(len(B), -1, np.int64)
    ok = m['ia'].notna().to_numpy()
    out[m['ib'].to_numpy()[ok]] = m['ia'].to_numpy()[ok].astype(np.int64)
    return out


def oriented_boundary(P, E):
    """Boundary faces of a tet mesh, each oriented with its normal pointing out of its own tet, and the owner."""
    f = np.concatenate([E[:, [1, 2, 3]], E[:, [0, 2, 3]], E[:, [0, 1, 3]], E[:, [0, 1, 2]]])
    fourth = np.concatenate([E[:, 0], E[:, 1], E[:, 2], E[:, 3]])
    owner = np.tile(np.arange(len(E)), 4)
    s = np.sort(f, axis=1)
    N = int(E.max()) + 1
    key = pd.DataFrame({'a': s[:, 0] * N + s[:, 1], 'b': s[:, 2]})
    dup = key.duplicated(keep=False).to_numpy()
    f, fourth, owner = f[~dup], fourth[~dup], owner[~dup]
    n = np.cross(P[f[:, 1]] - P[f[:, 0]], P[f[:, 2]] - P[f[:, 0]])
    flip = np.sum(n * (P[fourth] - P[f[:, 0]]), 1) > 0
    f[flip] = f[flip][:, [0, 2, 1]]
    return f, owner


def face_components(F):
    N = int(F.max()) + 1
    ed = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    k = np.minimum(ed[:, 0], ed[:, 1]) * N + np.maximum(ed[:, 0], ed[:, 1])
    fid = np.tile(np.arange(len(F)), 3)
    o = np.argsort(k, kind='stable'); k, fid = k[o], fid[o]
    same = k[1:] == k[:-1]
    A = coo_matrix((np.ones(same.sum()), (fid[:-1][same], fid[1:][same])), shape=(len(F), len(F)))
    return connected_components(A, directed=False)[1]


def closure(F):
    """Edge use of an oriented triangle set (node ids): undirected counts and directed balance."""
    N = int(F.max()) + 1
    de = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    dk = de[:, 0] * N + de[:, 1]; rk = de[:, 1] * N + de[:, 0]
    und = np.unique(np.minimum(dk, rk), return_counts=True)[1]
    du, dc = np.unique(dk, return_counts=True)
    ru, rc_ = np.unique(rk, return_counts=True)
    rc = np.zeros(len(du), int); m = np.isin(du, ru); rc[m] = rc_[np.searchsorted(ru, du[m])]
    return {'edges': int(len(und)), 'edges_in_2_triangles': int((und == 2).sum()), 'edges_in_1_triangle': int((und == 1).sum()),
            'pinch_edges_in_4_triangles': int((und == 4).sum()), 'edges_other_counts': int(((und != 1) & (und != 2) & (und != 4)).sum()),
            'orientation_consistent': bool(np.array_equal(dc, rc))}


def boundary_loops(F):
    """Directed boundary edges (edges in one triangle) of an oriented triangle set, grouped into connected loops."""
    N = int(F.max()) + 1
    de = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    k = np.minimum(de[:, 0], de[:, 1]) * N + np.maximum(de[:, 0], de[:, 1])
    u, inv, cnt = np.unique(k, return_inverse=True, return_counts=True)
    be = de[cnt[inv.ravel()] == 1]
    if not len(be):
        return []
    nb = np.unique(be); idx = np.full(N, -1); idx[nb] = np.arange(len(nb))
    A = coo_matrix((np.ones(len(be)), (idx[be[:, 0]], idx[be[:, 1]])), shape=(len(nb), len(nb)))
    nl, lab = connected_components(A, directed=False)
    return [be[lab[idx[be[:, 0]]] == L] for L in range(nl)]


def tet_vol(P, E):
    out = np.empty(len(E))
    for c0 in range(0, len(E), 1_000_000):
        x = P[E[c0:c0 + 1_000_000]]
        out[c0:c0 + 1_000_000] = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    return out


def centroids(P, E):
    out = np.empty((len(E), 3))
    for c0 in range(0, len(E), 1_000_000):
        out[c0:c0 + 1_000_000] = P[E[c0:c0 + 1_000_000]].mean(1)
    return out


def guarded(cmd, logf, env=None, cwd=None):
    """Run a command with the memory watchdog (kill if MemAvailable < MIN_MB); returns wall time, peak used, killed, rc."""
    t0, peak, killed = time.time(), 0, False
    with open(logf, 'w') as lg:
        p = subprocess.Popen([str(c) for c in cmd], stdout=lg, stderr=subprocess.STDOUT, env=env, cwd=cwd, start_new_session=True)
        while p.poll() is None:
            mi = dict(l.split(':') for l in open('/proc/meminfo').read().splitlines() if ':' in l)
            av = int(mi['MemAvailable'].split()[0]) // 1024; peak = max(peak, int(mi['MemTotal'].split()[0]) // 1024 - av)
            if av < MIN_MB:
                os.killpg(p.pid, signal.SIGKILL); killed = True
                break
            time.sleep(2)
        p.wait()
    return {'wall_s': round(time.time() - t0), 'peak_used_mb': peak, 'watchdog_killed': killed, 'returncode': p.returncode}


def meshtool(logname, h, *args):
    out = next((x.split('=', 1)[1] for x in args if x.startswith('-outmsh=')), None)
    if out and os.path.exists(out + '.elem') and os.path.exists(tdir(h, logname + '.done')):
        log('meshtool', logname, 'reused (output and .done marker exist)')
        return 'reused'
    r = guarded(['meshtool', *args], tdir(h, logname + '.log'))
    log('meshtool', logname, r)
    if r['returncode'] or r['watchdog_killed']:
        raise RuntimeError(f'meshtool {logname}: {r}; see {tdir(h, logname + ".log")}')
    open(tdir(h, logname + '.done'), 'w').write(json.dumps(r))
    return r


def read_carp(base):
    P = read_pts(base) / 1e3
    E, tag = read_elem(base)
    return P, E, tag


# ------------------------------------------------------------------ build
def build():
    h = os.environ['HEART']
    t0 = time.time()
    os.makedirs(tdir(h), exist_ok=True)
    rep = {'heart': h, 'lock_sha256': G.LOCK_SHA, 'stage': 'build'}
    # heart: cohort mesh with v5.2's tags, biv52 first
    P, E, tag = G.load_full(h)
    z = np.load(os.path.join(G.RUN, h, 'outflow52.npz'))
    tag52 = tag.copy(); tag52[z['crescent_elements']] = 1; tag52[z['sleeve_elements']] = 2
    nod = np.fromfile(hd(h, 'biv52.nod'), dtype=np.int64)
    Pm = read_pts(hd(h, 'biv52')) / 1e3
    Em, tm = read_elem(hd(h, 'biv52'))
    assert np.abs(P[nod] - Pm).max() < 1e-6, 'biv52 nodes are not the cohort nodes'
    idx = match_rows(E, nod[Em], len(P))
    assert (idx >= 0).all() and len(np.unique(idx)) == len(idx), 'a biv52 element is not a cohort element'
    assert np.array_equal(tag52[idx], tm), 'biv52 tags differ from the cohort tags with v5.2 re-tags'
    assert int(np.isin(tag52, MYO).sum()) == len(Em), 'a myocardium-tagged cohort element is not in biv52'
    rest = np.setdiff1d(np.arange(len(E)), idx)
    Nm = len(nod)
    newid = np.full(len(P), -1, np.int64); newid[nod] = np.arange(Nm)
    oth = np.where(newid < 0)[0]; newid[oth] = Nm + np.arange(len(oth))
    pose = json.load(open(os.path.join(REPO, 'analysis', 'v52_2026-10-20', '02_geometry', f'pose52_{h}.json')))
    tp = np.array(pose['t_prime_mm'])
    M = np.array(pose['pose_4x4 (x_torso_mm = x_heart_mm + t_prime; rotation identity)'])
    assert np.allclose(M[:3, :3], np.eye(3)) and np.allclose(M[:3, 3], tp, atol=1e-3)
    Ph = np.empty((len(P), 3)); Ph[newid] = P; Ph = Ph + M[:3, 3]
    Eh = np.vstack([Em, newid[E[rest]]]); th = np.concatenate([tm, tag52[rest]])
    rep['heart_mesh'] = {'cohort_nodes': int(len(P)), 'cohort_elements': int(len(E)), 'biv52_nodes_first': Nm, 'biv52_elements_first': int(len(Em)),
                    'other_heart_elements': int(len(rest)), 't_prime_mm (pose52, rotation identity)': M[:3, 3].tolist(),
                    'sleeve_elements_retagged_2': int(len(z['sleeve_elements'])), 'crescent_elements_retagged_1': int(len(z['crescent_elements'])),
                    'fibrous_layer_nodes (no element of their own)': int(len(z['fibrous_nodes']))}
    log(h, 'heart assembled', len(Eh), 'elements')
    # boundary components of the heart
    F, own = oriented_boundary(Ph, Eh)
    lab = face_components(F)
    comps = {}
    for L in np.unique(lab):
        tg = sorted(set(th[own[lab == L]].tolist()))
        ext = Ph[np.unique(F[lab == L])]
        comps[int(L)] = {'faces': int((lab == L).sum()), 'tags': tg, 'bbox_mm3': float(np.prod(ext.max(0) - ext.min(0)))}
    outer = max(comps, key=lambda L: comps[L]['bbox_mm3'])
    names, voids = {}, {}
    for L, c in comps.items():
        if L == outer:
            continue
        if c['faces'] <= 20 and c['bbox_mm3'] < 1.0:                   # a closed void of a few faces inside the cohort mesh
            voids[L] = c
            continue
        t = set(c['tags'])
        nm = 'LA' if (3 in t and 4 not in t) else 'RA' if (4 in t and 3 not in t) else 'LV' if (9 in t and 10 not in t) else 'RV' if (10 in t and 9 not in t) else None
        if nm is None or nm in names.values():
            raise SystemExit(f'{h}: boundary component {L} ({c}) is not one chamber; stop and report')
        names[L] = nm
    if sorted(names.values()) != ['LA', 'LV', 'RA', 'RV']:
        raise SystemExit(f'{h}: chambers found {names}; stop and report')
    rep['boundary_components'] = {('outer' if L == outer else names[L]): {**c, 'closure': closure(F[lab == L])} for L, c in comps.items() if L not in voids}
    rep['internal_voids (left as they are: no element fills them; not meshed)'] = {str(L): {**c, 'closure': closure(F[lab == L])} for L, c in voids.items()}
    # surfaces for meshtool (um)
    def surf(fsel, base):
        u = np.unique(F[fsel]); loc = np.full(len(Ph), -1); loc[u] = np.arange(len(u))
        write_mesh(base, Ph[u] * 1e3, loc[F[fsel]], 'Tr', np.ones(int(fsel.sum()), int))
        return u
    surf_nodes = {'outer': surf(lab == outer, tdir(h, 'heart_outer'))}
    for L, nm in names.items():
        surf_nodes[nm] = surf(lab == L, tdir(h, f'cav_{nm}'))
    T, tri = PO.read_vtk_polydata(T13 + '_torso_coarse_surface.vtk')
    write_mesh(tdir(h, 'skin_raw'), T * 1e3, tri, 'Tr', np.ones(len(tri), int))
    io = ['-ifmt=carp_txt', '-ofmt=carp_txt']
    rep['meshtool'] = {}
    rep['meshtool']['resample_skin'] = meshtool('mt_skin', h, 'resample', 'surfmesh', f'-msh={tdir(h, "skin_raw")}', f'-avrg={AVG_EDGE * 1e3}',
                                                f'-outmsh={tdir(h, "skin")}', *io)
    rep['meshtool']['torso'] = meshtool('mt_torso', h, 'generate', 'mesh', f'-surf={tdir(h, "skin")},{tdir(h, "heart_outer")}', '-holes=0,1',
                                        f'-ins_tag={TAG_TORSO},0', '-prsv_bdry=1', '-mode=1', f'-outmsh={tdir(h, "torso_vol")}', *io)
    for nm in ('LV', 'RV', 'LA', 'RA'):
        rep['meshtool'][f'cav_{nm}'] = meshtool(f'mt_cav_{nm}', h, 'generate', 'mesh', f'-surf={tdir(h, f"cav_{nm}")}', f'-ins_tag={BLOOD[nm]}',
                                                '-prsv_bdry=1', '-mode=1', f'-outmsh={tdir(h, f"blood_{nm}")}', *io)
    # merge by coordinates
    Pall, Eall, tall = [Ph], [Eh], [th]
    n_next = len(Ph)
    merge = {}
    skin_P = read_pts(tdir(h, 'skin')) / 1e3
    for part, base, keep_nodes in [('torso', 'torso_vol', surf_nodes['outer'])] + [(nm, f'blood_{nm}', surf_nodes[nm]) for nm in ('LV', 'RV', 'LA', 'RA')]:
        Pp, Ep, tp_ = read_carp(tdir(h, base))
        zero = tp_ == 0
        Ep, tp_ = Ep[~zero], tp_[~zero]
        d, j = cKDTree(Ph[keep_nodes]).query(Pp)
        hit = d < MATCH_MM
        mp = np.full(len(Pp), -1, np.int64); mp[hit] = keep_nodes[j[hit]]
        nnew = int((~hit).sum()); mp[~hit] = n_next + np.arange(nnew); n_next += nnew
        merge[part] = {'nodes': int(len(Pp)), 'matched_to_heart_surface': int(hit.sum()), 'surface_nodes': int(len(keep_nodes)),
                       'all_surface_nodes_matched_once': bool(hit.sum() == len(keep_nodes) and len(np.unique(j[hit])) == len(keep_nodes)),
                       'max_match_mm': float(d[hit].max()) if hit.any() else None, 'elements': int(len(Ep)), 'tag0_elements_dropped': int(zero.sum())}
        if not merge[part]['all_surface_nodes_matched_once']:
            raise SystemExit(f'{h}: {part} does not conform to the heart surface: {merge[part]}; stop and report')
        if part == 'torso':
            ds, js = cKDTree(Pp).query(skin_P)
            skin_new = mp[js]; merge['skin_nodes_found_mm_max'] = float(ds.max())
        Pall.append(Pp[~hit]); Eall.append(mp[Ep]); tall.append(tp_)
        log(h, 'merged', part, merge[part])
    Pf = np.vstack(Pall); Ef = np.vstack(Eall); tf = np.concatenate(tall)
    del Pall, Eall, tall
    rep['merge'] = merge
    vol = tet_vol(Pf, Ef)
    rep['final_before_lumens'] = {'nodes': int(len(Pf)), 'elements': int(len(Ef)), 'min_element_volume_mm3': float(vol.min()),
                                  'tags': {int(k): int(v) for k, v in zip(*np.unique(tf, return_counts=True))}}
    log(h, 'merged mesh', rep['final_before_lumens']['nodes'], 'nodes', rep['final_before_lumens']['elements'], 'elements')
    # ---------------- R3.1 lumens of the two great vessels; R3.2 gates for all six
    Pc = Ph - M[:3, 3]                                           # cohort frame for the vessel frames
    av, _ = G.aortic_frame(P, E, tag); pv, _ = G.pulmonary_frame(P, E, tag)
    # sleeve elements carry tag 2, so they are biv52 elements: their row in Eh is their biv52 row
    inv = np.full(len(E), -1); inv[idx] = np.arange(len(idx))
    sleeve_new = np.zeros(len(Eh), bool)
    assert (inv[z['sleeve_elements']] >= 0).all()
    sleeve_new[inv[z['sleeve_elements']]] = True
    gates = {}
    lum = {}
    fo = lab == outer
    for vname, frame, wall_tags, disc in (('aortic_root', av, [5], 9), ('pulmonary_artery', pv, [6], 10)):
        Fo, oo = F[fo], own[fo]
        wall = np.isin(th[oo], wall_tags) | (sleeve_new[oo] if vname == 'pulmonary_artery' else False)
        c = Pc[Fo].mean(1)
        nrm = np.cross(Pc[Fo[:, 1]] - Pc[Fo[:, 0]], Pc[Fo[:, 2]] - Pc[Fo[:, 0]]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        hgt = frame.h(c)
        hw = frame.h(Pc[np.unique(Eh[np.isin(th, wall_tags)])])
        hdisc = float(np.median(frame.h(Pc[np.unique(Eh[th == disc])])))
        dirn = 1.0 if hw.max() - hdisc >= hdisc - hw.min() else -1.0        # the cut end is the wall's end farther from the disc
        span = (hw.max() - hdisc) if dirn > 0 else (hdisc - hw.min())
        # the cut end: its plane normal n_cut from the far-end wall faces that face along the vessel (the cut may be oblique
        # to the valve axis where the vessel curves); the lumen = the outer-boundary faces on the valve side of a plane
        # normal to n_cut placed `back` mm before the lowest end-facing face, connected to the disc face nearest the
        # axis. back starts at 1.0 mm and grows by 0.5 mm (to 5 mm) until that set no longer reaches the exterior.
        far = wall & ((hgt - hdisc) * dirn > 0.8 * span) & ((nrm @ frame.n) * dirn > 0.3)
        if far.sum() < 10:
            raise SystemExit(f'{h}: {vname}: no cut-end faces found; stop and report')
        n_cut = nrm[far].mean(0); n_cut /= np.linalg.norm(n_cut)
        for _ in range(3):
            sel = far & (nrm @ n_cut > 0.9)
            n_cut = nrm[sel].mean(0); n_cut /= np.linalg.norm(n_cut)
        tpl = (c - c[sel].mean(0)) @ n_cut
        endf = far & (nrm @ n_cut > 0.7)
        Lsel = None
        for back in np.arange(1.0, 5.01, 0.5):
            sub = np.where(tpl < tpl[endf].min() - back)[0]
            lab2 = face_components(Fo[sub])
            dsc = np.where((th[oo[sub]] == disc) & ((nrm[sub] @ frame.n) * dirn > 0.5))[0]
            if not len(dsc):
                raise SystemExit(f'{h}: {vname}: no disc face looks into the lumen; stop and report')
            seed = dsc[np.argmin(frame.r(c[sub][dsc]))]
            cand_ = sub[lab2 == lab2[seed]]
            if len(cand_) < 0.2 * len(Fo):
                Lsel = cand_
                break
        if Lsel is None:
            raise SystemExit(f'{h}: {vname}: no cap plane up to 5 mm before the cut end separates the lumen; stop and report')
        FL = Fo[Lsel]
        loops = boundary_loops(FL)
        caps = []
        for be in loops:
            Cc = Ph[np.unique(be)].mean(0)
            caps.append(np.stack([Ph[be[:, 1]], Ph[be[:, 0]], np.repeat(Cc[None], len(be), 0)], 1))
        Tl = np.concatenate([Ph[FL]] + caps)
        V_ = np.unique(Tl.reshape(-1, 3), axis=0, return_inverse=True)[1].ravel().reshape(-1, 3)
        cl = closure(V_)
        svol = float(abs(np.einsum('ij,ij->i', Tl[:, 0], np.cross(Tl[:, 1], Tl[:, 2])).sum()) / 6 / 1e3)
        lo, hi = Tl.reshape(-1, 3).min(0) - 0.5, Tl.reshape(-1, 3).max(0) + 0.5
        tor = np.where(tf == TAG_TORSO)[0]
        cen = centroids(Pf, Ef[tor])
        box = np.all((cen >= lo) & (cen <= hi), axis=1)
        cand = tor[box]
        ins, split = C51.inside(Tl, cen[box])
        tf[cand[ins]] = BLOOD[vname]
        lum[vname] = {'T': Tl, 'faces': FL, 'loops': loops}
        gates[vname] = {'surface': {'luminal_faces': int(len(FL)), 'cut_end_loops': len(loops),
                                    'wall_length_beyond_disc_mm': round(float(span), 2),
                                    'cut_plane_normal_angle_to_valve_axis_deg': round(float(np.degrees(np.arccos(abs(n_cut @ frame.n)))), 1),
                                    'cut_end_irregularity_mm (end-facing faces along n_cut)': round(float(tpl[endf].max() - tpl[endf].min()), 2),
                                    'cap_plane_back_from_lowest_end_face_mm': float(back),
                                    'cap_triangles': int(sum(len(x) for x in caps)), 'tags_on_luminal_faces': sorted(set(th[oo[Lsel]].tolist())),
                                    **cl, 'volume_ml': round(svol, 3)},
                        'C7': {'candidates_in_box': int(len(cand)), 'blood_elements': int(ins.sum()), 'split_votes': split}}
        log(h, vname, gates[vname])
    # chambers: their surfaces are the boundary components; blood meshed directly
    for L, nm in names.items():
        lum[nm] = {'T': Ph[F[lab == L]], 'faces': F[lab == L], 'loops': None}
        gates[nm] = {'surface': {'faces': comps[L]['faces'], 'tags_on_faces': comps[L]['tags'], **closure(F[lab == L]),
                                 'volume_ml': round(float(abs(np.einsum('ij,ij->i', Ph[F[lab == L]][:, 0], np.cross(Ph[F[lab == L]][:, 1], Ph[F[lab == L]][:, 2])).sum()) / 6 / 1e3), 3)}}
    vol = tet_vol(Pf, Ef)
    rng = np.random.default_rng(0)
    for nm, L_ in lum.items():
        Tl = lum[nm]['T']; btag = BLOOD[nm]
        lo, hi = Tl.reshape(-1, 3).min(0) - 0.5, Tl.reshape(-1, 3).max(0) + 0.5
        near = np.where(np.isin(tf, [TAG_TORSO, btag]))[0]
        cen = centroids(Pf, Ef[near])
        near = near[np.all((cen >= lo) & (cen <= hi), axis=1)]
        w = rng.dirichlet(np.ones(4), len(near))
        sp_ = np.einsum('ek,ekj->ej', w, Pf[Ef[near]])
        ins_s, _ = C51.inside(Tl, sp_)
        isb = tf[near] == btag
        bvol = float(vol[near[isb]].sum() / 1e3)
        sv = gates[nm]['surface']['volume_ml']
        # luminal faces bordering blood: the tet on the far side of each heart boundary face
        FL = lum[nm]['faces']
        side = near
        loc_nodes = np.unique(Ef[side])
        Es = np.searchsorted(loc_nodes, Ef[side]); Nn = len(loc_nodes)
        fs = np.sort(np.concatenate([Es[:, [0, 1, 2]], Es[:, [0, 1, 3]], Es[:, [0, 2, 3]], Es[:, [1, 2, 3]]]), axis=1)
        ownr = np.tile(side, 4)
        kf = pd.DataFrame({'a': fs[:, 0] * Nn + fs[:, 1], 'b': fs[:, 2], 'o': ownr})
        okL = np.isin(FL, loc_nodes).all(1)
        q = np.sort(np.searchsorted(loc_nodes, FL[okL]), axis=1)
        kq = pd.DataFrame({'a': q[:, 0] * Nn + q[:, 1], 'b': q[:, 2]})
        mm = kq.merge(kf, on=['a', 'b'], how='left')
        found = mm['o'].notna().to_numpy()
        bord = float(np.mean(tf[mm['o'].to_numpy()[found].astype(np.int64)] == btag)) if found.any() else 0.0
        g = gates[nm]
        g['R3.2'] = {'blood_ml': round(bvol, 3), 'enclosed_ml': sv, 'blood_over_enclosed': round(bvol / sv, 4),
                     'blood_within_2pct': bool(abs(bvol / sv - 1) <= 0.02),
                     'torso_volume_inside_ml_sampled': round(float(vol[near[(~isb) & ins_s]].sum() / 1e3), 3),
                     'blood_volume_outside_ml_sampled': round(float(vol[near[isb & (~ins_s)]].sum() / 1e3), 3),
                     'luminal_faces': int(len(FL)), 'luminal_faces_with_a_neighbour_tet': int(found.sum()),
                     'luminal_faces_bordering_blood_frac': round(bord, 4), 'ge_95pct': bool(bord >= 0.95),
                     'closed_and_consistent (pinch edges counted as passing)': bool(g['surface']['edges_in_1_triangle'] == 0 and g['surface']['edges_other_counts'] == 0 and g['surface']['orientation_consistent'])}
        log(h, nm, 'R3.2', g['R3.2'])
    # v5.1's valve-plane count (C8; C69: v5.1's formula): loops where a chamber's wall faces meet its valve-disc faces
    for L, nm in names.items():
        Fc, oc = F[lab == L], own[lab == L]
        isdisc = np.isin(th[oc], list(DISC))
        loops = boundary_loops(Fc[~isdisc]) if isdisc.any() else []
        bc = centroids(Pf, Ef[tf == BLOOD[nm]])
        out = []
        for be in loops:
            nb = np.unique(be); Cc = Ph[nb].mean(0)
            tri = np.stack([Ph[be[:, 1]], Ph[be[:, 0]], np.repeat(Cc[None], len(be), 0)], 1)
            nc = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]).sum(0); nc /= np.linalg.norm(nc)
            rad = float(np.linalg.norm(Ph[nb] - Cc, axis=1).max())
            d = -(bc - Cc) @ nc
            r = np.linalg.norm((bc - Cc) - np.outer(d, nc), axis=1)
            dn = [DISC[int(t)] for t in np.unique(th[oc[isdisc]]) if np.isin(Fc[isdisc][th[oc[isdisc]] == t], nb).any()]
            out.append({'loop_nodes': int(len(nb)), 'discs_touching': dn, 'radius_mm': round(rad, 2),
                        'ring_planarity_rms_mm': round(float(np.sqrt(np.mean(((Ph[nb] - Cc) @ nc) ** 2))), 2),
                        'blood_centroids_beyond_plane_within_ring (v5.1 formula, C69)': int(((d > 0.5) & (r < rad)).sum())})
        gates[nm]['valve_planes'] = out
    rep['R3.1_R3.2'] = gates
    # ---------------- C66 table, tag 26
    tags_all = {int(k): int(v) for k, v in zip(*np.unique(tf, return_counts=True))}
    sg = sigma(h)
    atr = sg['sheet']['gi'] + sg['sheet']['ge']
    def cond(t):
        if t in MYO:
            return 'myocardium: sigma_i + sigma_e on biv52 fibres (R2.1-R2.3)'
        if t in ATRIAL:
            return f'atrial muscle {atr:.4f} S/m isotropic (R3.3; C66 for 26)'
        if t in BLOOD.values():
            return 'blood 0.7 S/m (R3.1)'
        if t == TAG_TORSO:
            return 'torso 0.2 S/m'
        if t in AT_TORSO:
            return '0.2 S/m (R3.3 walls 5, 6; C66 for 7-24, 27)'
        return 'UNASSIGNED'
    def v51(t):
        if t in MYO:
            return 'myocardium (v5.1 sigma, v5.1 speeds)'
        if t in (101, 102):
            return 'blood 0.7 S/m (v5.1 C7, ventricular cavities)'
        return 'not in v5.1 mesh: its space was torso, 0.2 S/m'
    rep['C66_tags'] = {t: {'elements': n, 'v52': cond(t), 'v51': v51(t)} for t, n in tags_all.items()}
    if any(v['v52'] == 'UNASSIGNED' for v in rep['C66_tags'].values()):
        raise SystemExit(f'{h}: unassigned tag in the mesh; stop and report: {rep["C66_tags"]}')
    t26 = np.where(th == 26)[0]
    n34 = np.zeros(len(Ph), bool); n34[np.unique(Eh[np.isin(th, [3, 4])])] = True
    adj = n34[Eh[t26]].any(1)
    c26 = Ph[Eh[t26]].mean(1)
    inside_any = np.zeros(len(t26), bool)
    for nm in ('LA', 'RA', 'LV', 'RV'):
        inside_any |= C51.inside(lum[nm]['T'], c26)[0]
    rep['tag26'] = {'elements': int(len(t26)), 'sharing_a_node_with_tag_3_or_4': int(adj.sum()), 'centroid_inside_a_chamber_surface': int(inside_any.sum()),
                    'in_atrial_wall (C66)': bool(adj.all() and not inside_any.any())}
    # ---------------- lon, write, electrodes
    lonm = read_lon(hd(h, 'biv52'))
    assert len(lonm) == len(Em)
    os.makedirs(tdir(h, 'electrodes'), exist_ok=True)
    base = tdir(h, 'heart_torso52')
    write_mesh(base, Pf * 1e3, Ef, 'Tt', tf)
    with open(base + '.lon', 'w') as f:
        f.write('2\n')
        pd.DataFrame(lonm).to_csv(f, sep=' ', header=False, index=False, float_format='%.7f')
        f.write('1 0 0 0 1 0\n' * (len(Ef) - len(Em)))
    el = np.loadtxt(T13 + '_electrodes.csv', delimiter=',', skiprows=1)
    elec = {}
    for name, xyz in zip(PO.ELEC, el):
        dd = np.linalg.norm(skin_P - xyz, axis=1); k = int(np.argmin(dd))
        with open(tdir(h, 'electrodes', name + '.vtx'), 'w') as f:
            f.write(f'1\nextra\n{int(skin_new[k])}\n')
        elec[name] = {'node': int(skin_new[k]), 'snap_mm': round(float(dd.min()), 3)}
    rep['electrodes'] = elec
    rep['final'] = {'nodes': int(len(Pf)), 'elements': int(len(Ef)), 'tags': tags_all, 'files': base + '.{pts,elem,lon}',
                    'elem_sha256': G.sha256(base + '.elem')}
    rep['wall_s'] = round(time.time() - t0); rep['python_peak_rss_MB'] = peak_mb()
    G.dump(rep, os.path.join(HERE, f'conductor52_{h}.json'))
    log(h, 'build done', rep['wall_s'], 's', 'peak', rep['python_peak_rss_MB'], 'MB')


# ------------------------------------------------------------------ lead fields
def test_vm(h, rid):
    """v5.1's C9 test Vm (first 10 ms of v5.1's template beat), with biv52's appended nodes at their nearest v5.1 node."""
    src = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'leadfield_v51', 'vm_first10ms.igb')
    b = open(src, 'rb').read()
    hdr = b[:1024].decode('latin1')
    x = int(hdr.split('x:')[1].split()[0]); nt = int(hdr.split(' t:')[1].split()[0])
    vm = np.frombuffer(b[1024:], dtype='<f4').reshape(nt, x)
    Pm = read_pts(hd(h, 'biv52')) / 1e3
    Nm = len(Pm)
    if Nm > x:
        j = cKDTree(Pm[:x]).query(Pm[x:])[1]
        vm = np.hstack([vm, vm[:, j]])
        hdr = hdr.replace(f'x:{x} ', f'x:{Nm} ', 1)
    out = os.path.join(rid, 'vm_first10ms.igb')
    open(out, 'wb').write((hdr + ' ' * 1024)[:1024].encode('latin1') + vm.astype('<f4').tobytes())
    return out, {'source': src, 'v51_nodes': x, 'biv52_nodes': Nm, 'frames': nt, 'appended_nodes_from_nearest': Nm - x}


def leadfield():
    h = os.environ['HEART']
    CD = C51.biv_module('cd', '15_conductor.py', h)
    from carputils.leadfield import leadfield_setup
    sg = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts'][h]
    s, atr = sg['sigma_S_m'], sg['atrial_muscle_S_m (R3.3; tags 3, 4, 26 by C66)']
    rid = lf_dir(h)
    os.makedirs(os.path.join(rid, 'POSTPROC_DIR'), exist_ok=True)
    vm, vinfo = test_vm(h, rid)
    mesh = tdir(h, 'heart_torso52')
    tags = json.load(open(os.path.join(HERE, f'conductor52_{h}.json')))['final']['tags']
    present = sorted(int(t) for t in tags)
    t02 = [t for t in present if t == TAG_TORSO or t in AT_TORSO]
    tb = [t for t in present if t in BLOOD.values()]
    ta = [t for t in present if t in ATRIAL]
    tm = [t for t in present if t in MYO]
    assert sorted(t02 + tb + ta + tm) == present, present
    g = ['-num_gregions', 4]
    def region(i, ids):
        return [f'-gregion[{i}].num_IDs', len(ids)] + [x for j, t in enumerate(ids) for x in (f'-gregion[{i}].ID[{j}]', t)]
    g += region(0, tm) + ['-gregion[0].g_il', s['fibre']['gi'], '-gregion[0].g_el', s['fibre']['ge'], '-gregion[0].g_it', s['sheet']['gi'],
                          '-gregion[0].g_et', s['sheet']['ge'], '-gregion[0].g_in', s['normal']['gi'], '-gregion[0].g_en', s['normal']['ge']]
    for i, ids, val in ((1, t02, G_TORSO), (2, tb, G_BLOOD), (3, ta, atr)):
        g += region(i, ids)
        for k in ('l', 't', 'n'):
            g += [f'-gregion[{i}].g_i{k}', val, f'-gregion[{i}].g_e{k}', val]
    phys = ['-num_phys_regions', 2, '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', len(tm)] \
        + [x for j, t in enumerate(tm) for x in (f'-phys_region[0].ID[{j}]', t)] \
        + ['-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', len(present)] \
        + [x for j, t in enumerate(present) for x in (f'-phys_region[1].ID[{j}]', t)]
    imp = ['-num_imp_regions', 1, '-imp_region[0].im', 'Tomek', '-imp_region[0].num_IDs', len(tm)] \
        + [x for j, t in enumerate(tm) for x in (f'-imp_region[0].ID[{j}]', t)]
    stim, elec, opts = leadfield_setup(12, tdir(h, 'electrodes'), lf_vmfile=vm, ecg_timedt=10)
    env = dict(os.environ, PATH='/usr/local/lib/opencarp/lib/petsc/bin:' + os.environ.get('PATH', ''))
    res = {'run': rid, 'mesh': mesh, 'sigma_S_m': s, 'atrial_S_m': atr, 'g_blood': G_BLOOD, 'g_torso_and_walls': G_TORSO, 'np': 1,
           'regions': {'myocardium': tm, 'at_0.2': t02, 'blood': tb, 'atrial': ta}, 'test_vm': vinfo, 'parts': {}}
    rf = os.path.join(HERE, f'leadfield52_{h}.json')
    for lead in RUNS:
        sub = os.path.join(rid, lead)
        if os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{lead}.igb')):
            res['parts'][lead] = 'exists'
            continue
        os.makedirs(sub, exist_ok=True)
        cmd = ['openCARP', '-meshname', mesh, '-simID', sub, '-bidomain', 0, '-dt', 10, '-tend', 10] + imp + g + phys \
            + CD.lead_subset(stim, elec, [lead]) + opts + ['-ellip_options_file', OPTS]
        r = guarded(cmd, os.path.join(sub, 'openCARP.log'), env=env)
        res['parts'][lead] = r
        log(h, lead, r)
        if r['watchdog_killed'] or r['returncode'] or not os.path.exists(os.path.join(sub, 'POSTPROC_DIR', f'LF_{lead}.igb')):
            G.dump(res, rf)
            raise SystemExit(f'{h}: lead {lead} failed: {r}')
    pp = os.path.join(rid, 'POSTPROC_DIR')
    Z = {}
    for lead in RUNS:
        b = open(os.path.join(rid, lead, 'POSTPROC_DIR', f'LF_{lead}.igb'), 'rb').read()
        hdr, Z[lead] = b[:1024], np.frombuffer(b[1024:], dtype='<f4').copy()
        open(os.path.join(pp, f'LF_{lead}.igb'), 'wb').write(b)
        e = os.path.join(rid, lead, 'POSTPROC_DIR', f'ECG_{lead}.dat')
        if os.path.exists(e):
            open(os.path.join(pp, f'ECG_{lead}.dat'), 'w').write(open(e).read())
    for n, zz in (('aVR', -(Z['I'] + Z['II']) / 2), ('aVL', Z['I'] - Z['II'] / 2), ('aVF', Z['II'] - Z['I'] / 2)):
        open(os.path.join(pp, f'LF_{n}.igb'), 'wb').write(hdr + zz.astype('<f4').tobytes())
    nx = int(hdr.decode('latin1').split('x:')[1].split()[0])
    res['lf_nodes'] = nx; res['lf_nodes_equal_biv52'] = bool(nx == vinfo['biv52_nodes'])
    res['III_minus_(II_minus_I)_max_abs'] = float(np.abs(Z['III'] - (Z['II'] - Z['I'])).max())
    res['lf_files'] = sorted(f for f in os.listdir(pp) if f.startswith('LF_'))
    G.dump(res, rf)
    log(h, 'lead fields done', {k: (v if isinstance(v, str) else (v['wall_s'], v['peak_used_mb'])) for k, v in res['parts'].items()})


def weights():
    h = os.environ['HEART']
    sys.modules.pop('common', None)
    FE = C51.biv_module('fe', '13_fast_ecg.py', h)
    s = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts'][h]['sigma_S_m']
    pair = [(s[a]['gi'], s[a]['ge']) for a in ('fibre', 'sheet', 'normal')]
    Gc = {'myo': pair, 'fast': pair}
    mesh = hd(h, 'biv52')
    pp = os.path.join(lf_dir(h), 'POSTPROC_DIR')
    vm = FE.igb(os.path.join(lf_dir(h), 'vm_first10ms.igb'))
    out = {'heart': h, 'mesh': mesh, 'lf_dir': pp}
    Wm = FE.weights(mesh, pp, Gc, 'm', -1.0, True)
    mine = FE.project(Wm, vm)
    comp = {}
    for i, l in enumerate(LEADS):
        f = os.path.join(pp, f'ECG_{l}.dat')
        if os.path.exists(f):
            d = np.loadtxt(f)
            k = np.rint(d[:, 0] / 1.0).astype(int)
            ok = k < len(mine)
            comp[l] = {'max_abs_err_mV': float(np.abs(mine[k[ok], i] - d[ok, 1]).max()), 'ref_peak_mV': float(np.abs(d[ok, 1]).max()), 'times_ms': d[ok, 0].tolist()}
    err = max(c['max_abs_err_mV'] for c in comp.values())
    out['C9_sigma_m_vs_openCARP'] = comp
    out['C9_max_abs_err_mV'] = err
    out['C9_pass_0.0002mV'] = bool(err <= 0.0002)
    Wi = FE.weights(mesh, pp, Gc, 'i', -1.0, True)
    out['sigma_i_over_sigma_m_weight_ratio_median'] = float(np.median(np.abs(Wi[np.abs(Wm) > 1e-12] / Wm[np.abs(Wm) > 1e-12])))
    if out['C9_pass_0.0002mV']:
        wf = hd(h, 'ecgW_v52.npz')
        np.savez(wf, W=Wi.astype(np.float32), sigma='i', c=-1.0, lf_dir=pp, mesh=mesh, conductor='v52 step 5 (fixes 2 and 3, CT pose)', ecg_source='sigma_i (R2.3)')
        out['written'] = wf
    G.dump(out, os.path.join(HERE, f'weights52_{h}.json'))
    print(json.dumps({k: v for k, v in out.items() if k != 'C9_sigma_m_vs_openCARP'}, indent=1))
    if not out['C9_pass_0.0002mV']:
        sys.exit('C9 failed')


if __name__ == '__main__':
    {'tensors': tensors, 'build': build, 'leadfield': leadfield, 'weights': weights}[sys.argv[1]]()
