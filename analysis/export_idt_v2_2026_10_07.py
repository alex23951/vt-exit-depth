#!/usr/bin/env python
"""
V2 traces for the by-eye IDT check (decision 4 of 4 Oct 2026; cloud desk check of 5 Oct).

Selects every site of the control-heart v4 table (analysis/pilot_grid_sites_v4.csv, Y5HYEDL4,
ecg_depth_criteria 0.3.0) with true-onset IDT >= 85 ms and exports, from the saved eikonal ECGs
(runs/<run_prefix>_eik_<heart>_<id>_ecg/POSTPROC_DIR/ECG_V2.dat, time 0 = stimulus):
  analysis/idt_v2_2026-10-07/idt_v2_traces.csv  time_ms + one V2 column (mV) per site
  analysis/idt_v2_2026-10-07/idt_v2_sites.csv   per site: name, depth, QRS, IDT, V2 wave amplitudes
  analysis/idt_v2_2026-10-07/idt_v2_panel.png   one small V2 plot per site, IDT and QRS end marked
No simulation; reads saved files only.
"""

import csv
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(REPO, 'analysis', 'idt_v2_2026-10-07')
COLS = ['id', 'name', 'family', 'depth_target', 'depth_achieved', 'run_prefix', 'true_qrs_duration_ms',
        'true_idt_v2_ms', 'true_idt_index', 'true_q_amp_V2', 'true_r_amp_V2', 'true_s_amp_V2',
        'detected_idt_v2_ms', 'detected_qrs_duration_ms']


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    rows = list(csv.DictReader(open(os.path.join(REPO, 'analysis', 'pilot_grid_sites_v4.csv'))))
    sel = [r for r in rows if num(r['true_idt_v2_ms']) is not None and num(r['true_idt_v2_ms']) >= 85]
    os.makedirs(OUT, exist_ok=True)
    traces = {}
    for r in sel:
        f = os.path.join(REPO, 'runs', f"{r['run_prefix']}_eik_{r['heart']}_{r['id']}_ecg", 'POSTPROC_DIR', 'ECG_V2.dat')
        traces[r['id']] = np.loadtxt(f)
    n = max(len(x) for x in traces.values())
    t = next(x[:, 0] for x in traces.values() if len(x) == n)
    with open(os.path.join(OUT, 'idt_v2_traces.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['time_ms'] + [f'V2_mV__{k}' for k in traces])
        for i in range(n):
            w.writerow([f'{t[i]:g}'] + [f'{x[i, 1]:.5g}' if i < len(x) else '' for x in traces.values()])
    with open(os.path.join(OUT, 'idt_v2_sites.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction='ignore')
        w.writeheader()
        w.writerows(sel)

    k = len(sel)
    nc = 5
    nr = int(np.ceil(k / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(12, 2.0 * nr), sharex=True)
    for ax, r in zip(axs.flat, sel):
        x = traces[r['id']]
        ax.plot(x[:, 0], x[:, 1], lw=0.9, color='k')
        ax.axhline(0, lw=0.5, color='0.6')
        ax.axvline(num(r['true_idt_v2_ms']), lw=0.8, color='tab:red')
        ax.axvline(num(r['true_qrs_duration_ms']), lw=0.8, ls='--', color='tab:blue')
        ax.set_title(f"{r['name']} {int(float(r['depth_target']) * 100)}%\nIDT {float(r['true_idt_v2_ms']):.0f} / QRS "
                     f"{float(r['true_qrs_duration_ms']):.0f} ms, r {float(r['true_r_amp_V2'] or 0):.2f} mV", fontsize=7)
        ax.tick_params(labelsize=6)
    for ax in list(axs.flat)[k:]:
        ax.axis('off')
    fig.suptitle('V2 at the 23 control-heart sites with IDT >= 85 ms (true onset; red = IDT, blue dashed = QRS end; '
                 'time from stimulus, mV)', fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'idt_v2_panel.png'), dpi=90)
    print(k, 'sites;', n, 'samples; written to', OUT)


if __name__ == '__main__':
    main()
