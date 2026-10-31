from pathlib import Path
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parents[2]
def manifest():return json.loads((R/'data/manifests/B08.json').read_text())
def load():
 result=[]
 for row in manifest()['files']:
  p=R/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];z=np.load(p);result.append((z['times'],z['labels']))
 return result
def validate(t,y,original_times,original_labels):
 assert isinstance(t,np.ndarray) and isinstance(y,np.ndarray) and t.shape==original_times.shape and y.shape==original_labels.shape
 assert np.isfinite(t).all() and np.issubdtype(t.dtype,np.floating) and np.issubdtype(y.dtype,np.integer)
 assert np.array_equal(y,original_labels) and np.all(np.diff(t)>=0)
 error=float(np.max(np.abs(t-original_times)));assert error<=50e-6+1e-10,'Timing tolerance exceeded'
 return error
