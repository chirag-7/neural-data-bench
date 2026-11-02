"""Post-hoc best-observed code procedure vs specialist/reference comparison; no fitting."""
from pathlib import Path
import json,hashlib,math,statistics,csv
from collections import Counter
R=Path(__file__).resolve().parents[1]; OUT=R/'analysis/specialist-frontier-v1'
SOURCES=['analysis/generation-comparison-v2/generation-comparison.json','website/data/H02-replication.json','registry/task-facets-v1.json','registry/catalog.json']
SPECIALIST_CLASSES={'historical_specialist','local_specialist','pretrained_specialist'}
SPECIALIST_METHODS={'mountainsort5','spikepack','wavpack-high','delta-blosc-zstd','deneux','speiser','friedrich','rupprecht','oasis-default','pyriemann-aligned','pyriemann-ts-svm','xdawn-tslr','xdawn-tslr-tuned','yasa-eeg','mriqc-rfc-2017','singler','polya-gamma'}
def summarize(tasks,field):
 return [{'analysis':mode,'n_tasks':len(tasks),'counts':dict(Counter(t[field]['classes'][mode] if t[field] else 'unavailable' for t in tasks))} for mode in ['raw','iqr_0.1','iqr_0.5']]
def main():
 d=json.loads((R/SOURCES[0]).read_text());rep=json.loads((R/SOURCES[1]).read_text());facets=json.loads((R/SOURCES[2]).read_text());annotations={a['benchmark_id']:a for a in facets['assignments']};models=d['models'];tasks=[];names={e['id']:e['task'] for e in json.loads((R/SOURCES[3]).read_text())['entries']}
 for t in d['tasks']:
  sign=1 if t['direction']=='higher' else -1
  vals=[t['scores'][m] for m in models];assert all(math.isfinite(v) for v in vals)
  q1,_,q3=statistics.quantiles(vals,n=4,method='inclusive');iqr=q3-q1; best=max(sign*v for v in vals)
  winners=[m for m in models if abs(sign*t['scores'][m]-best)<=1e-9];best_score=t['scores'][winners[0]]
  refrows=[x for x in t['chart_rows'] if x['model'] not in models]; supplement=[]
  if t['benchmark_id']=='H02':
   for x in rep['references']:
    if x['model']=='xdawn-tslr-tuned':
     assert t['n_slices']==1 and x['metric']==t['metric'] and x['direction']==t['direction']
     refrows.append({**x,'slice_id':t['slice_ids'][0],'reference_type':'local_specialist_reproduction_train_cv_followup'});supplement.append(x['model'])
  candidates=[];excluded=[]
  for name in sorted({x['model'] for x in refrows}):
   rs=[x for x in refrows if x['model']==name]; ids=[x['slice_id'] for x in rs]
   if len(set(ids))!=t['n_slices'] or set(ids)!=set(t['slice_ids']) or len(rs)!=len(set(ids)) or any(x.get('status')!='measured' or x.get('score') is None or not math.isfinite(x['score']) for x in rs):
    excluded.append({'model':name,'reason':'Incomplete or duplicate slice coverage; no imputation or per-slice winner stitching.'});continue
   score=statistics.mean(x['score'] for x in rs)
   primary=t.get('primary_reference',{});specialist=name in SPECIALIST_METHODS or name.startswith('vassi-run-') or (name in primary.get('names',[]) and primary.get('reference_class') in SPECIALIST_CLASSES)
   candidates.append({'model':name,'score':score,'specialist':specialist,'n_slices':len(rs),'reference_types':sorted(set(x.get('reference_type','unspecified') for x in rs)),'source':'H02-replication references' if name in supplement else 'retained comparison chart_rows'})
  def compare(pool):
   if not pool:return None
   b=max(sign*x['score'] for x in pool);selected=[x for x in pool if abs(sign*x['score']-b)<=1e-9];r=selected[0];delta=sign*(best_score-r['score']);raw='numerical_tie' if abs(delta)<=1e-9 else 'general_better' if delta>0 else 'specialist_better'
   ratio=delta/iqr if iqr>0 else None;classes={'raw':raw}
   for threshold in [.1,.5]:
    classes['iqr_'+str(threshold)]='within_band' if raw=='numerical_tie' else 'not_estimable' if ratio is None else 'general_better' if ratio>threshold+1e-12 else 'specialist_better' if ratio< -threshold-1e-12 else 'within_band'
   return {'methods':[x['model'] for x in selected],'score':r['score'],'raw_native_delta':best_score-r['score'],'direction_adjusted_delta':delta,'gap_in_general_panel_iqr':ratio,'classes':classes}
  tasks.append({'benchmark_id':t['benchmark_id'],'task':names[t['benchmark_id']],'family_code':annotations[t['benchmark_id']]['family_code'],'metric':t['metric'],'direction':t['direction'],'general_scores':t['scores'],'best_general_models':winners,'best_general_score':best_score,'q1':q1,'q3':q3,'general_panel_iqr':iqr,'best_specialist':compare([x for x in candidates if x['specialist']]),'best_available_reference':compare(candidates),'candidates':candidates,'excluded_candidates':excluded,'reference_evidence':t['primary_reference']['evidence'],'current_global_sota_verified':False})
 result={'revision':'specialist-frontier-v1','paradigm':'Neuroscience Analysis Code Generation','models':models,'n_tasks':len(tasks),'n_tasks_with_specialists':sum(t['best_specialist'] is not None for t in tasks),'summaries':{'specialist_only':summarize(tasks,'best_specialist'),'all_available_references':summarize(tasks,'best_available_reference')},'tasks':tasks,'selection':'Best test-score task mean among four retained general procedures; best complete specialist method separately. Post-hoc, unequal candidate pools and repair effort; not deployment selection.','normalization':'Direction-adjusted best-general minus comparator, divided by IQR of the original four general-model task means; inclusive linear quartiles. References are not added to that scale.','thresholds':[.1,.5],'tie_tolerance':1e-9,'input_sha256':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in SOURCES}}
 OUT.mkdir(exist_ok=True);s=json.dumps(result,indent=2,allow_nan=False)+'\n';(OUT/'comparison.json').write_text(s);(R/'website/data/specialist-frontier.json').write_text(s)
 with (OUT/'task-comparisons.csv').open('w') as f:
  fields=['benchmark_id','family_code','metric','direction','best_general_models','best_general_score','general_panel_iqr','comparator_scope','comparator_methods','comparator_score','raw_native_delta','direction_adjusted_delta','gap_in_general_panel_iqr','raw','iqr_0.1','iqr_0.5'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for t in tasks:
   for scope,key in [('specialist_only','best_specialist'),('all_available_references','best_available_reference')]:
    ref=t[key];row={k:t[k] for k in fields if k in t};row['best_general_models']=';'.join(t['best_general_models']);row['comparator_scope']=scope
    if ref:row.update(comparator_methods=';'.join(ref['methods']),comparator_score=ref['score'],**{k:ref[k] for k in ['raw_native_delta','direction_adjusted_delta','gap_in_general_panel_iqr']},**ref['classes'])
    else:row.update({k:'unavailable' for k in ['raw','iqr_0.1','iqr_0.5']})
    w.writerow(row)
 print(json.dumps(result['summaries'],indent=2));return result
if __name__=='__main__':main()
