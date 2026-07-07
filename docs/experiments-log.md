# Experiments Log

## 2026-04-25: Data Download and First Distance Prototype

### Data

Downloaded `LBBG_ZEEBRUGGE` Darwin Core Archive from:

<https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3>

Local archive:

`data/raw/lbbg_zeebrugge_v1_3_dwca.zip`

Extracted occurrence table:

`data/raw/lbbg_zeebrugge/occurrence.txt`

### Standardization

Script:

`src/standardize_dwca.py`

Output:

`data/processed/lbbg_zeebrugge_standardized.csv`

Rows:

- source rows read: 1,801,214
- standardized GPS rows written: 1,801,052

Schema:

- `individual_id`
- `timestamp`
- `latitude`
- `longitude`
- `species`

### First Distance Prototype

Script:

`src/prototype_distances.py`

Input:

`data/processed/lbbg_zeebrugge_standardized.csv`

Output directory:

`data/processed/prototype_25_distances/`

Settings:

- max individuals: 25
- minimum points per individual: 100
- resampled points per trajectory: 100

Outputs:

- `pointwise_l2_distances.csv`
- `srvf_distances.csv`
- `distance_summary.csv`

Summary:

| Metric | Trajectories | Mean distance |
|---|---:|---:|
| pointwise_l2 | 25 | 0.9312806789807663 |
| srvf | 25 | 1.1998887128525548 |

### Notes

This is only a first technical sanity check. It does not yet split tracks by migration season, remove local breeding-area movement, or align outbound/return migration phases. The next scientific step is trajectory segmentation.

## 2026-04-25: First Candidate Migration Segmentation

### Segmentation Heuristic

Script:

`src/segment_migration.py`

Input:

`data/processed/lbbg_zeebrugge_standardized.csv`

Output:

- `data/processed/lbbg_zeebrugge_candidate_segments.csv`
- `data/processed/lbbg_zeebrugge_candidate_segments_summary.csv`

Heuristic:

- Split by individual, calendar year, and season.
- Spring months: February to May.
- Autumn months: July to November.
- Keep only segments with at least 30 points.
- Keep only segments with maximum distance from Zeebrugge breeding area at least 300 km.
- Keep only segments with start-end displacement at least 150 km.

Result:

- candidate segments: 386
- segment points: 1,151,566

### First Segmented-Route Distance Prototype

Script:

`src/prototype_distances.py`

Input:

`data/processed/lbbg_zeebrugge_candidate_segments.csv`

Output directory:

`data/processed/prototype_50_segment_distances/`

Settings:

- id column: `trajectory_id`
- max trajectories: 50
- minimum points per trajectory: 50
- resampled points per trajectory: 100

Summary:

| Metric | Trajectories | Mean distance |
|---|---:|---:|
| pointwise_l2 | 50 | 1.3726680058393381 |
| srvf | 50 | 0.9833332558422958 |

### Interpretation

This is the first route-level SRVF sanity check. It is more scientifically meaningful than treating each bird's entire multi-year record as one curve.

The segmentation is still preliminary. The current calendar windows may include stationary wintering or breeding-area movements. A stronger version should detect migration phases from movement patterns, distance from colony, or change points.

## 2026-04-25: First Prototype Figures

### Script

`src/plot_segment_prototype.py`

### Input

Distance matrices:

- `data/processed/prototype_50_segment_distances/pointwise_l2_distances.csv`
- `data/processed/prototype_50_segment_distances/srvf_distances.csv`

Segment points:

- `data/processed/lbbg_zeebrugge_candidate_segments.csv`

### Output

Folder:

`figures/prototype_50_segments/`

Files:

- `pointwise_l2_heatmap.png`
- `srvf_heatmap.png`
- `srvf_clustered_routes.png`
- `srvf_cluster_assignments.csv`

### Notes

Matplotlib's default Tk backend failed in this local Python installation, so the script explicitly uses the non-GUI `Agg` backend for PNG generation.

## 2026-04-25: First Cluster Evaluation Metrics

