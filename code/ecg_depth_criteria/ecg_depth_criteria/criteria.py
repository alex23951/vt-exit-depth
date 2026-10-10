"""Published cut-offs and decision rules for an epicardial origin.

Every criterion except the LV summit criteria (SUMMIT) returns True when it
points to an epicardial origin, False when it does not, and None when it
cannot be scored (the measurement does not exist, such as IDT with a QS
complex in V2, or the paper applied it only to another QRS axis). A SUMMIT
criterion's True is its paper's own positive class.
"""
from __future__ import annotations

import math

# name: (measurement key, cut-off, source and accuracy in the derivation sample).
# A criterion is positive when the measurement is at or above the cut-off.
CUTOFFS = {
    "berruezo_pdw_ge_34": ("pseudo_delta_ms", 34.0, "Berruezo 2004, VTs: sensitivity 83%, specificity 95%"),
    "berruezo_idt_ge_85": ("idt_v2_ms", 85.0, "Berruezo 2004, VTs: sensitivity 87%, specificity 90%"),
    "berruezo_srs_ge_121": ("srs_ms", 121.0, "Berruezo 2004, VTs: sensitivity 76%, specificity 85%"),
    "daniels_mdi_ge_055": ("mdi_daniels", 0.55, "Daniels 2006, idiopathic VT: sensitivity 100%, specificity 98.7%, cut-off chosen in the same sample"),
    "valles_mdi_ge_045": ("mdi_valles", 0.45, "Valles 2010 revised, NICM pace maps: sensitivity 76%, specificity 75%; also used by Piers 2014"),
    "valles_idt_ge_90": ("idt_v2_ms", 90.0, "Valles 2010 revised, NICM pace maps: sensitivity 76%, specificity 79%"),
}

# name: (measurement key, cut-off, source). Positive (epicardial) when the measurement
# is below the cut-off. Prisco prints no inequality sign; "below" follows the
# Analysis plan's wording.
CUTOFFS_BELOW = {
    "prisco2024_initial_lt_4_5": ("prisco_initial_mv_s", 4.5, "Prisco 2024, NICM VT, mean of 12 leads: sensitivity 0.83, specificity 0.85; how the cut-off was chosen is not stated, reported only in the derivation sample"),
    "prisco2024_average_lt_6_0": ("prisco_average_mv_s", 6.0, "Prisco 2024, NICM VT, mean of 12 leads: sensitivity 1.00, specificity 0.90; how the cut-off was chosen is not stated, reported only in the derivation sample"),
}

# LV summit criteria. True is each paper's positive class, which is a position in
# the summit or a route to successful ablation, not an epicardial origin as for the
# criteria above. All cut-offs are strict, as printed. None was validated in another
# sample; only Jauregui states how its cut-offs were chosen (ROC analysis in the same
# sample).
SUMMIT = {
    "yamada2010_avl_avr_gt_1_1": "Yamada 2010: Q-wave ratio aVL/aVR > 1.1; positive = ablatable from the GCV, AIV or the accessible area, negative = the inaccessible area (sensitivity 87%, specificity 100%)",
    "yamada2010_iii_ii_gt_1_25": "Yamada 2010, Table 3: R-wave ratio III/II > 1.25; positive = the accessible area (pericardial approach), negative = the GCV or AIV, inaccessible-area VAs not compared (100%, 74%)",
    "yamada2010_avl_avr_gt_1_75": "Yamada 2010, Table 3: Q-wave ratio aVL/aVR > 1.75; same classes (100%, 74%)",
    "yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75": "Yamada 2010, Discussion: both of the two above; same classes; accuracy of the combination not reported",
    "santangeli2015_avl_avr_gt_1_85": "Santangeli 2015: Q-wave ratio aVL/aVR > 1.85 (4/5 successful vs 2/18 unsuccessful)",
    "santangeli2015_rs_v1_gt_2": "Santangeli 2015: R/S ratio in V1 > 2 (4/5 vs 5/18)",
    "santangeli2015_no_q_v1": "Santangeli 2015: no initial q wave in V1 (5/5 vs 12/18)",
    "santangeli2015_2_of_3": "Santangeli 2015: at least 2 of the 3 above; positive = successful percutaneous epicardial ablation (100%, 72%)",
    "jauregui2012_avl_avr_lt_1_45": "Jauregui Abularach 2012: Q-wave ratio aVL/aVR < 1.45; positive = successful ablation from the left sinus of Valsalva or the LV endocardium below it (89%, 75%)",
    "jauregui2012_iii_ii_lt_1_13": "Jauregui Abularach 2012: R-wave ratio III/II < 1.13; same positive class (78%, 75%)",
}

