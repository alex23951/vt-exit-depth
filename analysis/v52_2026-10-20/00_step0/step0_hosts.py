"""v5.2 step 0: read-only feasibility checks for arms A35 (lungs, KCL_torso1, Zenodo 7253863) and A36 (skeletal muscle,
Moss / Wuelfers / Seemann Torso.vtu, Zenodo 8285403), LOCK.md 9.4 (deviations D9a, D9b).

A35 (i)-(iv) on the downloaded KCL_torso1 (runs/v52_2026-10-20/00_step0/hosts/). A36 (i)-(iii) on Torso.vtu by HTTP range
requests only (2,363,848,659 B; the whole file is never downloaded): the XML header, the full Material cell array (to count
tissues) and the FibreXYZ cell array at a seeded sample of skeletal-muscle cells, decoded with the Python standard library
(base64, struct). Memory estimates scale the measured v5.1 lead-field runs (1,983,222 nodes / 12,528,941 elements, 2 processes,
process peak RSS 3.0 GB each; LABNOTES 18 Oct 2026 16:23).
Usage (repo root, venv): python -B analysis/v52_2026-10-20/00_step0/step0_hosts.py
"""
import base64
import json
import math
import os
import struct
import subprocess
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
HOSTS = os.path.join(REPO, 'runs', 'v52_2026-10-20', '00_step0', 'hosts')
URL = 'https://zenodo.org/api/records/8285403/files/Torso.vtu/content'
V51 = {'nodes': 1983222, 'elements': 12528941, 'processes': 2, 'process_rss_gb': 3.0, 'system_peak_used_gb': 6.45}
WSL_GB = 7.7


def mem_est(nodes, elements):
    per_node = V51['processes'] * V51['process_rss_gb'] / V51['nodes']
    per_elem = V51['processes'] * V51['process_rss_gb'] / V51['elements']
    return {'by_nodes_gb': round(nodes * per_node, 2), 'by_elements_gb': round(elements * per_elem, 2),
            'basis': 'total process memory of the v5.1 lead-field solve (2 x 3.0 GB) scaled by nodes or by elements'}


def kcl():
    b = os.path.join(HOSTS, 'KCL_torso1', 'KCL_torso1')
    rec = json.load(open(os.path.join(HOSTS, 'kcl.json')))
    f1 = [f for f in rec['files'] if f['key'] == 'KCL_torso1.zip'][0]
    P = pd.read_csv(b + '.pts', sep=' ', skiprows=1, header=None).to_numpy() / 1e3
    E = pd.read_csv(b + '.elem', sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).to_numpy()
    tag = E[:, 4]; E = E[:, :4]
    u, c = np.unique(tag, return_counts=True)
    heart_el = int(np.isin(tag, [34, 35]).sum())
    X = P[np.unique(E[tag == 3])]; S = P[np.unique(E[tag == 2])]
    zs = np.arange(75, -310, -20)
    slab = []
    for z0 in zs:
        m = (X[:, 2] <= z0) & (X[:, 2] > z0 - 20)
        Y = X[m]
        mid = Y[np.abs(Y[:, 0]) < 25]
        slab.append({'z_top': int(z0), 'bone_x_range': [round(float(Y[:, 0].min()), 1), round(float(Y[:, 0].max()), 1)] if len(Y) else None,
                     'midline_bone_most_anterior_y': round(float(mid[:, 1].min()), 1) if len(mid) else None})
    skin_ant = float(S[:, 1].min())
    sternum = [s_['z_top'] for s_ in slab if s_['midline_bone_most_anterior_y'] is not None and s_['midline_bone_most_anterior_y'] < skin_ant + 40]
    low = [s_ for s_ in slab if s_['z_top'] <= -245]
    pelvis = any(s_['bone_x_range'] and (s_['bone_x_range'][1] - s_['bone_x_range'][0]) > 200 for s_ in low[-2:])
    # skeleton as one connected component (individual bones cannot be told apart by tag or connectivity)
    out = {'record': {'id': rec['id'], 'doi': rec.get('doi'), 'title': rec['metadata']['title'], 'license': rec['metadata']['license'],
                      'published': rec['metadata']['publication_date'], 'creators': [x['name'] for x in rec['metadata']['creators']],
                      'file': f1['key'], 'file_id': f1.get('id'), 'bytes': f1['size'], 'md5': f1.get('checksum'),
                      'info_pdf': 'KCL_TorsoComputationalModels_Info.pdf (file id feda745d-7806-4e72-88bb-2ebe2ebc0672), tag table read'},
           'i_files_open': {'pass': True, 'how': 'openCARP text format (.pts um, .elem Tt with tag, .lon), read with numpy / pandas; '
                                                'meshtool reads carp_txt natively'},
           'ii_size_and_memory': {'nodes': int(len(P)), 'elements': int(len(E)), 'host_heart_elements_removed (tags 34, 35)': heart_el,
                                  'tags': {int(k): int(v) for k, v in zip(u, c)},
                                  'estimate_host_alone': mem_est(len(P), len(E)),
                                  'estimate_with_pilot_heart (host heart removed, pilot ventricles 375k nodes / 1.94M elements added)':
                                      mem_est(len(P) + 375190, len(E) - heart_el + 1939909),
                                  'fits_single_process_7.7GB': True,
                                  'note': 'smaller than the v5.1 heart-torso mesh in nodes; a measured subset run is still due before the solve (15.1)'},
           'iii_host_heart_axes': {'inputs_present': 'LV wall 35, RV wall 34, LV / RV blood pools 25 / 24, valves 16-19: the v5.1 Laplace '
                                                     'set-up (apex patch, valve rims, endocardium, epicardium) can be built',
                                   'solves_run': False, 'reason_not_run': 'item (iv) already fails, so the arm is not run'},
           'iv_electrode_landmarks': {'bones': 'one tag (3) for the whole skeleton, and the skeleton is one connected component, so single bones '
                                               'are told apart only by position',
                                      'sternum': {'found': bool(sternum), 'anterior_midline_bone_z_range': [min(sternum) - 20, max(sternum)] if sternum else None},
                                      'intercostal_spaces': 'ribs present laterally from the top cut to about z -265 mm; rib gaps would have to be read by position',
                                      'clavicles': 'the mesh is cut at z +75 mm through the lung apices; clavicles not separable from ribs and scapulae by tag',
                                      'costal_margin': 'lower anterior rib border near z -165 to -205 mm (by position)',
                                      'iliac_crest': {'found': bool(pelvis), 'reason': 'the mesh ends at z -306 mm; below z -245 mm the bone narrows to the '
                                                                                       'spine (x -31 to +54 mm in the last slab): no iliac wing is in the mesh'},
                                      'pass': False},
           'bone_slabs_20mm': slab,
           'A35_verdict': 'not run: check (iv) fails (no iliac crest in the host mesh, so the LL electrode cannot be placed by the '
                          'Kligfield landmark rule; the clavicles are not identifiable either)',
           'host_lung_value_recorded_not_used_S_m': 0.0714}
    return out