### Script

`src/evaluate_clusters.py`

### Input

`data/processed/prototype_50_segment_distances/`

### Output

- `data/processed/prototype_50_segment_distances/cluster_evaluation.csv`
- `data/processed/prototype_50_segment_distances/cluster_assignments_comparison.csv`

### Settings

- trajectories: 50
- clusters: 4
- clustering: agglomerative clustering with average linkage and precomputed distances

### Results

| Metric | Silhouette score | Davies-Bouldin index | Cluster sizes |
|---|---:|---:|---|
| pointwise_l2 | 0.46594864545064335 | 0.40473428828463726 | 1:23; 2:2; 3:24; 4:1 |
| srvf | 0.11979850096450981 | 1.0700769294736714 | 1:27; 2:1; 3:21; 4:1 |

### Interpretation

On this crude prototype, SRVF clustering is not yet better than pointwise L2 according to these simple internal cluster metrics. This is useful: it prevents overclaiming.

Likely reasons:

1. The migration segmentation is still broad and includes non-migration residence periods.
2. The current SRVF implementation does not yet perform optimal reparameterization/alignment.
3. The route sample is simply the first 50 candidate segments, not a curated balanced test set.
4. Pointwise L2 may be separating spring vs autumn direction strongly, which makes it look good under internal metrics.

Next improvement should focus on trajectory segmentation and SRVF alignment before making any journal-level performance claim.

## 2026-04-25: Season-Specific Distance and Cluster Evaluation

### Goal

Test whether SRVF clustering improves when spring and autumn candidate migration segments are analyzed separately.

### Data Split

Created:

- `data/processed/lbbg_zeebrugge_spring_candidate_segments.csv`
- `data/processed/lbbg_zeebrugge_autumn_candidate_segments.csv`

Rows:

- spring segment points: 535,917
- autumn segment points: 615,649

### Distance Outputs

Spring:

`data/processed/prototype_spring_100_segment_distances/`

Autumn:

`data/processed/prototype_autumn_100_segment_distances/`

Settings:

- max trajectories per season: 100
- resampled points per trajectory: 100
- minimum points per trajectory: 50

### Distance Summary

| Season | Metric | Trajectories | Mean distance |
|---|---|---:|---:|
| spring | pointwise_l2 | 100 | 1.0651730598910267 |
| spring | srvf | 100 | 0.9579071160950424 |
| autumn | pointwise_l2 | 100 | 0.9222506692880588 |
| autumn | srvf | 100 | 0.9102264412728999 |

### Cluster Evaluation

| Season | Metric | Silhouette score | Davies-Bouldin index | Cluster sizes |
|---|---|---:|---:|---|
| spring | pointwise_l2 | 0.3484973706773956 | 0.5903738639536162 | 1:26; 2:70; 3:1; 4:3 |
| spring | srvf | 0.1268148201324308 | 0.6524687973857654 | 1:95; 2:3; 3:1; 4:1 |
| autumn | pointwise_l2 | 0.5374584172148703 | 0.5042980127854604 | 1:96; 2:2; 3:1; 4:1 |
| autumn | srvf | 0.13555481367137634 | 0.49482810523155313 | 1:97; 2:1; 3:1; 4:1 |

### Interpretation

Season splitting alone does not make the current SRVF distance outperform pointwise L2 under these cluster metrics.

SRVF produces one dominant cluster plus a few outliers. This suggests the current prototype SRVF distance is not yet capturing enough discriminative route structure, or the route set is dominated by a single broad migration strategy.

The next useful experiment is not another cluster run. It is a controlled parameterization robustness test, where one route is artificially time-warped and we directly measure whether SRVF is less sensitive than pointwise L2.

## 2026-04-25: Controlled Time-Warp Robustness Test

### Goal

Test whether the current SRVF distance is less sensitive than pointwise L2 when the same trajectory is artificially traversed at different speeds.

### Script

`src/timewarp_robustness.py`

### Input

`data/processed/lbbg_zeebrugge_spring_candidate_segments.csv`

