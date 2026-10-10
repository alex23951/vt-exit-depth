# ecg_depth_criteria

Python code that measures the published 12-lead ECG criteria for an epicardial
origin of a PVC or VT, each one the way its paper defines it. The same code
scores simulated (openCARP) and real ECGs, so the two are measured identically.
Version 0.3.0, 4 Oct 2026. It needs only numpy; the tests need pytest.

Changes in 0.3.0: adds the LV summit criteria of Yamada 2010, Santangeli 2015
and Jauregui Abularach 2012, and Prisco 2024's two rates of change, with the
Q-, R- and S-wave amplitudes they need. Alex chose to add them on 3 Oct 2026
(Analysis plan, comparators). Nothing measured by 0.2.0 changes.

Changes in 0.2.0: IDT is measured to the first positive wave in V2 instead of
the largest. In the 3 Oct 2026 pilot grid, all 40 IDT ≥ 85 ms calls in the
control heart came from a positive wave at the very end of the QRS in V2.
Alex chose the change, which is recorded in the Analysis plan.

```
python3 -m pip install numpy pytest
python3 -m pytest          # run inside this folder; 63 tests
```

## Use

```python
from ecg_depth_criteria import from_leads, measure_beat, evaluate

# One beat, signals in mV, all the same length. III, aVR, aVL and aVF are
# derived from I and II when missing.
ecg = from_leads({"I": i, "II": ii, "V1": v1, "V2": v2, "V3": v3, "V4": v4, "V5": v5, "V6": v6})

m = measure_beat(ecg, fs=1000, stim_ms=20)   # paced beat: intervals start at the stimulus
c = evaluate(m, region="lv_basal_superior")  # region adds the Bazan criteria for that site
```

- Signals must be in mV. The thresholds assume it, and the code warns when the
  largest deflection is outside 0.1 to 50 mV.
- Spontaneous beats or VT: leave out `stim_ms` and the onset is detected.
- Real ECGs: also give `baseline_window_ms=(start, end)`, a flat stretch that
  ends just before the QRS (see Accuracy).
- Simulated beats: run once as above. Then run again with `onset_ms` and
  `offset_ms` taken from the activation map; the difference between the two
  runs is measurement error, not physiology.
- Regions are listed in `REGIONS`. `JOSEPHSON_LV` converts a Josephson LV site
  number to its region.

From the command line, with a CSV that has a header row of lead names and one
row per sample (a `time` column is ignored):

```
python3 -m ecg_depth_criteria beat.csv --fs 1000 --stim-ms 20 --region lv_basal_superior
```

In the JSON it prints, NaN is null and an infinite ratio is the string "inf";
`evaluate()` reads that string back as infinity.

## Criteria scored by `evaluate()`

True points to an epicardial origin. None means the criterion cannot be
scored: either the measurement does not exist (IDT with a QS complex in V2),
or the paper applied it only to the other QRS axis.