# Valles 2010 Fig 8, built for basal superior and lateral LV (Josephson 8, 10, 12) in NICM.
VALLES_PDW_MS = 75.0
VALLES_MDI = 0.59

# Bazan 2007 LV regions by Josephson site.
JOSEPHSON_LV = {
    10: "lv_basal_superior", 12: "lv_basal_superior",
    9: "lv_apical_superior", 11: "lv_apical_superior",
    6: "lv_basal_inferior", 8: "lv_basal_inferior",
    5: "lv_apical_inferior", 7: "lv_apical_inferior",
    1: "lv_apex",
}
LV_REGIONS = ("lv_basal_superior", "lv_apical_superior", "lv_basal_inferior", "lv_apical_inferior", "lv_apex")

# Bazan 2006 RV free-wall segments and the groups its criteria were derived in:
# anterior = apical superior + apical inferior; inferior = basal inferior + apical inferior.
RV_ANTERIOR = ("rv_anterior", "rv_apical_superior", "rv_apical_inferior")
RV_INFERIOR = ("rv_inferior", "rv_basal_inferior", "rv_apical_inferior")
RV_REGIONS = ("rvot", "rv_basal_superior", "rv_apical_superior", "rv_basal_inferior", "rv_apical_inferior", "rv_anterior", "rv_inferior")

REGIONS = LV_REGIONS + RV_REGIONS


def _missing(v) -> bool:
    """None or NaN of any numeric type (a float32 NaN from a table included)."""
    if v is None:
        return True
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return False


# float() also reads the "inf" strings the command line writes for infinite ratios.
def _at_least(v, cut):
    return None if _missing(v) else bool(float(v) >= cut)


def _above(v, cut):
    return None if _missing(v) else bool(float(v) > cut)


def _below(v, cut):
    return None if _missing(v) else bool(float(v) < cut)


def _count_at_least(flags, k: int):
    """True when at least k flags are True, False when that is out of reach, else None."""
    met = sum(f is True for f in flags)
    unknown = sum(f is None for f in flags)
    if met >= k:
        return True
    return False if met + unknown < k else None


def summit(m: dict) -> dict:
    """LV summit criteria (see SUMMIT for each key's positive class).

    Ratios come from measure_beat: q_ratio_avl_avr and r_ratio_iii_ii are wave
    amplitude ratios, rs_ratio_v1 is R over S in V1. A ratio is infinite when only
    its denominator wave is absent and missing (None here) when both are.
    """
    q_ratio, r_ratio, rs_v1 = m.get("q_ratio_avl_avr"), m.get("r_ratio_iii_ii"), m.get("rs_ratio_v1")
    q_v1 = m.get("q_V1")
    yamada_access = (_above(r_ratio, 1.25), _above(q_ratio, 1.75))
    santangeli = (_above(q_ratio, 1.85), _above(rs_v1, 2.0), None if _missing(q_v1) else not q_v1)
    return {
        "yamada2010_avl_avr_gt_1_1": _above(q_ratio, 1.1),
        "yamada2010_iii_ii_gt_1_25": yamada_access[0],
        "yamada2010_avl_avr_gt_1_75": yamada_access[1],
        "yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75": (
            False if False in yamada_access else None if None in yamada_access else True
        ),
        "santangeli2015_avl_avr_gt_1_85": santangeli[0],
        "santangeli2015_rs_v1_gt_2": santangeli[1],
        "santangeli2015_no_q_v1": santangeli[2],
        "santangeli2015_2_of_3": _count_at_least(santangeli, 2),
        "jauregui2012_avl_avr_lt_1_45": _below(q_ratio, 1.45),
        "jauregui2012_iii_ii_lt_1_13": _below(r_ratio, 1.13),
    }


