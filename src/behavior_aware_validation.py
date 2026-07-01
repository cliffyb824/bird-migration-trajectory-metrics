"""Validate global BB + conformal calibration against withheld segments.

Compares three approaches:
  (a) global BB with empirical radius inflation (old method)
  (b) global BB with conformal calibration (new method)
  (c) behavior-conditioned scale estimation (descriptive diagnostic)

Key contribution: conformal calibration provides finite-sample,
distribution-free coverage guarantees for trajectory uncertainty
envelopes — replacing ad-hoc empirical inflation.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from brownian_bridge_gap_reconstruction import (
    brownian_bridge_sphere_sample,
    estimate_global_bridge_scale,
    estimate_state_conditioned_scales,
)
from conformal_calibration import (
    calibrate_radii,
    empirical_coverage,
    split_conformal_calibrate,
)
from gap_reconstruction_baseline import (
    records_to_sphere,
    sample_gap_indices,
)
from geometry import great_circle_distance_km, normalize_vectors, spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories


# ---------------------------------------------------------------------------
# Core validation functions
# ---------------------------------------------------------------------------


def bridge_points(records, start, stop):
    """Return deterministic spherical-bridge points for the withheld interval."""
    points = records_to_sphere(records)
    gap_size = stop - start
    fractions = np.linspace(0.0, 1.0, gap_size + 2)[1:-1]
    return spherical_linear_interpolate(points[start - 1], points[stop], fractions)


def sample_center_and_radius(sample_points, quantile):
    """Estimate pointwise sample centers and uncertainty radii on the sphere."""
    samples = np.asarray(sample_points, dtype=float)
    centers = normalize_vectors(np.mean(samples, axis=0))
    sample_distances = great_circle_distance_km(samples, centers[None, :, :])
    radii = np.quantile(sample_distances, quantile, axis=0)
    return centers, radii


def validate_one_gap_global_bb(
    records,
    start,
    stop,
    scale,
    n_samples,
    quantile,
    rng,
):
    """Compute validation diagnostics for one gap using global BB.

    Returns both per-gap summary statistics and raw pointwise data
    needed for conformal calibration.
    """
    true_points = records_to_sphere(records)[start:stop]
    deterministic = bridge_points(records, start, stop)
    det_errors = great_circle_distance_km(deterministic, true_points)

    # Global BB samples
    samples = [
        brownian_bridge_sphere_sample(records, start, stop, scale, rng)[start:stop]
        for _ in range(n_samples)
    ]
    sample_array = np.asarray(samples, dtype=float)
    sample_errors = great_circle_distance_km(
        sample_array, true_points[None, :, :]
    )
    centers, radii = sample_center_and_radius(sample_array, quantile)
    center_errors = great_circle_distance_km(centers, true_points)

    # Empirical coverage
    raw_coverage = empirical_coverage(center_errors, radii)

    # Empirical radius inflation (old method)
    ratios = center_errors / np.maximum(radii, 1e-9)
    radius_inflation = float(np.quantile(ratios, quantile))
    calibrated_radii_empirical = radii * radius_inflation
    empirical_calibrated_coverage = empirical_coverage(
        center_errors, calibrated_radii_empirical
    )

    return {
        "gap_points": stop - start,
        "deterministic_mean_error_km": float(np.mean(det_errors)),
        "sample_mean_error_km": float(np.mean(sample_errors)),
        "sample_center_mean_error_km": float(np.mean(center_errors)),
        "oracle_sample_mean_error_km": float(np.mean(np.min(sample_errors, axis=0))),
        "coverage_raw": raw_coverage,
        "median_radius_km": float(np.median(radii)),
        # Old method: empirical inflation
        "radius_inflation": radius_inflation,
        "coverage_empirical_cal": empirical_calibrated_coverage,
        "median_radius_empirical_cal_km": float(np.median(calibrated_radii_empirical)),
        # Raw pointwise data for conformal calibration
        "_center_errors": center_errors,
        "_radii": radii,
    }


def run_global_bb_conformal_validation(season, input_path, args, rng):
    """Run global BB validation with conformal calibration.

    1. Estimate global scale on all trajectories.
    2. Phase 1 (calibration): Sample gaps → collect pointwise errors and radii.
    3. Phase 2: Split-conformal → q_hat from calibration set.
    4. Phase 3 (evaluation): Sample new gaps → compare raw, empirical, conformal.
    """
    groups = read_trajectory_points(input_path)
    selected = select_trajectories(groups, args.min_points, args.max_trajectories)

    # Scale estimation
    global_scale = estimate_global_bridge_scale(selected, max_span=args.scale_max_span)
    state_scales = estimate_state_conditioned_scales(
        selected, max_span=args.scale_max_span
    )

    print(f"[{season}] Global scale: {global_scale:.6g}")
    print(
        f"[{season}] State scales: "
        f"resting={state_scales['resting']:.6g}, "
        f"foraging={state_scales['foraging']:.6g}, "
        f"directed={state_scales['directed']:.6g}"
    )

    # -------------------------------------------------------------------
    # Phase 1: Sample calibration gaps — collect pointwise data
    # -------------------------------------------------------------------
    cal_pointwise_errors = []
    cal_pointwise_radii = []

    for missing_fraction in args.missing_fractions:
        for repeat in range(1, args.cal_repeats + 1):
            for trajectory_id, records in selected:
                start, stop = sample_gap_indices(len(records), missing_fraction, rng)
                result = validate_one_gap_global_bb(
                    records, start, stop, global_scale,
                    args.bridge_samples, args.quantile, rng,
                )
                cal_pointwise_errors.extend(result["_center_errors"].tolist())
                cal_pointwise_radii.extend(result["_radii"].tolist())

    # -------------------------------------------------------------------
    # Phase 2: Conformal calibration
    # -------------------------------------------------------------------
    cal_errors = np.array(cal_pointwise_errors)
    cal_radii = np.array(cal_pointwise_radii)

    cal_result = split_conformal_calibrate(
        cal_errors, cal_radii, alpha=args.alpha, rng=rng
    )
    q_hat = cal_result["q_hat"]
    print(
        f"[{season}] Conformal q_hat = {q_hat:.3f} "
        f"(n_train={cal_result['n_train']}, n_cal={cal_result['n_cal']}, "
        f"total pointwise={len(cal_errors)}, alpha={args.alpha})"
    )

    # -------------------------------------------------------------------
    # Phase 3: Evaluation on new independent gaps
    # -------------------------------------------------------------------
    rows = []
    for missing_fraction in args.missing_fractions:
        for repeat in range(1, args.eval_repeats + 1):
            for trajectory_id, records in selected:
                start, stop = sample_gap_indices(len(records), missing_fraction, rng)
                result = validate_one_gap_global_bb(
                    records, start, stop, global_scale,
                    args.bridge_samples, args.quantile, rng,
                )
                center_errors = result.pop("_center_errors")
                radii = result.pop("_radii")

                # Apply conformal calibration
                conformal_radii = calibrate_radii(radii, q_hat)
                conformal_coverage = empirical_coverage(center_errors, conformal_radii)

                rows.append(
                    {
                        "season": season,
                        "missing_fraction": missing_fraction,
                        "repeat": repeat,
                        "trajectory_id": trajectory_id,
                        "phase": "evaluation",
                        "global_scale": global_scale,
                        "resting_scale": state_scales["resting"],
                        "foraging_scale": state_scales["foraging"],
                        "directed_scale": state_scales["directed"],
                        "conformal_q_hat": q_hat,
                        # Old method
                        "coverage_raw": result["coverage_raw"],
                        "median_radius_km": result["median_radius_km"],
                        "radius_inflation": result["radius_inflation"],
                        "coverage_empirical_cal": result["coverage_empirical_cal"],
                        "median_radius_empirical_cal_km": result[
                            "median_radius_empirical_cal_km"
                        ],
                        # New method (conformal)
                        "coverage_conformal": conformal_coverage,
                        "median_radius_conformal_km": float(
                            np.median(conformal_radii)
                        ),
                        # Other diagnostics
                        "gap_points": result["gap_points"],
                        "deterministic_mean_error_km": result[
                            "deterministic_mean_error_km"
                        ],
                        "sample_mean_error_km": result["sample_mean_error_km"],
                        "sample_center_mean_error_km": result[
                            "sample_center_mean_error_km"
                        ],
                        "oracle_sample_mean_error_km": result[
                            "oracle_sample_mean_error_km"
                        ],
                    }
                )

    return rows, {
        "season": season,
        "global_scale": global_scale,
        "state_scales": state_scales,
        "q_hat": q_hat,
        "n_cal": cal_result["n_cal"],
        "n_train": cal_result["n_train"],
        "n_pointwise": len(cal_errors),
        "alpha": args.alpha,
    }


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def write_rows(path, rows):
    """Write per-gap combined validation rows."""
    fieldnames = [
        "season",
        "missing_fraction",
        "repeat",
        "trajectory_id",
        "phase",
        "gap_points",
        "global_scale",
        "resting_scale",
        "foraging_scale",
        "directed_scale",
        "deterministic_mean_error_km",
        "sample_mean_error_km",
        "sample_center_mean_error_km",
        "oracle_sample_mean_error_km",
        # Raw
        "coverage_raw",
        "median_radius_km",
        # Old: empirical inflation
        "radius_inflation",
        "coverage_empirical_cal",
        "median_radius_empirical_cal_km",
        # New: conformal calibration
        "conformal_q_hat",
        "coverage_conformal",
        "median_radius_conformal_km",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize_rows(rows):
    """Summarize validation by season, missing fraction, and method."""
    eval_rows = [r for r in rows if r["phase"] == "evaluation"]

    grouped = {}
    for row in eval_rows:
        key = (row["season"], row["missing_fraction"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (season, fraction), group in grouped.items():
        summary = {
            "season": season,
            "missing_fraction": fraction,
            "n_gaps": len(group),
            "q_hat": float(np.mean([r["conformal_q_hat"] for r in group])),
            "global_scale": float(np.mean([r["global_scale"] for r in group])),
            "resting_scale": float(np.mean([r["resting_scale"] for r in group])),
            "foraging_scale": float(np.mean([r["foraging_scale"] for r in group])),
            "directed_scale": float(np.mean([r["directed_scale"] for r in group])),
        }

        metrics = [
            # Raw
            ("coverage_raw_mean", "coverage_raw"),
            ("median_radius_raw_mean", "median_radius_km"),
            # Empirical
            ("radius_inflation_mean", "radius_inflation"),
            ("coverage_empirical_cal_mean", "coverage_empirical_cal"),
            ("median_radius_empirical_cal_mean", "median_radius_empirical_cal_km"),
            # Conformal
            ("coverage_conformal_mean", "coverage_conformal"),
            ("median_radius_conformal_mean", "median_radius_conformal_km"),
            # Error
            ("center_error_mean", "sample_center_mean_error_km"),
        ]
        for stat_name, field_name in metrics:
            values = np.asarray([r[field_name] for r in group], dtype=float)
            summary[stat_name] = float(np.mean(values))
            summary[stat_name.replace("_mean", "_std")] = (
                float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            )

        summaries.append(summary)
    return summaries


def write_summaries(path, summaries):
    """Write summarized validation diagnostics."""
    fieldnames = [
        "season",
        "missing_fraction",
        "n_gaps",
        "q_hat",
        "global_scale",
        "resting_scale",
        "foraging_scale",
        "directed_scale",
        "coverage_raw_mean",
        "coverage_raw_std",
        "median_radius_raw_mean",
        "median_radius_raw_std",
        "radius_inflation_mean",
        "radius_inflation_std",
        "coverage_empirical_cal_mean",
        "coverage_empirical_cal_std",
        "median_radius_empirical_cal_mean",
        "median_radius_empirical_cal_std",
        "coverage_conformal_mean",
        "coverage_conformal_std",
        "median_radius_conformal_mean",
        "median_radius_conformal_std",
        "center_error_mean",
        "center_error_std",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summaries)


def write_cal_info(path, cal_infos):
    """Write calibration metadata (q_hat, scales) to a sidecar CSV."""
    fieldnames = [
        "season",
        "global_scale",
        "resting_scale",
        "foraging_scale",
        "directed_scale",
        "q_hat",
        "n_cal",
        "n_train",
        "n_pointwise",
        "alpha",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for info in cal_infos:
            writer.writerow(
                {
                    "season": info["season"],
                    "global_scale": info["global_scale"],
                    "resting_scale": info["state_scales"]["resting"],
                    "foraging_scale": info["state_scales"]["foraging"],
                    "directed_scale": info["state_scales"]["directed"],
                    "q_hat": info["q_hat"],
                    "n_cal": info["n_cal"],
                    "n_train": info["n_train"],
                    "n_pointwise": info["n_pointwise"],
                    "alpha": info["alpha"],
                }
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Global BB + conformal calibration validation"
    )
    parser.add_argument(
        "--spring-input",
        default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--autumn-input",
        default="data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/behavior_aware_validation.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/behavior_aware_validation_summary.csv",
    )
    parser.add_argument(
        "--cal-info-output",
        default="data/processed/behavior_aware_calibration_info.csv",
    )
    parser.add_argument("--max-trajectories", type=int, default=30)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument(
        "--missing-fractions", nargs="+", type=float, default=[0.2, 0.4, 0.6]
    )
    parser.add_argument("--cal-repeats", type=int, default=3,
                        help="Repeats for calibration gap sampling")
    parser.add_argument("--eval-repeats", type=int, default=5,
                        help="Repeats for evaluation gap sampling")
    parser.add_argument("--bridge-samples", type=int, default=24)
    parser.add_argument("--scale-max-span", type=int, default=6)
    parser.add_argument("--alpha", type=float, default=0.10,
                        help="Target miscoverage rate for conformal calibration")
    parser.add_argument("--quantile", type=float, default=0.90,
                        help="Envelope quantile")
    parser.add_argument("--seed", type=int, default=20260701)
    parser.add_argument("--seasons", nargs="+", default=["spring", "autumn"],
                        help="Seasons to process")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    all_rows = []
    cal_infos = []

    season_inputs = {
        "spring": args.spring_input,
        "autumn": args.autumn_input,
    }

    for season in args.seasons:
        if season not in season_inputs:
            print(f"Skipping unknown season: {season}")
            continue
        input_path = season_inputs[season]
        if not Path(input_path).exists():
            print(f"Input not found: {input_path}, skipping {season}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {season}")
        print(f"{'='*60}")
        rows, cal_info = run_global_bb_conformal_validation(
            season, input_path, args, rng
        )
        all_rows.extend(rows)
        cal_infos.append(cal_info)

    # Write outputs
    for path in [args.output, args.summary_output, args.cal_info_output]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    write_rows(args.output, all_rows)
    print(f"\nWrote: {args.output} ({len(all_rows)} rows)")

    summaries = summarize_rows(all_rows)
    write_summaries(args.summary_output, summaries)
    print(f"Wrote: {args.summary_output} ({len(summaries)} rows)")

    write_cal_info(args.cal_info_output, cal_infos)
    print(f"Wrote: {args.cal_info_output}")

    # Print summary table
    print("\n" + "=" * 100)
    print("SUMMARY: Global BB — Raw vs Empirical Calibration vs Conformal Calibration")
    print("=" * 100)
    header = (
        f"{'Season':<8} {'Frac':<6} {'RawCov':<8} {'EmpCalCov':<10} {'ConfCov':<9} "
        f"{'Infl':<7} {'q_hat':<8} {'RawRad':<8} {'ConfRad':<8}"
    )
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(
            f"{s['season']:<8} {s['missing_fraction']:<6.0%} "
            f"{s['coverage_raw_mean']:<8.3f} "
            f"{s['coverage_empirical_cal_mean']:<10.3f} "
            f"{s['coverage_conformal_mean']:<9.3f} "
            f"{s['radius_inflation_mean']:<7.1f} "
            f"{s['q_hat']:<8.2f} "
            f"{s['median_radius_raw_mean']:<8.1f} "
            f"{s['median_radius_conformal_mean']:<8.1f}"
        )


if __name__ == "__main__":
    main()
