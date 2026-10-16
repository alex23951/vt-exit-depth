"""Missing values in the Aim 1 summaries (v5.1 brief Step 2, decision H; 16 Oct 2026): a missing value is never a
loss. It is left out and counted (audit F17: 'nan' strings became NaN floats, which statistics.median kept and which
lost every AUC comparison).

Unpaired values: scored() drops NaN / None / '' only (+-inf are kept, e.g. a ratio with a zero denominator), and
reports how many were dropped. Paired statistics drop the whole pair. Criterion rates leave None out of both counts.
"""
import math
import statistics as st

import numpy as np

NAN = float('nan')


def num(x):
    """A CSV cell or value as a float; None, '', 'None', 'nan' and text that is not a number give NaN."""
    if x is None:
        return NAN
    if isinstance(x, (bool, np.bool_)):
        return float(x)
    try:
        return float(x)
    except (TypeError, ValueError):
        return NAN


def scored(values):
    """(kept values, n_total, n_unscorable): NaN dropped, +-inf kept."""
    v = [num(x) for x in values]
    kept = [x for x in v if not math.isnan(x)]
    return kept, len(v), len(v) - len(kept)


def scored_median(values):
    """(median or None, n_scored, n_unscorable)."""
    kept, n, u = scored(values)
    return (st.median(kept) if kept else None), len(kept), u


def fmt_median(values, nd=3):
    m, n, u = scored_median(values)
    if n == 0:
        return f'not evaluable (0 scored, {u} unscorable)'
    return f'{round(m, nd)}' + (f' ({u} unscorable)' if u else '')


def auc_scored(pos, neg, pos_ids=None, neg_ids=None):
    """Unpaired Mann-Whitney AUC, higher = epicardial (pos): mean of 1[p > n] + 0.5 * 1[p == n] over the scored
    cross pairs; NaN dropped in each group. Returns dict(auc or None, n_pos, n_neg, dropped ids or counts)."""
    p = [(i, num(x)) for i, x in zip(pos_ids or range(len(pos)), pos)]
    q = [(i, num(x)) for i, x in zip(neg_ids or range(len(neg)), neg)]
    dp = [i for i, x in p if math.isnan(x)]; dq = [i for i, x in q if math.isnan(x)]
    a = [x for _, x in p if not math.isnan(x)]; b = [x for _, x in q if not math.isnan(x)]
    auc = sum((x > y) + 0.5 * (x == y) for x in a for y in b) / (len(a) * len(b)) if a and b else None
    return {'auc': auc, 'n_pos': len(a), 'n_neg': len(b), 'dropped_pos': dp, 'dropped_neg': dq}


def fmt_auc(pos, neg, nd=2):
    r = auc_scored(pos, neg)
    u = len(r['dropped_pos']) + len(r['dropped_neg'])
    if r['auc'] is None:
        return f'not evaluable ({u} unscorable)'
    return f"{round(r['auc'], nd)}" + (f' ({u} unscorable)' if u else '')


def paired(a, b):
    """Pairs (a_i, b_i) with both values scored; returns (kept a, kept b, n_pairs, n_dropped)."""
    kept = [(num(x), num(y)) for x, y in zip(a, b)]
    ok = [(x, y) for x, y in kept if not (math.isnan(x) or math.isnan(y))]
    return [x for x, _ in ok], [y for _, y in ok], len(ok), len(kept) - len(ok)


def up_count(a, b):
    """(n with b > a, n scored pairs, n dropped): paired 'up' count from a to b."""
    x, y, n, d = paired(a, b)
    return sum(v > u for u, v in zip(x, y)), n, d


def ratio_of_means(a, b):
    """mean(a) / mean(b) over the scored pairs; (ratio or None, n pairs, n dropped)."""
    x, y, n, d = paired(a, b)
    return (float(np.mean(x) / np.mean(y)) if n else None), n, d


def bootstrap_ratio_of_means(a, b, n_boot=2000, seed=0):
    """95 % percentile interval of mean(a) / mean(b), resampling scored pairs (seed 0, 2,000 resamples)."""
    x, y, n, _ = paired(a, b)
    if n == 0:
        return None
    x, y = np.asarray(x), np.asarray(y)
    idx = np.random.default_rng(seed).integers(0, n, (n_boot, n))
    r = x[idx].mean(1) / y[idx].mean(1)
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def flag(x):
    """True / False / None from a bool or a CSV cell ('True', 'False', '', 'None', 'nan')."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    s = str(x).strip().lower()
    return True if s in ('true', '1', '1.0') else False if s in ('false', '0', '0.0') else None


def rate(flags):
    """(k True, n scored, n unscorable); None is left out of both counts."""
    f = [flag(x) for x in flags]
    s = [x for x in f if x is not None]
    return sum(s), len(s), len(f) - len(s)


def fmt_rate(flags):
    k, n, u = rate(flags)
    return f'{k} / {n}' + (f' ({u} unscorable)' if u else '')
