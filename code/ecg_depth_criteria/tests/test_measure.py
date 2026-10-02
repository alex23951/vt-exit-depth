import math

import numpy as np
import pytest

from ecg_depth_criteria import LEADS, Settings, from_leads, measure_beat
from synthetic import FS, ONSET, beat, lead, noise


def test_intervals_from_the_true_onset():
    m = measure_beat(beat(), FS, onset_ms=ONSET)
    assert m["onset_source"] == "given"
    assert m["pseudo_delta_ms"] == pytest.approx(60, abs=1)
    assert m["pseudo_delta_lead"] == "V1"
    assert m["idt_v2_ms"] == pytest.approx(88, abs=0.5)
    assert m["srs_ms"] == pytest.approx(100, abs=0.5)
    assert m["srs_lead"] == "V4"
    assert m["qrs_duration_ms"] == pytest.approx(160, abs=1)
    assert m["qrs_duration_any_lead_ms"] == pytest.approx(170, abs=2)
    # Valles/Piers divide by the precordial QRS, Daniels by the latest offset in any lead.
    assert m["mdi_valles"] == pytest.approx(75 / 160, abs=0.01)
    assert m["mdi_valles_lead"] == "V3"
    assert m["mdi_daniels"] == pytest.approx(75 / 170, abs=0.01)


def test_detected_boundaries_without_noise():
    m = measure_beat(beat(), FS)
    assert m["onset_source"] == "detected"
    assert m["onset_ms"] == pytest.approx(ONSET, abs=1)
    assert m["offset_precordial_ms"] == pytest.approx(ONSET + 160, abs=2)
    assert m["offset_any_lead_ms"] == pytest.approx(ONSET + 170, abs=2)
    assert m["pseudo_delta_ms"] == pytest.approx(60, abs=1.5)
    assert m["srs_ms"] == pytest.approx(100, abs=1.5)


def test_paced_intervals_start_at_the_stimulus():
    m = measure_beat(beat(), FS, stim_ms=ONSET - 10)
    assert m["onset_source"] == "stimulus"
    assert m["visible_onset_ms"] == pytest.approx(ONSET, abs=1)
    assert m["pseudo_delta_ms"] == pytest.approx(70, abs=1)
    assert m["idt_v2_ms"] == pytest.approx(98, abs=0.5)
    assert m["srs_ms"] == pytest.approx(110, abs=0.5)
    assert m["qrs_duration_ms"] == pytest.approx(170, abs=2)
    assert m["mdi_valles"] == pytest.approx(85 / 170, abs=0.01)


def test_given_onset_and_offset_override_detection():
    m = measure_beat(beat(), FS, onset_ms=ONSET - 5, offset_ms=ONSET + 160)
    assert m["idt_v2_ms"] == pytest.approx(93, abs=0.5)
    assert m["offset_precordial_ms"] == m["offset_any_lead_ms"] == ONSET + 160
    assert m["mdi_daniels"] == m["mdi_valles"] == pytest.approx(80 / 165, abs=0.01)


def test_onset_after_offset_is_rejected():
    with pytest.raises(ValueError):
        measure_beat(beat(), FS, onset_ms=300)


def test_morphology():
    m = measure_beat(beat(), FS)
    assert m["q_lead_I"] is True
    assert m["inferior_q_any"] is False and m["inferior_q_all"] is False
    assert m["inferior_r_any"] is True
    assert m["q_V2"] is False and m["qs_V2"] is False
    assert m["inferior_axis"] is True  # aVF predominantly positive
    assert m["rbbb_like"] is True  # V1 predominantly positive
    assert m["avr_avl_ratio_lt_1"] is True  # aVL less negative than aVR
    assert m["initial_polarity"]["I"] == -1 and m["initial_polarity"]["III"] == 1


def test_q_waves_in_all_inferior_leads():
    o = ONSET
    m = measure_beat(
        beat(
            I=[(o, 0), (o + 20, 0.3), (o + 100, 0.8), (o + 170, 0)],
            II=[(o, 0), (o + 25, -0.3), (o + 100, 1.0), (o + 170, 0)],
        ),
        FS,
    )
    # III = II - I and aVF = II - I/2 also start negative.
    assert m["inferior_q_all"] is True and m["inferior_q_any"] is True
    assert m["inferior_r_any"] is False
    assert m["q_lead_I"] is False


