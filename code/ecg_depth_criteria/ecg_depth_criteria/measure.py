"""Measure one beat of a 12-lead ECG the way the published depth criteria define it."""
from __future__ import annotations

import math
import warnings
from dataclasses import asdict

import numpy as np

from .fiducials import Settings, qrs_offset, qrs_onset, slopes, spatial_velocity, waves
from .leads import INDEPENDENT, INFERIOR, LEADS, PRECORDIAL, rows

NAN = float("nan")


def measure_beat(
    ecg,
    fs: float,
    *,
    stim_ms: float | None = None,
    onset_ms: float | None = None,
    offset_ms: float | None = None,
    baseline_window_ms: tuple | None = None,
    settings: Settings = Settings(),
) -> dict:
    """Measure one beat.

    ecg: (12, n) array in mV, rows in LEADS order (see leads.from_leads).
    fs: sampling rate in Hz. All times are in ms from the first sample.
    stim_ms: pacing stimulus time. When given, every interval starts at the
        stimulus, as in Berruezo 2004, Bazan 2006/2007 and Vallès 2010.
        Blank any stimulus artifact first (simulated ECGs have none).
    onset_ms, offset_ms: override detection, for example with the true
        activation onset from a simulation, to separate measurement error
        from physiology.
    baseline_window_ms: (start, end) of a flat stretch before the QRS. It
        sets each lead's zero and the noise level, and the onset search never
        goes back past its end. Defaults to the settings.baseline_ms before
        the stimulus, else the opening settings.baseline_ms of the segment.
        With real ECGs give one that ends just before the QRS: noise
        measured far from the QRS underestimates the noise near it.
    """
    x = np.asarray(ecg, dtype=float)
    if x.ndim != 2 or x.shape[0] != len(LEADS):
        raise ValueError("ecg must be a (12, n) array in LEADS order; see leads.from_leads()")
    cfg = settings
    fs = float(fs)

    def idx(t_ms: float) -> int:
        return int(round(t_ms * fs / 1000.0))

    def ms(i: int) -> float:
        return i * 1000.0 / fs

    # Isoelectric level per lead.
    if baseline_window_ms is not None:
        b0, b1 = idx(baseline_window_ms[0]), idx(baseline_window_ms[1])
    elif stim_ms is not None:
        b1 = idx(stim_ms)
        b0 = max(0, b1 - idx(cfg.baseline_ms))
    else:
        b0, b1 = 0, idx(cfg.baseline_ms)
    base = slice(b0, max(b1, b0 + 1))
    x = x - np.median(x[:, base], axis=1, keepdims=True)
    peak_mv = float(np.abs(x).max())
    if not 0.1 <= peak_mv <= 50:
        warnings.warn(f"largest deflection is {peak_mv:.3g}; signals must be in mV, or the thresholds in Settings will not fit")

    # QRS boundaries. Onset is the earliest deflection from baseline in any
    # lead; the latest offset in any lead comes from the 8 independent leads
    # and the precordial offset from V1-V6.
    d = slopes(x, fs, cfg.smooth_ms)
    sv_any = spatial_velocity(d[rows(INDEPENDENT)])
    visible_onset = qrs_onset(x[rows(INDEPENDENT)], sv_any, fs, base, cfg)
    d_off = slopes(x, fs, cfg.offset_smooth_ms)
    off_any = qrs_offset(spatial_velocity(d_off[rows(INDEPENDENT)]), fs, base, cfg)
    off_pre = qrs_offset(spatial_velocity(d_off[rows(PRECORDIAL)]), fs, base, cfg)

    if onset_ms is not None:
        on, source = idx(onset_ms), "given"
    elif stim_ms is not None:
        on, source = idx(stim_ms), "stimulus"
    else:
        on, source = visible_onset, "detected"
    if offset_ms is not None:
        off_pre = off_any = idx(offset_ms)
    if not on < min(off_pre, off_any):
        raise ValueError("QRS onset is not before its offset; check the segment, stimulus time and baseline window")
    end = max(off_pre, off_any)

    lead_waves = {k: waves(x[i], on, end, cfg.wave_mv) for i, k in enumerate(LEADS)}
    polarity = {k: (w[0].sign if w else 0) for k, w in lead_waves.items()}

    # Pseudo-delta: onset to the earliest fast deflection in any precordial lead.
    dp = np.abs(d[rows(PRECORDIAL), on : off_pre + 1])
    hits = np.argwhere(dp >= cfg.fast_frac * dp.max())
    j = int(hits[:, 1].min())
    pseudo_delta = ms(j)
    pseudo_delta_lead = PRECORDIAL[int(hits[hits[:, 1] == j][0, 0])]

    # Intrinsicoid deflection time: onset to the peak of the R wave in V2.
    v2 = LEADS.index("V2")
    r_waves = [w for w in lead_waves["V2"] if w.sign > 0 and w.peak <= off_pre]
    if not r_waves:
        idt = NAN
    else:
        if cfg.r_peak == "first":
            r = r_waves[0]
        elif cfg.r_peak == "last":
            r = r_waves[-1]
        else:
            r = max(r_waves, key=lambda w: x[v2, w.peak])
        idt = ms(r.peak - on)

    # Shortest RS: onset to the nadir of the first S wave in any precordial lead.
    srs, srs_lead = NAN, None
    for k in PRECORDIAL:
        w = [v for v in lead_waves[k] if v.start <= off_pre]
        first_r = next((n for n, v in enumerate(w) if v.sign > 0), None)
        if first_r is None:
            continue
        s_wave = next((v for v in w[first_r + 1 :] if v.sign < 0), None)
        if s_wave is not None and (math.isnan(srs) or ms(s_wave.peak - on) < srs):
            srs, srs_lead = ms(s_wave.peak - on), k

    # Maximum deflection index: onset to the largest deflection in each
    # precordial lead, divided by QRS duration; the shortest lead is reported.
    def mdi(offset: int) -> tuple:
        best, best_lead = NAN, None
        for k in PRECORDIAL:
            t = int(np.argmax(np.abs(x[LEADS.index(k), on : offset + 1])))
            value = t / (offset - on)
            if math.isnan(best) or value < best:
                best, best_lead = value, k
        return best, best_lead

    mdi_valles, mdi_valles_lead = mdi(off_pre)  # QRS to the precordial offset (Vallès, Piers)
    mdi_daniels, mdi_daniels_lead = mdi(off_any)  # QRS to the latest offset in any lead (Daniels)

    # Net QRS amplitude: tallest positive minus deepest negative deflection.
    # Bazan 2006 scores a ratio a/b as > 1 when the QRS is more positive or
    # less negative in lead a; Bazan 2007 uses the same ratios without
    # restating the rule. Axis and bundle-branch pattern follow Piers 2014
    # (predominant R or S in aVF and V1).
    def net(k: str) -> float:
        seg = x[LEADS.index(k), on : end + 1]
        return float(max(seg.max(), 0.0) + min(seg.min(), 0.0))

    net_mv = {k: net(k) for k in LEADS}

    qrsd = ms(off_pre - on)
    early = sv_any[on : on + max(idx(20.0), 1)]
    return {
        "onset_ms": ms(on),
        "onset_source": source,
        "visible_onset_ms": ms(visible_onset),
        "offset_precordial_ms": ms(off_pre),
        "offset_any_lead_ms": ms(off_any),
        "qrs_duration_ms": qrsd,
        "qrs_duration_any_lead_ms": ms(off_any - on),
        "pseudo_delta_ms": pseudo_delta,
        "pseudo_delta_lead": pseudo_delta_lead,
        "idt_v2_ms": idt,
        "srs_ms": srs,
        "srs_lead": srs_lead,
        "mdi_valles": mdi_valles,
        "mdi_valles_lead": mdi_valles_lead,
        "mdi_daniels": mdi_daniels,
        "mdi_daniels_lead": mdi_daniels_lead,
        "q_lead_I": polarity["I"] < 0,
        "inferior_q_all": all(polarity[k] < 0 for k in INFERIOR),
        "inferior_q_any": any(polarity[k] < 0 for k in INFERIOR),
        "inferior_r_any": any(polarity[k] > 0 for k in INFERIOR),
        "q_V2": polarity["V2"] < 0,
        "qs_V2": bool(lead_waves["V2"]) and all(w.sign < 0 for w in lead_waves["V2"]),
        "avr_avl_ratio_lt_1": net_mv["aVR"] < net_mv["aVL"],
        "ii_iii_ratio_lt_1": net_mv["II"] < net_mv["III"],
        "inferior_axis": net_mv["aVF"] > 0,
        "rbbb_like": net_mv["V1"] > 0,
        "pseudo_delta_index": pseudo_delta / qrsd,
        "idt_index": idt / qrsd,
        "srs_index": srs / qrsd,
        "initial_velocity_ratio_20ms": float(early.mean() / sv_any.max()),
        "initial_polarity": polarity,
        "net_amplitude_mv": net_mv,
        "settings": asdict(cfg),
    }