def rng_get(a, b):
    r = subprocess.run(['curl', '-s', '-L', '-m', '900', '-r', f'{a}-{b}', URL], capture_output=True, check=True)
    return r.stdout


def moss():
    t0 = time.time()
    rec = json.load(open(os.path.join(HOSTS, 'moss.json')))
    f = [x for x in rec['files'] if x['key'] == 'Torso.vtu'][0]
    head = open(os.path.join(HOSTS, 'torso_head.bin'), 'rb').read()
    txt = head[:400].decode('latin1')
    npts = int(txt.split('NumberOfPoints="')[1].split('"')[0]); ncell = int(txt.split('NumberOfCells="')[1].split('"')[0])
    i = head.find(b'format="binary"'); j = head.find(b'>', i) + 1
    while head[j:j + 1] in b' \n\r\t':
        j += 1
    mat_start = j
    nb = 8 + 4 * ncell
    nchar = math.ceil(nb / 3) * 4
    cache = os.path.join(HOSTS, 'moss_material.b64')
    if not os.path.exists(cache) or os.path.getsize(cache) != nchar:
        data = rng_get(mat_start, mat_start + nchar - 1)
        open(cache, 'wb').write(data)
    raw = base64.b64decode(open(cache, 'rb').read())
    nbytes = struct.unpack('<Q', raw[:8])[0]
    mat = np.frombuffer(raw[8:8 + nbytes], dtype='<i4')
    assert len(mat) == ncell
    u, c = np.unique(mat, return_counts=True)
    # the next array's header (FibreXYZ)
    tail = rng_get(mat_start + nchar, mat_start + nchar + 400).decode('latin1')
    fstart = mat_start + nchar + tail.find('>', tail.find('FibreXYZ')) + 1
    while rng_get(fstart, fstart)[:1] in b' \n\r\t':
        fstart += 1
    # FibreXYZ (Float64 x 3): sample skeletal-muscle cells (material 8) with a fixed seed
    musc = np.where(mat == 8)[0]
    rs = np.random.default_rng(20261020)
    samp = np.sort(rs.choice(musc, min(200, len(musc)), replace=False)) if len(musc) else np.array([], dtype=np.int64)
    vec = []
    for cell in samp:
        off = 8 + 24 * int(cell)
        q0 = (off // 3) * 4; q1 = ((off + 24 + 2) // 3) * 4
        chunk = rng_get(fstart + q0, fstart + q1 - 1)
        dec = base64.b64decode(chunk)
        k = off - (off // 3) * 3
        vec.append(struct.unpack('<3d', dec[k:k + 24]))
    vec = np.array(vec).reshape(-1, 3)
    nz = np.linalg.norm(vec, axis=1) > 1e-6
    # a control: the same for left-ventricle cells (material 31), which should carry fibres
    lv = np.where(mat == 31)[0]
    samp_lv = np.sort(rs.choice(lv, 20, replace=False))
    vl = []
    for cell in samp_lv:
        off = 8 + 24 * int(cell); q0 = (off // 3) * 4; q1 = ((off + 24 + 2) // 3) * 4
        dec = base64.b64decode(rng_get(fstart + q0, fstart + q1 - 1)); k = off - (off // 3) * 3
        vl.append(struct.unpack('<3d', dec[k:k + 24]))
    vl = np.array(vl)
    names = {}
    for line in subprocess.run(['curl', '-s', '-L', '-m', '60', 'https://zenodo.org/api/records/8285403/files/material.tab/content'], capture_output=True, text=True).stdout.splitlines():
        p = line.split()
        if len(p) >= 2 and p[-1].isdigit():
            names[int(p[-1])] = ' '.join(p[:-1])
    counts = {f'{int(k)} {names.get(int(k), "?")}': int(v) for k, v in zip(u, c)}
    out = {'record': {'id': rec['id'], 'doi': rec.get('doi'), 'title': rec['metadata']['title'], 'license': rec['metadata']['license'],
                      'published': rec['metadata']['publication_date'], 'creators': [x['name'] for x in rec['metadata']['creators']],
                      'file': f['key'], 'file_id': f.get('id'), 'bytes': f['size'], 'md5': f.get('checksum')},
           'i_readable': {'pass': True, 'how': 'VTK XML UnstructuredGrid, header_type UInt64, inline base64 "binary" arrays, no compressor: '
                                               'parsed with the Python standard library (xml text, base64, struct); the full Material array '
                                               f'({nchar:,} characters) was fetched and decoded by HTTP range request; meshtool VTU input not tried'},
           'ii_size_and_memory': {'points': npts, 'cells': ncell, 'estimate_torso_alone': mem_est(npts, ncell),
                                  'fits_single_process_7.7GB': False,
                                  'note': 'about twice the v5.1 heart-torso mesh in cells and nodes before the pilot heart is added; the '
                                          'estimate exceeds WSL\'s 7.7 GB under either scaling'},
           'iii_skeletal_muscle_fibres': {'array': 'CellData FibreXYZ (Float64, 3 components) exists',
                                          'muscle_cells (Material 8)': int(len(musc)), 'sampled_muscle_cells (seed 20261020)': int(len(samp)),
                                          'sampled_with_nonzero_fibre': int(nz.sum()),
                                          'control_left_ventricle_cells (Material 31) sampled 20, nonzero': int((np.linalg.norm(vl, axis=1) > 1e-6).sum()),
                                          'reading': ('Torso.vtu holds no skeletal-muscle cells: Material 8 (Muscles_Skeleton) is listed in material.tab '
                                                      'but absent from the mesh (its Material range is 2-62 and no cell is 8), so there is no muscle to give '
                                                      'conductivities or fibres to' if not len(musc) else
                                                      ('skeletal muscle carries a fibre field' if nz.mean() > 0.5 else
                                                       'no skeletal-muscle fibre field (zero vectors); the Klepfer circumferential rule (assumption 53) would apply'))},
           'material_counts': counts,
           'A36_verdict': ('not run: Torso.vtu contains no skeletal muscle (Material 8 absent), and check (ii) fails (the memory estimate for '
                           'the torso alone exceeds the 7.7 GB single-process budget)') if not len(musc) else
                          'not run: check (ii) fails (the memory estimate for the torso alone exceeds the 7.7 GB single-process budget)',
           'download_bytes_used': int(nchar + 220 * 60 + 65536), 'wall_s': round(time.time() - t0, 1)}
    return out


def main():
    res = {'A35_KCL': kcl()}
    json.dump(res, open(os.path.join(HERE, 'hosts.json'), 'w'), indent=1, default=str)
    res['A36_Moss'] = moss()
    json.dump(res, open(os.path.join(HERE, 'hosts.json'), 'w'), indent=1, default=str)
    print(json.dumps({k: {kk: v[kk] for kk in v if kk.endswith('verdict') or kk.startswith('ii') or kk.startswith('iii')} for k, v in res.items()}, indent=1, default=str))


if __name__ == '__main__':
    main()
