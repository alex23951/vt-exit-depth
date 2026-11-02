"""C73 reference: each great-vessel stub's lumen closed at its own cut-end rim (lock thread, 2 Nov 2026).

usage: python3 -I rimcap.py COHORT_HEART_DIR HEART OUT_PREFIX
(sensitivity runs only: --root 0, --cov, --slab, --tau, --hmargin, --rmargin; C73's reference uses the defaults)
Reads myocardium_AV_FEC_BB_lvrv.bpts / .belem of the cohort archive (CT pose; coordinates in um, used here in mm).
Writes OUT_PREFIX.json (per vessel: valve frame, rim, holes, volume, checks) and OUT_PREFIX_<vessel>_surface.npz with
keys tris (closed surface: triangles over cohort node ids, ids >= the node count are fan apexes), apex (fan apex
coordinates, mm), rim (rim node ids as walked), o, a (valve frame) and sheet_faces (the sheet's faces as read, oriented
out of the tissue).

Rules, per vessel (aorta: wall tag 5, valve disc tag 9, root tags 1, 25, 27; PA: wall tag 6, disc tag 10, root tags
2, 28, 29):
 1. Boundary faces: faces of exactly one tetrahedron of the heart mesh, oriented so the normal points out of it.
 2. Valve frame: o = mean of the disc's nodes; a = the eigenvector of their covariance with the smallest eigenvalue,
    signed so that a . (mean of the wall's nodes - o) > 0. Height h(x) = (x - o) . a.
 3. Ring top z_top: ring coverage at height z = share of 36 sectors of 10 deg around the axis (o, a) holding a wall node
    with |h - z| < 0.75 mm. z0 = first z of 1.0, 1.5, ..., 29.5 mm with coverage >= 0.9; z_top = last z of the
    unbroken run of 0.5 mm steps from z0 with coverage >= 0.9.
 4. Luminal faces: wall-tag boundary faces whose outward normal n points at their axis point:
    n . (q - c) > 0, c the face centroid, q = o + clamp(h(c), 0, z_top) a.
    Then root-tag faces that pass the same test, lie above the disc centroid (h(c) > 0) and below h_root, and lie
    closer to the axis than rho_root: h_root and rho_root are 1.0 mm above the greatest height and 0.5 mm beyond the
    greatest distance from the axis of the nodes of the loops (6) that reach below 10 mm, other than the rim, of a first
    sheet grown (5) from the wall-tag luminal faces alone.
 5. Sheet: grown from the disc's distal faces (disc-tag boundary faces with n . a > 0) across shared edges into luminal
    faces. Across an edge shared by more than two boundary faces (a pinch edge) a face continues only into the face
    that bounds the same empty wedge.
 6. Loops: the sheet's boundary, walked by turning about each node inside the sheet (so a loop never jumps across a
    pinch node). Rim = the loop that reaches the greatest height (ties: the longer). The other loops are holes.
 7. Closed surface: the sheet's faces reversed (normals out of the lumen) and, over every loop, a fan from the mean of
    the coordinates of the loop's nodes as walked (a node walked twice counts twice). Blood is every torso element whose
    centroid lies inside it (step 5's inside test), after the heart's own pose transform is applied to it.
"""
import sys, json, hashlib, numpy as np
argv = sys.argv[1:]
D, H, OUT = argv[:3]
ROOTF = int(argv[argv.index('--root') + 1]) if '--root' in argv else 1
def opt(name, default):
    return float(argv[argv.index(name) + 1]) if name in argv else default
COV, SLAB, TAU, HM, RM = opt('--cov', 0.9), opt('--slab', 0.75), opt('--tau', 0.0), opt('--hmargin', 1.0), opt('--rmargin', 0.5)
def read_bpts(path):
    with open(path, 'rb') as f:
        n = int(f.read(1024).split()[0]); a = np.frombuffer(f.read(), dtype='<f4', count=3 * n).reshape(n, 3)
    return a.astype(np.float64) / 1000.0
def read_belem(path):
    with open(path, 'rb') as f:
        n = int(f.read(1024).split()[0]); a = np.frombuffer(f.read(), dtype='<i4', count=6 * n).reshape(n, 6)
    return a[:, 1:5].copy(), a[:, 5].copy()
