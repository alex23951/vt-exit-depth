#!/usr/bin/env python
"""
Anisotropic transmural wedge with a fast endocardial layer.

Geometry (same footprint as the 07_extracellular wedge): one element thick (x),
50 mm apex-to-base (y, apex at y = -25 mm, base at y = +25 mm), 10 mm wall (z).
Endocardium at z = -5 mm, epicardium at z = +5 mm (the mesher applies its "Endo"
fibre angles at z min; see LABNOTES 2026-10-02).

Myocardium: fibre +60 -> -60 deg (endo -> epi), sheets parallel to the wall
(sheet angle 90 deg throughout, option (a) chosen by Alex 2026-10-02), so the
sheet-normal axis is transmural. CVs fibre / sheet / sheet-normal set via tuneCV
files (default 0.6 / 0.4 / 0.45 m/s at 0.5 mm).

Fast endocardial layer: isotropic (default 2.0 m/s), first 0.8 mm of wall,
covering 10-90 % of apex-to-base (none in the apical and basal 10 %).

Stimulus modes:
  endo-all   : whole endocardial surface at once (normal endo-first activation)
  endo-point : small endocardial pad at mid apex-to-base
"""

import json
import os

import numpy as np

from carputils import mesh, tools
from carputils.model import Stimulus, optionlist
from carputils.model.lat import Lat

EXAMPLE_DESCRIPTIVE_NAME = 'Anisotropic wedge with fast endocardial layer'
EXAMPLE_DIR = os.path.dirname(__file__)
CALLER_DIR = os.getcwd()

TAG_MYO = 1
TAG_FAST = 2


def parser():
    p = tools.standard_parser()
    g = p.add_argument_group('wedge options')
    g.add_argument('--resolution', type=float, default=500., help='mesh resolution [um]')
    g.add_argument('--wall', type=float, default=10., help='wall thickness [mm]')
    g.add_argument('--length', type=float, default=50., help='apex-to-base length [mm]')
    g.add_argument('--fibre', nargs=2, type=float, default=[60., -60.], help='fibre angle endo epi [deg]')
    g.add_argument('--sheet', nargs=2, type=float, default=[90., 90.], help='sheet angle endo epi [deg]')
    g.add_argument('--tune-f', required=True, help='tuneCV json, fibre CV')
    g.add_argument('--tune-s', required=True, help='tuneCV json, sheet CV')
    g.add_argument('--tune-n', required=True, help='tuneCV json, sheet-normal CV')
    g.add_argument('--tune-fast', default=None, help='tuneCV json, fast endocardial layer CV (omit for no layer)')
    g.add_argument('--fast-thickness', type=float, default=0.8, help='fast layer thickness [mm]')
    g.add_argument('--fast-extent', nargs=2, type=float, default=[0.10, 0.90],
                   help='fast layer apex-to-base extent, fractions (0 = apex, 1 = base)')
    g.add_argument('--stim', choices=['endo-all', 'endo-point'], default='endo-all')
    g.add_argument('--stim-strength', type=float, default=100., help='stimulus current [uA/cm^3]')
    g.add_argument('--stim-depth', type=float, default=0.0, help='stimulus pad depth into the wall [mm]; 0 = surface nodes only')
    g.add_argument('--model', default='Tomek', help='ionic model')
    g.add_argument('--dt', type=float, default=10., help='time step [us], match tuneCV')
    g.add_argument('--duration', type=float, default=80., help='simulated time [ms]')
    return p


def jobID(args):
    return 'wedge_aniso'


def load_g(fname):
    with open(fname) as f:
        d = json.load(f)
    return d['results']['gi'], d['results']['ge'], d['params']['velocity']


