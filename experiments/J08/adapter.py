"""SynAPSeg 2D puncta instance segmentation against five independent experts.

Inputs N,C,Y,X: channel0 image intensity, channel1 valid human-annotated area.
Train labels N,Y,X, -1 unknown; test labels N,5,Y,X, -1 padding.
Output one nonnegative integer instance-label image per test image, N,Y,X.
"""
from pathlib import Path
import hashlib,io,json,shutil,urllib.request,zipfile
import numpy as np
from scipy import ndimage as ndi

P=Path(__file__).resolve().parent
REPO=P.parents[1]
CACHE=REPO/'data/cache/J08'
SOURCES={
 'BenchmarkDatasets.zip':('https://zenodo.org/api/records/18988899/files/BenchmarkDatasets.zip/content','be3744974f1a4654fc56970c8f3b981e',732816),
 'TrainingDatasets.zip':('https://zenodo.org/api/records/18988899/files/TrainingDatasets.zip/content','dd643ba927e24232b15e21525d9a33eb',693873172)}
RATERS=['A','B','C','D','E']
TEST_DATASETS=['Dataset1','Dataset2']
CROP=128
MIN_VALID_FRACTION=1.0/(CROP*CROP)

def digest(path,algorithm='sha256'):
 h=hashlib.new(algorithm)
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def _download(name):
 path=CACHE/'raw'/name;url,md5,nbytes=SOURCES[name]
 if not path.exists() or path.stat().st_size!=nbytes:
  with urllib.request.urlopen(url,timeout=600) as response,open(path.with_suffix('.partial'),'wb') as f:
   shutil.copyfileobj(response,f,length=1048576)
  path.with_suffix('.partial').replace(path)
 assert path.stat().st_size==nbytes and digest(path,'md5')==md5
 return path

def _read_tiff(data):
 import tifffile
 return tifffile.imread(io.BytesIO(data))

def _relabel(arr):
 """Author policy: split spatially disconnected painted labels, retain IDs separately."""
 arr=np.asarray(arr,dtype=np.int64)
 out=np.zeros(arr.shape,dtype=np.int32);offset=0
 structure=ndi.generate_binary_structure(arr.ndim,arr.ndim)
 for value,box in enumerate(ndi.find_objects(arr),start=1):
  if box is None:continue
  component,count=ndi.label(arr[box]==value,structure=structure)
  positive=component>0
  target=out[box];target[positive]=component[positive]+offset;offset+=count
 return out

def format_annotation(arr):
 """Exact documented object definition: relabel, remove<4, then MIP if annotation stack."""
 labels=_relabel(arr)
 areas=np.bincount(labels.ravel())
 small=np.flatnonzero(areas<4);small=small[small>0]
 if len(small):labels[np.isin(labels,small)]=0
 if labels.ndim==3:labels=labels.max(axis=0)
 assert labels.ndim==2
 return labels.astype(np.int32)

def normalize_image(image):
 image=np.asarray(image,dtype=np.float32)
 assert image.ndim==2 and np.isfinite(image).all()
 lo,hi=np.percentile(image,[1,99.8])
 return np.clip((image-lo)/max(float(hi-lo),1e-8),0,1).astype(np.float32)

def _training_members():
 root=CACHE/'raw/TrainingDatasets/2D/raw_datasets'
 manifest_path=CACHE/'raw/extracted-2d-manifest.json'
 if manifest_path.exists():
  records=json.loads(manifest_path.read_text())
  for r in records:assert digest(CACHE/'raw'/r['source_member'])==r['sha256']
  return root,records
 raw=_download('TrainingDatasets.zip');records=[]
 with zipfile.ZipFile(raw) as z:
  for i in z.infolist():
   if not i.filename.startswith('TrainingDatasets/2D/raw_datasets/') or i.is_dir():continue
   b=z.read(i);dest=CACHE/'raw'/i.filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
   records.append({'source_member':i.filename,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'zip_crc32':f'{i.CRC:08x}','zip_crc_checked':True})
 manifest_path.write_text(json.dumps(records,indent=2)+'\n')
 return root,records

