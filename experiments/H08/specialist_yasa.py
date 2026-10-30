"""Apply the published EEG-only YASA checkpoint to identical supplied test-night signals."""
from pathlib import Path
import json,hashlib,time,importlib.metadata
import numpy as np,mne,yasa
R=Path(__file__).resolve().parents[2];D=R/'experiments/H08';C=R/'data/cache/H08'
with np.load(C/'data.npz') as z:x=z['test_x']
assert yasa.__version__=='0.8.1';pred=[];start=time.perf_counter();model_paths=[]
for i,night in enumerate(x):
 raw=mne.io.RawArray(night.reshape(1,-1)*1e-6,mne.create_info(['EEG Fpz-Cz'],100,ch_types=['eeg']),verbose='ERROR');staging=yasa.SleepStaging(raw,eeg_name='EEG Fpz-Cz');hyp=staging.predict();print('YASA night',i,'model',getattr(staging,'_clf',None),flush=True)
 labels=np.asarray(hyp.hypno);mapping={'WAKE':0,'W':0,'N1':1,'N2':2,'N3':3,'REM':4,'R':4};values=np.array([mapping[str(v)] for v in labels],int);assert len(values)==1440;pred.append(values)
elapsed=time.perf_counter()-start;dest=R/'results/predictions/H08/specialist--yasa-eeg.npz';dest.parent.mkdir(exist_ok=True,parents=True);np.savez_compressed(dest,predictions=np.asarray(pred));weights=list(Path(yasa.__file__).parent.rglob('*.joblib'));info=dict(model='yasa-eeg',seconds=elapsed,prediction_file=str(dest.relative_to(R)),prediction_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),yasa_version=yasa.__version__,checkpoint_files=[dict(name=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in weights],runtime={name:importlib.metadata.version(name) for name in ['yasa','mne','lightgbm','numpy','scipy','pandas','scikit-learn','antropy','numba']},selection='default EEG-only,no EOG/EMG/demographics,no test-label tuning; NSRRpretrained')
(D/'specialist-runtime.json').write_text(json.dumps(info,indent=2));print('YASA prediction complete',elapsed)
