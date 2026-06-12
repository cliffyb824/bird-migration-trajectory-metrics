
"""Create a clean four-panel method figure for route-gap uncertainty."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import Ellipse, Polygon

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


def draw_bird_icon(ax, lon, lat, scale=1.0, color=DARK):
    wing_left = np.array([[-0.42, 0.00], [-0.12, 0.08], [0.02, 0.02], [-0.16, -0.03]]) * scale
    wing_right = np.array([[0.42, 0.00], [0.12, 0.08], [-0.02, 0.02], [0.16, -0.03]]) * scale
    tail = np.array([[-0.08, -0.02], [0.08, -0.02], [0.00, -0.16]]) * scale
    ax.add_patch(Polygon(wing_left + [lon, lat], closed=True, facecolor=color, edgecolor='white', linewidth=0.35, zorder=8))
    ax.add_patch(Polygon(wing_right + [lon, lat], closed=True, facecolor=color, edgecolor='white', linewidth=0.35, zorder=8))
    ax.add_patch(Polygon(tail + [lon, lat], closed=True, facecolor=color, edgecolor='white', linewidth=0.25, zorder=8))
    ax.add_patch(Ellipse((lon, lat), 0.18 * scale, 0.08 * scale, facecolor=color, edgecolor='white', linewidth=0.35, zorder=9))


def panel_gap(ax, complete, observed, removed):
    style_map(ax, bounds(complete))
    lon, lat = sphere_to_lonlat(complete)
    olon, olat = sphere_to_lonlat(observed)
    rlon, rlat = sphere_to_lonlat(removed)
    ax.plot(lon, lat, color='#A7ADB5', lw=1.8, zorder=2)
    ax.scatter(olon, olat, s=8, color=BLUE, alpha=0.62, zorder=3)
    ax.plot(rlon, rlat, color=ORANGE, lw=4.2, solid_capstyle='round', zorder=5)
    draw_bird_icon(ax, lon[0], lat[0], scale=0.75)
    ax.scatter([lon[-1]], [lat[-1]], s=38, marker='o', color='white', edgecolor=DARK, linewidth=0.8, zorder=7)
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
    draw_bird_icon(ax, blon[0], blat[0], scale=0.75)
    ax.scatter([blon[-1]], [blat[-1]], s=38, marker='o', color='white', edgecolor=DARK, linewidth=0.8, zorder=7)
    label(ax, '(b)')


def clean_axes(ax):
    ax.set_facecolor('white')
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#3A3F46')
    ax.spines['bottom'].set_color('#3A3F46')
    ax.tick_params(labelsize=8.5, colors='#333333')
    ax.grid(axis='y', color='#E6E9EE', linewidth=0.8)


def panel_bridge_construction(ax, complete, bridge, samples, start, stop):
    lon, lat = sphere_to_lonlat(complete)
    blon, blat = sphere_to_lonlat(bridge)
    gap_slice = slice(max(0, start - 8), min(len(complete), stop + 8))
    x0, x1 = lon[gap_slice].min(), lon[gap_slice].max()
    y0, y1 = lat[gap_slice].min(), lat[gap_slice].max()
    pad_x = max(0.35, (x1 - x0) * 0.35)
    pad_y = max(0.35, (y1 - y0) * 0.35)
    b = (x0 - pad_x, x1 + pad_x, y0 - pad_y, y1 + pad_y)
    style_map(ax, b)

    ax.plot(lon[gap_slice], lat[gap_slice], color='#B9BEC6', lw=1.6, zorder=2)
    for sample in samples:
        slon, slat = sphere_to_lonlat(sample)
        ax.plot(slon[start:stop], slat[start:stop], color=MAGENTA, lw=1.25, alpha=0.22, zorder=3)
    ax.plot(blon[start:stop], blat[start:stop], color=ORANGE, lw=2.8, zorder=5)
    ax.scatter([lon[start - 1], lon[stop]], [lat[start - 1], lat[stop]],
               s=46, color=BLUE, edgecolor='white', linewidth=0.7, zorder=6)
    ax.scatter(lon[start:stop: max(1, (stop - start) // 14)],
               lat[start:stop: max(1, (stop - start) // 14)],
               s=18, color='white', edgecolor=ORANGE, linewidth=0.9, zorder=7)

    mid = (start + stop) // 2
    ax.annotate('', xy=(blon[mid], blat[mid]), xytext=(blon[mid] + 0.35, blat[mid] + 0.28),
                arrowprops=dict(arrowstyle='->', lw=1.0, color=DARK), zorder=8)
    ax.text(0.60, 0.18, 'sampled gap paths', transform=ax.transAxes,
            fontsize=8.5, color=MAGENTA, ha='left', va='center')
    ax.text(0.08, 0.13, 'observed endpoints', transform=ax.transAxes,
            fontsize=8.5, color=BLUE, ha='left', va='center')
    label(ax, '(c)')


def panel_propagation(ax, summary):
    clean_axes(ax)
    filtered = [row for row in summary if row['method'] == 'brownian_bridge_sample' and abs(row['missing_fraction'] - 0.6) < 1e-9]
    order = [('spring', 'raw_dtw'), ('spring', 'srvf_dtw'), ('autumn', 'raw_dtw'), ('autumn', 'srvf_dtw')]
    rows = []
    for season, metric in order:
        rows.append(next(row for row in filtered if row['season'] == season and row['metric'] == metric))
    x = np.arange(len(rows))
    matrix_mean = np.array([row['matrix_spearman_mean'] for row in rows])
    matrix_p05 = np.array([row['matrix_spearman_p05'] for row in rows])
    matrix_p95 = np.array([row['matrix_spearman_p95'] for row in rows])
    cluster_ari = np.array([row['cluster_ari_mean'] for row in rows])
    ax.bar(x, matrix_mean, width=0.58,
           color=[BLUE, INDIGO, ORANGE, MAGENTA], alpha=0.86, zorder=3)
    ax.errorbar(x, matrix_mean, yerr=[matrix_mean - matrix_p05, matrix_p95 - matrix_mean],
                fmt='none', ecolor='#30343A', capsize=3, lw=1.0, zorder=4)
    ax.scatter(x, cluster_ari, s=42, color='white', edgecolor=DARK, linewidth=1.1, zorder=5, label='ARI')
    ax.set_ylim(0, 1.04)
    ax.set_xticks(x)
    names = [f"{row['season'].capitalize()}\n{row['metric'].replace('_', '-')}" for row in rows]
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel('Stability at 60% gaps', fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc='lower left')
    label(ax, '(d)')

def read_numeric_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key, value in list(row.items()):
            if key in {'season', 'method', 'metric'}:
                continue
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows

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
    summary = read_numeric_csv('data/processed/brownian_bridge_gap_reconstruction_summary.csv')

    fig = plt.figure(figsize=(12.2, 7.4), facecolor='white')
    gs = gridspec.GridSpec(2, 2, figure=fig, wspace=0.18, hspace=0.28)
    panel_gap(fig.add_subplot(gs[0, 0]), complete, observed, removed)
    panel_reconstruction(fig.add_subplot(gs[0, 1]), complete, observed, bridge, samples)
    panel_bridge_construction(fig.add_subplot(gs[1, 0]), complete, bridge, samples, start, stop)
    panel_propagation(fig.add_subplot(gs[1, 1]), summary)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=380, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Wrote: {out}')

if __name__ == '__main__':
    main()
