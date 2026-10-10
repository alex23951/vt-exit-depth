#!/usr/bin/env python
"""
Step 8: place the pilot heart in the T13 torso, mesh the torso volume, compute lead fields.

  place     ventricles (bivF, with fibres and fast layer) moved into torso coordinates with
            the rigid atrial fit (data/torso/atria/<HEART>_to_g001_rigid.txt from 08a_atrial_fit.py: x_mm @ R.T + t),
            i.e. our LA + RA matched to ONE statistical-shape-model atrial geometry (g001)
            that sits inside the torsos (Bender et al. 2026, Zenodo 10.5281/zenodo.20086105).
  mesh      T13 skin surface (mm -> um) resampled to ~AVG_EDGE mm, ventricular boundary
            surface as a hole (kept exactly, so the torso mesh is conforming), meshtool
            generate mesh (tag 100 = torso), then merge with the ventricles (tags 1, 2).
            Torso = one uniform conductor (blood, lungs and cavities included), 0.2 S/m.
  electrodes  nearest torso-skin node to each T13 electrode (RA, LA, LL, V1-V6) -> vtx.
  leadfield   openCARP lead-field post-processing (carputils leadfield_setup, 12-lead,
            experiment 4) using the check-run Vm, which gives LF_*.igb and a test ECG.

Output: data/biv/<HEART>/torso/
"""

import argparse
import json
import os
import subprocess

import numpy as np

from common import HEART, OUT, REPO, boundary_faces, read_elem, read_lon, read_pts

# Orientation sensitivity (9 Oct 2026): TORSO_ROT_FRONTAL_DEG rotates the placed heart about the torso's
# antero-posterior axis through its centroid (+ = long axis turned from left towards inferior, i.e. more vertical);
# outputs then go to data/biv/<HEART>/torso<TORSO_SUFFIX>/. Unset = the original placement and folder.
TOR = os.path.join(OUT, 'torso' + os.environ.get('TORSO_SUFFIX', ''))
ROT_FRONTAL_DEG = float(os.environ.get('TORSO_ROT_FRONTAL_DEG', '0'))
T13 = os.path.join(REPO, 'data', 'torso', 'torsoModels', 'T_13')
RIGID = os.path.join(REPO, 'data', 'torso', 'atria', f'{HEART}_to_g001_rigid.txt')
AVG_EDGE = 8.0          # mm, torso skin resampling
G_TORSO = 0.2           # S/m
TAG_TORSO = 100
G = {'f': (0.5606, 2.0138), 's': (0.3368, 1.2096), 'n': (0.2962, 1.0642), 'fast': (5.1670, 18.5601)}
_cal = os.path.join(OUT, 'calibration.json')
if os.path.exists(_cal):                     # per-heart calibration (07_patch_tune.py --auto)
    _c = json.load(open(_cal))
    G['n'] = (_c['sheet_normal']['gi'], _c['sheet_normal']['ge'])
    G['fast'] = (_c['fast_layer']['2.0']['gi'], _c['fast_layer']['2.0']['ge'])
    G['f'] = (_c['fibre']['gi'], _c['fibre']['ge'])
    G['s'] = (_c['sheet']['gi'], _c['sheet']['ge'])
ELEC = ['RA', 'LA', 'LL', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'RL']


def read_vtk_polydata(f):
    L = open(f).read().split('\n')
    i = [k for k, l in enumerate(L) if l.startswith('POINTS')][0]
    n = int(L[i].split()[1])
    tok, j = [], i + 1
    while len(tok) < 3 * n:
        tok += L[j].split(); j += 1
    P = np.array(tok[:3 * n], float).reshape(-1, 3)
    k = [m for m, l in enumerate(L) if l.startswith('POLYGONS')][0]
    nt = int(L[k].split()[1]); tri = []; j = k + 1
    while len(tri) < nt:
        v = L[j].split()
        if v:
            tri.append([int(x) for x in v[1:4]])
        j += 1
    return P, np.array(tri)


def write_mesh(base, P, elems, kind, tags, lon=None):
    np.savetxt(base + '.pts', P, fmt='%.3f', header=str(len(P)), comments='')
    with open(base + '.elem', 'w') as f:
        f.write(f'{len(elems)}\n')
        np.savetxt(f, np.hstack([elems, np.asarray(tags).reshape(-1, 1)]), fmt=kind + ' %d' * (elems.shape[1] + 1))
    if lon is not None:
        with open(base + '.lon', 'w') as f:
            f.write(f'{lon.shape[1] // 3}\n')
            np.savetxt(f, lon, fmt='%.5f')