| Key | Rule | Source, population, accuracy reported |
|---|---|---|
| `berruezo_pdw_ge_34` | pseudo-delta ≥ 34 ms | Berruezo 2004, RBBB VT, mostly post-MI; sens 83%, spec 95% |
| `berruezo_idt_ge_85` | IDT in V2 ≥ 85 ms | Berruezo 2004; 87%, 90% |
| `berruezo_srs_ge_121` | shortest RS ≥ 121 ms | Berruezo 2004; 76%, 85% |
| `daniels_mdi_ge_055` | MDI ≥ 0.55, QRS to the latest offset in any lead | Daniels 2006, idiopathic VT; 100%, 98.7%, cut-off chosen in the same sample |
| `valles_mdi_ge_045` | MDI ≥ 0.45, QRS to the precordial offset | Vallès 2010 revised, NICM pace maps; 76%, 75%. Piers 2014 also used it |
| `valles_idt_ge_90` | IDT ≥ 90 ms | Vallès 2010 revised; 76%, 79% |
| `valles_q_lead_I` | q wave in lead I | Vallès 2010, pace maps; 91%, 96% |
| `valles_no_inferior_q` | II, III or aVF starts positive | Vallès 2010; 99%, 58% |
| `valles_4step`, `valles_4step_step` | inferior q → not epi; PdW ≥ 75 ms → epi; MDI ≥ 0.59 → epi; q in lead I → epi; else not | Vallès 2010 Fig 8, basal superior and lateral LV in NICM; 96%, 93% on pace maps |
| `piers_q_I`, `piers_abs_q_inf` | q in lead I; II, III or aVF starts positive. Inferior-axis VT only | Piers 2014, NICM RBBB VT; Q-I 88%, 80% |
| `piers_q_inf` | II, III and aVF all start negative. Superior-axis VT only | Piers 2014; 73%, 67% |
| `bazan2007_*` | LV, no prior MI; each feature is scored as its own key. Basal superior: q in lead I; no q in any inferior lead. Apical superior: q in lead I. Basal inferior: q in any inferior lead; aVR/aVL < 1. Apical inferior: q in any inferior lead. Apex: q in V2 (`_unconfirmed`, as the matched analysis did not confirm it) | Bazan 2007 |
| `bazan2006_*` | RV free wall; each feature is scored as its own key. Anterior: q in lead I (52%, 94%); QS in V2 (67%, 61%). Inferior: q in any inferior lead (71%, 74%). RVOT: none | Bazan 2006 |
| `prisco2024_initial_lt_4_5` | Initial rate of change, mean of 12 leads, below 4.5 mV/s | Prisco 2024, nonischemic VT, 8 epicardial vs 18 endocardial; 0.83, 0.85, in the derivation sample (how the cut-off was chosen is not stated) |
| `prisco2024_average_lt_6_0` | Onset-to-maximum-deflection rate, mean of 12 leads, below 6.0 mV/s | Prisco 2024; 1.00, 0.90 |

### LV summit criteria

These predict where in the LV summit an arrhythmia sits, or whether ablation
from a given route works, not depth. So here True is each paper's own positive
class, not an epicardial origin. All cut-offs are strict, as printed. None was
tested outside the small sample it was reported in; only Jauregui says how its
cut-offs were chosen (ROC analysis in that sample). Descriptions are in
`SUMMIT`.

Each rule applies only to its paper's population. Yamada: idiopathic
arrhythmias from the LV summit (the III/II and aVL/aVR > 1.75 rules only among
those not from the inaccessible area, 4 vs 19). Santangeli: LV summit
arrhythmias taken to percutaneous epicardial ablation after failed ablation
from adjacent sites. Jauregui: arrhythmias whose earliest site was in the
distal great cardiac vein or proximal anterior interventricular vein, ablated
from the left sinus of Valsalva region. `evaluate()` still scores them on
every beat.

| Key | Rule | Positive class (negative class); accuracy |
|---|---|---|
| `yamada2010_avl_avr_gt_1_1` | Q-wave ratio aVL/aVR > 1.1 | Ablatable from the GCV, AIV or the accessible area (the inaccessible area); 87%, 100%, 27 patients |
| `yamada2010_iii_ii_gt_1_25`, `yamada2010_avl_avr_gt_1_75` | R-wave ratio III/II > 1.25; Q-wave ratio aVL/aVR > 1.75 (Table 3, one row each) | The accessible area, needing a pericardial approach (origins in the GCV or AIV); 100%, 74% for each ratio alone |
| `yamada2010_iii_ii_gt_1_25_and_avl_avr_gt_1_75` | Both of the two above, as the Discussion words it (p622) | Same classes; the accuracy of the combination is not reported |
| `santangeli2015_avl_avr_gt_1_85`, `_rs_v1_gt_2`, `_no_q_v1` | Q-wave ratio aVL/aVR > 1.85; R/S in V1 > 2; no initial q in V1 | Each component alone: 4/5 vs 2/18, 4/5 vs 5/18, 5/5 vs 12/18 |
| `santangeli2015_2_of_3` | At least 2 of the 3 | Successful percutaneous epicardial ablation (failed or not attempted); 100%, 72%, 23 patients |
| `jauregui2012_avl_avr_lt_1_45` | Q-wave ratio aVL/aVR < 1.45 | Successful ablation from the left sinus of Valsalva or the LV endocardium below it (failed from there); 89%, 75%, 17 arrhythmias |
| `jauregui2012_iii_ii_lt_1_13` | R-wave ratio III/II < 1.13 | Same; 78%, 75% |

