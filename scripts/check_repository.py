"""Portable integrity checks without raw-data downloads, scientific dependencies or model calls."""
from pathlib import Path
import hashlib,json,math,re,urllib.parse
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'registry/catalog.json').read_text());ids=[e['id'] for e in c['entries']];assert len(ids)==len(set(ids))
for p in R.rglob('*.md'):
 if 'data/cache' in str(p) or '.git' in p.parts:continue
 # Verbatim upstream documentation keeps its original relative links/nested
 # Markdown. Its bytes are checked by source/frozen seals, not rewritten for
 # this repository. Continue checking all project-authored documentation.
 relative=p.relative_to(R).parts
 if relative[0]=='experiments' and p.name.lower()=='readme.md' and any(part in ['source','upstream'] for part in relative[2:-1]):continue
 for raw in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  target=raw.strip('<>').split('#')[0]
  if not target or re.match(r'\w+://',target):continue
  assert (p.parent/urllib.parse.unquote(target)).exists(),f'Broken link {p}: {target}'
records=[json.loads(line) for line in (R/'results/measurements.jsonl').read_text().splitlines()]
for r in records:
 assert r['benchmark_id'] in ids
 if r['status']=='measured':
  assert isinstance(r['score'],(float,int));p=R/r['prediction_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['prediction_sha256']
  if r.get('posthoc_secondary_metrics'):
   v=r['posthoc_secondary_metrics'];assert v['tp']+v['fp']==v['n_predicted_events'] and v['tp']+v['fn']==v['n_true_events']
   assert abs(v['all_event_f1']-2*v['tp']/(v['n_predicted_events']+v['n_true_events']))<1e-12
for a,b in [('registry/catalog.json','website/data/catalog.json'),('analysis/summary.json','website/data/summary.json'),('results/measurements.jsonl','website/data/measurements.jsonl'),('results/measurements.csv','website/data/measurements.csv')]:
 assert (R/a).read_bytes()==(R/b).read_bytes(),f'Stale site data: {b}'
for task,base in [('C05','experiments/C05/pilot-v1'),('M04','experiments/M04')]:
 for p in json.loads((R/f'experiments/{task}/generation-provenance.json').read_text()):
  code=json.loads((R/base/(p['requested_model']+'.json')).read_text())['code'];assert hashlib.sha256(code.encode()).hexdigest()==p['code_sha256'];assert p['tool_events']==0
decisions=json.loads((R/'registry/admission-decisions.json').read_text());assert {x['benchmark_id'] for x in decisions}==set(ids)
historical={e['id'] for e in json.loads((R/'registry/catalog-history/v04-114.json').read_text())['entries']}
archived={e['id'] for e in json.loads((R/'registry/excluded-candidates.json').read_text())}
assert len(historical)==114 and set(ids).isdisjoint(archived) and set(ids)|archived==historical
for d in (R/'experiments/E01/slices').iterdir():
 if not (d/'run-spec.json').exists():continue
 spec=json.loads((d/'run-spec.json').read_text());seal=json.loads((d/'preparation-seal.json').read_text())
 assert spec['no_new_generation'] and hashlib.sha256((d/'preparation-seal.json').read_bytes()).hexdigest()==spec['source_seal_sha256']
 for filename,digest in seal['files'].items():assert hashlib.sha256((R/filename).read_bytes()).hexdigest()==digest
 for model,digest in spec['model_code_sha256'].items():
  code=json.loads((R/'experiments/E01'/(model+'.json')).read_text())['code'];assert hashlib.sha256(code.encode()).hexdigest()==digest
for e in c['entries']:
 assert (R/e['admission_evidence_file']).exists()
 if e['execution_admission']=='measured':
  d=R/f'benchmarks/{e["family_code"]}/{e["id"]}';intro=(d/'README.md').read_text().split('## Historical')[0]
  assert '**State:** measured.' in intro and 'No experiment admitted yet' not in intro
  assert 'No experiment admitted yet' not in (d/'methods.md').read_text()
for d in (R/'experiments').iterdir():
 if not (d/'run-spec.json').exists() or d.name in ['C05','M04']:continue
 spec=json.loads((d/'run-spec.json').read_text());assert hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest()==spec['prompt_sha256']
 if 'frozen_files' in spec:
  for filename,digest in spec['frozen_files'].items():
   if filename.startswith('data/cache/'):continue
   assert hashlib.sha256((R/filename).read_bytes()).hexdigest()==digest,filename
 codepath=d/('reference.py' if d.name=='N05' else 'adapter.py');assert hashlib.sha256(codepath.read_bytes()).hexdigest()==spec['reference_sha256' if d.name=='N05' else 'adapter_sha256']
 for filename,key in [('protocol.md','protocol_sha256'),('specialist.py','specialist_sha256')]:
  if key in spec:assert hashlib.sha256((d/filename).read_bytes()).hexdigest()==spec[key]
 if 'runner_sha256' in spec:assert hashlib.sha256((R/'scripts/grouped_candidates.py').read_bytes()).hexdigest()==spec['runner_sha256']
 prov=json.loads((d/'generation-provenance.json').read_text());assert len(prov)==3
 for p in prov:
  code=json.loads((d/(p['requested_model']+'.json')).read_text())['code'];assert hashlib.sha256(code.encode()).hexdigest()==p['code_sha256'];assert p['tool_events']==0 and p['usage'] is not None
for task in set(r['benchmark_id'] for r in records if r['model'] in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']):
 for model in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']:assert any(r['benchmark_id']==task and r['model']==model for r in records)
assert not any('luna' in r['model'] for r in records)
follow=R/'experiments/H02/replication-v1'
spec=json.loads((follow/'run-spec.json').read_text())
for filename,digest in spec['sealed_files'].items():assert hashlib.sha256((R/filename).read_bytes()).hexdigest()==digest
rep=json.loads((R/'results/replications/H02.json').read_text())
assert rep['original_primary_macro_unchanged'] and len(rep['attempts'])==9
assert {(r['model'],r['replicate']) for r in rep['attempts']}=={(m,k) for m in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol'] for k in [1,2,3]}
for r in rep['attempts']+rep['references']:
 if r['status']=='measured':assert hashlib.sha256((R/r['prediction_file']).read_bytes()).hexdigest()==r['prediction_sha256']
for p in json.loads((follow/'generation-provenance.json').read_text()):
 assert p['tool_events']==0 and p['user_prompt_sha256']==hashlib.sha256((R/'experiments/H02/prompt.txt').read_bytes()).hexdigest()
 for key in ['output','events']:
  if p[key+'_file']:assert hashlib.sha256((R/p[key+'_file']).read_bytes()).hexdigest()==p[key+'_sha256']
 if p['output_file']:
  code=json.loads((R/p['output_file']).read_text())['code'];row=next(r for r in rep['attempts'] if r['model']==p['requested_model'] and r['replicate']==p['replicate'])
  if row['status']=='measured':assert hashlib.sha256(code.encode()).hexdigest()==row['code_sha256'] and len(code.splitlines())==row['code_lines']
choice=json.loads((follow/'selection.json').read_text());tuned=next(r for r in rep['references'] if r['model']=='xdawn-tslr-tuned')
if tuned['status']=='measured':
 assert hashlib.sha256((follow/'selection.json').read_bytes()).hexdigest()==tuned['selection_sha256']
 assert len(choice['candidates'])==12 and choice['chosen_index']==max(range(12),key=lambda i:choice['candidates'][i]['validation_score'])
 assert hashlib.sha256((follow/'validation-predictions.npz').read_bytes()).hexdigest()==json.loads((follow/'verification.json').read_text())['selection_checks']['oof_prediction_sha256']
snapshot=R/'results/archive/v07-measurements.jsonl'
assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==json.loads((follow/'verification.json').read_text())['original_macro_measurements_sha256']
old_records=[json.loads(v) for v in snapshot.read_text().splitlines()]
for row in old_records:assert row in records,'A historical first-submission record changed'
for suffix in ['json','csv']:assert (R/f'results/replications/H02.{suffix}').read_bytes()==(R/f'website/data/H02-replication.{suffix}').read_bytes()
print(f'Integrity checks passed: {len(ids)} task cards, {len(records)} records, linked files, predictions, provenance and synchronized site data.')
print('H02 follow-up integrity passed: all 9 planned generations, separate results, unchanged original macro ledger.')
for task in ['K04','M01']:
 d=R/f'experiments/{task}';events=json.loads((d/'generation-event-files.json').read_text());assert len(events)==3
 for entry in events:
  assert hashlib.sha256((R/entry['event_file']).read_bytes()).hexdigest()==entry['sha256'] and entry['tool_events']==0 and entry['submission_matches_final_generation_event']
 assert len(json.loads((d/'verification.json').read_text())['prediction_checks'])==5
print('K04/M01 source, scorer, frozen runner and retained generation event evidence present.')
posterior=R/'experiments/L06'
if posterior.exists():
 source_record=json.loads((posterior/'source-record.json').read_text())
 for filename,digest in source_record['upstream_files'].items():assert hashlib.sha256((R/filename).read_bytes()).hexdigest()==digest
 verification=json.loads((posterior/'verification.json').read_text())
 assert len(verification['prediction_checks'])==5 and verification['source_files_verified']==42
 for event in verification['generation_checks']:
  assert hashlib.sha256((R/event['event_file']).read_bytes()).hexdigest()==event['sha256'] and event['tool_events']==0
 for row in records:
  if row['benchmark_id']=='L06' and row['status']=='measured':
   assert hashlib.sha256((R/row['scorer_audit_file']).read_bytes()).hexdigest()==row['scorer_audit_sha256']
 snapshot=R/'results/archive/v08-measurements.jsonl'
 for line in snapshot.read_text().splitlines():assert json.loads(line) in records,'A v0.8 historical record changed'
 print('L06 frozen posterior interface, all5 prediction/audit identities, sources and raw generation events passed; v0.8 records unchanged.')
compression=R/'experiments/B07'
if compression.exists():
 verification=json.loads((compression/'verification.json').read_text())
 assert verification['source_chunks_verified']==16 and verification['source_bytes_verified']==50331648
 for event in verification['generation_checks']:
  assert hashlib.sha256((R/event['event_file']).read_bytes()).hexdigest()==event['sha256'] and event['tool_events']==0 and event['submission_matches_final_generation_event']
 for row in records:
  if row['benchmark_id']!='B07' or row['status']!='measured':continue
  items=json.loads((R/row['prediction_file']).read_text());assert len(items)==16
  for item in items:
   payload=(R/item['compressed_file']).read_bytes();assert len(payload)==item['compressed_bytes'] and hashlib.sha256(payload).hexdigest()==item['compressed_sha256']
   assert item['lossless'] and item['decoded_sha256']==item['source_sha256']
  assert abs(sum(8*x['compressed_bytes']/(4096*384) for x in items)/16-row['score'])<1e-12
 for line in (R/'results/archive/v09-measurements.jsonl').read_text().splitlines():assert json.loads(line) in records,'A v0.9 historical record changed'
 print('B07 saved bitstream hashes/size arithmetic and source-audit evidence passed; all v0.9 records unchanged. CI does not redownload raw chunks or rerun decoders.')

def check_batch_integrity(ledger):
 """Portable batch evidence checks: no NumPy, source cache, decoder or fitting."""
 models=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
 tasks=('B03','B08','C06','E06','K05','K06','A15')
 reports={'B03':'results/audits/B03-batch-v11.json','C06':'results/audits/C06-batch-v11.json',
  'E06':'results/verification/E06-batch-v11.json','K05':'results/audits/cells-batch-v11.json',
  'K06':'results/audits/cells-batch-v11.json','B08':'results/verification/B08-independent-final.json',
  'A15':'results/audits/A15-batch-v11.json'}
 def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
 def path(rel):
  p=(R/rel).resolve();assert p.is_relative_to(R.resolve()),'Batch artifact outside repository';return p
 def read(rel):return json.loads(path(rel).read_text())
 historical=[json.loads(line) for line in (R/'results/archive/v10-measurements.jsonl').read_text().splitlines()]
 for row in historical:assert row in ledger,'A v0.10 first-submission row changed'
 total=measured=event_count=payload_count=0
 for task in tasks:
  d=R/f'experiments/{task}';spec=json.loads((d/'run-spec.json').read_text())
  assert spec['run_id']=='batch-v11' and spec['models']==list(models) and spec['reasoning_effort']=='high'
  assert spec['generation_replicates']==1 and spec['timeout_seconds']==180 and spec['line_limit_exclusive']==240
  assert digest(d/'prompt.txt')==spec['prompt_sha256']
  for rel,h in spec['frozen_files'].items():
   if not rel.startswith('data/cache/'):assert digest(path(rel))==h,rel
  prov=json.loads((d/'generation-provenance.json').read_text());events=json.loads((d/'generation-event-files.json').read_text())
  assert len(prov)==len(events)==3
  assert {p['requested_model'] for p in prov}=={p['model'] for p in events}==set(models)
  code_hashes={}
  for model in models:
   submission=json.loads((d/(model+'.json')).read_text());code=submission['code'];h=hashlib.sha256(code.encode()).hexdigest();code_hashes[model]=h
   if (d/(model+'.py')).exists():assert (d/(model+'.py')).read_bytes()==code.encode(),'Saved batch code differs from generation'
   p=next(p for p in prov if p['requested_model']==model);e=next(e for e in events if e['model']==model)
   assert p['code_sha256']==h and p['code_lines']==len(code.splitlines()) and p['tool_events']==0
   assert p['user_prompt_sha256']==spec['prompt_sha256'] and p['reasoning_effort']=='high' and p['generation_replicates']==1
   assert p['usage'] is not None and e['tool_events']==0 and e['submission_matches_final_generation_event']
   eventpath=path(e['event_file']);assert digest(eventpath)==e['sha256']
   raw=[json.loads(line) for line in eventpath.read_text().splitlines() if line.strip()]
   messages=[v['item']['text'] for v in raw if v.get('type')=='item.completed' and v.get('item',{}).get('type')=='agent_message']
   assert messages and json.loads(messages[-1])==submission
   assert sum(v.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for v in raw)==0
   assert next(v['usage'] for v in reversed(raw) if v.get('type')=='turn.completed')==p['usage'];event_count+=1
  local=read(f'results/{task}.json');local=[r for r in local if r.get('run_id','batch-v11')=='batch-v11']
  refs=('spikepack','task-baseline') if task=='B08' else ('task-baseline','mean-baseline') if task=='E06' else ('task-baseline',)
  slices=('batch-v11','taxis') if task=='E06' else ('batch-v11',)
  expected={(s,m) for s in slices for m in models+refs}
  assert len(local)==len(expected) and {(r['slice_id'],r['model']) for r in local}==expected,'Missing/duplicate batch attempts'
  audit=read(reports[task])
  if task in ['K05','K06']:
   assert audit['models_or_references_executed'] is False
   audit=next(v for v in audit['tasks'] if v['benchmark_id']==task)
   assert audit['source_labels_reconstructed'] and audit['group_disjoint']
  assert not audit.get('missing_attempts',audit.get('missing_models',[])),'Independent audit has missing attempts'
  if task!='B08':assert audit['complete'] and audit['models_or_references_executed'] is False
  else:assert audit['encoder_invoked'] is False and len(audit['original_sources'])==7
  audited={(a.get('slice_id','batch-v11'),a['model']):a for a in audit['measured_attempts']}
  failures={(a.get('slice_id','batch-v11'),a['model']):a for a in audit['failed_attempts']}
  assert set(audited).isdisjoint(failures) and set(audited)|set(failures)==expected
  for row in local:
   matching=[v for v in ledger if v['benchmark_id']==task and v.get('slice_id')==row['slice_id'] and v['model']==row['model']]
   assert len(matching)==1 and all(matching[0].get(k)==v for k,v in row.items()),'Central batch row differs from retained attempt'
   saved=matching[0];key=(row['slice_id'],row['model']);total+=1
   if row['status']!='measured':
    assert key in failures and failures[key]['status']==row['status'] and failures[key].get('reason')==row.get('reason')
    assert row.get('reason') and 'score' not in row;continue
   measured+=1;identity=audited[key]
   prediction=path(row['prediction_file']);assert digest(prediction)==row['prediction_sha256']
   assert row['prompt_sha256']==spec['prompt_sha256']
   expected_code=code_hashes[row['model']] if row['model'] in models else digest(d/('reference.py' if task=='B08' else 'adapter.py'))
   assert row['code_sha256']==expected_code
   if row['model'] in models:assert (d/(row['model']+'.py')).exists()
   assert identity.get('program_sha256',identity.get('code_sha256'))==expected_code
   if 'prediction_sha256' in identity:assert identity['prediction_sha256']==row['prediction_sha256']
   value=identity.get('score',identity.get('independent_metric',{}).get('score'))
   assert math.isclose(value,row['score'],rel_tol=1e-7,abs_tol=2e-6),'Independent audit score differs'
   if 'scorer_audit_file' in saved:
    assert saved['scorer_audit_file']==reports[task] and digest(path(saved['scorer_audit_file']))==saved['scorer_audit_sha256']
   if task=='B08':
    items=json.loads(prediction.read_text());assert len(items)==7 and identity['seven_recordings_passed']
    per=[]
    for item,source in zip(items,audit['original_sources']):
     blob=path(item['compressed_file']).read_bytes();assert len(blob)==item['compressed_bytes'] and hashlib.sha256(blob).hexdigest()==item['compressed_sha256']
     assert item['recording']==source['recording'] and item['n_events']==source['n_events']
     assert item['labels_exact'] and item['max_timing_error_seconds']<=50e-6+1e-10
     per.append(8*len(blob)/item['n_events']);payload_count+=1
    assert math.isclose(sum(per)/7,row['score'],rel_tol=0,abs_tol=1e-12)
    assert all(math.isclose(a,b,rel_tol=0,abs_tol=1e-12) for a,b in zip(per,identity['per_record_bits_per_event']))
    assert identity['max_timing_error_seconds']<=50e-6+1e-10
    assert identity['total_encoded_bytes']==sum(i['compressed_bytes'] for i in items)
  if task=='C06':assert audit['train_test_specimens_and_neurons_disjoint'] and audit['independent_event_binning_and_gaussian_reconstruction']
  if task=='E06':assert audit['training_arrays_identical'] and audit['train_test_target_disjoint'] and audit['main_taxis_targets_disjoint'] and set(audit['program_reuse_verified_models'])==set(models+refs)
  if task=='B03':assert not audit['source_voltage_regenerated'] and len(audit['simulation_checks'])==8
  if task=='A15':assert audit['n_test_recordings']==20 and audit['n_test_birds']==1
 assert total==35 and event_count==21
 return dict(tasks=len(tasks),attempts=total,measured=measured,generation_event_logs=event_count,codec_payloads=payload_count,historical_rows_unchanged=len(historical))

batch=check_batch_integrity(records)
print('Batch v11 portable integrity passed:',batch,'No raw data, fitting, model calls or fresh decoding used.')