P = read_bpts(f'{D}/myocardium_AV_FEC_BB_lvrv.bpts'); T, tag = read_belem(f'{D}/myocardium_AV_FEC_BB_lvrv.belem')
N = len(P)
# 1. boundary faces, oriented out of their tetrahedron
F = np.concatenate([T[:, [1, 2, 3]], T[:, [0, 2, 3]], T[:, [0, 1, 3]], T[:, [0, 1, 2]]])
opp = np.concatenate([T[:, 0], T[:, 1], T[:, 2], T[:, 3]]); own = np.tile(np.arange(len(T)), 4)
Fs = np.sort(F, axis=1).astype(np.int64); key = (Fs[:, 0] * N + Fs[:, 1]) * N + Fs[:, 2]
o_ = np.argsort(key, kind='stable'); ks = key[o_]
st = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]]); cnt = np.diff(np.r_[st, len(ks)]); assert cnt.max() <= 2
b = np.sort(o_[st[cnt == 1]])
bf = F[b].copy(); btag = tag[own[b]]
A, B, C = P[bf[:, 0]], P[bf[:, 1]], P[bf[:, 2]]
nrm = np.cross(B - A, C - A)
fl = np.einsum('ij,ij->i', nrm, P[opp[b]] - A) > 0
bf[fl] = bf[fl][:, [0, 2, 1]]; nrm[fl] *= -1
area = 0.5 * np.linalg.norm(nrm, axis=1); nu = nrm / (2 * area[:, None]); cen = (A + B + C) / 3
NF = len(bf)
# edge table: for each face and local edge k (bf[f,k] -> bf[f,(k+1)%3]), the face across it (pinch edges paired)
E = np.concatenate([bf[:, [0, 1]], bf[:, [1, 2]], bf[:, [2, 0]]])
Es = np.sort(E, axis=1).astype(np.int64); ek = Es[:, 0] * N + Es[:, 1]
eo = np.argsort(ek, kind='stable'); eks = ek[eo]
est = np.flatnonzero(np.r_[True, eks[1:] != eks[:-1]]); ecnt = np.diff(np.r_[est, len(eks)])
assert (ecnt % 2 == 0).all()
nb = np.full(3 * NF, -1, np.int64)
two = ecnt == 2
s2 = est[two]; nb[eo[s2]] = eo[s2 + 1] % NF; nb[eo[s2 + 1]] = eo[s2] % NF
n_pinch = 0
for s, c in zip(est[~two], ecnt[~two]):
    slots = eo[s:s + c]; faces = slots % NF; ks_ = slots // NF
    u = bf[faces[0], ks_[0]]; v = bf[faces[0], (ks_[0] + 1) % 3]
    e = P[v] - P[u]; e /= np.linalg.norm(e)
    phis, sides = [], []
    b1 = None
    for f in faces:
        w = [x for x in bf[f] if x != u and x != v][0]
        r = P[w] - P[u]; r -= (r @ e) * e; r /= np.linalg.norm(r)
        if b1 is None: b1 = r; b2 = np.cross(e, b1)
        phis.append(np.arctan2(r @ b2, r @ b1)); sides.append(np.sign(nu[f] @ np.cross(e, r)))
    order = np.argsort(phis); m = len(order)
    for i in range(m):
        fi, fj = order[i], order[(i + 1) % m]
        if sides[fi] > 0 and sides[fj] < 0:
            nb[slots[fi]] = faces[fj]; nb[slots[fj]] = faces[fi]
    n_pinch += 1
assert (nb >= 0).all()
NB = nb.reshape(3, NF).T  # NB[f, k]: face across local edge k of face f
VES = [(5, 9, [1, 25, 27], 'aorta'), (6, 10, [2, 28, 29], 'PA')]
def grow(seed, ok):
    ins = seed.copy(); q = list(np.flatnonzero(seed))
    while q:
        f = q.pop()
        for k in range(3):
            g = NB[f, k]
            if not ins[g] and ok[g]:
                ins[g] = True; q.append(g)
    return ins
