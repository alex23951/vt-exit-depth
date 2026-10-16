import math

import pytest

from ecg_depth_criteria import CUTOFFS_BELOW, SUMMIT, Settings, __version__, evaluate, measure_beat, summit
from ecg_depth_criteria.__main__ import _jsonable
from synthetic import FS, ONSET, beat

o = ONSET
NAN = float("nan")

# Jauregui Abularach 2012 Figure 5: Q waves in aVL and aVR of an unsuccessful (A) and a
# successful (B) case; QS complexes, printed ratios 3.46 and 0.60.
FIG5_A = {"aVL": [(o, 0), (o + 60, -1.04), (o + 120, 0)], "aVR": [(o, 0), (o + 50, -0.30), (o + 120, 0)]}
FIG5_B = {"aVL": [(o, 0), (o + 60, -0.59), (o + 120, 0)], "aVR": [(o, 0), (o + 50, -0.97), (o + 120, 0)]}
# Santangeli 2015 Figure 3, successful case: R II 0.91 mV, R III 0.94 mV.
FIG3_INFERIOR = {"II": [(o, 0), (o + 70, 0.91), (o + 140, 0)], "III": [(o, 0), (o + 70, 0.94), (o + 140, 0)]}
MONOPHASIC_V1 = {"V1": [(o, 0), (o + 70, 1.2), (o + 140, 0)]}


def measure(**override):
    return measure_beat(beat(**override), FS, onset_ms=ONSET)


def test_version():
    assert __version__ == "0.4.0"


def test_q_wave_ratio_reproduces_jauregui_figure_5():
    a, b = measure(**FIG5_A), measure(**FIG5_B)
    assert a["q_amplitude_mv"]["aVL"] == pytest.approx(1.04, abs=1e-3)
    assert a["q_amplitude_mv"]["aVR"] == pytest.approx(0.30, abs=1e-3)
    assert a["q_ratio_avl_avr"] == pytest.approx(3.46, abs=0.01)
    assert b["q_ratio_avl_avr"] == pytest.approx(0.60, abs=0.01)
    ca, cb = evaluate(a), evaluate(b)
    assert ca["jauregui2012_avl_avr_lt_1_45"] is False and cb["jauregui2012_avl_avr_lt_1_45"] is True
    assert ca["yamada2010_avl_avr_gt_1_1"] is True and cb["yamada2010_avl_avr_gt_1_1"] is False
    assert ca["santangeli2015_avl_avr_gt_1_85"] is True and cb["santangeli2015_avl_avr_gt_1_85"] is False


def test_r_wave_ratio_iii_ii():
    m = measure(**FIG3_INFERIOR)
    assert m["r_amplitude_mv"]["II"] == pytest.approx(0.91, abs=1e-3)
    assert m["r_amplitude_mv"]["III"] == pytest.approx(0.94, abs=1e-3)
    assert m["r_ratio_iii_ii"] == pytest.approx(0.94 / 0.91, abs=1e-3)
    c = evaluate(m)
    assert c["jauregui2012_iii_ii_lt_1_13"] is True
    assert c["yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75"] is False  # III/II 1.03


def test_q_then_r_and_a_notched_qs():
    m = measure(
        aVR=[(o, 0), (o + 20, -0.3), (o + 40, 0), (o + 80, 0.5), (o + 120, 0)],
        # A notch that comes back to -0.03 mV, inside the 0.05 mV wave threshold, stays one wave.
        aVL=[(o, 0), (o + 30, -0.4), (o + 40, -0.03), (o + 70, -0.9), (o + 120, 0)],
    )
    assert m["q_amplitude_mv"]["aVR"] == pytest.approx(0.3, abs=1e-3)
    assert m["r_amplitude_mv"]["aVR"] == pytest.approx(0.5, abs=1e-3)
    assert m["q_amplitude_mv"]["aVL"] == pytest.approx(0.9, abs=1e-3)
    assert m["q_ratio_avl_avr"] == pytest.approx(3.0, abs=0.01)


def test_rs_ratio_and_q_in_v1():
    m = measure()  # V1 of the synthetic beat: R 1.5 mV, then S 0.8 mV
    assert m["r_amplitude_mv"]["V1"] == pytest.approx(1.5, abs=1e-3)
    assert m["s_amplitude_mv"]["V1"] == pytest.approx(0.8, abs=1e-3)
    assert m["rs_ratio_v1"] == pytest.approx(1.875, abs=1e-3)
    assert m["q_V1"] is False
    c = evaluate(m)
    assert c["santangeli2015_rs_v1_gt_2"] is False and c["santangeli2015_no_q_v1"] is True


