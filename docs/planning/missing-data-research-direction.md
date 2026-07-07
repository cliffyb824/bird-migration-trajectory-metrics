# Missing-Data Research Direction

## Proposed Research Question

How reliably can migratory routes be compared when animal tracking data contain
irregular sampling, missing observations, and prolonged observation gaps?

The intended methodological contribution is not another deterministic
trajectory distance. It is an uncertainty-aware framework that propagates
observation and reconstruction uncertainty into route similarity, clustering,
and anomaly screening.

## Initial Feasibility Experiment

The first experiment used 30 transit-focused spring migration trajectories.
Each route was resampled to 60 points after removing 20%, 40%, or 60% of its
observations. Two missingness mechanisms were evaluated:

- random missing points;
- one contiguous missing observation gap.

Each condition was repeated five times. Raw-coordinate DTW and SRVF-DTW were
compared with their complete-data baselines using:

- Spearman correlation of the upper-triangle distance matrix;
- median relative distance error;
- adjusted Rand index for four-cluster assignments;
- Spearman correlation of anomaly rankings;
- top-five anomaly overlap.

## Main Finding

Random point loss had little effect after curve resampling. At 60% random
missingness, raw-DTW distance-matrix correlation remained 0.999 and SRVF-DTW
correlation remained 0.983.

Contiguous gaps caused materially larger instability. At 60% contiguous
missingness:

| Metric | Matrix correlation | Median relative error | Cluster ARI | Anomaly-rank correlation |
|---|---:|---:|---:|---:|
| Raw DTW | 0.953 | 0.121 | 0.569 | 0.869 |
| SRVF-DTW | 0.884 | 0.211 | 0.474 | 0.906 |

This result supports a new research direction: deterministic route comparison
can appear stable under random thinning while remaining unreliable under
realistic prolonged tracking gaps. The effect is especially important for
downstream cluster assignments.

## Next Methodological Step

Replace direct interpolation across missing intervals with a continuous-time
latent trajectory model. Generate posterior route samples and propagate them
through the trajectory-comparison workflow. Report distance distributions,
cluster-membership uncertainty, and anomaly-rank uncertainty rather than only
single deterministic outputs.

## Simple Reconstruction Baseline

A second feasibility experiment compared two deterministic treatments of one
contiguous tracking gap:

- observed-only resampling after deleting the gap;
- spherical bridge reconstruction using great-circle interpolation between
  the observations before and after the gap.

The two approaches were nearly indistinguishable. At 60% contiguous missingness,
the raw-DTW distance-matrix correlation was 0.944 for both methods. For SRVF-DTW,
the corresponding correlation was 0.866 for both methods. Cluster agreement was
also unchanged: 0.573 for raw DTW and 0.470 for SRVF-DTW.

This negative result is useful. It shows that simple geometric bridge
interpolation does not recover the route-comparison structure lost during
prolonged observation gaps. The next model must represent uncertainty over
possible paths inside the missing interval rather than inserting a single
deterministic path.

## Gaussian-Process Prototype

A small Gaussian-process prototype was then run on 12 transit-focused spring
trajectories with a 40% contiguous gap. Each unit-sphere coordinate was modeled
with an independent fixed-hyperparameter Gaussian process. For each gap scenario,
eight posterior route samples were drawn and propagated through raw-DTW and
SRVF-DTW distance matrices, clustering, and anomaly ranking.

The prototype demonstrated the mechanics of uncertainty propagation, but it is
not yet a suitable final movement model. Compared with a deterministic spherical
bridge, GP posterior samples produced much wider and poorer downstream
agreement with the complete-data baseline:

| Method | Metric | Matrix correlation | Median relative error | Cluster ARI |
|---|---|---:|---:|---:|
| Spherical bridge | Raw DTW | 0.976 | 0.107 | 0.711 |
| GP samples | Raw DTW | 0.413 | 1.607 | 0.197 |
| Spherical bridge | SRVF-DTW | 0.929 | 0.132 | 0.894 |
| GP samples | SRVF-DTW | 0.561 | 0.719 | 0.332 |

