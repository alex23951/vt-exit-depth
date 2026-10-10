"""Piecewise-linear 12-lead beats with known answers."""
import numpy as np

from ecg_depth_criteria import from_leads

FS = 2000.0  # Hz
T = np.arange(0, 400, 1000 / FS)  # ms
ONSET = 50.0  # ms


def lead(knots):
    """Signal through (ms, mV) knots, zero outside them."""
    t, v = zip(*knots)
    return np.interp(T, t, v, left=0.0, right=0.0)


def knots(o=ONSET):
    """A wide beat with a slow 60 ms start (a pseudo-delta wave).

    Known answers, from QRS onset o:
      pseudo-delta 60 ms: every precordial slope is <= 0.005 mV/ms until
        o + 60, when V1 steepens to 0.06 mV/ms (steepest precordial slope
        0.087 mV/ms, so the 30% threshold is 0.026 mV/ms);
      IDT 88 ms (R peak in V2); shortest RS 100 ms (S nadir in V4; V1 110,
        V3 105, V2 120, no S in V5-V6);
      largest precordial deflection first in V3, at 75 ms;
      precordial offset 160 ms (V5, V6), latest offset in any lead 170 ms (I, II);
      lead I starts with a q wave; II, III and aVF start positive.
    """
    return {
        "I": [(o, 0), (o + 20, -0.15), (o + 100, 0.8), (o + 170, 0)],
        "II": [(o, 0), (o + 30, 0.2), (o + 100, 1.0), (o + 170, 0)],
        "V1": [(o, 0), (o + 60, 0.3), (o + 80, 1.5), (o + 110, -0.8), (o + 150, 0)],
        "V2": [(o, 0), (o + 60, 0.25), (o + 88, 1.2), (o + 120, -0.3), (o + 150, 0)],
        "V3": [(o, 0), (o + 60, 0.25), (o + 75, 1.1), (o + 105, -0.5), (o + 150, 0)],
        "V4": [(o, 0), (o + 60, 0.2), (o + 85, 0.9), (o + 100, -0.4), (o + 150, 0)],
        "V5": [(o, 0), (o + 60, 0.2), (o + 90, 1.4), (o + 160, 0)],
        "V6": [(o, 0), (o + 60, 0.15), (o + 95, 1.0), (o + 160, 0)],
    }


def beat(o=ONSET, **override):
    """(12, n) array of the beat; keyword arguments replace a lead's knots."""
    k = knots(o)
    k.update(override)
    return from_leads({name: lead(v) for name, v in k.items()})


def noise(sd_mv, seed):
    """Band-limited noise (10 ms moving average of white noise), sd_mv per lead."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, 1.0, (12, T.size))
    width = int(10 * FS / 1000)
    n = np.apply_along_axis(lambda r: np.convolve(r, np.ones(width) / width, mode="same"), 1, n)
    return n / n.std(axis=1, keepdims=True) * sd_mv