@tools.carpexample(parser, jobID)
def run(args, job):
    h = args.resolution * 1e-3
    W, L, T = h, args.length, args.wall
    um = 1e3

    geom = mesh.Block(size=(W, L, T), resolution=h, etype='tetra')
    geom.set_fibres(args.fibre[0], args.fibre[1], args.sheet[0], args.sheet[1])
    if args.tune_fast:
        y0 = -L / 2 + args.fast_extent[0] * L
        y1 = -L / 2 + args.fast_extent[1] * L
        geom.add_region(mesh.BoxRegion((-W, y0, -T / 2), (W, y1, -T / 2 + args.fast_thickness), TAG_FAST))
    meshname = mesh.generate(geom)

    gif, gef, vf = load_g(args.tune_f)
    gis, ges, vs = load_g(args.tune_s)
    gin, gen, vn = load_g(args.tune_n)
    greg = ['-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', TAG_MYO,
            '-gregion[0].g_il', gif, '-gregion[0].g_el', gef,
            '-gregion[0].g_it', gis, '-gregion[0].g_et', ges,
            '-gregion[0].g_in', gin, '-gregion[0].g_en', gen]
    ngreg = 1
    if args.tune_fast:
        gip, gep, vp = load_g(args.tune_fast)
        greg += ['-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', TAG_FAST,
                 '-gregion[1].g_il', gip, '-gregion[1].g_el', gep,
                 '-gregion[1].g_it', gip, '-gregion[1].g_et', gep,
                 '-gregion[1].g_in', gip, '-gregion[1].g_en', gep]
        ngreg = 2

    if args.stim == 'endo-all':
        p0 = [-W * um, -L / 2 * um - 10, -T / 2 * um - 10]
        p1 = [W * um, L / 2 * um + 10, -T / 2 * um + args.stim_depth * um + 10]
    else:
        pad = 500
        p0 = [-W * um, -pad, -T / 2 * um - 10]
        p1 = [W * um, pad, -T / 2 * um + max(pad, args.stim_depth * um + 10)]
    stim = Stimulus('endo', **{'crct.type': 0, 'pulse.strength': args.stim_strength,
                               'ptcl.duration': 1.0, 'ptcl.npls': 1,
                               'elec.p0': p0, 'elec.p1': p1})
    lat = Lat('LATs', all=0, measurand=0, threshold=-10, method=1)

    cmd = tools.carp_cmd()
    cmd += ['-num_imp_regions', 1, '-imp_region[0].im', args.model,
            '-num_gregions', ngreg] + greg
    cmd += ['-bidomain', 0, '-dt', args.dt, '-parab_solve', 1,
            '-spacedt', 1.0, '-timedt', 1.0,
            '-meshname', meshname, '-tend', args.duration, '-simID', job.ID]
    cmd += optionlist([stim, lat])
    job.carp(cmd, 'Anisotropic wedge')

    if args.dry:
        return

    # ---- summary ----
    pts = np.loadtxt(meshname + '.pts', skiprows=1) / um
    elem = np.loadtxt(meshname + '.elem', skiprows=1, usecols=(1, 2, 3, 4, 5)).astype(int)
    act = np.loadtxt(os.path.join(job.ID, 'init_acts_LATs-thresh.dat'))
    z_endo, z_epi = -T / 2, T / 2
    on = lambda z, y=None: (np.abs(pts[:, 2] - z) < 1e-3) & (True if y is None else np.abs(pts[:, 1] - y) < 1e-3)
    res = {'stim': args.stim, 'stim_strength': args.stim_strength, 'stim_depth_mm': args.stim_depth,
           'cv_f_s_n': [vf, vs, vn],
           'unactivated_nodes': int((act < 0).sum()),
           'total_activation_ms': float(act.max())}
    # realised fast layer: tetra volume / footprint
    if args.tune_fast:
        x = pts[elem[:, :4]]
        vol = np.abs(np.einsum('ij,ij->i', x[:, 1] - x[:, 0],
                               np.cross(x[:, 2] - x[:, 0], x[:, 3] - x[:, 0]))) / 6
        fast = elem[:, 4] == TAG_FAST
        foot = W * L * (args.fast_extent[1] - args.fast_extent[0])
        res['fast_layer_mean_thickness_mm'] = float(vol[fast].sum() / foot)
        res['fast_layer_cv'] = vp
    # transmural profile at mid apex-to-base (y = 0) and at the base (outside the layer)
    for name, y in (('mid', 0.0), ('base', L / 2 - 1.0), ('apex', -L / 2 + 1.0)):
        try:
            t1 = act[on(z_epi - 1.0, y)].mean()
            t7 = act[on(z_epi - 7.0, y)].mean()
            res[f'{name}_outer6mm_transit_ms'] = float(t1 - t7)
            res[f'{name}_endo_lat_ms'] = float(act[on(z_endo, y)].mean())
            res[f'{name}_epi_lat_ms'] = float(act[on(z_epi, y)].mean())
        except Exception:
            pass
    epi = on(z_epi)
    res['epi_first_ms'] = float(act[epi].min())
    res['epi_first_y_mm'] = float(pts[epi][np.argmin(act[epi]), 1])
    res['epi_last_ms'] = float(act[epi].max())
    endo = on(z_endo)
    res['endo_last_ms'] = float(act[endo].max())
    with open(os.path.join(job.ID, 'summary.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    run()