## How each measurement is defined

| Measurement | Papers | Implementation |
|---|---|---|
| QRS onset | Earliest ventricular activation, or the stimulus artifact when paced (Berruezo, Vallès, Piers, Bazan). Daniels: earliest rapid deflection in any of the 12 leads | Uses the stimulus when one is given. Otherwise it finds the earliest deflection from baseline: the combined magnitude of leads I, II and V1 to V6 is followed back from the steepest part of the QRS until it returns to the baseline noise |
| QRS offset | End of the QRS in the precordial leads (Berruezo, Vallès, Piers); latest end in any lead (Daniels, Bazan 2006) | The point where the combined slope of V1 to V6 (or of I, II and V1 to V6) falls below 10% of its peak and stays down. Reported as `offset_precordial_ms` and `offset_any_lead_ms` |
| Pseudo-delta | Onset to the earliest fast deflection in any precordial lead | The first sample where any precordial slope reaches 30% of the steepest precordial slope in the QRS |
| IDT | Onset to the peak of the R wave in V2 | Peak of the first positive wave in V2, since a later positive wave after an S wave is R′. Positive pieces split by a notch that never turns negative (noise on a slow upstroke) count as one wave. Version 0.1.0 used the largest positive wave; that is now the sensitivity analysis, `Settings(r_peak="largest")` (`"last"` also exists) |
| Shortest RS | Onset to the nadir of the first S wave in any precordial lead | In each precordial lead, the nadir of the first negative wave after the first positive wave; the earliest across leads is kept |
| MDI | Onset to the largest deflection in each precordial lead, shortest lead, divided by QRS duration | `mdi_valles` divides by the precordial QRS (Vallès, Piers). `mdi_daniels` divides by the QRS to the latest offset in any lead |
| q wave | Initial negative deflection, sometimes after a short isoelectric segment (Vallès, Piers) | The first wave larger than 0.05 mV after the onset is negative |
| Inferior q | All of II, III and aVF (Piers Q-INF), or any of them (Bazan) | `inferior_q_all`, `inferior_q_any`. `inferior_r_any` is Piers's absence of inferior q |
| QS in V2 | Entirely negative QRS in V2 (Bazan 2006) | Every wave in V2 is negative |
| aVR/aVL < 1 | Bazan 2006 scores a ratio as > 1 when the QRS is more positive or less negative in the first lead | Net amplitude (height of the tallest positive peak minus depth of the deepest negative peak) is lower in aVR than in aVL |
| Axis, RBBB pattern | Predominant R or S in aVF and in V1 (Piers) | Sign of the net amplitude |
| Q-, R- and S-wave amplitude | Not defined in the text of Yamada 2010, Santangeli 2015 or Jauregui 2012. Santangeli's Figure 3 measures from the pre-QRS baseline to the nadir of the negative deflection (QS complexes in aVL and aVR) and to the R peak in II and III; Jauregui's Figure 5 labels whole QS complexes in aVL and aVR as "Q" | In mV from the isoelectric level, as positive numbers (`q_amplitude_mv`, `r_amplitude_mv`, `s_amplitude_mv`, every lead). Q: the opening wave when it is negative, a whole QS complex included; 0 when the lead starts positive. R: the first positive wave (as for IDT; `Settings.r_peak` also applies here); 0 when there is none. S: the first negative wave after the first R; 0 when there is none. Pieces of one sign split by a notch inside the wave threshold are one wave |
| Q-wave ratio aVL/aVR, R-wave ratio III/II | aVL over aVR (all three papers); III over II (Yamada, Jauregui). Santangeli reports the R ratio as II/III and uses it in no criterion | `q_ratio_avl_avr`, `r_ratio_iii_ii`. Infinite when only the denominator's wave is absent; missing (NaN, so the criterion is None) when both are |
| R/S in V1 | "R-wave to S-wave ratio in lead V1" (Santangeli) | `rs_ratio_v1`: R over S amplitude. Infinite with an R and no S (a monophasic R); 0 with no R (QS); missing when V1 has no wave at all |
| Initial q in V1 | Not defined beyond "initial q wave" (Santangeli) | `q_V1`: the first wave in V1 is negative, as for the other q waves, so a QS complex counts as a q |
| Prisco initial rate | \|V(onset + 30 ms) − V(onset)\| / 30 ms in each lead, averaged over the 12 leads, on a signal-averaged VT beat with a manually set onset | `prisco_initial_mv_s`: the same two-point chord in each lead from the package's single QRS onset to the sample nearest 30 ms later, divided by the time to that sample (exactly 30 ms at 1 or 2 kHz, 29.7 ms at the paper's 977 Hz), in mV/s, averaged over the 12 leads. Limb (I, II, III, aVR, aVL, aVF) and precordial means and per-lead values are also returned |
| Prisco average rate | \|V(onset) − V(max)\| / (time to max) in each lead, where max is the lead's maximum deflection, "the furthest point from the average of the signal" (Methods) or "max deflection from baseline" (Figure 2) | `prisco_average_mv_s`: the maximum deflection is the point between the onset and the latest offset furthest from the isoelectric level. `Settings(prisco_reference="qrs_mean")` instead takes the lead's wave peak furthest from its mean over that window, one reading of the Methods; only wave peaks qualify, as Figure 3 marks the peak, because a broad monophasic complex is otherwise furthest from its own mean at the QRS edges. Either mean is undefined when any lead's rate is (a flat lead has no maximum deflection) |

