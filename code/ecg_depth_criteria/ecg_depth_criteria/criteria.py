"""Published cut-offs and decision rules for an epicardial origin.

Every criterion returns True when it points to an epicardial origin, False
when it does not, and None when it cannot be scored (the measurement does
not exist, such as IDT with a QS complex in V2, or the paper applied it only
to another QRS axis).
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
    return v is None or (isinstance(v, float) and math.isnan(v))


def _at_least(v, cut):
    return None if _missing(v) else bool(v >= cut)


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
    when region is given (see REGIONS and JOSEPHSON_LV).
    """
    out = {name: _at_least(m[key], cut) for name, (key, cut, _) in CUTOFFS.items()}
    out["valles_q_lead_I"] = bool(m["q_lead_I"])
    out["valles_no_inferior_q"] = bool(m["inferior_r_any"])
    out["valles_4step"], out["valles_4step_step"] = valles_4step(m, valles_inferior)
    inferior_axis = bool(m["inferior_axis"])
    out["piers_q_I"] = bool(m["q_lead_I"]) if inferior_axis else None
    out["piers_abs_q_inf"] = bool(m["inferior_r_any"]) if inferior_axis else None
    out["piers_q_inf"] = None if inferior_axis else bool(m["inferior_q_all"])
    if region is not None:
        out.update(bazan(m, region))
    return out
