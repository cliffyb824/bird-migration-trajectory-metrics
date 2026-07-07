# Results Interpretation Notes

## Current Prototype Result

The first 50-segment prototype does not yet show SRVF outperforming pointwise L2 on simple internal clustering metrics.

This is not a failure. It is a useful diagnostic.

## What the Metrics Say

For 50 candidate route segments and 4 clusters:

| Metric | Silhouette score | Davies-Bouldin index |
|---|---:|---:|
| pointwise_l2 | 0.46594864545064335 | 0.40473428828463726 |
| srvf | 0.11979850096450981 | 1.0700769294736714 |

Higher silhouette is better. Lower Davies-Bouldin is better.

So, in this crude setup, pointwise L2 looks cleaner.

## Why This May Be Happening

1. **Segmentation is too broad.**  
   Current segments are calendar windows, not carefully detected migration phases.

2. **Spring and autumn are directionally different.**  
   Pointwise L2 can easily separate northbound vs southbound trajectories if they are aligned by calendar windows.

3. **SRVF alignment is incomplete.**  
   The current implementation computes SRVF distance after resampling, but it does not solve the full elastic matching / optimal reparameterization problem.

4. **The sample is not balanced.**  
   The first 50 segments are not necessarily representative.

5. **Internal clustering metrics may not measure ecological usefulness.**  
   A distance metric can be useful for route-shape interpretation even if its first silhouette score is lower.

## What We Should Not Claim Yet

Do not claim:

- SRVF is better than all baselines.
- SRVF improves clustering accuracy.
- SRVF reveals biologically meaningful groups.
- SRVF is robust to reparameterization in this implementation.

## What We Can Claim Safely

At this stage, we can claim only:

- The data pipeline works.
- SRVF distances can be computed for real bird migration route segments.
- Preliminary visual and quantitative diagnostics are available.
- Further work is needed on segmentation and elastic alignment.

## Next Scientific Fixes

1. Separate spring and autumn experiments.
2. Improve migration phase segmentation.
3. Add true SRVF elastic alignment or a dynamic-programming approximation.
4. Use balanced samples across seasons and individuals.
5. Evaluate parameterization robustness using artificial time warping.
6. Compare interpretability of cluster medoids, not only internal metrics.

## Updated Interpretation After SRVF-DTW

SRVF-DTW solves a different problem than clustering quality.

In the controlled time-warp experiment, SRVF-DTW is clearly robust to artificial changes in trajectory speed. This supports a methodological claim about parameterization robustness.

However, the season-specific clustering metrics still do not show SRVF-DTW outperforming pointwise L2. This means the paper should not be framed as "SRVF gives better clusters" yet.

Better framing:

> We introduce a sphere-aware SRVF framework for migration route comparison and show that its aligned version is robust to temporal reparameterization. We then use the method for exploratory route-shape clustering and anomaly detection.

This is more defensible than claiming global clustering superiority.
