
"""Create a clean four-panel method figure for route-gap uncertainty."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

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
RED = '#C44E52'
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


def clean_axes(ax):
    ax.set_facecolor('white')
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#3A3F46')
    ax.spines['bottom'].set_color('#3A3F46')
    ax.tick_params(labelsize=8.5, colors='#333333')
    ax.grid(axis='y', color='#E6E9EE', linewidth=0.8)


def panel_validation(ax, validation):
    clean_axes(ax)
    gaps = sorted({int(row['missing_fraction'] * 100) for row in validation})
    x = np.arange(len(gaps))
    width = 0.34
    seasons = ['spring', 'autumn']
    colors = [BLUE, ORANGE]
    for i, season in enumerate(seasons):
        sd = sorted([row for row in validation if row['season'] == season], key=lambda row: row['missing_fraction'])
        coverage = [row['coverage_90_mean'] for row in sd]
        calibrated = [row['calibrated_coverage_90_mean'] for row in sd]
        ax.bar(x + (i - 0.5) * width, coverage, width,
               color=colors[i], alpha=0.82, label=season.capitalize(), zorder=3)
        ax.scatter(x + (i - 0.5) * width, calibrated,
                   marker='D', s=34, color=DARK, edgecolor='white', linewidth=0.5, zorder=5)
    ax.axhline(0.90, color=RED, lw=1.3, ls='--', zorder=2)
    ax.set_ylim(0, 1.02)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{v}%' for v in gaps])
    ax.set_ylabel('Pointwise coverage', fontsize=9)
    ax.set_xlabel('Withheld route fraction', fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc='upper left')
    ax.text(0.97, 0.88, 'nominal 90%', transform=ax.transAxes, ha='right', va='center', fontsize=8.5, color=RED)
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
    validation = read_numeric_csv('data/processed/withheld_gap_validation_summary.csv')
    summary = read_numeric_csv('data/processed/brownian_bridge_gap_reconstruction_summary.csv')

    fig = plt.figure(figsize=(12.2, 7.4), facecolor='white')
    gs = gridspec.GridSpec(2, 2, figure=fig, wspace=0.18, hspace=0.28)
    panel_gap(fig.add_subplot(gs[0, 0]), complete, observed, removed)
    panel_reconstruction(fig.add_subplot(gs[0, 1]), complete, observed, bridge, samples)
    panel_validation(fig.add_subplot(gs[1, 0]), validation)
    panel_propagation(fig.add_subplot(gs[1, 1]), summary)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=380, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Wrote: {out}')

if __name__ == '__main__':
    main()
