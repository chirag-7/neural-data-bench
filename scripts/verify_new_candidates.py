"""Independent source alignment and explicit endpoint arithmetic for K04/M01."""
from pathlib import Path
import collections,csv,hashlib,io,json,zipfile
import numpy as np
import h5py
from scipy import sparse
from expansion import ROOT as R,adapter,sha

def verify_k04():
 d=R/'experiments/K04';c=R/'data/cache/K04';spec=json.loads((d/'run-spec.json').read_text());assert sha(c/'data.npz')==spec['data_sha256']
 with np.load(c/'data.npz') as z:data={k:z[k] for k in z.files}
 rows=json.loads((d/'spot-manifest.json').read_text());manifest=json.loads((R/'data/manifests/K04.json').read_text());chosen=np.array(json.loads((d/'feature-selection.json').read_text())['indices']);labels={(v[1],v[0]):v[2] for v in csv.reader((d/'barcode_level_layer_map.tsv').open(),delimiter='\t')};donors={v['10xID']:v['Description'].split('_')[1] for v in csv.DictReader((d/'source-sample-metadata.csv').open())}
 assert not set(data['train_groups'])&set(data['test_groups']);assert len(set(data['test_groups']))==1 and len(set(data['test_sections']))==4
 cursor={'train':0,'test':0};gene_sum=None;gene_sq=None;n=0;verified_spots=0;source_counts=[]
 for item in manifest['files']:
  sample=item['sample'];assert donors[sample]==item['donor'];assert sha(R/item['path'])==item['sha256'];split='test' if donors[sample]=='Br8100' else 'train';selected=[v for v in rows if v['sample']==sample]
  with h5py.File(R/item['path']) as f:
   g=f['matrix'];barcodes=g['barcodes'].asstr()[:];names=g['features/name'].asstr()[:];counts=sparse.csc_matrix((g['data'][:],g['indices'][:],g['indptr'][:]),shape=tuple(g['shape'][:]))
  lookup={b:i for i,b in enumerate(barcodes)};columns=[lookup[v['barcode']] for v in selected];truth=np.array([['L1','L2','L3','L4','L5','L6','WM'].index(labels[(sample,v['barcode'])]) for v in selected]);start=cursor[split];stop=start+len(selected);assert np.array_equal(truth,data[split+'_y'][start:stop]);assert all(v['donor']==donors[sample] for v in selected)
  for j in sorted(set([0,len(selected)//2,len(selected)-1])):
   column=counts[:,columns[j]].toarray().ravel().astype(float);expected=np.log1p(column[chosen]*10000/column.sum());assert np.allclose(expected,data[split+'_x'][start+j],rtol=1e-6,atol=1e-6);verified_spots+=1
  if split=='train':
   a=counts[:,columns].astype(float);total=np.asarray(a.sum(axis=0)).ravel();a.data=np.log1p(a.data*10000/np.repeat(total,np.diff(a.indptr)));s=np.asarray(a.sum(axis=1)).ravel();q=np.asarray(a.multiply(a).sum(axis=1)).ravel();gene_sum=s if gene_sum is None else gene_sum+s;gene_sq=q if gene_sq is None else gene_sq+q;n+=a.shape[1]
  cursor[split]=stop;source_counts.append(dict(sample=sample,source_spots=len(barcodes),retained=len(selected),donor=donors[sample]))
 assert cursor['train']==len(data['train_x']) and cursor['test']==len(data['test_x'])
 variance=gene_sq/n-(gene_sum/n)**2;eligible=np.flatnonzero(~np.char.startswith(names.astype(str),'MT-'));independent=np.sort(eligible[np.lexsort((eligible,-variance[eligible]))[:500]]);assert np.array_equal(chosen,independent)
 a=adapter('K04');assert abs(a.score(data['test_y'],data['test_y'])['score']-1)<1e-12
 return dict(all12_sources_hashed=True,author_donor_metadata_verified=True,all_target_annotation_joins_verified=True,n_independent_spot_normalizations_checked=verified_spots,top500_genes_independently_recomputed_from_training_only=True,train_test_donors_disjoint=True,test_sections=4,test_donors=1,oracle_scorer_fixture=1.,source_counts=source_counts)

def verify_m01():
 d=R/'experiments/M01';c=R/'data/cache/M01';spec=json.loads((d/'run-spec.json').read_text());assert sha(c/'data.npz')==spec['data_sha256']
 with np.load(c/'data.npz') as z:data={k:z[k] for k in z.files}
 rows=json.loads((d/'trial-manifest.json').read_text());selected=json.loads((d/'selection-verification.json').read_text())['subjects'];manifest=json.loads((R/'data/manifests/M01.json').read_text());assert sha(R/manifest['files'][0]['path'])==manifest['files'][0]['sha256'];cursor={'train':0,'test':0};checks=0
 with zipfile.ZipFile(R/manifest['files'][0]['path']) as z:
  members=set(z.namelist());sessions=collections.defaultdict(list)
  for member in members:
   if member.endswith('/_ibl_trials.choice.npy'):
    p=member.split('/');prefix='/'.join(p[:-1]);required=[prefix+'/_ibl_trials.'+v+'.npy' for v in ['choice','contrastLeft','contrastRight','feedbackType','probabilityLeft']]
    if all(v in members for v in required):sessions[p[3]].append((p[4],p[5],p[1],prefix))
  assert set(sessions)=={v['subject'] for v in selected}
  for rec in selected:
   subject=rec['subject'];split=rec['split'];session=rec['session'];assert session==max(sessions[subject])[3];assert split==('test' if int(hashlib.sha256(('M01-v1:'+subject).encode()).hexdigest()[:8],16)%5==0 else 'train')
   fields={f:np.load(io.BytesIO(z.read(session+'/_ibl_trials.'+f+'.npy')),allow_pickle=False).ravel() for f in ['choice','contrastLeft','contrastRight','feedbackType','probabilityLeft']};subset=[v for v in rows if v['subject']==subject];targets={v['target_trial'] for v in subset};histories={i for v in subset for i in v['history_trials']};assert not targets&histories
   for v in subset:
    i=v['target_trial'];h=np.array(v['history_trials']);assert i%6==5 and i<1000 and np.array_equal(h,np.arange(i-1,i-6,-1));at=cursor[split];x=data[split+'_x'][at];assert data[split+'_y'][at]==int(fields['choice'][i]==1) and data[split+'_groups'][at]==subject
    expected=np.r_[np.nan_to_num(fields['contrastLeft'][i],nan=0),np.nan_to_num(fields['contrastRight'][i],nan=0),fields['probabilityLeft'][i],np.where(np.isin(fields['choice'][h],[-1,0,1]),fields['choice'][h],0),np.where(np.isin(fields['feedbackType'][h],[-1,1]),fields['feedbackType'][h],0)].astype(np.float32);assert np.array_equal(x,expected);cursor[split]+=1;checks+=1
 assert cursor['train']==len(data['train_x']) and cursor['test']==len(data['test_x']);assert not set(data['train_groups'])&set(data['test_groups'])
 chance=adapter('M01').score(np.full(len(data['test_y']),.5),data['test_y'])['score'];assert abs(chance-np.log(2))<1e-12
 return dict(archive_sha256_verified=True,latest_structurally_complete_session_verified=True,all_selected_target_and_history_values_verified=checks,all100_mice_included=True,test_mice=len(set(data['test_groups'])),train_test_mice_disjoint=True,no_scored_test_targets_in_any_history=True,constant_half_log_loss_fixture=float(chance))

def rescore(task):
 a=adapter(task);truth=a.load()[3];c=R/f'data/cache/{task}';d=R/f'experiments/{task}'
 with np.load(c/'data.npz') as z:groups=z['test_sections' if task=='K04' else 'test_groups']
 results=[]
 for row in json.loads((R/f'results/{task}.json').read_text()):
  if row['status']!='measured':continue
  p=R/row['prediction_file'];assert sha(p)==row['prediction_sha256']
  with np.load(p) as z:pred=z['predictions']
  values=[]
  for g in np.unique(groups):
   t=truth[groups==g];v=pred[groups==g]
   if task=='K04':
    f=[]
    for k in range(7):
     tp=np.sum((t==k)&(v==k));den=np.sum(t==k)+np.sum(v==k);f.append(float(2*tp/den) if den else 0.)
    values.append(float(np.mean(f)))
   else:
    v=np.clip(v.astype(float),1e-6,1-1e-6);values.append(float(np.mean(-t*np.log(v)-(1-t)*np.log1p(-v))))
  error=abs(float(np.mean(values))-row['score']);unit_error=float(np.max(np.abs(np.asarray(values)-row['per_unit'])));tolerance=float(np.finfo(pred.dtype).eps) if task=='M01' and pred.dtype.itemsize<8 else 1e-12
  assert error<tolerance and unit_error<tolerance
  results.append(dict(model=row['model'],prediction_sha256=sha(p),prediction_dtype=str(pred.dtype),independent_float64_score=float(np.mean(values)),independent_metric_error=error,max_unit_error=unit_error,numerical_tolerance=tolerance,note='Frozen sklearn loss retains float32 arithmetic for float32 outputs; independent float64 audit bounded by one float32 epsilon' if tolerance>1e-12 else 'Independent arithmetic agrees within1e-12'))
 return results

if __name__=='__main__':
 for task,source in [('K04',verify_k04),('M01',verify_m01)]:
  report=dict(source_checks=source(),prediction_checks=rescore(task) if (R/f'results/{task}.json').exists() else [],scope='Independent source joins, normalization and metric arithmetic; no proof of uncontaminated training or external expert validation')
  (R/f'experiments/{task}/verification.json').write_text(json.dumps(report,indent=2)+'\n');print(task,json.dumps(report)[:1400],flush=True)
