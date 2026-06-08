"""Run the core reproducible analysis pipeline.

This script assumes the raw archive has already been downloaded. It regenerates
the main processed data products and figures used by the current manuscript.
"""

from __future__ import annotations

import subprocess
import sys


def run(command):
    """Run a command and stop on failure."""
    print(f"\n$ {' '.join(command)}")
    subprocess.run(command, check=True)


def main():
    py = sys.executable
    commands = [
        [py, "src/standardize_dwca.py"],
        [py, "src/segment_migration.py"],
        [py, "src/split_segments_by_season.py"],
        [py, "src/trim_transit_segments.py"],
        [
            py,
            "src/split_segments_by_season.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_segments.csv",
            "--output-dir",
            "data/processed",
            "--prefix",
            "lbbg_zeebrugge_transit",
        ],
        [
            py,
            "src/timewarp_robustness_batch.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
            "--output",
            "data/processed/timewarp_robustness_transit_batch.csv",
            "--summary",
            "data/processed/timewarp_robustness_transit_batch_summary.csv",
            "--max-trajectories",
            "20",
            "--min-points",
            "80",
            "--n-points",
            "100",
        ],
        [
            py,
            "src/plot_timewarp_robustness_batch.py",
            "--input",
            "data/processed/timewarp_robustness_transit_batch_summary.csv",
            "--output",
            "figures/timewarp_robustness_transit_batch.png",
        ],
        [
            py,
            "src/shape_perturbation_batch.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
            "--output",
            "data/processed/shape_perturbation_transit_batch.csv",
            "--summary",
            "data/processed/shape_perturbation_transit_batch_summary.csv",
            "--max-trajectories",
            "20",
            "--min-points",
            "80",
            "--n-points",
            "100",
        ],
        [
            py,
            "src/plot_shape_perturbation_batch.py",
            "--input",
            "data/processed/shape_perturbation_transit_batch_summary.csv",
            "--output",
            "figures/shape_perturbation_transit_batch.png",
        ],
        [
            py,
            "src/shape_perturbation_sweep.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
            "--season",
            "spring",
            "--output",
            "data/processed/shape_perturbation_sweep_spring.csv",
            "--summary",
            "data/processed/shape_perturbation_sweep_spring_summary.csv",
            "--n-points",
            "80",
            "--min-points",
            "80",
        ],
        [
            py,
            "src/shape_perturbation_sweep.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv",
            "--season",
            "autumn",
            "--output",
            "data/processed/shape_perturbation_sweep_autumn.csv",
            "--summary",
            "data/processed/shape_perturbation_sweep_autumn_summary.csv",
            "--n-points",
            "80",
            "--min-points",
            "80",
        ],
        [
            py,
            "src/plot_shape_perturbation_sweep.py",
            "--input",
            "data/processed/shape_perturbation_sweep_spring_summary.csv",
            "data/processed/shape_perturbation_sweep_autumn_summary.csv",
            "--output",
            "figures/shape_perturbation_sweep_relative.png",
        ],
        [
            py,
            "src/prototype_distances.py",
            "--input",
            "data/processed/lbbg_zeebrugge_transit_segments.csv",
            "--id-column",
            "trajectory_id",
            "--output-dir",
            "data/processed/prototype_50_transit_distances",
            "--max-individuals",
            "50",
            "--n-points",
            "100",
            "--min-points",
            "20",
        ],
        [
            py,
            "src/anomaly_scores.py",
            "--distance-matrix",
            "data/processed/prototype_50_transit_distances/srvf_dtw_distances.csv",
            "--output",
            "data/processed/prototype_50_transit_distances/srvf_dtw_anomaly_scores.csv",
        ],
        [
            py,
            "src/plot_anomaly_routes.py",
            "--scores",
            "data/processed/prototype_50_transit_distances/srvf_dtw_anomaly_scores.csv",
            "--segments",
            "data/processed/lbbg_zeebrugge_transit_segments.csv",
            "--output",
            "figures/top_anomaly_transit_coastline.png",
        ],
        [
            py,
            "src/download_naturalearth.py",
        ],
        [
            py,
            "src/plot_route_map.py",
            "--segments",
            "data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
            "--assignments",
            "data/processed/no_assignments.csv",
            "--output",
            "figures/route_map_transit_coastline.png",
            "--max-trajectories",
            "50",
            "--title",
            "Candidate Spring Transit Route Segments",
        ],
    ]

    for command in commands:
        run(command)


if __name__ == "__main__":
    main()
