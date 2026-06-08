"""Season-aware intensity sweep for controlled route perturbations."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from shape_perturbation import (
    add_local_detour,
    add_local_loop,
    compare,
    moving_average_curve,
)
from shape_perturbation_batch import read_trajectories
from timewarp_robustness import sample_curve_by_warp


METRICS = ["pointwise_l2", "raw_dtw", "srvf", "srvf_dtw"]
TIME_WARP_GAMMAS = [0.4, 2.5]
SMOOTHING_WINDOWS = [3, 7, 11, 15, 21]
DETOUR_AMPLITUDES = [0.01, 0.02, 0.04, 0.06, 0.08]
LOOP_AMPLITUDES = [0.01, 0.02, 0.04, 0.06, 0.08]


def variants_for_curve(curve, n_points):
    """Create time-warp controls and multi-intensity shape perturbations."""
    base = sample_curve_by_warp(curve, n_points, gamma=1.0)
    variants = []
    for gamma in TIME_WARP_GAMMAS:
        variants.append(
            (
                "time_warp",
                gamma,
                sample_curve_by_warp(curve, n_points, gamma=gamma),
            )
        )
    for window in SMOOTHING_WINDOWS:
        variants.append(("smoothed", window, moving_average_curve(base, window=window)))
    for amplitude in DETOUR_AMPLITUDES:
        variants.append(("local_detour", amplitude, add_local_detour(base, amplitude=amplitude)))
    for amplitude in LOOP_AMPLITUDES:
        variants.append(("local_loop", amplitude, add_local_loop(base, amplitude=amplitude)))
    return base, variants


def add_relative_responses(rows, eps=1e-12):
    """Normalize each metric by its route-specific strong time-warp baseline."""
    by_trajectory = OrderedDict()
    for row in rows:
        by_trajectory.setdefault(row["trajectory_id"], []).append(row)

    for trajectory_rows in by_trajectory.values():
        controls = [row for row in trajectory_rows if row["perturbation"] == "time_warp"]
        if len(controls) != len(TIME_WARP_GAMMAS):
            raise ValueError("each trajectory must have both time-warp controls")
        for metric in METRICS:
            baseline = float(np.mean([row[metric] for row in controls]))
            for row in trajectory_rows:
                row[f"{metric}_relative"] = row[metric] / max(baseline, eps)
    return rows


def run_sweep(trajectories, season, n_points):
    """Run the controlled intensity sweep across one season."""
    rows = []
    for trajectory_id, curve in trajectories:
        base, variants = variants_for_curve(curve, n_points)
        for perturbation, intensity, variant in variants:
            rows.append(
                {
                    "season": season,
                    "trajectory_id": trajectory_id,
                    "perturbation": perturbation,
                    "intensity": intensity,
                    **compare(base, variant),
                }
            )
    return add_relative_responses(rows)


def summarize(rows):
    """Summarize absolute and relative responses by season and intensity."""
    grouped = OrderedDict()
    for row in rows:
        key = (row["season"], row["perturbation"], row["intensity"])
        grouped.setdefault(key, []).append(row)

    summary = []
    for (season, perturbation, intensity), group_rows in grouped.items():
        out = {
            "season": season,
            "perturbation": perturbation,
            "intensity": intensity,
            "n_trajectories": len(group_rows),
        }
        for metric in METRICS:
            for suffix in ["", "_relative"]:
                values = np.asarray([row[f"{metric}{suffix}"] for row in group_rows], dtype=float)
                out[f"{metric}{suffix}_mean"] = float(np.mean(values))
                out[f"{metric}{suffix}_std"] = float(np.std(values, ddof=0))
                out[f"{metric}{suffix}_median"] = float(np.median(values))
        summary.append(out)
    return summary


def write_rows(path, rows):
    """Write trajectory-level sweep results."""
    fieldnames = ["season", "trajectory_id", "perturbation", "intensity"]
    fieldnames += METRICS
    fieldnames += [f"{metric}_relative" for metric in METRICS]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path, rows):
    """Write season-level sweep summaries."""
    fieldnames = ["season", "perturbation", "intensity", "n_trajectories"]
    for metric in METRICS:
        for suffix in ["", "_relative"]:
            fieldnames += [
                f"{metric}{suffix}_mean",
                f"{metric}{suffix}_std",
                f"{metric}{suffix}_median",
            ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--season", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--n-points", type=int, default=80)
    parser.add_argument("--min-points", type=int, default=80)
    parser.add_argument("--max-trajectories", type=int)
    args = parser.parse_args()

    trajectories = read_trajectories(
        args.input,
        max_trajectories=args.max_trajectories,
        min_points=args.min_points,
    )
    rows = run_sweep(trajectories, season=args.season, n_points=args.n_points)
    write_rows(args.output, rows)
    write_summary(args.summary, summarize(rows))
    print(f"Season: {args.season}")
    print(f"Trajectories: {len(trajectories)}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.summary}")


if __name__ == "__main__":
    main()
