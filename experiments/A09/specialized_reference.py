"""Rescore archived VASSI predictions at unchanged frozen A09 frame centers.
Primary run00 preselected before rescoring; no fitting or best-test-run selection.
Requires h5py only for archive reading, plus NumPy/sklearn.
"""
from pathlib import Path
import hashlib,json,urllib.request
import numpy as np
P=Path(__file__).resolve().parent
REPO=P.parents[1]
CACHE=REPO/'data/cache/A09'
OUTPUT=P/'archived-vassi'
SOURCE='https://edmond.mpg.de/api/access/datafile/315313'
MD5='242beccb757da2573c7879db66908ec6'

def digest(path,algorithm='sha256'):
 h=hashlib.new(algorithm)
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def acquire():
 path=CACHE/'raw/vassi-results.h5'
 path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  with urllib.request.urlopen(SOURCE,timeout=180) as r:path.write_bytes(r.read())
 assert digest(path,'md5')==MD5
 return path

def rescore():
 import h5py
 from sklearn.metrics import f1_score,balanced_accuracy_score,precision_recall_fscore_support,confusion_matrix
 selection=json.loads((P/'specialist-selection-plan.json').read_text())
 assert selection['primary_archived_run']=='run_00' and selection['selection_locked_before_rescoring']
 alignment=json.loads((P/'specialist-alignment.json').read_text())
 assert alignment['all_original_frames_match_archived_truth'] and alignment['all20run_truth_arrays_match_original']
 path=acquire()
 with np.load(CACHE/'data.npz') as z:
  truth=z['test_y'].copy();units=z['test_units'].copy();groups=z['test_groups'].copy()
 # Reconstruct frozen global indices from the unchanged original-sequence manifest.
 manifest=json.loads((P/'data-manifest.json').read_text())
 seq=[s for s in manifest['sequences'] if s['split']=='test']
 indices=[];expected_units=[];offset=0
 for group,row in enumerate(seq):
  m=alignment['sequences'][group]
  assert row['sequence']==m['sequence_id'] and row['original_frames']==m['frames']
  center=np.arange(15,row['original_frames']-15,10)
  indices.extend((offset+center).tolist());expected_units.extend(row['sequence']+':'+str(i) for i in center)
  offset+=row['original_frames']
 indices=np.array(indices)
 assert np.array_equal(np.array(expected_units),units)
 assert len(indices)==26162
 OUTPUT.mkdir(exist_ok=True)
 metrics=[]
 with h5py.File(path) as f:
  for i in range(20):
   run=f'run_{i:02d}';model=f'vassi-run-{i:02d}'
   labels=f[run+'/true/timestamp'][:][indices]
   assert np.array_equal(labels,truth)
   pred=f[run+'/pred/timestamp'][:][indices].astype(np.int64)
   assert pred.shape==truth.shape and set(pred.tolist())<=set(range(4))
   np.savez_compressed(OUTPUT/(model+'.predictions.npz'),predictions=pred,test_units=units)
   precision,recall,perclass,support=precision_recall_fscore_support(truth,pred,labels=[0,1,2,3],zero_division=0)
   result={'model_id':model,'source_archived_run':run,'primary_reference':i==0,'task_id':'A09','endpoint':'calms21-task1-3hz-custom','metric':'macro_f1','direction':'higher','primary_score':float(f1_score(truth,pred,labels=[0,1,2,3],average='macro',zero_division=0)),'secondary':{'balanced_accuracy':float(balanced_accuracy_score(truth,pred)),'foreground_macro_f1':float(f1_score(truth,pred,labels=[0,1,2],average='macro',zero_division=0))},'per_class':{'precision':precision.tolist(),'recall':recall.tolist(),'f1':perclass.tolist(),'support':support.tolist()},'confusion_matrix':confusion_matrix(truth,pred,labels=[0,1,2,3]).tolist(),'per_recording':[{'recording':str(g),'examples':int((groups==g).sum()),'macro_f1_fixed_four_classes':float(f1_score(truth[groups==g],pred[groups==g],labels=[0,1,2,3],average='macro',zero_division=0))} for g in np.unique(groups)],'evaluation_examples':len(truth),'predictions_sha256':digest(OUTPUT/(model+'.predictions.npz')),'comparison_tier':'archived domain-specialist pipeline; unequal training/context/optimization budget','matched_test_centers_labels_metric':True,'matched_training_input_budget':False,'is_current_sota':False,'source_url':SOURCE}
   (OUTPUT/(model+'.scores.json')).write_text(json.dumps(result,indent=2)+'\n')
   metrics.append(result)
 scores=np.array([m['primary_score'] for m in metrics])
 result={'task_id':'A09','primary_reference_model':'vassi-run-00','primary_score':float(scores[0]),'selection_rule':'lowest numeric archived run ID; locked before any rescoring','num_archived_runs':len(scores),'secondary_descriptive':{'median':float(np.median(scores)),'minimum':float(np.min(scores)),'maximum':float(np.max(scores)),'std_population':float(np.std(scores))},'metric':'macro_f1','metric_classes':[0,1,2,3],'original_test_frames':offset,'frozen_test_centers':len(truth),'source_doi':'10.17617/3.3R0QYI','source_version':'1.0','archive_file_id':315313,'archive_sha256':digest(path),'publisher_md5':MD5,'matched_test_centers_labels_metric':True,'matched_training_input_budget':False,'is_current_sota':False,'pipeline':'VASSI201hand-designedspatiotemporalfeatures;XGBoost1000trees;trainonly5foldpostprocessingoptimization;20archivedruns;fullframecontext','notes':['A09fourclassmacroF1differsfromoriginalCalMS21foregroundF1','Do not treat20runs as20independentdatasets','Maximum is descriptive rangeendpoint, never selected comparator','Archived pipeline uses more training/context/optimization budget than Solcodegeneration submissions. Exclude from strict matched-budget superiority counts.'],'runs':[{'model_id':m['model_id'],'primary_score':m['primary_score'],'primary_reference':m['primary_reference']} for m in metrics]}
 (OUTPUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

def load_predictions(run='run_00',test_units=None):
 i=int(run.split('_')[-1]);assert 0<=i<20
 with np.load(OUTPUT/(f'vassi-run-{i:02d}.predictions.npz')) as z:
  if test_units is not None:assert np.array_equal(test_units,z['test_units'])
  return z['predictions'].copy()

if __name__=='__main__':print(json.dumps(rescore(),indent=2))
