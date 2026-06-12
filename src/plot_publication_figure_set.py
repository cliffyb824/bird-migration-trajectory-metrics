
"""Generate additional publication-style figures for the route-gap manuscript."""
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
BLUE = '#276FBF'; ORANGE = '#D95F02'; TEAL = '#1B9E77'; MAGENTA = '#B44E8A'; INDIGO = '#5E5AAE'; DARK = '#20242A'; SEA = '#E9EEF3'


def rows(path):
    with open(path, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def sphere_to_lonlat(points):
    p = np.asarray(points, float)
    return np.rad2deg(np.arctan2(p[:, 1], p[:, 0])), np.rad2deg(np.arcsin(np.clip(p[:, 2], -1, 1)))


def records_lonlat(records):
    return sphere_to_lonlat(records_to_sphere(records))


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
    ax.set_xlim(bounds[0], bounds[1]); ax.set_ylim(bounds[2], bounds[3])
    if aspect:
        ax.set_aspect('equal', adjustable='box')
    ax.grid(color='white', linewidth=0.75)
    ax.tick_params(labelsize=8, length=3, colors='#333333')
    for s in ax.spines.values():
        s.set_color('#30343A'); s.set_linewidth(0.85)
    ax.set_xlabel('Longitude', fontsize=8.5); ax.set_ylabel('Latitude', fontsize=8.5)


def label(ax, s):
    ax.text(0.015, 0.985, s, transform=ax.transAxes, ha='left', va='top', fontsize=12, weight='bold', color=DARK)


def route_bounds(points, pad=0.7):
    lon, lat = sphere_to_lonlat(points)
    return lon.min() - pad, lon.max() + pad, lat.min() - pad, lat.max() + pad


def route_overview(outdir):
    spring = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'), 80, max_trajectories=34)
    autumn = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv'), 80, max_trajectories=34)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.2), facecolor='white')
    for ax, data, color, title, panel in [
        (axes[0], spring, BLUE, 'Spring transit routes', '(a)'),
        (axes[1], autumn, ORANGE, 'Autumn transit routes', '(b)'),
    ]:
        style_map(ax, (-22, 42, 18, 63))
        for _, recs in data:
            lon, lat = records_lonlat(recs)
            ax.plot(lon, lat, color=color, alpha=0.42, lw=1.0, zorder=3)
        ax.scatter([3.18], [51.34], s=95, color='black', marker='*', zorder=5)
        ax.set_title(title, fontsize=11, weight='bold')
        label(ax, panel)
    fig.tight_layout()
    fig.savefig(outdir / 'route_overview_by_season.png', dpi=360, bbox_inches='tight')
    plt.close(fig)


def reconstruction_gallery(outdir):
    selected = select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'), 120, max_trajectories=6)
    scale = estimate_global_bridge_scale(selected, max_span=6)
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 7.8), facecolor='white')
    rng = np.random.default_rng(20260612)
    for idx, (ax, (_, recs)) in enumerate(zip(axes.flat, selected[:6])):
        start, stop = centered_gap_indices(len(recs), 0.40)
        complete = records_to_sphere(recs)
        observed = np.vstack([complete[:start], complete[stop:]])
        removed = complete[start:stop]
        bridge = make_bridge(complete, start, stop)
        style_map(ax, route_bounds(complete), aspect=False)
        lon, lat = sphere_to_lonlat(complete); rlon, rlat = sphere_to_lonlat(removed); olon, olat = sphere_to_lonlat(observed); blon, blat = sphere_to_lonlat(bridge)
        for _ in range(14):
            smp = brownian_bridge_sphere_sample(recs, start, stop, scale, rng)
            slon, slat = sphere_to_lonlat(smp)
            ax.plot(slon, slat, color=MAGENTA, alpha=0.16, lw=0.9, zorder=2)
        ax.plot(lon, lat, color='#A9AEB4', lw=1.0, zorder=1)
        ax.scatter(olon, olat, s=5, color=BLUE, alpha=0.45, zorder=3)
        ax.plot(rlon, rlat, color=ORANGE, lw=3.5, zorder=4, solid_capstyle='round')
        ax.plot(blon, blat, color='black', lw=1.1, alpha=0.75, zorder=5)
        label(ax, f'({chr(97+idx)})')
    fig.tight_layout()
    fig.savefig(outdir / 'gap_reconstruction_gallery.png', dpi=360, bbox_inches='tight')
    plt.close(fig)


