"""Consolidate audited manual repairs; originals and unsuccessful revisions stay intact."""
from pathlib import Path
import hashlib,json,datetime,ast
R=Path(__file__).resolve().parents[1];B=R/'experiments/generation-repairs-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plan=read(B/'plan.json');attempts=[];latest={};last={}
 base=[json.loads(x) for x in (R/'analysis/generation-comparison-v1/comparison-measurements.jsonl').read_text().splitlines()];basekeys={(r['benchmark_id'],r['slice_id'],r['model']):r for r in base}
 for order,x in enumerate(plan['attempts']):
  t,s,m,v=[x[k] for k in ['benchmark_id','slice_id','model','revision']];p=B/'artifacts'/t/m/v/s/'result.json';assert p.exists(),('Unfinished planned repair',t,m,v,s)
  r=read(p);assert sha(R/r['submission_file'])==r['submission_sha256'];key=(t,s,m);r.update(repair_order=order,result_file=str(p.relative_to(R)),result_sha256=sha(p));last[key]=r
  if r['status']=='measured':
   audit=p.parent/'saved-output-audit.json';a=read(audit);assert a['status']=='passed';assert sha(R/r['prediction_file'])==r['prediction_sha256'];r.update(saved_output_audit_file=str(audit.relative_to(R)),saved_output_audit_sha256=sha(audit));obj=read(R/r['submission_file'])
   if obj.get('AST_equivalent'):
    source=R/obj.get('parent_submission_file',obj['original_submission_file']);old=read(source)['code'] if source.suffix=='.json' else source.read_text();assert ast.dump(ast.parse(old))==ast.dump(ast.parse(obj['code']))
    if obj['repair_type']=='AST_identical_format_only' and key in basekeys and basekeys[key]['status']=='measured':assert abs(r['score']-basekeys[key]['score'])<1e-10,(key,'format changed score')
   latest[key]=r
  attempts.append(r)
 initial=[r for r in read(R/'results/generation-extension-v1.json')['records'] if r['status']=='failed'];unresolved=[]
 for r in initial:
  key=(r['benchmark_id'],r['slice_id'],r['model'])
  if key not in latest:
   lastrow=last[key];assert lastrow['status']=='failed';reason='Not scored within the 180-second computation limit after compatibility and exact-caching repairs.' if 'exceeded 180' in lastrow.get('reason','') else 'Not scored: no valid output under the frozen task requirements after documented repair attempts.'
   unresolved.append(dict(original_key={'benchmark_id':key[0],'slice_id':key[1],'model':key[2]},status='failed',failure_phase=lastrow.get('failure_phase'),reason=lastrow.get('reason'),not_scored_reason=reason,latest_attempt_file=lastrow['result_file'],repair_attempts=sum((a['benchmark_id'],a['slice_id'],a['model'])==key for a in attempts),exclusion_is_not_zero_score=True,claim='This is an implementation/budget exclusion, not proof that the model is intrinsically inapplicable to the modality.'))
 d=dict(revision='generation-repairs-v1',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_API_calls=0,original_runtime_failures=10,recovered_original_runtime_failures=10-len(unresolved),remaining_unscored=len(unresolved),attempt_count=len(attempts),successful_repair_slice_outputs=len(latest),format_only_repaired_programs=len({(a['benchmark_id'],a['model']) for a in latest.values() if a['repair_type']=='AST_identical_format_only'}),policy='Explicit manual runtime/shape/library patches, same-objective optimizer fixes, a documented J08 bootstrap training-budget adaptation, and AST-identical formatting. No test-label access, test-score search, new model generation or relaxed time budget. Not unbiased generation evidence.',attempts=attempts,latest_successes=list(latest.values()),unresolved=unresolved,source_sha256={str(p.relative_to(R)):sha(p) for p in [B/'plan.json',B/'runner-seal.json',R/'scripts/extension_repair_evaluate.py',R/'scripts/mechanical_format_repair.py',R/'results/generation-extension-v1.json']})
 (R/'results/generation-repairs-v1.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
 lines=['# Manual repair and exclusion audit','',f"Recovered **{d['recovered_original_runtime_failures']} of 10** original older-model runtime failures. **{d['remaining_unscored']}** remain unscored under the original task requirements. No new API calls were made. Original attempts and previous macro reports are preserved.",'','Physical-line violations were separately repaired by mechanically preserving the complete Python AST. This does not establish original model brevity or compliance; original violations remain in the first-attempt panel. Formats were rerun, audited and required to retain scores where an earlier numeric comparison exists.','','| Task | Model | Revision | Outcome | Native score | Patch |','|---|---|---|---|---:|---|']
 for a in attempts:lines.append(f"| {a['benchmark_id']} | {a['model']} | {a['repair_revision']} | {a['status']} | {a.get('score','unscored')} | {a['patch_description']} |")
 lines+=['','## Exclusions','']+[f"- {u['original_key']['benchmark_id']} / {u['original_key']['model']}: {u['not_scored_reason']} {u['claim']}" for u in unresolved]
 lines+=['','## Interpretation','','These points measure manually repaired procedures. Optimizer changes preserve the stated training objective but may change numerical convergence and predictions; they are not byte-identical executions. J08 GPT-4.1 additionally caps per-tree bootstrap draws at 250000 rather than 16451616 to meet the unchanged 180-second computation limit. This manual training-budget adaptation changes fitting and cannot be attributed to the original model alone. Compatibility/shape fixes may enable an original method without improving its scientific quality. A valid low score stays low: no test-score-driven algorithm replacement was performed. The repaired panel cannot establish that an untouched model would debug itself or outperform specialists autonomously.','','[Plan and patch descriptions](plan.json), [consolidated attempts and hashes](../../results/generation-repairs-v1.json), [original API study](../generation-extension-v1/), [original four-model report](../../analysis/generation-comparison-v1/report.md).']
 (B/'README.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:d[k] for k in ['recovered_original_runtime_failures','remaining_unscored','attempt_count','successful_repair_slice_outputs']},indent=2))
if __name__=='__main__':main()
