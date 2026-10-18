"""Activation wave and 12-lead ECG for one LV free-wall site paced at 10 % and at 90 % wall depth (read-only figure).

Saved beats only, nothing is solved: the v5 beats regenerated bit-exactly on 14 Oct
(analysis/audit_addendum_2026-10-14/maps/<H>/<site>.T.npy = activation time per mesh node in ms,
<site>.ecg.npy = 12 leads in mV at 1 ms, t = 0 at the stimulus) and the heart mesh (data/biv/<H>/biv.pts, biv.elem,
surfaces/). Criteria printed on the figure: the 14 Oct rescore table (pace-map convention: from the stimulus, clean ECG;
intervals are identical under ecg_depth_criteria 0.3.0 and 0.4.0) and q in lead I under the 0.4.0 primary rule
(analysis/v51_2026-10-15/02_measure_040/per_site.csv). Writes only <OUT>.gif and <OUT>_final.png.

Views: top, the heart from outside, looking at the pacing site perpendicular to the LV long axis (base up);
middle, a cut across the heart containing the pacing line (both site nodes), close to a short-axis cut, seen from the
apex with the paced wall on the right.

Usage: python -B wave_ecg_gif.py   (environment: HEART, SITE = site id without the _dNN suffix, OUT)
"""
import json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm, colors as mcolors
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
H = os.environ.get('HEART', 'Y5HYEDL4'); SITE = os.environ.get('SITE', 'lv_free_wall_phi180_z0.5')
MAPS = os.path.join(REPO, 'analysis', 'audit_addendum_2026-10-14', 'maps', H)
MESH = os.path.join(REPO, 'data', 'biv', H)
OUT = os.environ.get('OUT', os.path.join(REPO, 'figures', f'2026-10-18_{H}_{SITE}_10_vs_90'))
LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
GRID = [['I', 'aVR', 'V1', 'V4'], ['II', 'aVL', 'V2', 'V5'], ['III', 'aVF', 'V3', 'V6']]
DEPTHS = ('d10', 'd90'); COL = {'d10': '#1f5fbf', 'd90': '#d9480f'}
PX = 0.2            # mm per pixel of the rendered views
STEP, FRAME_MS, HOLD_MS = 3, 110, 3000
CMAP = matplotlib.colormaps['rainbow_r']   # red = earliest, purple = latest (as on a CARTO activation map)


def table(path, cols, dtype):
    return pd.read_csv(path, sep=r'\s+', header=None, skiprows=1, usecols=cols, dtype=dtype).to_numpy()


def unit(v):
    return v / np.linalg.norm(v)


