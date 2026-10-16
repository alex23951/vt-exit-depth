"""Audit 10: junction (PMJ) density by region; His / bundle landmarks; AP template shape; epicardial-face sanity. Read only."""
import json
import numpy as np
from scipy.spatial import cKDTree
OUT = {}
for h in ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']:
    B = f'data/biv/{h}/'
    P = np.loadtxt(B + 'biv.pts', skiprows=1) / 1e3
    z, phi = np.loadtxt(B + 'uvc/z.dat'), np.degrees(np.loadtxt(B + 'uvc/phi.dat'))
    rd = lambda n: np.loadtxt(B + f'surfaces/{n}.vtx', skiprows=2, dtype=np.int64)
    sf = lambda n: np.loadtxt(B + f'surfaces/{n}.surf', skiprows=1, usecols=(1, 2, 3), dtype=np.int64)
    lv, rv, epi = rd('lv_endo'), rd('rv_endo'), rd('epi')
    net = np.load(B + 'purkinje/network.npz'); pm = net['nodes'][net['pmj']]; kind = net['kind'][net['pmj']]
    te, tl, tr = cKDTree(P[epi]), cKDTree(P[lv]), cKDTree(P[rv])
    lv_sep = lv[tr.query(P[lv])[0] < te.query(P[lv])[0]]; rv_sep = rv[tl.query(P[rv])[0] < te.query(P[rv])[0]]
    dens = {}
    for side, nodes, tri, sep in (('LV', lv, sf('lv_endo'), lv_sep), ('RV', rv, sf('rv_endo'), rv_sep)):
        a = 0.5 * np.linalg.norm(np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]]), axis=1) / 100     # cm2
        na = np.bincount(tri.ravel(), weights=np.repeat(a / 3, 3), minlength=len(P))
        issep = np.zeros(len(P), bool); issep[sep] = True
        pk = pm[np.char.endswith(kind, side.lower())]
        for band, (lo, hi) in (('apical z<0.33', (0, 0.33)), ('mid 0.33-0.67', (0.33, 0.67)), ('basal 0.67-0.9', (0.67, 0.9)), ('top z>0.9', (0.9, 1.01))):
            for wall, ws in (('septal', True), ('free', False)):
                m = (z[nodes] >= lo) & (z[nodes] < hi) & (issep[nodes] == ws)
                area = na[nodes][m].sum()
                mp = (z[pk] >= lo) & (z[pk] < hi) & (issep[pk] == ws)
                dens[f'{side} {wall} {band}'] = {'area_cm2': round(float(area), 1), 'pmj': int(mp.sum()), 'per_cm2': round(float(mp.sum() / area), 1) if area > 0 else None}
    s = json.load(open(B + 'purkinje/summary.json'))
    OUT[h] = {'pmj_density_by_region(per cm2 of endocardium)': dens, 'landmarks': s['landmarks'], 'proximal_mm': s['proximal_mm'], 'proximal_speed_m_s': s['proximal_speed_m_s'],
              'pmj_on_endo_surface': bool(np.isin(pm, np.concatenate([lv, rv])).all()), 'his_to_lv_sites_ms': s['his_to_lv_sites_ms']}
    # epicardial faces: any face with all three nodes on an endocardial surface?
    E3 = sf('epi'); endo = np.zeros(len(P), bool); endo[lv] = True; endo[rv] = True
    OUT[h]['epi_faces_all_nodes_on_endo'] = int(endo[E3].all(1).sum()); OUT[h]['epi_faces'] = int(len(E3))
    print(h, json.dumps({k: v for k, v in OUT[h].items() if k != 'pmj_density_by_region(per cm2 of endocardium)'}, default=str)[:900])
    for k, v in dens.items(): print('   ', k, v)
# AP template (control heart full-QRS monodomain beat)
for h, run in (('Y5HYEDL4', 'runs/2026-10-02_biv_fullqrs'), ('6G8DD8S5', 'runs/2026-10-03_6G8DD8S5_fullqrs'), ('7D98EVAR', 'runs/2026-10-03_7D98EVAR_fullqrs')):
    try:
        b = open(run + '/vm.igb', 'rb').read(); hd = b[:1024].decode('latin1'); x = int(hd.split('x:')[1].split()[0])
        lat = np.loadtxt(run + '/init_acts_LATs-thresh.dat'); k = int(np.argmin(np.abs(lat - 60)))
        V = np.frombuffer(b[1024:], dtype='<f4').reshape(-1, x)[:, k].astype(float); del b
        dv = np.diff(V)
        OUT[h + '_template'] = {'node': k, 'lat_ms': float(lat[k]), 'frames': len(V), 'dt_ms': 1.0, 'rest_mV': round(V[0], 1), 'peak_mV': round(V.max(), 1),
                                'max_dVdt_mV_per_ms(1ms frames)': round(dv.max(), 1), 'upstroke_10_90_ms': int(np.sum((V > V[0] + 0.1 * (V.max() - V[0])) & (V < V[0] + 0.9 * (V.max() - V[0])) & (np.arange(len(V)) < np.argmax(V) + 1))),
                                'V_at_lat+20ms': round(float(np.interp(lat[k] + 20, np.arange(len(V)), V)), 1), 'V_last': round(V[-1], 1)}
        print(h + '_template', OUT[h + '_template'])
    except Exception as ex:
        print('template', h, ex)
json.dump(OUT, open('analysis/audit_2026-10-13/a10_pmj_template_epi.json', 'w'), indent=1, default=str)
