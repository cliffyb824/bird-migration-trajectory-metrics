# Bird Migration SRVF Journal Paper Plan

## Target

This project is intended for an English-language journal paper. All titles, abstracts, figures, captions, and manuscript drafts should be prepared in academic English.

## Working Title

**Parameterization-Robust Shape Analysis of Bird Migration Trajectories Using Spherical SRVF**

Alternative titles:

1. **Sphere-Aware Shape Analysis of Bird Migration Trajectories Using Square Root Velocity Functions**
2. **Parameterization-Invariant Analysis of Bird Migration Trajectories via Spherical SRVF**
3. **Shape-Based Bird Migration Route Comparison on the Sphere Using Aligned SRVF**

## Core Idea

Bird migration routes are not just point sequences on a flat map. They are trajectories on the Earth's sphere, and their scientific meaning often lies in the overall route shape rather than the exact speed at which each bird flies.

This project uses SRVF to represent migration paths as shapes, so that routes with similar geometric patterns can be compared even when birds travel at different speeds or with different sampling rates.

## Main Motivation

Existing trajectory analysis methods often have three weaknesses:

1. They treat longitude-latitude tracks as flat 2D curves, ignoring the spherical structure of Earth.
2. They are sensitive to time parameterization, so two similar routes may look different if one bird flies faster or pauses more.
3. They focus on pointwise distance rather than the global shape of the migration path.

SRVF is attractive because it naturally focuses on curve shape and can reduce sensitivity to speed or reparameterization.

## Journal Framing

The safest English-journal framing is methodological but ecology-aware:

> This paper proposes a sphere-aware, shape-based framework for comparing bird migration trajectories. By representing migration paths with square root velocity functions, the method compares route geometry while reducing sensitivity to differences in flight speed, stopover timing, and sampling rate.

Avoid claiming that the method fully explains migration behavior. Also avoid claiming that SRVF produces better clusters until the evidence supports it. The stronger and safer claim is that aligned SRVF provides a useful geometric representation for parameterization-robust route comparison.

## Proposed Contribution

The paper can claim three modest but clear contributions:

1. A sphere-aware pipeline for representing bird migration GPS tracks as trajectories on the unit sphere.
2. An SRVF-based shape representation for comparing migration routes independent of flying speed.
3. A controlled time-warp experiment showing that aligned SRVF is less sensitive to route parameterization than pointwise distances.
4. Exploratory clustering and anomaly-detection experiments using real migration route segments.

Journal-style contribution wording:

1. We introduce a sphere-aware preprocessing pipeline that represents bird migration tracks as trajectories on the unit sphere.
2. We adapt the SRVF representation to migration trajectory comparison, enabling shape-based route similarity analysis with reduced sensitivity to temporal parameterization.
3. We evaluate the framework on public GPS tracking data through controlled parameterization-sensitivity tests.
4. We demonstrate exploratory downstream uses through route clustering and abnormal-route detection.

## Method Pipeline

1. **Data preparation**
   - Collect public bird migration GPS data.
   - Clean missing points and outliers.
   - Resample each trajectory to a common number of points.

2. **Spherical embedding**
   - Convert longitude-latitude coordinates into 3D unit-sphere coordinates:

   \[
   x = \cos(\phi)\cos(\lambda), \quad
   y = \cos(\phi)\sin(\lambda), \quad
   z = \sin(\phi)
   \]

   where \(\phi\) is latitude and \(\lambda\) is longitude.

3. **SRVF representation**
   - For a trajectory \(f(t)\), compute:

   \[
   q(t)=\frac{\dot f(t)}{\sqrt{\|\dot f(t)\|}}
   \]

   - In discrete data, approximate \(\dot f(t)\) using finite differences.

4. **Distance computation**
   - Compute pointwise, direct SRVF, and DTW-aligned SRVF distances.
   - Compare sensitivity to artificial time warping.

5. **Clustering or anomaly detection**
   - Use hierarchical clustering, k-means, or spectral clustering.
   - Visualize route groups on a map.
   - Identify abnormal or highly deviated migration paths.
   - Treat these as exploratory applications unless stronger metrics emerge.

## Baselines

Use simple baselines first:

1. Euclidean distance on resampled longitude-latitude points.
2. Great-circle distance averaged over aligned time points.
3. Dynamic Time Warping.
4. Direct SRVF distance.
5. DTW-aligned SRVF distance.

