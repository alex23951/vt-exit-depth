#!/usr/bin/env python
"""
Meshalyzer-free pictures of the 07_extracellular wedge: activation-time map
and membrane-voltage snapshots, seen face-on (the wedge is one element thick,
so the y-z face shows everything).

Usage (from the project root, venv active):
    python analysis/plot_wedge_maps.py runs/<endo_run> runs/<epi_run> \
        --labels "Endo stim" "Epi stim" --out figures/<name>.png
"""
import argparse
import os
import re

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from carputils.carpio import igb

INK, INK2 = '#0b0b0b', '#52514e'
SNAP_MS = [2, 6, 10, 14, 18, 22]


def load(run):
    par = open(os.path.join(run, 'parameters.par')).read()
    mesh = re.search(r'^meshname\s*=\s*(\S+)', par, re.M).group(1)
    root = os.path.dirname(run.rstrip('/'))
    pts = np.loadtxt(os.path.join(root, mesh + '.pts'), skiprows=1) / 1000.  # mm
    lat = np.loadtxt(os.path.join(run, 'init_acts_LATs-thresh.dat'))
    f = igb.IGBFile(os.path.join(run, 'vm.igb'))
    h = f.header()
    vm = f.data().reshape(h['t'], h['x'])
    return pts, lat, vm, h['inc_t']


def face(pts):
    """Keep nodes on one x-face and triangulate them in the (y, z) plane."""
    keep = np.isclose(pts[:, 0], pts[:, 0].min())
    return keep, mtri.Triangulation(pts[keep, 1], pts[keep, 2])


def label_sides(ax):
    ax.set_ylabel('Depth (mm)')
    ax.text(1.01, 1.0, 'endo', transform=ax.transAxes, va='top', fontsize=8, color=INK2)
    ax.text(1.01, 0.0, 'epi', transform=ax.transAxes, va='bottom', fontsize=8, color=INK2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('runs', nargs=2)
    p.add_argument('--labels', nargs=2, required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()

    data = [load(r) for r in a.runs]
    nrow = 1 + len(SNAP_MS)
    fig, axes = plt.subplots(nrow, 2, figsize=(12, 1.55 * nrow + 1.2),
                             sharex=True, sharey=True)
    fig.patch.set_facecolor('#fcfcfb')

    latmax = max(lat.max() for _, lat, _, _ in data)
    for col, ((pts, lat, vm, dt), lab) in enumerate(zip(data, a.labels)):
        keep, tri = face(pts)
        ax = axes[0, col]
        cs = ax.tricontourf(tri, lat[keep], levels=np.arange(0, latmax + 2, 2), cmap='viridis_r')
        ax.tricontour(tri, lat[keep], levels=np.arange(0, latmax + 5, 5), colors='w', linewidths=0.5)
        ax.set_title(f'{lab}: activation time (white lines every 5 ms)',
                     loc='left', fontsize=9.5, color=INK)
        for r, t in enumerate(SNAP_MS, start=1):
            ax = axes[r, col]
            vs = ax.tripcolor(tri, vm[int(round(t / dt)), keep], cmap='RdBu_r',
                              vmin=-90, vmax=40, shading='gouraud')
            ax.set_title(f'{lab}: membrane voltage at {t} ms', loc='left',
                         fontsize=9.5, color=INK)
        for ax in axes[:, col]:
            ax.set_aspect('equal')
            if col == 1:
                label_sides(ax)
            else:
                ax.set_ylabel('Depth (mm)')
    axes[-1, 0].set_xlabel('Apex  <-  position along wedge (mm)  ->  base')
    axes[-1, 1].set_xlabel('Apex  <-  position along wedge (mm)  ->  base')
    fig.colorbar(cs, ax=axes[0, :], label='ms', shrink=0.9, pad=0.04)
    fig.colorbar(vs, ax=axes[1:, :], label='Vm (mV)', shrink=0.5, pad=0.04)
    fig.suptitle('Wedge seen face-on (top edge = endocardium, bottom edge = epicardium)',
                 x=0.01, ha='left', fontsize=11, color=INK)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    fig.savefig(a.out, dpi=130)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