def validation_calibration(outdir):
    data = rows('data/processed/withheld_gap_validation_summary.csv')
    seasons = ['spring', 'autumn']
    fig = plt.figure(figsize=(12.4, 7.6), facecolor='white')
    gs = gridspec.GridSpec(2, 2, figure=fig, wspace=0.24, hspace=0.28)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[0, 1]); ax3 = fig.add_subplot(gs[1, :])
    for ax, season, color, panel in [(ax1, 'spring', BLUE, '(a)'), (ax2, 'autumn', ORANGE, '(b)')]:
        sub = [r for r in data if r['season'] == season]
        x = np.array([float(r['missing_fraction']) * 100 for r in sub])
        det = np.array([float(r['deterministic_mean_error_km_mean']) for r in sub])
        bb = np.array([float(r['sample_center_mean_error_km_mean']) for r in sub])
        ax.plot(x, det, 'o-', color=color, lw=2, label='deterministic')
        ax.plot(x, bb, 's--', color=MAGENTA, lw=2, label='BB center')
        ax.set_title(season.capitalize(), fontsize=11, weight='bold')
        ax.set_xlabel('Withheld fraction', fontsize=9); ax.set_ylabel('Mean error (km)', fontsize=9)
        ax.set_xticks(x); ax.set_xticklabels([f'{int(v)}%' for v in x])
        ax.grid(color='#E5E7EB'); ax.legend(frameon=False, fontsize=8)
        label(ax, panel)
    width = 3.8
    positions = [] ; raw = [] ; cal = [] ; cols = [] ; ticks = []
    for j, season in enumerate(seasons):
        sub = [r for r in data if r['season'] == season]
        for r in sub:
            base = j * 42 + float(r['missing_fraction']) * 100
            positions.append(base); raw.append(float(r['coverage_90_mean'])); cal.append(float(r['calibrated_coverage_90_mean'])); cols.append(BLUE if season == 'spring' else ORANGE); ticks.append(f"{season[0].upper()}{int(float(r['missing_fraction'])*100)}")
    pos = np.array(positions)
    ax3.bar(pos - width/2, raw, width=width, color=MAGENTA, alpha=0.72, label='raw envelope')
    ax3.bar(pos + width/2, cal, width=width, color=TEAL, alpha=0.80, label='calibrated envelope')
    ax3.axhline(0.9, color=DARK, lw=1, ls='--')
    ax3.set_ylim(0, 1.05); ax3.set_ylabel('90% envelope coverage', fontsize=9); ax3.set_xticks(pos); ax3.set_xticklabels(ticks, fontsize=8)
    ax3.grid(axis='y', color='#E5E7EB'); ax3.legend(frameon=False, fontsize=8, ncol=2, loc='lower right')
    label(ax3, '(c)')
    fig.savefig(outdir / 'validation_calibration_summary.png', dpi=360, bbox_inches='tight')
    plt.close(fig)


def downstream_dashboard(outdir):
    data = rows('data/processed/brownian_bridge_gap_reconstruction_summary.csv')
    metrics = [('matrix_spearman_mean', 'Matrix correlation'), ('cluster_ari_mean', 'Cluster ARI'), ('anomaly_rank_spearman_mean', 'Anomaly correlation'), ('top_k_overlap_mean', 'Top-k overlap')]
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.2), facecolor='white')
    for ax, (field, title), panel in zip(axes.flat, metrics, ['(a)', '(b)', '(c)', '(d)']):
        for season, color, ls in [('spring', BLUE, '-'), ('autumn', ORANGE, '-')]:
            for metric, marker, alpha in [('raw_dtw', 'o', 1.0), ('srvf_dtw', 's', 0.68)]:
                sub = [r for r in data if r['season'] == season and r['method'] == 'brownian_bridge' and r['metric'] == metric]
                sub = sorted(sub, key=lambda r: float(r['missing_fraction']))
                x = [float(r['missing_fraction']) * 100 for r in sub]
                y = [float(r[field]) for r in sub]
                ax.plot(x, y, marker=marker, color=color, alpha=alpha, lw=2, label=f'{season} {metric.replace("_", "-")}')
        ax.set_title(title, fontsize=11, weight='bold')
        ax.set_xlabel('Gap fraction', fontsize=9); ax.set_ylim(0, 1.03); ax.set_xticks([20, 40, 60]); ax.set_xticklabels(['20%', '40%', '60%'])
        ax.grid(color='#E5E7EB'); label(ax, panel)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(outdir / 'downstream_stability_dashboard.png', dpi=360, bbox_inches='tight')
    plt.close(fig)


def scale_sensitivity(outdir):
    data = rows('data/processed/brownian_bridge_scale_sensitivity_summary.csv')
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.9), facecolor='white', sharey=True)
    for ax, season, panel in [(axes[0], 'spring', '(a)'), (axes[1], 'autumn', '(b)')]:
        for metric, color, marker in [('raw_dtw', BLUE, 'o'), ('srvf_dtw', ORANGE, 's')]:
            sub = [r for r in data if r['season'] == season and r['metric'] == metric]
            sub = sorted(sub, key=lambda r: float(r['scale_multiplier']))
            x = [float(r['scale_multiplier']) for r in sub]
            y = [float(r['matrix_spearman_mean']) for r in sub]
            ax.plot(x, y, marker=marker, color=color, lw=2.2, label=metric.replace('_', '-'))
        ax.set_title(season.capitalize(), fontsize=11, weight='bold')
        ax.set_xlabel('Scale multiplier', fontsize=9); ax.set_ylabel('Matrix correlation', fontsize=9)
        ax.set_xticks([0.5, 1.0, 2.0]); ax.set_ylim(0, 1.03); ax.grid(color='#E5E7EB'); ax.legend(frameon=False, fontsize=8)
        label(ax, panel)
    fig.tight_layout()
    fig.savefig(outdir / 'brownian_scale_sensitivity.png', dpi=360, bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default='figures')
    args = parser.parse_args()
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    route_overview(outdir)
    reconstruction_gallery(outdir)
    validation_calibration(outdir)
    downstream_dashboard(outdir)
    scale_sensitivity(outdir)
    print('Wrote additional publication figures to', outdir)

if __name__ == '__main__':
    main()