### Output

`data/processed/timewarp_robustness.csv`

### Test Trajectory

`5420314|2017|spring`

### Results

| Gamma | Pointwise L2 | SRVF |
|---:|---:|---:|
| 0.4 | 2.0790435378573373 | 1.1718665244717958 |
| 0.6 | 1.5761402787631742 | 1.1453696269520266 |
| 0.8 | 0.9646419252021011 | 1.1695018543023221 |
| 1.0 | 0.0 | 0.0 |
| 1.25 | 0.9652352263549577 | 1.19957859838442 |
| 1.5 | 1.3854454469871857 | 1.1806035860359916 |
| 2.0 | 1.8346989913575116 | 1.0597228617907908 |
| 2.5 | 2.085856293514071 | 1.0746778569372084 |

### Interpretation

The corrected test gives zero distance at `gamma=1.0`, as expected.

The current SRVF distance is less sensitive than pointwise L2 under strong time warps (`gamma=0.4`, `0.6`, `1.5`, `2.0`, `2.5`), but not under mild warps (`gamma=0.8`, `1.25`). This is plausible because this prototype uses direct SRVF comparison after sampling, not full elastic SRVF alignment.

This supports the next methodological step: implement reparameterization-aware SRVF matching or compare against DTW-style alignment.

## 2026-04-25: SRVF-DTW Alignment Prototype

### Goal

Add a practical alignment layer by applying dynamic time warping to SRVF sequences. This is a prototype approximation to reparameterization-aware SRVF matching.

### Code

Updated:

- `src/srvf.py`
- `src/prototype_distances.py`
- `src/evaluate_clusters.py`
- `src/timewarp_robustness.py`

New distance:

`srvf_dtw`

### Controlled Time-Warp Result

Input:

`data/processed/timewarp_robustness.csv`

Test trajectory:

`5420314|2017|spring`

| Gamma | Pointwise L2 | SRVF | SRVF-DTW |
|---:|---:|---:|---:|
| 0.4 | 2.0790435378573373 | 1.1718665244717958 | 0.014461450997286731 |
| 0.6 | 1.5761402787631742 | 1.1453696269520266 | 0.014976822961676548 |
| 0.8 | 0.9646419252021011 | 1.1695018543023221 | 0.012918200175101875 |
| 1.0 | 0.0 | 0.0 | 0.0 |
| 1.25 | 0.9652352263549577 | 1.19957859838442 | 0.012800177699975678 |
| 1.5 | 1.3854454469871857 | 1.1806035860359916 | 0.01459063182598883 |
| 2.0 | 1.8346989913575116 | 1.0597228617907908 | 0.015428585437127426 |
| 2.5 | 2.085856293514071 | 1.0746778569372084 | 0.01712794286804209 |

Interpretation:

SRVF-DTW behaves as expected in the controlled time-warp setting. Distances remain close to zero when the same route is traversed under different monotone time parameterizations.

### Season-Specific Cluster Evaluation With SRVF-DTW

Spring output:

`data/processed/prototype_spring_60_aligned_distances/`

Autumn output:

`data/processed/prototype_autumn_60_aligned_distances/`

Settings:

- 60 trajectories per season
- 80 resampled points per trajectory
- 4 agglomerative clusters

Spring:

| Metric | Silhouette score | Davies-Bouldin index | Cluster sizes |
|---|---:|---:|---|
| pointwise_l2 | 0.3865287765897742 | 0.49828802110354614 | 1:46; 2:11; 3:1; 4:2 |
| srvf | 0.126753994423502 | 0.6693059946069654 | 1:56; 2:2; 3:1; 4:1 |
| srvf_dtw | 0.13641472191087478 | 0.6368087817805075 | 1:56; 2:2; 3:1; 4:1 |

Autumn:

| Metric | Silhouette score | Davies-Bouldin index | Cluster sizes |
|---|---:|---:|---|
| pointwise_l2 | 0.5690711352771309 | 0.17335904082785536 | 1:57; 2:1; 3:1; 4:1 |
| srvf | 0.1369001893907126 | 0.5256508223347179 | 1:57; 2:1; 3:1; 4:1 |
| srvf_dtw | 0.10697738903139627 | 1.1438836642122554 | 1:2; 2:54; 3:3; 4:1 |

### Interpretation

SRVF-DTW clearly improves robustness to time warping in a controlled test. It does not yet improve route clustering under simple internal metrics.

This distinction is important for the paper:

- Strong claim supported now: aligned SRVF is robust to timing differences.
- Claim not yet supported: aligned SRVF gives better ecological clustering.

The next paper direction should emphasize parameterization robustness first, then use clustering as exploratory analysis rather than the central proof.

## 2026-04-25: Time-Warp Robustness Figure

### Script

`src/plot_timewarp_robustness.py`

### Input

`data/processed/timewarp_robustness.csv`

### Output

`figures/timewarp_robustness.png`

### Manuscript Role

This is currently the strongest central result figure. It directly supports the claim that DTW-aligned SRVF is robust to artificial temporal reparameterization.

## 2026-04-25: Batch Time-Warp Robustness Test

### Goal

Strengthen the central robustness claim by repeating the artificial time-warp test across multiple candidate migration trajectories.

### Scripts

- `src/timewarp_robustness_batch.py`
- `src/plot_timewarp_robustness_batch.py`

### Input

`data/processed/lbbg_zeebrugge_spring_candidate_segments.csv`

### Outputs

- `data/processed/timewarp_robustness_batch.csv`
- `data/processed/timewarp_robustness_batch_summary.csv`
- `figures/timewarp_robustness_batch.png`

### Settings

- trajectories: 20
- minimum points per trajectory: 500
- resampled points: 100
- gamma values: 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5

### Summary

| Gamma | Pointwise L2 mean | SRVF mean | SRVF-DTW mean |
|---:|---:|---:|---:|
| 0.4 | 1.2444498363167393 | 0.968958847756755 | 0.019325658056771614 |
| 0.6 | 0.9310504779654554 | 0.967076142571106 | 0.01609352585907372 |
| 0.8 | 0.5656499129164746 | 0.9434514101941843 | 0.012090253859062587 |
| 1.0 | 0.0 | 0.0 | 0.0 |
| 1.25 | 0.5658620339303062 | 0.9547479887135657 | 0.01228293652056691 |
| 1.5 | 0.8211949693919005 | 0.9611484327981671 | 0.014435711641705923 |
| 2.0 | 1.1034440678272008 | 0.9628629088744424 | 0.01626182445972623 |
| 2.5 | 1.268325228904795 | 0.9391628298318258 | 0.01756156790554835 |

### Interpretation

This is stronger than the single-route test. Across 20 trajectories, SRVF-DTW remains close to zero under artificial time warping, while pointwise L2 increases substantially and direct SRVF remains sensitive to sampling alignment.

This should be the main quantitative evidence for the paper's central claim.

## 2026-04-26: Added Raw-Coordinate DTW Baseline

### Goal

Check whether SRVF-DTW provides time-warp robustness beyond a plain DTW baseline applied directly to trajectory coordinates.

### Code Updated

- `src/srvf.py`
- `src/prototype_distances.py`
- `src/evaluate_clusters.py`
- `src/timewarp_robustness.py`
- `src/timewarp_robustness_batch.py`
- `src/plot_timewarp_robustness.py`
- `src/plot_timewarp_robustness_batch.py`

### Batch Robustness Summary With Raw DTW