def valles_4step(m: dict, inferior: str = "all") -> tuple:
    """Valles 2010 four-step algorithm. Returns (epicardial, step reached).

    1. q waves in the inferior leads: not epicardial.
    2. Pseudo-delta >= 75 ms: epicardial.
    3. MDI >= 0.59 (QRS to the precordial offset): epicardial.
    4. q wave in lead I: epicardial; otherwise not.

    Valles defines "no inferior q" as an initial positive deflection in the
    inferior leads without saying all or any. inferior="all" follows Piers
    2014, who applied the same definitions: q waves means all of II, III and
    aVF start negative. inferior="any" counts a q in any one of them.
    Step 2 reads ">= 75 ms" in the abstract and Figure 8 and "> 75 ms" in the
    discussion; ">=" is used. epicardial is None when a step's value is missing.
    """
    if inferior not in ("all", "any"):
        raise ValueError("inferior must be 'all' or 'any'")
    if m["inferior_q_all" if inferior == "all" else "inferior_q_any"]:
        return False, 1
    pdw = m["pseudo_delta_ms"]
    if _missing(pdw):
        return None, 2
    if pdw >= VALLES_PDW_MS:
        return True, 2
    mdi = m["mdi_valles"]
    if _missing(mdi):
        return None, 3
    if mdi >= VALLES_MDI:
        return True, 3
    return bool(m["q_lead_I"]), 4


def bazan(m: dict, region: str) -> dict:
    """Region-specific criteria of Bazan 2007 (LV, no prior MI) and Bazan 2006 (RV free wall).

    Bazan 2007, kept only where the anatomically matched analysis confirmed them:
      basal superior: Q in lead I; no Q in any of II, III, aVF.
      apical superior: Q in lead I.
      basal inferior: Q in any of II, III, aVF; aVR/aVL ratio < 1.
      apical inferior: Q in any of II, III, aVF.
      apex: Q in V2, reported but not confirmed in the matched analysis.
    Bazan 2006:
      anterior RV: Q in lead I (sensitivity 52%, specificity 94%); QS in V2 (67%, 61%).
      inferior RV: Q in any of II, III, aVF (71%, 74%).
      RVOT: no criterion separated epicardial from endocardial pace maps.
    """
    if region not in REGIONS:
        raise ValueError(f"unknown region {region!r}; choose from {REGIONS}")
    out = {}
    if region == "lv_basal_superior":
        out["bazan2007_q_lead_I"] = bool(m["q_lead_I"])
        out["bazan2007_no_inferior_q"] = not m["inferior_q_any"]
    elif region == "lv_apical_superior":
        out["bazan2007_q_lead_I"] = bool(m["q_lead_I"])
    elif region == "lv_basal_inferior":
        out["bazan2007_inferior_q"] = bool(m["inferior_q_any"])
        out["bazan2007_avr_avl_lt_1"] = bool(m["avr_avl_ratio_lt_1"])
    elif region == "lv_apical_inferior":
        out["bazan2007_inferior_q"] = bool(m["inferior_q_any"])
    elif region == "lv_apex":
        out["bazan2007_q_v2_unconfirmed"] = bool(m["q_V2"])
    if region in RV_ANTERIOR:
        out["bazan2006_q_lead_I"] = bool(m["q_lead_I"])
        out["bazan2006_qs_v2"] = bool(m["qs_V2"])
    if region in RV_INFERIOR:
        out["bazan2006_inferior_q"] = bool(m["inferior_q_any"])
    return out


def evaluate(m: dict, region: str | None = None, valles_inferior: str = "all") -> dict:
    """Score one beat's measurements (from measure_beat) against every criterion.

    Piers 2014 scored Q-I and the absence of inferior Q waves only in
    inferior-axis VTs, and Q waves in all inferior leads only in
    superior-axis VTs; the other axis gets None. Bazan criteria are added
    when region is given (see REGIONS and JOSEPHSON_LV). The LV summit
    criteria (see SUMMIT) are always added; their True is each paper's own
    positive class, not an epicardial origin.
    """
    out = {name: _at_least(m[key], cut) for name, (key, cut, _) in CUTOFFS.items()}
    out.update({name: _below(m.get(key), cut) for name, (key, cut, _) in CUTOFFS_BELOW.items()})
    out["valles_q_lead_I"] = bool(m["q_lead_I"])
    out["valles_no_inferior_q"] = bool(m["inferior_r_any"])
    out["valles_4step"], out["valles_4step_step"] = valles_4step(m, valles_inferior)
    inferior_axis = bool(m["inferior_axis"])
    out["piers_q_I"] = bool(m["q_lead_I"]) if inferior_axis else None
    out["piers_abs_q_inf"] = bool(m["inferior_r_any"]) if inferior_axis else None
    out["piers_q_inf"] = None if inferior_axis else bool(m["inferior_q_all"])
    out.update(summit(m))
    if region is not None:
        out.update(bazan(m, region))
    return out
