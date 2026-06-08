# Next Experiment: Shape Perturbation

## Why This Experiment Is Needed

The artificial time-warp experiment showed that raw-coordinate DTW is already extremely robust to temporal reparameterization. Therefore, time-warp robustness alone is not enough to justify SRVF-DTW.

The next question is:

> Does SRVF-DTW behave differently from raw-coordinate DTW when the route shape changes, not just the traversal speed?

## Candidate Perturbations

Apply controlled perturbations to one route while keeping the same endpoints.

### 1. Local Detour

Push a middle section of the route sideways, creating a detour.

Expected behavior:

- raw DTW may remain small if many points still align spatially;
- SRVF-DTW may increase because local velocity direction changes.

### 2. Route Smoothing

Smooth a route to remove local wiggles.

Expected behavior:

- raw DTW may measure point displacement;
- SRVF-DTW may capture loss of local path-shape variation.

### 3. Direction Reversal

Reverse route order.

Expected behavior:

- both metrics should change substantially if direction matters.

### 4. Local Loop Injection

Insert a loop or strong curvature segment.

Expected behavior:

- SRVF-DTW should react to the velocity-shape change.

## Success Criterion

The goal is not necessarily to prove SRVF-DTW is always better.

The goal is to show what each metric is sensitive to:

- raw DTW: spatial coordinate alignment;
- SRVF-DTW: aligned velocity/shape structure.

This can support a more nuanced paper:

> coordinate DTW is best for pure timing differences, while SRVF-DTW provides complementary sensitivity to path-shape and directional structure.
