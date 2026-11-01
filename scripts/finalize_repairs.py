"""Report-only repair finalization; read retained outputs, never run procedures.

The sealed round2 runner completed scientific work but its report assembly hit
sum(None). Preserve that source and every original result; finalize saved rows.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments/repairs-v1'
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def check(folder):
 spec=json.loads((folder/'run-spec.json').read_text())
 for rel,h in spec['frozen_files'].items():assert sha(ROOT/rel)==h,rel
 return spec
def normalized(row,history=False):
 row=dict(row);row['model']=row.get('model',row['method']);task=row['benchmark_id'];model=row['model']
 row['original_key']=dict(benchmark_id=task,slice_id='batch-v11' if task=='B08' else 'expansion-v1',model=model)
 row['repair_type']=row.get('repair_kind','harness_only' if task=='B08' else 'manual_minimal_algorithm_patch')
 row['repair_revision']=row.get('repair_revision',1);row['history_only']=history
 row['control_originally_successful']=bool(row.get('control_originally_successful',False))
 if row['status']=='measured':
  code=BASE/'N05/revision-2/gpt-5.6-sol.py' if task=='N05' and row['repair_revision']==2 else BASE/task/(model+'.py') if model in MODELS else ROOT/'experiments/B08/reference.py'
  assert sha(code)==row['code_sha256'];row['code_file']=str(code.relative_to(ROOT))
  assert sha(ROOT/row['prediction_file'])==row['prediction_sha256']
 return row

def main():
 archive=ROOT/'results/repairs-v1/round-1.json';prior=json.loads(archive.read_text())
 for task in ['B08','J08','N05','C05']:check(BASE/task)
 check(BASE/'N05/revision-2');check(BASE/'B08/decode-revision-2')
 for rel,h in json.loads((BASE/'original-preservation.json').read_text()).items():assert sha(ROOT/rel)==h
 rows=json.loads((BASE/'B08/decode-revision-2/common-procedure-results.json').read_text());b08=[];verification=[]
 for row in rows:
  method=row['method'];folder=BASE/'B08/decode-revision-2'/method
  audit=json.loads((folder/'audit.json').read_text());plan=json.loads((folder/'plan.json').read_text())
  assert audit['code_sha256']==row['code_sha256'] and not audit['encoder_invoked'] and not audit['source_arrays_loaded']
  assert audit['pid']!=audit['parent_pid'] and len(audit['items'])==7
  assert sha(ROOT/plan['program'])==plan['program_file_sha256']
  items=json.loads((ROOT/row['prediction_file']).read_text());per=[];errors=[]
  # No decoder/encoder here. Compare retained fresh-output identities to the
  # common-procedure validation and bitstreams already sealed for round2.
  for decoded,saved in zip(audit['items'],items):
   p=ROOT/decoded['decoded_file'];assert sha(p)==decoded['sha256']
   assert decoded['times_sha256']==saved['decoded_times_sha256'] and decoded['labels_sha256']==saved['decoded_labels_sha256']
   blob=ROOT/saved['compressed_file'];assert sha(blob)==saved['compressed_sha256'] and blob.stat().st_size==saved['compressed_bytes']
   with np.load(p,allow_pickle=False) as z:
    t=z['times'];y=z['labels'];assert t.shape==y.shape==(saved['n_events'],) and np.isfinite(t).all() and np.all(np.diff(t)>=0)
    assert hashlib.sha256(np.ascontiguousarray(t).tobytes()).hexdigest()==saved['decoded_times_sha256']
    assert hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()==saved['decoded_labels_sha256']
   assert saved['labels_exact'] and saved['max_timing_error_seconds']<=50e-6+1e-10
   per.append(8*saved['compressed_bytes']/saved['n_events']);errors.append(saved['max_timing_error_seconds'])
  assert np.allclose(per,row['per_unit'],rtol=0,atol=1e-12) and math.isclose(sum(per)/7,row['score'],rel_tol=0,abs_tol=1e-12)
  decoded=dict(status='passed',fresh_process=True,encoder_invoked=False,n_recordings=7,
   max_timing_error_seconds=max(errors),report_file=str((folder/'audit.json').relative_to(ROOT)),report_sha256=sha(folder/'audit.json'))
  row=dict(row,repair_revision=2,encoder_rerun=False,independent_decode=decoded,
   decode_repair_spec_sha256=sha(BASE/'B08/decode-revision-2/run-spec.json'))
  row=normalized(row)
  original=next(r for r in json.loads((ROOT/'results/B08.json').read_text()) if r['model']==method)
  if original['status']=='measured':
   assert math.isclose(row['score'],original['score'],rel_tol=0,abs_tol=1e-12)
   olditems=json.loads((ROOT/original['prediction_file']).read_text())
   row['control_score_matches_original']=True
   row['control_payloads_match_original']=all(a['compressed_sha256']==b['compressed_sha256'] for a,b in zip(items,olditems))
  if method in MODELS:
   original_code=json.loads((ROOT/f'experiments/B08/{method}.json').read_text())['code']
   assert (ROOT/row['code_file']).read_bytes()==original_code.encode();row['program_byte_unchanged']=True
  b08.append(row);verification.append(dict(benchmark_id='B08',model=method,n_payloads=7,saved_fresh_decode_identity_and_metric_arithmetic_passed=True))
 log=BASE/'N05/revision-2/execution.txt';n05=json.JSONDecoder().raw_decode(log.read_text().lstrip())[0]
 assert n05['status']=='measured' and n05['all_fields_correct'] and n05['n_units']==61
 n05=normalized(n05);n05['execution_log']=str(log.relative_to(ROOT))
 j08=normalized(next(r for r in prior['attempts'] if r['benchmark_id']=='J08'))
 with np.load(ROOT/j08['prediction_file'],allow_pickle=False) as z:
  pred=z['predictions'];assert pred.shape==(2,727,546) and np.isfinite(pred).all() and np.all(pred>=0) and np.all(pred==np.floor(pred))
 final=[j08,n05]+b08
 history=[normalized(r,True) for r in prior['attempts']]+[r for r in final if r['benchmark_id']!='J08']
 unresolved=[dict(c,original_key=dict(benchmark_id='C05',slice_id=c['slice_id'],model=c['model']),repair_type='archived_output_incomplete_no_fabrication') for c in prior['c05_cases']]
 report=dict(track='posthoc-repairs-v1',status='complete',not_single_shot=True,excluded_from_original_macro=True,new_model_calls=0,
  attempts=history,latest_successes=final,unresolved=unresolved,
  repair_attempt_history_file=str(archive.relative_to(ROOT)),repair_attempt_history_sha256=sha(archive),
  original_results_and_ledger_unchanged=True,original_failures_considered=8,
  repair_assisted_failures_recovered=sum(r['original_status']=='failed' for r in final),controls_reexecuted=sum(r['control_originally_successful'] for r in final),
  strict_format_recovered_failures=sum(r['original_status']=='failed' and r.get('line_limit_compliant') is True for r in final),
  irreparable_archived_cases=4,c05_cases=unresolved,
  finalizer=dict(script='scripts/finalize_repairs.py',sha256=sha(Path(__file__)),reason='Sealed round2 runner completed outputs but failed only assembling controls count because None was summed. Finalizer uses retained successful worker/decode reports; no procedure rerun or scientific code change.'),
  scientific_caveats=['Repair-assisted output is never a replacement for single-shot evidence.',
   'Four runtime failures were recovered numerically; three meet the original line limit. N05 originally had249lines and revision2 remains over the limit; no cosmetic rewrite.',
   'First N05patch failure and first independent-reference decoder dependency-resolution failures remain in round1 history.',
   'C05source archives cannot satisfy full-support prediction contract; original source jointly-masked-NaN scoring is a different partial-coverage endpoint, not a complete-output repair. No missing values filled.'])
 write(ROOT/'results/repairs-v1.json',report)
 write(BASE/'verification.json',dict(status='passed',first_attempt_results_and_ledger_unchanged=True,
  all_repair_seals_and_original_code_hashes_pass=True,B08=verification,J08=dict(repaired_shape=[2,727,546],finite_integer_instances=True),
  N05=dict(status='passed',all_fields_correct=True,n_fields=61,metadata_only_patch=True),
  result_file='results/repairs-v1.json',result_sha256=sha(ROOT/'results/repairs-v1.json'),
  method_or_encoder_or_decoder_executed_by_finalizer=False))
 print(json.dumps(dict(recovered=report['repair_assisted_failures_recovered'],controls=report['controls_reexecuted'],unresolved=4,
  latest=[{k:r[k] for k in ['benchmark_id','model','score','metric','line_limit_compliant']} for r in final]),indent=2))
if __name__=='__main__':main()
