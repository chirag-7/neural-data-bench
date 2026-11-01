"""Derive the four-model comparison without changing frozen measurements.

No model calls. Requires all 74 extension rows; failures remain missing, not zero.
Use --output-root work/path --no-website to build an isolated review copy.
"""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import argparse, csv, hashlib, json, math

ROOT=Path(__file__).resolve().parents[1]
MODELS=['gpt-4.1-2025-04-14','gpt-5-2025-08-07','gpt-5.6-sol','gpt-6.1-sol']
PAIRS=list(combinations(MODELS,2))
EXCLUDE={'B01','B03','B08','L06','M04','N05'}
NOTES={
 'M04':'Known-equation numerical estimators nearly coincide. Tiny ordering is not demonstrated capability progress.',
 'L06':'C2ST approaches chance 0.5. Finite classifier differences near chance need uncertainty analysis.',
 'N05':'Correctness ceiling 1 on 61 fields of one NWB file; other schemas are untested.',
 'C06':'Pearson correlation does not measure count calibration; inspect count error separately.',
 'B01':'Primary GT-unit accuracy and post-hoc all-output eventF1 can reverse rankings.',
 'E06':'Native equal-slice means can hide main/taxis reversals.',
 'B08':'The final comparison permits heapq under the documented harness repair; original whitelist failures remain archived.'}

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(r):return r.get('status')=='measured' and isinstance(r.get('score'),(int,float)) and not isinstance(r.get('score'),bool) and math.isfinite(r['score'])
def mean(v):return sum(v)/len(v) if v else None
def outcome(d):return 'better' if d>1e-9 else 'worse' if d< -1e-9 else 'numerical_tie'
def save(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def csvsave(p,rows):
 if not rows:return
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def normalize(row,template):
 r=dict(row)
 for k in ['metric','direction','family_code','reference_type','baseline_name']:
  if r.get(k) is None:r[k]=template.get(k)
 if not valid(r):r['score']=None
 r['strict_format_compliant']=bool(r.get('strict_format_compliant',r.get('line_limit_compliant',False)))
 return r

def trajectory(rows,tid,reference):
 selected=[r for r in rows if r['model'] in MODELS]
 sids=sorted({r['slice_id'] for r in selected})
 direction=selected[0]['direction'];metric=selected[0]['metric'];orient=1 if direction=='higher' else -1
 assert all(r['direction']==direction and r['metric']==metric for r in selected),(tid,'incompatible task metrics')
 scores={};fmt={}
 for m in MODELS:
  a=[r for r in selected if r['model']==m]
  assert len(a)==len(sids) and {r['slice_id'] for r in a}==set(sids),(tid,m,'missing/duplicate rows')
  scores[m]=mean([r['score'] for r in a]) if all(valid(r) for r in a) else None
  fmt[m]=all(r['strict_format_compliant'] for r in a)
 pairs=[]
 for a,b in PAIRS:
  delta=scores[b]-scores[a] if scores[a] is not None and scores[b] is not None else None
  pairs.append(dict(older=a,newer=b,raw_native_delta=delta,direction_adjusted_delta=orient*delta if delta is not None else None,outcome=outcome(orient*delta) if delta is not None else 'incomplete',strict_pair_compliant=fmt[a] and fmt[b]))
 complete=all(v is not None for v in scores.values())
 steps=[outcome((scores[b]-scores[a])*orient) for a,b in zip(MODELS,MODELS[1:])] if complete else []
 label='incomplete' if not complete else 'all steps improve' if all(x=='better' for x in steps) else 'all steps regress' if all(x=='worse' for x in steps) else 'numerically unchanged' if all(x=='numerical_tie' for x in steps) else 'nonmonotonic or partly tied'
 versus={m:{'outcome':outcome((s-reference['score'])*orient) if s is not None else 'incomplete','direction_adjusted_delta':(s-reference['score'])*orient if s is not None else None} for m,s in scores.items()}
 chart=[{k:r.get(k) for k in ['benchmark_id','slice_id','model','status','score','metric','direction','reference_type','line_limit_compliant','strict_format_compliant','baseline_name','description','repair_applied','repair_type','repair_revision','code_repaired','not_scored_reason','reason']} for r in rows]
 return dict(benchmark_id=tid,n_slices=len(sids),slice_ids=sids,metric=metric,direction=direction,scores=scores,format_compliant=fmt,pairs=pairs,trajectory=label,adjacent_step_outcomes=steps,ordinal_direction_adjusted_slope=(scores[MODELS[-1]]-scores[MODELS[0]])*orient/3 if complete else None,slope_units=metric+' per ordinal version label (not time/compute)',flat_interpretation='Numerical tie is not practical or statistical equivalence.',interpretation=NOTES.get(tid,'One generated program per model; source and generation replication remain limited.'),chart_rows=chart,primary_reference=reference,versus_primary_reference=versus,best_general_model=max((m for m in MODELS if scores[m] is not None),key=lambda m:scores[m]*orient,default=None),observed_general_winners_vs_tested_reference=[m for m in MODELS if versus[m]['outcome']=='better'])

def summaries(tasks,track):
 result=[]
 for scope in ['all_measured_tasks','observed_data_tasks']:
  selected=[t for t in tasks if scope=='all_measured_tasks' or t['observed_macro_eligible']]
  for a,b in PAIRS:
   counts=Counter(next(p['outcome'] for p in t[track]['pairs'] if (p['older'],p['newer'])==(a,b)) for t in selected)
   result.append(dict(scope=scope,n_tasks=len(selected),older=a,newer=b,counts={k:counts[k] for k in ['better','worse','numerical_tie','incomplete']},estimand='Sign of native equal-slice task mean; no missing-score imputation.'))
 families=[]
 for fam in sorted({t['family_code'] for t in tasks}):
  selected=[t for t in tasks if t['family_code']==fam];comparisons=[]
  for a,b in PAIRS:
   counts=Counter(next(p['outcome'] for p in t[track]['pairs'] if (p['older'],p['newer'])==(a,b)) for t in selected)
   comparisons.append(dict(older=a,newer=b,counts={k:counts[k] for k in ['better','worse','numerical_tie','incomplete']},signed_task_mean=mean([1 if x=='better' else -1 if x=='worse' else 0 for x in [next(p['outcome'] for p in t[track]['pairs'] if (p['older'],p['newer'])==(a,b)) for t in selected] if x!='incomplete'])))
  families.append(dict(family_code=fam,n_tasks=len(selected),comparisons=comparisons))
 for row in result:
  if row['scope']=='all_measured_tasks':
   fs=[next(p['signed_task_mean'] for p in f['comparisons'] if (p['older'],p['newer'])==(row['older'],row['newer'])) for f in families]
   row['family_balanced_signed_direction']=mean([v for v in fs if v is not None]);row['families_with_valid_pairs']=sum(v is not None for v in fs)
 return result,families

def strict_summaries(tasks):
 rows=[]
 for older,newer in PAIRS:
  pairs=[next(p for p in t['repair_assisted']['pairs'] if (p['older'],p['newer'])==(older,newer)) for t in tasks]
  eligible=[p for p in pairs if p['outcome']!='incomplete' and p['strict_pair_compliant']]
  counts=Counter(p['outcome'] for p in eligible)
  rows.append(dict(older=older,newer=newer,eligible_task_pairs=len(eligible),incomplete=sum(p['outcome']=='incomplete' for p in pairs),format_ineligible=sum(p['outcome']!='incomplete' and not p['strict_pair_compliant'] for p in pairs),counts={k:counts[k] for k in ['better','worse','numerical_tie']}))
 return rows

def report(data):
 lines=['# Four-model generation comparison','',data['summary_text'],'',data['provenance_note'],'','## Descriptive pairwise results','', '| Earlier | Later | Better | Worse | Numerical tie | Incomplete | Family-balanced direction |','|---|---|---:|---:|---:|---:|---:|']
 for s in data['task_direction_summaries']:
  if s['scope']=='all_measured_tasks':
   c=s['counts'];v=s['family_balanced_signed_direction'];lines.append(f"| {s['older']} | {s['newer']} | {c['better']} | {c['worse']} | {c['numerical_tie']} | {c['incomplete']} | {v:.4f} |" if v is not None else f"| {s['older']} | {s['newer']} | {c['better']} | {c['worse']} | {c['numerical_tie']} | {c['incomplete']} | unavailable |")
 lines+=['','## Strict-format sensitivity','', 'Both model procedures must meet their original line limits and have numeric scores on every slice. Format-ineligible numeric pairs remain visible in the main table; this sensitivity excludes them.', '', '| Earlier | Later | Eligible tasks | Better | Worse | Tie | Incomplete | Format-ineligible |','|---|---|---:|---:|---:|---:|---:|---:|']
 for row in data['strict_format_task_direction_summaries']:
  c=row['counts'];lines.append(f"| {row['older']} | {row['newer']} | {row['eligible_task_pairs']} | {c['better']} | {c['worse']} | {c['numerical_tie']} | {row['incomplete']} | {row['format_ineligible']} |")
 lines+=['','Positive family-balanced direction means more improvements than regressions after equalizing category weights; it is descriptive, with incomplete task-pairs excluded and coverage reported. It does not measure effect size or probability of superiority.','','## Findings','']+['- '+x for x in data['findings']]
 lines+=['','## Practical interpretation','','A win over our fixed tested reference is not a win over the best current specialist. The thirty specialist reviews retain their source links and input/split limitations. No blanket replacement recommendation follows. Inspect each task’s native score, line-limit compliance and current-specialist review.','','## Files and audit trail','','- [Methods](methods.md)','- [Native task scores](task-scores.csv)','- [All slice records](comparison-measurements.jsonl)','- [Six pairwise task comparisons](task-pairs.csv)','- [First-attempt sensitivity](first-attempt-pairs.csv)','- [Machine-readable trajectories](generation-comparison.json)','- [Frozen historical three-model analysis](../practical-review-2026-11-01/report.md)','','Original GPT-6 Sol data remain in the historical ledger and report; GPT-6 Sol is excluded from the current four-model display.']
 return '\n'.join(lines)+'\n'

METHODS='''# Methods: four-model extension

The current display includes pinned GPT-4.1-2025-04-14 and GPT-5-2025-08-07 API snapshots plus the existing GPT-5.6Sol and GPT-6.1Sol procedures. GPT-6 Sol is retained in historical artifacts, not the current comparison.

## Estimand and exclusions

Thirty tasks span fourteen categories and 37 evaluation slices per model. Each task uses its existing primary metric and direction. A model’s task score is the equal-slice native mean only if every slice is valid. Failed/missing scores are incomplete; zero is never substituted. Six ordered model pairs are compared by the sign of their task-native mean difference, with numerical tolerance 1e-9. Metric magnitudes are never pooled across tasks. Family-balanced signed direction first averages signs within family, excluding incomplete pairs, then averages families with a valid pair; coverage is retained. This is not a significance test.

The observed-data sensitivity excludes B01, B03, L06, M04 (fully synthetic), B08 (protocol ambiguity) and N05 (single-file correctness). The default final usability view applies documented repairs to existing selected Sol procedures and separately versioned API-generation repairs, while the first-attempt sensitivity retains original failures. Original frozen measurements, summary, catalog and historical analyses are not changed. Missing C05 archived reference predictions remain unresolved and are not padded or imputed.

## Interpretation limits

Model order is an ordinal display convention, not training compute, size, release-time spacing or a scaling-law independent variable. End-point slopes are descriptive only. One new program per task/model and existing selectively repaired older procedures do not support unbiased population claims about model generations. GPT-4.1/GPT-5 are direct API calls whereas the Sol runs used the Codex environment. Wrapper instructions, exposed tools, reasoning budgets and execution histories can confound model differences; inspect the extension provider metadata and execution seal. No model-selection oracle should be treated as deployable performance.

Native ties are numerical, not demonstrated practical equivalence. A higher correlation can coexist with worse calibration; near-chance C2ST and nearly identical numerical estimators require special care. Reusing the frozen tested references makes extension comparisons consistent, but does not establish current specialist state of the art. Review links identify candidates, not unexecuted best scores. No broad replacement recommendation or future crossover forecast is justified.

## Provenance

Input SHA256 hashes, extension metadata, retained code and scored-output hashes are recorded in generation-comparison.json and the extension record. Runtime/library/shape fixes, optimizer changes for the same training objective, and AST-identical formatting are recorded separately. No test-label or test-score-based model search is performed. Scores of manually repaired procedures cannot establish what the original model would do autonomously. No new measured score is invented. Historical GPT-6 results remain accessible through the prior report. Regenerate with python3 scripts/build_generation_comparison_v2.py after all 74 extension rows exist; run python3 scripts/check_generation_comparison_v2.py for structural checks.
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('--extension',type=Path,default=ROOT/'results/generation-extension-v1.json');p.add_argument('--output-root',type=Path,default=ROOT/'analysis/generation-comparison-v2');p.add_argument('--no-website',action='store_true');args=p.parse_args()
 frozen_paths=[ROOT/x for x in ['results/measurements.jsonl','analysis/summary.json','registry/catalog.json']];hashes={str(x.relative_to(ROOT)):sha(x) for x in frozen_paths}
 original=[json.loads(x) for x in frozen_paths[0].read_text().splitlines()];base=read(frozen_paths[1]);catalog=read(frozen_paths[2]);entries={e['id']:e for e in catalog['entries']};family_names={f['code']:f['name'] for f in catalog['families']};extension=read(args.extension);new=extension['records'];repairs=read(ROOT/'results/repairs-v1.json');extra=read(ROOT/'results/generation-repairs-v1.json');repairs={k:repairs.get(k,[])+extra.get(k,[]) for k in ['attempts','latest_successes','unresolved']};old_models=MODELS[2:]
 expected={(r['benchmark_id'],r['slice_id']) for r in original if r['model']==old_models[0]}
 assert len(expected)==37 and len(new)==74,'Need37slices/model,74 extension rows including failures'
 assert {r['model'] for r in new}==set(MODELS[:2]),'Wrong extension models'
 for m in MODELS[:2]:
  a=[r for r in new if r['model']==m];assert len(a)==37 and {(r['benchmark_id'],r['slice_id']) for r in a}==expected,(m,'missing/duplicate slice')
 templates={(r['benchmark_id'],r['slice_id']):r for r in original if valid(r)}
 assert set(templates)==expected,'Every slice needs measured metric metadata'
 first=[normalize(r,templates.get((r['benchmark_id'],r['slice_id']),{})) for r in original if r['model']!='gpt-6-sol']+[normalize(r,templates[(r['benchmark_id'],r['slice_id'])]) for r in new]
 effective=[dict(r) for r in first];applied=[]
 for repair in repairs.get('latest_successes',[]):
  key=repair.get('original_key',{})
  if key.get('model')=='gpt-6-sol' or not valid(repair):continue
  matches=[r for r in effective if (r['benchmark_id'],r['slice_id'],r['model'])==(key.get('benchmark_id'),key.get('slice_id'),key.get('model'))]
  assert len(matches)==1,(key,'missing repair original')
  matches[0].update({k:v for k,v in repair.items() if k not in ['original_key','model','benchmark_id','slice_id']});matches[0]['repair_applied']=True
  if 'line_limit_compliant' in repair:matches[0]['strict_format_compliant']=repair['line_limit_compliant']
  applied.append(repair)
 # Explicit final exclusions update display reasons, never substitute a zero.
 for unresolved in extra.get('unresolved',[]):
  key=unresolved['original_key']
  for row in effective:
   if (row['benchmark_id'],row['slice_id'],row['model'])==(key['benchmark_id'],key['slice_id'],key['model']):
    row.update(status='failed',score=None,not_scored_reason=unresolved['not_scored_reason'],latest_repair_attempt_file=unresolved['latest_attempt_file'])
 tasks=[]
 for tid in sorted(base['measured_task_ids']):
  es=[r for r in effective if r['benchmark_id']==tid];fs=[r for r in first if r['benchmark_id']==tid];refs=[r for r in base['reference_envelopes'] if r['benchmark_id']==tid]
  reference=dict(names=sorted({r['model'] for r in refs}),score=mean([r['score'] for r in refs]),reference_class=refs[0]['reference_class'],current_sota_verified=False,evidence='; '.join(dict.fromkeys(r['evidence'] for r in refs)))
  tr=trajectory(es,tid,reference);tr['first_attempt']=trajectory(fs,tid,reference);tr['repair_assisted']={k:v for k,v in tr.items() if k!='first_attempt'}
  review=ROOT/'literature/specialist-review-2026-11-01'/f'{tid}.json';assert review.exists(),tid
  e=entries[tid];tr.update(task=e['task'],family_code=e['family_code'],family_name=family_names[e['family_code']],executed_slice=e.get('executed_slice'),source_limitations=e.get('limitations',''),observed_macro_eligible=tid not in EXCLUDE,specialist_review=read(review),specialist_evidence_file=str(review.relative_to(ROOT)),repair_info={'latest_successes':[r for r in applied if r['original_key']['benchmark_id']==tid],'unresolved':[r for r in repairs.get('unresolved',[]) if r.get('original_key',{}).get('benchmark_id',r.get('benchmark_id'))==tid]},switch_decision='evaluate_as_an_alternative' if tr['observed_general_winners_vs_tested_reference'] else 'retain_reference_and_investigate',switch_now_evidence='No blanket replacement claim: matched current-best specialist, independent sources, practical margins and operational checks are incomplete.')
  tasks.append(tr)
 stats,families=summaries(tasks,'repair_assisted');firststats,firstfam=summaries(tasks,'first_attempt')
 for f in families+firstfam:f['family_name']=family_names[f['family_code']]
 findings=[]
 for s in stats:
  if s['scope']=='all_measured_tasks':
   c=s['counts'];findings.append(f"{s['newer']} versus {s['older']}: {c['better']} task improvements, {c['worse']} regressions, {c['numerical_tie']} numerical ties and {c['incomplete']} incomplete comparisons in the final usability track.")
 mono=sum(t['trajectory']=='all steps improve' for t in tasks);findings.append(f'{mono} of 30 tasks improve at every adjacent model step; failures prevent trajectory classification where incomplete. This is descriptive and does not establish a scaling law.')
 findings+=['Quantitative: counts describe these fixed tasks, not a random sample of neuroscience problems; task and family weighting answer different questions.','Qualitative: specialist candidates vary by modality and input requirements. Wins over a conventional local reference are insufficient grounds to replace the current best specialist.','Quantitative + qualitative: investigate reversals and near-ceiling tasks individually; native score differences, calibration and runtime can change practical conclusions.','No extrapolation of future crossover dates, compute scaling or universal newer-model superiority is supported.']
 data=dict(revision='generation-comparison-v2',models=MODELS,tasks=tasks,coverage={'measured_tasks':30,'measured_families':14,'evaluation_slices_per_model':37,'model_attempts':148,'specialist_reviews_present':30},task_direction_summaries=stats,repair_assisted_task_direction_summaries=stats,strict_format_task_direction_summaries=strict_summaries(tasks),family_summaries=families,repair_family_summaries=families,first_attempt_task_direction_summaries=firststats,first_attempt_family_summaries=firstfam,findings=findings,summary_text='Four-model comparison across 30 tasks and 14 categories. Native score trajectories and six model pairs are descriptive; incomplete attempts remain visible.',provenance_note='Final usability scores include explicitly versioned manual runtime, optimizer and format repairs across model generations. Original submissions and first-attempt outcomes remain unchanged. GPT-4.1/GPT-5 use the API; Sol runs use Codex. These are repaired analysis procedures, not an unbiased generation ranking.',input_sha256={**hashes,str(args.extension.relative_to(ROOT)) if args.extension.is_relative_to(ROOT) else str(args.extension):sha(args.extension),'results/repairs-v1.json':sha(ROOT/'results/repairs-v1.json'),'results/generation-repairs-v1.json':sha(ROOT/'results/generation-repairs-v1.json')},provider_metadata={k:v for k,v in extension.items() if k!='records'},source_refs=['results/generation-extension-v1.json','results/measurements.jsonl','results/repairs-v1.json','results/generation-repairs-v1.json','literature/specialist-review-2026-11-01'],ordinal_slope_warning='Ordinal labels are not time or compute. Slopes are descriptive, not a scaling law.',flatness_warning='Numerical ties do not establish practical or statistical equivalence.',switching_warning='Current-best specialist performance remains unverified on custom slices; no blanket switch recommendation.')
 summary={k:base[k] for k in ['version','date','mapped_entries','historical_mapped_entries','archived_candidates','mapped_families','measured_tasks','measured_task_ids','measured_families','reference_envelopes','fully_synthetic_task_ids','semisynthetic_repair_task_ids'] if k in base};summary.update(models=MODELS,model_attempts=148,record_count=len(effective),model_summaries=[dict(model=m,attempted=sum(r['model']==m for r in effective),valid=sum(r['model']==m and valid(r) for r in effective),strict_format_valid=sum(r['model']==m and valid(r) and r.get('strict_format_compliant',False) for r in effective),failed=sum(r['model']==m and not valid(r) for r in effective)) for m in MODELS],comparison_revision='generation-comparison-v2',provenance_note=data['provenance_note'])
 out=args.output_root;out.mkdir(parents=True,exist_ok=True)
 save(out/'generation-comparison.json',data);save(out/'comparison-summary.json',summary)
 (out/'comparison-measurements.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in effective));(out/'report.md').write_text(report(data));(out/'methods.md').write_text(METHODS)
 csvsave(out/'task-scores.csv',[dict(benchmark_id=t['benchmark_id'],family=t['family_code'],task=t['task'],metric=t['metric'],direction=t['direction'],**t['scores'],primary_reference=t['primary_reference']['score'],trajectory=t['trajectory']) for t in tasks])
 for track,name in [('repair_assisted','task-pairs.csv'),('first_attempt','first-attempt-pairs.csv')]:csvsave(out/name,[dict(benchmark_id=t['benchmark_id'],family=t['family_code'],**p) for t in tasks for p in t[track]['pairs']])
 if not args.no_website:
  for name,obj in [('generation-comparison.json',data),('comparison-summary.json',summary)]:save(ROOT/'website/data'/name,obj)
  (ROOT/'website/data/comparison-measurements.jsonl').write_bytes((out/'comparison-measurements.jsonl').read_bytes())
 assert all(sha(ROOT/p)==h for p,h in hashes.items()),'Frozen input changed'
 print(json.dumps({'tasks':len(tasks),'models':MODELS,'model_summaries':summary['model_summaries'],'output':str(out)},indent=2))
if __name__=='__main__':main()
