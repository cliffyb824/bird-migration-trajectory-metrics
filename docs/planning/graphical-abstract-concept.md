# Graphical Abstract Concept

## Core Message

Different trajectory metrics reveal different aspects of bird migration routes:

- raw DTW aligns coordinate sequences and is strongest for timing differences;
- SRVF-DTW aligns velocity-shape structure and shows a distinct response profile.

## Suggested Layout

Use a left-to-right workflow with four panels.

### Panel 1: GPS Tracks

Show raw bird GPS points or simplified migration tracks.

Label:

**Open GPS tracking data**

Visual:

- small map-like route lines;
- bird route points;
- colony marker.

### Panel 2: Sphere-Aware Route Representation

Show longitude-latitude points mapped to a sphere.

Label:

**Embed routes on unit sphere**

Visual:

- small globe/sphere;
- curve on surface.

### Panel 3: Metric Comparison

Show four metric branches:

1. Pointwise L2
2. Raw DTW
3. Direct SRVF
4. SRVF-DTW

Label:

**Compare coordinate and velocity-shape metrics**

Visual:

- two small curves;
- arrows to metric boxes.

### Panel 4: Diagnostic Experiments

Show two perturbation types:

- time warp;
- shape perturbation.

Label:

**Diagnose metric sensitivity**

Visual:

- time-warp icon: same curve with shifted point positions;
- shape icon: curve with loop or detour.

## Caption Draft

Workflow for comparing bird migration trajectories with coordinate-based and SRVF-based aligned metrics. GPS tracks are converted into transit-focused route segments, embedded on the unit sphere, and compared using pointwise, DTW, SRVF, and SRVF-DTW distances. Controlled time-warp and shape-perturbation experiments diagnose what each metric is sensitive to.

## Design Notes

- Keep it clean and schematic.
- Use four colors consistently:
  - pointwise L2: gray;
  - raw DTW: blue;
  - direct SRVF: orange;
  - SRVF-DTW: green.
- Avoid claiming a universally best method visually.
- Show that metric choice depends on the analysis question.
- Do not use generative AI to produce the submitted artwork.

## Possible Tools

- PowerPoint / Keynote for quick version.
- Inkscape / Illustrator for final vector version.
- Python/Matplotlib for simple route and perturbation panels.
