# Source Code Plan

This folder will contain the analysis code for the paper.

## Planned Scripts

1. `load_data.py`
   - Load raw GPS tracking data.
   - Standardize column names.
   - Save cleaned trajectory tables.

2. `preprocess.py`
   - Remove invalid observations.
   - Split tracks by individual and season.
   - Resample trajectories to a common number of points.

3. `geometry.py`
   - Convert latitude-longitude coordinates to unit-sphere coordinates.
   - Compute great-circle distances.

4. `split_segments_by_season.py`
   - Split candidate migration segment tables by season.
   - Produces spring/autumn analysis inputs.

5. `srvf.py`
   - Compute discrete SRVF representations.
   - Compute SRVF distances.

6. `cluster.py`
   - Compute pairwise distance matrices.
   - Run clustering.
   - Compute anomaly scores.

7. `plot_tracks.py`
   - Plot raw tracks, clustered tracks, and abnormal trajectories.

8. `missing_data_stability.py`
   - Remove random observations or contiguous observation blocks.
   - Recompute raw-DTW and SRVF-DTW distance matrices.
   - Measure distance-matrix, clustering, and anomaly-ranking stability.

9. `plot_missing_data_stability.py`
   - Plot the missing-observation stability diagnostics.

10. `gap_reconstruction_baseline.py`
   - Compare observed-only resampling with a spherical bridge reconstruction
     for contiguous observation gaps.

11. `plot_gap_reconstruction_baseline.py`
   - Plot the simple contiguous-gap reconstruction baseline diagnostics.

12. `gp_gap_reconstruction.py`
   - Draw simple independent-coordinate Gaussian-process route samples for a
     contiguous observation gap.
   - Propagate posterior route samples through distance, clustering, and
     anomaly diagnostics.

13. `plot_gp_gap_reconstruction.py`
   - Plot uncertainty intervals from the GP gap-reconstruction prototype.

14. `brownian_bridge_gap_reconstruction.py`
   - Draw tangent-plane Brownian bridge route samples for a contiguous
     observation gap.
   - Estimate bridge scale from local great-circle residuals in observed
     trajectory segments.
   - Propagate movement-aware bridge samples through route-comparison
     diagnostics.

15. `plot_brownian_bridge_gap_reconstruction.py`
   - Plot uncertainty intervals from the Brownian bridge prototype.

16. `plot_brownian_bridge_batch.py`
   - Plot season-aware Brownian bridge diagnostics across multiple contiguous
     gap fractions.

17. `plot_uncertainty_framework_figure.py`
   - Create the main workflow schematic showing a contiguous tracking gap,
     deterministic spherical bridge, Brownian bridge route samples, and
     downstream uncertainty propagation.

18. `withheld_gap_validation.py`
   - Withhold observed route segments and compare deterministic and Brownian
     bridge reconstructions against the hidden observations.
   - Report great-circle reconstruction error and empirical Brownian sample
     envelope coverage.
   - Estimate the radius-inflation factor needed to approach nominal 90%
     pointwise coverage.

19. `brownian_bridge_scale_sensitivity.py`
   - Re-run the Brownian bridge downstream diagnostics under multiple
     perturbation-scale multipliers.
   - Checks whether conclusions change smoothly when the estimated bridge scale
     is inflated or deflated.

20. `segmentation_sensitivity.py`
   - Re-run transit trimming under moderate threshold changes.
   - Summarize route and point counts by season to document the stability of the
     candidate-route sample.

## First Prototype

Start with a small subset:

1. 3 to 10 birds.
2. One migration season.
3. 100 resampled points per trajectory.
4. Baseline distance matrix vs SRVF distance matrix.