def test_absent_waves():
    # No S wave in V1: R/S is infinite, so above 2.
    m = measure(**MONOPHASIC_V1)
    assert m["s_amplitude_mv"]["V1"] == 0.0 and math.isinf(m["rs_ratio_v1"])
    assert evaluate(m)["santangeli2015_rs_v1_gt_2"] is True
    # QS in V1: it opens with a q, and R/S is 0.
    m = measure(V1=[(o, 0), (o + 60, -1.0), (o + 120, 0)])
    assert m["q_V1"] is True and m["rs_ratio_v1"] == 0.0
    c = evaluate(m)
    assert c["santangeli2015_no_q_v1"] is False and c["santangeli2015_rs_v1_gt_2"] is False
    # aVR opens positive (no Q) while aVL has one: the ratio is infinite.
    m = measure(aVL=FIG5_A["aVL"], aVR=[(o, 0), (o + 50, 0.4), (o + 120, 0)])
    assert m["q_amplitude_mv"]["aVR"] == 0.0 and math.isinf(m["q_ratio_avl_avr"])
    c = evaluate(m)
    assert c["yamada2010_avl_avr_gt_1_1"] is True and c["jauregui2012_avl_avr_lt_1_45"] is False
    # Neither has a Q: the ratio is missing and so are the criteria.
    m = measure(aVL=[(o, 0), (o + 50, 0.4), (o + 120, 0)], aVR=[(o, 0), (o + 50, 0.4), (o + 120, 0)])
    assert math.isnan(m["q_ratio_avl_avr"])
    c = evaluate(m)
    assert c["yamada2010_avl_avr_gt_1_1"] is None and c["jauregui2012_avl_avr_lt_1_45"] is None


def test_summit_cutoffs_are_strict():
    at = {"q_ratio_avl_avr": 1.1, "r_ratio_iii_ii": 1.13, "rs_ratio_v1": 2.0, "q_V1": True}
    c = summit(at)
    assert c["yamada2010_avl_avr_gt_1_1"] is False
    assert c["jauregui2012_iii_ii_lt_1_13"] is False
    assert c["santangeli2015_rs_v1_gt_2"] is False
    assert summit({"q_ratio_avl_avr": 1.45})["jauregui2012_avl_avr_lt_1_45"] is False
    assert summit({"q_ratio_avl_avr": 1.85})["santangeli2015_avl_avr_gt_1_85"] is False
    both = summit({"q_ratio_avl_avr": 1.76, "r_ratio_iii_ii": 1.26})
    assert both["yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75"] is True
    one = summit({"q_ratio_avl_avr": 1.75, "r_ratio_iii_ii": 1.26})
    assert one["yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75"] is False


@pytest.mark.parametrize(
    "q_ratio, rs, q_v1, expected",
    [
        (2.0, 3.0, True, True),  # 2 of 3
        (2.0, 3.0, False, True),  # 3 of 3
        (1.0, 1.0, False, False),  # 1 of 3
        (NAN, 3.0, True, None),  # 1 met, 1 unknown
        (NAN, NAN, False, None),  # 1 met, 2 unknown
        (NAN, 1.0, True, False),  # 2 out of reach
    ],
)
def test_santangeli_two_of_three(q_ratio, rs, q_v1, expected):
    c = summit({"q_ratio_avl_avr": q_ratio, "rs_ratio_v1": rs, "q_V1": q_v1})
    assert c["santangeli2015_2_of_3"] is expected


def test_prisco_rates_of_change():
    m = measure()
    # V1 rises 0.3 mV over the first 60 ms: 0.15 mV at 30 ms, 5 mV/s. Its largest
    # deflection is 1.5 mV at 80 ms: 18.75 mV/s.
    assert m["prisco_initial_by_lead_mv_s"]["V1"] == pytest.approx(5.0, rel=1e-3)
    assert m["prisco_average_by_lead_mv_s"]["V1"] == pytest.approx(18.75, rel=1e-3)
    # Lead I: q to -0.15 mV at 20 ms, then up to 0.8 mV at 100 ms. At 30 ms it is
    # -0.03125 mV (1.04 mV/s); the largest deflection is 0.8 mV at 100 ms (8 mV/s).
    assert m["prisco_initial_by_lead_mv_s"]["I"] == pytest.approx(0.03125 / 0.030, rel=1e-3)
    assert m["prisco_average_by_lead_mv_s"]["I"] == pytest.approx(8.0, rel=1e-3)
    initial = m["prisco_initial_by_lead_mv_s"]
    assert m["prisco_initial_mv_s"] == pytest.approx(sum(initial.values()) / 12)
    limb = [initial[k] for k in ("I", "II", "III", "aVR", "aVL", "aVF")]
    assert m["prisco_initial_limb_mv_s"] == pytest.approx(sum(limb) / 6)
    assert set(CUTOFFS_BELOW) == {"prisco2024_initial_lt_4_5", "prisco2024_average_lt_6_0"}


