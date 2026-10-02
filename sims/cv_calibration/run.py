#!/usr/bin/env python
"""
Transmural CV calibration wedge.

Builds a small transmural block (default 2 x 2 x 10 mm) with orthotropic fibres
(Bayer 2012 rule: fibre +60 deg endo -> -60 deg epi, sheet -65 deg endo -> +25 deg epi),
activates the whole endocardial surface at once, and reports the activation transit
time across the outer part of the wall (default 1 to 7 mm below the epicardium).

Axis convention (checked against the mesher's .lon output, see LABNOTES 2026-10-02):
z is transmural, endocardium at z = -wall/2 (mesher applies the "Endo" angles at
z min), epicardium at z = +wall/2.

Conductivities come from tuneCV runs (one json per CV) so that fibre, sheet and
sheet-normal CVs are each specified in m/s.
"""

import json
import os

import numpy as np

from carputils import mesh, tools
from carputils.carpio import txt
from carputils.model import Stimulus, optionlist
from carputils.model.lat import Lat

EXAMPLE_DESCRIPTIVE_NAME = 'Transmural CV calibration wedge'
EXAMPLE_DIR = os.path.dirname(__file__)
CALLER_DIR = os.getcwd()


def parser():
    p = tools.standard_parser()
    g = p.add_argument_group('calibration options')
    g.add_argument('--resolution', type=float, default=500., help='mesh resolution [um]')
    g.add_argument('--wall', type=float, default=10., help='wall thickness [mm]')
    g.add_argument('--lateral', type=float, default=2., help='in-plane block size [mm]')
    g.add_argument('--fibre', nargs=2, type=float, default=[60., -60.], help='fibre angle endo epi [deg]')
    g.add_argument('--sheet', nargs=2, type=float, default=[-65., 25.], help='sheet angle endo epi [deg]')
    g.add_argument('--tune-f', required=True, help='tuneCV json for the fibre CV')
    g.add_argument('--tune-s', required=True, help='tuneCV json for the sheet CV')
    g.add_argument('--tune-n', required=True, help='tuneCV json for the sheet-normal CV')
    g.add_argument('--model', default='Tomek', help='ionic model')
    g.add_argument('--dt', type=float, default=10., help='time step [us], match tuneCV')
    g.add_argument('--duration', type=float, default=60., help='simulated time [ms]')
    g.add_argument('--depths', nargs=2, type=float, default=[1., 7.],
                   help='depths below epicardium [mm] between which transit time is measured')
    return p


def jobID(args):
    return 'cvcal'


def load_g(fname):
    with open(fname) as f:
        d = json.load(f)
    return d['results']['gi'], d['results']['ge'], d['params']['velocity']


@tools.carpexample(parser, jobID)
def run(args, job):
    wall, lat_sz, h = args.wall, args.lateral, args.resolution * 1e-3

    geom = mesh.Block(size=(lat_sz, lat_sz, wall), resolution=h, etype='tetra')
    geom.set_fibres(args.fibre[0], args.fibre[1], args.sheet[0], args.sheet[1])
    meshname = mesh.generate(geom)

    gif, gef, vf = load_g(args.tune_f)
    gis, ges, vs = load_g(args.tune_s)
    gin, gen, vn = load_g(args.tune_n)

    # whole endocardial surface (z min) stimulated at once
    um = 1e3
    stim = Stimulus('endo', **{'crct.type': 0,
                               'pulse.strength': 100.0,
                               'ptcl.duration': 1.0,
                               'ptcl.npls': 1,
                               'elec.p0': [-lat_sz * um, -lat_sz * um, -wall / 2 * um - 10],
                               'elec.p1': [lat_sz * um, lat_sz * um, -wall / 2 * um + 10]})
    lat = Lat('LATs', all=0, measurand=0, threshold=-10, method=1)

    cmd = tools.carp_cmd()
    cmd += ['-num_imp_regions', 1,
            '-imp_region[0].im', args.model,
            '-num_gregions', 1,
            '-gregion[0].num_IDs', 1,
            '-gregion[0].ID[0]', 1,
            '-gregion[0].g_il', gif, '-gregion[0].g_el', gef,
            '-gregion[0].g_it', gis, '-gregion[0].g_et', ges,
            '-gregion[0].g_in', gin, '-gregion[0].g_en', gen,
            '-bidomain', 0,
            '-dt', args.dt,
            '-parab_solve', 1,
            '-spacedt', 1.0,
            '-timedt', 1.0,
            '-meshname', meshname,
            '-tend', args.duration,
            '-simID', job.ID]
    cmd += optionlist([stim, lat])
    job.carp(cmd, 'Transmural CV calibration')

    if args.dry:
        return

    # transit time across the chosen depth band
    pts = np.loadtxt(meshname + '.pts', skiprows=1) / um   # mm
    act = np.loadtxt(os.path.join(job.ID, 'init_acts_LATs-thresh.dat'))
    z_epi = wall / 2
    res = {'vf': vf, 'vs': vs, 'vn': vn, 'g': [gif, gef, gis, ges, gin, gen]}
    times = []
    for d in args.depths:
        sel = np.abs(pts[:, 2] - (z_epi - d)) < 1e-3
        if not sel.any():
            raise RuntimeError(f'no mesh nodes at {d} mm below epi; pick depths on the grid')
        times.append(float(act[sel].mean()))
    res['depths_mm'] = args.depths
    res['lat_ms'] = times
    res['transit_ms'] = times[0] - times[1]
    res['total_activation_ms'] = float(act[act > 0].max())
    # transmural LAT profile (mean per z level) for the record
    zs = np.unique(np.round(pts[:, 2], 4))
    res['profile'] = [[float(z), float(act[np.abs(pts[:, 2] - z) < 1e-3].mean())] for z in zs]
    # endo surface -> epi surface crossing time
    res['fullwall_ms'] = res['profile'][-1][1] - res['profile'][0][1]
    with open(os.path.join(job.ID, 'transit.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print(f"CVs f/s/n = {vf}/{vs}/{vn} m/s -> transit {args.depths[1]}->{args.depths[0]} mm "
          f"below epi = {res['transit_ms']:.2f} ms; total activation {res['total_activation_ms']:.1f} ms")


if __name__ == '__main__':
    run()
