"""CalMS21 Task1 official animal-disjoint split, fixed 3Hz temporal slice.
Raw pose estimates are inputs. Human expert behavior annotations are targets.
"""
from pathlib import Path
import hashlib
import json
import re
import urllib.request
import zipfile
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / 'data/cache/A09'
SOURCE = 'https://data.caltech.edu/api/records/s0vdx-0k302/files/task1_classic_classification.zip/content'
OFFSETS = np.array([-15, -5, -1, 0, 1, 5, 15])
STRIDE = 10

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def _sequences(stream):
    """Read one sequence at a time from the frozen release's pretty JSON."""
    name = None
    lines = []
    for b in stream:
        line = b.decode('utf-8')
        match = re.match(r'^        "(task1/[^\"]+)": \{', line)
        if match:
            assert name is None
            name = match.group(1)
            lines = ['{\n']
        elif name is not None:
            if line.startswith('        }'):
                lines.append('}\n')
                yield name, json.loads(''.join(lines))
                name, lines = None, []
            else: lines.append(line)
    assert name is None

def prepare():
    (CACHE/'raw').mkdir(parents=True, exist_ok=True)
    raw = CACHE/'raw/task1_classic_classification.zip'
    if not raw.exists():
        with urllib.request.urlopen(SOURCE, timeout=240) as r: raw.write_bytes(r.read())
    md5 = hashlib.md5()
    with open(raw,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):md5.update(block)
    assert md5.hexdigest() == '8a02654fddae28614ee24a6a082261b8'
    arrays = {k: [] for k in ['train_x','train_y','test_x','test_y','train_groups','test_groups','train_units','test_units']}
    sequences = []
    with zipfile.ZipFile(raw) as z:
        for split in ['train', 'test']:
            member = 'task1_classic_classification/calms21_task1_'+split+'.json'
            with z.open(member) as stream:
                for name, row in _sequences(stream):
                    pose = np.asarray(row['keypoints'], dtype=np.float32)
                    labels = np.asarray(row['annotations'], dtype=np.int64)
                    assert pose.shape == (len(labels), 2, 2, 7)
                    assert np.isfinite(pose).all() and set(np.unique(labels)) <= {0,1,2,3}
                    # No padding/cross-recording windows; fixed stride regardless of labels.
                    centers = np.arange(15, len(labels)-15, STRIDE)
                    x = pose[centers[:,None]+OFFSETS].reshape(len(centers),7,28)
                    group = name.split('/')[-1].split('_')[0]
                    arrays[split+'_x'].append(x)
                    arrays[split+'_y'].append(labels[centers])
                    arrays[split+'_groups'].append(np.full(len(centers),group))
                    arrays[split+'_units'].append(np.array([name+':'+str(i) for i in centers]))
                    sequences.append({'sequence':name,'group':group,'split':split,'original_frames':len(labels),'evaluated_centers':len(centers)})
    arrays = {k: np.concatenate(v) for k,v in arrays.items()}
    assert not set(arrays['train_groups']) & set(arrays['test_groups'])
    np.savez_compressed(CACHE/'data.npz', **arrays)
    manifest = {'dataset':'CalMS21 v1.0 Task1','url':SOURCE,'raw_sha256':sha256(raw),'raw_bytes':raw.stat().st_size,'publisher_md5':'8a02654fddae28614ee24a6a082261b8','prepared_sha256':sha256(CACHE/'data.npz'),'sequences':sequences,'stride':STRIDE,'offsets':OFFSETS.tolist(),'shapes':{k:list(v.shape) for k,v in arrays.items()},'class_counts':{s:np.bincount(arrays[s+'_y'],minlength=4).tolist() for s in ['train','test']}}
    (Path(__file__).parent/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def load():
    with np.load(CACHE/'data.npz') as z:
        return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def _features(x):
    p = np.asarray(x).reshape(-1,7,2,2,7)
    # Distances are invariant to common translation and arena rotation.
    pts = p.transpose(0,1,2,4,3).reshape(-1,7,14,2)
    i,j = np.triu_indices(14,k=1)
    d = np.sqrt(((pts[:,:,i]-pts[:,:,j])**2).sum(axis=-1))
    speed = np.linalg.norm(pts[:,4]-pts[:,2],axis=-1)/2
    return np.c_[d.reshape(len(x),-1),speed]

def baseline(train_x,train_y,test_x):
    """Reproduced geometry ExtraTrees reference; neither original MARS nor SOTA."""
    from sklearn.ensemble import ExtraTreesClassifier
    model = ExtraTreesClassifier(n_estimators=100,max_depth=18,min_samples_leaf=5,max_features='sqrt',class_weight='balanced',random_state=1729,n_jobs=1)
    model.fit(_features(train_x),train_y)
    return model.predict(_features(test_x))

if __name__=='__main__': print(json.dumps(prepare(),indent=2))
