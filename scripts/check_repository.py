"""Portable integrity checks without raw-data downloads, scientific dependencies or model calls."""
from pathlib import Path
import hashlib,json,re,urllib.parse
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'registry/catalog.json').read_text());ids=[e['id'] for e in c['entries']];assert len(ids)==len(set(ids))
for p in R.rglob('*.md'):
 if 'data/cache' in str(p) or '.git' in p.parts:continue
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
 if d.name=='L06':
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