def prepare():
 (CACHE/'raw').mkdir(parents=True,exist_ok=True)
 benchmark=_download('BenchmarkDatasets.zip')
 root,raw_members=_training_members()
 tx=[];ty=[];groups=[];units=[];crop_manifest=[]
 for folder in sorted(root.iterdir()):
  if not folder.is_dir():continue
  image=_read_tiff((folder/'image.tiff').read_bytes());labels=_read_tiff((folder/'labels.tiff').read_bytes())
  assert image.shape==labels.shape and image.ndim==2
  raw_image_sha=hashlib.sha256(np.ascontiguousarray(image).tobytes()).hexdigest()
  image=normalize_image(image);labels=format_annotation(labels)
  roi=(_read_tiff((folder/'ROIs.tiff').read_bytes())>0) if (folder/'ROIs.tiff').exists() else np.ones(image.shape,dtype=bool)
  assert roi.shape==image.shape
  for top in range(0,image.shape[0],CROP):
   for left in range(0,image.shape[1],CROP):
    height=min(CROP,image.shape[0]-top);width=min(CROP,image.shape[1]-left)
    valid=np.zeros((CROP,CROP),dtype=bool);valid[:height,:width]=roi[top:top+height,left:left+width]
    if valid.mean()<MIN_VALID_FRACTION:continue
    features=np.zeros((2,CROP,CROP),dtype=np.float32)
    features[0,:height,:width]=image[top:top+height,left:left+width]
    features[1]=valid
    target=np.full((CROP,CROP),-1,dtype=np.int32)
    target[:height,:width]=labels[top:top+height,left:left+width]
    target[~valid]=-1
    unit=folder.name+f':y{top}:x{left}'
    tx.append(features);ty.append(target);groups.append(folder.name);units.append(unit)
    crop_manifest.append({'unit':unit,'source_field':folder.name,'source_shape':list(image.shape),'top':top,'left':left,'valid_pixels':int(valid.sum()),'raw_image_array_sha256':raw_image_sha})
 assert len(set(groups))==27
 train_x=np.stack(tx);train_y=np.stack(ty)
 test_images=[];test_labels=[];specialist=[];test_records=[];member_manifest=[]
 with zipfile.ZipFile(benchmark) as z:
  for dataset in TEST_DATASETS:
   prefix='BenchmarkDatasets/'+dataset+'/'
   raw_name=prefix+'image.tiff';raw_bytes=z.read(raw_name);image=_read_tiff(raw_bytes)
   assert image.ndim==2
   test_images.append(normalize_image(image));rater_masks=[];rater_files=[]
   for rater in RATERS:
    matches=[n for n in z.namelist() if n.startswith(prefix+'annotations/annotated_'+rater+'_') and n.endswith('.tiff')]
    assert len(matches)==1
    b=z.read(matches[0]);annotation=_read_tiff(b);rater_masks.append(format_annotation(annotation));rater_files.append(matches[0])
    member_manifest.append({'member':matches[0],'sha256':hashlib.sha256(b).hexdigest(),'raw_shape':list(annotation.shape),'prepared_shape':list(rater_masks[-1].shape)})
   assert all(m.shape==image.shape for m in rater_masks)
   pred_names=[n for n in z.namelist() if n.startswith(prefix+'annotations/annotated_predStardist_v3.6.0.8_')]
   assert len(pred_names)==1
   pred_bytes=z.read(pred_names[0]);pred=format_annotation(_read_tiff(pred_bytes));assert pred.shape==image.shape
   specialist.append(pred);test_labels.append(np.stack(rater_masks))
   test_records.append({'dataset':dataset,'source_image':raw_name,'image_shape':list(image.shape),'source_image_sha256':hashlib.sha256(raw_bytes).hexdigest(),'rater_files':rater_files,'specialist_file':pred_names[0],'specialist_mask_sha256':hashlib.sha256(pred_bytes).hexdigest(),'full_field_held_out':True,'animal_identity':'Not independently resolvable from released file metadata'})
 height=max(i.shape[0] for i in test_images);width=max(i.shape[1] for i in test_images)
 test_x=np.zeros((2,2,height,width),dtype=np.float32);test_y=np.full((2,5,height,width),-1,dtype=np.int32);archived=np.zeros((2,height,width),dtype=np.int32)
 for i,(image,labels,pred) in enumerate(zip(test_images,test_labels,specialist)):
  h,w=image.shape;test_x[i,0,:h,:w]=image;test_x[i,1,:h,:w]=1;test_y[i,:,:h,:w]=labels;archived[i,:h,:w]=pred
 arrays={'train_x':train_x,'train_y':train_y,'test_x':test_x,'test_y':test_y,'train_groups':np.array(groups),'test_groups':np.array(TEST_DATASETS),'train_units':np.array(units),'test_units':np.array(TEST_DATASETS),'test_shapes':np.array([i.shape for i in test_images]),'archived_specialist':archived}
 np.savez_compressed(CACHE/'data.npz',**arrays)
 archives=[]
 for name,(url,md5,nbytes) in SOURCES.items():
  path=CACHE/'raw'/name
  complete=path.exists() and path.stat().st_size==nbytes
  if complete:assert digest(path,'md5')==md5
  archives.append({'name':name,'url':url,'expected_bytes':nbytes,'publisher_md5':md5,'whole_archive_complete_and_md5_verified':complete,'sha256':digest(path) if complete else None})
 manifest={'id':'J08','release':'Zenodo18988899','license':'CC BY4.0','training_fields':27,'training_crops':len(tx),'training_crop_size':CROP,'minimum_annotated_fraction':MIN_VALID_FRACTION,'minimum_annotated_pixels':1,'training_field_ids':sorted(set(groups)),'training_crop_manifest':crop_manifest,'training_member_checksums':raw_members,'test':test_records,'benchmark_member_checksums':member_manifest,'archives':archives,'shapes':{k:list(v.shape) for k,v in arrays.items()},'prepared_sha256':digest(CACHE/'data.npz'),'selection':'All27released2Drawfields, fixednonoverlap128grid, ROIcoverageonly; no target-object-count filter. OnlyDataset1/2 officialheldout2Dbenchmarks.','annotation_policy':'Connected components separately within each painted positiveID with fullconnectivity; removeobjects<4voxels; maxprojectmanualstacksfor2Dimages, matchingauthoranalysis. No majority/consensusoracle constructed.'}
 (P/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return manifest

def load():
 with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def baseline(train_x,train_y,test_x):
 """Archived author StarDist masks; no fitting. Information budget differs, explicit."""
 with np.load(CACHE/'data.npz') as z:
  assert np.array_equal(test_x,z['test_x']), 'Archive only applies to fixed canonical image order'
  return z['archived_specialist'].copy()

def _instance_f1(truth,pred,tau=0.5):
 from scipy.optimize import linear_sum_assignment
 truth=np.asarray(truth);pred=np.asarray(pred)
 tvals=np.unique(truth);tvals=tvals[tvals>0];pvals=np.unique(pred);pvals=pvals[pvals>0]
 if len(tvals)==0 or len(pvals)==0:
  return (1. if not len(tvals) and not len(pvals) else 0.),0,int(len(pvals)),int(len(tvals))
 tids,tinv=np.unique(truth,return_inverse=True);pids,pinv=np.unique(pred,return_inverse=True)
 counts=np.bincount(tinv.ravel()*len(pids)+pinv.ravel(),minlength=len(tids)*len(pids)).reshape(len(tids),len(pids))
 tmask=tids>0;pmask=pids>0
 inter=counts[tmask][:,pmask].astype(float)
 tsize=counts.sum(axis=1)[tmask];psize=counts.sum(axis=0)[pmask]
 iou=inter/(tsize[:,None]+psize[None,:]-inter)
 # Maximize threshold-qualified matches first, IoU second. Pairs are one-to-one.
 cost=-(iou>=tau).astype(float)-iou/(2*min(iou.shape))
 rows,cols=linear_sum_assignment(cost);tp=int((iou[rows,cols]>=tau).sum());fp=len(pvals)-tp;fn=len(tvals)-tp
 return float(2*tp/(2*tp+fp+fn)),tp,int(fp),int(fn)

def score(predictions,test_y):
 """Equal image/rater mean objectF1 at IoU>=.5; keep all experts separate."""
 pred=np.asarray(predictions);truth=np.asarray(test_y)
 assert pred.shape==(truth.shape[0],truth.shape[2],truth.shape[3])
 assert np.isfinite(pred).all() and np.all(pred>=0) and np.all(pred==np.floor(pred))
 values=[]
 for i in range(len(pred)):
  valid=truth[i,0]>=0;assert np.all((truth[i]>=0)==valid)
  ys,xs=np.where(valid);h,w=ys.max()+1,xs.max()+1
  canon=format_annotation(pred[i,:h,:w])
  for rater in range(5):values.append(_instance_f1(truth[i,rater,:h,:w],canon)[0])
 return float(np.mean(values))

if __name__=='__main__':
 result=prepare();print(json.dumps({k:v for k,v in result.items() if k not in ['training_crop_manifest','training_member_checksums','benchmark_member_checksums']},indent=2))