def test_prisco_cutoffs_are_below_and_strict():
    c = evaluate({**_neutral(), "prisco_initial_mv_s": 4.5, "prisco_average_mv_s": 5.99})
    assert c["prisco2024_initial_lt_4_5"] is False and c["prisco2024_average_lt_6_0"] is True


def test_prisco_reference_option():
    m = measure_beat(beat(), FS, onset_ms=ONSET, settings=Settings(prisco_reference="qrs_mean"))
    assert m["prisco_average_by_lead_mv_s"]["V1"] == pytest.approx(18.75, rel=1e-3)
    assert m["settings"]["prisco_reference"] == "qrs_mean"
    with pytest.raises(ValueError):
        Settings(prisco_reference="mean")


def _neutral():
    return {
        "pseudo_delta_ms": 20.0, "idt_v2_ms": 60.0, "srs_ms": 90.0, "mdi_valles": 0.3, "mdi_daniels": 0.3,
        "q_lead_I": False, "inferior_q_all": False, "inferior_q_any": False, "inferior_r_any": True,
        "q_V2": False, "qs_V2": False, "avr_avl_ratio_lt_1": False, "inferior_axis": True,
    }


def test_old_measurement_dicts_still_score():
    c = evaluate(_neutral())
    assert all(c[k] is None for k in SUMMIT)
    assert all(c[k] is None for k in CUTOFFS_BELOW)


def test_json_output_keeps_infinity():
    assert _jsonable({"a": math.inf, "b": NAN, "c": 1.0}) == {"a": "inf", "b": None, "c": 1.0}


def test_yamada_table_3_rows_scored_alone():
    c = summit({"q_ratio_avl_avr": 1.8, "r_ratio_iii_ii": 1.0})
    assert c["yamada2010_avl_avr_gt_1_75"] is True and c["yamada2010_iii_ii_gt_1_25"] is False
    assert c["yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75"] is False


def test_flat_v1_has_no_rs_ratio():
    m = measure(V1=[(o, 0), (o + 60, 0.0), (o + 120, 0)])
    assert math.isnan(m["rs_ratio_v1"])
    assert evaluate(m)["santangeli2015_rs_v1_gt_2"] is None


def test_missing_values_of_any_type():
    import numpy as np

    c = summit({"q_ratio_avl_avr": 2.0, "r_ratio_iii_ii": np.float32("nan"), "rs_ratio_v1": 1.0, "q_V1": NAN})
    assert c["yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75"] is None
    assert c["jauregui2012_iii_ii_lt_1_13"] is None
    assert c["santangeli2015_no_q_v1"] is None and c["santangeli2015_2_of_3"] is None
    # Infinite ratios written as "inf" by the command line score as infinity.
    c = summit({"q_ratio_avl_avr": "inf", "rs_ratio_v1": "inf", "q_V1": False})
    assert c["santangeli2015_2_of_3"] is True and c["jauregui2012_avl_avr_lt_1_45"] is False


def test_prisco_mean_needs_every_lead():
    # A flat lead has no maximum deflection, so the 12-lead average rate is undefined.
    m = measure(aVL=[(o, 0), (o + 60, 0.0), (o + 120, 0)])
    assert math.isnan(m["prisco_average_by_lead_mv_s"]["aVL"])
    assert math.isnan(m["prisco_average_mv_s"]) and math.isnan(m["prisco_average_limb_mv_s"])
    assert not math.isnan(m["prisco_average_precordial_mv_s"])
    assert evaluate(m)["prisco2024_average_lt_6_0"] is None


def test_prisco_qrs_mean_finds_the_peak_of_a_broad_complex():
    # A broad dome in V5 sits far above its own mean; the peak, not the QRS edge, is
    # the maximum deflection: 1.0 mV at 75 ms, 13.3 mV/s.
    dome = [(o, 0), (o + 20, 0.9), (o + 75, 1.0), (o + 130, 0.9), (o + 150, 0)]
    m = measure_beat(beat(V5=dome), FS, onset_ms=ONSET, settings=Settings(prisco_reference="qrs_mean"))
    assert m["prisco_average_by_lead_mv_s"]["V5"] == pytest.approx(1.0 / 0.075, rel=1e-3)
