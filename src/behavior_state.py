"""Classify GPS points into behavioral states for movement-aware gap reconstruction.

States: 'resting', 'foraging', 'directed' — based on speed and turning angle.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from geometry import great_circle_distance_km, latlon_to_unit_sphere


def _parse_isotime(timestamp_str: str) -> datetime:
    """Parse an ISO-8601 timestamp string to a timezone-aware datetime."""
    ts = timestamp_str.strip()
    # Handle trailing Z (UTC indicator)
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def compute_speeds_and_turn_angles(
    records: list[tuple[str, float, float]],
) -> tuple[np.ndarray, np.ndarray]:
    """Compute per-segment speeds and per-interior-point turning angles.

    Parameters
    ----------
    records : list of (timestamp, latitude, longitude) tuples.

    Returns
    -------
    speeds : np.ndarray of shape (n-1,)
        Speed in km/h for each segment between consecutive points.
    turn_angles : np.ndarray of shape (n-2,)
        Turning angle in degrees at each interior point (angle between
        incoming and outgoing displacement vectors on the unit sphere).
    """
    n = len(records)
    if n < 2:
        return np.array([], dtype=float), np.array([], dtype=float)

    # Parse all timestamps
    times = np.array(
        [_parse_isotime(rec[0]).timestamp() for rec in records], dtype=float
    )
    lats = np.array([rec[1] for rec in records], dtype=float)
    lons = np.array([rec[2] for rec in records], dtype=float)

    # Unit sphere positions
    sphere = latlon_to_unit_sphere(lats, lons)

    # Segment speeds (km/h)
    time_diffs_hours = np.diff(times) / 3600.0
    # Handle zero or negative time diffs
    time_diffs_hours = np.maximum(time_diffs_hours, 1e-6)
    dists_km = great_circle_distance_km(sphere[:-1], sphere[1:])
    speeds = dists_km / time_diffs_hours

    # Turning angles at interior points (degrees)
    if n < 3:
        return speeds, np.array([], dtype=float)

    # Displacement vectors in R^3 (not tangent plane — sphere embedding)
    displacements = np.diff(sphere, axis=0)  # shape (n-1, 3)
    # Normalize each displacement
    disp_norms = np.linalg.norm(displacements, axis=1, keepdims=True)
    disp_unit = displacements / np.maximum(disp_norms, 1e-12)

    # Angle between consecutive unit displacement vectors
    dots = np.sum(disp_unit[:-1] * disp_unit[1:], axis=1)
    dots = np.clip(dots, -1.0, 1.0)
    turn_angles = np.rad2deg(np.arccos(dots))

    return speeds, turn_angles


def classify_behavioral_states(
    records: list[tuple[str, float, float]],
    speed_resting_threshold: float = 5.0,
    speed_directed_threshold: float = 30.0,
    turning_directed_max: float = 30.0,
    min_points: int = 3,
) -> list[str]:
    """Label each GPS point as 'resting', 'foraging', or 'directed'.

    Classification rules (applied per point):
    - speed < speed_resting_threshold km/h  → 'resting'
    - speed > speed_directed_threshold km/h AND turning angle < turning_directed_max
                                            → 'directed'
    - otherwise                             → 'foraging'

    Per-point assignment uses segment speed after each point and turning
    angle at each interior point. Edge points use their sole neighboring
    segment's speed; the first and last points have no turning angle and
    are classified by speed alone.

    Parameters
    ----------
    records : list of (timestamp, latitude, longitude) tuples.
    speed_resting_threshold : float
        km/h below which a point is classified as resting.
    speed_directed_threshold : float
        km/h above which (with low turning angle) a point is directed.
    turning_directed_max : float
        Maximum turning angle (degrees) for directed classification.
    min_points : int
        Minimum records required; fewer than this returns all 'foraging'.

    Returns
    -------
    list[str]
        State labels, same length as records.
    """
    n = len(records)
    if n < min_points:
        return ["foraging"] * n

    speeds, turn_angles = compute_speeds_and_turn_angles(records)

    # Per-point speed: point i gets the speed of the segment starting at i
    # (or ending at i for the last point)
    point_speeds = np.empty(n, dtype=float)
    point_speeds[:-1] = speeds  # segment after each of first n-1 points
    point_speeds[-1] = speeds[-1]  # last point gets last segment speed

    # Per-point turning angle: interior points get turn_angles[i-1]
    # Edge points: no turning angle → cannot be directed (speed-only classification)
    has_turn = np.zeros(n, dtype=bool)
    point_turns = np.zeros(n, dtype=float)
    if n >= 3:
        has_turn[1:-1] = True
        point_turns[1:-1] = turn_angles

    labels = []
    for i in range(n):
        speed = point_speeds[i]
        if speed < speed_resting_threshold:
            labels.append("resting")
        elif (
            has_turn[i]
            and speed > speed_directed_threshold
            and point_turns[i] < turning_directed_max
        ):
            labels.append("directed")
        elif not has_turn[i] and speed > speed_directed_threshold:
            # Edge point with high speed — default to directed
            labels.append("directed")
        else:
            labels.append("foraging")

    return labels


def state_transition_counts(
    labels: list[str],
) -> dict[tuple[str, str], int]:
    """Count transitions between consecutive behavioral states.

    Parameters
    ----------
    labels : list of state label strings.

    Returns
    -------
    dict mapping (from_state, to_state) -> transition count.
    """
    counts: dict[tuple[str, str], int] = {}
    for a, b in zip(labels[:-1], labels[1:]):
        key = (a, b)
        counts[key] = counts.get(key, 0) + 1
    return counts


def state_label_series(
    records: list[tuple[str, float, float]],
    **kwargs,
) -> tuple[list[str], dict]:
    """Classify states and return labels with summary statistics.

    Parameters
    ----------
    records : list of (timestamp, latitude, longitude) tuples.
    **kwargs : passed to classify_behavioral_states.

    Returns
    -------
    labels : list[str]
    summary : dict with keys:
        n_resting, n_foraging, n_directed, n_total,
        frac_resting, frac_foraging, frac_directed,
        transitions: dict of (from, to) -> count
    """
    labels = classify_behavioral_states(records, **kwargs)
    n = len(labels)
    counts = {
        "resting": labels.count("resting"),
        "foraging": labels.count("foraging"),
        "directed": labels.count("directed"),
    }
    summary = {
        "n_total": n,
        "n_resting": counts["resting"],
        "n_foraging": counts["foraging"],
        "n_directed": counts["directed"],
        "frac_resting": counts["resting"] / n if n > 0 else 0.0,
        "frac_foraging": counts["foraging"] / n if n > 0 else 0.0,
        "frac_directed": counts["directed"] / n if n > 0 else 0.0,
        "transitions": state_transition_counts(labels),
    }
    return labels, summary
