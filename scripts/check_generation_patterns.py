"""Verify macro counts against native directions and retained source scores."""
from pathlib import Path
import hashlib,json,math,csv
R=Path(__file__).resolve().parents[1];P=R/'analysis/generation-patterns-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((P/'patterns.json').read_text());src=json.loads((R/'analysis/generation-comparison-v2/generation-comparison.json').read_text());assert len(d['tasks'])==30 and len(d['family_summaries'])==14
 assert sum(d['trajectory_counts'].values())==30;assert sum(d['step_pattern_counts'].values())==d['n_complete_trajectories'];assert sum(d['metric_direction_counts'].values())==30
 for p,h in d['input_sha256'].items():assert sha(R/p)==h,p
 lookup={t['benchmark_id']:t for t in src['tasks']};endpoint={'better':0,'worse':0,'numerical_tie':0,'incomplete':0}
 for t in d['tasks']:
  source=lookup[t['benchmark_id']];assert t['scores']==source['scores'];values=list(t['scores'].values());assert t['direction']==source['direction'];a=values[0];b=values[-1]
  if a is None or b is None:endpoint['incomplete']+=1
  else:
   delta=(b-a)*(1 if source['direction']=='higher' else -1);endpoint['better' if delta>1e-9 else 'worse' if delta< -1e-9 else 'numerical_tie']+=1
  if t['trajectory_class']=='strictly_improving':assert all((b-a)*(1 if source['direction']=='higher' else -1)>1e-9 for a,b in zip(values,values[1:]))
  assert t['randomness_assessment']=='not_estimated' and t['equivalence_assessment']=='not_established'
 assert all(endpoint[k]==d['endpoint']['counts'][k] for k in endpoint)
 assert endpoint==dict(better=27,worse=2,numerical_tie=0,incomplete=1),'Final repaired snapshot changed: investigate, do not update blindly'
 assert d['trajectory_counts']['strictly_improving']==9 and d['trajectory_counts']['mixed_reversals']==19 and d['trajectory_counts']['nondecreasing_with_ties']==1
 assert sum(f['n_tasks'] for f in d['family_summaries'])==30
 assert d['diminishing_gains']['strictly_diminishing']==5 and d['diminishing_gains']['last_smaller_than_first']==8
 assert d['metric_direction_counts']=={'higher':18,'lower':12}
 assert (R/'website/data/generation-patterns.json').read_bytes()==(P/'patterns.json').read_bytes()
 repairs=json.loads((R/'results/generation-repairs-v1.json').read_text());assert repairs['recovered_original_runtime_failures']==9 and repairs['remaining_unscored']==1
 for r in repairs['latest_successes']:
  assert sha(R/r['result_file'])==r['result_sha256'];assert sha(R/r['prediction_file'])==r['prediction_sha256'];assert sha(R/r['saved_output_audit_file'])==r['saved_output_audit_sha256'];assert r['line_limit_compliant']
 print('Macro checks passed:27/2/0/1 endpoint;9 monotonic,19 reversals,1 improves with ties,1 excluded;30 metric directions;20 audited repair outputs;all input hashes.')
if __name__=='__main__':main()
