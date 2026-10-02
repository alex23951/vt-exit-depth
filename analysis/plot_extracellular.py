#!/usr/bin/env python
"""
Overlay recovered extracellular potentials (unipolar electrograms) from two
runs of the 07_extracellular wedge example, e.g. endocardial vs epicardial
stimulation.

Usage (from the project root, venv active):
    python analysis/plot_extracellular.py runs/<endo_run> runs/<epi_run> \
        --labels "Endo stim" "Epi stim" --out figures/<name>.png

Writes the figure (PNG) and a CSV of all traces next to it.
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from carputils.carpio import igb

# Recording points written by sims/07_extracellular/run.py (writeECGgrid),
# z in mm; +z = endocardial side. Listed top-to-bottom, endo bath -> epi bath.
POINTS = [
    (6, 'Endo-side fluid, 10 mm from wall', 15),
    (5, 'Endo-side fluid, 5 mm from wall', 10),
    (2, 'Endocardial surface', 5),
    (1, 'Mid-wall', 0),
    (0, 'Epicardial surface', -5),
    (4, 'Epi-side fluid, 5 mm from wall', -10),
    (3, 'Epi-side fluid, 10 mm from wall', -15),
]

# Validated categorical slots 1 & 2 (dataviz reference palette, light mode)
COLORS = ['#2a78d6', '#eb6834']
STYLES = ['-', '--']
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
ZOOM_MS = 20


def load(run):
    f = igb.IGBFile(os.path.join(run, 'phie_recovery.igb'))
    h = f.header()
    data = f.data().reshape(h['t'], h['x'])
    t = h.get('org_t', 0.0) + np.arange(h['t']) * h['inc_t']
    return t, data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('runs', nargs=2)
    p.add_argument('--labels', nargs=2, default=None)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    labels = a.labels or [os.path.basename(r.rstrip('/')) for r in a.runs]

    traces = [load(r) for r in a.runs]

    plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2,
                         'xtick.color': INK2, 'ytick.color': INK2,
                         'axes.labelcolor': INK2})
    fig, axes = plt.subplots(len(POINTS), 2, figsize=(11, 12.5), sharex='col',
                             gridspec_kw={'width_ratios': [2.2, 1]})
    fig.patch.set_facecolor('#fcfcfb')

    for row, (idx, name, z) in enumerate(POINTS):
        for col in range(2):
            ax = axes[row, col]
            ax.set_facecolor('#fcfcfb')
            ax.axvspan(0, 1, color=GRID, lw=0)          # 1 ms stimulus pulse
            ax.axhline(0, color=GRID, lw=1)
            for (t, d), lab, c, ls in zip(traces, labels, COLORS, STYLES):
                ax.plot(t, d[:, idx], color=c, ls=ls, lw=1.6, label=lab)
            for s in ('top', 'right'):
                ax.spines[s].set_visible(False)
            if col == 1:
                ax.set_xlim(0, ZOOM_MS)
                t0 = traces[0][0]
                win = t0 <= ZOOM_MS
                lo = min(d[win, idx].min() for _, d in traces)
                hi = max(d[win, idx].max() for _, d in traces)
                pad = 0.08 * (hi - lo or 1)
                ax.set_ylim(lo - pad, hi + pad)
            else:
                ax.set_xlim(traces[0][0][0], traces[0][0][-1])
                ax.set_ylabel('mV')
                ax.set_title(f'Point {idx}: {name} (z = {z:+d} mm)',
                             loc='left', fontsize=9.5, color=INK)
    axes[0, 1].set_title(f'Zoom: first {ZOOM_MS} ms', loc='left',
                         fontsize=9.5, color=INK)
    axes[-1, 0].set_xlabel('Time after stimulus (ms)')
    axes[-1, 1].set_xlabel('Time after stimulus (ms)')
    axes[0, 0].legend(loc='upper right', frameon=False, fontsize=9)
    fig.suptitle('Recovered extracellular potentials: ' + ' vs '.join(labels)
                 + '\n(grey band = 1 ms stimulus; each row has its own vertical scale)',
                 x=0.01, ha='left', fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    fig.savefig(a.out, dpi=150)

    # Table view of the same data
    t = traces[0][0]
    cols, header = [t], ['time_ms']
    for (_, d), lab in zip(traces, labels):
        for idx, name, _ in POINTS:
            cols.append(d[:, idx])
            header.append(f'{lab} | pt{idx} {name}')
    csv = os.path.splitext(a.out)[0] + '.csv'
    np.savetxt(csv, np.column_stack(cols), delimiter=',',
               header=','.join(header), comments='', fmt='%.6g')
    print('wrote', a.out, 'and', csv)


if __name__ == '__main__':
    main()
