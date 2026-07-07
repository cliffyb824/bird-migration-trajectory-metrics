# Plain-Language Summary

GPS tracking data often contain long gaps. If a bird is not observed during an
important part of migration, analysts may fill the gap with one smooth path and
then compare the completed route with other routes. This can make the results
look more certain than they really are.

This study asks how uncertainty from missing route segments affects migration
route comparison. Using open tracking data from Lesser Black-backed Gulls, the
analysis removes observations in controlled ways, reconstructs missing segments,
and then checks how distance matrices, route clusters, and anomaly rankings
change.

The results show that random point loss and long contiguous gaps are different
problems. Randomly missing points often have little effect after resampling, but
long gaps can change downstream conclusions. Brownian bridge samples provide a
transparent way to stress-test the analysis, but withheld-segment validation
shows that this simple baseline should not be treated as a fully calibrated
model of the true hidden path. The study therefore estimates how much the
uncertainty envelope would need to be widened to approach 90% coverage of hidden
observed points.

The study is a reproducible case study, not a claim about all gull migration.
The main contribution is a validate-calibrate-propagate diagnostic that can be
applied to other tracking datasets: reconstruct plausible missing routes,
validate and calibrate the uncertainty envelope when withheld observations are
available, propagate that uncertainty into the analyses that depend on route
distances, and report whether the conclusions remain stable.
