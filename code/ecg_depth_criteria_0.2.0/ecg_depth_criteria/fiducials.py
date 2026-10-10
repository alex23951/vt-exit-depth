"""QRS boundaries, slopes and individual waves for one beat."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Settings:
    """Fixed measurement settings, reported with every result.

    Keep the defaults for the main analyses so simulated and real ECGs are
    measured identically; vary them only in sensitivity analyses.
    """

    baseline_ms: float = 40.0  # isoelectric window that ends at the stimulus, or opens the segment
    smooth_ms: float = 2.0  # moving average before the slopes and the onset search
    onset_mv: float = 0.02  # QRS onset: smallest spatial magnitude accepted as a deflection
    offset_frac: float = 0.10  # QRS offset: spatial velocity falls below this fraction of its peak
    offset_smooth_ms: float = 6.0  # moving average before the slopes used for the offset
    noise_sd: float = 5.0  # onset and offset thresholds also sit this many SDs above the baseline
    gap_ms: float = 10.0  # sub-threshold dips shorter than this stay inside the QRS
    wave_mv: float = 0.05  # smallest deflection counted as a wave (0.5 mm at 10 mm/mV)
    fast_frac: float = 0.30  # pseudo-delta ends when a precordial slope first reaches this
    #                          fraction of the steepest precordial slope in the QRS
    r_peak: str = "first"  # IDT: peak of the "first" (the R wave; a later one after an S is R'),
    #                        "largest" or "last" positive wave in V2

    def __post_init__(self):
        if self.r_peak not in ("largest", "first", "last"):
            raise ValueError("r_peak must be 'largest', 'first' or 'last'")


@dataclass(frozen=True)
class Wave:
    """A deflection beyond +/- the wave threshold, in sample indices."""

    sign: int  # +1 positive, -1 negative
    start: int
    end: int
    peak: int  # sample of the extreme value


def smooth(x: np.ndarray, fs: float, width_ms: float) -> np.ndarray:
    """Centred moving average along the last axis, edges padded with edge values."""
    n = int(round(width_ms * fs / 1000.0))
    if n < 2:
        return x
    kernel = np.ones(n) / n
    left = n // 2
    pad = [(0, 0)] * (x.ndim - 1) + [(left, n - 1 - left)]
    xp = np.pad(x, pad, mode="edge")
    return np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="valid"), -1, xp)


def slopes(x: np.ndarray, fs: float, width_ms: float) -> np.ndarray:
    """dV/dt in mV/ms after a moving average."""
    return np.gradient(smooth(x, fs, width_ms), axis=-1) * fs / 1000.0


def spatial_velocity(slope_rows: np.ndarray) -> np.ndarray:
    """Root sum of squared slopes across leads, mV/ms."""
    return np.sqrt(np.sum(slope_rows ** 2, axis=0))


def _edge(sv: np.ndarray, start: int, thr: float, gap: int, step: int) -> int:
    """Walk from start in direction step; return the last supra-threshold sample
    reached before a sub-threshold run longer than gap samples."""
    last, below, i = start, 0, start + step
    while 0 <= i < len(sv):
        if sv[i] >= thr:
            last, below = i, 0
        else:
            below += 1
            if below > gap:
                break
        i += step
    return last


def _baseline_stats(v: np.ndarray, base: slice) -> tuple:
    b = v[base]
    return (float(b.mean()), float(b.std())) if b.size >= 3 else (0.0, 0.0)


def qrs_offset(sv: np.ndarray, fs: float, base: slice, s: Settings) -> int:
    """End of the QRS from the spatial velocity.

    Followed forward from its peak, first to where it stays below a high
    threshold (offset_frac of the peak, and noise_sd SDs above its baseline
    mean) for longer than gap_ms, then on while it stays above offset_frac
    of the peak and above anything seen in the baseline window. Without
    noise both thresholds equal offset_frac of the peak.
    """
    mu, sd = _baseline_stats(sv, base)
    b = sv[base]
    rel = s.offset_frac * float(sv.max())
    lo = max(rel, float(b.max()) if b.size >= 3 else 0.0)
    hi = max(rel, mu + s.noise_sd * sd, lo)
    i = _edge(sv, int(np.argmax(sv)), hi, int(round(s.gap_ms * fs / 1000.0)), +1)
    while i < len(sv) - 1 and sv[i + 1] > lo:
        i += 1
    return i


def qrs_onset(x_rows: np.ndarray, sv: np.ndarray, fs: float, base: slice, s: Settings) -> int:
    """Earliest deflection from baseline in any of the given leads.

    The spatial magnitude of the baseline-corrected leads is followed back
    from the steepest point of the QRS, first to where it stays below a high
    threshold (noise_sd SDs above its baseline mean, at least onset_mv) for
    longer than gap_ms, then on to the first sample no larger than anything
    seen in the baseline window (at least onset_mv / 4). A slow initial
    deflection such as a pseudo-delta wave stays inside the QRS even when its
    slope is buried in noise, which a slope threshold would miss.
    """
    a = np.sqrt(np.sum(smooth(x_rows, fs, s.smooth_ms) ** 2, axis=0))
    mu, sd = _baseline_stats(a, base)
    b = a[base]
    lo = max(float(b.max()) if b.size >= 3 else 0.0, s.onset_mv / 4)
    hi = max(mu + s.noise_sd * sd, s.onset_mv, lo)
    stop = base.stop if base.stop < int(np.argmax(sv)) else 0
    i = _edge(a, int(np.argmax(sv)), hi, int(round(s.gap_ms * fs / 1000.0)), -1)
    while i > stop and a[i - 1] > lo:
        i -= 1
    return i


def waves(x: np.ndarray, i0: int, i1: int, thr: float) -> list:
    """Deflections beyond +/- thr between samples i0 and i1, in time order."""
    seg = x[i0 : i1 + 1]
    label = np.where(seg >= thr, 1, np.where(seg <= -thr, -1, 0))
    out, k, n = [], 0, len(seg)
    while k < n:
        if label[k] == 0:
            k += 1
            continue
        sign, a = int(label[k]), k
        while k < n and label[k] == sign:
            k += 1
        part = seg[a:k]
        p = a + int(np.argmax(part) if sign > 0 else np.argmin(part))
        out.append(Wave(sign, i0 + a, i0 + k - 1, i0 + p))
    return out
