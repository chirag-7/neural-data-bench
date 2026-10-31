"""Independent K05/K06 post-output audit. No adapter imports or model fitting.
Run after batch predictions exist. Only writes an optional --output report.
"""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol','task-baseline')
def require(ok,message):
    if not ok:raise AssertionError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inside(rel):
    p=(ROOT/rel).resolve();require(p.is_relative_to(ROOT.resolve()),'Path outside repository');return p

def raw_truth(task,cache,data,rows):
    """Rebuild test labels from independent upstream targets, not scorer code."""
    wanted=[r for r in rows if r['split']=='test']
    if task=='K05':
        halo=list(csv.DictReader((cache/'HALO_cell_type_proportions.csv').open()))
        output=[]
        for r in wanted:
            panel=[z for z in halo if z['Sample']==r['block'] and z['Combo']=='Circle'];denom=sum(int(z['n_cell']) for z in panel)
            values=[]
            for target in ['Astro','EndoMural','Inhib']:
                matches=[z for z in panel if z['cell_type']==target];require(len(matches)==1,'Ambiguous target')
                z=matches[0];require(z['Confidence'] in ['OK','High'],'Low confidence target');value=int(z['n_cell'])/denom
                require(abs(value-float(z['prop']))<1e-12,'Source fraction denominator mismatch');values.append(value)
            output.append(values)
        ids=[r['sample_id'] for r in wanted]
        output=np.array(output)
    else:
        import h5py
        with h5py.File(cache/'groundTruth_cell_list.mat') as h:
            def read(key):
                arr=h['gt'][key][()]
                if arr.dtype.kind!='O':return arr.ravel().tolist()
                return [''.join(chr(int(x)) for x in h[ref][()].ravel()) for ref in arr.ravel()]
            fields=[read(k) for k in ['menu_name','menu_UID','menu_groundTruth','menu_animals']]
        mapping={(s,int(uid)):(label,animal) for s,uid,label,animal in zip(*fields)}
        output=[]
        for r in wanted:
            label,animal=mapping[(r['session'],r['source_uid'])]
            require(label==r['label'] and animal==r['animal'] and animal.startswith('AllenInstitute_'),'Independent GT mapping mismatch')
            require(label in ['PV','SST'],'Wrong class');output.append(int(label=='SST'))
        output=np.array(output,dtype=int);ids=[r['session']+':'+str(r['source_uid']) for r in wanted]
    require(ids==data['test_units'].tolist(),'Test source row order mismatch')
    np.testing.assert_allclose(output,data['test_y'],rtol=1e-12,atol=1e-15)
    return output

def independent_score(task,pred,truth,data):
    require(pred.shape==truth.shape and np.isfinite(pred).all(),'Invalid prediction shape/nonfinite values')
    groups=data['test_groups'];units=sorted(set(groups))
    if task=='K05':
        require(np.all((pred>=0)&(pred<=1)),'Fractions outside[0,1]')
        blocks=data['test_blocks'];errors=np.square(pred-truth);donor=[]
        for g in units:
            perblock=[errors[blocks==b].mean(axis=0) for b in sorted(set(blocks[groups==g]))]
            donor.append(np.stack(perblock).mean(axis=0))
        mse=np.stack(donor);per=np.sqrt(mse).mean(axis=1)
        return dict(score=float(np.sqrt(mse.mean(axis=0)).mean()),metric='donor_block_macro_rmse',direction='lower',per_unit=per.tolist(),unit_ids=units)
    require(np.isin(pred,[0,1]).all(),'Illegal PV/SST class')
    acc=[];labels=[]
    for g in units:
        y=truth[groups==g];require(len(set(y))==1,'Mouse has mixed genetic labels');labels.append(int(y[0]));acc.append(float((pred[groups==g]==y).mean()))
    value=np.mean([np.mean([v for v,label in zip(acc,labels) if label==c]) for c in [0,1]])
    return dict(score=float(value),metric='class_balanced_mouse_accuracy',direction='higher',per_unit=acc,unit_ids=units,unit_labels=labels)

def audit_task(task,require_complete=False):
    exp=ROOT/'experiments'/task;cache=ROOT/'data/cache'/task;spec=json.loads((exp/'run-spec.json').read_text())
    require(spec['benchmark_id']==task and spec['run_id']=='batch-v11','Unexpected frozen run')
    for rel,digest in spec['frozen_files'].items():require(sha(inside(rel))==digest,'Frozen file changed: '+rel)
    manifest=json.loads((exp/'source.json').read_text())
    for row in manifest['files']:
        p=inside(row['path']);require(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Source hash mismatch: '+row['path'])
    require(sha(cache/'data.npz')==spec['data_sha256'],'Frozen data changed')
    with np.load(cache/'data.npz',allow_pickle=False) as z:data={k:z[k] for k in z.files}
    require(set(data['train_groups']).isdisjoint(data['test_groups']),'Group leakage')
    if task=='K05':require(set(data['train_blocks']).isdisjoint(data['test_blocks']),'Block leakage')
    rows=json.loads((cache/'row-manifest.json').read_text());truth=raw_truth(task,cache,data,rows)
    resultpath=ROOT/'results'/f'{task}.json';results=json.loads(resultpath.read_text()) if resultpath.exists() else []
    results=[r for r in results if r.get('run_id','batch-v11')=='batch-v11' and r.get('slice_id')=='batch-v11']
    seen=set();audited=[];failed=[]
    for row in results:
        model=row['model'];require(model in MODELS and model not in seen,'Unexpected/duplicate attempt');seen.add(model)
        if row['status']!='measured':failed.append(dict(model=model,status=row['status'],reason=row.get('reason')));continue
        p=inside(row['prediction_file']);require(sha(p)==row['prediction_sha256'],'Prediction hash mismatch')
        with np.load(p,allow_pickle=False) as z:pred=z['predictions']
        direct=independent_score(task,pred,truth,data)
        require(row['metric']==direct['metric'] and row['direction']==direct['direction'],'Metric metadata mismatch')
        require(np.isclose(row['score'],direct['score'],rtol=1e-12,atol=1e-15),'Independent score mismatch')
        np.testing.assert_allclose(row['per_unit'],direct['per_unit'],rtol=1e-12,atol=1e-15)
        require(row.get('unit_ids')==direct['unit_ids'],'Per-unit label/order mismatch')
        if task=='K06':require(row.get('unit_labels')==direct['unit_labels'],'Mouse class label mismatch')
        program=exp/(model+'.py') if model!='task-baseline' else exp/'adapter.py'
        require(sha(program)==row['code_sha256'],'Program hash mismatch')
        require(row['prompt_sha256']==spec['prompt_sha256'],'Prompt mismatch')
        audited.append(dict(model=model,prediction_sha256=sha(p),program_sha256=sha(program),original_target_mapping_verified=True,independent_metric=direct))
    missing=sorted(set(MODELS)-seen);complete=not missing and not failed
    if require_complete:require(complete,'Missing or failed expected attempts')
    return dict(benchmark_id=task,verification_status='passed' if complete else 'passed_for_available_measured_attempts',complete=complete,source_files_verified=len(manifest['files']),source_labels_reconstructed=True,group_disjoint=True,measured_attempts=audited,failed_attempts=failed,missing_models=missing,models_or_references_executed=False)

def audit(tasks=('K05','K06'),require_complete=False):
    return dict(run_id='batch-v11',tasks=[audit_task(t,require_complete) for t in tasks],models_or_references_executed=False)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--task',choices=['K05','K06'],action='append');parser.add_argument('--require-complete',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args()
    report=audit(args.task or ('K05','K06'),args.require_complete);text=json.dumps(report,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text)
