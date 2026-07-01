"""Conformal calibration for trajectory envelope uncertainty quantification.

Provides split-conformal prediction that guarantees finite-sample,
distribution-free marginal coverage: P(e_new <= q_hat * r_new) >= 1 - alpha.
"""

from __future__ import annotations

import numpy as np


def compute_nonconformity_scores(
    center_errors: np.ndarray,
    radii: np.ndarray,
    epsilon: float = 1e-9,
) -> np.ndarray:
    """Compute nonconformity scores s_i = e_i / (r_i + epsilon).

    A score > 1 means the true point lies outside the envelope.
    A score of 0.5 means the error is half the envelope radius.

    Parameters
    ----------
    center_errors : array-like
        Great-circle distances between true points and BB sample centers.
        Shape (n,) or (n_gaps, n_points).
    radii : array-like, same shape as center_errors
        Pointwise BB envelope radii (e.g., 90% quantile radius).

    Returns
    -------
    scores : np.ndarray, same shape as inputs
        Nonconformity scores.
    """
    errors = np.asarray(center_errors, dtype=float)
    rads = np.asarray(radii, dtype=float)
    return errors / np.maximum(rads, epsilon)


def conformal_quantile(
    scores: np.ndarray,
    alpha: float = 0.10,
) -> float:
    """Compute the split-conformal quantile q_hat.

    q_hat = the ceil((n+1)*(1-alpha))-th order statistic of the calibration
    scores. For a finite calibration set, this provides the guarantee:
        P(e_new <= q_hat * r_new) >= 1 - alpha
    where the probability is over the random calibration split.

    Parameters
    ----------
    scores : np.ndarray, shape (n_cal,)
        Nonconformity scores from the calibration set. Must be 1D.
    alpha : float
        Target miscoverage rate (default 0.10 for 90% coverage).

    Returns
    -------
    float
        Conformal quantile multiplier q_hat.
    """
    scores = np.asarray(scores, dtype=float).ravel()
    n = len(scores)
    if n == 0:
        raise ValueError("calibration set must contain at least one score")

    # Finite-sample correction: ceil((n+1)*(1-alpha)) / n
    # The quantile index is k = ceil((n+1)*(1-alpha))
    # We bound it to [1, n] to avoid going out of bounds
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))

    sorted_scores = np.sort(scores)
    return float(sorted_scores[k - 1])  # 0-indexed


def calibrate_radii(
    radii: np.ndarray,
    q_hat: float,
) -> np.ndarray:
    """Apply conformal calibration: r_tilde = q_hat * r.

    Parameters
    ----------
    radii : array-like
        Original envelope radii.
    q_hat : float
        Conformal quantile from calibration set.

    Returns
    -------
    np.ndarray
        Calibrated radii.
    """
    return np.asarray(radii, dtype=float) * q_hat


def split_conformal_calibrate(
    all_errors: np.ndarray,
    all_radii: np.ndarray,
    alpha: float = 0.10,
    train_frac: float = 0.70,
    rng: np.random.Generator | None = None,
) -> dict:
    """Run the full split-conformal calibration pipeline.

    1. Randomly permute gap indices.
    2. Split into train (70%) and calibration (30%) sets.
    3. Compute nonconformity scores on calibration set.
    4. Compute conformal quantile q_hat.

    The training set is reserved for model fitting (scale estimation).
    The calibration set is held out from training and used only for
    computing q_hat.

    Parameters
    ----------
    all_errors : np.ndarray, shape (n_gaps,)
        Center errors for each gap (or per-gap mean error).
    all_radii : np.ndarray, same shape
        Envelope radii for each gap (or per-gap mean radius).
    alpha : float
        Target miscoverage rate.
    train_frac : float
        Fraction of data for the training set.
    rng : np.random.Generator or None
        Random state for reproducible split.

    Returns
    -------
    dict with keys:
        q_hat : float — conformal quantile
        n_cal : int — number of calibration gaps
        n_train : int — number of training gaps
        n_total : int — total number of gaps
        cal_scores : np.ndarray — nonconformity scores on calibration set
        cal_indices : np.ndarray — integer indices of calibration gaps
        train_indices : np.ndarray — integer indices of training gaps
        alpha : float — target miscoverage rate
    """
    errors = np.asarray(all_errors, dtype=float).ravel()
    radii = np.asarray(all_radii, dtype=float).ravel()

    if len(errors) == 0:
        raise ValueError("at least one gap is required")
    if len(errors) != len(radii):
        raise ValueError(
            f"errors and radii must have same length, got {len(errors)} and {len(radii)}"
        )

    n = len(errors)

    if rng is None:
        rng = np.random.default_rng()

    # Random permutation for fair split
    perm = rng.permutation(n)
    n_train = max(1, int(n * train_frac))
    train_indices = perm[:n_train]
    cal_indices = perm[n_train:]

    # Nonconformity scores on calibration set
    cal_scores = compute_nonconformity_scores(errors[cal_indices], radii[cal_indices])
    q_hat = conformal_quantile(cal_scores, alpha)

    return {
        "q_hat": q_hat,
        "n_cal": len(cal_indices),
        "n_train": len(train_indices),
        "n_total": n,
        "cal_scores": cal_scores,
        "cal_indices": cal_indices,
        "train_indices": train_indices,
        "alpha": alpha,
    }


def empirical_coverage(
    errors: np.ndarray,
    radii: np.ndarray,
) -> float:
    """Compute empirical coverage: fraction of errors within radii.

    Parameters
    ----------
    errors : array-like, shape (n,)
        Pointwise or per-gap errors.
    radii : array-like, same shape
        Corresponding envelope radii.

    Returns
    -------
    float between 0 and 1.
    """
    errors = np.asarray(errors, dtype=float).ravel()
    radii = np.asarray(radii, dtype=float).ravel()
    covered = errors <= radii
    return float(np.mean(covered))
