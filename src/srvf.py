"""Discrete SRVF transforms and distances for trajectory curves."""

from __future__ import annotations

import numpy as np


def discrete_velocity(curve):
    """Compute finite-difference velocities for a sampled curve."""
    arr = np.asarray(curve, dtype=float)
    if arr.ndim != 2:
        raise ValueError("curve must have shape (n_samples, n_dimensions)")
    if len(arr) < 2:
        raise ValueError("at least two samples are required")
    return np.diff(arr, axis=0)


def srvf_transform(curve, eps=1e-12):
    """Compute a discrete square root velocity function representation.

    For a continuous curve f(t), SRVF is q(t) = f'(t) / sqrt(||f'(t)||).
    This function applies that formula to finite-difference velocities.
    """
    velocity = discrete_velocity(curve)
    speeds = np.linalg.norm(velocity, axis=1, keepdims=True)
    return velocity / np.sqrt(np.maximum(speeds, eps))


def srvf_distance(curve_a, curve_b):
    """Compute the L2 distance between two discrete SRVF representations.

    The two input curves must be resampled to the same number of points before
    calling this function.
    """
    q_a = srvf_transform(curve_a)
    q_b = srvf_transform(curve_b)
    if q_a.shape != q_b.shape:
        raise ValueError("curves must produce SRVFs with the same shape")
    return float(np.sqrt(np.sum((q_a - q_b) ** 2)))


def dtw_sequence_distance(sequence_a, sequence_b):
    """Dynamic time warping distance between two vector-valued sequences.

    The local cost is Euclidean distance between sequence elements. The final
    score is normalized by the warping path length scale so distances remain
    comparable across moderate sequence lengths.
    """
    a = np.asarray(sequence_a, dtype=float)
    b = np.asarray(sequence_b, dtype=float)
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("sequences must have shape (n_samples, n_dimensions)")
    if a.shape[1] != b.shape[1]:
        raise ValueError("sequences must have the same dimensionality")

    n = len(a)
    m = len(b)
    costs = np.full((n + 1, m + 1), np.inf, dtype=float)
    costs[0, 0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            local = np.linalg.norm(a[i - 1] - b[j - 1])
            costs[i, j] = local + min(
                costs[i - 1, j],
                costs[i, j - 1],
                costs[i - 1, j - 1],
            )

    return float(costs[n, m] / (n + m))


def srvf_dtw_distance(curve_a, curve_b):
    """DTW-aligned distance between two discrete SRVF sequences."""
    q_a = srvf_transform(curve_a)
    q_b = srvf_transform(curve_b)
    return dtw_sequence_distance(q_a, q_b)


def pairwise_srvf_distance(curves):
    """Compute a symmetric pairwise SRVF distance matrix."""
    n = len(curves)
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = srvf_distance(curves[i], curves[j])
            distances[i, j] = d
            distances[j, i] = d
    return distances


def pairwise_srvf_dtw_distance(curves):
    """Compute a symmetric pairwise DTW-aligned SRVF distance matrix."""
    n = len(curves)
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = srvf_dtw_distance(curves[i], curves[j])
            distances[i, j] = d
            distances[j, i] = d
    return distances


def pointwise_l2_distance(curve_a, curve_b):
    """Baseline pointwise Euclidean distance for aligned curves."""
    a = np.asarray(curve_a, dtype=float)
    b = np.asarray(curve_b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("curves must have the same shape")
    return float(np.sqrt(np.sum((a - b) ** 2)))


def raw_dtw_distance(curve_a, curve_b):
    """DTW distance directly on curve coordinates."""
    return dtw_sequence_distance(curve_a, curve_b)


def pairwise_pointwise_l2_distance(curves):
    """Compute a symmetric pairwise pointwise-L2 distance matrix."""
    n = len(curves)
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = pointwise_l2_distance(curves[i], curves[j])
            distances[i, j] = d
            distances[j, i] = d
    return distances


def pairwise_raw_dtw_distance(curves):
    """Compute a symmetric pairwise raw-coordinate DTW distance matrix."""
    n = len(curves)
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = raw_dtw_distance(curves[i], curves[j])
            distances[i, j] = d
            distances[j, i] = d
    return distances