def place():
    os.makedirs(TOR, exist_ok=True)
    M = np.loadtxt(RIGID)
    R, t = M[:3], M[3]
    P = read_pts(os.path.join(OUT, 'bivF')) / 1e3 @ R.T + t        # mm, torso frame
    E, tag = read_elem(os.path.join(OUT, 'bivF'))
    lon = read_lon(os.path.join(OUT, 'bivF'))
    lon = np.hstack([lon[:, :3] @ R.T, lon[:, 3:] @ R.T])
    if ROT_FRONTAL_DEG:                  # torso frame: +x left, -y anterior, +z superior (T13 electrodes)
        a = np.radians(ROT_FRONTAL_DEG)
        Q = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
        c = P.mean(0)
        P = (P - c) @ Q.T + c
        lon = np.hstack([lon[:, :3] @ Q.T, lon[:, 3:] @ Q.T])
    write_mesh(os.path.join(TOR, 'heart'), P * 1e3, E, 'Tt', tag, lon)
    bf, _ = boundary_faces(E)
    nodes = np.unique(bf)
    new = -np.ones(len(P), np.int64); new[nodes] = np.arange(len(nodes))
    write_mesh(os.path.join(TOR, 'heart_bdry'), P[nodes] * 1e3, new[bf], 'Tr', np.ones(len(bf), int))
    T, tri = read_vtk_polydata(T13 + '_torso_coarse_surface.vtk')
    write_mesh(os.path.join(TOR, 'torso_skin_raw'), T * 1e3, tri, 'Tr', np.ones(len(tri), int))
    return {'heart_bbox_mm_in_torso': [P.min(0).round(1).tolist(), P.max(0).round(1).tolist()],
            'torso_bbox_mm': [T.min(0).round(1).tolist(), T.max(0).round(1).tolist()],
            'heart_boundary_faces': int(len(bf)), 'rot_frontal_deg': ROT_FRONTAL_DEG}


