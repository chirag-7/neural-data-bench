"""DLPFC expression-to-curated-layer transfer; all sections of one donor held out."""
from pathlib import Path
import hashlib, json
import h5py
import numpy as np
from scipy import sparse
from sklearn.metrics import f1_score, accuracy_score
R=Path(__file__).resolve().parents[2];D=R/'experiments/K04';C=R/'data/cache/K04'
SAMPLES=['151507','151508','151509','151510','151669','151670','151671','151672','151673','151674','151675','151676']
DONORS={s:('Br5292' if i<4 else 'Br5595' if i<8 else 'Br8100') for i,s in enumerate(SAMPLES)}
LABELS=['L1','L2','L3','L4','L5','L6','WM']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(sample):
 with h5py.File(C/f'raw/{sample}.h5') as f:
  g=f['matrix'];x=sparse.csc_matrix((g['data'][:],g['indices'][:],g['indptr'][:]),shape=tuple(g['shape'][:])).T.tocsr()
  ids=g['features/id'].asstr()[:];names=g['features/name'].asstr()[:];barcodes=g['barcodes'].asstr()[:]
 assert x.shape==(len(barcodes),len(ids)) and len(set(ids))==len(ids) and len(set(barcodes))==len(barcodes)
 assert np.isfinite(x.data).all() and (x.data>=0).all()
 return x,ids,names,barcodes
def prepare():
 labels={};excluded={};matrices=[];targets=[];groups=[];donors=[];manifest=[];spotrows=[];gene_ids=None
 for line in (D/'barcode_level_layer_map.tsv').read_text().splitlines():
  barcode,sample,label=line.split('\t');key=(sample,barcode);assert key not in labels;labels[key]=label
 for sample in SAMPLES:
  x,ids,names,barcodes=read(sample)
  if gene_ids is None:gene_ids=ids;gene_names=names
  else:assert np.array_equal(gene_ids,ids)
  values=np.array([labels.get((sample,b),'UNANNOTATED') for b in barcodes]);keep=np.isin(values,LABELS)
  lib=np.asarray(x.sum(axis=1)).ravel();assert (lib>0).all()
  x=sparse.diags(1e4/lib[keep])@x[keep];x=x.tocsr();x.data=np.log1p(x.data)
  matrices.append(x);targets.extend(LABELS.index(v) for v in values[keep]);groups.extend([sample]*int(keep.sum()));donors.extend([DONORS[sample]]*int(keep.sum()))
  spotrows.extend(dict(sample=sample,barcode=str(b),donor=DONORS[sample],label=LABELS.index(v)) for b,v in zip(barcodes[keep],values[keep]))
  p=C/f'raw/{sample}.h5';manifest.append(dict(sample=sample,donor=DONORS[sample],url=f'https://spatial-dlpfc.s3.us-east-2.amazonaws.com/h5/{sample}_filtered_feature_bc_matrix.h5',path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p),source_spots=len(barcodes),retained_labeled_spots=int(keep.sum()),excluded_annotation_counts={str(v):int((values[~keep]==v).sum()) for v in np.unique(values[~keep])}))
 x=sparse.vstack(matrices).tocsr();y=np.asarray(targets);groups=np.asarray(groups);donors=np.asarray(donors)
 train=donors!='Br8100';test=~train;assert not set(donors[train])&set(donors[test])
 a=x[train];mean=np.asarray(a.mean(axis=0)).ravel();var=np.asarray(a.multiply(a).mean(axis=0)).ravel()-mean**2
 eligible=~np.char.startswith(gene_names.astype(str),'MT-');indices=np.flatnonzero(eligible)
 # Selection depends only on outer-training expression, never held-out expression/labels.
 chosen=indices[np.lexsort((indices,-var[indices]))[:500]];chosen=np.sort(chosen)
 train_x=x[train][:,chosen].toarray().astype(np.float32);test_x=x[test][:,chosen].toarray().astype(np.float32)
 np.savez_compressed(C/'data.npz',train_x=train_x,train_y=y[train],test_x=test_x,test_y=y[test],train_groups=donors[train],test_groups=donors[test],train_sections=groups[train],test_sections=groups[test])
 meta=dict(benchmark_id='K04',dataset='Maynard2021 HumanPilot DLPFC',primary_metric='section_equal_macro_f1_7classes',direction='higher',train_shape=list(train_x.shape),test_shape=list(test_x.shape),feature_names=gene_names[chosen].tolist(),gene_ids=gene_ids[chosen].tolist(),label_encoding=dict(enumerate(LABELS)),train_donors=sorted(set(donors[train])),test_donors=sorted(set(donors[test])),train_sections=sorted(set(groups[train])),test_sections=sorted(set(groups[test])),units='log1p(counts / full33538-gene library total *10000)',feature_selection='500 highest-variance non-mitochondrial genes using all outer-training spots; not reselected inside model inner CV',truth_type='Curated layer/white-matter annotations; expression-assisted, not fully orthogonal molecular truth',adaptation='No fitting transforms on held-out donor; fixed per-spot library normalization allowed')
 (C/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');(D/'spot-manifest.json').write_text(json.dumps(spotrows,separators=(',',':'))+'\n');(D/'feature-selection.json').write_text(json.dumps(dict(indices=chosen.tolist(),training_variances=var[chosen].tolist(),test_data_used=False,excluded_mitochondrial=True),indent=2)+'\n')
 (R/'data/manifests/K04.json').write_text(json.dumps(dict(benchmark_id='K04',author_commit='044446d6bd8fc154aa74f7be62ec67effb1ec376',files=manifest,annotation_sha256=sha(D/'barcode_level_layer_map.tsv'),prepared_sha256=sha(C/'data.npz'),prepared_file='data/cache/K04/data.npz'),indent=2)+'\n')
 print(json.dumps({k:meta[k] for k in ['train_shape','test_shape','train_donors','test_donors']}))
def load():
 with np.load(C/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def train_groups():
 with np.load(C/'data.npz') as z:return z['train_groups']
def baseline(x,y,xt,groups):
 from sklearn.pipeline import make_pipeline
 from sklearn.preprocessing import StandardScaler
 from sklearn.linear_model import LogisticRegression
 return make_pipeline(StandardScaler(),LogisticRegression(C=1,class_weight='balanced',solver='lbfgs',max_iter=500,random_state=20261030)).fit(x,y).predict(xt)
def score(pred,truth,test_x=None):
 pred=np.asarray(pred);assert pred.shape==truth.shape and np.isfinite(pred).all() and np.isin(pred,np.arange(7)).all()
 with np.load(C/'data.npz') as z:g=z['test_sections']
 results=[dict(group=str(v),n=int((g==v).sum()),score=float(f1_score(truth[g==v],pred[g==v],labels=np.arange(7),average='macro',zero_division=0))) for v in np.unique(g)]
 return dict(score=float(np.mean([v['score'] for v in results])),metric='section_equal_macro_f1_7classes',direction='higher',per_unit=[v['score'] for v in results],group_results=results,pooled_macro_f1=float(f1_score(truth,pred,labels=np.arange(7),average='macro',zero_division=0)),accuracy=float(accuracy_score(truth,pred)))
if __name__=='__main__':prepare()
