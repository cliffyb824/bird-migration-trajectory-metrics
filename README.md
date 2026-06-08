# Validation and Calibration Diagnostics for Bird Migration Route Comparison

This repository contains code, figures, and LaTeX manuscript materials for a
methods paper on validated and calibrated uncertainty diagnostics for comparing
migratory routes from incomplete animal tracking data.

## Project Summary

The study uses open GPS tracking data for Lesser Black-backed Gulls from the
`LBBG_ZEEBRUGGE` dataset. Transit-focused migration routes are embedded on the
unit sphere and compared with raw-coordinate DTW and SRVF-DTW distances.

The current manuscript focuses on missing-data uncertainty:

1. random point loss versus contiguous tracking gaps;
2. sensitivity of route counts to transit-segmentation thresholds;
3. deterministic spherical bridge reconstruction;
4. estimated-scale Brownian bridge route samples;
5. withheld-segment validation of reconstruction error and sample coverage;
6. empirical radius calibration of Brownian bridge uncertainty envelopes;
7. Brownian bridge scale sensitivity under severe contiguous gaps;
8. propagation of reconstruction uncertainty into distance matrices, clustering,
   anomaly ranking, and top-ranked anomaly overlap.

The central diagnostic sequence is to validate missing-route envelopes against
withheld observations, calibrate coverage with empirical radius inflation, and
propagate reconstruction uncertainty into downstream route-comparison outputs.

## Data

Raw data are not redistributed in this repository.

Download the public source dataset from INBO:

<https://ipt.inbo.be/resource?r=lbbg_zeebrugge>

Direct Darwin Core Archive:

<https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3>

## Installation

```powershell
pip install -r requirements.txt
```

## Current Manuscript

The current LaTeX manuscript is in `submission/latex/`.

Build it with:

```powershell
powershell -ExecutionPolicy Bypass -File submission\latex\build.ps1
```

Expected output:

- `submission/latex/main.pdf`

## Main Scripts

- `src/download_lbbg.py`: download and extract the public Darwin Core Archive.
- `src/standardize_dwca.py`: standardize Darwin Core occurrence records.
- `src/segment_migration.py`: create broad candidate migration segments.
- `src/trim_transit_segments.py`: trim segments to transit-focused routes.
- `src/segmentation_sensitivity.py`: summarize route-count sensitivity to trimming thresholds.
- `src/missing_data_stability.py`: compare random missingness and contiguous gaps.
- `src/gap_reconstruction_baseline.py`: evaluate deterministic spherical bridge reconstruction.
- `src/brownian_bridge_gap_reconstruction.py`: sample Brownian bridge missing-route reconstructions.
- `src/withheld_gap_validation.py`: validate reconstructed gaps and calibrate Brownian envelope coverage.
- `src/brownian_bridge_scale_sensitivity.py`: test downstream sensitivity to Brownian bridge scale multipliers.
- `src/plot_uncertainty_framework_figure.py`: generate the workflow figure.
- `src/plot_missing_data_stability.py`: plot missingness mechanism diagnostics.
- `src/plot_brownian_bridge_batch.py`: plot season-aware Brownian bridge diagnostics.

## Main Figures

- `figures/uncertainty_framework_figure.png`
- `figures/missing_data_stability.png`
- `figures/brownian_bridge_gap_reconstruction_batch.png`

## License

Code is released under the MIT License. See `LICENSE`.

## Citation

If using the data, cite the original `LBBG_ZEEBRUGGE` dataset:

Stienen, E. W., Desmet, P., Milotic, T., Hernandez, F., Deneudt, K., Bouten,
W., Muller, W., Matheve, H., & Lens, L. (2025). *LBBG_ZEEBRUGGE - Lesser
black-backed gulls (Larus fuscus, Laridae) breeding at the southern North Sea
coast (Belgium and the Netherlands).* Version 1.3. Research Institute for
Nature and Forest (INBO). Occurrence dataset.
<https://ipt.inbo.be/resource?r=lbbg_zeebrugge&v=1.3>
