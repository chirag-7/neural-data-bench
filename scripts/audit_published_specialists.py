"""Describe published-score compatibility without fitting or changing measurements."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/published-specialists-v1'
REASONS = {
 'A09': 'CalMS21 Task 1 data, but only 3 Hz centers with seven pose offsets; published all-frame scores use different temporal information and aggregation.',
 'A14': 'Six-landmark HeadF seven-frame imputation with subjects 1–3 versus 4–5. DISK uses sequence-level chronological 70/15/15 splits and other masking configurations.',
 'A15': 'Held-out fourth bird and recording-equal event F1 with explicit boundary tolerances. DAS reports precision/recall/jitter on a different train/test construction.',
 'B01': 'One 10-second MEArec tutorial fixture. Kilosort4 paper evaluates other hybrid/drifting simulations and uses different reported unit-level summaries.',
 'B03': 'New eight-seed synthetic processed-raster motion experiment, with four held-out simulations. DREDge/MEDiCINe paper results are not scores for these generated rasters.',
 'B07': 'Fixed 4096-sample chunks from 16 source recordings, with local payload/header accounting. Whole-recording paper compression ratios cannot substitute for these chunk scores.',
 'B08': 'FALCON M2 event streams substituted for the original IBL recordings; includes local label/header accounting and a 50 microsecond timing constraint.',
 'C05': 'Five original Spikefinder preparations and official per-cell scorer. Our preparation-equal aggregate and complete-archive eligibility are not a verified published current-best aggregate. Rescored archived predictions remain usable local evidence.',
 'C06': 'CASCADE DS04 at native rate with held-out animals and 200 ms smoothing. Paper noise-resampled leave-one-neuron-out evaluations differ.',
 'D02': 'One Allen example cell and two held-out hyperpolarizing current amplitudes, with passive-voltage RMSE. GLIF spike-prediction explained variance is a different endpoint.',
 'E01': 'Three NLB-derived co-smoothing slices. Area2/DMFC published 20 ms co-bps are relevant slice-level candidates; complete protocol equivalence is unverified. Full MC-Maze is not MC-Maze-Small. No complete three-slice published aggregate is established.',
 'E06': '256 fixed neurons, 64 past frames and 32 future frames. ZAPBench paper uses whole-brain targets, 4/256-frame contexts and horizon-dependent metrics.',
 'F04': 'One Goldin natural-image retinal recording with 18×18 block-averaged inputs and 41-neuron 300 ms Poisson NLL. Published full-study metrics/splits do not establish this score.',
 'G01': 'New chronological split of FALCON M2 calibration recordings, without test-day calibration labels. This is not the official FALCON evaluation split/score.',
 'H01': 'Only eight PhysioNet participants with held-out-person balanced accuracy. Official MOABB left/right table uses within-session ROC-AUC across a different participant panel.',
 'H02': 'BI2012 training runs split people 1–15 versus 16–25; equal-person AUC. MOABB table reports within-session five-fold results.',
 'H08': 'Eight Sleep-EDF first nights, one Fpz-Cz channel and a clock-defined 12-hour window. Different participant folds, wake trimming or channels change the published task.',
 'H16': 'New component-disjoint ocular mixtures with fixed SNR generation. Published EEGdenoiseNet results vary by SNR, noise type and splitting policy; a single transferable aggregate is unverified.',
 'I07': 'Custom ten-person optical-density summaries and split, with a session/condition confound. HbO/HbR paper results are not this processed-input endpoint.',
 'I10': 'Custom MRIQC IQM site-held-out diagnostic and rater collapse. Original paper cohort/split/target conventions differ; archived local predictions remain local evidence.',
 'J08': 'Two SynAPSeg 2D fields, five separate raters, mean instance F1 at IoU 0.5. The paper spatial-centroid consensus endpoint differs. Archived StarDist masks have been rescored locally.',
 'K01': 'New Allen 11-feature spiny/aspiny task with donor-disjoint split. Full cell-type taxonomy papers do not report this binary feature-restricted benchmark.',
 'K04': 'DLPFC expression-only supervised layer transfer, 500 training-selected genes, one test donor and equal-section macro F1. Spatial clustering ARI or multimodal segmentation are different targets.',
 'K05': 'Anonymous 2000-gene inputs and three orthogonal IF/RNAScope fractions in a custom donor/block split. Reference-based seven-cell-type deconvolution has different inputs and targets.',
 'K06': 'Mouse PV/SST genetic-label prediction from waveforms with held-out mice. WaveMAP paper accuracy predicts eight unsupervised macaque waveform clusters, not PV/SST.',
 'L04': 'One teaching-data place cell, chronological 60/40 split plus gap, and local train-null bits/spike. NeMoS is a modeling library, not a leaderboard for this exact fixture.',
 'L06': 'sbibm observations, but likelihood-informed samplers and a 2000-draw C2ST adaptation. The original simulator-only, simulation-budget benchmark is different; values below chance are not superior posteriors.',
 'M01': 'Custom IBL history-feature and held-out-mouse next-choice task. Official full-session behavioral-model likelihoods do not establish this processed-input score.',
 'M04': 'New 24-agent reinforcement-learning simulation and normalized parameter MAE. Wilson & Collins is the motivating methods paper, not a published score for our simulator seed.',
 'N05': 'New 61-field calculation fixture from one legacy Allen NWB file. PyNWB schema validation is not this physical-unit question-answer score; correctness is deterministic.',
}

def number(model, value, metric, unit, source, location, scope):
 return dict(model=model, value=value, metric=metric, unit=unit, source_url=source,
             source_location=location, selection_scope=scope,
             eligible_for_local_win_loss=False, global_current_best_verified=False)

NUMBERS = {
 'A09': [number('VASSI, smoothing + thresholds', .867, 'four-class frame macro F1', 'fraction',
  'https://elifesciences.org/reviewed-preprints/108329', 'Results: CALMS21 dataset, Figure 1C–D; reported SD 0.001 over 20 runs',
  'Best four-class postprocessing variant reported in this paper; newer candidates in the review are not ruled out.')],
 'A15': [number('DAS', 99, 'Bengalese finch precision', 'percent',
  'https://pmc.ncbi.nlm.nih.gov/articles/PMC8560090/', 'Table 3, Bengalese finch row',
  'Paper comparison; not a verified 2026 global winner.'),
  number('DAS', 99, 'Bengalese finch recall', 'percent',
  'https://pmc.ncbi.nlm.nih.gov/articles/PMC8560090/', 'Table 3, Bengalese finch row', 'Same method and row; not a separate benchmark.')],
 'E01': [number('LangevinFlow', .2881, 'Area2-Bump 20 ms co-bps', 'bits/spike',
  'https://arxiv.org/html/2507.11531v2', 'Table 2, Area2-Bump co-bps column',
  'Highest co-bps among methods in Table 2; full leaderboard optimality and our exact slice compatibility are unverified.'),
  number('LangevinFlow', .1904, 'DMFC-RSG 20 ms co-bps', 'bits/spike',
  'https://arxiv.org/html/2507.11531v2', 'Table 2, DMFC-RSG co-bps column', 'Highest co-bps among methods in Table 2; not a complete E01 three-slice aggregate.')],
 'H01': [number('FgMDM', 68.46, 'PhysionetMI left/right within-session ROC-AUC', 'percent',
  'https://moabb.neurotechx.com/docs/paper_results.html', 'Motor Imagery – Left vs Right Hand, PhysionetMI column; SD 19.06',
  'Highest PhysionetMI mean among the pipelines in this official table, not across every published model.')],
 'H02': [number('XDAWNCov+TS+SVM', 90.99, 'BI2012 within-session ROC-AUC', 'percent',
  'https://moabb.neurotechx.com/docs/paper_results.html', 'P300/ERP table, BI2012 column; SD 4.79',
  'Highest BI2012 mean among pipelines in this official table, not a cross-person result.')],
 'K06': [number('Gradient-boosted classifier of WaveMAP clusters', 91, 'Eight-cluster classification accuracy', 'percent',
  'https://elifesciences.org/articles/67490', 'Figure 3C and associated Results',
  'Reported cluster predictability; explicitly not a PV/SST classification result or a claim of genetic cell-type SOTA.')],
}

def main():
 original = ROOT / 'analysis/specialist-frontier-v1/comparison.json'
 panel = json.loads(original.read_text())
 rows = []
 for task in panel['tasks']:
  bid = task['benchmark_id']
  review_path = ROOT / f'literature/specialist-review-2026-11-01/{bid}.json'
  review = json.loads(review_path.read_text())
  protocol = ROOT / ('experiments/C05/phase2-protocol.md' if bid == 'C05' else f'experiments/{bid}/protocol.md')
  assert protocol.exists(), protocol
  candidates = [{'name': c['name'], 'source_urls': c.get('source_urls', []),
                 'status': 'candidate_from_prior_review_not_a_certified_winner'} for c in review['candidates']]
  rows.append(dict(benchmark_id=bid, task=task['task'], local_metric=task['metric'],
   local_direction=task['direction'], general_scores=task['general_scores'],
   protocol_path=str(protocol.relative_to(ROOT)), protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),
   compatibility='no_exact_published_task_aggregate_verified', reason=REASONS[bid],
   published_results=NUMBERS.get(bid, []), candidates=candidates,
   review_path=str(review_path.relative_to(ROOT)), eligible_published_comparator=None))
 result=dict(revision='published-specialists-v1', audited_on='2026-11-01',
  purpose='Published/official result lookup, not new specialist fitting.',
  status='Compatibility audit complete for 30 tasks; published current-best score collection incomplete.',
  n_tasks=len(rows), n_exact_published_task_aggregates_verified=0,
  n_tasks_with_verified_context_numbers=len(NUMBERS),
  n_verified_context_numbers=sum(map(len, NUMBERS.values())),
  rules=['Keep all four model measurements and the 30 task definitions fixed.',
   'Use the strongest verified result for the same protocol; newest publication alone does not establish best performance.',
   'Require dataset/version, input information, targets, evaluation split, metric and aggregation compatibility.',
   'A failed or incomplete source search is not evidence that no matching publication exists.',
   'Unmatched paper numbers are context only and never enter local graphs, gaps, IQR bands or win/loss totals.',
   'No model calls, fitting, task redesign or paper-to-metric conversions in this audit.'],
  source_panel_sha256=hashlib.sha256(original.read_bytes()).hexdigest(), tasks=rows)
 OUT.mkdir(exist_ok=True)
 payload=json.dumps(result, indent=2, ensure_ascii=False)+'\n'
 (OUT/'audit.json').write_text(payload)
 (ROOT/'website/data/published-specialists.json').write_text(payload)
 text=['# Published specialist results: compatibility audit', '',
  '**Status: 30 local protocols audited; zero exact published task aggregates verified so far. This is not a completed current-SOTA leaderboard.**', '',
  'The requested experiment was to run existing benchmarks and retrieve their best published specialist results. Several evaluations introduced here instead use custom subsets, splits, inputs or scoring rules. That implementation choice prevents a direct paper-score substitution in many rows. Official data does not automatically make an evaluation the official benchmark.', '',
  'The four-model measurements remain unchanged and still describe model-written analysis programs executed locally. The existing 14 scored specialist references include local implementations and rescored author predictions; they are not 14 certified current published SOTA results. Their 10-versus-4 raw outcome must not be described as general models beating the best neuroscience models.', '',
  '## Import rule', '',
  'Look for the strongest verified paper or official result on the same benchmark version, inputs, target, evaluation split, metric and aggregation. Prefer a newer comparable result only when its performance or authority justifies selection; a newer paper can perform worse. Preserve source date/version and exact table/row. A source can match one evaluation slice without supporting a whole-task mean. Different research compute is disclosed separately from evaluation identity.', '',
  'No new specialist fitting or task redesign is authorized by this lookup. Earlier exploratory adaptations are retained separately under [specialist-extension-v1](../../experiments/specialist-extension-v1/protocol.md), superseded for this purpose and excluded from every published macro count.', '',
  '## Verified published numbers: context only', '',
  'These are exact numbers checked in the cited primary sources. They are not certified global winners, and none has been admitted to the local win/loss totals. No score is converted between precision/recall, F1, accuracy, AUC or other endpoints.', '',
  '| Local task | Published method | Published result | Source location |', '|---|---|---|---|']
 for bid, nums in NUMBERS.items():
  for n in nums:
   text.append(f"| {bid} | {n['model']} | {n['value']} {n['unit']} · {n['metric']} | [{n['source_location']}]({n['source_url']}) |")
 text += ['', '## All 30 protocol checks', '',
  'Every row currently has the disposition **no exact published task aggregate verified**. This records the evidence reviewed, not proof that no compatible result exists. Linked candidate reviews contain additional sources and search limitations; candidate names do not establish best performance.', '',
  '| Task | Why a related paper number cannot yet substitute | Protocol / review |', '|---|---|---|']
 for row in rows:
  bid=row['benchmark_id']
  text.append(f"| {bid} · {row['task']} | {row['reason']} | [Protocol](../../{row['protocol_path']}) · [Sources](../../{row['review_path']}) |")
 text += ['', '## Consequence for the analysis', '',
  'The observed generation trend among GPT-4.1, GPT-5, GPT-5.6 and GPT-6.1 remains a descriptive result for these fixed code-generation evaluations. It cannot establish that general models outperform current specialist SOTA. The missing published comparators remain unresolved, not numerical losses or ties. Collecting more related papers alone will not repair a changed evaluation protocol. This audit leaves the official-versus-custom distinction explicit instead of manufacturing a complete specialist table.', '',
  'The [machine-readable audit](audit.json) binds each explanation to its protocol SHA256, copies the unchanged four-model task means, records source locations and keeps every unmatched published score ineligible. Existing [specialist comparison](../specialist-frontier-v1/report.md) remains a separate local-reference analysis.', '']
 (OUT/'report.md').write_text('\n'.join(text))
 print(f'{len(rows)} task audits; {len(NUMBERS)} tasks with {sum(map(len, NUMBERS.values()))} context numbers; 0 exact task aggregates verified')

if __name__ == '__main__':
 main()
