"""v5.2 step 0 (LOCK.md 15.2, read only): the non-geometry items.

  v5.1 tag and files; template run (site, cell type); openCARP Tomek cell types; the transmural coordinate the v5.1 fibres
  use; v5.1 atrial and vessel-wall conductivity; v5.1 stimulus radius; dream.solve; v5.1 pose (atrial-fit rotation, axis,
  angle, pivot, 4x4 per heart); the 17.3 dataset checksums; the four KIT torso IDs for A37.

Nothing is written outside analysis/v52_2026-10-20/00_step0/ and runs/v52_2026-10-20/00_step0/.
Usage (repo root, venv, PATH with mpiexec): python -B analysis/v52_2026-10-20/00_step0/step0_base.py
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '00_step0')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
LIMPET = '/usr/local/lib/opencarp/share/openCARP/physics/limpet'

# LOCK.md 17.3, copied
MD5 = {'Y5HYEDL4.zip': 'a7e648775f75badcbfddb73df3e1d720', '6G8DD8S5.zip': '8e8122eb09e0b1b0a65d13303159576b',
       '7D98EVAR.zip': '48b4cc87b766d3fe6a70e481deb22f8a', 'dataset_info.csv': '5b5a670d36373535f0013b3b94d2d33e'}
CRC_FILES = ['myocardium_AV_FEC_BB_lvrv.pts', 'myocardium_AV_FEC_BB_lvrv.elem', 'myocardium_AV_FEC_BB_lvrv.lon',
             'fascicles_lv.vtx', 'fascicles_rv.vtx', 'tags_lvrv.json']
CRC = {'Y5HYEDL4': ['a15d542b', 'fd5ee8b4', '46ebe383', 'c531067a', 'eaa854b6', '6e271ea0'],
       '6G8DD8S5': ['3fe32117', '6a0d49b6', 'b069be97', 'd8391977', 'ac8d314d', '49119edb'],
       '7D98EVAR': ['98f27b73', '939eef82', '197c680e', '1753e290', '5ddd73c5', '49119edb']}
CRC_BIN_Y5 = {'myocardium_AV_FEC_BB_lvrv.belem': 'f6e99f45', 'myocardium_AV_FEC_BB_lvrv.bpts': 'ee9fd3f7',
              'myocardium_AV_FEC_BB_lvrv.blon': '37a73ce5'}


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw).stdout


def sha256(f):
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def md5(f):
    h = hashlib.md5()
    with open(f, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def crc32(f):
    c = 0
    with open(f, 'rb') as fh:
        while b := fh.read(8 << 20):
            c = zlib.crc32(b, c)
    return f'{c & 0xffffffff:08x}'


def git_items():
    tag = sh(['git', 'rev-parse', 'v5.1^{commit}']).strip()
    head = sh(['git', 'rev-parse', 'HEAD']).strip()
    ns = [l.split('\t') for l in sh(['git', 'diff', '--name-status', 'v5.1', 'HEAD']).splitlines()]
    modified = [p for s, p in ns if s != 'A']
    tracked_dirty = [l for l in sh(['git', 'status', '--porcelain', '-uno']).splitlines()]
    # v5.1 data manifest (brief 4.7): size, mtime and sha256 of every listed file
    sys.path.insert(0, os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup'))
    from make_manifest import mtime_iso                                                    # noqa: E402
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(REPO, 'manifests', 'v51_data_sha256.tsv'))][1:]
    bad = []
    for p, size, mt, dig in rows:
        a = os.path.join(REPO, p)
        if not os.path.exists(a):
            bad.append(f'missing {p}'); continue
        st = os.stat(a)
        # this manifest's mtimes went through a float (st_mtime), so they differ from st_mtime_ns by < 1 us: compare at 1 us
        import datetime as dt
        sec, frac = mt.rstrip('Z').split('.') if '.' in mt else (mt.rstrip('Z'), '0')
        t_man = dt.datetime.strptime(sec, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() + float('0.' + frac)
        if str(st.st_size) != size or abs(st.st_mtime_ns / 1e9 - t_man) > 1e-6:
            bad.append(f'size/mtime {p}: {st.st_size} {mtime_iso(st.st_mtime_ns)} (manifest {size} {mt})')
        if sha256(a) != dig:
            bad.append(f'sha256 {p}')
    v5 = subprocess.run([sys.executable, '-B', os.path.join(REPO, 'analysis', 'v51_2026-10-15', '01_backup', 'check_v5_files.py'), '--full'],
                        cwd=REPO, capture_output=True, text=True)
    return {'v5.1_tag_commit': tag, 'head': head, 'tag_is_ancestor_of_head': subprocess.run(['git', 'merge-base', '--is-ancestor', 'v5.1', 'HEAD'], cwd=REPO).returncode == 0,
            'files_changed_since_tag_other_than_added': modified,
            'heart51_change_since_tag': sh(['git', 'log', '--format=%h %s', 'v5.1..HEAD', '--', 'analysis/v51_2026-10-15/04_build/heart51.py']).strip(),
            'tracked_files_with_uncommitted_changes': tracked_dirty,
            'v51_data_manifest': {'files': len(rows), 'checked': 'size, mtime, sha256', 'differences': bad},
            'v5_files_check': v5.stdout.strip().splitlines()[-3:] if v5.stdout else v5.stderr[-500:]}


def template_items():
    out = {}
    for h in HEARTS:
        run = os.path.join(REPO, 'runs', '2026-10-02_biv_fullqrs' if h == 'Y5HYEDL4' else f'2026-10-03_{h}_fullqrs')
        s = json.load(open(os.path.join(run, 'summary_06.json')))
        par = open(os.path.join(run, 'parameters.par')).read()
        lat = np.loadtxt(os.path.join(run, 'init_acts_LATs-thresh.dat'))
        k = int(np.argmin(np.abs(lat - 60)))
        imp = re.findall(r'^imp_region\[0\]\.(\S+)\s*=\s*(.*)$', par, re.M)
        out[h] = {'run': os.path.relpath(run, REPO), 'site_node': s['site_node'], 'site_uvc_z_phi_deg': [round(s['site_z'], 3), round(s['site_phi_deg'], 1)],
                  'site_mm': s['site_mm'], 'imp_region_settings': dict(imp), 'cell_type': 'ENDO (Tomek default: no flags or im_param given; Tomek.model line 23 "celltype = ENDO")',
                  'model': 'monodomain (bidomain 0), dt 10 us, tend 140 ms, Vm every 1 ms',
                  'template_node': k, 'template_node_LAT_ms': round(float(lat[k]), 3),
                  'template_window_ms': [round(-float(lat[k]), 1), round(140 - float(lat[k]), 1)],
                  'used_by': 'sims/biv_model/15_conductor.py Template (node whose LAT is closest to 60 ms), via heart51.Heart51.TM'}
    return out


def tomek_items():
    model = open(os.path.join(LIMPET, 'models', 'Tomek.model')).read()
    line = [l for l in model.splitlines() if 'celltype' in l and 'flag' in l]
    types = re.findall(r'^(ENDO|EPI|MCELL)\s*=\s*(\d+);', model, re.M)
    return {'model_file': os.path.join(LIMPET, 'models', 'Tomek.model'), 'cell_type_flags': dict(types), 'flag_line': line,
            'default': 'ENDO', 'epicardial_type_available': 'EPI' in dict(types),
            'note': 'Tomek 2019 (ToR-ORd), openCARP v20 build ffce195; set per region with imp_region[i].im_param "flags=EPI" (R1.1 single-cell runs)'}


def fibre_items():
    out = {'LV side (d <= 0.5)': 'v5 fibres (analysis/v5_grid_2026-10-13/fibres_E/<H>/bivF.lon, fibre_fix_2026-10-13/fibres_fix.py): Bayer 2012 '
                                 'LDRB; transmural coordinate phi_epi_fix = Laplace, LV + RV endocardium 0 -> epicardium + aortic-root interface 1 '
                                 '(fibres_E/<H>/laplace/phi_epi_fix.dat), per element as the mean of its nodes; septal blend by '
                                 'd = phi_rv / (phi_lv + phi_rv) (LV endocardium 0 -> RV endocardium 1); helix +60 -> -60 deg by bislerp in phi_epi_fix',
           'RV side (d > 0.5)': 'Doste 2019 (analysis/v51_2026-10-15/04_build/doste_rv.py): transmural d = clip(1 - Phi_D, 0, 1), Phi_D = -2 u_lv + u_rv '
                                '(runs/v51_2026-10-15/04_build/<H>/laplace/phi_D.dat), per element',
           'site depth (not fibres)': 'UVC rho = phi_epi (data/biv/<H>/uvc/rho.dat) and sep for the septum',
           'per heart': {}}
    for h in HEARTS:
        f = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'laplace', 'phi_epi_fix.dat')
        d = json.load(open(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', f'doste_{h}.json')))
        out['per heart'][h] = {'phi_epi_fix_sha256': sha256(f), 'phi_D_sha256': sha256(os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'laplace', 'phi_D.dat')),
                               'v51_fibre_file': f'data/biv/{h}/fibres_v51/bivF_v51.lon',
                               'doste_report_keys': sorted(d.keys())[:20]}
    return out


def wall_items():
    out = {}
    for h in HEARTS:
        base = os.path.join(REPO, 'data', 'biv', h, 'torso', 'full_nofast_blood_v51')
        tags = np.unique(np.loadtxt(base + '.elem', skiprows=1, usecols=(5,), dtype=np.int64))
        lf = os.path.join(REPO, 'runs', 'v51_2026-10-15', '04_build', h, 'leadfield_v51')
        pars = [os.path.join(dp, f) for dp, _, fs in os.walk(lf) for f in fs if f == 'parameters.par']
        greg = sorted(set(l.strip() for p in pars for l in open(p) if l.startswith('gregion')))
        out[h] = {'heart_torso_mesh': os.path.relpath(base, REPO), 'element_tags': tags.tolist(),
                  'lead_field_gregion_lines': greg[:40],
                  'reading': 'the v5.1 heart-torso mesh holds the ventricles (tags 1, 2), LV/RV cavity blood (101, 0.7 S/m) and one torso '
                             'conductor (100, 0.2 S/m); the atria, their blood, the aortic root and pulmonary artery are not separate: their '
                             'space is torso, so v5.1 used 0.2 S/m for atrial muscle, atrial blood, vessel walls and vessel blood'}
    return out


def stim_items():
    src = open(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '04_build', 'heart51.py')).read()
    lines = [f'heart51.py:{i + 1}: {l.strip()}' for i, l in enumerate(src.splitlines()) if 'BALL_UM' in l]
    out = {'code': lines, 'reading': 'radius 1.5 mm: every mesh node with |x - x_site| < 1500 um fires at t = 0 (strict <); no '
                                     'connectivity or tissue clause (the simulation mesh is myocardium only)', 'per heart': {}}
    for h in HEARTS:
        P = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'biv.pts'), skiprows=1)
        S = json.load(open(os.path.join(REPO, 'data', 'biv', h, 'sites.json')))
        S = S['sites'] if isinstance(S, dict) and 'sites' in S else S
        n = [int((np.linalg.norm(P - P[int(s['node'])], axis=1) < 1500.0).sum()) for s in S]
        out['per heart'][h] = {'sites': len(n), 'stimulated_nodes_min_median_max': [int(np.min(n)), float(np.median(n)), int(np.max(n))]}
    return out


def dream_items():
    txt = sh(['openCARP', '+Help', 'dream.solve'])
    txt = '\n'.join(l for l in txt.splitlines() if 'git repo' not in l.lower())
    return {'dream.solve_help': txt.strip().splitlines()[:25], 'offered': '0 eikonal, 1 RE+ (diffusion), 2 RE- (default), 3 DREAM' if 'RE+' in txt else 'not found'}


def pose_items():
    out = {}
    for h in HEARTS:
        M = np.loadtxt(os.path.join(REPO, 'data', 'torso', 'atria', f'{h}_to_g001_rigid.txt'))
        R, t = M[:3], M[3]
        ang = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
        w, V = np.linalg.eig(R)
        u = np.real(V[:, np.argmin(np.abs(w - 1))]); u /= np.linalg.norm(u)
        if u @ np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) < 0:
            u = -u                                                   # right-hand rule: positive angle about u
        T4 = np.eye(4); T4[:3, :3] = R; T4[:3, 3] = t
        # screw axis: point p0 with (I - R) p0 = t - (t.u) u, closest to the mesh origin
        A = np.eye(3) - R
        p0 = np.linalg.lstsq(A, t - (t @ u) * u, rcond=None)[0]
        p0 = p0 - (p0 @ u) * u
        # did v5.1 apply it? the heart-torso mesh's first nodes are the ventricles in torso coordinates
        Pb = np.loadtxt(os.path.join(REPO, 'data', 'biv', h, 'biv.pts'), skiprows=1) / 1e3
        nh = len(Pb)
        with open(os.path.join(REPO, 'data', 'biv', h, 'torso', 'full_nofast_blood_v51.pts')) as fh:
            fh.readline()
            Pt = np.loadtxt(fh, max_rows=nh)
        scale = 1e3 if np.abs(Pt).max() > 5e3 else 1.0
        err = np.linalg.norm(Pt / scale - (Pb @ R.T + t), axis=1)
        out[h] = {'file': f'data/torso/atria/{h}_to_g001_rigid.txt', 'convention': 'x_torso_mm = R x_heart_mm + t (08a_atrial_fit.py, 08_torso.py)',
                  'rotation_angle_deg': round(ang, 2), 'rotation_axis_unit': u.round(4).tolist(), 'translation_mm': t.round(3).tolist(),
                  'pivot': 'R is applied about the heart mesh origin (0, 0, 0), then t (ICP from a centroid match, 60 iterations)',
                  'screw_axis_point_mm': p0.round(2).tolist(), 'slide_along_axis_mm': round(float(t @ u), 2),
                  'pose_4x4': T4.round(9).tolist(),
                  'applied_in_v51': bool(err.max() < 1e-2), 'max_node_error_mm_v51_mesh_vs_transform': float(err.max())}
    return out


def checksum_items():
    out = {'md5': {}, 'crc32': {}}
    for h in HEARTS:
        z = os.path.join(REPO, 'data', 'cohort', f'{h}.zip')
        got = md5(z)
        out['md5'][f'{h}.zip'] = {'expected': MD5[f'{h}.zip'], 'got': got, 'match': got == MD5[f'{h}.zip'], 'bytes': os.path.getsize(z)}
        zf = zipfile.ZipFile(z)
        byname = {os.path.basename(i.filename): i for i in zf.infolist()}
        rows = {}
        exp = dict(zip(CRC_FILES, CRC[h])) | (CRC_BIN_Y5 if h == 'Y5HYEDL4' else {})
        for f, e in exp.items():
            cd = f'{byname[f].CRC & 0xffffffff:08x}' if f in byname else None
            ext = os.path.join(REPO, 'data', 'cohort', h, h, f)
            ex = crc32(ext) if os.path.exists(ext) else None
            rows[f] = {'expected': e, 'zip_central_directory': cd, 'extracted_file': ex,
                       'match': cd == e and (ex is None or ex == e)}
        out['crc32'][h] = rows
    # dataset_info.csv: no stored copy on the PC; fetched now from the version record 19351401 for the md5 check
    dl = os.path.join(RUN, 'dataset_info.csv')
    if not os.path.exists(dl):
        meta = json.loads(subprocess.run(['curl', '-s', '-L', '-m', '60', 'https://zenodo.org/api/records/19351401'], capture_output=True, text=True).stdout)
        f = [x for x in meta['files'] if x['key'] == 'dataset_info.csv'][0]
        subprocess.run(['curl', '-s', '-L', '-m', '120', f['links']['self'], '-o', dl], check=True)
        out['dataset_info_record_checksum'] = f.get('checksum')
    got = md5(dl)
    out['md5']['dataset_info.csv'] = {'expected': MD5['dataset_info.csv'], 'got': got, 'match': got == MD5['dataset_info.csv'],
                                      'note': 'no stored copy existed on the PC (searched data/, the repo, ~ and /mnt/c/Users/Alex); '
                                              'downloaded now from Zenodo record 19351401 into runs/v52_2026-10-20/00_step0/'}
    rows = [l for l in open(dl).read().splitlines()]
    out['dataset_info_pilot_rows'] = [rows[0]] + [r for r in rows if any(h in r for h in HEARTS)]
    out['all_match'] = all(v['match'] for v in out['md5'].values()) and all(r['match'] for h in out['crc32'].values() for r in h.values())
    return out


def kit_items():
    z = zipfile.ZipFile(os.path.join(REPO, 'data', 'torso', 'torsoModels.zip'))
    order = [i.filename for i in z.infolist()]
    shapes = []
    for n in order:
        m = re.fullmatch(r'torsoModels/(T_\d+)_torso_coarse_surface\.vtk', n)
        if m:
            shapes.append(m.group(1))
    return {'archive': 'data/torso/torsoModels.zip', 'md5': md5(os.path.join(REPO, 'data', 'torso', 'torsoModels.zip')),
            'record': 'Zenodo 20086105 (Bender 2026), torsoModels.zip md5 528b7c89d1a8ab86168a9d59a87a4ed1',
            'shape_surfaces_in_archive_order': shapes, 'n_shapes': len(shapes),
            'first_four_in_archive_order': shapes[:4],
            'meantorso_present': any('meantorso_torso' in n for n in order),
            'note': 'the archive order starts with T_13, the primary torso itself; reported, not resolved here'}


def main():
    t0 = time.time()
    os.makedirs(RUN, exist_ok=True)
    out = {'written': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    for k, f in (('git', git_items), ('template', template_items), ('tomek', tomek_items), ('fibre_transmural', fibre_items),
                 ('wall_conductivity_v51', wall_items), ('stimulus', stim_items), ('dream', dream_items), ('pose_v51', pose_items),
                 ('checksums_17_3', checksum_items), ('kit_torsos_A37', kit_items)):
        t1 = time.time()
        out[k] = f()
        print(f'{k}: {time.time() - t1:.0f} s', flush=True)
    out['wall_s'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, 'base.json'), 'w'), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ('git', 'checksums_17_3')}, indent=1, default=str)[:6000])


if __name__ == '__main__':
    main()
