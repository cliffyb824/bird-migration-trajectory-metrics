# Bird Migration Trajectory Metric Comparison

This repository contains code and manuscript materials for a study comparing coordinate-based and SRVF-based trajectory metrics on bird migration GPS data.

## Project Summary

The study analyzes open GPS tracking data for lesser black-backed gulls from the `LBBG_ZEEBRUGGE` dataset. Candidate migration route segments are embedded on the unit sphere and compared using:

1. pointwise coordinate distance;
2. raw-coordinate dynamic time warping;
3. direct square root velocity function distance;
4. DTW-aligned square root velocity function distance.

The main finding is that raw-coordinate DTW is strongest for pure temporal
alignment and strongly separates the tested spatial perturbations relative to
its own time-warp baseline. SRVF-DTW provides an alternative velocity-shape
representation with a distinct response profile.

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

## Reproduce Core Outputs

After downloading and extracting the raw data archive, run:

```powershell
python src\run_core_pipeline.py
```

For detailed steps, see:

`reproducibility.md`

## Main Scripts

- `src/download_lbbg.py`: download and extract the public Darwin Core Archive.
- `src/download_naturalearth.py`: download the Natural Earth coastline used by the map figure.
- `src/standardize_dwca.py`: convert Darwin Core occurrence records into a compact trajectory table.
- `src/segment_migration.py`: create broad candidate migration segments.
- `src/trim_transit_segments.py`: trim broad segments to transit-focused route portions.
- `src/prototype_distances.py`: compute trajectory distance matrices.
- `src/timewarp_robustness_batch.py`: run batch time-warp diagnostics.
- `src/shape_perturbation_batch.py`: run batch shape-perturbation diagnostics.
- `src/shape_perturbation_sweep.py`: run season-aware perturbation sweeps.
- `src/plot_shape_perturbation_sweep.py`: plot normalized sweep responses.
- `src/anomaly_scores.py`: compute exploratory route anomaly scores.

## Main Figures

- `figures/timewarp_robustness_transit_batch.png`
- `figures/shape_perturbation_sweep_relative.png`
- `figures/route_map_transit_coastline.png`
- `figures/top_anomaly_transit_coastline.png`

## License

Code is released under the MIT License. See `LICENSE`.

## Citation

If using the data, cite the original `LBBG_ZEEBRUGGE` dataset:

Stienen, E. W., Desmet, P., Milotic, T., Hernandez, F., Deneudt, K., Bouten, W., Muller, W., Matheve, H., & Lens, L. (2025). *LBBG_ZEEBRUGGE - Lesser black-backed gulls (Larus fuscus, Laridae) breeding at the southern North Sea coast (Belgium and the Netherlands).* Version 1.3. Research Institute for Nature and Forest (INBO). Occurrence dataset. https://ipt.inbo.be/resource?r=lbbg_zeebrugge&v=1.3
