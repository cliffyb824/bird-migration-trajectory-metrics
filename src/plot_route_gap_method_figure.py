
"""Create a clean four-panel method figure for route-gap uncertainty."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import Circle, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brownian_bridge_gap_reconstruction import brownian_bridge_sphere_sample, estimate_global_bridge_scale
from gap_reconstruction_baseline import records_to_sphere
from geometry import spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories
from plot_route_map import add_coastline

COAST = 'data/external/naturalearth/ne_110m_coastline/ne_110m_coastline.shp'
BLUE = '#276FBF'
ORANGE = '#D95F02'
MAGENTA = '#B44E8A'
TEAL = '#1B9E77'
INDIGO = '#5E5AAE'
DARK = '#20242A'
SEA = '#E9EEF3'


def sphere_to_lonlat(points):
    p = np.asarray(points, float)
    return np.rad2deg(np.arctan2(p[:, 1], p[:, 0])), np.rad2deg(np.arcsin(np.clip(p[:, 2], -1, 1)))


def centered_gap_indices(n, frac):
    size = min(max(1, int(round(n * frac))), n - 2)
    start = max(1, (n - size) // 2)
    return start, min(n - 1, start + size)


def make_bridge(points, start, stop):
    f = np.linspace(0, 1, stop - start + 2)[1:-1]
    b = spherical_linear_interpolate(points[start - 1], points[stop], f)
    return np.vstack([points[:start], b, points[stop:]])


def bounds(points, pad=0.8):
    lon, lat = sphere_to_lonlat(points)
    return lon.min() - pad, lon.max() + pad, lat.min() - pad, lat.max() + pad


def style_map(ax, b):
    ax.set_facecolor(SEA)
    add_coastline(ax, COAST, b)
    ax.set_xlim(b[0], b[1])
    ax.set_ylim(b[2], b[3])
    ax.grid(color='white', linewidth=0.8)
    ax.tick_params(labelsize=8, length=3, colors='#333333')
    for s in ax.spines.values():
        s.set_color('#30343A')
        s.set_linewidth(0.85)
    ax.set_xlabel('Longitude', fontsize=8.5)
    ax.set_ylabel('Latitude', fontsize=8.5)


def label(ax, text):
    ax.text(0.015, 0.985, text, transform=ax.transAxes, ha='left', va='top', fontsize=12, weight='bold', color=DARK)


def panel_gap(ax, complete, observed, removed):
    style_map(ax, bounds(complete))
    lon, lat = sphere_to_lonlat(complete)
    olon, olat = sphere_to_lonlat(observed)
    rlon, rlat = sphere_to_lonlat(removed)
    ax.plot(lon, lat, color='#A7ADB5', lw=1.8, zorder=2)
    ax.scatter(olon, olat, s=8, color=BLUE, alpha=0.62, zorder=3)
    ax.plot(rlon, rlat, color=ORANGE, lw=4.2, solid_capstyle='round', zorder=5)
    label(ax, '(a)')


def panel_reconstruction(ax, complete, observed, bridge, samples):
    style_map(ax, bounds(complete))
    olon, olat = sphere_to_lonlat(observed)
    blon, blat = sphere_to_lonlat(bridge)
    for sample in samples:
        slon, slat = sphere_to_lonlat(sample)
        ax.plot(slon, slat, color=MAGENTA, lw=0.95, alpha=0.20, zorder=2)
    ax.plot(blon, blat, color=ORANGE, lw=2.6, zorder=4)
    ax.scatter(olon, olat, s=7, color=BLUE, alpha=0.38, zorder=3)
    label(ax, '(b)')


def panel_calibration(ax):
    ax.set_facecolor('white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color('#30343A')
        s.set_linewidth(0.85)
    rng = np.random.default_rng(42)
    centers = [(0.24, 0.68), (0.40, 0.53), (0.57, 0.66), (0.72, 0.47), (0.31, 0.31), (0.62, 0.27)]
    for i, (x, y) in enumerate(centers):
        raw_r = 0.045 + 0.008 * (i % 2)
        cal_r = raw_r * 1.85
        ax.add_patch(Circle((x, y), cal_r, fill=False, edgecolor=TEAL, linewidth=1.5, alpha=0.75))
        ax.add_patch(Circle((x, y), raw_r, fill=False, edgecolor=MAGENTA, linewidth=1.3, alpha=0.8))
        ax.scatter([x + rng.normal(0, 0.06)], [y + rng.normal(0, 0.06)], s=28, color=ORANGE, edgecolor='white', linewidth=0.5, zorder=4)
    ax.plot([0.16, 0.83], [0.12, 0.12], color='#B8BEC7', lw=1.1)
    ax.scatter([0.20, 0.32], [0.12, 0.12], s=55, facecolors='none', edgecolors=[MAGENTA, TEAL], linewidths=1.5)
    ax.text(0.24, 0.105, 'raw', fontsize=8.5, va='center', color=MAGENTA)
    ax.text(0.36, 0.105, 'calibrated', fontsize=8.5, va='center', color=TEAL)
    label(ax, '(c)')


def panel_outputs(ax):
    ax.set_facecolor('white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color('#30343A')
        s.set_linewidth(0.85)
    mat = np.array([[0, .24, .55, .70, .38], [.24, 0, .35, .62, .44], [.55, .35, 0, .29, .65], [.70, .62, .29, 0, .53], [.38, .44, .65, .53, 0]])
    ax.imshow(mat, extent=(0.08, 0.40, 0.56, 0.88), cmap='YlGnBu', vmin=0, vmax=0.75)
    x = [0.63, 0.73, 0.83, 0.66, 0.78, 0.89]
    y = [0.78, 0.85, 0.76, 0.60, 0.58, 0.66]
    ax.scatter(x[:3], y[:3], s=85, color=BLUE, edgecolor='white', linewidth=0.7)
    ax.scatter(x[3:], y[3:], s=85, color=TEAL, edgecolor='white', linewidth=0.7)
    for i, h in enumerate([.20, .36, .24, .55, .43]):
        ax.add_patch(Rectangle((0.12 + 0.055 * i, 0.13), 0.035, h * 0.40, facecolor=INDIGO, alpha=0.80))
    xs = np.array([0.61, 0.70, 0.79, 0.88])
    ys = np.array([0.28, 0.23, 0.33, 0.27])
    ax.plot(xs, ys, color=ORANGE, lw=2.2)
    ax.fill_between(xs, ys - 0.06, ys + 0.07, color=ORANGE, alpha=0.20)
    label(ax, '(d)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='figures/route_gap_method_figure.png')
    args = parser.parse_args()

    selected = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'), 120, max_trajectories=20)
    _, recs = selected[0]
    scale = estimate_global_bridge_scale(selected, max_span=6)
    start, stop = centered_gap_indices(len(recs), 0.40)
    complete = records_to_sphere(recs)
    observed = np.vstack([complete[:start], complete[stop:]])
    removed = complete[start:stop]
    bridge = make_bridge(complete, start, stop)
    rng = np.random.default_rng(20260612)
    samples = [brownian_bridge_sphere_sample(recs, start, stop, scale, rng) for _ in range(30)]

    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    fig = plt.figure(figsize=(11.6, 7.2), facecolor='white')
    gs = gridspec.GridSpec(2, 2, figure=fig, wspace=0.18, hspace=0.22)
    panel_gap(fig.add_subplot(gs[0, 0]), complete, observed, removed)
    panel_reconstruction(fig.add_subplot(gs[0, 1]), complete, observed, bridge, samples)
    panel_calibration(fig.add_subplot(gs[1, 0]))
    panel_outputs(fig.add_subplot(gs[1, 1]))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=380, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Wrote: {out}')

if __name__ == '__main__':
    main()
