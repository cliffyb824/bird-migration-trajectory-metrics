# Cover Letter

Dear Editor,

We are pleased to submit our manuscript entitled **"Uncertainty propagation
from incomplete tracking data in migratory-route comparison"** for
consideration in *Movement Ecology*.

Animal tracking datasets often contain irregular sampling and prolonged
observation gaps, yet migration routes are commonly compared after reducing
each incomplete track to a single deterministic curve. This manuscript
presents a validate--calibrate--propagate diagnostic framework for assessing
how missing-route uncertainty propagates into trajectory-distance analyses.
Using open GPS tracking data for Lesser Black-backed Gulls from the
`LBBG_ZEEBRUGGE` dataset, we compare random point loss with contiguous
tracking gaps, evaluate deterministic spherical bridge reconstruction,
validate Brownian bridge uncertainty envelopes against withheld route
segments, estimate empirical radius inflation needed for nominal coverage,
and propagate reconstruction uncertainty into distance matrices, clustering,
anomaly ranking, and top-ranked anomaly overlap.

The paper is positioned as a movement ecology methods contribution. Its main
claim is that route-comparison conclusions should not rely on a single
deterministic distance matrix when prolonged tracking gaps are present.
Instead, plausible reconstruction uncertainty should be validated and
calibrated where possible, then propagated into the downstream conclusions
that movement ecologists inspect. The framework engages with established
movement modeling approaches---including dynamic Brownian bridge movement
models, hidden Markov models, continuous-time stochastic processes, and
state-space formulations---while using a simple, transparent reconstruction
baseline that can be validated, calibrated, and compared against richer
models in future work.

The empirical results are intentionally framed as a reproducible open-data
case study rather than as species-general biological claims about gull
migration. The transferable contribution is the diagnostic framework for
validating, calibrating, and propagating missing-route uncertainty into
downstream computational conclusions. The framework applies to any movement
dataset where routes, gaps, reconstruction assumptions, and downstream
comparison tasks can be specified.

We believe the manuscript fits *Movement Ecology* because it addresses a
practical analytical challenge in movement data analysis---handling
incomplete trajectories---and provides a transparent, reproducible framework
for uncertainty-aware route comparison. The study uses methods and concepts
familiar to the movement ecology community (Brownian bridges, trajectory
similarity, movement models) and engages with literature published in
*Movement Ecology* and related journals.

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