## Choices where the papers are unclear

- **Vallès's "no inferior q"** is defined as an initial positive deflection in
  the inferior leads, without saying all or any. The 4-step therefore follows
  Piers's explicit version: q waves mean all three leads start negative.
  `evaluate(m, valles_inferior="any")` uses the other reading.
- **Berruezo's IDT** reads ≥ 85 ms in the abstract and results, but > 85 ms
  in the discussion. The code uses ≥.
- **Vallès step 2** reads ≥ 75 ms in the abstract and Figure 8, but > 75 ms
  in the discussion. The code uses ≥.
- **Bazan 2007** uses amplitude ratios without defining them. The code takes
  the rule from Bazan 2006, by the same group.
- **Summit wave amplitudes** are not defined in the text of any of the three
  papers. The two figures that show them (above) show only QS complexes in aVL
  and aVR and upright R waves in II and III. The code follows them: baseline to
  nadir or peak, with a QS complex counted as a Q wave. Everything else is the
  code's choice. A lead that opens with a positive wave larger than 0.05 mV has
  no Q wave, so an rS complex in aVL gives a Q-wave ratio of 0, although
  Jauregui calls the quantity "the amplitude ratio of the negative deflection
  in aVL/aVR" (p871), which would measure the S. R is the first positive wave
  and S the first negative wave after it. How the papers handled a missing
  wave is not stated. The code uses arithmetic: a ratio is infinite when only
  its denominator wave is missing, and missing when both are. R/S in V1 is 0
  when there is no R and missing when V1 has no wave.
- **The 0.05 mV wave threshold** decides whether a small wave exists. A
  0.049 mV QS in aVR makes aVL/aVR infinite, while 0.051 mV gives 11.8. Check
  any ratio whose denominator lead is near that size, which matters most for
  small simulated leads.
- **Yamada's III/II and aVL/aVR > 1.75 rules**: the results (p621) say "both a
  III/II amplitude ratio >1.25 and aVL/aVR amplitude ratio >1.75 predicted
  necessity of a pericardial approach", and Table 3 gives 100%, 74% to each
  ratio in its own row. Only the Discussion (p622) words them as one combined
  rule. The code scores each ratio alone and the combination; requiring both
  is a choice.
