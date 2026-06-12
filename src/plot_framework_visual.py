
"""Create a low-text, publication-style visual framework figure."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brownian_bridge_gap_reconstruction import brownian_bridge_sphere_sample, estimate_global_bridge_scale
from gap_reconstruction_baseline import records_to_sphere
from geometry import spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories
from plot_route_map import add_coastline

COAST = 'data/external/naturalearth/ne_110m_coastline/ne_110m_coastline.shp'
BLUE = '#276FBF'
ORANGE = '#D95F02'
TEAL = '#1B9E77'
MAGENTA = '#B44E8A'
INDIGO = '#5E5AAE'
DARK = '#20242A'
LAND = '#F4F5F6'
SEA = '#E9EEF3'
GRID = '#FFFFFF'


def sphere_to_lonlat(points):
    p = np.asarray(points, float)
    return np.rad2deg(np.arctan2(p[:, 1], p[:, 0])), np.rad2deg(np.arcsin(np.clip(p[:, 2], -1, 1)))


def records_lonlat(records):
    return sphere_to_lonlat(records_to_sphere(records))


def read_rows(path):
    with open(path, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def centered_gap_indices(n, frac):
    size = min(max(1, int(round(n * frac))), n - 2)
    start = max(1, (n - size) // 2)
    return start, min(n - 1, start + size)


def make_bridge(points, start, stop):
    f = np.linspace(0, 1, stop - start + 2)[1:-1]
    b = spherical_linear_interpolate(points[start - 1], points[stop], f)
    return np.vstack([points[:start], b, points[stop:]])


def style_map(ax, bounds, aspect=True):
    ax.set_facecolor(SEA)
    add_coastline(ax, COAST, bounds)
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    if aspect:
        ax.set_aspect('equal', adjustable='box')
    ax.grid(color=GRID, linewidth=0.8)
    ax.tick_params(labelsize=8, colors='#30343A', length=3)
    for spine in ax.spines.values():
        spine.set_linewidth(0.9)
        spine.set_color('#2F343A')
    ax.set_xlabel('Longitude', fontsize=8.5)
    ax.set_ylabel('Latitude', fontsize=8.5)


def panel_label(ax, label):
    ax.text(0.015, 0.985, label, transform=ax.transAxes, ha='left', va='top', fontsize=12, weight='bold', color=DARK)


def panel_routes(ax, spring, autumn):
    bounds = (-22, 42, 18, 63)
    style_map(ax, bounds)
    for _, recs in autumn:
        lon, lat = records_lonlat(recs)
        ax.plot(lon, lat, color=ORANGE, alpha=0.50, lw=1.15, zorder=3)
    for _, recs in spring:
        lon, lat = records_lonlat(recs)
        ax.plot(lon, lat, color=BLUE, alpha=0.55, lw=1.15, zorder=4)
    ax.scatter([3.18], [51.34], s=70, color='black', marker='*', zorder=6)
    ax.plot([], [], color=BLUE, lw=2, label='spring')
    ax.plot([], [], color=ORANGE, lw=2, label='autumn')
    ax.legend(loc='lower left', frameon=True, framealpha=0.88, fontsize=8, borderpad=0.4)
    panel_label(ax, '(a)')


def route_bounds(complete, pad=0.8):
    lon, lat = sphere_to_lonlat(complete)
    return (lon.min() - pad, lon.max() + pad, lat.min() - pad, lat.max() + pad)


def panel_gap(ax, complete, observed, removed):
    bounds = route_bounds(complete)
    style_map(ax, bounds, aspect=False)
    lon, lat = sphere_to_lonlat(complete)
    olon, olat = sphere_to_lonlat(observed)
    rlon, rlat = sphere_to_lonlat(removed)
    ax.plot(lon, lat, color='#969CA3', lw=1.8, zorder=2)
    ax.scatter(olon, olat, s=7, color=BLUE, alpha=0.62, zorder=3)
    ax.plot(rlon, rlat, color=ORANGE, lw=4.0, solid_capstyle='round', zorder=5)
    panel_label(ax, '(b)')


def panel_recon(ax, complete, observed, bridge, samples):
    bounds = route_bounds(complete)
    style_map(ax, bounds, aspect=False)
    olon, olat = sphere_to_lonlat(observed)
    blon, blat = sphere_to_lonlat(bridge)
    for sample in samples:
        slon, slat = sphere_to_lonlat(sample)
        ax.plot(slon, slat, color=MAGENTA, lw=0.9, alpha=0.22, zorder=2)
    ax.plot(blon, blat, color=ORANGE, lw=2.4, zorder=4)
    ax.scatter(olon, olat, s=6, color=BLUE, alpha=0.35, zorder=3)
    panel_label(ax, '(c)')


def panel_validation(ax, rows):
    rows = [r for r in rows if r['season'] == 'spring']
    x = np.array([float(r['missing_fraction']) * 100 for r in rows])
    raw = np.array([float(r['coverage_90_mean']) for r in rows])
    cal = np.array([float(r['calibrated_coverage_90_mean']) for r in rows])
    w = 6
    ax.bar(x - w/2, raw, width=w, color=MAGENTA, alpha=0.78)
    ax.bar(x + w/2, cal, width=w, color=TEAL, alpha=0.82)
    ax.axhline(0.9, color=DARK, ls='--', lw=1.0)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(v)}%' for v in x], fontsize=8)
    ax.set_ylabel('Coverage', fontsize=8.5)
    ax.set_xlabel('Gap', fontsize=8.5)
    ax.grid(axis='y', color='#E5E7EB', lw=0.8)
    ax.tick_params(labelsize=8)
    for s in ax.spines.values(): s.set_color('#30343A'); s.set_linewidth(0.8)
    panel_label(ax, '(d)')


def panel_missingness(ax, rows):
    for mech, color in [('random_points', BLUE), ('contiguous_block', ORANGE)]:
        sub = [r for r in rows if r['missing_mechanism'] == mech and r['metric'] == 'raw_dtw']
        sub = sorted(sub, key=lambda r: float(r['missing_fraction']))
        x = [float(r['missing_fraction']) * 100 for r in sub]
        y = [float(r['matrix_spearman_mean']) for r in sub]
        ax.plot(x, y, 'o-', color=color, lw=2.0, ms=4.5)
    ax.set_ylim(0.84, 1.01)
    ax.set_ylabel('Matrix corr.', fontsize=8.5)
    ax.set_xlabel('Missingness', fontsize=8.5)
    ax.set_xticks([20, 40, 60])
    ax.set_xticklabels(['20%', '40%', '60%'], fontsize=8)
    ax.grid(color='#E5E7EB', lw=0.8)
    ax.tick_params(labelsize=8)
    for s in ax.spines.values(): s.set_color('#30343A'); s.set_linewidth(0.8)
    panel_label(ax, '(e)')


def panel_downstream(ax, rows):
    keep = [r for r in rows if r['missing_fraction'] == '0.6' and r['method'] == 'brownian_bridge']
    order = [('spring', 'raw_dtw'), ('spring', 'srvf_dtw'), ('autumn', 'raw_dtw'), ('autumn', 'srvf_dtw')]
    vals = []
    cols = []
    labs = []
    for season, metric in order:
        m = [r for r in keep if r['season'] == season and r['metric'] == metric]
        if not m:
            continue
        vals.append(float(m[0]['cluster_ari_mean']))
        cols.append(BLUE if season == 'spring' else ORANGE)
        labs.append('Raw' if metric == 'raw_dtw' else 'SRVF')
    ax.bar(range(len(vals)), vals, color=cols, alpha=0.82, width=0.65)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('ARI', fontsize=8.5)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, fontsize=8)
    ax.grid(axis='y', color='#E5E7EB', lw=0.8)
    for s in ax.spines.values(): s.set_color('#30343A'); s.set_linewidth(0.8)
    panel_label(ax, '(f)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='figures/route_gap_uncertainty_framework_v3.png')
    args = parser.parse_args()

    spring = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'), 80, max_trajectories=16)
    autumn = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv'), 80, max_trajectories=16)
    selected = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'), 120, max_trajectories=20)
    _, recs = selected[0]
    scale = estimate_global_bridge_scale(selected, max_span=6)
    start, stop = centered_gap_indices(len(recs), 0.40)
    complete = records_to_sphere(recs)
    observed = np.vstack([complete[:start], complete[stop:]])
    removed = complete[start:stop]
    bridge = make_bridge(complete, start, stop)
    rng = np.random.default_rng(20260612)
    samples = [brownian_bridge_sphere_sample(recs, start, stop, scale, rng) for _ in range(28)]

    validation = read_rows('data/processed/withheld_gap_validation_summary.csv')
    missing = read_rows('data/processed/missing_data_stability_summary.csv')
    downstream = read_rows('data/processed/brownian_bridge_gap_reconstruction_summary.csv')

    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    fig = plt.figure(figsize=(12.6, 8.8), facecolor='white')
    gs = gridspec.GridSpec(3, 3, figure=fig, width_ratios=[1.55, 1, 1], height_ratios=[1, 1, 1], wspace=0.24, hspace=0.28)
    panel_routes(fig.add_subplot(gs[:, 0]), spring, autumn)
    panel_gap(fig.add_subplot(gs[0, 1]), complete, observed, removed)
    panel_recon(fig.add_subplot(gs[0, 2]), complete, observed, bridge, samples)
    panel_validation(fig.add_subplot(gs[1, 1]), validation)
    panel_missingness(fig.add_subplot(gs[1, 2]), missing)
    panel_downstream(fig.add_subplot(gs[2, 1:3]), downstream)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=360, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Wrote: {out}')

if __name__ == '__main__':
    main()
