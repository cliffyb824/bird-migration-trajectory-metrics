# Migration Segmentation Notes

## Why Segmentation Matters

The raw dataset contains long time series for individual birds. These tracks include breeding-area movement, migration, wintering-area movement, stopovers, and repeated years. Treating an entire multi-year individual record as one trajectory is not scientifically appropriate for route-shape analysis.

The unit of analysis should be a candidate migration route, not an entire bird record.

## Current First-Pass Heuristic

The current prototype uses simple calendar windows:

- spring: February to May;
- autumn: July to November.

It then filters for long-distance movement:

- at least 30 points;
- maximum distance from Zeebrugge breeding area at least 300 km;
- start-end displacement at least 150 km.

This produces candidate route segments that are good enough for a first SRVF pipeline test.

## Limitations

The first-pass heuristic is not yet journal-quality because:

1. It may include stationary wintering movements inside the spring/autumn window.
2. It does not explicitly detect departure and arrival dates.
3. It does not distinguish migration flight from stopover residence.
4. It assumes all birds share the same broad calendar windows.
5. It uses an approximate breeding colony coordinate instead of individual-specific breeding sites.

## Better Segmentation Options

### Option 1: Distance-From-Colony Threshold

Detect departure when distance from colony remains above a threshold for several consecutive observations.

Detect return or arrival when the bird reaches a stable distant region or returns to colony.

### Option 2: Movement-Speed Change Points

Use speed or step length to identify high-movement periods. Migration phases should have longer directional steps than local residence periods.

### Option 3: Residence Area Detection

Cluster locations into breeding, stopover, and wintering areas. Then define migration as transitions between residence areas.

### Option 4: Use Existing Movebank Event Metadata

Check whether Movebank or the Darwin Core extension includes track/session identifiers, deployment metadata, or event annotations that can help separate biologically meaningful movement periods.

## Recommended Manuscript Path

For the first paper, use a transparent and reproducible segmentation rule:

1. Define breeding colony reference coordinates.
2. Define seasonal windows.
3. Use distance-from-colony and displacement thresholds to extract candidate migration segments.
4. Report the thresholds clearly.
5. Add a sensitivity analysis showing that moderate threshold changes do not
   substantially alter the candidate-route sample.

This is simpler than full behavioral-state modeling and easier to defend in a first methodological paper.

## Implemented Refinement: Transit-Focused Trimming

Implemented script:

`src/trim_transit_segments.py`

The refinement trims broad seasonal candidate segments to likely transit portions using distance from the Zeebrugge colony.

Heuristic:

- autumn: keep from departure away from the colony to near maximum seasonal distance;
- spring: keep from leaving distant area to return near the colony;
- departure/return threshold: 100 km;
- near-maximum threshold: 90% of seasonal maximum distance;
- minimum retained points: 20.

Current output:

- `data/processed/lbbg_zeebrugge_transit_segments.csv`
- `data/processed/lbbg_zeebrugge_transit_segments_summary.csv`

Result:

- broad candidate points: 1,151,566;
- transit-focused points: 374,341;
- transit-focused segments: 381.

This should become the preferred segmentation for future experiments, while still being described as heuristic.

## Implemented Sensitivity Check

Implemented script:

`src/segmentation_sensitivity.py`

The check re-runs transit trimming under moderate threshold changes:

- departure/return threshold: 75 km, 100 km, 150 km;
- near-maximum-distance fraction: 0.85, 0.90, 0.95;
- minimum retained points: 20.

Result:

- baseline: 381 transit routes and 374,341 points;
- sensitivity range: 377 to 383 transit routes;
- point-count range: 272,794 to 413,853 points.

Interpretation:

The route count is stable under moderate threshold changes, but the retained
number of points varies because endpoint residence-period movement is more
sensitive to trimming. This supports using the rule as candidate-route
extraction, not as behavioral-state validation.
