"""Real Rat7M head/spine mocap, controlled missing-pose recovery, rat-disjoint."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile
import numpy as np

REPO=Path(__file__).resolve().parents[2]
CACHE=REPO/'data/cache/A14'
SOURCE='https://zenodo.org/api/records/18405201/files/rat7M_raw_data.zip/content'
LANDMARKS=['HeadF','HeadB','HeadL','SpineF','SpineM','SpineL']
TRAIN_SUBJECTS=[1,2,3]
TEST_SUBJECTS=[4,5]

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def prepare():
    from scipy.io import loadmat
    (CACHE/'raw').mkdir(parents=True,exist_ok=True)
    raw=CACHE/'raw/rat7M_raw_data.zip'
    if not raw.exists():
        with urllib.request.urlopen(SOURCE,timeout=240) as r:raw.write_bytes(r.read())
    assert raw.stat().st_size==246184002
    md5=hashlib.md5()
    with open(raw,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):md5.update(block)
    assert md5.hexdigest()=='9cebea82f2bd2403a201df52cdccc486'
    arrays={k:[] for k in ['train_x','train_y','test_x','test_y','train_groups','test_groups','train_units','test_units']}
    manifest=[]
    with zipfile.ZipFile(raw) as z:
        for name in sorted(z.namelist()):
            subject=int(name.split('-s')[1].split('-')[0])
            split='train' if subject in TRAIN_SUBJECTS else 'test'
            with z.open(name) as f:mocap=loadmat(f,squeeze_me=True,struct_as_record=False)['mocap']
            poses=np.stack([getattr(mocap,k) for k in LANDMARKS],axis=1).astype(np.float32)
            starts=np.arange(0,len(poses)-30,60)
            target=poses[starts[:,None]+np.arange(31)].reshape(-1,31,18)
            valid=np.isfinite(target).all(axis=(1,2))
            starts,target=starts[valid],target[valid]
            x=target.copy()
            x[:,12:19,:3]=np.nan
            arrays[split+'_x'].append(x)
            arrays[split+'_y'].append(target)
            arrays[split+'_groups'].append(np.full(len(x),subject))
            arrays[split+'_units'].append(np.array([name+':'+str(i) for i in starts]))
            manifest.append({'member':name,'subject':subject,'split':split,'frames':len(poses),'candidate_windows':int(len(valid)),'complete_windows':len(starts),'excluded_incomplete_windows':int((~valid).sum()),'original_nonfinite_fraction':float((~np.isfinite(poses)).mean())})
    arrays={k:np.concatenate(v) for k,v in arrays.items()}
    assert not set(arrays['train_groups'])&set(arrays['test_groups'])
    assert all(np.isfinite(arrays[s+'_y']).all() for s in ['train','test'])
    np.savez_compressed(CACHE/'data.npz',**arrays)
    result={'dataset':'Rat7M raw mocap distributed with DISK pinned record18405201','url':SOURCE,'raw_sha256':sha256(raw),'raw_bytes':raw.stat().st_size,'publisher_md5':'9cebea82f2bd2403a201df52cdccc486','prepared_sha256':sha256(CACHE/'data.npz'),'landmarks':LANDMARKS,'window_length':31,'stride':60,'masked_frames':[12,13,14,15,16,17,18],'masked_columns':[0,1,2],'source_files':manifest,'shapes':{k:list(v.shape) for k,v in arrays.items()}}
    (Path(__file__).parent/'data-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def load():
    with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def baseline(train_x,train_y,test_x):
    """Per-window temporal linear interpolation, evaluated only artificially masked entries."""
    result=np.asarray(test_x).copy()
    t=np.arange(result.shape[1])
    for row in result:
        for j in range(row.shape[1]):
            valid=np.isfinite(row[:,j])
            row[:,j]=np.interp(t,t[valid],row[valid,j])
    return result

if __name__=='__main__':print(json.dumps(prepare(),indent=2))
