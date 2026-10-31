"""Bird-disjoint annotated Bengalese-finch song event detection from numeric audio."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];CACHE=ROOT/'data/cache/A15'
FS=32000;HOP=32;DT=.001;SEED=20261031
BIRDS=['bl26lb16','gr41rd51','gy6or6','or60yw70'];TEST_BIRD='or60yw70'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def intervals(mask):
    x=np.asarray(mask,dtype=bool);edges=np.diff(np.r_[False,x,False].astype(np.int8));return np.c_[np.flatnonzero(edges==1),np.flatnonzero(edges==-1)]*DT

def prepare():
    files=json.loads((CACHE/'selected-source-files.json').read_text());audio=sorted([r['name'] for r in files if r['name'].endswith('.npz')]);assert len(audio)==80
    records=[];waves=[];ys=[];events=[];merge_count=0
    for name in audio:
        bird=name.split('_')[0];assert bird in BIRDS
        with np.load(CACHE/name,allow_pickle=False) as z:
            wave=z['data'].astype(np.float32);assert int(z['samplerate'])==FS and wave.ndim==1 and np.isfinite(wave).all()
        rows=list(csv.DictReader((CACHE/(name[:-4]+'_annotations.csv')).open()))
        # Upstream DAS headers incorrectly say seconds. Exact original-source comparison confirms milliseconds.
        times=np.array(sorted((float(r['start_seconds'])/1000,float(r['stop_seconds'])/1000) for r in rows))
        assert times.ndim==2 and times.shape[1]==2 and np.all(times[:,1]>times[:,0]) and np.all(times>=0) and np.max(times)<=len(wave)/FS+1/FS
        n=len(wave)//HOP;centres=(np.arange(n)+.5)*DT;y=np.zeros(n,dtype=np.int8)
        for a,b in times:
            left=max(0,int(np.ceil(a/DT-.5-1e-9)));right=min(n,int(np.ceil(b/DT-.5-1e-9)));y[left:right]=1
        count=len(intervals(y));merge_count+=len(times)-count
        records.append(dict(recording=name[:-4],bird=bird,n_samples=len(wave),n_frames=n,duration_seconds=len(wave)/FS,n_source_events=len(times),n_rasterized_runs=count,split='test' if bird==TEST_BIRD else 'train'))
        waves.append(wave);ys.append(y);events.append(times)
    arrays={}
    for split in ['train','test']:
        idx=[i for i,r in enumerate(records) if r['split']==split];width=max(records[i]['n_frames']+int(records[i]['n_samples']%HOP!=0) for i in idx)
        x=np.full((len(idx),width*HOP),np.nan,dtype=np.float32);y=np.full((len(idx),width),-1,dtype=np.int8)
        ev=np.full((len(idx),max(len(events[i]) for i in idx),2),np.nan,dtype=np.float64)
        for j,i in enumerate(idx):x[j,:len(waves[i])]=waves[i];y[j,:len(ys[i])]=ys[i];ev[j,:len(events[i])]=events[i]
        arrays.update({split+'_x':x,split+'_y':y,split+'_events':ev,split+'_groups':np.array([records[i]['bird'] for i in idx]),split+'_units':np.array([records[i]['recording'] for i in idx]),split+'_lengths':np.array([records[i]['n_samples'] for i in idx])})
    np.savez_compressed(CACHE/'data.npz',**arrays)
    meta=dict(benchmark_id='A15',slice_id='das-bengalese-birdholdout-song-events-v1',status='prepared for parent review; not frozen or scored',
        dataset='DAS Bengalese finch train/test data derived from Nicholson/Queen/Sober Bengalese Finch Song Repository',
        source='https://doi.org/10.25625/ENKMJS',source_doi_actual='10.25625/ENKMJS',
        sampling_rate_hz=FS,input='float32 (whole_recordings,padded_audio_samples), numeric monaural waveforms in source native arbitrary amplitude units; NaN only after recording end',
        units='Input source amplitude units, not calibrated volts; upstream float16 audio converted losslessly to float32. Targets1ms binary masks of annotated song syllables, -1 outside full valid1ms bins',
        label_encoding={'-1':'padding/unscored','0':'no annotated syllable','1':'annotated song syllable of any original bird-specific type'},
        output='Integer0/1 array(n_test_recordings,test_x.shape[1]//32); ignore source NaN padding. Consecutive positive1ms bins become one predicted event.',
        grouping='individual male Bengalese finch; three training birds, one entirely held-out bird; all recordings intact',
        train_birds=BIRDS[:3],test_birds=[TEST_BIRD],n_train=60,n_test=20,train_shape=list(arrays['train_x'].shape),test_shape=list(arrays['test_x'].shape),train_y_shape=list(arrays['train_y'].shape),test_y_shape=list(arrays['test_y'].shape),
        split='Take20 paired audio files per bird with smallest SHA256(filename), independent of audio/labels; lexical last bird or60yw70 held out; sort selected filenames before arrays',
        selection_count_per_bird=20,source_events=sum(len(e) for e in events),rasterization_merged_or_lost_events=int(merge_count),duration_seconds={s:sum(r['duration_seconds'] for r in records if r['split']==s) for s in ['train','test']},
        metric='recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset',primary_metric='recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset',direction='higher',
        event_matching='One-to-one maximum-cardinality matching; abs onset error<=20ms AND abs offset error<=max(20ms,20% reference-event duration); original converted-source intervals are scorer truth',
        aggregation='F1=2TP/(Npred+Ntrue) within each complete recording; average recordings equally. Only one test bird, so no population-level animal uncertainty claim',
        reference='Fixed log-spectral-feature HistGradientBoosting; every fifth whole training recording validates global threshold/gap/minimum duration, then refit all training recordings; no bird IDs or pretrained weights',
        model_signature='fit_predict(train_x,train_y,test_x,train_groups)',train_groups_use='None for reference and general submissions; preparation/scoring retains bird IDs only to establish outer split; fixed inner validation rows0,5,10,... from60 whole training recordings, exposed equally',
        normalization='No prepared amplitude normalization. Deterministic per-recording waveform/spectral normalization allowed equally for references and general submissions; no jointly test-fitted population transforms',
        annotation_units='DAS *_seconds CSV fields contain milliseconds, corrected by1/1000; independently verified against all90 original source events in same named gy6or6 recording',
        truth_type='Original annotated song syllable events, with amplitude-segmented boundaries and human-assigned syllable labels; not pristine independent hand-drawn boundaries or exhaustive all-call detection',
        license='DAS Dataverse release CC0-1.0; underlying original Nicholson/Queen/Sober audio/annotations CC BY4.0, retained with attribution; combined reuse follows CC BY4.0 attribution',
        terms_url='https://creativecommons.org/licenses/by/4.0/',
        limitations=['Only one held-out bird; recordings correlated within bird and this does not establish multi-animal population generalization',
        'Source annotations use amplitude-threshold segmentation followed by manual syllable labeling; boundaries are not wholly independently hand drawn',
        'Source contact calls may be incompletely annotated; target is reproduction of annotated song intervals, not exhaustive detection of every animal sound',
        'Source recordings were amplitude-triggered and curated for song bouts; background is not an unbiased continuous laboratory recording',
        'Binary mapping merges arbitrary bird-specific syllable labels; no syllable taxonomy or species classification claim',
        'Source audio is already float16 quantized; no calibrated acoustic level or native multimodal LLM perception claim',
        '1ms target rasterization can merge rare gaps shorter than1ms; exact source-event truth and fixed20ms matching tolerance remain documented'],
        models=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol'],reasoning_effort='high',generation_count_per_model=1,tool_access_during_generation=False,numeric_cpu_threads=1,timeout_seconds=180,line_limit_exclusive=240,data_sha256=sha(CACHE/'data.npz'))
    source=json.loads((CACHE/'das-dataset-metadata.json').read_text())['data']
    meta['source_doi_actual']=source['datasetPersistentId'].removeprefix('doi:')
    meta['source']='https://doi.org/'+meta['source_doi_actual']
    meta['train_groups_supplied']=False
    meta['prompt_brief']=Path(__file__).with_name('context-brief.txt').read_text()
    meta['validation_information']='Reference/general receive no source IDs; fixed training validation rows0,5,...55; reference uses training masks only'
    (CACHE/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');(CACHE/'row-manifest.json').write_text(json.dumps(records,indent=2)+'\n');return meta

def load():
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:return tuple(d[k].copy() for k in ['train_x','train_y','test_x','test_y'])

def event_f1(pred_events,true_events):
    from scipy.optimize import linear_sum_assignment
    p=np.asarray(pred_events).reshape(-1,2);t=np.asarray(true_events).reshape(-1,2)
    if len(p)==0 or len(t)==0:return (1. if len(p)==len(t)==0 else 0.),0
    valid=(np.abs(p[:,None,0]-t[None,:,0])<=.020+1e-12)&(np.abs(p[:,None,1]-t[None,:,1])<=np.maximum(.020,.2*(t[:,1]-t[:,0]))[None,:]+1e-12)
    a,b=linear_sum_assignment(valid.astype(np.int8),maximize=True);tp=int(valid[a,b].sum());return 2.*tp/(len(p)+len(t)),tp

def score(pred,truth,test_x=None):
    p=np.asarray(pred)
    if p.shape!=truth.shape or not np.isfinite(p).all() or not np.isin(p,[0,1]).all():raise ValueError('Expected finite binary1ms masks with test_y shape')
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:
        assert np.array_equal(truth,d['test_y']);events=d['test_events'];units=d['test_units']
    per=[];tps=[];nps=[];nts=[]
    for i in range(len(p)):
        pe=intervals(p[i,:np.sum(truth[i]>=0)]==1);te=events[i][np.isfinite(events[i,:,0])];value,tp=event_f1(pe,te);per.append(value);tps.append(tp);nps.append(len(pe));nts.append(len(te))
    return dict(score=float(np.mean(per)),metric='recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset',direction='higher',per_unit=per,unit_ids=units.tolist(),true_positive_events=tps,predicted_event_counts=nps,reference_event_counts=nts,unit_definition='whole recording; all20 test recordings from one held-out bird')

def baseline(train_x,train_y,test_x):
    """Fixed conventional reference; no learned weights imported or method run pre-freeze."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from scipy.signal import stft
    from scipy.ndimage import uniform_filter1d
    def features(v):
        v=v[np.isfinite(v)].astype(float);n=len(v)//HOP
        _,_,z=stft(np.pad(v,(112,144),mode='reflect'),fs=FS,nperseg=256,noverlap=224,boundary=None,padded=False)
        power=(np.abs(z[:,:n])**2).astype(np.float32);bands=np.array_split(np.arange(2,97),24)
        band=np.log1p(np.stack([power[b].sum(axis=0) for b in bands],axis=1));noise=np.percentile(band,20,axis=0)
        total=np.log1p(power[2:97].sum(axis=0));relative=total-np.percentile(total,20)
        return np.c_[band-noise,relative,uniform_filter1d(relative,size=5),uniform_filter1d(relative,size=15)].astype(np.float32)
    fs=[features(v) for v in train_x];xt=[features(v) for v in test_x];ys=[y[y>=0] for y in train_y];assert all(len(a)==len(b) for a,b in zip(fs,ys))
    def fit(indices):
        x=np.concatenate([fs[i] for i in indices]);y=np.concatenate([ys[i] for i in indices]);rng=np.random.default_rng(SEED)
        keep=np.sort(rng.choice(len(y),min(60000,len(y)),replace=False));model=HistGradientBoostingClassifier(max_iter=80,max_leaf_nodes=15,learning_rate=.1,l2_regularization=10.,max_bins=128,random_state=SEED).fit(x[keep],y[keep]);return model
    validation=np.arange(len(fs))[::5];training=np.setdiff1d(np.arange(len(fs)),validation)
    model=fit(training);validation_prob=[model.predict_proba(fs[i])[:,1] for i in validation]
    def clean(prob,threshold,gap,minimum):
        mask=prob>=threshold
        for a,b in intervals(~mask):
            start,end=int(round(a/DT)),int(round(b/DT))
            if start>0 and end<len(mask) and end-start<=gap:mask[start:end]=True
        for a,b in intervals(mask):
            start,end=int(round(a/DT)),int(round(b/DT))
            if end-start<minimum:mask[start:end]=False
        return mask
    best=-1.;choice=None
    for threshold in [.3,.5,.7]:
        for gap in [0,4,8]:
            for minimum in [5,10,20]:
                per=[event_f1(intervals(clean(p,threshold,gap,minimum)),intervals(ys[i]==1))[0] for p,i in zip(validation_prob,validation)]
                value=np.mean(per)
                if value>best:best=value;choice=(threshold,gap,minimum)
    model=fit(np.arange(len(fs)));output=np.zeros((len(test_x),test_x.shape[1]//HOP),dtype=np.int8)
    for i,x in enumerate(xt):output[i,:len(x)]=clean(model.predict_proba(x)[:,1],*choice)
    return output

if __name__=='__main__':
    m=prepare();print({k:m[k] for k in ['train_shape','test_shape','train_y_shape','test_y_shape','duration_seconds','source_events','rasterization_merged_or_lost_events']})
