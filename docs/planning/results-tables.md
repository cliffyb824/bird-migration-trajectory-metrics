# Results Tables

## Table 1. Transit-Segment Batch Time-Warp Robustness

Mean distance to the original trajectory under artificial temporal reparameterization across 20 transit-focused candidate spring migration trajectories. Lower values indicate greater invariance to time warping.

| Gamma | Pointwise L2 | Raw DTW | Direct SRVF | SRVF-DTW |
|---:|---:|---:|---:|---:|
| 0.4 | 0.5402 | 0.0015 | 0.6852 | 0.0147 |
| 0.6 | 0.3540 | 0.0007 | 0.6878 | 0.0106 |
| 0.8 | 0.1933 | 0.0005 | 0.6477 | 0.0068 |
| 1.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 1.25 | 0.1961 | 0.0005 | 0.6533 | 0.0071 |
| 1.5 | 0.3081 | 0.0006 | 0.6829 | 0.0100 |
| 2.0 | 0.4603 | 0.0008 | 0.7024 | 0.0130 |
| 2.5 | 0.5671 | 0.0009 | 0.7087 | 0.0152 |

**Interpretation:** Raw-coordinate DTW is the most invariant metric under pure time warping. SRVF-DTW is also much more robust than pointwise L2 and direct SRVF, but it does not outperform raw DTW for this specific task.

## Supplementary Table S1. Transit-Segment Batch Shape-Perturbation Response

Mean distance to the original trajectory under controlled perturbations across 20 transit-focused candidate spring migration trajectories.

| Perturbation | Pointwise L2 | Raw DTW | Direct SRVF | SRVF-DTW |
|---|---:|---:|---:|---:|
| time warp, gamma 0.4 | 0.5402 | 0.0015 | 0.6852 | 0.0147 |
| time warp, gamma 2.5 | 0.5671 | 0.0009 | 0.7087 | 0.0152 |
| smoothed | 0.0690 | 0.0017 | 0.4480 | 0.0174 |
| local detour | 0.4232 | 0.0152 | 0.3474 | 0.0144 |
| local loop | 0.2751 | 0.0087 | 0.9756 | 0.0337 |
| reversed | 1.0857 | 0.0399 | 0.9005 | 0.0304 |

**Interpretation:** Raw DTW remains very small under pure time warping and
several local perturbations. Because the metrics have different absolute
scales, cross-metric sensitivity should be interpreted using the normalized
season-aware sweep in Table 2.

## Supplementary Table S2. Exploratory Season-Specific Clustering

Internal clustering metrics for season-specific candidate migration segments. Four agglomerative clusters were used.

| Season | Metric | Silhouette | Davies-Bouldin | Cluster sizes |
|---|---|---:|---:|---|
| spring | pointwise L2 | 0.3485 | 0.5904 | 1:26; 2:70; 3:1; 4:3 |
| spring | direct SRVF | 0.1268 | 0.6525 | 1:95; 2:3; 3:1; 4:1 |
| autumn | pointwise L2 | 0.5375 | 0.5043 | 1:96; 2:2; 3:1; 4:1 |
| autumn | direct SRVF | 0.1356 | 0.4948 | 1:97; 2:1; 3:1; 4:1 |

**Interpretation:** These exploratory clustering results do not support a claim that SRVF improves route clustering. Clustering should remain secondary in the manuscript.

## Table 2. Season-Aware Normalized Perturbation Sweep

Median metric-specific response relative to each trajectory's mean response to
strong time-warp controls (`gamma=0.4` and `gamma=2.5`). Values above 1 indicate
that the perturbation produces a larger response than the metric's own
time-warp baseline.

| Season | Perturbation | Highest intensity | Raw DTW | SRVF-DTW |
|---|---|---:|---:|---:|
| spring | smoothing window | 21 | 2.4742 | 1.2738 |
| spring | local detour amplitude | 0.08 | 10.6784 | 0.8754 |
| spring | local loop amplitude | 0.08 | 8.3220 | 2.4785 |
| autumn | smoothing window | 21 | 3.2780 | 1.1870 |
| autumn | local detour amplitude | 0.08 | 11.4119 | 0.7592 |
| autumn | local loop amplitude | 0.08 | 9.2341 | 2.0123 |

**Interpretation:** Raw-coordinate DTW strongly separates the tested spatial
perturbations from pure time warping. SRVF-DTW has a distinct response profile:
it rises consistently with smoothing and loop intensity, but the present
experiment does not support a claim of generally stronger sensitivity.