def loops_of(ins):
    """Boundary loops of the face set, in the reversed (out-of-lumen) orientation, by turning about each node."""
    # reversed face f: (bf[f,0], bf[f,2], bf[f,1]); its directed edges are the reverses of the original ones.
    # Original local edge k goes bf[f,k] -> bf[f,k+1]; reversed it goes bf[f,k+1] -> bf[f,k].
    used = set(); loops = []
    bnd = [(f, k) for f in np.flatnonzero(ins) for k in range(3) if not ins[NB[f, k]]]
    bset = set(bnd)
    for f0, k0 in sorted(bnd):
        if (f0, k0) in used: continue
        loop = []; f, k = f0, k0
        while (f, k) not in used:
            used.add((f, k))
            v_from = bf[f, (k + 1) % 3]; v_to = bf[f, k]   # reversed direction
            loop.append(int(v_from))
            # next boundary edge leaves v_to: in reversed face f the edge leaving v_to is the reverse of original edge
            # (k-1): original bf[f,k-1] -> bf[f,k], reversed bf[f,k] -> bf[f,k-1]
            g, kk = f, (k - 1) % 3
            while True:
                if (g, kk) in bset:
                    f, k = g, kk; break
                h = NB[g, kk]
                # in face h, the shared edge is {bf[g,kk], bf[g,kk+1]}; find h's local edge index for it, then the
                # edge of h leaving v_to (reversed sense) is h's original edge ending at v_to other than the shared one
                a_, b_ = bf[g, kk], bf[g, (kk + 1) % 3]
                hk = [j for j in range(3) if {bf[h, j], bf[h, (j + 1) % 3]} == {a_, b_}][0]
                # v_to is bf[g,kk+1]?? (reversed edge kk goes bf[g,kk+1] -> bf[g,kk]; it leaves v_to, so v_to = bf[g,kk+1])
                # in h the same edge runs the other way, so in h's reversed orientation it arrives at v_to; the edge
                # leaving v_to in reversed h is the reverse of h's original edge ending at v_to
                j = [jj for jj in range(3) if bf[h, (jj + 1) % 3] == v_to and jj != hk][0]
                g, kk = h, j
        loops.append(loop)
    return loops
def ring_cov(WP, o, a, z, e1, e2):
    m = np.abs((WP - o) @ a - z) < SLAB
    if m.sum() == 0: return 0.0
    Q = WP[m] - o; ang = np.arctan2(Q @ e2, Q @ e1)
    return len(np.unique(np.floor((ang + np.pi) / (2 * np.pi) * 36).astype(int) % 36)) / 36
def signed_volume(PP, TT):
    return np.einsum('ij,ij->i', PP[TT[:, 0]], np.cross(PP[TT[:, 1]], PP[TT[:, 2]])).sum() / 6.0
def vol_above(PP, TT, p0, n):
    V = 0.0; X = PP[TT] - p0; s = X @ n
    for tri, sv in zip(X, s):
        pos = sv > 0
        if pos.all(): V += np.dot(tri[0], np.cross(tri[1], tri[2])); continue
        if not pos.any(): continue
        poly = []
        for i in range(3):
            A_, B_ = tri[i], tri[(i + 1) % 3]; sa, sb = sv[i], sv[(i + 1) % 3]
            if sa > 0: poly.append(A_)
            if (sa > 0) != (sb > 0): poly.append(A_ + sa / (sa - sb) * (B_ - A_))
        for i in range(1, len(poly) - 1): V += np.dot(poly[0], np.cross(poly[i], poly[i + 1]))
    return V / 6.0
out = {'heart': H, 'root_lining': ROOTF, 'cov': COV, 'slab_mm': SLAB, 'tau': TAU, 'h_margin_mm': HM, 'rho_margin_mm': RM, 'nodes': int(N), 'tets': int(len(T)),
       'boundary_faces': int(NF), 'pinch_edges': int(n_pinch)}
