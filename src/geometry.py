"""Geometry utilities for spherical bird trajectory analysis."""

from __future__ import annotations

import numpy as np


EARTH_RADIUS_KM = 6371.0088


def latlon_to_unit_sphere(latitude_deg, longitude_deg):
    """Convert latitude-longitude coordinates to 3D unit-sphere coordinates.

    Parameters
    ----------
    latitude_deg, longitude_deg:
        Scalars or arrays in degrees.

    Returns
    -------
    numpy.ndarray
        Array with shape (..., 3), containing x, y, z unit vectors.
    """
    lat = np.deg2rad(np.asarray(latitude_deg, dtype=float))
    lon = np.deg2rad(np.asarray(longitude_deg, dtype=float))

    cos_lat = np.cos(lat)
    x = cos_lat * np.cos(lon)
    y = cos_lat * np.sin(lon)
    z = np.sin(lat)
    return np.stack([x, y, z], axis=-1)


def great_circle_distance_km(points_a, points_b, radius_km=EARTH_RADIUS_KM):
    """Compute great-circle distance between unit-sphere points.

    Parameters
    ----------
    points_a, points_b:
        Arrays with shape (..., 3).
    radius_km:
        Sphere radius in kilometers.

    Returns
    -------
    numpy.ndarray
        Great-circle distances in kilometers.
    """
    a = np.asarray(points_a, dtype=float)
    b = np.asarray(points_b, dtype=float)
    dots = np.sum(a * b, axis=-1)
    angles = np.arccos(np.clip(dots, -1.0, 1.0))
    return radius_km * angles


def normalize_vectors(vectors, eps=1e-12):
    """Normalize vectors along the last axis."""
    arr = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(arr, axis=-1, keepdims=True)
    return arr / np.maximum(norms, eps)


def spherical_linear_interpolate(point_a, point_b, fractions, eps=1e-12):
    """Interpolate between two unit-sphere points along the great-circle arc."""
    a = normalize_vectors(np.asarray(point_a, dtype=float))
    b = normalize_vectors(np.asarray(point_b, dtype=float))
    t = np.asarray(fractions, dtype=float)
    dot = float(np.clip(np.sum(a * b), -1.0, 1.0))
    angle = np.arccos(dot)
    if angle < eps:
        return normalize_vectors((1.0 - t[:, None]) * a + t[:, None] * b)
    sin_angle = np.sin(angle)
    weights_a = np.sin((1.0 - t) * angle) / sin_angle
    weights_b = np.sin(t * angle) / sin_angle
    return normalize_vectors(weights_a[:, None] * a + weights_b[:, None] * b)


def resample_curve(points, n_points):
    """Resample a polyline to a fixed number of points by arc length.

    This is a Euclidean chord-length resampling in the current coordinate
    system. For unit-sphere trajectories this is adequate for the first
    prototype; later versions can replace it with geodesic interpolation.
    """
    curve = np.asarray(points, dtype=float)
    if curve.ndim != 2:
        raise ValueError("points must have shape (n_samples, n_dimensions)")
    if len(curve) < 2:
        raise ValueError("at least two points are required")
    if n_points < 2:
        raise ValueError("n_points must be at least 2")

    segment_lengths = np.linalg.norm(np.diff(curve, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(segment_lengths)])

    if cumulative[-1] == 0:
        return np.repeat(curve[:1], n_points, axis=0)

    target = np.linspace(0.0, cumulative[-1], n_points)
    out = np.empty((n_points, curve.shape[1]), dtype=float)
    for dim in range(curve.shape[1]):
        out[:, dim] = np.interp(target, cumulative, curve[:, dim])
    return out
