"""Shortest RS on a notched S wave (0.4.1)."""
import synthetic as S

from ecg_depth_criteria import measure_beat


def test_notched_s_uses_deepest_point():
    # V4's S wave comes back to -0.03 mV, inside the 0.05 mV threshold, between -0.4 and
    # -0.9 mV: one S wave, whose nadir at 125 ms makes V3 (105 ms) the shortest RS.
    o = S.ONSET
    v4 = [(o, 0), (o + 60, 0.2), (o + 85, 0.9), (o + 100, -0.4), (o + 112, -0.03), (o + 125, -0.9), (o + 150, 0)]
    m = measure_beat(S.beat(V4=v4), S.FS, stim_ms=o)
    assert m["srs_lead"] == "V3" and abs(m["srs_ms"] - 105) <= 0.5
    assert abs(m["s_amplitude_mv"]["V4"] - 0.9) <= 0.01


def test_s_wave_ends_at_the_next_positive_wave():
    # A positive wave (R') between two negative ones ends the first S wave: V4's shortest RS
    # stays at the first nadir, 100 ms, even though the later S' is deeper.
    o = S.ONSET
    v4 = [(o, 0), (o + 60, 0.2), (o + 85, 0.9), (o + 100, -0.4), (o + 112, 0.2), (o + 125, -0.9), (o + 150, 0)]
    m = measure_beat(S.beat(V4=v4), S.FS, stim_ms=o)
    assert m["srs_lead"] == "V4" and abs(m["srs_ms"] - 100) <= 0.5
