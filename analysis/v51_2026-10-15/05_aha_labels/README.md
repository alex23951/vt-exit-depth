# Step 5 (decision F): AHA-segment labels and a placement rule, STOP 5

PC clock 2026-10-18 17:10-17:25 CEST. Alex 15:06:23 UTC: "Yes" (tag v5.1 and Step 5).
- **Read only:** no site moved, no beat run. sites.json and sites.csv are unchanged (sha256 before and after equal).
- **Script:** aha51.py. It uses the frame and insertion rule of the 14 Oct audit's a05_site_labels.py and
  a11_aha_thickness.py (copies here; sha256 of the originals in audit_originals.sha256).
- **Outputs:** pilot_site_labels.csv, insertions.json, placement_dry_run.csv, summary.json.

## Rule (from the audit; the level thirds, the apex cap and the body-defined basal / apical are my reading)

- **Long axis:** apex node -> mitral-ring centroid. f = fraction along it.
- **Short-axis angle:** 0 = towards the RV septal centre, + = towards the body's anterior.
- **RV insertion lines:** LV epicardium within 2 mm of the RV epicardium. The anterior and inferior insertion angles are
  medians at the site's own height (+-3 mm).
- **AHA segments (Cerqueira 2002):**
  - levels by thirds of f, with an apex cap below f 0.08 (segment 17);
  - septum = the arc between the insertions;
  - free wall: 4 equal parts at basal and mid, 3 at apical.
- **AV-ring sites:** sites above the last height that has an LV slab and both insertions take that height's frame (noted
  per site): 8 / 18 / 16 sites in Y5HYEDL4 / 6G8DD8S5 / 7D98EVAR.
- **Body-defined Bazan region:**
  - superior / inferior = the sign of the site direction along the body's superior axis, projected into the short-axis
    plane;
  - basal / apical = f >= 0.5 or below.

## Insertion points (anterior / inferior angle, septal arc; degrees)

| | basal (f 0.725) | mid (f 0.475) | apical (f 0.225) |
|---|---|---|---|
| Y5HYEDL4 | +80 / -68, 149 | +77 / -66, 143 | +60 / -48, 108 |
| 6G8DD8S5 | +70 / -51, 121 | +66 / -67, 133 | +60 / -62, 121 |
| 7D98EVAR | +66 / -63, 129 | +64 / -63, 127 | +42 / -40, 82 |

## Pilot labels (pilot_site_labels.csv: all 144 sites per heart)

- **Segments:** every LV-side site gets exactly one AHA segment: 100 / 100 per heart, 300 / 300 in all. Acceptance: PASS.
  - Aortic-cusp sites are labelled by the segment they project onto and flagged as aortic root.
  - RV-family sites get "n/a".
- **Old vs body-defined Bazan region:** they disagree at 25 / 24 / 24 LV sites. This is the audit's F02: UVC phi is centred
  near the septum.
- **Pooled LV-wall positions for Bazan 2007:** 45 positions (free wall, vein course, summit) over the three hearts.

  | Region | Old UVC labels | Body-defined labels |
  |---|---|---|
  | Basal superior | 21 | 17 |
  | Basal inferior | 8 | 16 |
  | Apical superior | 9 | 6 |
  | Apical inferior | 7 | 6 |

- **Flagged LV-tagged RV sites (element tags of the site node; 1 = LV myocardium, 25 / 29 = other labels of the cohort
  mesh):**
  - 6G8DD8S5 rv_free_wall_q75_z0.25: d10 "1 29", d50 "1", d75 "1", d90 "25".
  - 7D98EVAR rv_free_wall_q25_z0.25: d10 "29", d50 "1", d75 "1", d90 "25".

## Placement rule for study hearts (geometry-only dry run on the pilot hearts; a proposal)

- **Placement:**
  - one transmural line per AHA segment centre (the centre angle of its arc at the middle of its level);
  - from the LV endocardium to the epicardium (free wall) or to the RV endocardium (septum);
  - sites at 10 / 50 / 75 / 90 % of the line, named by segment;
  - Bazan regions from the body axes;
  - 17 segments x 4 depths = 68 LV sites per heart. Other families (RV, RVOT, cusps, summit, vein course) are kept as
    now.
- **Dry run:**
  - 200 of 204 placed points land in their own target segment.
  - Exception: 6G8DD8S5's segment 17. Its endocardial apex lies at f 0.148 (thick apical wall, 14 mm), above the
    0.08 apex-cap limit, so the cap rule must be anchored to the endocardial apex for study hearts (proposal).
  - The new points are 13.5 mm (median; at most 28 mm) from the nearest old pilot LV site. Wall length along the lines:
    3.3-15.7 mm.
- **Decision for Alex before any study heart runs:** which segments to use, how many sites per segment, and the apex-cap
  rule.

## Reading of decision F (to confirm)

- Step 6 scores the Bazan 2007 gate with the old labels, so it stays comparable with 13 Oct.
- The AHA / body-label version is printed beside it with its position count.
- With 17 pooled basal-superior positions, below the 20 required, the body-label version is "not evaluable". On 14 Oct
  the audit's body regions gave 4 / 14 vs 1 / 14.

## Addendum 18 Oct 2026 22:50 CEST: placement rule adopted (Alex, 20:45:11 UTC, "Yes to all")

**The adopted rule for the study hearts:**
- 17 AHA segments x 4 depths (10 / 50 / 75 / 90 %) = 68 LV sites per heart, at the segment centres, named by segment.
- Bazan regions are taken from the body axes.
- Other families (RV, RVOT, cusps, summit, vein course) stay as in the pilot grid.

**The apex cap is anchored to the endocardial apex:**
- Segment 17 is the myocardium below the lowest LV endocardial node (Cerqueira: beyond the end of the cavity), at least f < 0.08.
- Cap limits: Y5HYEDL4 0.08, 6G8DD8S5 0.148, 7D98EVAR 0.081.

**The level thirds now run from the end of the cavity to the mitral ring.** I made this follow-on change myself: Cerqueira divides the LV with myocardium all around, not the whole apex-to-base axis.
- Why: with the anchored cap but thirds of the whole axis, 3 outer points of 6G8DD8S5's thick apex (segments 13 and 15 at 75-90 %) fell inside the cap.

**Effect on the outputs:**
- **Dry run:** 204 / 204 points land in their own segment, including segment 17 in all three hearts.
- **Pilot labels:** 18 pilot sites move across a level boundary (Y5HYEDL4 4, 6G8DD8S5 12, 7D98EVAR 2; mostly basal -> mid septal sites near f 0.68-0.71).
- **No change:** the body-defined Bazan regions (0 changes) and no gate.
- **Undo:** if Alex prefers thirds of the whole axis, reverting is one line.
