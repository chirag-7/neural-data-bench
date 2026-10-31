"""Frozen train-only xDAWN → Riemannian tangent space → logistic regression."""
from pathlib import Path
import hashlib,importlib.metadata,json,time
import numpy as np
import pyriemann
from pyriemann.estimation import XdawnCovariances
from pyriemann.tangentspace import TangentSpace
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
R=Path(__file__).resolve().parents[2];D=R/'experiments/H02';C=R/'data/cache/H02'
def fit_predict(x,y,xt,groups):
 assert pyriemann.__version__=='0.12'
 model=make_pipeline(XdawnCovariances(nfilter=4,classes=[1],estimator='oas',xdawn_estimator='oas'),TangentSpace(metric='riemann',tsupdate=False),StandardScaler(),LogisticRegression(C=1,class_weight='balanced',solver='liblinear',max_iter=1000,random_state=20261030))
 model.fit(x.astype(float)*1e-6,y);return model.decision_function(xt.astype(float)*1e-6)
if __name__=='__main__':
 spec=json.loads((D/'run-spec.json').read_text());assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==spec['specialist_sha256']
 with np.load(C/'data.npz') as z:x,y,xt,g=(z[k] for k in ['train_x','train_y','test_x','train_groups'])
 t=time.perf_counter();pred=fit_predict(x,y,xt,g);elapsed=time.perf_counter()-t
 p=R/'results/predictions/H02/expansion-v1--xdawn-tslr.npz';p.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(p,predictions=pred)
 info=dict(model='xdawn-tslr',seconds=elapsed,prediction_file=str(p.relative_to(R)),prediction_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),packages={n:importlib.metadata.version(n) for n in ['pyriemann','numpy','scipy','scikit-learn']},code_sha256=spec['specialist_sha256'],selection='Frozen before generation; no reference/test-score-based tuning',test_labels_loaded=False)
 (D/'specialist-runtime.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
