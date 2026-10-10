"""Lead names and assembly of 12-lead ECG arrays."""
from __future__ import annotations

import numpy as np

LEADS = ("I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6")
PRECORDIAL = ("V1", "V2", "V3", "V4", "V5", "V6")
LIMB = ("I", "II", "III", "aVR", "aVL", "aVF")
INFERIOR = ("II", "III", "aVF")
# The 8 independent leads. III, aVR, aVL and aVF are combinations of I and II,
# so "the earliest/latest deflection in any of the 12 leads" is found in these.
INDEPENDENT = ("I", "II") + PRECORDIAL


def rows(names):
    """Row indices of the named leads in a (12, n) array."""
    return [LEADS.index(k) for k in names]


def from_leads(leads: dict) -> np.ndarray:
    """Stack a dict of lead signals (mV) into a (12, n) array in LEADS order.

    Missing III, aVR, aVL and aVF are derived from I and II with the
    Einthoven and Goldberger relations.
    """
    d = {k: np.asarray(v, dtype=float) for k, v in leads.items()}
    if "I" not in d or "II" not in d:
        raise ValueError("leads I and II are required")
    lead_i, lead_ii = d["I"], d["II"]
    d.setdefault("III", lead_ii - lead_i)
    d.setdefault("aVR", -(lead_i + lead_ii) / 2)
    d.setdefault("aVL", lead_i - lead_ii / 2)
    d.setdefault("aVF", lead_ii - lead_i / 2)
    missing = [k for k in LEADS if k not in d]
    if missing:
        raise ValueError(f"missing leads: {missing}")
    if len({d[k].shape for k in LEADS}) != 1:
        raise ValueError("all leads must have the same length")
    return np.vstack([d[k] for k in LEADS])
