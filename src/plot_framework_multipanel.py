
"""Create a journal-style multi-panel framework figure for route-gap uncertainty."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import Rectangle, FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brownian_bridge_gap_reconstruction import brownian_bridge_sphere_sample, estimate_global_bridge_scale
from gap_reconstruction_baseline import records_to_sphere
from geometry import spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories

BLUE="#1f77b4"; ORANGE="#d95f02"; GREEN="#1b9e77"; PURPLE="#7570b3"; PINK="#cc79a7"; GREY="#777777"; DARK="#222222"

def sphere_to_lonlat(points):
    p=np.asarray(points,float); return np.rad2deg(np.arctan2(p[:,1],p[:,0])), np.rad2deg(np.arcsin(np.clip(p[:,2],-1,1)))

def records_lonlat(records):
    pts=records_to_sphere(records); return sphere_to_lonlat(pts)

def read_rows(path):
    with open(path, newline='', encoding='utf-8') as fh: return list(csv.DictReader(fh))

def centered_gap_indices(n, frac):
    size=min(max(1,int(round(n*frac))),n-2); start=max(1,(n-size)//2); return start,min(n-1,start+size)

def make_bridge(points,start,stop):
    f=np.linspace(0,1,stop-start+2)[1:-1]
    b=spherical_linear_interpolate(points[start-1],points[stop],f)
    return np.vstack([points[:start],b,points[stop:]])

def clean_map_axis(ax):
    ax.set_facecolor('#f2f4f7')
    ax.grid(color='white', linewidth=1.0)
    for s in ax.spines.values(): s.set_color('#333333'); s.set_linewidth(0.8)
    ax.tick_params(labelsize=8, colors='#333333')
    ax.set_xlabel('Longitude', fontsize=9); ax.set_ylabel('Latitude', fontsize=9)

def panel_routes(ax, spring, autumn):
    ax.set_title('(a) Transit-focused migratory routes', loc='left', fontsize=11, weight='bold')
    for tid, recs in spring:
        lon,lat=records_lonlat(recs); ax.plot(lon,lat,color=BLUE,alpha=.48,lw=1.25)
    for tid, recs in autumn:
        lon,lat=records_lonlat(recs); ax.plot(lon,lat,color=ORANGE,alpha=.48,lw=1.25)
    ax.scatter([3.18],[51.34],s=45,color='black',zorder=5)
    ax.text(3.7,51.5,'Zeebrugge colony',fontsize=8,color=DARK)
    ax.plot([],[],color=BLUE,lw=2,label='Spring routes'); ax.plot([],[],color=ORANGE,lw=2,label='Autumn routes')
    ax.legend(frameon=True,fontsize=8,loc='lower left')
    ax.set_xlim(-20,45); ax.set_ylim(20,62); clean_map_axis(ax)

def panel_gap(ax, complete, observed, removed):
    ax.set_title('(b) A prolonged GPS gap hides route geometry', loc='left', fontsize=11, weight='bold')
    lon,lat=sphere_to_lonlat(complete); olon,olat=sphere_to_lonlat(observed); rlon,rlat=sphere_to_lonlat(removed)
    ax.plot(lon,lat,color='#bbbbbb',lw=2.0,label='Complete route')
    ax.scatter(olon,olat,s=9,color=BLUE,alpha=.65,label='Observed fixes')
    ax.plot(rlon,rlat,color=ORANGE,lw=4.0,label='Withheld / missing segment')
    ax.legend(frameon=True,fontsize=7,loc='best')
    ax.set_xlim(lon.min()-1,lon.max()+1); ax.set_ylim(lat.min()-1,lat.max()+1); clean_map_axis(ax)

def panel_recon(ax, complete, observed, bridge, samples):
    ax.set_title('(c) Deterministic bridge and route ensemble', loc='left', fontsize=11, weight='bold')
    lon,lat=sphere_to_lonlat(complete); olon,olat=sphere_to_lonlat(observed); blon,blat=sphere_to_lonlat(bridge)
    for smp in samples:
        slon,slat=sphere_to_lonlat(smp); ax.plot(slon,slat,color=PINK,lw=.8,alpha=.22)
    ax.plot(blon,blat,color=ORANGE,lw=2.4,label='Spherical bridge')
    ax.scatter(olon,olat,s=8,color=BLUE,alpha=.45,label='Observed fixes')
    ax.plot([],[],color=PINK,lw=2,label='Brownian samples')
    ax.legend(frameon=True,fontsize=7,loc='best')
    ax.set_xlim(lon.min()-1,lon.max()+1); ax.set_ylim(lat.min()-1,lat.max()+1); clean_map_axis(ax)

def panel_validation(ax, rows):
    ax.set_title('(d) Validate and calibrate envelope coverage', loc='left', fontsize=11, weight='bold')
    rows=[r for r in rows if r['season']=='spring']
    x=np.array([float(r['missing_fraction'])*100 for r in rows])
    raw=np.array([float(r['coverage_90_mean']) for r in rows])
    cal=np.array([float(r['calibrated_coverage_90_mean']) for r in rows])
    w=6
    ax.bar(x-w/2,raw,width=w,color=PINK,alpha=.75,label='Raw 90% envelope')
    ax.bar(x+w/2,cal,width=w,color=GREEN,alpha=.75,label='Calibrated envelope')
    ax.axhline(.9,color='black',ls='--',lw=1,label='Nominal 0.90')
    ax.set_xticks(x); ax.set_xticklabels([f'{int(v)}%' for v in x]); ax.set_ylim(0,1.05)
    ax.set_ylabel('Coverage'); ax.set_xlabel('Gap fraction'); ax.legend(frameon=False,fontsize=7,loc='lower right')
    ax.grid(axis='y',color='#e5e7eb')

def panel_missingness(ax, rows):
    ax.set_title('(e) Missingness mechanism changes stability', loc='left', fontsize=11, weight='bold')
    for mech,color,label in [('random_points',BLUE,'Random point loss'),('contiguous_block',ORANGE,'Contiguous gap')]:
        sub=[r for r in rows if r['missing_mechanism']==mech and r['metric']=='raw_dtw']
        sub=sorted(sub,key=lambda r:float(r['missing_fraction']))
        x=[float(r['missing_fraction'])*100 for r in sub]; y=[float(r['matrix_spearman_mean']) for r in sub]
        ax.plot(x,y,'o-',color=color,lw=2,label=label)
    ax.set_ylim(.84,1.01); ax.set_ylabel('Distance-matrix correlation'); ax.set_xlabel('Missing fraction')
    ax.legend(frameon=False,fontsize=7,loc='lower left'); ax.grid(color='#e5e7eb')

def panel_downstream(ax, rows):
    ax.set_title('(f) Reconstruction uncertainty propagates downstream', loc='left', fontsize=11, weight='bold')
    keep=[r for r in rows if r['missing_fraction']=='0.6' and r['method']=='brownian_bridge' and r['season'] in ('spring','autumn')]
    vals=[]; labels=[]; cols=[]
    for season,c in [('spring',BLUE),('autumn',ORANGE)]:
        for metric in ['raw_dtw','srvf_dtw']:
            m=[r for r in keep if r['season']==season and r['metric']==metric]
            if m:
                vals.append(float(m[0]['cluster_ari_mean'])); labels.append(f'{season}\n{metric.replace("_","-")}'); cols.append(c)
    ax.bar(range(len(vals)),vals,color=cols,alpha=.78)
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels,fontsize=7)
    ax.set_ylim(0,1); ax.set_ylabel('Cluster ARI at 60% gaps'); ax.grid(axis='y',color='#e5e7eb')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='figures/route_gap_uncertainty_framework_v2.png'); args=ap.parse_args()
    spring=select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'),80,max_trajectories=14)
    autumn=select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv'),80,max_trajectories=14)
    selected=select_trajectories(read_trajectory_points('data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv'),120,max_trajectories=20)
    tid,recs=selected[0]; scale=estimate_global_bridge_scale(selected,max_span=6); start,stop=centered_gap_indices(len(recs),.40)
    complete=records_to_sphere(recs); observed=np.vstack([complete[:start],complete[stop:]]); removed=complete[start:stop]; bridge=make_bridge(complete,start,stop)
    rng=np.random.default_rng(20260612); samples=[brownian_bridge_sphere_sample(recs,start,stop,scale,rng) for _ in range(24)]
    miss=read_rows('data/processed/missing_data_stability_summary.csv'); val=read_rows('data/processed/withheld_gap_validation_summary.csv'); bb=read_rows('data/processed/brownian_bridge_gap_reconstruction_summary.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.titlesize':11})
    fig=plt.figure(figsize=(13.2,9.0),facecolor='white')
    gs=gridspec.GridSpec(3,3,figure=fig,width_ratios=[1.45,1,1],height_ratios=[1.05,1,1],wspace=.34,hspace=.40)
    panel_routes(fig.add_subplot(gs[:,0]),spring,autumn)
    panel_gap(fig.add_subplot(gs[0,1]),complete,observed,removed)
    panel_recon(fig.add_subplot(gs[0,2]),complete,observed,bridge,samples)
    panel_validation(fig.add_subplot(gs[1,1]),val)
    panel_missingness(fig.add_subplot(gs[1,2]),miss)
    panel_downstream(fig.add_subplot(gs[2,1:3]),bb)
    fig.suptitle('How prolonged GPS gaps affect migratory-route comparison',fontsize=15,weight='bold',y=.985)
    fig.text(.5,.955,'Observed routes are stress-tested by withholding gaps, reconstructing plausible alternatives, validating coverage, and propagating uncertainty to route-comparison outputs.',ha='center',fontsize=9.5,color=GREY)
    out=Path(args.output); out.parent.mkdir(exist_ok=True,parents=True); fig.savefig(out,dpi=320,bbox_inches='tight'); plt.close(fig)
    print(f'Wrote: {out}'); print(f'Example route: {tid}; scale={scale:.6g}')
if __name__=='__main__': main()