def mt(*args):
    r = subprocess.run(['meshtool', *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    return r.stdout


def mesh():
    s = os.path.join(TOR, 'torso_skin')
    mt('resample', 'surfmesh', f'-msh={s}_raw', f'-avrg={AVG_EDGE * 1e3}', f'-outmsh={s}',
       '-ifmt=carp_txt', '-ofmt=carp_txt')
    mt('generate', 'mesh', f'-surf={s},{os.path.join(TOR, "heart_bdry")}', '-holes=0,1',
       f'-ins_tag={TAG_TORSO},0', '-prsv_bdry=1', '-mode=1', f'-outmsh={os.path.join(TOR, "torso_vol")}',
       '-ifmt=carp_txt', '-ofmt=carp_txt')
    mt('merge', 'meshes', f'-msh1={os.path.join(TOR, "heart")}', f'-msh2={os.path.join(TOR, "torso_vol")}',
       f'-outmsh={os.path.join(TOR, "full")}', '-ifmt=carp_txt', '-ofmt=carp_txt')
    P = read_pts(os.path.join(TOR, 'full'))
    E, tag = read_elem(os.path.join(TOR, 'full'))
    # meshtool leaves a few tiny tag-0 elements in crevices of the heart surface (all nodes
    # on the heart boundary, < 0.3 mm3); drop them (2026-10-02: 19 elements)
    n0 = int((tag == 0).sum())
    # meshtool merge keeps only the fibre column; rebuild fibre + sheet for the heart
    # elements (merged mesh lists the heart elements first, same order: checked below)
    Eh, _ = read_elem(os.path.join(TOR, 'heart'))
    if not np.array_equal(E[:len(Eh)], Eh):
        raise RuntimeError('heart elements are not first / same order in the merged mesh')
    keep = tag != 0
    lon = np.tile([1.0, 0, 0, 0, 1.0, 0], (len(E), 1))
    lon[:len(Eh)] = read_lon(os.path.join(TOR, 'heart'))
    E, tag, lon = E[keep], tag[keep], lon[keep]
    write_mesh(os.path.join(TOR, 'full'), P, E, 'Tt', tag, lon)
    Ph = read_pts(os.path.join(TOR, 'heart'))
    same_order = bool(np.allclose(P[:len(Ph)], Ph, atol=1.0))
    x = P[E] / 1e3
    vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
    tor = tag == TAG_TORSO
    edge = np.linalg.norm(x[tor][:, 1] - x[tor][:, 0], axis=1)
    return {'removed_tag0_elements': n0, 'full_nodes': int(len(P)), 'full_elements': int(len(E)),
            'torso_elements': int(tor.sum()), 'heart_elements': int((~tor).sum()),
            'tags': {int(k): int(v) for k, v in zip(*np.unique(tag, return_counts=True))},
            'torso_volume_L': float(vol[tor].sum() / 1e6), 'heart_volume_ml': float(vol[~tor].sum() / 1e3),
            'torso_edge_mm_p5_p50_p95': np.percentile(edge, [5, 50, 95]).round(2).tolist(),
            'min_elem_volume_mm3': float(vol.min()),
            'heart_nodes_first_same_order': same_order}


def electrodes():
    d = os.path.join(TOR, 'electrodes')
    os.makedirs(d, exist_ok=True)
    P = read_pts(os.path.join(TOR, 'full'))
    E, tag = read_elem(os.path.join(TOR, 'full'))
    bf, _ = boundary_faces(E)
    skin = np.unique(bf)          # after merging, the only outer boundary is the torso skin
    el = np.loadtxt(T13 + '_electrodes.csv', delimiter=',', skiprows=1) * 1e3
    out = {}
    for name, xyz in zip(ELEC, el):
        dd = np.linalg.norm(P[skin] - xyz, axis=1)
        k = int(skin[np.argmin(dd)])
        with open(os.path.join(d, name + '.vtx'), 'w') as f:
            f.write(f'1\nextra\n{k}\n')
        out[name] = {'node': k, 'snap_mm': float(dd.min() / 1e3)}
    return out


def variants():
    """Full heart-torso meshes with modified heart tags (same nodes, fibres, element order):
    full_lbbb  : fast-layer elements touching the LV endocardium -> myocardium (tag 1), as in
                 bivF_lbbb (05b_lbbb_variant.py)
    full_nofast: all fast-layer elements -> myocardium (no-fast-layer control)"""
    P = os.path.join(TOR, 'full')
    E, tag = read_elem(P)
    out = {}
    hv = os.path.join(OUT, 'bivF_lbbb.elem')
    for name in ('full_lbbb', 'full_nofast'):
        new = tag.copy()
        if name == 'full_lbbb':
            if not os.path.exists(hv):
                continue
            _, th = read_elem(os.path.join(OUT, 'bivF_lbbb'))
            new[:len(th)] = th                       # heart elements are first, same order
        else:
            new[new == 2] = 1
        with open(os.path.join(TOR, name + '.elem'), 'w') as f:
            f.write(f'{len(E)}\n')
            np.savetxt(f, np.hstack([E, new[:, None]]), fmt='Tt %d %d %d %d %d')
        for ext in ('pts', 'lon'):
            if not os.path.exists(os.path.join(TOR, f'{name}.{ext}')):
                os.symlink(f'full.{ext}', os.path.join(TOR, f'{name}.{ext}'))
        out[name] = {'fast_elements': int((new == 2).sum())}
    return out


def leadfield(vm, np_=4, lf_dir=None, rid_name=None, ecg_dt=None, tend=30, full='full'):
    rid_name = rid_name or f'lf_T13_{HEART}'
    from carputils.leadfield import leadfield_setup
    d = os.path.join(TOR, 'electrodes')
    rid = os.path.join(REPO, 'runs', rid_name)
    os.makedirs(rid, exist_ok=True)
    stim, elec, opts = leadfield_setup(12, d, lf_vmfile=vm, lf_dir=lf_dir, ecg_timedt=ecg_dt)
    g = ['-num_gregions', 3,
         '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
         '-gregion[0].g_il', G['f'][0], '-gregion[0].g_el', G['f'][1],
         '-gregion[0].g_it', G['s'][0], '-gregion[0].g_et', G['s'][1],
         '-gregion[0].g_in', G['n'][0], '-gregion[0].g_en', G['n'][1],
         '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[1].g_i{k}', G['fast'][0], f'-gregion[1].g_e{k}', G['fast'][1]]
    g += ['-gregion[2].num_IDs', 1, '-gregion[2].ID[0]', TAG_TORSO]
    for k in ('l', 't', 'n'):
        g += [f'-gregion[2].g_i{k}', G_TORSO, f'-gregion[2].g_e{k}', G_TORSO]
    phys = ['-num_phys_regions', 2,
            '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1, '-phys_region[0].ID[1]', 2,
            '-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', 3, '-phys_region[1].ID[0]', 1,
            '-phys_region[1].ID[1]', 2, '-phys_region[1].ID[2]', TAG_TORSO]
    cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', os.path.join(TOR, full), '-simID', rid,
           '-bidomain', 0, '-dt', 10, '-tend', tend,
           '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek', '-imp_region[0].num_IDs', 2,
           '-imp_region[0].ID[0]', 1, '-imp_region[0].ID[1]', 2] + g + phys + stim + elec + opts
    with open(os.path.join(rid, 'openCARP.log'), 'w') as log:
        subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT, check=True)
    return {'run': rid, 'files': sorted(os.listdir(rid))[:40]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['place', 'mesh', 'electrodes', 'variants', 'leadfield'])
    p.add_argument('--full', default='full', choices=['full', 'full_lbbb', 'full_nofast'])
    p.add_argument('--vm', default=None, help='Vm file (intracellular heart nodes) for the test projection')
    p.add_argument('--lf-dir', default=None, help='reuse lead fields (POSTPROC_DIR of an earlier run)')
    p.add_argument('--run-id', default=None)
    p.add_argument('--ecg-dt', type=float, default=None)
    p.add_argument('--tend', type=float, default=30.0, help='length of the Vm file [ms]')
    a = p.parse_args()
    res = {'place': place, 'mesh': mesh, 'electrodes': electrodes, 'variants': variants}.get(
        a.stage, lambda: leadfield(a.vm, lf_dir=a.lf_dir, rid_name=a.run_id, ecg_dt=a.ecg_dt, tend=a.tend, full=a.full))()
    f = os.path.join(TOR, 'summary_08.json') if os.path.isdir(TOR) else None
    allr = json.load(open(f)) if f and os.path.exists(f) else {}
    allr[a.stage] = res
    os.makedirs(TOR, exist_ok=True)
    json.dump(allr, open(os.path.join(TOR, 'summary_08.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
