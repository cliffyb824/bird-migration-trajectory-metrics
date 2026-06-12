"""Create an overall research framework figure for the manuscript."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon


BLUE = "#276FBF"
ORANGE = "#D95F02"
MAGENTA = "#B44E8A"
GREEN = "#1B9E77"
INDIGO = "#5E5AAE"
RED = "#C44E52"
DARK = "#20242A"
GRAY = "#65707A"
LIGHT = "#F4F6F8"
LINE = "#C9D0D8"


def box(ax, x, y, w, h, title, subtitle, color):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.2,
        edgecolor=color,
        facecolor="white",
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x + 0.04 * w, y + h - 0.26 * h, title, fontsize=12, weight="bold", color=DARK, va="top")
    ax.text(x + 0.04 * w, y + h - 0.52 * h, subtitle, fontsize=8.6, color=GRAY, va="top", linespacing=1.22)


def arrow(ax, xy1, xy2, color=GRAY, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            xy1,
            xy2,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.35,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            zorder=3,
        )
    )


def bird(ax, x, y, s=1.0, color=DARK):
    left = np.array([[-0.11, 0.00], [-0.03, 0.04], [0.01, 0.01], [-0.04, -0.02]]) * s
    right = np.array([[0.11, 0.00], [0.03, 0.04], [-0.01, 0.01], [0.04, -0.02]]) * s
    tail = np.array([[-0.022, -0.018], [0.022, -0.018], [0.00, -0.060]]) * s
    ax.add_patch(Polygon(left + [x, y], closed=True, facecolor=color, edgecolor="white", linewidth=0.5, zorder=6))
    ax.add_patch(Polygon(right + [x, y], closed=True, facecolor=color, edgecolor="white", linewidth=0.5, zorder=6))
    ax.add_patch(Polygon(tail + [x, y], closed=True, facecolor=color, edgecolor="white", linewidth=0.4, zorder=6))
    ax.add_patch(Circle((x, y), 0.018 * s, facecolor=color, edgecolor="white", linewidth=0.4, zorder=7))


def route_icon(ax, x, y, w, h):
    t = np.linspace(0, 1, 90)
    xs = x + w * (0.12 + 0.76 * t)
    ys = y + h * (0.25 + 0.52 * np.sin(1.1 * np.pi * t) + 0.12 * np.sin(4 * np.pi * t))
    ax.plot(xs, ys, color=BLUE, lw=2.2, zorder=4)
    ax.scatter(xs[::12], ys[::12], s=12, color="white", edgecolor=BLUE, linewidth=0.8, zorder=5)
    bird(ax, xs[0], ys[0], 0.75)
    ax.scatter([xs[-1]], [ys[-1]], s=34, facecolor="white", edgecolor=DARK, linewidth=1.0, zorder=5)


def missingness_icon(ax, x, y, w, h):
    t = np.linspace(0, 1, 100)
    xs = x + w * (0.10 + 0.80 * t)
    ys = y + h * (0.52 + 0.20 * np.sin(2.2 * np.pi * t))
    gap = (t > 0.42) & (t < 0.62)
    ax.plot(xs[~gap], ys[~gap], color=BLUE, lw=2.0, zorder=4)
    ax.plot(xs[gap], ys[gap], color=ORANGE, lw=4.0, solid_capstyle="round", zorder=5)
    ax.text(x + 0.45 * w, y + 0.18 * h, "gap", fontsize=8.5, color=ORANGE, ha="center")


def ensemble_icon(ax, x, y, w, h):
    t = np.linspace(0, 1, 90)
    xs = x + w * (0.10 + 0.80 * t)
    base = y + h * (0.50 + 0.16 * np.sin(1.5 * np.pi * t))
    rng = np.random.default_rng(7)
    for _ in range(11):
        noise = 0.035 * h * np.sin((2.0 + rng.random()) * np.pi * t + rng.uniform(-1, 1))
        ax.plot(xs, base + noise, color=MAGENTA, lw=1.0, alpha=0.25, zorder=4)
    ax.plot(xs, base, color=ORANGE, lw=2.4, zorder=5)
    ax.scatter([xs[0], xs[-1]], [base[0], base[-1]], s=30, color=BLUE, edgecolor="white", linewidth=0.7, zorder=6)


def validation_icon(ax, x, y, w, h):
    xs = np.linspace(x + 0.20 * w, x + 0.80 * w, 5)
    ys = y + h * np.array([0.36, 0.60, 0.47, 0.68, 0.43])
    for xi, yi, r in zip(xs, ys, [0.050, 0.070, 0.055, 0.075, 0.060]):
        ax.add_patch(Circle((xi, yi), r * w, fill=False, edgecolor=MAGENTA, linewidth=1.1, alpha=0.75, zorder=4))
        ax.add_patch(Circle((xi, yi), r * 1.65 * w, fill=False, edgecolor=GREEN, linewidth=1.1, alpha=0.70, zorder=4))
        ax.scatter([xi + 0.055 * w], [yi + 0.020 * h], s=16, color=ORANGE, edgecolor="white", linewidth=0.4, zorder=5)


def outputs_icon(ax, x, y, w, h):
    mat = np.array([[0.1, 0.4, 0.7], [0.4, 0.2, 0.5], [0.7, 0.5, 0.15]])
    ax.imshow(mat, extent=(x + 0.08 * w, x + 0.35 * w, y + 0.46 * h, y + 0.78 * h), cmap="YlGnBu", zorder=4)
    ax.scatter(
        x + w * np.array([0.57, 0.67, 0.77, 0.60, 0.72, 0.84]),
        y + h * np.array([0.70, 0.78, 0.66, 0.43, 0.50, 0.38]),
        s=36,
        color=[BLUE, BLUE, BLUE, GREEN, GREEN, GREEN],
        edgecolor="white",
        linewidth=0.6,
        zorder=5,
    )
    bars = [0.22, 0.44, 0.32, 0.58]
    for i, height in enumerate(bars):
        ax.add_patch(
            FancyBboxPatch(
                (x + (0.12 + 0.08 * i) * w, y + 0.16 * h),
                0.045 * w,
                height * h,
                boxstyle="round,pad=0,rounding_size=0.004",
                facecolor=INDIGO,
                edgecolor="none",
                alpha=0.80,
                zorder=4,
            )
        )


def conclusion_icon(ax, x, y, w, h):
    t = np.linspace(0, 1, 80)
    ax.plot(x + w * (0.12 + 0.76 * t), y + h * (0.66 + 0.03 * np.sin(4 * np.pi * t)), color=GREEN, lw=2.4)
    ax.fill_between(
        x + w * (0.12 + 0.76 * t),
        y + h * (0.61 + 0.03 * np.sin(4 * np.pi * t)),
        y + h * (0.71 + 0.03 * np.sin(4 * np.pi * t)),
        color=GREEN,
        alpha=0.18,
    )
    ax.plot(x + w * (0.12 + 0.76 * t), y + h * (0.32 + 0.12 * np.sin(3.2 * np.pi * t)), color=RED, lw=2.0)
    ax.fill_between(
        x + w * (0.12 + 0.76 * t),
        y + h * (0.20 + 0.12 * np.sin(3.2 * np.pi * t)),
        y + h * (0.44 + 0.12 * np.sin(3.2 * np.pi * t)),
        color=RED,
        alpha=0.15,
    )
    ax.text(x + 0.78 * w, y + 0.68 * h, "stable", fontsize=8.2, color=GREEN, va="center")
    ax.text(x + 0.78 * w, y + 0.32 * h, "unstable", fontsize=8.2, color=RED, va="center")


def main():
    out = Path("figures/research_framework_overview.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14.0, 7.8), facecolor="white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.955,
        "Uncertainty-aware migratory-route comparison from incomplete GPS tracking data",
        ha="center",
        va="top",
        fontsize=17,
        weight="bold",
        color=DARK,
    )
    ax.text(
        0.5,
        0.912,
        "Problem-driven workflow: missing route segments are reconstructed, validated, calibrated, and propagated into downstream ecological-informatics conclusions",
        ha="center",
        va="top",
        fontsize=10.2,
        color=GRAY,
    )

    y_top = 0.58
    y_bottom = 0.21
    w = 0.18
    h = 0.22
    xs_top = [0.055, 0.30, 0.545, 0.79]
    xs_bottom = [0.18, 0.43, 0.68]

    box(ax, xs_top[0], y_top, w, h, "1  Tracking data", "Individual bird GPS records\nbecome route units", BLUE)
    route_icon(ax, xs_top[0] + 0.02, y_top + 0.015, w * 0.84, h * 0.42)

    box(ax, xs_top[1], y_top, w, h, "2  Missingness design", "Random point loss versus\ncontiguous route gaps", ORANGE)
    missingness_icon(ax, xs_top[1] + 0.02, y_top + 0.02, w * 0.84, h * 0.40)

    box(ax, xs_top[2], y_top, w, h, "3  Gap reconstruction", "Spherical bridge plus\nBrownian route ensemble", MAGENTA)
    ensemble_icon(ax, xs_top[2] + 0.02, y_top + 0.02, w * 0.84, h * 0.40)

    box(ax, xs_top[3], y_top, w, h, "4  Envelope diagnostics", "Withheld segments test\ncoverage and calibration", GREEN)
    validation_icon(ax, xs_top[3] + 0.02, y_top + 0.02, w * 0.84, h * 0.40)

    box(ax, xs_bottom[0], y_bottom, w, h, "5  Propagation", "Recompute distance matrices,\nclusters, and anomaly ranks", INDIGO)
    outputs_icon(ax, xs_bottom[0] + 0.02, y_bottom + 0.02, w * 0.84, h * 0.42)

    box(ax, xs_bottom[1], y_bottom, w, h, "6  Stability metrics", "Matrix correlation, relative error,\nARI, anomaly overlap", BLUE)
    for i, val in enumerate([0.84, 0.66, 0.47, 0.76]):
        ax.add_patch(
            FancyBboxPatch(
                (xs_bottom[1] + (0.16 + 0.13 * i) * w, y_bottom + 0.13 * h),
                0.065 * w,
                val * 0.58 * h,
                boxstyle="round,pad=0,rounding_size=0.004",
                facecolor=[BLUE, ORANGE, MAGENTA, GREEN][i],
                edgecolor="none",
                alpha=0.84,
                zorder=4,
            )
        )
    ax.plot(
        [xs_bottom[1] + 0.14 * w, xs_bottom[1] + 0.78 * w],
        [y_bottom + 0.45 * h, y_bottom + 0.45 * h],
        color=LINE,
        lw=1,
        zorder=3,
    )

    box(ax, xs_bottom[2], y_bottom, w, h, "7  Interpretation", "Report which conclusions are\nrobust to missing-route uncertainty", RED)
    conclusion_icon(ax, xs_bottom[2] + 0.02, y_bottom + 0.02, w * 0.84, h * 0.42)

    arrow(ax, (xs_top[0] + w, y_top + 0.11), (xs_top[1], y_top + 0.11))
    arrow(ax, (xs_top[1] + w, y_top + 0.11), (xs_top[2], y_top + 0.11))
    arrow(ax, (xs_top[2] + w, y_top + 0.11), (xs_top[3], y_top + 0.11))
    arrow(ax, (xs_top[3] + 0.09, y_top), (xs_bottom[0] + 0.09, y_bottom + h), rad=0.16)
    arrow(ax, (xs_bottom[0] + w, y_bottom + 0.11), (xs_bottom[1], y_bottom + 0.11))
    arrow(ax, (xs_bottom[1] + w, y_bottom + 0.11), (xs_bottom[2], y_bottom + 0.11))

    ax.add_patch(
        FancyBboxPatch(
            (0.055, 0.06),
            0.89,
            0.065,
            boxstyle="round,pad=0.014,rounding_size=0.02",
            facecolor=LIGHT,
            edgecolor=LINE,
            linewidth=1.0,
            zorder=1,
        )
    )
    ax.text(
        0.5,
        0.092,
        "Core claim: route reconstruction is not the endpoint; reconstruction uncertainty must be validated and propagated to the conclusions drawn from trajectory distances.",
        ha="center",
        va="center",
        fontsize=10,
        color=DARK,
    )

    fig.savefig(out, dpi=360, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
