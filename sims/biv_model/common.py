"""Shared paths and helpers for the biventricular model pipeline (sims/biv_model)."""

import os

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HEART = os.environ.get('HEART', 'Y5HYEDL4')
SRC = os.path.join(REPO, 'data', 'cohort', HEART, HEART)
SRC_MESH = os.path.join(SRC, 'myocardium_AV_FEC_BB_lvrv')
OUT = os.path.join(REPO, 'data', 'biv', HEART)
BIV = os.path.join(OUT, 'biv')

# cohort element tags (tags_lvrv.json)
VENT_TAGS = [1, 2, 25, 28, 29]          # LV, RV, FEC_LV, FEC_RV, FEC_SV
TAG_NAMES = {1: 'LV', 2: 'RV', 3: 'LA', 4: 'RA', 5: 'Ao', 6: 'PArt', 7: 'MV', 8: 'TV',
             9: 'AV', 10: 'PV', 25: 'FEC_LV', 26: 'BB', 27: 'AV_plane', 28: 'FEC_RV', 29: 'FEC_SV'}


def read_pts(base):
    return pd.read_csv(base + '.pts', sep=' ', skiprows=1, header=None).values.astype(float)


def read_elem(base):
    e = pd.read_csv(base + '.elem', sep=' ', skiprows=1, header=None, usecols=[1, 2, 3, 4, 5]).values
    return e[:, :4].astype(np.int64), e[:, 4].astype(np.int64)


def read_lon(base):
    return pd.read_csv(base + '.lon', sep=' ', skiprows=1, header=None).values.astype(float)


def read_surf(fname):
    return pd.read_csv(fname, sep=' ', skiprows=1, header=None, usecols=[1, 2, 3]).values.astype(np.int64)


def write_surf(fname, tri):
    with open(fname, 'w') as f:
        f.write(f'{len(tri)}\n')
        np.savetxt(f, tri, fmt='Tr %d %d %d')


def write_vtx(fname, idx):
    idx = np.unique(idx)
    with open(fname, 'w') as f:
        f.write(f'{len(idx)}\nintra\n')
        np.savetxt(f, idx, fmt='%d')


def read_vtx(fname):
    return np.loadtxt(fname, skiprows=2, dtype=np.int64, ndmin=1)


def write_dat(fname, x):
    np.savetxt(fname, x, fmt='%.6g')


def tet_faces(E):
    """All 4 faces of each tet, sorted node order, plus owning element index."""
    f = np.concatenate([E[:, [1, 2, 3]], E[:, [0, 2, 3]], E[:, [0, 1, 3]], E[:, [0, 1, 2]]])
    owner = np.tile(np.arange(len(E)), 4)
    return np.sort(f, axis=1), owner


def boundary_faces(E):
    f, owner = tet_faces(E)
    key = f[:, 0] * (1 << 42) + f[:, 1] * (1 << 21) + f[:, 2]
    _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    b = cnt[inv] == 1
    return f[b], owner[b]


def face_key(f):
    f = np.sort(f, axis=1)
    return f[:, 0] * (1 << 42) + f[:, 1] * (1 << 21) + f[:, 2]
