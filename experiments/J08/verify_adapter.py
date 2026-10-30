"""Verify data masks/scorer independently of any evaluated-model program."""
from pathlib import Path
import ast,hashlib,importlib.util,io,json,types,typing,zipfile
import numpy as np
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('j08adapter',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def _author_function(path,name,namespace):
 tree=ast.parse(path.read_text())
 node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
 return namespace[name]

def verify():
 import skimage.morphology
 ns={'np':np,'Optional':typing.Optional}
 relabel=_author_function(P/'source/utils_image_processing.py','relabel',ns)
 namespace={'np':np,'skimage':types.SimpleNamespace(morphology=skimage.morphology),'uip':types.SimpleNamespace(relabel=relabel,mip=lambda x,axis:np.max(x,axis=axis),unique_nonzero=lambda x:np.unique(x[x>0]))}
 original_format=_author_function(P/'source/fig2_intrarater_var_analysis.py','format_annot',namespace)
 comparisons=[]
 with zipfile.ZipFile(a.CACHE/'raw/BenchmarkDatasets.zip') as z:
  for n in z.namelist():
   if not any(n.startswith('BenchmarkDatasets/'+d+'/annotations/') for d in a.TEST_DATASETS) or not n.endswith('.tiff'):continue
   raw=a._read_tiff(z.read(n))
   expected=original_format(raw,force2d=False)
   if expected.ndim==3:expected=expected.max(axis=0)
   actual=a.format_annotation(raw)
   assert np.array_equal(expected,actual),n
   comparisons.append({'member':n,'original_shape':list(raw.shape),'formatted_shape':list(actual.shape),'instance_count':int(len(np.unique(actual))-1),'matches_author_function_exactly':True})
 assert len(comparisons)==12
 with np.load(a.CACHE/'data.npz') as z:
  assert z['train_x'].shape==(1262,2,128,128)
  assert z['test_x'].shape==(2,2,727,546) and z['test_y'].shape==(2,5,727,546)
  assert np.array_equal(z['train_x'][:,1]>0,z['train_y']>=0)
  assert not set(z['train_groups'])&set(z['test_groups'])
  assert len(set(z['train_groups']))==27
  for i in range(2):
   valid=z['test_x'][i,1]>0
   assert np.all((z['test_y'][i]>=0)==valid)
  image_maxes=z['test_x'][:,0].max(axis=(1,2))
  assert np.all(image_maxes<=1) and np.isfinite(z['train_x']).all()
 toy=np.zeros((12,12),dtype=np.int32);toy[1:4,1:4]=1;toy[7:10,7:10]=2
 assert a._instance_f1(toy,toy)==(1.,2,0,0)
 perm=toy.copy();perm[toy==1]=73;perm[toy==2]=9
 assert a._instance_f1(toy,perm)==(1.,2,0,0)
 assert a._instance_f1(toy,np.zeros_like(toy))==(0.,0,0,2)
 assert a._instance_f1(np.zeros_like(toy),toy)==(0.,0,2,0)
 assert a._instance_f1(np.zeros_like(toy),np.zeros_like(toy))==(1.,0,0,0)
 # Independent brute-force threshold matching for all possible tiny2x2 assignments.
 from itertools import permutations
 for seed in range(5):
  pred=np.random.default_rng(seed).integers(0,3,size=(12,12))
  pids=[i for i in np.unique(pred) if i>0];tids=[1,2]
  iou=np.array([[np.logical_and(toy==t,pred==p).sum()/np.logical_or(toy==t,pred==p).sum() for p in pids] for t in tids])
  best=max(sum(iou[row,col]>=.5 for row,col in enumerate(cols)) for cols in permutations(range(len(pids)),min(len(tids),len(pids))))
  expected=2*best/(len(tids)+len(pids))
  assert a._instance_f1(toy,pred)[0]==expected
 result={'date':'2026-10-30','author_annotation_preprocessing_exact_matches':comparisons,'num_masks_compared':len(comparisons),'train_fields':27,'train_crops':1262,'test_fields':2,'raters_per_test_field':5,'training_unknown_pixels_never_negative_examples':True,'test_padding_mask_verified':True,'scorer_toy_cases_passed':['perfect','ID_permutation','empty_prediction','empty_truth','both_empty','independent_bruteforce_assignment'],'general_model_calls':0}
 (P/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
