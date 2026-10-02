#!/usr/bin/env python
"""
Step 9: 12-lead plot and simple QRS measures from openCARP lead-field ECG files.

Usage: python 09_plot_ecg.py <POSTPROC_DIR> <out.png> [--title TITLE]
QRS onset/offset rule (provisional, same for every run): global signal = sum over the
12 leads of |ECG|; onset = first time it exceeds 2 % of its maximum, offset = last time.
"""

import argparse
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

LEADS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('postproc')
    p.add_argument('png')
    p.add_argument('--title', default='')
    a = p.parse_args()
    d = {l: np.loadtxt(os.path.join(a.postproc, f'ECG_{l}.dat')) for l in LEADS}
    t = d['I'][:, 0]
    X = np.stack([d[l][:, 1] for l in LEADS])
    g = np.abs(X).sum(0)
    on_i = int(np.argmax(g > 0.02 * g.max()))
    off_i = int(len(g) - 1 - np.argmax(g[::-1] > 0.02 * g.max()))
    res = {'qrs_onset_ms': float(t[on_i]), 'qrs_offset_ms': float(t[off_i]),
           'qrs_duration_ms': float(t[off_i] - t[on_i]), 'leads': {}}
    for i, l in enumerate(LEADS):
        x = X[i, on_i:off_i + 1]
        res['leads'][l] = {'max_mV': float(x.max()), 'min_mV': float(x.min()),
                           'main_deflection': 'positive' if x.max() > -x.min() else 'negative',
                           'net_mV': float(x.max() + x.min())}
    fig, ax = plt.subplots(4, 3, figsize=(11, 10), sharex=True)
    lim = np.abs(X).max() * 1.05
    # layout: limb leads in columns 1-2, V1-V4 in column 3, V5/V6 on the bottom row
    order = [('I', 0, 0), ('II', 1, 0), ('III', 2, 0), ('aVR', 0, 1), ('aVL', 1, 1), ('aVF', 2, 1),
             ('V1', 0, 2), ('V2', 1, 2), ('V3', 2, 2), ('V4', 3, 2), ('V5', 3, 0), ('V6', 3, 1)]
    for l, r, c in order:
        axx = ax[r, c]
        axx.plot(t, d[l][:, 1], 'k', lw=1.2)
        axx.axhline(0, color='0.7', lw=0.6)
        axx.axvspan(t[on_i], t[off_i], color='0.93', zorder=0)
        axx.set_ylim(-lim, lim)
        axx.set_title(l, loc='left', fontsize=11)
        axx.grid(alpha=0.3)
    for c in range(3):
        ax[3, c].set_xlabel('time (ms)')
    for r in range(4):
        ax[r, 0].set_ylabel('mV')
    fig.suptitle(a.title + f'   QRS {res["qrs_duration_ms"]:.0f} ms (shaded)', fontsize=12)
    fig.tight_layout()
    fig.savefig(a.png, dpi=130)
    json.dump(res, open(os.path.splitext(a.png)[0] + '.json', 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
