# Main Tables

## Table 1. Route Counts

Route counts after broad seasonal filtering and transit-focused trimming.

| Season | Broad routes | Transit routes | Individuals | Transit points | Batch routes |
|---|---:|---:|---:|---:|---:|
| Spring | 204 | 200 | 84 | 74,567 | 30 |
| Autumn | 182 | 181 | 81 | 299,774 | 30 |
| Total | 386 | 381 | -- | 374,341 | 60 |

Notes:

- Broad routes come from `data/processed/lbbg_zeebrugge_candidate_segments_summary.csv`.
- Transit routes come from `data/processed/lbbg_zeebrugge_transit_segments_summary.csv`.
- Batch routes are the balanced spring/autumn subset used in the season-aware Brownian bridge experiment.

## Table 2. Brownian Bridge Diagnostics at 60% Contiguous Gaps

Means across sampled Brownian bridge reconstructions.

| Season | Metric | Scale | Matrix corr. | Rel. error | ARI | Anomaly corr. | Top-k overlap |
|---|---|---:|---:|---:|---:|---:|---:|
| Spring | Raw DTW | 0.001088 | 0.929 | 0.128 | 0.791 | 0.831 | 0.933 |
| Spring | SRVF-DTW | 0.001088 | 0.836 | 0.119 | 0.626 | 0.887 | 0.744 |
| Autumn | Raw DTW | 0.000352 | 0.958 | 0.115 | 0.878 | 0.931 | 0.733 |
| Autumn | SRVF-DTW | 0.000352 | 0.707 | 0.096 | 0.493 | 0.679 | 0.622 |

Source:

- `data/processed/brownian_bridge_gap_reconstruction_summary.csv`
- Rows: `method = brownian_bridge_sample`, `missing_fraction = 0.6`

## Table 3. Withheld-Segment Validation

Lightweight validation using 12 spring and 12 autumn transit routes, two gap
placements per withheld fraction, and 12 Brownian bridge samples per gap.

| Season | Withheld | Det. error km | BB center error km | Coverage | Inflation | Cal. coverage |
|---|---:|---:|---:|---:|---:|---:|
| Spring | 20% | 74.1 | 75.6 | 0.46 | 3.8 | 0.89 |
| Spring | 40% | 139.5 | 142.0 | 0.25 | 4.4 | 0.89 |
| Spring | 60% | 171.2 | 172.8 | 0.31 | 5.3 | 0.90 |
| Autumn | 20% | 59.8 | 61.8 | 0.69 | 7.0 | 0.90 |
| Autumn | 40% | 90.2 | 92.7 | 0.60 | 6.5 | 0.90 |
| Autumn | 60% | 140.8 | 143.8 | 0.51 | 8.0 | 0.90 |

Source:

- `data/processed/withheld_gap_validation_summary.csv`

## Scale Sensitivity Notes

Lightweight sensitivity check at 60% contiguous gaps using 8 spring and 8 autumn
routes, one gap placement, four Brownian bridge samples, and scale multipliers
0.5, 1.0, and 2.0.

Key Brownian sample matrix correlations:

| Season | Metric | 0.5x scale | 1.0x scale | 2.0x scale |
|---|---|---:|---:|---:|
| Spring | Raw DTW | 0.850 | 0.852 | 0.616 |
| Spring | SRVF-DTW | 0.748 | 0.729 | 0.584 |
| Autumn | Raw DTW | 0.954 | 0.930 | 0.764 |
| Autumn | SRVF-DTW | 0.744 | 0.574 | 0.070 |

Source:

- `data/processed/brownian_bridge_scale_sensitivity_summary.csv`

## Segmentation Sensitivity Notes

Transit-route counts under moderate trimming-threshold changes.

| Scenario | Spring routes | Autumn routes | Total routes | Total points |
|---|---:|---:|---:|---:|
| Baseline | 200 | 181 | 381 | 374,341 |
| 75 km departure/return | 200 | 182 | 382 | 408,245 |
| 150 km departure/return | 200 | 179 | 379 | 272,794 |
| 0.85 max-distance fraction | 199 | 178 | 377 | 351,663 |
| 0.95 max-distance fraction | 201 | 182 | 383 | 413,853 |

Source:

- `data/processed/segmentation_sensitivity_summary.csv`
