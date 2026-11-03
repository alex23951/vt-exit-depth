"""D43 (Alex "Adopt both", 3 Nov 2026 13:13:21 UTC): the ECG source formed element by element on the split mesh, each copy of
a split node with its own Vm and its merged node's lead-field value; lead fields unchanged.

Same assembly as conductor52.weights() / 13_fast_ecg.py (P1 stiffness with fix 2's sigma_i on biv52's fibres, the C73
step-5 lead fields LF_<lead>.igb, c = -1), except that each element's columns are its biv52cut nodes: W_split[l, b] =
c sum_{e containing b} sum_a K^e_ab Z_l(merged(a)). biv52cut.elem must be biv52.elem with copies substituted (checked:
cut_dup52 maps every cut element back to its biv52 element). Checks: the copies' weights sum to the step-5 weights
(ecgW_v52_c73.npz) and a Vm equal on both copies gives the step-5 ECG. 12 leads only (aVR / aVL / aVF from I and II, as
step 5); the unipolar electrode potentials of D36 (i) are formed from them against Wilson's central terminal.
Writes runs/v52_2026-10-20/11_engine/<H>/mesh/ecgW_split.npz (W over the simulation mesh's nodes) and ecgsplit52_<H>.json.
Usage (repo root, venv): HEART=<H> python -B .../ecgsplit52.py
"""
import importlib.util
import json
import os
import sys

import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))
spec = importlib.util.spec_from_file_location('fe13', os.path.join(REPO, 'sims', 'biv_model', '13_fast_ecg.py'))
FE = importlib.util.module_from_spec(spec); spec.loader.exec_module(FE)
LEADS = FE.LEADS


def main():
    h = os.environ['HEART']
    V = os.path.join(REPO, 'data', 'biv', h, 'v52')
    ref = np.load(os.path.join(V, 'ecgW_v52_c73.npz'))
    s = json.load(open(os.path.join(REPO, 'params', 'v52_conductivities.json')))['hearts'][h]['sigma_S_m']
    pair = [(s[a]['gi'], s[a]['ge']) for a in ('fibre', 'sheet', 'normal')]
    mesh = os.path.join(V, 'biv52')
    Em, _ = FE.read_elem(mesh)
    Ec = np.loadtxt(os.path.join(V, 'biv52cut.elem'), skiprows=1, usecols=(1, 2, 3, 4), dtype=np.int64)
    src = np.load(os.path.join(V, 'cut_dup52.npy'))
    assert Ec.shape == Em.shape and (src[Ec] == Em).all(), 'biv52cut.elem is not biv52.elem with copies'
    # rebuild K's element blocks with the cut columns: same Ke, columns from Ec
    pts = FE.read_pts(mesh) / 1e3
    lon = FE.read_lon(mesh)
    f = lon[:, :3] / np.linalg.norm(lon[:, :3], axis=1, keepdims=True); s_ = lon[:, 3:6] / np.linalg.norm(lon[:, 3:6], axis=1, keepdims=True)
    n = np.cross(f, s_)
    S = pair[0][0] * f[:, :, None] * f[:, None, :] + pair[1][0] * s_[:, :, None] * s_[:, None, :] + pair[2][0] * n[:, :, None] * n[:, None, :]
    x = pts[Em]
    J = np.stack([x[:, 1] - x[:, 0], x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]], axis=1)
    Jinv = np.linalg.inv(J)
    gr = np.concatenate([-Jinv.sum(2, keepdims=True), Jinv], axis=2)
    vol = np.abs(np.linalg.det(J)) / 6
    Ke = vol[:, None, None] * np.einsum('eki,ekl,elj->eij', gr, S, gr)
    Nm, Nc = len(pts), int(src.shape[0])
    rows = np.repeat(Em, 4, axis=1).ravel(); cols = np.tile(Ec, (1, 4)).ravel()
    Ks = sp.coo_matrix((Ke.ravel(), (rows, cols)), shape=(Nm, Nc)).tocsr()
    Z = np.stack([FE.igb(os.path.join(str(ref['lf_dir']), f'LF_{l}.igb'))[-1].astype(float) for l in LEADS])
    c = float(ref['c'])
    Wc = c * (Ks.T @ Z.T).T                                                            # (12, Nc)
    Wm_back = np.zeros((12, Nm)); np.add.at(Wm_back.T, src, Wc.T)
    Wref = ref['W'].astype(float)
    split = np.where(np.bincount(src, minlength=Nm) > 1)[0]
    rng = np.random.default_rng(0)
    vm = rng.normal(-80, 20, Nm)
    e_ref, e_new = Wref @ vm, Wc @ vm[src]
    M = np.load(os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', h, 'mesh', 'maps.npz'))
    keep = M['keep']
    assert (M['merged'] == src[keep]).all()
    rec = {'heart': h, 'merged_nodes': Nm, 'cut_nodes': Nc, 'split_merged_nodes': int(len(split)), 'sim_nodes': int(len(keep)),
           'max_abs_weight_sum_diff_vs_step5': float(np.abs(Wm_back - Wref).max()), 'max_abs_step5_weight': float(np.abs(Wref).max()),
           'equal_copies_ecg_max_abs_diff_mV': float(np.abs(e_ref - e_new).max()), 'equal_copies_ecg_scale_mV': float(np.abs(e_ref).max()),
           'sim_nodes_cover_all_cut_nodes': bool(len(keep) == Nc), 'lf_dir': str(ref['lf_dir']), 'c': c, 'sigma': 'i (fix 2, R2.3)'}
    np.savez(os.path.join(REPO, 'runs', 'v52_2026-10-20', '11_engine', h, 'mesh', 'ecgW_split.npz'), W=Wc[:, keep].astype(np.float32), leads=np.array(LEADS),
             rule='D43: per-copy Vm, element by element on the split mesh')
    json.dump(rec, open(os.path.join(HERE, f'ecgsplit52_{h}.json'), 'w'), indent=1)
    print(json.dumps(rec, indent=1))


if __name__ == '__main__':
    main()
