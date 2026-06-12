
"""Create a polished Figure 1 infographic for route-gap uncertainty analysis."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from brownian_bridge_gap_reconstruction import brownian_bridge_sphere_sample, estimate_global_bridge_scale
from gap_reconstruction_baseline import records_to_sphere
from geometry import spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories

BLUE = "#2A6FBB"; ORANGE = "#E07A2F"; PINK = "#B64B8C"; GREEN = "#2E8B57"; PURPLE = "#6656A5"; DARK = "#263238"; GREY = "#6B7280"

def sphere_to_lonlat(points):
    points = np.asarray(points, dtype=float)
    lon = np.rad2deg(np.arctan2(points[:, 1], points[:, 0]))
    lat = np.rad2deg(np.arcsin(np.clip(points[:, 2], -1.0, 1.0)))
    return lon, lat

def centered_gap_indices(n_records, missing_fraction):
    gap_size = min(max(1, int(round(n_records * missing_fraction))), n_records - 2)
    start = max(1, (n_records - gap_size) // 2)
    return start, min(n_records - 1, start + gap_size)

def make_spherical_bridge(points, start, stop):
    fractions = np.linspace(0.0, 1.0, stop - start + 2)[1:-1]
    bridge = spherical_linear_interpolate(points[start - 1], points[stop], fractions)
    return np.vstack([points[:start], bridge, points[stop:]])

def setup_route_axis(ax, complete):
    lon, lat = sphere_to_lonlat(complete)
    ax.set_xlim(lon.min() - max(0.4, 0.08 * np.ptp(lon)), lon.max() + max(0.4, 0.08 * np.ptp(lon)))
    ax.set_ylim(lat.min() - max(0.4, 0.08 * np.ptp(lat)), lat.max() + max(0.4, 0.08 * np.ptp(lat)))
    ax.set_xlabel("Longitude", fontsize=9); ax.set_ylabel("Latitude", fontsize=9)
    ax.grid(color="#E2E8F0", linewidth=0.8); ax.tick_params(labelsize=8, colors=GREY)
    for spine in ax.spines.values(): spine.set_color("#D6DEE8")

def stage(ax, x, title, text, color):
    box = FancyBboxPatch((x, 0.18), 0.21, 0.66, boxstyle="round,pad=0.015,rounding_size=0.025", facecolor="white", edgecolor=color, linewidth=1.8)
    ax.add_patch(box); ax.add_patch(Rectangle((x, 0.72), 0.21, 0.12, facecolor=color, edgecolor=color))
    ax.text(x + 0.025, 0.78, title, color="white", fontsize=11, weight="bold", va="center")
    ax.text(x + 0.025, 0.66, text, color=DARK, fontsize=9.3, va="top", linespacing=1.25)

def draw_pipeline(ax):
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.96, "Route-gap uncertainty workflow for animal tracking data", ha="center", va="center", fontsize=16, weight="bold", color=DARK)
    ax.text(0.5, 0.90, "Replace a single completed track with validated uncertainty carried into route-comparison conclusions", ha="center", va="center", fontsize=10.5, color=GREY)
    xs = [0.02, 0.27, 0.52, 0.77]
    titles = ["1  GPS gaps", "2  Reconstruct", "3  Validate", "4  Propagate"]
    texts = ["Observed route\n+ prolonged\nunobserved interval", "Deterministic bridge\n+ stochastic route\nensemble", "Withheld segments\n+ calibrated\ncoverage", "Distance matrix\nclusters\nanomaly ranks"]
    colors = [BLUE, ORANGE, GREEN, PURPLE]
    for x, t, txt, c in zip(xs, titles, texts, colors): stage(ax, x, t, txt, c)
    for x0, x1 in [(0.235, 0.27), (0.485, 0.52), (0.735, 0.77)]:
        ax.add_patch(FancyArrowPatch((x0, 0.51), (x1, 0.51), arrowstyle="-|>", mutation_scale=18, linewidth=1.8, color=DARK))

def plot_gap(ax, complete, observed, removed):
    lon, lat = sphere_to_lonlat(complete); obs_lon, obs_lat = sphere_to_lonlat(observed); rem_lon, rem_lat = sphere_to_lonlat(removed)
    ax.plot(lon, lat, color="#B8C2CC", linewidth=2.2); ax.scatter(obs_lon, obs_lat, s=14, color=BLUE, alpha=0.78)
    ax.plot(rem_lon, rem_lat, color=ORANGE, linewidth=4.2, alpha=0.90)
    ax.set_title("Observed migration route with a prolonged GPS gap", fontsize=11, weight="bold", color=DARK)
    ax.text(0.03, 0.94, "blue = observed fixes", transform=ax.transAxes, color=BLUE, fontsize=9, weight="bold")
    ax.text(0.03, 0.86, "orange = hidden gap", transform=ax.transAxes, color=ORANGE, fontsize=9, weight="bold")
    setup_route_axis(ax, complete)

def plot_recon(ax, complete, observed, bridge, samples):
    lon, lat = sphere_to_lonlat(complete); obs_lon, obs_lat = sphere_to_lonlat(observed); br_lon, br_lat = sphere_to_lonlat(bridge)
    ax.plot(lon, lat, color="#D5DAE0", linewidth=1.5)
    for sample in samples:
        slon, slat = sphere_to_lonlat(sample); ax.plot(slon, slat, color=PINK, linewidth=1.0, alpha=0.25)
    ax.plot(br_lon, br_lat, color=ORANGE, linewidth=2.6); ax.scatter(obs_lon, obs_lat, s=11, color=BLUE, alpha=0.35)
    ax.set_title("One bridge is not enough: sample plausible route alternatives", fontsize=11, weight="bold", color=DARK)
    ax.text(0.03, 0.94, "orange = deterministic bridge", transform=ax.transAxes, color=ORANGE, fontsize=9, weight="bold")
    ax.text(0.03, 0.86, "pink = uncertainty ensemble", transform=ax.transAxes, color=PINK, fontsize=9, weight="bold")
    setup_route_axis(ax, complete)

def plot_validation(ax):
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.03, 0.96, "Validate and calibrate", fontsize=11, weight="bold", color=DARK, va="top")
    rng = np.random.default_rng(4)
    for i, yy in enumerate(np.linspace(0.72, 0.30, 6)):
        cx = 0.34 + 0.06 * np.sin(i); r = 0.06 + 0.018 * (i % 3)
        ax.add_patch(plt.Circle((cx, yy), r, fill=False, edgecolor=PINK, linewidth=1.4, alpha=0.75))
        ax.scatter([cx + rng.normal(0, 0.055)], [yy + rng.normal(0, 0.055)], s=28, color=ORANGE, zorder=3)
    ax.text(0.60, 0.76, "Withheld route points\ncheck whether nominal\n90% envelopes are\nwide enough", fontsize=9.5, color=DARK, va="top")
    ax.add_patch(plt.Circle((0.24, 0.17), 0.045, fill=False, edgecolor=PINK, linewidth=1.5))
    ax.add_patch(FancyArrowPatch((0.34, 0.17), (0.58, 0.17), arrowstyle="-|>", mutation_scale=16, linewidth=1.5, color=DARK))
    ax.add_patch(plt.Circle((0.70, 0.17), 0.085, fill=False, edgecolor=GREEN, linewidth=1.8))
    ax.text(0.19, 0.06, "raw", fontsize=9, color=PINK); ax.text(0.62, 0.06, "calibrated", fontsize=9, color=GREEN)

def plot_outputs(ax):
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.03, 0.96, "Propagate into conclusions", fontsize=11, weight="bold", color=DARK, va="top")
    mat = np.array([[0, .25, .55, .72, .41], [.25, 0, .38, .61, .35], [.55, .38, 0, .28, .63], [.72, .61, .28, 0, .52], [.41, .35, .63, .52, 0]])
    ax.imshow(mat, extent=(0.05, 0.39, 0.43, 0.77), cmap="YlGnBu", vmin=0, vmax=.8); ax.text(0.22, 0.38, "distance matrix", ha="center", fontsize=8.5, color=GREY)
    ax.scatter([.58, .68, .77, .63, .83, .73], [.70, .76, .68, .55, .55, .47], s=95, c=[BLUE, BLUE, BLUE, GREEN, GREEN, GREEN], edgecolor="white", linewidth=.8); ax.text(0.71, 0.38, "cluster stability", ha="center", fontsize=8.5, color=GREY)
    for i, h in enumerate([.18, .34, .24, .58, .42]): ax.add_patch(Rectangle((.10 + i*.055, .10), .035, h*.33, facecolor=PURPLE, alpha=.82))
    ax.text(.22, .05, "anomaly ranks", ha="center", fontsize=8.5, color=GREY)
    ax.plot([.58, .66, .74, .82], [.18, .13, .22, .16], color=ORANGE, linewidth=2.3); ax.fill_between([.58, .66, .74, .82], [.12, .08, .16, .10], [.24, .20, .28, .23], color=ORANGE, alpha=.20)
    ax.text(.70, .05, "uncertainty bands", ha="center", fontsize=8.5, color=GREY)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input", default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv"); parser.add_argument("--output", default="figures/route_gap_uncertainty_framework.png")
    parser.add_argument("--min-points", type=int, default=120); parser.add_argument("--missing-fraction", type=float, default=0.40); parser.add_argument("--bridge-samples", type=int, default=22); parser.add_argument("--scale-max-span", type=int, default=6); parser.add_argument("--seed", type=int, default=20260612); args = parser.parse_args()
    groups = read_trajectory_points(args.input); selected = select_trajectories(groups, args.min_points, max_trajectories=20); trajectory_id, records = selected[0]
    scale = estimate_global_bridge_scale(selected, max_span=args.scale_max_span); start, stop = centered_gap_indices(len(records), args.missing_fraction)
    complete = records_to_sphere(records); observed = np.vstack([complete[:start], complete[stop:]]); removed = complete[start:stop]; bridge = make_spherical_bridge(complete, start, stop)
    rng = np.random.default_rng(args.seed); samples = [brownian_bridge_sphere_sample(records, start, stop, scale, rng) for _ in range(args.bridge_samples)]
    plt.rcParams.update({"font.family": "DejaVu Sans"}); fig = plt.figure(figsize=(14.5, 9.2), facecolor="white"); gs = gridspec.GridSpec(3, 4, height_ratios=[0.72, 1.3, 1.05], hspace=0.42, wspace=0.34)
    ax_pipe = fig.add_subplot(gs[0, :]); draw_pipeline(ax_pipe); ax_gap = fig.add_subplot(gs[1, 0:2]); plot_gap(ax_gap, complete, observed, removed); ax_rec = fig.add_subplot(gs[1, 2:4]); plot_recon(ax_rec, complete, observed, bridge, samples); ax_val = fig.add_subplot(gs[2, 0:2]); plot_validation(ax_val); ax_out = fig.add_subplot(gs[2, 2:4]); plot_outputs(ax_out)
    for label, ax in zip(["A", "B", "C", "D"], [ax_gap, ax_rec, ax_val, ax_out]): ax.text(-0.06, 1.06, label, transform=ax.transAxes, fontsize=14, weight="bold", color=DARK, va="top")
    fig.text(0.012, 0.012, f"Example route: {trajectory_id}; missing fraction={args.missing_fraction:.0%}; Brownian bridge scale={scale:.4g}", fontsize=8.5, color=GREY)
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); fig.savefig(out, dpi=320, bbox_inches="tight"); plt.close(fig)
    print(f"Trajectory: {trajectory_id}"); print(f"Bridge scale: {scale:.8g}"); print(f"Wrote: {out}")
if __name__ == "__main__": main()
