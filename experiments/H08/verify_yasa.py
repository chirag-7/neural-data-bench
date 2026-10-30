"""Check packaged legacy-label-encoder compatibility against raw LightGBM booster outputs."""
from pathlib import Path
import json,hashlib
import numpy as np,mne,yasa
R=Path(__file__).resolve().parents[2]
with np.load(R/'data/cache/H08/data.npz') as z:x=z['test_x']
with np.load(R/'results/predictions/H08/specialist--yasa-eeg.npz') as z:expected=z['predictions']
checks=[];mapping={'W':0,'WAKE':0,'N1':1,'N2':2,'N3':3,'R':4,'REM':4}
for i,night in enumerate(x):
 raw=mne.io.RawArray(night.reshape(1,-1)*1e-6,mne.create_info(['EEG Fpz-Cz'],100,ch_types=['eeg']),verbose='ERROR');s=yasa.SleepStaging(raw,eeg_name='EEG Fpz-Cz');s.fit();clf=s._load_model('auto');f=s._features[clf.feature_name_];p=clf.booster_.predict(f.to_numpy(),num_threads=1);wrapped=clf.predict_proba(f);assert p.shape==(1440,5) and np.isfinite(p).all() and np.allclose(p.sum(axis=1),1,atol=1e-12);assert np.allclose(p,wrapped,rtol=0,atol=1e-12);decoded=np.array([mapping[str(v)] for v in clf.classes_[p.argmax(axis=1)]]);assert np.array_equal(decoded,expected[i]);checks.append(dict(night=i,raw_booster_and_wrapper_probabilities_agree=True,stored_decoded_labels_agree=True,epochs=1440,class_order=list(map(str,clf.classes_))))
checkpoint=Path(yasa.__file__).parent/'classifiers/clf_eeg_lgb_0.5.0.joblib';(R/'experiments/H08/specialist-verification.json').write_text(json.dumps(dict(checks=checks,chosen_checkpoint=checkpoint.name,chosen_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),warning='Packaged LabelEncoder trained withsklearn0.24.2loadedunder1.9.1; all4320labels crosscheckedagainst rawLightGBM booster probabilityargmax/classorder. No checkpoint changes or score-driven adjustment.'),indent=2));print('YASA raw-booster compatibility checks passed for4320epochs')
