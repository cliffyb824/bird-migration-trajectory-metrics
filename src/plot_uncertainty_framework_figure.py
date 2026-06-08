"""Create Figure 1 schematic for uncertainty-aware route comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from brownian_bridge_gap_reconstruction import (
    brownian_bridge_sphere_sample,
    estimate_global_bridge_scale,
)
from gap_reconstruction_baseline import records_to_sphere
from geometry import spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories


def sphere_to_lonlat(points):
    """Convert unit-sphere points to longitude-latitude coordinates."""
    points = np.asarray(points, dtype=float)
    lon = np.rad2deg(np.arctan2(points[:, 1], points[:, 0]))
    lat = np.rad2deg(np.arcsin(np.clip(points[:, 2], -1.0, 1.0)))
    return lon, lat


def centered_gap_indices(n_records, missing_fraction):
    """Return a deterministic centered contiguous gap."""
    gap_size = max(1, int(round(n_records * missing_fraction)))
    gap_size = min(gap_size, n_records - 2)
    start = max(1, (n_records - gap_size) // 2)
    stop = min(n_records - 1, start + gap_size)
    return start, stop


def make_spherical_bridge(points, start, stop):
    """Construct deterministic spherical bridge points for a deleted gap."""
    gap_size = stop - start
    fractions = np.linspace(0.0, 1.0, gap_size + 2)[1:-1]
    bridge = spherical_linear_interpolate(points[start - 1], points[stop], fractions)
    return np.vstack([points[:start], bridge, points[stop:]])


def plot_panel_a(ax, complete, observed, removed):
    """Plot complete route and removed contiguous gap."""
    lon, lat = sphere_to_lonlat(complete)
    obs_lon, obs_lat = sphere_to_lonlat(observed)
    rem_lon, rem_lat = sphere_to_lonlat(removed)
    ax.plot(lon, lat, color="#555555", linewidth=1.7, label="Complete route")
    ax.scatter(obs_lon, obs_lat, s=11, color="#0072B2", alpha=0.75, label="Observed")
    ax.scatter(rem_lon, rem_lat, s=14, color="#D55E00", alpha=0.85, label="Removed gap")
    ax.set_title("A. Contiguous tracking gap")


def plot_panel_b(ax, complete, observed, bridge):
    """Plot deterministic spherical bridge reconstruction."""
    lon, lat = sphere_to_lonlat(complete)
    obs_lon, obs_lat = sphere_to_lonlat(observed)
    bridge_lon, bridge_lat = sphere_to_lonlat(bridge)
    ax.plot(lon, lat, color="#BBBBBB", linewidth=1.2, label="Complete route")
    ax.scatter(obs_lon, obs_lat, s=10, color="#0072B2", alpha=0.55, label="Observed")
    ax.plot(bridge_lon, bridge_lat, color="#E69F00", linewidth=2.0, label="Spherical bridge")
    ax.set_title("B. Deterministic bridge")


def plot_panel_c(ax, complete, observed, samples):
    """Plot Brownian bridge route samples."""
    lon, lat = sphere_to_lonlat(complete)
    obs_lon, obs_lat = sphere_to_lonlat(observed)
    ax.plot(lon, lat, color="#BBBBBB", linewidth=1.2, label="Complete route")
    ax.scatter(obs_lon, obs_lat, s=10, color="#0072B2", alpha=0.45, label="Observed")
    for sample in samples:
        sample_lon, sample_lat = sphere_to_lonlat(sample)
        ax.plot(sample_lon, sample_lat, color="#CC79A7", linewidth=0.9, alpha=0.28)
    ax.plot([], [], color="#CC79A7", linewidth=1.6, label="Brownian bridge samples")
    ax.set_title("C. Uncertainty-aware route samples")


def plot_panel_d(ax):
    """Plot conceptual propagation from route samples to downstream diagnostics."""
    ax.axis("off")
    boxes = [
        (0.08, 0.66, "Route\nsamples"),
        (0.38, 0.66, "Distance\nmatrices"),
        (0.68, 0.78, "Cluster\nstability"),
        (0.68, 0.53, "Anomaly-rank\nstability"),
        (0.38, 0.28, "Uncertainty\nintervals"),
    ]
    for x, y, text in boxes:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=10,
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": "#F2F2F2",
                "edgecolor": "#555555",
                "linewidth": 0.9,
            },
        )
    arrows = [
        ((0.18, 0.66), (0.29, 0.66)),
        ((0.48, 0.68), (0.58, 0.77)),
        ((0.48, 0.64), (0.58, 0.55)),
        ((0.42, 0.58), (0.42, 0.40)),
    ]
    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={"arrowstyle": "->", "color": "#333333", "linewidth": 1.2},
        )
    ax.set_title("D. Propagation to downstream conclusions")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/uncertainty_framework_figure.png",
    )
    parser.add_argument("--min-points", type=int, default=120)
    parser.add_argument("--missing-fraction", type=float, default=0.4)
    parser.add_argument("--bridge-samples", type=int, default=18)
    parser.add_argument("--scale-max-span", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    groups = read_trajectory_points(args.input)
    selected = select_trajectories(groups, args.min_points, max_trajectories=20)
    trajectory_id, records = selected[0]
    scale = estimate_global_bridge_scale(selected, max_span=args.scale_max_span)
    start, stop = centered_gap_indices(len(records), args.missing_fraction)
    complete = records_to_sphere(records)
    observed = np.vstack([complete[:start], complete[stop:]])
    removed = complete[start:stop]
    bridge = make_spherical_bridge(complete, start, stop)

    rng = np.random.default_rng(args.seed)
    samples = [
        brownian_bridge_sphere_sample(records, start, stop, scale, rng)
        for _ in range(args.bridge_samples)
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    plot_panel_a(axes[0, 0], complete, observed, removed)
    plot_panel_b(axes[0, 1], complete, observed, bridge)
    plot_panel_c(axes[1, 0], complete, observed, samples)
    plot_panel_d(axes[1, 1])

    route_axes = [axes[0, 0], axes[0, 1], axes[1, 0]]
    all_lon, all_lat = sphere_to_lonlat(complete)
    lon_pad = 0.08 * (all_lon.max() - all_lon.min())
    lat_pad = 0.08 * (all_lat.max() - all_lat.min())
    for ax in route_axes:
        ax.set_xlim(all_lon.min() - lon_pad, all_lon.max() + lon_pad)
        ax.set_ylim(all_lat.min() - lat_pad, all_lat.max() + lat_pad)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(alpha=0.25)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    handles_b, labels_b = axes[0, 1].get_legend_handles_labels()
    handles_c, labels_c = axes[1, 0].get_legend_handles_labels()
    legend = {}
    for handle, label in zip(handles + handles_b + handles_c, labels + labels_b + labels_c):
        legend[label] = handle
    fig.legend(legend.values(), legend.keys(), loc="lower center", ncol=3, frameon=False)
    fig.suptitle(
        f"Uncertainty-aware route comparison workflow\n"
        f"Example trajectory: {trajectory_id}; bridge scale={scale:.4g}"
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Trajectory: {trajectory_id}")
    print(f"Bridge scale: {scale:.8g}")
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
