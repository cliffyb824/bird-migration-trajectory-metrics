# Project Status

Last updated: 2026-04-26

## Current Paper Direction

The project is now framed as:

**A methodological route-representation paper comparing coordinate-based and SRVF-based aligned distances on bird migration trajectories.**

Current supported claim:

> Coordinate DTW is strongest for pure temporal alignment and strongly
> separates the tested spatial perturbations relative to its own time-warp
> baseline. SRVF-DTW provides an alternative velocity-shape representation
> with a distinct response profile.

## Dataset

Primary dataset:

`LBBG_ZEEBRUGGE`, lesser black-backed gull GPS tracking data from INBO.

Local standardized file:

`data/processed/lbbg_zeebrugge_standardized.csv`

Current standardized GPS rows:

1,801,052

## Current Data Products

Candidate migration segments:

`data/processed/lbbg_zeebrugge_candidate_segments.csv`

Segment summary:

`data/processed/lbbg_zeebrugge_candidate_segments_summary.csv`

Candidate segments:

386

Segment points:

1,151,566

Preferred refined segments:

`data/processed/lbbg_zeebrugge_transit_segments.csv`

Transit-focused segments:

381

Transit-focused points:

374,341

## Main Evidence

### 1. Batch Time-Warp Robustness

Files:

- `data/processed/timewarp_robustness_transit_batch.csv`
- `data/processed/timewarp_robustness_transit_batch_summary.csv`
- `figures/timewarp_robustness_transit_batch.png`

Interpretation:

- Pointwise L2 is sensitive to time warping.
- Raw DTW is extremely robust to time warping.
- SRVF-DTW is also robust, but does not beat raw DTW for pure time alignment.

### 2. Batch Shape Perturbation

Files:

- `data/processed/shape_perturbation_transit_batch.csv`
- `data/processed/shape_perturbation_transit_batch_summary.csv`
- `figures/shape_perturbation_transit_batch.png`

Interpretation:

- Raw DTW remains very small for several perturbations.
- Absolute distances differ across metrics and should not be directly ranked.
- The normalized season-aware sweep shows distinct perturbation-response profiles.

### 3. Season-Aware Perturbation Intensity Sweep

Files:

- `data/processed/shape_perturbation_sweep_spring_summary.csv`
- `data/processed/shape_perturbation_sweep_autumn_summary.csv`
- `figures/shape_perturbation_sweep_relative.png`

Interpretation:

- Covers all transit-focused routes with at least 80 points: 175 spring and 172 autumn trajectories.
- Normalizes each metric by its trajectory-specific mean response to strong time-warp controls.
- Raw DTW strongly separates the tested spatial perturbations.
- SRVF-DTW increases with smoothing and local-loop intensity, but the results do not support a general sensitivity-superiority claim.

### 4. Exploratory Anomaly Scoring

Files:

- `data/processed/prototype_50_transit_distances/srvf_dtw_anomaly_scores.csv`
- `figures/top_anomaly_transit_coastline.png`

Interpretation:

- Ranks transit candidate routes by mean SRVF-DTW distance to other routes.
- Exploratory only; not a biological abnormality claim.

### 5. Coastline-Aware Route Overview

Files:

- `data/external/naturalearth/ne_110m_coastline/ne_110m_coastline.shp`
- `figures/route_map_transit_coastline.png`

Interpretation:

- Provides geographic context for the spring transit route sample.
- Uses Natural Earth 1:110m coastline data through a lightweight shapefile reader, avoiding a hard dependency on GIS packages.

## Manuscript Files

- `manuscript/draft.md`
- `manuscript/current-claim.md`
- `manuscript/results-tables.md`
- `manuscript/figure-captions.md`
- `manuscript/writing-status.md`

## Code Health

All Python scripts in `src/` passed syntax checks on 2026-04-26.

Dependency file:

`requirements.txt`

Core pipeline runner:

`src/run_core_pipeline.py`

The core runner now regenerates the transit-focused workflow by default.

## Known Weaknesses

1. Migration segmentation is heuristic and calendar-window based.
2. Spherical resampling uses chord-length interpolation.
3. SRVF-DTW is a practical approximation, not full elastic SRVF registration.
4. Clustering results are weak and should remain exploratory.
5. Raw DTW is a very strong baseline, so claims must be carefully framed.

## Best Next Steps

1. Improve candidate migration segmentation.
2. Add final Methods text describing all four metrics:
   - pointwise L2;
   - raw DTW;
   - direct SRVF;
   - SRVF-DTW.
3. Decide target journal category: ecological informatics, movement ecology, or geospatial data analysis.

## Completed Since Last Status

- Added `src/split_segments_by_season.py`.
- Replaced one-off season splitting with a reproducible script.
- Added `src/plot_route_map.py`.
- Generated `figures/route_map_fallback.png`.
- Added raw-coordinate DTW baseline to metric pipeline.
- Added batch shape-perturbation experiment.
- Added exploratory anomaly scoring and route plot.
- Added `requirements.txt`.
- Added `src/run_core_pipeline.py`.
- Added `src/trim_transit_segments.py`.
- Generated transit-focused candidate segments.
- Re-ran main time-warp and shape-perturbation diagnostics on transit-focused spring segments.
- Added `src/download_naturalearth.py`.
- Updated `src/plot_route_map.py` to draw Natural Earth coastlines without GIS dependencies.
- Generated `figures/route_map_transit_coastline.png`.
- Updated `src/plot_anomaly_routes.py` to draw the same coastline layer.
- Generated `figures/top_anomaly_transit_coastline.png`.
