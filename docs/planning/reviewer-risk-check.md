# Reviewer Risk Check

This file tracks likely reviewer criticisms for the current manuscript:

**Validation and Calibration Diagnostics for Migratory-Route Comparison from
Incomplete Animal Tracking Data**

## Risk 1: "Brownian bridge is too simple to be a movement model."

Status: Mitigated as a transparent baseline, with validation and sensitivity checks.

Response:

- Do not claim the Brownian bridge is the final reconstruction model.
- Present it as a transparent movement-aware baseline.
- Emphasize that the paper's target is downstream route-comparison stability,
  not proof of true-path recovery.

Current manuscript defense:

- Methods says the Brownian bridge is a practical baseline, not a full movement
  model.
- Results include a withheld-segment validation showing the baseline is not
  fully calibrated for true-path recovery.
- Results now include an empirical radius-inflation diagnostic estimating how
  much the Brownian envelope must be widened to approach nominal 90% coverage.
- Results include a scale-sensitivity check at 60% contiguous gaps, showing
  downstream diagnostics can change under scale inflation.
- Discussion states that richer movement models are needed for calibrated path
  recovery.

Remaining improvement:

- Compare against a richer continuous-time or state-space movement model if the
  paper is expanded beyond the current diagnostic scope.

## Risk 2: "There is no withheld-gap validation."

Status: Mitigated with a lightweight validation.

Response:

- The complete-route baseline tests stability of route-comparison
  conclusions after controlled data removal.
- A separate withheld-segment validation now compares deterministic spherical
  bridges and Brownian bridge samples with hidden observed route segments.
- The validation shows that the Brownian bridge is not fully calibrated for
  true-path recovery, which supports the conservative baseline framing.

Current manuscript defense:

- Methods and Results now include a withheld-segment validation.
- Results include empirical coverage calibration through a radius-inflation
  factor.
- Discussion states that the paper remains primarily a downstream stability
  study and that richer movement models are needed for calibrated path recovery.

Remaining improvement:

- Expand validation across more gap locations, sampling intervals, and movement
  model classes if time permits.

## Risk 3: "Only one species and one dataset."

Status: Mitigated by framing as a reproducible case study.

Response:

- Frame the manuscript as a reproducible ecological-informatics case study.
- Avoid claiming species-general ecological conclusions.
- Emphasize that the validate--calibrate--propagate diagnostic is transferable
  even if the empirical result is dataset-specific.

Remaining improvement:

- Add another public dataset only if it can be processed without derailing the
  manuscript.

Current manuscript defense:

- Abstract now calls the empirical analysis a reproducible case study.
- Introduction states that the gull data are used to demonstrate the diagnostic
  framework, not to make species-general biological claims.
- Discussion separates dataset-specific empirical numbers from the
  dataset-agnostic diagnostic framework.

## Risk 4: "Route segmentation is heuristic."

Status: Mitigated.

Response:

- Treat segmentation as transparent candidate-route extraction.
- Do not claim exact migration departure/arrival or behavioral-state labels.
- Downstream cluster/anomaly results are computational diagnostics, not
  biological classifications.

Current manuscript defense:

- Data section says segmentation is reproducible but not a validated
  behavioral-state classifier.
- Data section now reports a threshold sensitivity check: moderate
  departure/return and near-maximum-distance threshold changes retain 377 to
  383 total transit routes, compared with 381 under the baseline rule.
- Discussion states that this does not validate biological departure or arrival
  times.

## Risk 5: "The novelty is not a new model."

Status: Central positioning issue.

Response:

- The novelty is not Brownian bridge itself.
- The novelty is the validated and calibrated uncertainty diagnostic: tracking
  gaps -> plausible reconstructed routes -> withheld-segment validation ->
  empirical envelope calibration -> downstream distance, clustering, and anomaly
  stability.
- Keep language focused on ecological-informatics diagnostics and
  decision-stability.

Remaining improvement:

- Add a concise diagnostic/algorithm box if the journal format permits.

## Risk 6: "SRVF-DTW distracts from the missing-data paper."

Status: Mostly mitigated.

Response:

- Keep raw DTW and SRVF-DTW as downstream diagnostic metrics.
- Do not argue that SRVF-DTW is superior.
- The paper asks whether conclusions under different route representations are
  stable under missing-route uncertainty.

## Current Safe Core Claim

The safest claim is:

> Migratory-route comparison can be stable under random point loss yet unstable
> under prolonged contiguous tracking gaps. A practical route-comparison
> diagnostic should therefore validate and, when needed, calibrate plausible
> missing-route uncertainty before propagating it into downstream distance
> matrices, cluster labels, and anomaly rankings.

## Claims To Avoid

- The Brownian bridge recovers true unobserved migration paths.
- The results generalize biologically beyond this gull dataset.
- The cluster labels represent validated migration strategies.
- SRVF-DTW is better than raw DTW.
- The method is a complete continuous-time movement model.
