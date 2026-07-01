# Cover Letter

Dear Editor,

We are pleased to submit our manuscript entitled **"Uncertainty propagation
from incomplete tracking data in migratory-route comparison"** for
consideration in *Movement Ecology*.

Animal tracking datasets often contain irregular sampling and prolonged
observation gaps, yet migration routes are commonly compared after reducing
each incomplete track to a single deterministic curve. This manuscript
presents a validate--calibrate--propagate diagnostic framework for assessing
how missing-route uncertainty propagates into trajectory-distance analyses,
augmented with two new methodological contributions: state-conditioned
perturbation scale estimation and split-conformal envelope calibration.

Using open GPS tracking data for Lesser Black-backed Gulls from the
`LBBG_ZEEBRUGGE` dataset, we compare random point loss with contiguous
tracking gaps, evaluate deterministic spherical bridge and Brownian bridge
reconstruction, estimate behavioral-state-conditioned perturbation scales
(resting, foraging, directed), apply split-conformal prediction to provide
distribution-free finite-sample coverage guarantees, and propagate
reconstruction uncertainty into distance matrices, clustering, anomaly
ranking, and top-ranked anomaly overlap.

The key findings are:

1. Missingness mechanism matters more than missingness fraction: random
   thinning is largely absorbed by resampling, but contiguous gaps
   substantially alter downstream route-comparison conclusions.

2. Deterministic spherical bridge interpolation does not fully resolve the
   instability introduced by prolonged gaps.

3. A simple Brownian bridge baseline, with season-specific perturbation
   scales estimated from observed route residuals, makes reconstruction
   uncertainty visible but under-covers by a factor of 3--8×.

4. State-conditioned scale estimation reveals a twenty-fold range between
   resting and directed-flight perturbation magnitudes, but endpoint-state
   conditioning does not improve raw envelope calibration because
   gap-interior behavior is not predictable from boundary states alone.

5. Split-conformal calibration lifts empirical coverage from 33--66% to
   80--94% with conformal quantiles of 3.8--4.0, providing a principled,
   distribution-free alternative to ad-hoc empirical inflation.

The paper is positioned as a movement ecology methods contribution. Its main
claim is that route-comparison conclusions should not rely on a single
deterministic distance matrix when prolonged tracking gaps are present.
Instead, plausible reconstruction uncertainty should be validated and
calibrated, then propagated into the downstream conclusions that movement
ecologists inspect. To our knowledge, this is the first application of
conformal prediction to animal trajectory uncertainty quantification.

We believe the manuscript fits *Movement Ecology* because it addresses a
practical analytical challenge in movement data analysis---handling
incomplete trajectories---and provides a transparent, reproducible framework
for uncertainty-aware route comparison. The study engages with literature
published in *Movement Ecology* and related journals on Brownian bridges,
hidden Markov models, continuous-time movement models, and trajectory
similarity analysis.

This manuscript is original, has not been published previously, and is not
under consideration elsewhere.

The data used in the study are publicly available from the INBO
`LBBG_ZEEBRUGGE` dataset. The analysis code and manuscript materials are
available at:

<https://github.com/cliffyb824/bird-migration-trajectory-metrics>

The author declares no competing interests. This research did not receive any
specific grant from funding agencies in the public, commercial, or
not-for-profit sectors.

Sincerely,

Yuan Qiu

Department of Statistics, College of Economics

Hangzhou Dianzi University

Hangzhou 310003, China

yuanqiu@hdu.edu.cn