- **Prisco 2024** prints no inequality sign for its cut-offs. "Below", as in
  the Analysis plan, is used, so a value of exactly 4.5 or 6.0 mV/s is not
  epicardial. The paper also does not say whether one onset serves all 12
  leads (the code uses one), over what window "the average of the signal" is
  taken (the code uses the isoelectric level by default), or which limb leads
  it averaged (it prints "I, II, II, aVR, aVL, aVF" in the Methods and "I, II,
  II, aVF, aVL, and aVF" in the Results, never lead III; the code uses the six
  limb leads). It defines no QRS end; the code looks for the maximum
  deflection only between the onset and the latest QRS offset. Its formula
  divides by 30 ms; the code divides by the time to the sample nearest 30 ms.
  The paper required usable recordings in every lead, so a lead whose rate is
  undefined makes the mean, and the criterion, undefined. Its rates are in mV/s, so unlike the ratio criteria they depend on
  the ECG's amplitude scale, and a paced beat timed from the stimulus includes
  the stimulus latency in its first 30 ms. Its Tables 2 and 3 are not
  consistent with each other (sensitivity 1.00 at 6.0 mV/s with an epicardial
  mean of 6.3 mV/s), so its accuracy figures are uncertain.
- **"Fast deflection"** (30% of the steepest slope) and **"wave"** (0.05 mV,
  0.5 mm at standard gain) are operational choices, not taken from the papers.
  Change them in `Settings` only for sensitivity analyses, and use the same
  settings for simulated and real ECGs. Every result records its settings.

## Accuracy on synthetic beats

The test beat is a wide QRS with a slow 60 ms start. Its true pseudo-delta is
60 ms, IDT 88 ms, shortest RS 100 ms and MDI 75/160. Results over 50
band-limited noise draws, with a baseline window ending 5 ms before the QRS:

| Noise per lead | Onset error, mean [range] | Offset error | Intervals with true onset |
|---|---|---|---|
| none | +0.5 ms | −0.5 (precordial), −1.5 (any lead) | within 0.5 ms |
| 5 µV | +0.7 [−5, +3] ms | within 2 ms | within 0.5 ms |
| 10 µV | +1.4 [−5, +5] ms | within 2.5 ms | within 1 ms |
| 20 µV | +3.1 [−5, +9] ms | precordial within 2, any lead −9.5 to +2.5 ms | within 2 ms |

Noise mostly makes the detected onset late, which shortens every interval. It
is never placed before the end of the baseline window. If that window is far
from the QRS, it underestimates the noise near the QRS, and the onset then
comes early, at the window's end. With real ECGs:

- average several beats first;
- give a baseline window that ends just before the QRS;
- check the onset by eye, or give `onset_ms`.

Piers found that interval criteria failed in fast VT, where the T wave hid the
QRS onset. No detector fixes that.

## Exploratory measures (not from any paper)

These are candidate conduction-normalised markers. Define them in the
pre-registration before using them.

- `pseudo_delta_index`, `idt_index`, `srs_index`: each interval divided by the
  precordial QRS duration.
- `initial_velocity_ratio_20ms`: mean combined slope over the first 20 ms,
  divided by its peak.

## Files

- `leads.py`: lead order and `from_leads`.
- `fiducials.py`: settings, QRS onset and offset, and wave detection.
- `measure.py`: `measure_beat`.
- `criteria.py`: cut-offs, the Vallès 4-step, the Bazan regions and the LV summit criteria.
- `__main__.py`: the command line.
- `tests/`: synthetic beats with known answers, plus tests for every criterion
  branch. `test_summit_prisco.py` checks that QS complexes with the depths
  printed in Jauregui 2012's Figure 5 give its printed ratios (3.46 and 0.60;
  the paper truncates 1.04/0.30 = 3.47 and 0.59/0.97 = 0.61).