| Gamma | Pointwise L2 mean | Raw DTW mean | SRVF mean | SRVF-DTW mean |
|---:|---:|---:|---:|---:|
| 0.4 | 1.2444498363167393 | 0.001063001090542203 | 0.968958847756755 | 0.019325658056771614 |
| 0.6 | 0.9310504779654554 | 0.0009587420238497521 | 0.967076142571106 | 0.01609352585907372 |
| 0.8 | 0.5656499129164746 | 0.0005807522427376629 | 0.9434514101941843 | 0.012090253859062587 |
| 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 1.25 | 0.5658620339303062 | 0.0006604571131718759 | 0.9547479887135657 | 0.01228293652056691 |
| 1.5 | 0.8211949693919005 | 0.000764045206497918 | 0.9611484327981671 | 0.014435711641705923 |
| 2.0 | 1.1034440678272008 | 0.0008337899027639663 | 0.9628629088744424 | 0.01626182445972623 |
| 2.5 | 1.268325228904795 | 0.0008481955980346106 | 0.9391628298318258 | 0.01756156790554835 |

### Interpretation

This is a critical baseline. Raw-coordinate DTW is even more invariant than SRVF-DTW in the pure artificial time-warp experiment.

Therefore, the paper cannot claim that SRVF-DTW is uniquely robust to time warping. Plain DTW already solves that controlled problem very strongly.

The revised scientific question should become:

> Does SRVF-DTW provide a route-shape representation that is complementary to raw-coordinate DTW, especially when local velocity structure, path shape, or geometric deformation matter?

The next experiment should compare raw DTW vs SRVF-DTW under shape perturbations, not only time warping.

## 2026-04-26: Controlled Shape-Perturbation Experiment

### Goal

Compare metric sensitivity under perturbations that change route shape, not only traversal speed.

### Scripts

- `src/shape_perturbation.py`
- `src/plot_shape_perturbation.py`

### Input

`data/processed/lbbg_zeebrugge_spring_candidate_segments.csv`

### Outputs

- `data/processed/shape_perturbation.csv`
- `figures/shape_perturbation.png`

### Test Trajectory

`5420314|2017|spring`

### Results

| Variant | Pointwise L2 | Raw DTW | SRVF | SRVF-DTW |
|---|---:|---:|---:|---:|
| identity | 0.0 | 0.0 | 0.0 | 0.0 |
| time_warp_gamma_0.4 | 2.0790435378573373 | 0.000793274006325287 | 1.1718665244717958 | 0.014461450997286731 |
| time_warp_gamma_2.5 | 2.085856293514071 | 0.0009131388984999806 | 1.0746778569372084 | 0.01712794286804209 |
| smoothed | 0.19163603996788717 | 0.0031723986412231053 | 0.6765853044976987 | 0.019980267275319062 |
| local_detour | 0.42092208959092486 | 0.013098083012419177 | 0.3221236380199373 | 0.013836618937681207 |
| local_loop | 0.27407604681802883 | 0.008480739430255034 | 0.9081876464122884 | 0.03289328590606819 |
| reversed | 3.485320004963781 | 0.155859022407241 | 1.1185195644601154 | 0.027071770315316684 |

### Interpretation

Raw-coordinate DTW is extremely robust to pure time warping and often gives very small distances for shape perturbations as well. SRVF-DTW reacts more strongly than raw DTW to smoothing and loop-like perturbations, suggesting complementary sensitivity to local velocity/shape structure.

However, this is only a single-route experiment. The next step should batch this across multiple trajectories before making a manuscript-level claim.

## 2026-04-26: Batch Shape-Perturbation Experiment

### Goal

Repeat the controlled shape-perturbation experiment across multiple trajectories.

### Scripts

- `src/shape_perturbation_batch.py`
- `src/plot_shape_perturbation_batch.py`

### Outputs

- `data/processed/shape_perturbation_batch.csv`
- `data/processed/shape_perturbation_batch_summary.csv`
- `figures/shape_perturbation_batch.png`

### Settings

- trajectories: 20
- minimum points per trajectory: 500
- resampled points: 100

### Summary

