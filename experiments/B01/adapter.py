"""Blind unsupervised sorting of the standard 10s MEArec simulation fixture."""
from pathlib import Path
import hashlib
import json
import urllib.request
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/B01"
REVISION = "71e5c5b04e34ab9e69533a4fb092a6ce4d244034"
URL = f"https://gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/{REVISION}/mearec/mearec_test_10s.h5"
MS5_PARAMETERS = {"detect_threshold":5.5,"detect_channel_radius":100.,"detect_time_radius_msec":.5,"detect_sign":-1,"snippet_T1":20,"snippet_T2":44,"snippet_mask_radius":150.,"npca_per_channel":3,"npca_per_subdivision":10,"skip_alignment":False}
WHITEN_PARAMETERS = {"apply_mean":True,"regularize":True,"regularize_kwargs":{"method":"GraphicalLassoCV"},"mode":"global","seed":20261030,"num_chunks_per_segment":20,"chunk_size":10000,"chunk_duration":None}
COMPARE_PARAMETERS = {"delta_time":.4,"match_score":.5,"chance_score":.1,"well_detected_score":.8,"redundant_score":.2,"overmerged_score":.2,"exhaustive_gt":True,"match_mode":"hungarian","agreement_method":"count"}

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare():
    import h5py
    CACHE.mkdir(parents=True, exist_ok=True)
    raw = CACHE / "mearec_test_10s.h5"
    if not raw.exists():
        with urllib.request.urlopen(URL,timeout=180) as r:
            raw.write_bytes(r.read())
    with h5py.File(raw) as f:
        recording = np.asarray(f["recordings"],dtype=np.float32)
        positions = np.asarray(f["channel_positions"],dtype=np.float64)
        fs = float(f["info/recordings/fs"][()])
        timestamps = np.asarray(f["timestamps"])
        assert fs == 32000 and recording.shape == (320000,32) and positions.shape == (32,3)
        assert np.isfinite(recording).all() and np.isfinite(positions).all()
        assert np.allclose(timestamps,np.arange(320000)/fs,atol=1e-12)
        assert not bool(f["info/recordings/drifting"][()])
        assert bool(f["info/recordings/filter"][()])
        units = sorted(f["spiketrains"].keys(),key=int)
        truth=[];counts=[]
        for unit in units:
            times=np.asarray(f[f"spiketrains/{unit}/times"],dtype=np.float64)
            # Matches SI NeoSortingSegment conversion: multiply seconds byfs then astype int64.
            samples=(times*fs).astype(np.int64)
            assert np.all((samples>=0)&(samples<len(recording))) and np.all(np.diff(samples)>0)
            counts.append(len(samples));truth.extend((int(t),int(unit)) for t in samples)
        seeds={k:int(f[f"info/seeds/{k}"][()]) for k in f['info/seeds']}
        noise_level=float(f["info/recordings/noise_level"][()])
        mearec_version=str(f.attrs["mearec_version"])
    truth=np.array(sorted(truth),dtype=np.int64)
    np.savez_compressed(CACHE/"inputs.npz",recording_uv=recording,fs=np.array(fs),channel_positions_um=positions)
    np.savez_compressed(CACHE/"truth.npz",events=truth,unit_ids=np.array(list(map(int,units))))
    meta={"benchmark_id":"B01","slice_id":"mearec-standard-10s-blind-sorting-v1","dataset":"MEArec standard SpikeInterface/Neo test fixture","data_origin":"SIMULATED extracellular waveforms and spike trains, not paired real biological ground truth","resource_relationship":"Additional standard MEArec/SpikeInterface resource for B01 spike sorting; no claim that an official SpikeForest paired-data protocol was executed","metric":"mean_gt_accuracy","direction":"higher","interface":"sort(recording_uv,fs,channel_positions_um)->int64 event array(n_events,2)","task_description":"Blind unsupervised spike sorting. Receive a float32 extracellular recording of shape(320000,32), sampling rate32000Hz, and32x3 electrode positions in micrometers. Signal amplitudes are microvolts; source signal is already bandpass filtered300–6000Hz. Return an integer array(n_events,2) with sample index in column0 and arbitrary nonnegative neuron/cluster ID in column1, sorted bysample thenunit. Infer unit count and templates from the supplied voltage only; no ground-truth times, labels, simulated source templates or true unit count are supplied. The entire10-second recording may be used unsupervised for detection/clustering; this is not supervised train/test fitting. Predictions are matched to hidden truth by the official SpikeInterface event/unit scorer.","input_shape":list(recording.shape),"sampling_rate_hz":fs,"duration_seconds":len(recording)/fs,"input_units":"microvolts","channel_position_units":"micrometers","source_filter_hz":[300,6000],"drifting":False,"grouping":"one simulated recording/seed,32 channels; units/events are not independent biological preparations","split":"unlabeled whole-recording sorting; hidden ground-truth event labels scored externally; no supervised training cases or independent recording holdout","adaptation":"unsupervised/transductive waveform/template/clustering estimation on the scored voltage is allowed, as in spike sorting","gt_scorer_only":{"n_units":len(units),"event_counts_per_unit":counts,"total_events":len(truth),"truth_time_conversion":"floor(seconds*fs) via astype(int64), matching SI NeoSortingSegment"},"baseline":"MountainSort5 0.5.9 scheme1 with frozen preprocessing/configuration, no truth-derived templates or parameter selection","baseline_role":"reproduced neuroscience-specific spike sorter; not verified current SOTA","whitening_parameters":WHITEN_PARAMETERS,"mountainsort5_parameters":MS5_PARAMETERS,"comparison_parameters":COMPARE_PARAMETERS,"scorer":"SpikeInterface0.105.4 compare_sorter_to_ground_truth; per-GT-unit accuracy TP/(TP+FN+FP), Hungarian one-to-one matching; mean over all GT units, unmatched GT=0","score_limitations":"Mean GT-unit accuracy does not fully penalize extra unmatched output units; always report false-positive/redundant/overmerged unit counts and predicted unit count alongside it","current_best_status":"not verified for this fixture and protocol; no imported old tutorial scores","source":URL,"source_revision":REVISION,"mearec_version":mearec_version,"generation_seeds":seeds,"noise_std_uv":noise_level,"data_license":"Primary repository README declares ODbL1.0 for database and links CC-BY-SA4.0 for individual contents; cache and derivatives retain those terms, distinct from code license","license_source":"https://gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/"+REVISION+"/README.md","source_sha256":sha256(raw),"inputs_sha256":sha256(CACHE/"inputs.npz"),"truth_sha256":sha256(CACHE/"truth.npz"),"limitations":["One short standard public MEArec1.5.1 simulation only; no paired-real, drift, cross-recording or cross-lab claim","Ground-truth spike timing and templates are known from generation but never passed to sorting programs","Source fixture/public labels may have been included in model pretraining","Simulated waveforms/noise may favor algorithms differently from real recordings","Small number of spikes per unit limits stable waveform estimation and collision analysis","Sorting is unsupervised on the same voltage being scored; this must not be described as independent supervised test generalization","Mean per-unit accuracy alone can hide excess false-positive output clusters; unit-category diagnostics are required"]}
    (CACHE/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n")
    manifest={"benchmark_id":"B01","accessed_on":"2026-10-30","source_revision":REVISION,"files":[{"url":URL,"path":"data/cache/B01/mearec_test_10s.h5","bytes":raw.stat().st_size,"sha256":sha256(raw)}],"prepared":[{"path":"data/cache/B01/inputs.npz","sha256":meta["inputs_sha256"],"model_accessible":True},{"path":"data/cache/B01/truth.npz","sha256":meta["truth_sha256"],"model_accessible":False}],"data_origin":meta["data_origin"],"data_terms":meta["data_license"],"license_source":meta["license_source"],"attribution":"NeuralEnsemble electrophysiology testing data; MEArec by Buccino & Einevoll; SpikeInterface standard test fixture","redistribution":"Raw/prepared data stay ignored cache; tracked acquisition code/manifests preserve terms"}
    (REPO/"data/manifests/B01.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return meta

def load():
    with np.load(CACHE/"inputs.npz",allow_pickle=False) as d:
        return d["recording_uv"].copy(),float(d["fs"]),d["channel_positions_um"].copy()

def load_truth():
    with np.load(CACHE/"truth.npz",allow_pickle=False) as d:
        return d["events"].copy(),d["unit_ids"].copy()

def validate_events(events,n_samples=320000):
    events=np.asarray(events)
    if events.shape == (0,):events=events.reshape(0,2)
    assert events.ndim==2 and events.shape[1]==2,"Expected shape(n_events,2)"
    assert np.issubdtype(events.dtype,np.integer),"Event fields must be integer sample indices and IDs"
    assert np.all((events[:,0]>=0)&(events[:,0]<n_samples)) and np.all(events[:,1]>=0)
    assert len(np.unique(events,axis=0))==len(events),"Duplicate events within the same unit are invalid"
    return events[np.lexsort((events[:,1],events[:,0]))].astype(np.int64)

def baseline(recording_uv,fs,channel_positions_um):
    import spikeinterface as si
    import spikeinterface.preprocessing as spre
    import mountainsort5 as ms5
    assert si.__version__=="0.105.4" and ms5.__version__=="0.5.9"
    np.random.seed(20261030)
    r=si.NumpyRecording(recording_uv,sampling_frequency=fs)
    # Source probe lies in the y/z plane (all x=0). SI's convenience setter
    # otherwise projects xyz onto xy, creating duplicate contact positions.
    # y/z preserves every physical Euclidean distance; no score-driven change.
    assert np.ptp(channel_positions_um[:,0])==0
    r.set_channel_locations(channel_positions_um[:,1:3])
    r=spre.whiten(r,**WHITEN_PARAMETERS)
    sorting=ms5.sorting_scheme1(r,sorting_parameters=ms5.Scheme1SortingParameters(**MS5_PARAMETERS))
    events=[]
    for label,unit in enumerate(sorting.get_unit_ids()):
        events.extend((int(t),label) for t in sorting.get_unit_spike_train(unit))
    return validate_events(np.asarray(events,dtype=np.int64))

def score(events):
    import spikeinterface as si
    import spikeinterface.comparison as sc
    assert si.__version__=="0.105.4"
    events=validate_events(events)
    truth,unit_ids=load_truth()
    if not len(events):
        return {"mean_gt_accuracy":0.,"mean_precision":0.,"mean_recall":0.,"n_predicted_units":0,"n_gt_units":len(unit_ids),"per_gt_unit_accuracy":{str(u):0. for u in unit_ids}}
    def obj(e,ids):
        return si.NumpySorting.from_unit_dict({int(u):e[e[:,1]==u,0].astype(np.int64) for u in ids},sampling_frequency=32000.)
    comparison=sc.compare_sorter_to_ground_truth(obj(truth,unit_ids),obj(events,np.unique(events[:,1])),**COMPARE_PARAMETERS)
    per=comparison.get_performance(method="by_unit")
    return {"mean_gt_accuracy":float(per["accuracy"].mean()),"mean_precision":float(per["precision"].mean()),"mean_recall":float(per["recall"].mean()),"n_gt_units":len(unit_ids),"n_predicted_units":len(np.unique(events[:,1])),"n_predicted_events":len(events),"well_detected_unit_ids":list(map(int,comparison.get_well_detected_units())),"false_positive_unit_ids":list(map(int,comparison.get_false_positive_units())),"redundant_unit_ids":list(map(int,comparison.get_redundant_units())),"overmerged_unit_ids":list(map(int,comparison.get_overmerged_units())),"per_gt_unit_accuracy":{str(u):float(per.loc[u,"accuracy"]) for u in unit_ids},"per_gt_unit_metrics":{str(u):{k:float(v) for k,v in per.loc[u].items()} for u in unit_ids},"scorer":"SpikeInterface0.105.4","comparison_parameters":COMPARE_PARAMETERS}

if __name__=="__main__":
    print(json.dumps(prepare(),indent=2))
