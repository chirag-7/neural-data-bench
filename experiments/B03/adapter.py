"""Synthetic rigid motion from fixed voltage-derived peak-depth rasters.

This is a processed-observation motion-registration diagnostic, not real drift
ground truth, raw-voltage processing or an official leaderboard reproduction.
"""
from pathlib import Path
import hashlib,json,time
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
CACHE=ROOT/'data/cache/B03'
DURATION=90
FS=20000.
BIN_UM=5.
BIN_S=1.
SEEDS=(2026110101,2026110102,2026110103,2026110104,2026110201,2026110202,2026110203,2026110204)
PROBE=dict(num_columns=2,num_contact_per_column=32,xpitch=32,ypitch=20,y_shift_per_column=[0,0],contact_shapes='circle',contact_shape_params={'radius':5})
TEMPLATES=dict(mode='ellipsoid',ms_before=1.5,ms_after=3.,unit_params=dict(alpha=(100.,500.),spatial_decay=(10.,45.),ellipse_angle=(0.,2*np.pi),ellipse_shrink=(.4,1.)))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def config(index):
 seed=SEEDS[index];profile=('zigzag','random_walk')[index%2]
 # Balanced profile/noise regimes in both independently generated populations.
 noise=(6.,10.) if index%4<2 else (10.,14.)
 motion=dict(drift_mode=profile,amplitude_factor=1.,non_rigid_gradient=None,t_start_drift=0.,t_end_drift=None)
 if profile=='zigzag':motion['period_s']=31. if index<4 else 37.
 return dict(num_units=64,duration=float(DURATION),sampling_frequency=FS,seed=seed,
  generate_probe_kwargs=PROBE,
  generate_unit_locations_kwargs=dict(margin_um=20.,minimum_z=5.,maximum_z=45.,minimum_distance=18.,distribution='uniform',distance_strict=False,max_iteration=100),
  generate_displacement_vector_kwargs=dict(displacement_sampling_frequency=5.,drift_start_um=[0.,30.],drift_stop_um=[0.,-30.],drift_step_um=2.,motion_list=[motion]),
  generate_templates_kwargs=TEMPLATES,generate_sorting_kwargs=dict(firing_rates=(2.,8.),refractory_period_ms=4.),
  generate_noise_kwargs=dict(noise_levels=noise,spatial_decay=25.),amplitude_std=.15,extra_outputs=True)

