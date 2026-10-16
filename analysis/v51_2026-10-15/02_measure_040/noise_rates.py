"""Step 2.5 noise table (v5.1 brief, decision H; 16 Oct 2026): false-q and false-initial-r rates in synthetic lead I.

Beats from the package's tests/synthetic.py (2 kHz, onset o = 50 ms; the other leads carry the QRS, so the visible
onset is o): (1) lead I isoelectric; (2) lead I with a 0.10 mV initial r (o -> o + 10 ms -> back to 0 at o + 20 ms)
before a deep S (-0.6 mV at o + 40). Noise: synthetic.noise (10 ms moving average of white noise) at 10 and 20 uV per
lead, seeds 0-399. Measured in the default detected mode. Rules: 0.3.0 (window and recognition off), window only
(40 ms), CSE primary (40 ms, 20 uV).
false q = q_lead_I True; false initial r (isoelectric lead) = initial_polarity I > 0.
Writes noise_table.csv in this folder.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PKG = os.path.join(REPO, 'code', 'ecg_depth_criteria')
sys.path[:0] = [PKG, os.path.join(PKG, 'tests')]
from ecg_depth_criteria import Settings, measure_beat   # noqa: E402
from synthetic import FS, ONSET, beat, noise            # noqa: E402

O = ONSET
RULES = {'0.3.0 rule': Settings(q_window_ms=None, recog_mv=None), 'window only 40 ms': Settings(q_window_ms=40.0, recog_mv=None),
         'CSE primary 40 ms': Settings(q_window_ms=40.0, recog_mv=0.02)}
BEATS = {'isoelectric lead I': beat(I=[(0, 0), (1, 0)]),
         '0.10 mV initial r in lead I': beat(I=[(O, 0), (O + 10, 0.10), (O + 20, 0), (O + 40, -0.6), (O + 100, 0.5), (O + 170, 0)])}


def main():
    rows = []
    for bname, clean in BEATS.items():
        for uv in (10, 20):
            for rname, s in RULES.items():
                q, r, n = 0, 0, 400
                for seed in range(n):
                    m = measure_beat(clean + noise(uv / 1000, seed), FS, settings=s)
                    q += bool(m['q_lead_I']); r += m['initial_polarity']['I'] > 0
                row = {'beat': bname, 'noise_uV': uv, 'rule': rname, 'draws': n, 'false_q': q, 'false_q_pct': 100 * q / n}
                if bname.startswith('isoelectric'):
                    row.update(false_initial_r=r, false_initial_r_pct=100 * r / n)
                else:
                    row.update(initial_r_called=r, initial_r_called_pct=100 * r / n)
                rows.append(row)
                print(row, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, 'noise_table.csv'), index=False)


if __name__ == '__main__':
    main()
