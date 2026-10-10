import json

import pytest

from ecg_depth_criteria import CUTOFFS, JOSEPHSON_LV, REGIONS, bazan, evaluate, measure_beat, valles_4step
from ecg_depth_criteria.__main__ import main
from synthetic import FS, ONSET, T, beat

NAN = float("nan")


def morph(**kw):
    """A measurement dict with neutral values; keywords override."""
    m = {
        "pseudo_delta_ms": 20.0, "idt_v2_ms": 60.0, "srs_ms": 90.0,
        "mdi_valles": 0.3, "mdi_daniels": 0.3,
        "q_lead_I": False, "inferior_q_all": False, "inferior_q_any": False, "inferior_r_any": True,
        "q_V2": False, "qs_V2": False, "avr_avl_ratio_lt_1": False, "inferior_axis": True,
    }
    m.update(kw)
    return m


def test_published_cutoffs_on_the_synthetic_beat():
    c = evaluate(measure_beat(beat(), FS, onset_ms=ONSET))
    assert c["berruezo_pdw_ge_34"] is True  # 60 ms
    assert c["berruezo_idt_ge_85"] is True  # 88 ms
    assert c["valles_idt_ge_90"] is False  # 88 ms
    assert c["berruezo_srs_ge_121"] is False  # 100 ms
    assert c["valles_mdi_ge_045"] is True  # 75/160
    assert c["daniels_mdi_ge_055"] is False  # 75/170
    assert (c["valles_4step"], c["valles_4step_step"]) == (True, 4)
    assert c["piers_q_I"] is True and c["piers_abs_q_inf"] is True and c["piers_q_inf"] is None


def test_cutoffs_are_inclusive():
    at = morph(pseudo_delta_ms=34.0, idt_v2_ms=90.0, srs_ms=121.0, mdi_valles=0.45, mdi_daniels=0.55)
    below = morph(pseudo_delta_ms=33.9, idt_v2_ms=84.9, srs_ms=120.9, mdi_valles=0.449, mdi_daniels=0.549)
    assert all(evaluate(at)[name] for name in CUTOFFS)
    assert not any(evaluate(below)[name] for name in CUTOFFS)


def test_missing_measurement_scores_none():
    c = evaluate(morph(idt_v2_ms=NAN, srs_ms=NAN))
    assert c["berruezo_idt_ge_85"] is None and c["valles_idt_ge_90"] is None
    assert c["berruezo_srs_ge_121"] is None
    assert c["berruezo_pdw_ge_34"] is False


@pytest.mark.parametrize(
    "kw, expected",
    [
        (dict(inferior_q_all=True, inferior_q_any=True, pseudo_delta_ms=90.0, q_lead_I=True), (False, 1)),
        (dict(pseudo_delta_ms=75.0), (True, 2)),
        (dict(pseudo_delta_ms=74.0, mdi_valles=0.59), (True, 3)),
        (dict(pseudo_delta_ms=74.0, mdi_valles=0.58, q_lead_I=True), (True, 4)),
        (dict(pseudo_delta_ms=74.0, mdi_valles=0.58, q_lead_I=False), (False, 4)),
        (dict(pseudo_delta_ms=NAN), (None, 2)),
        (dict(mdi_valles=NAN), (None, 3)),
    ],
)
def test_valles_4step(kw, expected):
    assert valles_4step(morph(**kw)) == expected


def test_valles_inferior_q_all_or_any():
    m = morph(inferior_q_any=True, inferior_q_all=False, q_lead_I=True)
    assert valles_4step(m, "all") == (True, 4)
    assert valles_4step(m, "any") == (False, 1)
    with pytest.raises(ValueError):
        valles_4step(m, "most")


def test_piers_q_criteria_follow_the_axis():
    sup = evaluate(morph(inferior_axis=False, inferior_q_all=True, q_lead_I=True))
    assert sup["piers_q_I"] is None and sup["piers_abs_q_inf"] is None
    assert sup["piers_q_inf"] is True


def test_bazan_regions():
    m = measure_beat(beat(), FS)
    assert bazan(m, "lv_basal_superior") == {"bazan2007_q_lead_I": True, "bazan2007_no_inferior_q": True}
    assert bazan(m, "lv_apical_superior") == {"bazan2007_q_lead_I": True}
    assert bazan(m, "lv_basal_inferior") == {"bazan2007_inferior_q": False, "bazan2007_avr_avl_lt_1": True}
    assert bazan(m, "lv_apical_inferior") == {"bazan2007_inferior_q": False}
    assert bazan(m, "lv_apex") == {"bazan2007_q_v2_unconfirmed": False}
    # Apical inferior RV belongs to both the anterior and the inferior group.
    assert set(bazan(m, "rv_apical_inferior")) == {"bazan2006_q_lead_I", "bazan2006_qs_v2", "bazan2006_inferior_q"}
    assert set(bazan(m, "rv_basal_inferior")) == {"bazan2006_inferior_q"}
    assert bazan(m, "rvot") == {} and bazan(m, "rv_basal_superior") == {}
    with pytest.raises(ValueError):
        bazan(m, "lateral")


def test_region_lookup_tables():
    assert JOSEPHSON_LV[10] == JOSEPHSON_LV[12] == "lv_basal_superior"
    assert JOSEPHSON_LV[1] == "lv_apex"
    assert set(JOSEPHSON_LV.values()) <= set(REGIONS)
    assert "bazan2007_q_lead_I" in evaluate(measure_beat(beat(), FS), region="lv_basal_superior")


def test_command_line(tmp_path, capsys):
    x = beat()
    names = ["time", "I", "II", "V1", "V2", "V3", "V4", "V5", "V6"]
    rows = {"I": 0, "II": 1, "V1": 6, "V2": 7, "V3": 8, "V4": 9, "V5": 10, "V6": 11}
    path = tmp_path / "beat.csv"
    with open(path, "w") as f:
        f.write(",".join(names) + "\n")
        for j, t in enumerate(T):
            f.write(",".join([f"{t:.2f}"] + [f"{x[rows[k], j]:.6f}" for k in names[1:]]) + "\n")
    main([str(path), "--fs", str(FS), "--stim-ms", "40", "--region", "lv_basal_superior"])
    out = json.loads(capsys.readouterr().out)
    assert out["measurements"]["onset_source"] == "stimulus"
    assert out["measurements"]["idt_v2_ms"] == pytest.approx(98, abs=0.5)
    assert out["criteria"]["bazan2007_q_lead_I"] is True
    assert out["criteria"]["piers_q_inf"] is None