def prepare():
 import spikeinterface as si
 import probeinterface
 from spikeinterface.generation import generate_drifting_recording
 from spikeinterface.core import get_noise_levels
 from spikeinterface.preprocessing import bandpass_filter
 from spikeinterface.sortingcomponents.peak_detection import detect_peaks
 from spikeinterface.sortingcomponents.peak_localization import localize_peaks
 from spikeinterface.sortingcomponents.motion.motion_utils import make_2d_motion_histogram,get_spatial_bin_edges
 assert si.__version__=='0.105.4' and probeinterface.__version__=='0.4.2'
 (CACHE/'raw').mkdir(parents=True,exist_ok=True)
 histograms=[];targets=[];records=[]
 for i,seed in enumerate(SEEDS):
  params=config(i);start=time.monotonic();dest=CACHE/'raw'/f'simulation-{i:02d}.npz';meta=dest.with_suffix('.json')
  if not dest.exists():
   static,drifting,sorting,extra=generate_drifting_recording(**params)
   recording=bandpass_filter(drifting,freq_min=300.,freq_max=6000.,filter_order=3,dtype='float32')
   noise=get_noise_levels(recording,return_in_uV=False,random_slices_kwargs=dict(num_chunks_per_segment=20,chunk_size=4000,seed=seed+51),n_jobs=1,progress_bar=False)
   peaks=detect_peaks(recording,method='locally_exclusive',method_kwargs=dict(peak_sign='neg',detect_threshold=5.,exclude_sweep_ms=1.,radius_um=50.,noise_levels=noise),job_kwargs=dict(n_jobs=1,chunk_duration='1s',progress_bar=False))
   locations=localize_peaks(recording,peaks,method='center_of_mass',method_kwargs=dict(radius_um=60.,feature='ptp'),ms_before=.5,ms_after=.5,job_kwargs=dict(n_jobs=1,chunk_duration='1s',progress_bar=False))
   depths=get_spatial_bin_edges(recording,'y',20.,BIN_UM)
   raster,tedges,dedges=make_2d_motion_histogram(recording,peaks,locations,direction='y',bin_s=BIN_S,spatial_bin_edges=depths,weight_with_amplitude=False,depth_smooth_um=None,time_smooth_s=None)
   # Injector holds a5Hz state, then selects the nearest2um template position.
   state=np.asarray(extra['unit_displacements'][:,0,1],dtype=float)
   assert np.all(extra['displacement_unit_factor']==1)
   assert np.allclose(extra['unit_displacements'][:,:,1],state[:,None])
   grid=np.arange(30.,-30.01,-2.)
   quantized=grid[np.argmin(np.abs(grid[:,None]-state[None,:]),axis=0)]
   target=quantized.reshape(DURATION,5).mean(axis=1);target-=target.mean()
   assert raster.shape==(90,132) and len(tedges)==91
   np.savez_compressed(dest,histogram=raster.astype(np.float32),target=target.astype(np.float32),
    peaks=peaks,peak_locations=locations,unit_locations=extra['unit_locations'],
    unit_displacements=extra['unit_displacements'],displacement_vectors=extra['displacement_vectors'],
    quantized_displacement_5hz=quantized,temporal_edges=tedges,depth_edges=dedges,
    noise_estimate_uv=noise,geometry=recording.get_channel_locations(),spike_vector=sorting.to_spike_vector())
   # A fixed response-independent voltage chunk seals the generator/noise/filter.
   first=recording.get_traces(start_frame=0,end_frame=int(FS))
   info=dict(simulation=i,split='train' if i<4 else 'test',parameters=params,
    raw_n_events=int(sorting.count_total_num_spikes()),detected_peaks=int(len(peaks)),
    histogram_count=int(raster.sum()),noise_median_uv=float(np.median(noise)),
    voltage_first_second_sha256=hashlib.sha256(np.ascontiguousarray(first).tobytes()).hexdigest(),
    source_array_sha256=sha(dest),seconds_prepare=time.monotonic()-start)
   meta.write_text(json.dumps(info,indent=2)+'\n')
   del static,drifting,recording,sorting,extra
  info=json.loads(meta.read_text());assert info['parameters']==json.loads(json.dumps(params))
  assert sha(dest)==info['source_array_sha256']
  with np.load(dest,allow_pickle=False) as z:
   histograms.append(z['histogram']);targets.append(z['target'])
  records.append(info);print('prepared',i,info['detected_peaks'],round(time.monotonic()-start,2),flush=True)
 x=np.stack(histograms);y=np.stack(targets)
 arrays=dict(train_x=x[:4],train_y=y[:4],test_x=x[4:],test_y=y[4:],train_groups=np.arange(4),test_groups=np.arange(4,8))
 np.savez_compressed(CACHE/'data.npz',**arrays)
 manifest=dict(benchmark_id='B03',origin='SIMULATED; SpikeInterface official procedural ellipsoid templates, noise and drift, not measured biological recordings',
  software=dict(spikeinterface=si.__version__,probeinterface=probeinterface.__version__),records=records,
  n_simulations=8,total_duration_seconds=8*DURATION,data_sha256=sha(CACHE/'data.npz'),
  prepared_bytes=(CACHE/'data.npz').stat().st_size,retained_simulation_archive_bytes=sum(p.stat().st_size for p in (CACHE/'raw').glob('*.npz')),
  shapes={k:list(v.shape) for k,v in arrays.items()},selection='Every simulation, all90one-second bins, no scoring/activity-based exclusions',
  license='Generated procedural arrays; source generator and preserved code MIT. No third-party real voltage or paired biological labels included.')
 (P/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 metadata=dict(benchmark_id='B03',status='prepared awaiting scientific review/freeze',primary_metric='recording_mean_motion_rmse_um',
  truth_type='known quantized simulator displacement, never algorithm-estimated gold',
  input='N independent simulated recordings x90 timebins x132 depthbins, detected peak counts;1second x5micrometer bins, spatialrange[-20,640]um',
  input_description='Processed rasters of detected/center-of-mass-localized peaks from noisy drifting64channel voltage. No true events, true positions, templates, seeds or drift trajectories given for test.',
  units={'inputs':'detected peak counts/bin','outputs':'relative rigid tissue displacement micrometers'},
  normalization='None; raw count histograms, no smoothing. Target and scorer remove constant temporal mean per recording to fix translation gauge.',
  baseline_name='SpikeInterface0.105.4 decentralized pairwise raster registration + global LSMR, fixed parameters',
  test_groups=[4,5,6,7],train_groups=[0,1,2,3],superiority_eligible=False,
  limitations='Synthetic ellipsoid waveform family, rigid-only processed-raster diagnostic;4heldout seeds, not biological generalization or current DREDge/SOTA claim')
 (CACHE/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n');(P/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 return manifest

def load():
 with np.load(CACHE/'data.npz',allow_pickle=False) as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def baseline(train_x,train_y,test_x):
 """Original SI specialist numerical routines on exactly the supplied rasters."""
 from spikeinterface.sortingcomponents.motion.decentralized import compute_pairwise_displacement,compute_global_displacement
 outputs=[]
 for raster in test_x:
  displacements,weights=compute_pairwise_displacement(np.asarray(raster,dtype=float),BIN_UM,conv_engine='numpy',
   max_displacement_um=60.,corr_threshold=.1,weight_scale='linear',normalized_xcorr=True,centered_xcorr=True,
   bin_s=BIN_S,time_horizon_s=None,progress_bar=False)
  shift=compute_global_displacement(displacements,pairwise_displacement_weight=weights,
   convergence_method='lsmr',temporal_prior=True,spatial_prior=False,soft_weights=False,progress_bar=False)
  shift=np.asarray(shift).reshape(-1);outputs.append(shift-shift.mean())
 return np.stack(outputs)

def score(predictions,truth,test_x=None):
 p=np.asarray(predictions,dtype=float);y=np.asarray(truth,dtype=float)
 if p.shape!=y.shape or p.shape!=(4,90) or not np.isfinite(p).all():raise ValueError('Expected finite displacement shape(4,90)')
 p=p-p.mean(axis=1,keepdims=True);y=y-y.mean(axis=1,keepdims=True)
 error=p-y;per=np.sqrt(np.mean(error**2,axis=1))
 return dict(score=float(per.mean()),metric='recording_mean_motion_rmse_um',direction='lower',per_unit=per.tolist(),
  recording_mae_um=np.mean(np.abs(error),axis=1).tolist(),recording_max_error_um=np.max(np.abs(error),axis=1).tolist())

if __name__=='__main__':
 m=prepare();print(json.dumps({k:v for k,v in m.items() if k!='records'},indent=2))
