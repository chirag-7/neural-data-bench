"""Consolidate completed, independently audited extension attempts without altering them."""
from pathlib import Path
import collections,datetime,hashlib,json,math
R=Path(__file__).resolve().parents[1];B=R/'experiments/generation-extension-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def main():
 manifest=read(B/'manifest.json');models=[x['requested_snapshot'] for x in manifest['new_models']];ledger=read(B/'api-cost-ledger.json');calls=ledger['requests'];keys=[(x['task'],x['model']) for x in calls]
 assert len(calls)==60 and len(set(keys))==60,'Every task/model must have exactly one provider call'
 assert all(x['status']!='dispatched' for x in calls),'Provider request still in flight'
 assert ledger['conservative_spent_or_reserved_usd']<=15
 audits=read(B/'saved-output-audits.json')['records'];byhash={a['original_result_sha256']:a for a in audits};rows=[];provs=[]
 for t in manifest['tasks']:
  tid=t['benchmark_id'];taskrows=[]
  for m in models:
   gp=B/'generation'/tid/m/'provenance.json';g=read(gp);provs.append(dict(benchmark_id=tid,model=m,file=str(gp.relative_to(R)),sha256=sha(gp),status=g['status']))
   for sid in t['original_slices']:
    p=B/'artifacts'/tid/m/sid/'result.json'
    if g['status']=='generated':
     assert p.exists(),(tid,m,sid,'missing execution');row=read(p)
     assert row['submission_sha256']==sha(R/row['submission_file'])
     if row['status']=='measured':
      assert isinstance(row['score'],(int,float)) and math.isfinite(row['score'])
      assert sha(R/row['prediction_file'])==row['prediction_sha256']
      a=byhash[sha(p)];assert a['status']=='passed';assert sha(R/a['audit_result_file'])==a['audit_result_sha256'];row['saved_output_audit_file']=a['audit_result_file']
     row['initial_result_file']=str(p.relative_to(R));row['initial_result_sha256']=sha(p)
    else:
     assert not p.exists();row=dict(benchmark_id=tid,slice_id=sid,model=m,status='failed',failure_phase='generation',reason=g.get('error',g['status']),run_id='generation-extension-v1',track='T3',generation_replicates=1,code_repaired=False,superiority_eligible=False)
    row.update(generation_provenance_file=str(gp.relative_to(R)),generation_provenance_sha256=sha(gp),provider='OpenAI Responses API',requested_snapshot=m,returned_snapshot=g.get('returned_model'),generation_status=g['status'])
    if tid in {'H02','K04','M01'}:row['unit_metadata_note']='n_units in the sealed generic evaluator counts prediction rows; use the native scorer per_unit/group_results for group-equal scoring units.'
    rows.append(row);taskrows.append(row)
  lines=[f'# {tid}: older-model extension','',f'Category {t["family"]}; original contract: [task folder](../../../{tid}/). Exact prompt: [{Path(t["prompt_file"]).name}](../../../../{t["prompt_file"]}).','',f'Prompt SHA256: `{t["prompt_sha256"]}`. One unchanged program per model, reused across {len(t["original_slices"])} dependent slice(s). No test scores or execution feedback were passed to generation.','', '| Snapshot | Slice | Status | Native score | Within line limit | Initial result |','|---|---|---|---:|---|---|']
  for r in taskrows:
   path=r.get('initial_result_file',r['generation_provenance_file']);rel='../../../../'+path
   lines.append(f'| {r["model"]} | {r["slice_id"]} | {r["status"]} | {r.get("score","missing")} | {r.get("line_limit_compliant","unavailable")} | [record]({rel}) |')
  lines+=['','## Steps and interpretation','','1. Verify the original prompt and generation/execution seals.','2. Generate one structured program through the restricted API bridge; retain the original provider response and code.','3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.','4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.','5. Consolidate these rows once with the full panel; no missing score is imputed.','','[Generation responses and programs](../../generation/'+tid+'/), [slice artifacts and logs](../../artifacts/'+tid+'/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).','','These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.']
  writepath=B/'tasks'/tid/'README.md';writepath.parent.mkdir(parents=True,exist_ok=True);writepath.write_text('\n'.join(lines)+'\n')
 assert len(rows)==74
 result=dict(study='generation-extension-v1',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),models=models,task_count=30,family_count=14,planned_generations=60,provider_call_count=len(calls),model_slice_attempts=74,counts=[dict(model=m,**dict(collections.Counter(r['status'] for r in rows if r['model']==m))) for m in models],cost_policy='Conservative uncached-rate token accounting; unused credit remains in the account; no automatic recharge.',conservative_spent_or_reserved_usd=ledger['conservative_spent_or_reserved_usd'],actual_uncached_rate_usd=sum(x.get('actual_uncached_rate_usd',0) for x in calls),budget_ceiling_usd=15,input_sha256={str(p.relative_to(R)):sha(p) for p in [B/'manifest.json',B/'generation-seal.json',B/'execution-seal.json',B/'api-cost-ledger.json',B/'saved-output-audits.json']},generation_provenance=provs,records=rows)
 write(R/'results/generation-extension-v1.json',result);write(B/'final-run-status.json',{k:v for k,v in result.items() if k not in {'records','generation_provenance'}})
 print(json.dumps({k:result[k] for k in ['task_count','family_count','provider_call_count','model_slice_attempts','counts','actual_uncached_rate_usd']},indent=2))
if __name__=='__main__':main()