| Variant | Pointwise L2 mean | Raw DTW mean | SRVF mean | SRVF-DTW mean |
|---|---:|---:|---:|---:|
| time_warp_gamma_0.4 | 1.2444498363167393 | 0.001063001090542203 | 0.968958847756755 | 0.019325658056771614 |
| time_warp_gamma_2.5 | 1.268325228904795 | 0.0008481955980346106 | 0.9391628298318258 | 0.01756156790554835 |
| smoothed | 0.15132902545085453 | 0.0024902206687475613 | 0.6538466136436579 | 0.020010400949150083 |
| local_detour | 0.42215883971962437 | 0.013962623639418211 | 0.3374279454238761 | 0.014277315030637843 |
| local_loop | 0.2745675850715802 | 0.008475957139362243 | 0.9460515556139789 | 0.032723293772736375 |
| reversed | 2.0811541997374103 | 0.08899158846924836 | 1.0040154817728104 | 0.02648840355579492 |

### Interpretation

The batch result confirms the single-route pattern.

Raw-coordinate DTW is strongest for pure time-warp invariance and remains very small for several perturbations. SRVF-DTW is more sensitive than raw DTW to smoothing and local loop perturbations, suggesting complementary sensitivity to local velocity-shape structure.

This gives the paper a more nuanced contribution:

> Raw DTW handles temporal alignment extremely well, while SRVF-DTW provides a complementary velocity-shape view that reacts more strongly to certain path-shape perturbations.

## 2026-04-26: Prototype Anomaly Scores

### Goal

Add a concrete exploratory anomaly-detection output based on route distance matrices.

### Scripts

- `src/anomaly_scores.py`
- `src/plot_anomaly_routes.py`

### Inputs

- `data/processed/prototype_50_segment_distances/srvf_dtw_distances.csv`
- `data/processed/lbbg_zeebrugge_candidate_segments.csv`

### Outputs

- `data/processed/prototype_50_segment_distances/srvf_dtw_anomaly_scores.csv`
- `figures/top_anomaly_routes.png`

### Top Ranked Routes

| Rank | Trajectory ID | Mean SRVF-DTW distance |
|---:|---|---:|
| 1 | 5519709\|2018\|autumn | 0.03866937359897959 |
| 2 | 5424410\|2019\|spring | 0.037895919021428574 |
| 3 | 5424410\|2016\|autumn | 0.03778107405306123 |
| 4 | 5509729\|2018\|spring | 0.03586363305877551 |
| 5 | 5424410\|2017\|spring | 0.03575712442265306 |
| 6 | 5468062\|2016\|autumn | 0.035690302648163266 |

### Interpretation

This is an exploratory downstream application. The anomaly scores rank routes by mean distance to other routes in the prototype set. They should not be interpreted as biological abnormality without better segmentation and ecological validation.

## 2026-04-26: Transit-Focused Segment Trimming

### Goal

Improve the broad calendar-window migration segments by trimming likely residence periods and retaining a more focused transit portion.

### Script

`src/trim_transit_segments.py`

### Inputs

`data/processed/lbbg_zeebrugge_candidate_segments.csv`

### Outputs

- `data/processed/lbbg_zeebrugge_transit_segments.csv`
- `data/processed/lbbg_zeebrugge_transit_segments_summary.csv`
- `data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv`
- `data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv`

### Heuristic

- Autumn: keep from initial departure away from the colony to near maximum seasonal distance.
- Spring: keep from leaving distant area to return near the colony.
- Distance thresholds:
  - departure/return threshold: 100 km
  - near-maximum distance threshold: 90% of segment maximum distance
  - minimum retained points: 20

### Results

- broad candidate segments: 386
- transit-focused segments: 381
- broad segment points: 1,151,566
- transit-focused points: 374,341
- transit spring points: 74,567
- transit autumn points: 299,774

### 50-Route Transit Prototype Metrics

Output:

`data/processed/prototype_50_transit_distances/`

Distance summary:

| Metric | Mean distance |
|---|---:|
| pointwise_l2 | 1.2183135944195962 |
| raw_dtw | 0.04891630556443141 |
| srvf | 0.7826277731558501 |
| srvf_dtw | 0.03105299218470217 |

Cluster evaluation:

