# Step 2.3: regression of ecg_depth_criteria 0.4.0 against 0.3.0 (bit-exact)

PC clock 2026-10-16 23:12-23:17 CEST. Script `regression.py`; result `regression.json` (all_pass: true). Wall time 300 s.

**Beats:** every saved v5 beat, 579 in all: 432 paced sites + 3 His beats (network) and 144 no-network beats
(analysis/audit_addendum_2026-10-14/maps). They are prepared as in the 14 Oct rescore (60 ms flat pad; the project's
noise code at 0.05-100 Hz with the notch off).

**Conditions per beat (7,527 measurements per rule):**
- true, stimulus and detected onset on the clean ECG
- stimulus onset with 10 uV noise, seeds 0-9, for the pace-map families
- detected onset with 10 uV noise, seeds 0-9, for the control heart and the His beats

Each measurement is made with the 0.3.0 copy (runs/v51_2026-10-15/pkg_030, the six sha256 prefixes checked) and with
0.4.0 under the rules below. The comparison covers every output of measure_beat and evaluate (flattened; nested dicts
per lead).

| 0.4.0 rule | Expected | Result |
|---|---|---|
| `Settings(q_window_ms=None, recog_mv=None)` | every 0.3.0 output identical | PASS: 7,527 / 7,527 identical on every 0.3.0 key (0 keys differed) |
| N = 20 ms, CSE (recog_mv 0.02) | identical except the q outputs and the criteria reading them | PASS: 0 unexpected differences |
| N = 20 ms, window only (recog_mv None) | same | PASS |
| N = 40 ms, CSE | same | PASS |
| N = 40 ms, window only | same | PASS |

**Outputs allowed to differ:**
- measurements: initial_polarity, q_lead_I, inferior_q_all / any, inferior_r_any, q_V1, q_V2, qs_V2, q_amplitude_mv, q_ratio_avl_avr, rs_ratio_v1
- criteria: valles_q_lead_I, valles_no_inferior_q, valles_4step(_step), piers_q_I / abs_q_inf / q_inf, yamada2010_avl_avr_*, santangeli2015_*, jauregui2012_avl_avr_lt_1_45, the Bazan 2007 / 2006 q items

**Outputs that must not differ, and did not:** QRS onset / offset / duration, pseudo-delta, IDT, shortest RS, MDI (both),
net amplitudes, R and S amplitudes, Prisco rates, initial velocity ratio, axis and RBBB flags, and every criterion built
on them (Berruezo, Daniels, Vallès MDI / IDT, Prisco, Yamada and Jauregui III/II, Bazan aVR/aVL).

New 0.4.0 outputs (q_anchor_ms, initial_start_ms, initial_sign, the four new settings) are not part of 0.3.0 and were not
compared. Unscorable beats (onset not before offset) under 0.3.0: 0, and 0.4.0 raises in exactly the same cases.
As the brief asks, only identity was asserted here; the q-call comparison is in Step 2.5.
