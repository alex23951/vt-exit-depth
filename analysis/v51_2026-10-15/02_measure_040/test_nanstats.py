"""Step 2 NaN tests (v5.1 brief): one injected NaN gives the median of the rest and hand-checked AUC / up-counts.
Run (repo root, venv): PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -p no:cacheprovider analysis/v51_2026-10-15/02_measure_040/test_nanstats.py
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import nanstats as ns  # noqa: E402


def test_injected_nan_gives_the_median_of_the_rest():
    assert ns.scored_median([3.0, 'nan', 1.0, 2.0]) == (2.0, 3, 1)
    assert ns.fmt_median([3.0, 'nan', 1.0, 2.0], 1) == '2.0 (1 unscorable)'
    assert ns.scored_median(['nan', None, '']) == (None, 0, 3)
    assert ns.fmt_median(['nan', None]).startswith('not evaluable')
    assert ns.scored([1.0, float('inf'), 'nan'])[0] == [1.0, float('inf')]       # inf kept, NaN dropped


def test_auc_hand_checked():
    # pos 3, 5, NaN vs neg 1, 3, NaN: scored cross pairs (3>1) 1, (3=3) 0.5, (5>1) 1, (5>3) 1 -> 3.5 / 4
    r = ns.auc_scored([3.0, 5.0, 'nan'], [1.0, 3.0, 'nan'], ['p1', 'p2', 'p3'], ['n1', 'n2', 'n3'])
    assert r['auc'] == 0.875 and (r['n_pos'], r['n_neg']) == (2, 2)
    assert r['dropped_pos'] == ['p3'] and r['dropped_neg'] == ['n3']
    # the F17 behaviour: NaN counted as a loss would give 3.5 / 9
    nan = float('nan')
    assert sum((p > q) + 0.5 * (p == q) for p in (3.0, 5.0, nan) for q in (1.0, 3.0, nan)) / 9 != r['auc']


def test_paired_statistics_drop_the_whole_pair():
    a, b = [10.0, 20.0, 'nan', 40.0], [12.0, 'nan', 31.0, 39.0]
    assert ns.paired(a, b) == ([10.0, 40.0], [12.0, 39.0], 2, 2)
    assert ns.up_count(a, b) == (1, 2, 2)                         # 10 -> 12 up, 40 -> 39 down
    r, n, d = ns.ratio_of_means(a, b)
    assert math.isclose(r, 50 / 51) and (n, d) == (2, 2)


def test_rates_leave_none_out():
    assert ns.rate([True, 'False', None, 'True', '', 'nan']) == (2, 3, 3)
    assert ns.fmt_rate([True, 'False', None]) == '1 / 2 (1 unscorable)'


def test_6g_lv_septum_idt_median_is_a_number():
    rows = list(csv.DictReader(open(os.path.join(REPO, 'analysis', 'v5_adopted_2026-10-13', 'purk_6G8DD8S5_v5.csv'))))
    v = [r['true_idt_v2_ms'] for r in rows if r['family'] == 'lv_septum']
    m, n, u = ns.scored_median(v)
    assert m is not None and (n, u) == (29, 3)
    assert ns.fmt_median(v, 1).endswith('(3 unscorable)')