def test_qs_in_v2_leaves_idt_undefined():
    o = ONSET
    m = measure_beat(beat(V2=[(o, 0), (o + 60, -0.25), (o + 95, -1.2), (o + 150, 0)]), FS)
    assert m["qs_V2"] is True and m["q_V2"] is True
    assert math.isnan(m["idt_v2_ms"])


def test_r_peak_choice_in_v2():
    o = ONSET
    v2 = [(o, 0), (o + 20, 0.3), (o + 40, -0.15), (o + 88, 1.2), (o + 120, -0.3), (o + 135, 0.2), (o + 150, 0)]
    x = beat(V2=v2)
    got = {c: measure_beat(x, FS, onset_ms=o, settings=Settings(r_peak=c))["idt_v2_ms"] for c in ("first", "largest", "last")}
    assert got == pytest.approx({"first": 20, "largest": 88, "last": 135}, abs=0.5)
    with pytest.raises(ValueError):
        Settings(r_peak="tallest")


@pytest.mark.parametrize("seed", range(10))
def test_band_limited_noise_10_microvolts(seed):
    x = beat() + noise(0.010, seed)
    m = measure_beat(x, FS, baseline_window_ms=(5, ONSET - 5))
    # The slow start is partly hidden in noise, so the onset errs late; it
    # can never be placed before the end of the baseline window.
    assert ONSET - 5 <= m["onset_ms"] <= ONSET + 8
    assert m["offset_precordial_ms"] == pytest.approx(ONSET + 160, abs=4)
    assert m["offset_any_lead_ms"] == pytest.approx(ONSET + 170, abs=4)
    assert m["q_lead_I"] is True and m["inferior_r_any"] is True
    g = measure_beat(x, FS, onset_ms=ONSET, baseline_window_ms=(5, ONSET - 5))
    assert g["pseudo_delta_ms"] == pytest.approx(60, abs=1.5)
    assert g["idt_v2_ms"] == pytest.approx(88, abs=1.5)
    assert g["srs_ms"] == pytest.approx(100, abs=1.5)
    assert g["mdi_valles"] == pytest.approx(75 / 160, abs=0.02)


def test_from_leads_derives_limb_leads():
    t = np.linspace(0, 1, 50)
    leads = {"I": np.sin(t), "II": np.cos(t)}
    leads.update({f"V{i}": t * i for i in range(1, 7)})
    x = from_leads(leads)
    row = {k: x[i] for i, k in enumerate(LEADS)}
    np.testing.assert_allclose(row["III"], np.cos(t) - np.sin(t))
    np.testing.assert_allclose(row["aVR"], -(np.sin(t) + np.cos(t)) / 2)
    np.testing.assert_allclose(row["aVL"], np.sin(t) - np.cos(t) / 2)
    np.testing.assert_allclose(row["aVF"], np.cos(t) - np.sin(t) / 2)


def test_from_leads_rejects_incomplete_input():
    v = {f"V{i}": np.zeros(10) for i in range(1, 7)}
    with pytest.raises(ValueError):
        from_leads(v)
    with pytest.raises(ValueError):
        from_leads({"I": np.zeros(10), "II": np.zeros(10)})
    with pytest.raises(ValueError):
        from_leads({"I": np.zeros(10), "II": np.zeros(10), **v, "V6": np.zeros(9)})


def test_onset_search_stops_at_the_baseline_window():
    # Noise measured far from the QRS is too low; the onset is then early but
    # never earlier than the window's end.
    for seed in range(10):
        m = measure_beat(beat() + noise(0.010, seed), FS, baseline_window_ms=(0, 20))
        assert m["onset_ms"] >= 20


def test_warns_when_signals_are_not_in_millivolts():
    with pytest.warns(UserWarning, match="mV"):
        measure_beat(beat() / 1000, FS, onset_ms=ONSET, offset_ms=ONSET + 160)


def test_rejects_wrong_shape():
    with pytest.raises(ValueError):
        measure_beat(np.zeros((8, 100)), FS)


def test_lead_helper_is_continuous():
    assert lead([(10, 0), (20, 1), (30, 0)]).max() == pytest.approx(1)
