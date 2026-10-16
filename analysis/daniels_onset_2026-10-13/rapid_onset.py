"""Daniels-style "earliest rapid deflection" QRS onset and precordial MDI.
SENSITIVITY only. Daniels 2006 (Circulation 113:1659, Methods p.1660): QRS from "the earliest rapid deflection
of the ventricular complex in any of the 12 simultaneous leads to the latest offset in any lead".
S calibrated on Zheng 2020 real PVC templates (2000 Hz, 0.5-150 Hz), frozen 2026-10-13.
x: (12, n) mV, rows I, II, III, aVR, aVL, aVF, V1..V6, isoelectric level subtracted (or pass baseline=(b0, b1)).
onset: measure_beat onset_ms * fs/1000; offset: measure_beat offset_any_lead_ms * fs/1000. At S -> 0 equals mdi_daniels.
(Received from the coordinator session, 13 Oct 2026 00:39 UTC; one guard added on the PC: an empty baseline window
uses at least one sample, x[:, b0:max(b1, b0 + 1)].)
"""
import numpy as np

S_FROZEN = 0.008      # mV/ms
SMOOTH_MS = 4.0
SUSTAIN_MS = 5.0
PRECORDIAL = slice(6, 12)


def _smooth(x, fs, width_ms):
    n = int(round(width_ms * fs / 1000.0))
    if n < 2:
        return x
    left = n // 2
    xp = np.pad(x, [(0, 0), (left, n - 1 - left)], mode="edge")
    k = np.ones(n) / n
    return np.array([np.convolve(r, k, mode="valid") for r in xp])


def rapid_onset_mdi(x, fs, onset, offset, S=S_FROZEN, smooth_ms=SMOOTH_MS,
                    sustain_ms=SUSTAIN_MS, baseline=None):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[0] != 12:
        raise ValueError("x must be (12, n) in I, II, III, aVR, aVL, aVF, V1..V6 order")
    if baseline is not None:
        b0, b1 = int(baseline[0]), int(baseline[1])
        x = x - np.median(x[:, b0:max(b1, b0 + 1)], axis=1, keepdims=True)
    onset, offset = int(onset), int(offset)
    if not 0 <= onset < offset < x.shape[1]:
        raise ValueError("need 0 <= onset < offset < n")
    t_max = onset + np.argmax(np.abs(x[PRECORDIAL, onset:offset + 1]), axis=1)
    t_first = int(t_max.min())
    slope = np.abs(np.gradient(_smooth(x, fs, smooth_ms), axis=1)) * fs / 1000.0
    n = int(round(sustain_ms * fs / 1000.0)) + 1
    ok = np.pad(slope >= S, [(0, 0), (1, 0)]).astype(np.int64).cumsum(axis=1)
    run = (ok[:, n:] - ok[:, :-n]) == n
    hits = np.flatnonzero(run[:, onset:min(t_first, run.shape[1])].any(axis=0))
    found = hits.size > 0
    on_r = onset + int(hits[0]) if found else onset
    mdi_all = (t_max - on_r) / (offset - on_r)
    return {"onset": on_r, "found": found, "shift_ms": (on_r - onset) * 1000.0 / fs,
            "qrs_ms": (offset - on_r) * 1000.0 / fs, "mdi": float(mdi_all.min()),
            "mdi_lead": "V%d" % (int(np.argmin(mdi_all)) + 1), "t_max": t_max}
