# ecg_depth_criteria

Python code that measures the published 12-lead ECG criteria for an epicardial
origin of a PVC or VT, each one the way its paper defines it. The same code
scores simulated (openCARP) and real ECGs, so the two are measured identically.
Version 0.1.0, 2 Oct 2026. It needs only numpy; the tests need pytest.

```
python3 -m pip install numpy pytest
python3 -m pytest          # run inside this folder; 40 tests
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
| `bazan2007_*` | LV, no prior MI. Basal superior: q in lead I, and no q in any inferior lead. Apical superior: q in lead I. Basal inferior: q in any inferior lead, and aVR/aVL < 1. Apical inferior: q in any inferior lead. Apex: q in V2 (`_unconfirmed`, as the matched analysis did not confirm it) | Bazan 2007 |
| `bazan2006_*` | RV free wall. Anterior: q in lead I (52%, 94%) and QS in V2 (67%, 61%). Inferior: q in any inferior lead (71%, 74%). RVOT: none | Bazan 2006 |

## How each measurement is defined

| Measurement | Papers | Implementation |
|---|---|---|
| QRS onset | Earliest ventricular activation, or the stimulus artifact when paced (Berruezo, Vallès, Piers, Bazan). Daniels: earliest rapid deflection in any of the 12 leads | Uses the stimulus when one is given. Otherwise it finds the earliest deflection from baseline: the combined magnitude of leads I, II and V1 to V6 is followed back from the steepest part of the QRS until it returns to the baseline noise |
| QRS offset | End of the QRS in the precordial leads (Berruezo, Vallès, Piers); latest end in any lead (Daniels, Bazan 2006) | The point where the combined slope of V1 to V6 (or of I, II and V1 to V6) falls below 10% of its peak and stays down. Reported as `offset_precordial_ms` and `offset_any_lead_ms` |
| Pseudo-delta | Onset to the earliest fast deflection in any precordial lead | The first sample where any precordial slope reaches 30% of the steepest precordial slope in the QRS |
| IDT | Onset to the peak of the R wave in V2 | Peak of the largest positive wave in V2. `Settings(r_peak="first"/"last")` changes this |
| Shortest RS | Onset to the nadir of the first S wave in any precordial lead | In each precordial lead, the nadir of the first negative wave after the first positive wave; the earliest across leads is kept |
| MDI | Onset to the largest deflection in each precordial lead, shortest lead, divided by QRS duration | `mdi_valles` divides by the precordial QRS (Vallès, Piers). `mdi_daniels` divides by the QRS to the latest offset in any lead |
| q wave | Initial negative deflection, sometimes after a short isoelectric segment (Vallès, Piers) | The first wave larger than 0.05 mV after the onset is negative |
| Inferior q | All of II, III and aVF (Piers Q-INF), or any of them (Bazan) | `inferior_q_all`, `inferior_q_any`. `inferior_r_any` is Piers's absence of inferior q |
| QS in V2 | Entirely negative QRS in V2 (Bazan 2006) | Every wave in V2 is negative |
| aVR/aVL < 1 | Bazan 2006 scores a ratio as > 1 when the QRS is more positive or less negative in the first lead | Net amplitude (tallest positive minus deepest negative) is lower in aVR than in aVL |
| Axis, RBBB pattern | Predominant R or S in aVF and in V1 (Piers) | Sign of the net amplitude |

## Choices where the papers are unclear

- **Vallès's "no inferior q"** is defined as an initial positive deflection in
  the inferior leads, without saying all or any. The 4-step therefore follows
  Piers's explicit version: q waves mean all three leads start negative.
  `evaluate(m, valles_inferior="any")` uses the other reading.
- **Vallès step 2** reads ≥ 75 ms in the abstract and Figure 8, but > 75 ms
  in the discussion. The code uses ≥.
- **Bazan 2007** uses amplitude ratios without defining them. The code takes
  the rule from Bazan 2006, by the same group.
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
- `criteria.py`: cut-offs, the Vallès 4-step and the Bazan regions.
- `__main__.py`: the command line.
- `tests/`: synthetic beats with known answers, plus tests for every criterion
  branch.
