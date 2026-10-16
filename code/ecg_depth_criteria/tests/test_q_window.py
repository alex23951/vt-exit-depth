"""0.4.0: initial window and CSE recognition for q waves and initial r waves (decision H, 15 Oct 2026).

Synthetic beats at 2 kHz with onset o = 50 ms; the other leads deflect from o, so the visible onset is o.
Every test passes q_window_ms and recog_mv explicitly, so it does not depend on the defaults.
"""
import os
import subprocess
import sys

import numpy as np
import pytest

from ecg_depth_criteria import Settings, from_leads, measure_beat
from synthetic import FS, ONSET, T, beat, knots, lead, noise

O = ONSET
INDEPENDENT = ["I", "II", "V1", "V2", "V3", "V4", "V5", "V6"]
V030 = Settings(q_window_ms=None, recog_mv=None)


def cse(n, **kw):
    return Settings(q_window_ms=n, recog_mv=0.02, **kw)


def window_only(n, **kw):
    return Settings(q_window_ms=n, recog_mv=None, **kw)


def m_of(ecg, s, **kw):
    return measure_beat(ecg, FS, settings=s, **kw)


def test_settings_are_validated():
    for bad in (dict(q_window_ms=0), dict(q_window_ms=-5), dict(q_window_ms=float("nan")), dict(q_anchor="stimulus"),
                dict(recog_mv=0.0), dict(recog_mv=0.05), dict(recog_mv=0.2), dict(recog_ms=0)):
        with pytest.raises(ValueError):
            Settings(**bad)


def test_a_late_first_deflection_is_no_q():
    ecg = beat(I=[(O, 0), (O + 50, 0), (O + 56, -0.5), (O + 120, 0.6), (O + 170, 0)])
    for n in (20, 40):
        for s in (cse(n), window_only(n)):
            m = m_of(ecg, s)
            assert not m["q_lead_I"] and m["initial_polarity"]["I"] == 0 and m["q_amplitude_mv"]["I"] == 0.0
    for s in (V030, cse(None)):
        assert m_of(ecg, s)["q_lead_I"]
    m = m_of(ecg, cse(40))
    assert m["initial_sign"]["I"] == -1 and m["initial_start_ms"]["I"] == pytest.approx(50, abs=1.5)
    assert m["q_anchor_ms"] == pytest.approx(O, abs=1)


def test_b_q_after_a_short_isoelectric_segment():
    ecg = beat(I=[(O, 0), (O + 15, 0), (O + 17, -0.1), (O + 40, -0.3), (O + 100, 0.8), (O + 170, 0)])
    for n in (20, 40):
        for s in (cse(n), window_only(n)):
            assert m_of(ecg, s)["q_lead_I"]


def test_c_tiny_initial_r_before_a_deep_s():
    ecg = beat(I=[(O, 0), (O + 1, 0.03), (O + 9, 0.03), (O + 12, 0), (O + 30, -0.6), (O + 100, 0.5), (O + 170, 0)])
    assert m_of(ecg, V030)["q_lead_I"]                       # 0.3.0: the first 0.05 mV wave is the S
    for n in (20, 40):
        assert m_of(ecg, window_only(n))["q_lead_I"]          # window only: the same
        m = m_of(ecg, cse(n))                                 # CSE: an initial r is recognised, then turns back
        assert not m["q_lead_I"] and m["initial_polarity"]["I"] == 0 and m["initial_sign"]["I"] == 1


def test_d_slow_qs_from_onset():
    ecg = beat(I=[(O, 0), (O + 80, -0.8), (O + 170, 0)])
    for s in (cse(20), cse(40), window_only(40), V030):
        m = m_of(ecg, s)
        assert m["q_lead_I"] and m["q_amplitude_mv"]["I"] == pytest.approx(0.8, abs=1e-9)


def test_e_window_opens_at_the_visible_onset_not_the_stimulus():
    ecg = beat()                                              # lead I: q from o
    for n in (20, 40):
        for s in (cse(n), window_only(n)):
            m = m_of(ecg, s, stim_ms=O - 20)
            assert m["onset_source"] == "stimulus" and m["q_lead_I"]
            assert m["q_anchor_ms"] == pytest.approx(O, abs=1)
    # sensitivity anchor at the stimulus: the q starts > 20 ms after it
    for s in (cse(20, q_anchor="onset"), window_only(20, q_anchor="onset")):
        assert not m_of(ecg, s, stim_ms=O - 20)["q_lead_I"]


def test_f_notched_q_is_one_q_with_its_deepest_point():
    ecg = beat(I=[(O, 0), (O + 10, -0.3), (O + 16, -0.03), (O + 26, -0.6), (O + 40, 0), (O + 100, 0.8), (O + 170, 0)])
    for s in (cse(20), cse(40), window_only(40), V030):
        m = m_of(ecg, s)
        assert m["q_lead_I"] and m["q_amplitude_mv"]["I"] == pytest.approx(0.6, abs=1e-9)


def test_g_every_030_test_passes_with_the_window_off():
    here = os.path.dirname(os.path.abspath(__file__))
    files = [os.path.join(here, f) for f in ("test_measure.py", "test_criteria.py", "test_summit_prisco.py")]
    env = dict(os.environ, EDC_LEGACY_Q="1", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q", *files],
                       cwd=os.path.dirname(here), env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]


def noisy_seed21():
    k = knots(O)
    k["I"] = [(O, 0), (O + 30, 0.10), (O + 60, -0.6), (O + 120, 0.3), (O + 170, 0)]
    nz = np.random.default_rng(21).normal(0, 0.020, (8, T.size))
    return from_leads({name: lead(k[name]) + nz[j] for j, name in enumerate(INDEPENDENT)})


def test_h_noise_spike_before_a_small_initial_r_is_no_q():
    ecg = noisy_seed21()
    true_onset = dict(onset_ms=O, baseline_window_ms=(O - 45, O - 5))   # the project's convention
    assert m_of(ecg, V030, **true_onset)["q_lead_I"]          # 0.3.0 calls the noise spike a q (detected mode: no)
    for kw in ({}, true_onset):
        for n in (20, 40):
            assert not m_of(ecg, cse(n), **kw)["q_lead_I"]    # primary rule; window only is reported


@pytest.mark.parametrize("make", [cse, window_only])
@pytest.mark.parametrize("n", [20, 40])
def test_i_false_q_rate_in_an_isoelectric_lead(make, n):
    clean = beat(I=[(0, 0), (1, 0)])                          # lead I flat; the QRS is in the other leads
    calls = [m_of(clean + noise(0.010, seed), make(n))["q_lead_I"] for seed in range(400)]
    assert np.mean(calls) <= 0.01