The paper becomes stronger if SRVF produces cleaner route clusters or more interpretable anomaly cases, but the current central claim should be parameterization robustness rather than clustering superiority.

## Evaluation Metrics

Use at least two quantitative metrics so the paper is not only visual:

1. Cluster quality: silhouette score, Davies-Bouldin index, or adjusted Rand index if labels are available.
2. Parameterization robustness: distance change after artificial time warping.
3. Route deviation: distance to cluster center or nearest medoid.
4. Interpretability: map-based visualization of cluster representatives and abnormal trajectories.

## Possible Experiments

### Experiment 1: Parameterization Robustness

Goal: show that aligned SRVF is less sensitive to time parameterization.

Procedure:

1. Take one route.
2. Create artificially time-warped versions of it.
3. Compare distances under pointwise L2, direct SRVF, and SRVF-DTW.

Expected result:

SRVF-DTW should give much smaller distances between shape-equivalent routes.

Current prototype result:

This expectation is supported. SRVF-DTW remains near zero under artificial time warping, while pointwise distances increase substantially.

### Experiment 2: Route Clustering

Goal: group birds by migration route shape as an exploratory downstream application.

Expected result:

Do not assume SRVF will outperform pointwise baselines. Report cluster metrics and interpret route groups cautiously.

### Experiment 3: Abnormal Migration Detection

Goal: detect routes that strongly deviate from typical migration shapes.

Procedure:

1. Compute each route's distance to its cluster center.
2. Rank routes by deviation score.
3. Visualize the top abnormal tracks.

Expected result:

The abnormal routes may correspond to detours, incomplete migration, weather disruption, or unusual stopover behavior.

## Paper Structure

1. **Introduction**
   - Bird migration GPS data is important for ecology.
   - Migration paths are spherical trajectories.
   - Existing methods are sensitive to speed and flat-map assumptions.
   - This paper proposes SRVF-based spherical trajectory shape analysis.

2. **Related Work**
   - Bird migration tracking.
   - Trajectory similarity and clustering.
   - Shape analysis and SRVF.
   - Spherical/geometric trajectory analysis.

3. **Method**
   - GPS preprocessing.
   - Sphere embedding.
   - SRVF representation.
   - Distance computation.
   - Clustering/anomaly detection.

4. **Experiments**
   - Dataset description.
   - Baselines.
   - Clustering results.
   - Speed-invariance test.
   - Abnormal route examples.

5. **Discussion**
   - What SRVF captures well.
   - Ecological interpretation of clusters.
   - Limitations: data quality, sampling rate, species differences.

6. **Conclusion**
   - SRVF provides a useful shape-based view of bird migration trajectories on the sphere.

## Draft Abstract

Bird migration trajectories contain rich information about route choice, stopover behavior, and population-level movement patterns. However, many trajectory comparison methods treat geographic tracks as planar point sequences and are sensitive to differences in flight speed, sampling rate, and temporal alignment. This paper proposes a sphere-aware shape analysis framework for bird migration trajectories based on square root velocity functions (SRVF). GPS tracks are embedded as curves on the unit sphere, transformed into SRVF representations, and compared using direct and DTW-aligned SRVF distances. The primary evaluation tests robustness to artificial temporal reparameterization, while route clustering and abnormal-route detection are used as exploratory applications. Preliminary experiments on open GPS tracking data for lesser black-backed gulls show that DTW-aligned SRVF distances are substantially less sensitive to time warping than pointwise trajectory distances. These results support SRVF as a useful geometric representation for parameterization-robust migration route comparison.

## Target Journal Types

Good target categories:

1. Ecological informatics journals.
2. Movement ecology or animal tracking journals.
3. Applied data science journals with ecological applications.
4. Pattern recognition or geospatial analysis journals, if the method is strong enough.

The first manuscript should probably target ecological informatics or movement ecology rather than a pure mathematics journal.

## Immediate Next Steps

1. Find one public GPS bird migration dataset.
2. Write a small Python script to load and visualize tracks.
3. Implement a simple discrete SRVF transform.
4. Compute pairwise distances and run clustering.
5. Generate the first three figures:
   - raw migration tracks;
   - SRVF-based cluster visualization;
   - baseline vs SRVF distance comparison.

## First Version Scope

Keep the first version small:

- one species or one dataset;
- 20 to 200 trajectories;
- simple SRVF implementation;
- simple clustering;
- clear visual comparison.

The goal is not to solve all migration analysis problems. The goal is to show that SRVF gives a clean, shape-aware representation that is useful for migration route comparison.