| Metric | Silhouette | Davies-Bouldin | Cluster sizes |
|---|---:|---:|---|
| pointwise_l2 | 0.5356274493072202 | 0.5053625963233932 | 1:17; 2:19; 3:5; 4:9 |
| raw_dtw | 0.5852250927995132 | 0.6915560559178868 | 1:25; 2:18; 3:1; 4:6 |
| srvf | 0.35071319036634513 | 0.5279422787445505 | 1:21; 2:1; 3:27; 4:1 |
| srvf_dtw | 0.32808935536923106 | 0.7902254543794579 | 1:26; 2:20; 3:3; 4:1 |

### Interpretation

Transit trimming substantially reduces residence-period data and gives more balanced exploratory clusters than the broad seasonal segments. Coordinate-based metrics still score better under simple internal cluster metrics, but the refined segmentation is a clear methodological improvement and should replace broad seasonal windows in future main experiments.

## 2026-04-26: Main Diagnostics Re-run on Transit-Focused Segments

### Goal

Regenerate the main time-warp and shape-perturbation diagnostic experiments using transit-focused spring segments instead of broad seasonal spring windows.

### Inputs

`data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv`

### Outputs

- `data/processed/timewarp_robustness_transit_batch.csv`
- `data/processed/timewarp_robustness_transit_batch_summary.csv`
- `figures/timewarp_robustness_transit_batch.png`
- `data/processed/shape_perturbation_transit_batch.csv`
- `data/processed/shape_perturbation_transit_batch_summary.csv`
- `figures/shape_perturbation_transit_batch.png`

### Time-Warp Summary

| Gamma | Pointwise L2 mean | Raw DTW mean | SRVF mean | SRVF-DTW mean |
|---:|---:|---:|---:|---:|
| 0.4 | 0.5401714535829439 | 0.0014869725762602082 | 0.685184331576141 | 0.014653465056426096 |
| 0.6 | 0.3540315126429484 | 0.0006987880842676817 | 0.6877773003868797 | 0.010640408796202653 |
| 0.8 | 0.19333741504377921 | 0.0004816004416918603 | 0.6477052008262472 | 0.00683266230006888 |
| 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 1.25 | 0.19609632054654166 | 0.0004823791671960126 | 0.6533210513313936 | 0.007064085899304644 |
| 1.5 | 0.3080518984895385 | 0.0006304807226049696 | 0.6829251905713403 | 0.010010053550777054 |
| 2.0 | 0.46034355223107915 | 0.0007721351144202782 | 0.7024381864957979 | 0.013011057295497199 |
| 2.5 | 0.5671272743555884 | 0.0009213309756798035 | 0.7087003929524218 | 0.015172489126689314 |

### Shape-Perturbation Summary

| Variant | Pointwise L2 mean | Raw DTW mean | SRVF mean | SRVF-DTW mean |
|---|---:|---:|---:|---:|
| time_warp_gamma_0.4 | 0.5401714535829439 | 0.0014869725762602082 | 0.685184331576141 | 0.014653465056426096 |
| time_warp_gamma_2.5 | 0.5671272743555884 | 0.0009213309756798035 | 0.7087003929524218 | 0.015172489126689314 |
| smoothed | 0.06897710777821284 | 0.0016620255274743434 | 0.44799477175201546 | 0.017434014780561058 |
| local_detour | 0.4231726954692133 | 0.015177519097949132 | 0.34738543357665663 | 0.01438306873971475 |
| local_loop | 0.27505198269131365 | 0.008696950596814768 | 0.9756246539137738 | 0.03373317190596527 |
| reversed | 1.0857258086878916 | 0.039948508173505405 | 0.9004901541563616 | 0.030391389358839567 |

### Interpretation

The refined transit-focused results preserve the same core pattern as the broad-window experiments:

- raw DTW is strongest for pure time-warp invariance;
- SRVF-DTW is also time-warp robust;
- SRVF-DTW reacts more strongly than raw DTW to smoothing and local loop perturbations.

These transit-focused results should supersede the broad-window results in the manuscript tables and figures.
