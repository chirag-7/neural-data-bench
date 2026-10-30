import json,hashlib,zipfile,importlib.util
from pathlib import Path
import numpy as np,h5py
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a09',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
archive=a.CACHE/'raw/vassi-results.h5'
h=hashlib.md5()
with open(archive,'rb') as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
assert h.hexdigest()=='242beccb757da2573c7879db66908ec6'
rows=[];alltruth=[];allcenters=[];offset=0
with h5py.File(archive) as f,zipfile.ZipFile(a.CACHE/'raw/task1_classic_classification.zip') as z:
 with z.open('task1_classic_classification/calms21_task1_test.json') as stream:
  for i,(name,row) in enumerate(a._sequences(stream)):
   d=f["test_dataset/group_results/"+str(i)+"/results/('resident', 'intruder')/data"]
   labels=np.asarray(row['annotations']);arch=d['_y_true_numeric'][:];ts=d['timestamps'][:]
   assert len(labels)==len(arch)
   assert np.array_equal(ts,np.arange(len(labels)))
   print(i,name,len(labels),'groundtruth_equal',np.array_equal(labels,arch),'mismatches',int((labels!=arch).sum()),flush=True)
   rows.append({'group_index':i,'sequence_id':name,'frames':len(labels),'timestamp_start':int(ts[0]),'timestamp_stop_inclusive':int(ts[-1]),'raw_label_match':bool(np.array_equal(labels,arch)),'mismatch_count':int((labels!=arch).sum()),'fullframe_offset':offset})
   alltruth.append(labels)
   allcenters.extend((offset+np.arange(15,len(labels)-15,10)).tolist())
   offset+=len(labels)
 truth=np.concatenate(alltruth);centers=np.array(allcenters)
 for run in [f'run_{i:02d}' for i in range(20)]:
  arch=f[run+'/true/timestamp'][:]
  assert np.array_equal(truth,arch)
 with np.load(a.CACHE/'data.npz') as prepared:
  assert np.array_equal(truth[centers],prepared['test_y'])
 result={'frame_index_convention':'zero-based np.arange(len(original_sequence)); no offset applied','archive_md5_matches_publisher':True,'all_original_frames_match_archived_truth':all(r['raw_label_match'] for r in rows),'all20run_truth_arrays_match_original':True,'all_frozen_center_labels_match':True,'num_test_sequences':len(rows),'num_original_frames':len(truth),'num_frozen_centers':len(centers),'sequences':rows}
 (P/'specialist-alignment.json').write_text(json.dumps(result,indent=2)+'\n')
 np.savez_compressed(a.CACHE/'vassi-center-map.npz',indices=centers,truth=truth[centers])
 print(json.dumps({k:v for k,v in result.items() if k!='sequences'},indent=2))
