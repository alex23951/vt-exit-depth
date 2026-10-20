"""v5.2 step 2 shared geometry (LOCK.md re-issued 20 Oct 2026 19:28 UTC, sha256 08ea65d3...): meshes, valve frames, rings.

The full cohort mesh (data/cohort/<H>/<H>/myocardium_AV_FEC_BB_lvrv, all tags) and the v5.1 simulation mesh
(data/biv/<H>/biv, tags 1, 2, 25, 28, 29: the full mesh's ventricular elements in their original order, nodes sorted,
biv.nod = full node of each biv node; checked 20 Oct 2026).

Valve frames (deviations D13 and D15, 20 Oct 2026):
  valve plane = the valve disc's mid-plane (principal-component fit of the disc nodes; normal toward its artery);
  mid-plane ring = the disc nodes shared with the wall around it that lie within RING_TOL of the mid-plane;
  aortic frame (8.5 item 6, D15): root axis = the disc normal through the aortic mid-plane ring's centroid; theta = 0 is
    the direction of the mitral-disc centroid projected onto the mid-plane; the sense is the one that puts the
    pulmonary-disc centroid 90-150 deg from theta = 0; neither sense -> stop;
  pulmonary frame (8.6, assumption 18): theta = 0 at the mid-plane ring point nearest the aortic wall (tag 5), the
    posterior sinus centre; the other sinuses at +-120 deg.
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))
from common import face_key, tet_faces                                                  # noqa: E402

HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
VENT = [1, 2, 25, 28, 29]
LV_GROUP, RV_GROUP = [1, 25, 29], [2, 28]
RING_TOL = 0.75                     # mm, half the mean edge (1.05 mm) plus margin
RUN = os.path.join(REPO, 'runs', 'v52_2026-10-20', '02_geometry')
CACHE = os.path.join(REPO, 'runs', 'v52_2026-10-20', 'cache52')
LOCK_SHA = '08ea65d3cda1adac9dcb1935a9000f32bbe093fc65e1e2e52ed8556373a1980b'


def sha256(f):
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        while b := fh.read(8 << 20):
            h.update(b)
    return h.hexdigest()


def load_full(h):
    os.makedirs(CACHE, exist_ok=True)
    c = os.path.join(CACHE, f'full_{h}.npz')
    if os.path.exists(c):
        z = np.load(c)
        return z['P'], z['E'], z['tag']
    base = os.path.join(REPO, 'data', 'cohort', h, h, 'myocardium_AV_FEC_BB_lvrv')
    E = pd.read_csv(base + '.elem', sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).to_numpy()
    P = pd.read_csv(base + '.pts', sep=' ', skiprows=1, header=None).to_numpy() / 1e3
    out = (P, E[:, :4].astype(np.int64), E[:, 4].astype(np.int64))
    np.savez(c, P=out[0], E=out[1], tag=out[2])
    return out


def load_biv(h):
    B = os.path.join(REPO, 'data', 'biv', h)
    c = os.path.join(CACHE, f'biv_{h}.npz')
    if os.path.exists(c):
        z = np.load(c)
        return z['P'], z['E'], z['tag'], z['nod']
    P = pd.read_csv(os.path.join(B, 'biv.pts'), sep=' ', skiprows=1, header=None).to_numpy() / 1e3
    E = pd.read_csv(os.path.join(B, 'biv.elem'), sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).to_numpy()
    nod = np.fromfile(os.path.join(B, 'biv.nod'), dtype=np.int64)
    out = (P, E[:, :4].astype(np.int64), E[:, 4].astype(np.int64), nod)
    np.savez(c, P=out[0], E=out[1], tag=out[2], nod=out[3])
    return out


def interfaces(E, tag):
    """Faces shared by two elements of different tags: faces (k, 3), the two element ids (a, b), their tags."""
    f, own = tet_faces(E)
    k = face_key(f)
    o = np.argsort(k, kind='stable'); ks = k[o]
    j = np.where(ks[1:] == ks[:-1])[0]
    a, b = own[o][j], own[o][j + 1]
    m = tag[a] != tag[b]
    return f[o][j][m], a[m], b[m]


def tri_area(P, F):
    return 0.5 * np.linalg.norm(np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]]), axis=1)


def tet_vol(P, E):
    x = P[E]
    return np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0], np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6.0


class Valve:
    def __init__(self, P, E, tag, vtag, wall_tags, artery_tag):
        self.P = P
        self.nodes = np.unique(E[tag == vtag])
        X = P[self.nodes]
        c = X.mean(0)
        _, _, vt = np.linalg.svd(X - c, full_matrices=False)
        n = vt[2]
        ac = P[np.unique(E[tag == artery_tag])].mean(0)
        self.n = n if (ac - c) @ n > 0 else -n
        self.disc_c = c
        hh = (X - c) @ self.n
        self.thickness = float(np.percentile(hh, 98) - np.percentile(hh, 2))
        self.faces = (float(np.percentile(hh, 2)), float(np.percentile(hh, 98)))       # ventricular face, arterial face
        wall = np.unique(E[np.isin(tag, wall_tags)])
        self.contact = np.intersect1d(self.nodes, wall)
        hc = (P[self.contact] - c) @ self.n
        self.ring = self.contact[np.abs(hc) <= RING_TOL]
        self.c = P[self.ring].mean(0) - ((P[self.ring].mean(0) - c) @ self.n) * self.n   # ring centroid, in the mid-plane
        e1 = np.cross(self.n, [1.0, 0, 0])
        if np.linalg.norm(e1) < 0.1:
            e1 = np.cross(self.n, [0, 1.0, 0])
        e1 /= np.linalg.norm(e1)
        self.e1, self.e2 = e1, np.cross(self.n, e1)
        self.a0, self.sign = 0.0, 1

    def h(self, X):
        return (np.atleast_2d(X) - self.c) @ self.n

    def r(self, X):
        d = np.atleast_2d(X) - self.c
        return np.linalg.norm(d - np.outer(d @ self.n, self.n), axis=1)

    def ang_raw(self, X):
        d = np.atleast_2d(X) - self.c
        return np.degrees(np.arctan2(d @ self.e2, d @ self.e1))

    def set_frame(self, a0_deg, sign):
        self.a0, self.sign = float(a0_deg), int(sign)

    def theta(self, X):
        return (self.sign * (self.ang_raw(X) - self.a0)) % 360.0

    def ring_point(self, th, win=5.0):
        """Mid-plane ring node at angle th (deg): within win of th, the one nearest the mid-plane."""
        t = self.theta(self.P[self.ring])
        d = np.abs((t - th + 180) % 360 - 180)
        k = self.ring[d <= win]
        if not len(k):
            k = self.ring[np.argsort(d)[:5]]
        return int(k[np.argmin(np.abs(self.h(self.P[k])))])


def aortic_frame(P, E, tag):
    """D15: theta 0 = projected mitral-disc centroid; sense from the pulmonary-disc centroid (90-150 deg)."""
    av = Valve(P, E, tag, 9, [1, 5, 25, 29], 5)
    mv_c = P[np.unique(E[tag == 7])].mean(0)
    pv_c = P[np.unique(E[tag == 10])].mean(0)
    a0 = float(av.ang_raw(mv_c)[0])
    res = {}
    for s in (1, -1):
        av.set_frame(a0, s)
        res[s] = float(av.theta(pv_c)[0])
    ok = [s for s in (1, -1) if 90.0 <= res[s] <= 150.0]
    rec = {'theta0': 'projected mitral-disc centroid direction', 'pulmonary_centroid_deg': {'+': round(res[1], 2), '-': round(res[-1], 2)},
           'sense': ('+' if ok[0] == 1 else '-') if ok else None, 'check_90_150': 'pass' if ok else 'FAIL',
           'axis': av.n.round(5).tolist(), 'ring_centroid_mm': av.c.round(3).tolist(), 'ring_nodes': int(len(av.ring)),
           'disc_thickness_mm': round(av.thickness, 2), 'disc_faces_mm': [round(x, 2) for x in av.faces]}
    if ok:
        av.set_frame(a0, ok[0])
    return av, rec


def pulmonary_frame(P, E, tag):
    pv = Valve(P, E, tag, 10, [2, 6, 28], 6)
    ao = np.unique(E[tag == 5])
    post = int(pv.ring[np.argmin(cKDTree(P[ao]).query(P[pv.ring])[0])])
    pv.set_frame(float(pv.ang_raw(P[post])[0]), 1)
    rec = {'posterior_centre_ring_node': post, 'axis': pv.n.round(5).tolist(), 'ring_centroid_mm': pv.c.round(3).tolist(),
           'ring_nodes': int(len(pv.ring)), 'disc_thickness_mm': round(pv.thickness, 2), 'disc_faces_mm': [round(x, 2) for x in pv.faces]}
    return pv, rec


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=1, default=str)