The route-sample plot showed that independent-coordinate GP samples can wander
away from plausible migration corridors. This is useful as a prototype because
it exposes uncertainty, but the next model needs movement-aware constraints:
for example a continuous-time state-space model, Brownian bridge movement
model, correlated random walk, or GP with stronger path and speed constraints.

## Brownian Bridge Prototype

A movement-aware bridge prototype was then added. The method keeps the
observations before and after the gap fixed, constructs a great-circle bridge
between them, adds Brownian bridge perturbations in local tangent planes, and
projects the sampled path back to the unit sphere. The perturbation scale is now
estimated from observed local great-circle residuals rather than set only by
hand. For the 12-route prototype, the estimated scale was `0.0010018` in
unit-sphere coordinates.

For the same 12-route, 40% contiguous-gap prototype:

| Method | Metric | Matrix correlation | Median relative error | Cluster ARI | Anomaly-rank correlation |
|---|---|---:|---:|---:|---:|
| Spherical bridge | Raw DTW | 0.956 | 0.106 | 0.844 | 0.860 |
| Brownian bridge samples | Raw DTW | 0.937 | 0.116 | 0.690 | 0.746 |
| Spherical bridge | SRVF-DTW | 0.906 | 0.112 | 0.690 | 0.890 |
| Brownian bridge samples | SRVF-DTW | 0.881 | 0.087 | 0.850 | 0.901 |

The Brownian bridge prototype provides a more defensible uncertainty baseline
than the independent-coordinate GP because samples are constrained to the
deleted interval and fixed at both ends. It also shows that downstream
conclusions can differ by metric: in this run, SRVF-DTW cluster assignments were
stable across Brownian bridge samples, while raw-DTW anomaly rankings were much
less stable.

The estimated-scale Brownian bridge is a better first movement-aware baseline
than the fixed-scale version. A publishable version should still refine the
variance model by conditioning it on sampling interval, season, movement speed,
or local route context.

## Season-Aware Batch Experiment

The Brownian bridge prototype was then expanded from a 12-route single-gap
prototype to a season-aware batch experiment:

- 30 spring transit routes and 30 autumn transit routes;
- 20%, 40%, and 60% contiguous observation gaps;
- three repeated gap placements per condition;
- six Brownian bridge samples per repeated gap scenario;
- season-specific bridge-scale estimation from observed local great-circle
  residuals.

The estimated Brownian bridge scales differed by season:

| Season | Estimated bridge scale |
|---|---:|
| Spring | 0.00108755 |
| Autumn | 0.000352488 |

This difference supports season-specific movement uncertainty rather than a
single global bridge variance.

Several patterns are now visible:

1. Distance-matrix rank correlations remain high for raw DTW across both
   seasons even at 60% contiguous missingness.
2. SRVF-DTW distance-matrix stability decreases more strongly, especially in
   autumn at 60% missingness.
3. Median relative distance error grows with gap size, but the estimated
   Brownian bridge can reduce SRVF-DTW relative error compared with a purely
   deterministic spherical bridge.
4. Cluster agreement is the least stable diagnostic and varies strongly by
   season, metric, and reconstruction method.
5. Anomaly-rank correlations remain high in spring but degrade for autumn
   SRVF-DTW under 60% gaps.

The batch experiment strengthens the paper direction: the goal should not be to
choose one universally best route distance. The central contribution should be
to quantify when downstream ecological-informatics conclusions are stable under
plausible missing-route reconstructions.

## Required Validation

1. Expand the simulation design to vary gap location, gap duration, sampling
   interval, and location error.
2. Evaluate coverage and calibration using simulated latent routes with known
   truth.
3. Add multiple public animal tracking datasets with different movement
   geometries and sampling regimes.
4. Compare deterministic interpolation, state-space reconstruction, Gaussian
   process reconstruction, and continuous-time movement models.
5. Validate downstream conclusions against ecological labels or covariates
   where available.
