# Validated Uncertainty Diagnostics Manuscript Outline

## Working Title

Validation and Calibration Diagnostics for Migratory-Route Comparison from
Incomplete Animal Tracking Data

## Target Journal

Primary target: Ecological Informatics.

The manuscript should be positioned as an ecological-informatics methods paper,
not as a new ecological finding about Lesser Black-backed Gull migration.

## Central Claim

Migratory-route comparison is sensitive not only to the choice of trajectory
metric, but also to how prolonged tracking gaps are reconstructed. A useful
route-comparison diagnostic should therefore validate and calibrate plausible
missing-route uncertainty where possible, then propagate that uncertainty into
downstream distance matrices, route clustering, and anomaly ranking rather than
reporting only one deterministic distance matrix.

## Core Contributions

1. Demonstrate that random missing observations and contiguous tracking gaps
   have different effects on route-comparison stability.
2. Show that deterministic spherical bridge interpolation does not fully solve
   the instability caused by prolonged gaps.
3. Provide a movement-aware Brownian bridge baseline that generates plausible
   route samples inside missing intervals.
4. Validate sampled uncertainty envelopes against withheld observed route
   segments.
5. Calibrate Brownian bridge uncertainty envelopes with empirical radius
   inflation toward nominal pointwise coverage.
6. Estimate Brownian bridge perturbation scales from observed local route
   residuals, with season-specific scales for spring and autumn routes.
7. Propagate route-reconstruction uncertainty into downstream diagnostics:
   distance-matrix rank correlation, relative distance error, clustering
   agreement, anomaly-rank correlation, and top-ranked anomaly overlap.

## Abstract Skeleton

Animal tracking datasets often contain irregular sampling and prolonged
observation gaps, yet migration routes are commonly compared after deterministic
preprocessing. This study evaluates how missing-route reconstruction affects
trajectory-distance analyses of bird migration routes. Transit-focused routes
from open GPS tracking data for Lesser Black-backed Gulls are embedded on the
unit sphere and compared using raw-coordinate DTW and SRVF-DTW. Controlled
missingness experiments contrast random point loss with contiguous tracking
gaps. Deterministic spherical bridge interpolation is compared with an
estimated-scale Brownian bridge reconstruction that samples plausible paths
inside missing intervals. Route-reconstruction uncertainty is propagated to
distance matrices, route clustering, and anomaly ranking. Results show that
random point loss has limited effect after resampling, whereas contiguous gaps
can substantially alter clustering and anomaly diagnostics. Brownian bridge
scales differ between spring and autumn routes, and downstream stability depends
on both metric and season. These findings support uncertainty-aware route
comparison as a practical diagnostic framework for ecological movement-data
analysis.

## Paper Structure

### 1. Introduction

Purpose:
Explain why incomplete tracking data create a methodological problem for
migration-route comparison.

Key points:

- GPS animal tracking data are often irregular, sparse, or interrupted.
- Many route-comparison workflows convert observations into one deterministic
  curve before computing distances.
- This hides uncertainty introduced by prolonged tracking gaps.
- Route comparison is used for downstream tasks such as clustering, route
  fidelity analysis, and anomaly screening.
- The paper asks: when are those downstream conclusions stable under plausible
  reconstructions of missing route segments?

Avoid:

- Do not claim a new ecological result about gull migration.
- Do not claim Brownian bridge is the final or universally best movement model.
- Do not center the paper on SRVF novelty.

### 2. Data and Route Construction

Reuse from old manuscript:

- Open `LBBG_ZEEBRUGGE` GPS tracking data.
- Transit-focused spring and autumn candidate routes.
- Latitude-longitude to unit-sphere embedding.
- Fixed-length curve resampling.

Revise emphasis:

- Present segmentation as a reproducible route-extraction procedure, not as
  exact behavioral-state classification.
- Mention that raw data are not redistributed; code points to public dataset.

### 3. Route Metrics

Use as baselines:

- Raw-coordinate DTW.
- SRVF-DTW.

Move to supplement or shorten:

- Direct pointwise L2.
- Direct SRVF.
- Old clustering/anomaly exploratory figures.

Message:

These metrics represent two different route-comparison views. They are not the
paper's novelty; they are downstream diagnostics used to test how reconstruction
uncertainty propagates.

### 4. Missingness Experiments

Experiments:

1. Random point loss: 20%, 40%, 60%.
2. Contiguous tracking gap: 20%, 40%, 60%.

Stability diagnostics:

- Spearman correlation of distance-matrix upper triangles.
- Median relative distance error.
- Adjusted Rand index for cluster labels.
- Spearman correlation of anomaly scores/ranks.
- Top-k anomaly overlap as a secondary diagnostic.

Expected main result:

Random point loss is mostly absorbed by resampling, whereas contiguous gaps
produce larger instability, especially for clustering.

### 5. Reconstruction Models

Models:

1. Deterministic spherical bridge.
2. Independent-coordinate GP prototype.
3. Estimated-scale Brownian bridge.

Recommended manuscript role:

- Spherical bridge: main deterministic baseline.
- Brownian bridge: main uncertainty-aware baseline.
- Independent GP: supplement or short negative-control subsection, because it
  demonstrates uncertainty propagation but can produce implausible routes.

Brownian bridge details:

- Bridge is constructed between gap endpoints on the unit sphere.
- Perturbations are sampled in local tangent planes.
- Samples are projected back to the unit sphere.
- Perturbation scale is estimated from observed local great-circle residuals.
- Scale is estimated separately by season.