for W, Dt, RT, name in VES:
    dn = np.unique(T[tag == Dt]); o = P[dn].mean(0)
    wn = np.unique(T[tag == W]); WP = P[wn]
    ev = np.linalg.eigh(np.cov((P[dn] - o).T))[1][:, 0]; a = ev * np.sign(ev @ (WP.mean(0) - o))
    e1 = np.cross(a, [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
    z0 = next(z for z in np.arange(1.0, 30.0, 0.5) if ring_cov(WP, o, a, z, e1, e2) >= COV)
    z = z0
    while ring_cov(WP, o, a, z + 0.5, e1, e2) >= COV: z += 0.5
    ztop = z
    hc = (cen - o) @ a
    q = o + np.outer(np.clip(hc, 0, ztop), a)
    dq = q - cen
    front = np.einsum('ij,ij->i', nu, dq) > TAU * np.linalg.norm(dq, axis=1)
    disc = btag == Dt; dist = disc & (nu @ a > 0)
    lum = (btag == W) & front
    sheet = grow(dist, lum | dist)
    root = {}
    if ROOTF:
        lp = loops_of(sheet)
        hm = [((P[l] - o) @ a).max() for l in lp]; top = int(np.argmax(np.array(hm) + 1e-6 * np.array([len(l) for l in lp])))
        rn = np.unique(np.concatenate([l for i, l in enumerate(lp) if i != top and ((P[l] - o) @ a).min() < 10.0]))
        hn = (P[rn] - o) @ a; rh = np.linalg.norm((P[rn] - o) - np.outer(hn, a), axis=1)
        HR, RR = hn.max() + HM, rh.max() + RM
        rho = np.linalg.norm((cen - o) - np.outer(hc, a), axis=1)
        lum = lum | (np.isin(btag, RT) & front & (hc > 0) & (hc < HR) & (rho < RR))
        sheet = grow(dist, lum | dist)
        root = {'h_root_mm': round(float(HR), 3), 'rho_root_mm': round(float(RR), 3)}
    lp = loops_of(sheet)
    hm = [((P[l] - o) @ a).max() for l in lp]; top = int(np.argmax(np.array(hm) + 1e-6 * np.array([len(l) for l in lp])))
    rim = lp[top]
    apex = []; fans = []
    for i, l in enumerate(lp):
        apex.append(P[l].mean(0)); k = N + len(apex) - 1
        # loop runs along the reversed sheet's boundary; the fan must run the other way
        fans.append(np.array([[l[(j + 1) % len(l)], l[j], k] for j in range(len(l))]))
    PP = np.vstack([P, np.array(apex)])
    TT = np.vstack([bf[sheet][:, [0, 2, 1]]] + fans)
    de = np.concatenate([TT[:, [0, 1]], TT[:, [1, 2]], TT[:, [2, 0]]])
    sde = set(map(tuple, de.tolist())); unpaired = sum((y, x) not in sde for x, y in sde)
    V = signed_volume(PP, TT)
    hr = (P[rim] - o) @ a
    rc = P[rim].mean(0); evr = np.linalg.eigh(np.cov((P[rim] - rc).T))[1][:, 0]
    rimplane_tilt = float(np.degrees(np.arccos(abs(evr @ a))))
    fan_area = lambda f: float(0.5 * np.linalg.norm(np.cross(PP[f[:, 1]] - PP[f[:, 0]], PP[f[:, 2]] - PP[f[:, 0]]), axis=1).sum())
    rim_ids = np.array(rim, dtype=np.int64)
    r = {'disc_nodes': int(len(dn)), 'wall_nodes': int(len(wn)), 'o_mm': o.round(4).tolist(), 'a': a.round(6).tolist(),
         'ring_top_mm': float(ztop), 'ring_start_mm': float(z0), **root,
         'sheet_faces': int(sheet.sum()),
         'sheet_tags': {int(k): int(v) for k, v in zip(*np.unique(btag[sheet], return_counts=True))},
         'rim': {'nodes': len(rim), 'distinct_nodes': len(set(rim)), 'start_node': int(rim[0]),
                 'length_mm': round(float(np.linalg.norm(P[rim] - P[np.roll(rim, -1)], axis=1).sum()), 2),
                 'height_mm': [round(float(hr.min()), 3), round(float(hr.max()), 3)],
                 'plane_tilt_from_axis_deg': round(rimplane_tilt, 2),
                 'max_dev_from_own_plane_mm': round(float(np.abs((P[rim] - rc) @ evr).max()), 3),
                 'cap_area_mm2': round(fan_area(fans[top]), 2),
                 'sorted_node_ids_sha256': hashlib.sha256(np.sort(rim_ids).tobytes()).hexdigest()},
         'holes': [{'nodes': len(l), 'height_mm': [round(float(((P[l] - o) @ a).min()), 2), round(float(((P[l] - o) @ a).max()), 2)],
                    'fan_area_mm2': round(fan_area(fans[i]), 2)} for i, l in enumerate(lp) if i != top],
         'closed_surface_triangles': int(len(TT)), 'unpaired_directed_edges': int(unpaired),
         'volume_mL': round(float(V) / 1000, 4)}
    out[name] = r
    np.savez_compressed(f'{OUT}_{name}_surface.npz', tris=TT, apex=np.array(apex), rim=rim_ids, o=o, a=a,
                        sheet_faces=bf[sheet])
    print(H, name, json.dumps({k: v for k, v in r.items() if k not in ('o_mm', 'a', 'holes')}), 'holes', len(r['holes']),
          'hole area', round(sum(hh['fan_area_mm2'] for hh in r['holes']), 1))
json.dump(out, open(OUT + '.json', 'w'), indent=1)
