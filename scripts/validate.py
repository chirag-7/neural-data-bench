"""Scientific artifact checks; no model calls or estimator retraining."""
import ast, hashlib, json
import numpy as np
import pandas as pd
from evaluate import ROOT, score, nll, MODELS
checks={}
cat=json.loads((ROOT/'registry/catalog.json').read_text());ids=[e['id'] for e in cat['entries']]
assert len(ids)==len(set(ids))
historical=json.loads((ROOT/'registry/catalog-history/v04-114.json').read_text())
old_ids={e['id'] for e in historical['entries']}
excluded=json.loads((ROOT/'registry/excluded-candidates.json').read_text())
excluded_ids={e.get('benchmark_id',e.get('id')) for e in excluded}
assert len(old_ids)==114 and set(ids).isdisjoint(excluded_ids)
assert set(ids)|excluded_ids==old_ids
for e in cat['entries']:
    for name in ['README.md','methods.md','worklog.md','data.json','references.json']:
        assert (ROOT/f'benchmarks/{e["family_code"]}/{e["id"]}/{name}').exists()
checks['registry_and_task_cards']=f'{len(ids)} active source-linked cards; {len(excluded_ids)} auditable archived candidates; 114 historical entries'
manifest=json.loads((ROOT/'data/manifests/spikefinder.json').read_text())
for f in manifest['files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
checks['acquired_input_hashes']=len(manifest['files'])
ns=dict(np.__dict__);tree=ast.parse((ROOT/'data/cache/spikefinder/spikefinder_eval.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['_downsample','_corr']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'pinned_official_scorer','exec'),ns)
records=[json.loads(s) for s in (ROOT/'results/measurements.jsonl').read_text().splitlines()]
archive=pd.read_csv(ROOT/'data/cache/spikefinder/results_30_06_17.csv');archive_checks=0;pred_checks=0
for r in records:
    if r['status']!='measured' or r['benchmark_id'] not in ['C05','M04']:continue
    p=ROOT/r['prediction_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['prediction_sha256']
    pred=np.load(p)['predictions'];pred_checks+=1
    if r['benchmark_id']=='C05':
        truth=pd.read_csv(ROOT/f'data/cache/spikefinder/{r["slice_id"]}.test.spikes.csv').to_numpy(float)
        official=[]
        for j in range(truth.shape[1]):
            mask=np.isfinite(truth[:,j]);x=ns['_downsample'](pred[mask,j],4);y=ns['_downsample'](truth[mask,j],4)
            official.append(ns['_corr'](x,y) if np.std(x)>0 else 0.)
        assert np.allclose(r['per_unit'],official,atol=1e-12,rtol=0)
        if r['model'] in ['deneux','speiser','friedrich','rupprecht']:
            rows=archive[(archive.algo==r['model'])&(archive.dset==int(r['slice_id']))&(archive.split=='test')&(archive.measure=='corr')].sort_values('cell')
            assert len(rows)==len(official)
            assert np.allclose(rows.value.to_numpy(),official,atol=1e-10,rtol=0);archive_checks+=1
    else:
        a=np.load(ROOT/'data/cache/cognitive-v1.npz');errors=np.mean(np.abs(pred-a['truth'])/[.98,9.9],axis=1)
        assert np.allclose(errors,r['per_unit'],atol=1e-15)
        assert np.isclose(np.mean(errors),r['score'])
checks['prediction_files_and_hashes']=pred_checks
checks['official_function_equivalence']='all complete C05 predictions'
checks['published_archive_cell_agreement']=archive_checks
alpha,beta=.3,2.;expected=np.log(2)+np.logaddexp(0,beta*alpha*.5)
assert np.isclose(nll([alpha,beta],[1,0],[1,0])[0],expected)
checks['cognitive_likelihood_hand_fixture']='passed'
mle=next(r for r in records if r['model']=='canonical-mle')
checks['mle_converged_agents']=sum(x['success'] for x in mle['optimization_diagnostics'])
assert checks['mle_converged_agents']==24
for model in MODELS:
    r=next(r for r in records if r['benchmark_id']=='C05' and r['slice_id']=='1' and r['model']==model)
    old=json.loads((ROOT/f'experiments/C05/pilot-v1/{model}.scores.json').read_text())
    assert np.allclose(r['per_unit'],old['per_neuron'],atol=1e-12)
checks['original_pilot_reproduction']='all three models agree'
assert not any('luna' in r['model'] for r in records)
assert all(r.get('score') is None or np.isfinite(r['score']) for r in records)
checks['central_store_records']=len(records)
checks['model_attempts']=sum(r['model'] in MODELS for r in records)
(ROOT/'analysis/validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