### 6. Results

#### Result 1: Missingness Mechanism Matters

Use:

- `figures/missing_data_stability.png`

Claim:

Random missing points are less damaging than contiguous gaps. This establishes
the need to study realistic tracking interruptions, not only random thinning.

#### Result 2: Simple Interpolation Is Not Enough

Use:

- `figures/gap_reconstruction_baseline.png`

Claim:

Spherical bridge interpolation and observed-only resampling are nearly
indistinguishable for contiguous gaps. Deterministic bridge reconstruction does
not recover the complete-data route-comparison structure.

#### Result 3: Naive GP Exposes but Does Not Solve Uncertainty

Use:

- `figures/gp_gap_reconstruction_samples.png`
- `figures/gp_gap_reconstruction_summary.png`

Likely placement:

Supplement, unless the main text needs a short negative-control example.

Claim:

Independent-coordinate GP samples can be too unconstrained and may wander away
from plausible migration corridors. This motivates movement-aware
reconstruction.

#### Result 4: Estimated Brownian Bridge Gives a Movement-Aware Baseline

Use:

- `figures/brownian_bridge_gap_reconstruction_samples.png`
- `figures/brownian_bridge_gap_reconstruction_summary.png`

Claim:

Estimated-scale Brownian bridge samples remain localized to missing intervals
and expose downstream uncertainty without producing the extreme GP behavior.

#### Result 5: Season-Aware Batch Experiment

Use as likely main figure:

- `figures/brownian_bridge_gap_reconstruction_batch.png`

Key values:

- Spring estimated bridge scale: 0.00108755.
- Autumn estimated bridge scale: 0.000352488.

Claims:

- Route-reconstruction uncertainty differs by season.
- Raw-DTW distance matrices remain relatively stable.
- SRVF-DTW distance stability declines more strongly in some conditions.
- Cluster agreement is the least stable downstream conclusion.
- Anomaly ranks can remain stable even when cluster labels are unstable.

### 7. Discussion

Main arguments:

- A single deterministic distance matrix can understate uncertainty from
  tracking gaps.
- Stability depends on the downstream task, not only on the route metric.
- Clustering is especially sensitive and should not be overinterpreted without
  uncertainty diagnostics.
- Brownian bridge reconstruction is a practical first baseline, but not a full
  movement model.
- Future work should use richer continuous-time movement models and multiple
  datasets.

Limitations:

- One species and one tracking dataset.
- Route segmentation remains heuristic.
- Brownian bridge variance is estimated simply from local residuals.
- No external ecological label validates clusters or anomaly scores.
- Current bridge does not condition on wind, habitat, stopover behavior, or
  individual movement state.

## Proposed Figures and Tables

### Main Figures

Figure 1:
Route map and gap illustration.

Source:

- `figures/uncertainty_framework_figure.png`

Message:

This is the visual entry point for the new paper. It shows observed route
points, a removed contiguous gap, deterministic spherical bridge reconstruction,
Brownian bridge route samples, and propagation to downstream route-comparison
diagnostics.

Figure 2:
Missingness mechanism stability.

Source:

- `figures/missing_data_stability.png`

Figure 3:
Season-aware Brownian bridge batch experiment.

Source:

- `figures/brownian_bridge_gap_reconstruction_batch.png`

Figure 4:
Brownian bridge route samples.

Source:

- `figures/brownian_bridge_gap_reconstruction_samples.png`

Possible supplement:

- `figures/gap_reconstruction_baseline.png`
- `figures/gp_gap_reconstruction_samples.png`
- `figures/gp_gap_reconstruction_summary.png`

### Main Tables

Table 1:
Dataset and route counts by season after filtering.

Table 2:
Estimated Brownian bridge scales by season.

Table 3:
Summary of stability diagnostics at 60% contiguous gaps.

## What to Keep from the Old Manuscript

Keep:

- Data description.
- Route extraction workflow.
- Unit-sphere embedding.
- Raw-DTW and SRVF-DTW metric definitions.
- Code/data availability sections.
- Reproducibility framing.

Shorten:

- General SRVF motivation.
- Old perturbation experiments.
- Old route clustering discussion.

Move to supplement:

- Direct pointwise L2 and direct SRVF results.
- Shape perturbation sweep.
- Old prototype clustering heatmaps.
- Old anomaly route examples.

Remove as main claims:

- Any suggestion that SRVF-DTW is superior.
- Any route-clustering ecological interpretation.
- Any anomaly result framed as biological abnormality.

## Remaining Work Before Drafting Full Paper

High priority:

1. Create route-map plus gap-reconstruction schematic for the new Figure 1.
2. Export clean tables for route counts and bridge-scale estimates.
3. Run at least one sensitivity check for Brownian bridge scale estimation.
4. Decide whether GP prototype belongs in main text or supplement.
5. Rewrite the abstract and introduction around missing-data uncertainty.

Medium priority:

1. Add autumn/spring route count table after transit filtering.
2. Add computational reproducibility script for the new experiment sequence.
3. Add captions for all new figures.
4. Check whether all generated figures use consistent colors and terminology.

Potential future expansion:

1. Add another public animal tracking dataset.
2. Add a continuous-time state-space model.
3. Calibrate Brownian bridge variance against known withheld route segments.
4. Test sensitivity to gap location, not only gap fraction.

## Drafting Decision

This project should now proceed as a new paper. The old DTW/SRVF manuscript is
best treated as a baseline source and technical supplement, not as the primary
submission manuscript.