def raster(xy, z, tris, vals, shade, extent):
    """z-buffered rasteriser: xy (n,2) view-plane mm, z (n,) toward the viewer, tris (m,3), vals (n,k) nodal values,
    shade (m,). Returns per-pixel interpolated values (ny,nx,k), shade (ny,nx) and coverage mask."""
    x0, x1, y0, y1 = extent
    nx, ny = int(np.ceil((x1 - x0) / PX)), int(np.ceil((y1 - y0) / PX))
    u, v = (xy[:, 0] - x0) / PX - 0.5, (y1 - xy[:, 1]) / PX - 0.5          # pixel centres at integers, row 0 on top
    bz = np.full(nx * ny, -np.inf); bt = np.full(nx * ny, -1); bw = np.zeros((nx * ny, 3))
    span = np.maximum(np.ptp(u[tris], 1), np.ptp(v[tris], 1))
    for K in np.unique(np.ceil(span).astype(int) + 2):
        sel = np.where(np.ceil(span).astype(int) + 2 == K)[0]
        for c0 in range(0, len(sel), max(1, 3_000_000 // (K * K))):
            tt = tris[sel[c0:c0 + max(1, 3_000_000 // (K * K))]]
            U, V, Z = u[tt], v[tt], z[tt]
            iu = np.floor(U.min(1))[:, None, None] + np.arange(K)[None, :, None] + 0 * np.arange(K)[None, None, :]
            iv = np.floor(V.min(1))[:, None, None] + 0 * np.arange(K)[None, :, None] + np.arange(K)[None, None, :]
            u0, u1, u2 = (U[:, i, None, None] for i in range(3)); v0, v1, v2 = (V[:, i, None, None] for i in range(3))
            den = (v1 - v2) * (u0 - u2) + (u2 - u1) * (v0 - v2)
            den = np.where(den == 0, np.nan, den)
            w0 = ((v1 - v2) * (iu - u2) + (u2 - u1) * (iv - v2)) / den
            w1 = ((v2 - v0) * (iu - u2) + (u0 - u2) * (iv - v2)) / den
            w2 = 1 - w0 - w1
            ok = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9) & (iu >= 0) & (iu < nx) & (iv >= 0) & (iv < ny)
            k, a, b = np.nonzero(ok)
            W = np.stack([w0[k, a, b], w1[k, a, b], w2[k, a, b]], 1)
            pix = (iv[k, a, b] * nx + iu[k, a, b]).astype(np.int64)
            zz = (W * Z[k]).sum(1)
            o = np.lexsort((-zz, pix)); first = np.unique(pix[o], return_index=True)[1]; o = o[first]
            upd = zz[o] > bz[pix[o]]; o = o[upd]
            bz[pix[o]] = zz[o]; bt[pix[o]] = sel[c0:c0 + max(1, 3_000_000 // (K * K))][k[o]]; bw[pix[o]] = W[o]
    hit = bt >= 0
    out = np.full((nx * ny, vals.shape[1]), np.nan)
    out[hit] = np.einsum('pi,pik->pk', bw[hit], vals[tris[bt[hit]]])
    sh = np.zeros(nx * ny); sh[hit] = shade[bt[hit]]
    return out.reshape(ny, nx, -1), sh.reshape(ny, nx), hit.reshape(ny, nx)


def colour(Tpix, sh, hit, t, tmax):
    """RGB image at time t: activated tissue in activation-time colour, resting tissue grey, the front (last 3 ms) light."""
    rgb = np.ones(Tpix.shape + (3,))
    act = hit & (Tpix <= t)
    base = np.where(act[..., None], CMAP(np.clip(Tpix / tmax, 0, 1))[..., :3], 0.80)
    front = act & (Tpix > t - 3) & (t < tmax)
    base = np.where(front[..., None], 0.45 * base + 0.55, base)
    rgb[hit] = (base * sh[..., None])[hit]
    return rgb


# ---- data ----
pts = table(os.path.join(MESH, 'biv.pts'), [0, 1, 2], np.float64) / 1000.0          # um -> mm
epi = table(os.path.join(MESH, 'surfaces', 'epi.surf'), [1, 2, 3], np.int64)
lv_endo = table(os.path.join(MESH, 'surfaces', 'lv_endo.surf'), [1, 2, 3], np.int64)
apex = pts[int(open(os.path.join(MESH, 'surfaces', 'apex.vtx')).read().split()[2])]
base = pts[np.loadtxt(os.path.join(MESH, 'surfaces', 'mv_rim.vtx'), skiprows=2, dtype=int)].mean(0)
S = {s['id']: s for s in json.load(open(os.path.join(MESH, 'sites.json')))}
site = {d: S[f'{SITE}_{d}'] for d in DEPTHS}
T = {d: np.load(os.path.join(MAPS, f'{SITE}_{d}.T.npy')).astype(float) for d in DEPTHS}
E = {d: np.load(os.path.join(MAPS, f'{SITE}_{d}.ecg.npy')).astype(float) for d in DEPTHS}
assert all(len(T[d]) == len(pts) for d in DEPTHS)
tmax = max(T[d].max() for d in DEPTHS)
vals = np.stack([T[d] for d in DEPTHS], 1)

r = pd.read_csv(os.path.join(REPO, 'analysis', 'audit_addendum_2026-10-14', 'rescore', 'per_site.csv'))
r = r[(r.heart == H) & (r.network == 'net') & (r['mode'] == 'stim') & (r.noise == 'clean')].set_index('site')
q = pd.read_csv(os.path.join(REPO, 'analysis', 'v51_2026-10-15', '02_measure_040', 'per_site.csv'))
q = q[(q.heart == H) & (q.network == 'net') & (q['mode'] == 'stim') & (q.rule == 'primary')].set_index('site')
crit = {}
for d in DEPTHS:
    a = r.loc[f'{SITE}_{d}']
    crit[d] = (f"QRS {a.qrs_duration_any_lead_ms:.0f} ms   pseudo-delta {a.pseudo_delta_ms:.0f} ms   IDT V2 {a.idt_v2_ms:.0f} ms\n"
               f"shortest RS {a.srs_ms:.0f} ms   MDI {a.mdi_daniels:.2f}   q in I {'yes' if q.loc[f'{SITE}_{d}', 'q_lead_I'] else 'no'}")

# ---- view 1: the heart from outside, facing the site ----
LA = unit(base - apex)
pe = pts[site['d10']['epi_end_node']]
c_ax = apex + np.dot(pe - apex, LA) * LA
V = unit((pe - c_ax) - np.dot(pe - c_ax, LA) * LA)          # toward the viewer
R = np.cross(LA, V)
rel = pts - c_ax
xy = np.stack([rel @ R, rel @ LA], 1); z = rel @ V
nrm = np.cross(pts[epi[:, 1]] - pts[epi[:, 0]], pts[epi[:, 2]] - pts[epi[:, 0]])
shade = 0.35 + 0.65 * np.abs(nrm @ V) / np.linalg.norm(nrm, axis=1)
en = np.unique(epi)
ext3 = (xy[en, 0].min() - 3, xy[en, 0].max() + 3, xy[en, 1].min() - 3, xy[en, 1].max() + 3)
T3, S3, M3 = raster(xy, z, epi, vals, shade, ext3)

# ---- view 2: cut through the pacing line (contains both site nodes; near short-axis), seen from the apex ----
P0 = 0.5 * (pts[site['d10']['node']] + pts[site['d90']['node']])
ln = unit(pts[site['d90']['node']] - pts[site['d10']['node']])
NC = unit(LA - np.dot(LA, ln) * ln)                          # plane normal, toward the base
elem = table(os.path.join(MESH, 'biv.elem'), [1, 2, 3, 4], np.int64)
dn = (pts - P0) @ NC; dn[dn == 0] = 1e-9
de = dn[elem]; X = elem[(de.min(1) < 0) & (de.max(1) > 0)]; de = dn[X]
Rc = unit((pe - c_ax) - np.dot(pe - c_ax, NC) * NC); Uc = np.cross(-NC, Rc)
P, Vl, M = [], [], []
for i, j in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
    lam = de[:, i] / (de[:, i] - de[:, j])
    P.append(pts[X[:, i]] + lam[:, None] * (pts[X[:, j]] - pts[X[:, i]]))
    Vl.append(vals[X[:, i]] + lam[:, None] * (vals[X[:, j]] - vals[X[:, i]]))
    M.append((de[:, i] < 0) != (de[:, j] < 0))
P, Vl, M = np.stack(P, 1), np.stack(Vl, 1), np.stack(M, 1)        # (nt, 6, .)
p2 = np.stack([(P - P0) @ Rc, (P - P0) @ Uc], -1)
cen = (p2 * M[..., None]).sum(1) / M.sum(1)[:, None]
ang = np.where(M, np.arctan2(p2[..., 1] - cen[:, None, 1], p2[..., 0] - cen[:, None, 0]), np.inf)
o = np.argsort(ang, 1) + 6 * np.arange(len(X))[:, None]
tri2 = np.concatenate([o[:, [0, 1, 2]], o[M.sum(1) == 4][:, [0, 2, 3]]])
cxy, cval = p2.reshape(-1, 2), Vl.reshape(-1, 2)
ext2 = (cxy[M.ravel()][:, 0].min() - 3, cxy[M.ravel()][:, 0].max() + 3, cxy[M.ravel()][:, 1].min() - 3, cxy[M.ravel()][:, 1].max() + 3)
T2, S2, M2 = raster(cxy, np.zeros(len(cxy)), tri2, cval, np.full(len(tri2), 1.0), ext2)

# ---- numbers for the report ----
lvn = np.unique(lv_endo)
for d in DEPTHS:
    p = pts[site[d]['node']]
    print(f"{d}: node {site[d]['node']} depth {site[d]['depth_achieved']} ({site[d]['depth_achieved_mm']} of {site[d]['wall_thickness_mm']} mm), "
          f"off cut plane {abs(np.dot(p - P0, NC)):.3f} mm, cut tilted {np.degrees(np.arccos(np.dot(NC, LA))):.1f} deg from short axis; total activation {T[d].max():.1f} ms; "
          f"first epicardium {T[d][en].min():.1f} ms; first LV endocardium {T[d][lvn].min():.1f} ms")

# ---- figure ----
fig = plt.figure(figsize=(11, 12.5), dpi=72)
fig.text(0.5, 0.988, 'Paced beat from the mid LV free wall (inferolateral), control heart: 10 % vs 90 % wall depth',
         ha='center', va='top', fontsize=14, weight='bold')
for k, line in enumerate([f'Model v5 (adopted 13 Oct): saved 14 Oct beats with the Purkinje network; heart {H}, site {SITE}.',
                          'Top: the heart from outside, facing the site (base up). Middle: a cut across the heart through the pacing line, '
                          'seen from the apex. Star = pacing site.',
                          'Colour = activation time after the stimulus (red earliest, purple latest); grey = not yet activated; '
                          'light band = the wavefront.']):
    fig.text(0.5, 0.966 - 0.0135 * k, line, ha='center', va='top', fontsize=9)
tt = fig.text(0.5, 0.925, '', ha='center', va='top', fontsize=13, weight='bold')
ims, cuts = {}, {}
for c, d in enumerate(DEPTHS):
    x0 = 0.03 + 0.5 * c
    s = site[d]
    fig.text(x0 + 0.22, 0.905, f"Paced at {round(100 * s['depth_target'])} % depth", ha='center', va='top', fontsize=11,
             color=COL[d], weight='bold')
    fig.text(x0 + 0.22, 0.89, f"{s['depth_achieved_mm']:.1f} mm from the endocardium (wall {s['wall_thickness_mm']:.1f} mm)",
             ha='center', va='top', fontsize=9.5, color=COL[d])
    a = fig.add_axes([x0, 0.645, 0.44, 0.235]); a.set_axis_off()
    ims[d] = a.imshow(colour(T3[..., c], S3, M3, 0, tmax), extent=ext3, interpolation='antialiased')
    ps = pts[s['node']] - c_ax
    a.plot(ps @ R, ps @ LA, marker='*', ms=15, mfc='white', mec='black', mew=1.2)
    b = fig.add_axes([x0, 0.43, 0.44, 0.205]); b.set_axis_off()
    cuts[d] = b.imshow(colour(T2[..., c], S2, M2, 0, tmax), extent=ext2, interpolation='antialiased')
    pc = pts[s['node']] - P0
    b.plot(pc @ Rc, pc @ Uc, marker='*', ms=15, mfc='white', mec='black', mew=1.2)
    fig.text(x0 + 0.22, 0.424, crit[d], ha='center', va='top', fontsize=9.5, color=COL[d], family='monospace')
cax = fig.add_axes([0.488, 0.45, 0.012, 0.40])
fig.colorbar(cm.ScalarMappable(mcolors.Normalize(0, tmax), CMAP), cax=cax)
cax.set_title('ms', fontsize=8.5); cax.tick_params(labelsize=8)
fig.text(0.5, 0.392, 'Criteria measured from the stimulus on the clean ECG (14 Oct rescore); q in I by the 0.4.0 rule.\n'
         'Published epicardial cut-offs: pseudo-delta >= 34 ms, IDT >= 85 ms, shortest RS >= 121 ms, MDI >= 0.55.',
         ha='center', va='top', fontsize=8.5, color='0.25')

n = max(len(E[d]) for d in DEPTHS)
lo = min(E[d].min() for d in DEPTHS) - 0.15; hi = max(E[d].max() for d in DEPTHS) + 0.15
bold, curs = [], []
for i, row in enumerate(GRID):
    for j, lead in enumerate(row):
        a = fig.add_axes([0.04 + 0.24 * j, 0.255 - 0.11 * i, 0.225, 0.10])
        k = LEADS.index(lead)
        for x in range(0, n + 1, 40):
            a.axvline(x, color='#f2c4c4', lw=0.6, zorder=0)
        for y in np.arange(np.ceil(lo / 0.5) * 0.5, hi, 0.5):
            a.axhline(y, color='#f2c4c4', lw=0.6, zorder=0)
        for d in DEPTHS:
            a.plot(np.arange(len(E[d])), E[d][:, k], color=COL[d], lw=1.0, alpha=0.25)
            bold.append((a.plot([], [], color=COL[d], lw=1.6)[0], d, k))
        curs.append(a.axvline(0, color='black', lw=0.8))
        a.set_xlim(0, n); a.set_ylim(lo, hi)
        a.set_yticks([]); a.set_xticks(range(0, n + 1, 40) if i == 2 else [])
        a.tick_params(labelsize=7.5)
        for sp in a.spines.values():
            sp.set_color('0.7')
        a.text(0.02, 0.95, lead, transform=a.transAxes, va='top', fontsize=10, weight='bold')
        if i == 2 and j == 0:
            a.set_xlabel('ms after the stimulus (grid 40 ms, 0.5 mV)', fontsize=8)
fig.text(0.04, 0.367, '12-lead ECG, same scale in every lead', fontsize=9.5, va='top')
fig.text(0.70, 0.367, '10 % depth', fontsize=9.5, va='top', color=COL['d10'], weight='bold')
fig.text(0.82, 0.367, '90 % depth', fontsize=9.5, va='top', color=COL['d90'], weight='bold')


def draw(t):
    tt.set_text(f't = {t:.0f} ms after the stimulus')
    for c, d in enumerate(DEPTHS):
        ims[d].set_data(colour(T3[..., c], S3, M3, t, tmax))
        cuts[d].set_data(colour(T2[..., c], S2, M2, t, tmax))
    for ln, d, k in bold:
        m = min(len(E[d]), int(t) + 1); ln.set_data(np.arange(m), E[d][:m, k])
    for cl in curs:
        cl.set_xdata([t, t])
    fig.canvas.draw()
    return Image.frombuffer('RGBA', fig.canvas.get_width_height(), fig.canvas.buffer_rgba(), 'raw', 'RGBA', 0, 1).convert('RGB')


times = list(range(0, int(np.ceil(tmax)) + STEP, STEP))
times[-1] = int(np.ceil(tmax))
frames = [draw(t) for t in times]
w, h = frames[0].size; combo = Image.new('RGB', (w, 2 * h)); combo.paste(frames[-1], (0, 0)); combo.paste(frames[len(frames) // 5], (0, h))
pal = combo.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)   # palette from a late and an early frame
gif = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
gif[0].save(OUT + '.gif', save_all=True, append_images=gif[1:], duration=[FRAME_MS] * (len(gif) - 1) + [HOLD_MS], loop=0,
            optimize=False, disposal=1)
fig.set_dpi(110); draw(times[-1]); fig.savefig(OUT + '_final.png', dpi=110)
print(f'wrote {OUT}.gif ({os.path.getsize(OUT + ".gif") / 1e6:.1f} MB, {len(gif)} frames) and {OUT}_final.png')
