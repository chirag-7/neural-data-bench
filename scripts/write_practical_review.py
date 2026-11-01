"""Reproducible navigation/report layer; no model calls, fitting or score edits."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json
R=Path(__file__).resolve().parents[1];D=R/'analysis/practical-review-2026-11-01'
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvsave(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 x=read(D/'trajectories.json');tasks=x['tasks'];sources=[];matrix=[];fingerprints=[]
 for t in tasks:
  v=t['specialist_review'];path=R/t['specialist_evidence_file'];protocol=v.get('local_protocol')
  if isinstance(protocol,dict):protocol=protocol.get('path',protocol.get('file'))
  if not protocol:protocol='experiments/'+t['benchmark_id']+'/protocol.md'
  assert (R/protocol).exists(),(t['benchmark_id'],protocol)
  fingerprints.append(dict(benchmark_id=t['benchmark_id'],review_file=str(path.relative_to(R)),review_sha256=digest(path),protocol_file=protocol,protocol_sha256=digest(R/protocol)))
  for s in v['sources']:sources.append(dict(benchmark_id=t['benchmark_id'],url=s['url'],title=s.get('title',''),publication_date=s.get('publication_date'),accessed_on=s.get('accessed_on','2026-11-01'),finding=s.get('finding','')))
  matrix.append(dict(benchmark_id=t['benchmark_id'],family=t['family_code'],task=t['task'],current_best_claim=v['current_best_claim'],candidate_count=len(v['candidates']),candidate_names='; '.join(c['name'] for c in v['candidates']),executed_primary_reference='; '.join(t['primary_reference']['names']),reference_class=t['primary_reference']['reference_class'],recommended_next_comparator=v['recommended_next_comparator'],switching_assessment=v['switching_assessment'],review_file=t['specialist_evidence_file']))
 urls=sorted({s['url'] for s in sources})
 reference_counts=[]
 for track in ['original_first_attempt','repair_assisted']:
  for cls in sorted({t['primary_reference']['reference_class'] for t in tasks}):
   group=[t for t in tasks if t['primary_reference']['reference_class']==cls]
   values=[t.get('repair_assisted',t) if track=='repair_assisted' else t for t in group]
   reference_counts.append(dict(track=track,reference_class=cls,n_tasks=len(group),tasks_with_any_general_point_win=sum(bool(v['observed_general_winners_vs_tested_reference']) for v in values),winning_task_ids=','.join(t['benchmark_id'] for t,v in zip(group,values) if v['observed_general_winners_vs_tested_reference']),selection='Post-hoc any-of-three point winner; includes numeric format deviations and synthetic tasks; not prospective selection, current global SOTA or replacement evidence.'))
 csvsave(D/'reference-point-wins.csv',reference_counts)
 coverage=dict(reviewed_tasks=len(tasks),families=len({t['family_code'] for t in tasks}),candidate_entries=sum(len(t['specialist_review']['candidates']) for t in tasks),unique_candidate_name_strings=len({c['name'] for t in tasks for c in t['specialist_review']['candidates']}),source_task_associations=len(sources),unique_source_urls=len(urls),matched_current_global_winners=0,claims=dict(Counter(t['specialist_review']['current_best_claim'] for t in tasks)),review_scope='All 30 measured custom tasks; not all 92 active entries or an exhaustive literature census. Candidates/source URLs are not distinct fully reviewed papers.',reviewed_on='2026-11-01')
 save(D/'specialist-coverage.json',coverage);save(D/'specialist-source-ledger.json',sources);save(D/'review-fingerprints.json',fingerprints);csvsave(D/'specialist-matrix.csv',matrix)
 current=read(R/'registry/current-best.json')
 for entry in current:
  t=next((t for t in tasks if t['benchmark_id']==entry['benchmark_id']),None)
  if not t:continue
  entry.update(checked_on='2026-11-01',status='not verified',reason='Fresh primary-source review completed; no current global winner verified on this exact custom input/split/metric contract. Named candidates are not new measured scores.',review_file=t['specialist_evidence_file'],review_status=t['specialist_review']['current_best_claim'],candidate_names=[c['name'] for c in t['specialist_review']['candidates']],source_urls=sorted({s['url'] for s in t['specialist_review']['sources']}))
 save(R/'registry/current-best.json',current)
 def comparison_table(key):
  rows=['| Scope | Newer vs older | Better | Worse | Numerical tie | Incomplete |','|---|---|---:|---:|---:|---:|']
  for p in x[key]:
   c=p['counts'];rows.append(f"| {p['scope']} | {p['newer']} vs {p['older']} | {c.get('better',0)} | {c.get('worse',0)} | {c.get('numerical_tie',0)} | {c.get('incomplete',0)} |")
  return '\n'.join(rows)
 def fmt(v):return 'failed/incomplete' if v is None else f'{v:.8g}'
 native=['| ID | Metric (direction) | 5.6 | 6 | 6.1 | Version trajectory |','|---|---|---:|---:|---:|---|']
 for t in tasks:
  native.append(f"| [{t['benchmark_id']}](../../{t['specialist_evidence_file']}) | {t['metric']} ({t['direction']}) | {' | '.join(fmt(t['scores'][m]) for m in x['models'])} | {t['trajectory']} |")
 specialists=['| Task | Tested reference | General programs above tested reference | Next specialist comparison |','|---|---|---|---|']
 for t in tasks:
  v=t['specialist_review'];candidates='; '.join(c['name'] for c in v['candidates'][:3]);wins=', '.join(t['observed_general_winners_vs_tested_reference']) or 'none'
  specialists.append(f"| [{t['benchmark_id']}](../../{t['specialist_evidence_file']}) | {'; '.join(t['primary_reference']['names'])} ({t['primary_reference']['reference_class']}) | {wins} | {candidates.replace('|','/')} |")
 report='''# Version progress, repairs and practical model choice

Analysis revision 1 November 2026; original scientific snapshot 0.11. This is an exploratory study of **models generating analysis programs**, not direct neural-signal understanding. All 30 measured tasks / 14 families now have a fresh primary-source specialist review. No new model generations were made for this revision. Numerical recovery, format compliance, current-specialist evidence and production suitability remain separate questions.

## Quantitative findings: progress is uneven

GPT-6 is mixed relative to GPT-5.6. GPT-6.1 has more positive task-native point changes than either older version, but is worse on a substantial minority. Neither “all benchmarks improve” nor “everything is flat” describes the data. Aggregate cancellation can hide large opposing changes; a tie in win counts is not task-level equivalence.

The original first-attempt panel, including over-limit programs as numeric outcomes:

'''+comparison_table('task_direction_summaries')+'''

Observed-data scope excludes B01/B03 synthetic fixtures, B08 ambiguous whitelist, L06 synthetic posterior diagnostic, M04 synthetic recovery and N05 deterministic correctness. It contains 24 tasks / 13 families. Each table cell counts the direction of one task's equal-slice native mean. This differs from the previous family-balanced mean of slice directions. Failures remain incomplete here, rather than being replaced by zero or silently removed. Tasks and sources are correlated; do not treat these counts as 30 independent experimental replications.

The original family-balanced analysis remains unchanged: net signed direction −0.0654 for 6 vs 5.6, +0.2154 for 6.1 vs 5.6 and +0.2179 for 6.1 vs 6. Conditional family sign-flip diagnostics give p=0.8086, 0.4155 and 0.4463; Holm adjustment gives 1.0 for all three. The diagnostics assume independent symmetric family contrasts, not random sampling of neuroscience tasks. These data do **not** establish a general improvement law; they also do not establish equivalence or absence of progress. [Full assumptions and strict-compliance sensitivities](../macro-patterns/methods.md).

### Where improvement is most consistent, and where it reverses

- **Cell and molecular tasks K01/K04/K05/K06:** all four have higher GPT-6.1 point performance than both older versions. This is a post-hoc category signal across four different endpoints, not a validated universal rule. SingleR still leads all three on K04. K05 is supervised fraction regression rather than standard unsupervised/reference-based deconvolution. K06 is waveform-only; a full pretrained cell-typing model may use additional information or overlapping source units.
- **Behavior:** A09 and A15 improve across both version steps; A14 pose imputation peaks at GPT-6. Acoustic interval detection is a narrow same-bird test, not general behavior recognition.
- **Electrical tasks:** B03 drift error increases from 3.604 to 4.418 to 5.275 µm on its synthetic fixture. B07 compression favors GPT-6. After the B08 harness correction, GPT-5.6 is best. These do not support monotonic electrical-task progress.
- **EEG:** H01 motor imagery peaks at GPT-6; H02 P300 favors 6.1; H08 staging declines across versions; H16 artifact repair favors 6.1. Individual tasks, not an EEG-wide recommendation, are supported.
- **Population/sensory/decoding:** E01, F04 and G01 favor 6.1 but dip at 6; E06 improves in its equal-slice mean, while its unseen taxis slice worsens from 6 to 6.1. Aggregate improvement does not mean robustness to each distribution shift.
- **Near-flat candidates:** M04 compares nearly identical known-equation numerical estimators. M01 log loss is 0.436515 / 0.437584 / 0.436634; such small differences need a prospective meaningful margin and independent repeats. N05 reaches the 1.0 correctness ceiling after repair. L06's C2ST is near chance; tiny ordering there does not establish posterior superiority.

### Slopes and flatness

The website shows all three native scores, both stepwise changes, and the direction-adjusted endpoint slope `(score_6.1 − score_5.6)/2` after orienting higher-is-better. Version labels use ordinal positions 0/1/2. Units are **native metric per ordinal version step**. These are descriptive slopes, not slopes per month, compute or dollar, and cannot forecast when specialists will be surpassed. Three versions, mostly one generated program each, are insufficient to fit a defensible scaling law. Different metrics' slopes are never pooled. Numerical equality uses 1e−9 only for display; practical or statistical equivalence has not been demonstrated.

## Quantitative + qualitative findings: when to try a general program

**No task currently supports an unconditional switch from the best available specialist.** This does not mean the general programs are useless. It means current-best matched comparison, source/generation replication and operational constraints have not all been established. Trial decisions can be narrower than a scientific claim of superiority.

At least one of the three general programs beats the declared primary reference in **23/30 original tasks**, or **24/30 with repairs**. Split by reference strength, this is **8/14 named historical/local/pretrained specialist tasks** originally, **9/14 with repairs**, and **14/14 ordinary conventional/domain-reference tasks** in both views. The remaining two tasks use an objective-mismatched synthetic mathematical reference and deterministic correctness. These are post-hoc any-of-three point wins, include numeric format deviations and B03's synthetic fixture, and are not the performance of a prospectively selected general model. The strong difference by reference class shows why “general beats specialist” cannot be inferred from the overall win fraction. [Exact denominators, classes and task IDs](reference-point-wins.csv).

1. **B07 offline compression is the strongest narrow engineering candidate.** GPT-6 uses 6.901698 bits/sample against pinned WavPack 7.690052: about 10.25% smaller on the 16 tested byte-exact chunks. All saved payloads were independently decoded. Encoding takes about 9.02 s vs 4.61 s in the recorded run, so smaller files cost about 1.96× the encode time. Only ~0.137 s from each recording is tested, making header/chunk effects important. Trial the fixed generated codec on held-out long recordings with storage/throughput/portability checks; retain WavPack until that succeeds. [Protocol and evidence](../../experiments/B07/protocol.md).
2. **B08 event compression:** after the harness-only fix, unchanged GPT-5.6/6 programs use 7.585598/7.693067 bits/event vs Spikepack 8.142312 and 6.1 8.636802. Every retained payload independently decodes (35/35). This is an input-matched pilot win over a named specialist on seven recordings from one monkey, not proof of a universally better spike format. Container metadata, longer recordings, exact unit/order preservation and time-error budget still matter.
3. **H02 P300 is a candidate for dataset-specific evaluation.** The separate three-generation follow-up gives mean AUC 0.784685 for 6.1 versus train-only-selected xDAWN 0.778541; all three 6.1 attempts exceed it, with minimum advantage only 0.000754. This is one public dataset, not independent confirmation across labs. Stronger ERP classifiers are now documented. [Follow-up](../../experiments/H02/replication-v1/results.md).
4. **C06 calcium inference demonstrates the importance of the target.** General programs beat the local OASIS reference on correlation and count error here, but their own relative count errors remain large. A high correlation does not justify calibrated spike-count use. Retrained, source-excluded CASCADE/ENS2/SpikeSSL is a stronger next comparison.
5. **A09 behavior, H08 sleep staging and I10 MRI quality:** wins are against archived or restricted-input specialist references. Reproduce modern methods under matched inputs and source-overlap controls before replacing tools. YASA restricted to this EEG channel is not a test against multimodal sleep staging.
6. **Keep specialist-first workflows for K04 cortical transfer, J08 puncta segmentation, C05 archived spike inference and L06 posterior inference.** Tested strong references lead all general programs on their primary endpoints; repaired J08 remains well behind archived StarDist. B01 also needs all-output spike accounting: nearly matching per-GT-unit accuracy hides many excess spikes.

C05 uses a test-selected per-preparation envelope among inspected 2017 archives, potentially choosing different methods for different preparations; it is not a single deployable estimator or a prospectively selected specialist. Other reference-class details and budget mismatches remain in the source-linked evidence.

The all-task matrix below identifies exactly which reference was beaten. An ordinary ridge/GLM/interpolation reference is not a certified strongest specialist. Source-specific recommendations and candidate information/compute mismatches are in every linked review.

'''+ '\n'.join(specialists)+'''

## Qualitative findings: the current-specialist search changes the next experiment

The review records queries, primary links, dates where verified, endpoint compatibility, negative findings and next comparators for every measured task. It identifies current DREDge presets (older SpikeInterface presets remain in the original pilot), modern latent population models, contemporary calcium/event methods, sleep/EEG foundations and new cell-typing contenders. Examples: [DREDge official code](https://github.com/evarol/dredge), [NLB official challenge and method links](https://neurallatents.github.io/challenge.html), [AIND compression benchmark](https://github.com/AllenNeuralDynamics/ephys-compression). The NLB challenge is closed; its published leaderboard snapshot and now-public test data are not a new blind evaluation.

The search does not yield a single defensible current global winner on any of our 30 custom contracts. Some endpoints have no official leaderboard; others alter inputs, split, metric, runtime or allowed pretraining. A new paper does not automatically outperform an older method. Modern pretrained models with extra channels, video, ISIs, gene identities or test-source exposure belong in explicitly different information tiers. Read the per-task review before choosing a comparator.

This revision contains **'''+str(coverage['candidate_entries'])+''' candidate entries and '''+str(coverage['unique_source_urls'])+''' distinct primary-source URLs** across 30 task reviews. These are source associations and candidate entries, not counts of unique papers/models or proof of exhaustive coverage. All scores in the plots still come from locally executed or explicitly archived matched outputs. No unmatched paper/leaderboard number has been imported as a comparable score. [Full specialist matrix](specialist-matrix.csv), [source ledger](specialist-source-ledger.json), [coverage counts](specialist-coverage.json).

## Repair-assisted sensitivity: usability, not fresh model capability

Four model runtime failures are recovered in a separate track: B08's two whitelist rejections, J08's shape bug and N05's link traversal. Only three meet the original line cap; repaired N05 has 265 lines. B08 changes only the harness; J08 and N05 are human/Codex-debugged programs. Selective post-hoc debugging is not an unbiased comparison of original model generation ability. Original attempts and the old macro panel remain intact.

'''+comparison_table('repair_assisted_task_direction_summaries')+'''

Four C05 archived reference outputs genuinely lack finite values on required support. Their official legacy scorer accepts partial coverage, which differs from our complete-output contract. Padding, interpolating, dropping target support or changing the scoring contract would not recover missing author predictions. They remain explicitly unresolved; obtain/rerun complete predictions under a prospective contract if needed. [Repair methods, verification and attempt history](../../experiments/repairs-v1/README.md).

## Every task's original native trajectory

'''+ '\n'.join(native)+'''

Inspect [task-trajectories.csv](task-trajectories.csv) for exact raw deltas/slopes, [all-model-slices.csv](all-model-slices.csv) for every original slice, and [trajectories.json](trajectories.json) for both tracks and source-linked evidence. Native equal-slice means summarize this finite panel only. All new recommendations are exploratory and require prospective validation.
'''
 (D/'report.md').write_text(report)
 (D/'README.md').write_text('# Practical review, 1 November 2026\n\n[Read the findings](report.md) · [Methods](methods.md) · [Specialist matrix](specialist-matrix.csv) · [Sources](specialist-source-ledger.json) · [All native trajectories](task-trajectories.csv).\n\nOriginal first-attempt evidence and repair-assisted sensitivity are separate. This revision makes no new model calls and certifies no global SOTA winner.\n')
 (D/'methods.md').write_text('''# Methods and interpretation

The input is the unchanged 208-row central ledger and declared primary reference envelopes. General programs: GPT-5.6 Sol, GPT-6 Sol and GPT-6.1 Sol; one frozen first generation per task, with H02 repetitions reported separately. Numerically valid and original line-limit compliance are separate fields. Task scores equal-average their predeclared slices only when all slices for that model are available. Failed tasks are incomplete. This task-level sign-of-native-mean estimand differs from the earlier family-balanced mean-of-slice-directions diagnostic; both are labeled and neither overwrites the other.

Within each task, assert a common metric/direction. Positive oriented native delta means improvement. Numerical tie threshold 1e−9 has no clinical/practical interpretation. Ordinal version slope is half the oriented endpoint difference, defined only for three complete numeric points; both intermediate steps remain visible. No incompatible metric magnitude is averaged across tasks. No new significance test is claimed from dependent task counts. The earlier conditional family sign-flip diagnostics, strict-format sensitivity and assumptions remain in the sealed macro-patterns folder.

Repair view overlays only keys explicitly linked by original task/slice/model. Human/Codex debugging, harness amendment, successful controls and unsuccessful repair attempts retain identities/hashes. Original predictions/scores/protocols remain unchanged. Repairs were chosen after observing failures, hence provide a usability sensitivity, not a randomized or unbiased generation comparison. N05 remains over the original line limit. C05 missing archived outputs are unresolved.

Current-specialist review searches all 30 measured task contracts using primary papers, official repositories and official leaderboards. Per-task JSON records search queries, verified source dates or null, retrieved-on date, information/split/scorer mismatch, existing-reference strength and prospective next comparison. Candidate entries are not independent models/papers. A negative search does not establish nonexistence. Search is bounded, not an exhaustive systematic-review census; no preregistered database-wide retrieval/dual screening was performed. The 62 active unrun entries are outside this fresh current-specialist review. Current-best status stays unverified without exact-contract evidence. No unmatched published score is imported into the measurement ledger or specialist graph.

Reproduce derived files with `python3 scripts/analyze_practical_trends.py --require-specialists --require-repairs` then `python3 scripts/write_practical_review.py`; synchronize trajectories.json to website/data/practical-review.json. Run `python3 scripts/check_practical_review.py` plus existing repository/macro/site checks. These report commands require only the standard library; they do not refit models or access raw caches. Review fingerprints bind each literature record to the local protocol. Artifact manifest binds this report and generator scripts; it does not replace the frozen experimental seals.
''')
 files=list(D.glob('*'));manifest=dict(revision=x['revision'],original_input_sha256=x['input_sha256'],repair_results_sha256=digest(R/'results/repairs-v1.json'),files=[dict(path=str(p.relative_to(R)),sha256=digest(p)) for p in sorted(files+[R/'scripts/analyze_practical_trends.py',R/'scripts/write_practical_review.py',R/'scripts/check_practical_review.py']) if p.is_file() and p.name!='artifact-manifest.json'])
 save(D/'artifact-manifest.json',manifest);print(json.dumps(coverage,indent=2))
if __name__=='__main__':main()
