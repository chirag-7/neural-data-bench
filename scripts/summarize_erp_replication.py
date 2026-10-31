"""Separate, audited follow-up ledger; never modify original macro measurements."""
from pathlib import Path
import csv, json
import numpy as np
from scipy.stats import rankdata
from expansion import ROOT as R, MODELS, sha

D = R / 'experiments/H02/replication-v1'
L = R / 'results/generation/H02-replication-v1'

def rank_auc(y, pred):
    y = np.asarray(y, dtype=int)
    ranks = rankdata(np.asarray(pred, dtype=float), method='average')
    n = int(y.sum())
    return float((ranks[y == 1].sum() - n * (n + 1) / 2) / (n * (len(y) - n)))

def main():
    spec = json.loads((D / 'run-spec.json').read_text())
    for path, value in spec['sealed_files'].items():
        assert sha(R / path) == value, path
    assert sha(R / 'data/cache/H02/data.npz') == spec['data_sha256']
    original = json.loads((R / 'results/H02.json').read_text())
    new = json.loads((D / 'new-attempts.json').read_text())
    assert {(r['model'], r['replicate']) for r in new} == {(m, k) for m in MODELS for k in [2, 3]}
    rows = [dict(r, replicate=1, study='original', original_macro_eligible=True)
            for r in original if r['model'] in MODELS] + new
    refs = [r for r in original if r['model'] not in MODELS]
    tuned = json.loads((D / 'specialist-result.json').read_text())
    refs.append(tuned)
    provenance = []
    for r in new:
        name = f"{r['model']}--r{r['replicate']}"
        logfile = L / (name + '.jsonl')
        events = [json.loads(line) for line in logfile.read_text().splitlines() if line.strip()]
        tools = [e for e in events if e.get('type') in ['item.started', 'item.completed']
                 and e.get('item', {}).get('type') in ['command_execution', 'mcp_tool_call', 'web_search', 'file_change']]
        usage = [e['usage'] for e in events if e.get('type') == 'turn.completed']
        assert not tools, name + ': generation tools were used'
        generation_exit = json.loads((L / (name + '.exit.json')).read_text())['exit_code']
        assert len(usage) == 1 or generation_exit != 0, name + ': successful generation needs completion usage'
        output = D / 'generated' / (name + '.json')
        provenance.append(dict(requested_model=r['model'], replicate=r['replicate'],
                               reasoning_effort='high', user_prompt_sha256=sha(R / 'experiments/H02/prompt.txt'),
                               output_file=str(output.relative_to(R)) if output.exists() else None,
                               output_sha256=sha(output) if output.exists() else None,
                               generation_exit=generation_exit,
                               events_file=str(logfile.relative_to(R)), events_sha256=sha(logfile),
                               tool_events=len(tools), usage=usage[0] if usage else None,
                               effective_context='Identical explicit user prompt; CLI/provider instructions and resolved checkpoint not independently controlled'))
    with np.load(R / 'data/cache/H02/data.npz') as z:
        y, groups, train_y, train_groups = (z[k] for k in ['test_y', 'test_groups', 'train_y', 'train_groups'])
    assert not set(groups) & set(train_groups)
    verification = []
    for r in rows + refs:
        if r['status'] != 'measured':
            continue
        p = R / r['prediction_file']
        assert sha(p) == r['prediction_sha256']
        with np.load(p) as z:
            pred = z['predictions']
        assert pred.shape == y.shape and np.isfinite(pred).all()
        per = [rank_auc(y[groups == g], pred[groups == g]) for g in np.unique(groups)]
        error = abs(float(np.mean(per)) - r['score'])
        assert error < 1e-12 and np.max(np.abs(np.asarray(per) - r['per_unit'])) < 1e-12
        verification.append(dict(model=r['model'], replicate=r.get('replicate'),
                                 prediction_sha256=sha(p), independent_rank_auc_error=error))
    selection_checks = None
    if tuned['status'] == 'measured':
        choice = json.loads((D / 'selection.json').read_text())
        assert sha(D / 'selection.json') == tuned['selection_sha256']
        with np.load(D / 'validation-predictions.npz') as z:
            oof = z['predictions']
        assert oof.shape == (12, len(train_y)) and np.isfinite(oof).all()
        for i, c in enumerate(choice['candidates']):
            value = float(np.mean([rank_auc(train_y[train_groups == g], oof[i, train_groups == g])
                                   for g in np.unique(train_groups)]))
            assert abs(value - c['validation_score']) < 1e-12
        assert choice['chosen_index'] == max(range(12), key=lambda i: choice['candidates'][i]['validation_score'])
        validation_people = []
        for fold in choice['folds']:
            assert not set(fold['train_people']) & set(fold['validation_people'])
            assert set(fold['train_people']) | set(fold['validation_people']) == set(train_groups)
            validation_people += fold['validation_people']
        assert sorted(validation_people) == sorted(set(train_groups))
        selection_checks = dict(all_12_oof_candidate_scores_verified=True, validation_people_once_only=True,
                                group_disjoint_folds=True, selection_matches_declared_rule=True,
                                selected=choice['selected'],
                                oof_prediction_sha256=sha(D / 'validation-predictions.npz'))
    summaries = []
    fixed_score = next(r['score'] for r in refs if r['model'] == 'xdawn-tslr')
    for model in MODELS:
        attempts = sorted([r for r in rows if r['model'] == model], key=lambda r: r['replicate'])
        valid = [r for r in attempts if r['status'] == 'measured']
        scores = [r['score'] for r in valid]
        summaries.append(dict(model=model, attempted=len(attempts), valid=len(valid),
                              strict_valid=sum(r.get('line_limit_compliant') is True for r in valid),
                              mean=float(np.mean(scores)) if scores else None,
                              minimum=min(scores) if scores else None, maximum=max(scores) if scores else None,
                              per_attempt=[dict(replicate=r['replicate'], status=r['status'], score=r.get('score'),
                                                line_limit_compliant=r.get('line_limit_compliant')) for r in attempts],
                              attempts_above_fixed_specialist=sum(v > fixed_score for v in scores),
                              attempts_above_tuned_specialist=sum(v > tuned['score'] for v in scores) if tuned['status'] == 'measured' else None))
    report = dict(benchmark_id='H02', study='replication-v1', original_primary_macro_unchanged=True,
                  prospective=False, scope='One dataset, ten held-out people; original plus two fresh generations per model',
                  generation_summary=summaries, attempts=rows, references=refs,
                  limitations=['Retrospective selection of task and follow-up design',
                               'Three generations are descriptive and not independent datasets',
                               'Provider context and checkpoint changes not fully observable',
                               'No global SOTA or equal total tuning effort established'])
    dest = R / 'results/replications'
    dest.mkdir(exist_ok=True)
    (dest / 'H02.json').write_text(json.dumps(report, indent=2) + '\n')
    keys = ['benchmark_id', 'study', 'model', 'replicate', 'status', 'score', 'metric',
            'seconds', 'code_lines', 'line_limit_compliant', 'prediction_file', 'prediction_sha256', 'original_macro_eligible']
    with (dest / 'H02.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows + refs)
    (D / 'generation-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (D / 'verification.json').write_text(json.dumps(dict(frozen_seal_verified=True,
        independently_rescored_predictions=verification, selection_checks=selection_checks,
        original_macro_measurements_sha256=sha(R / 'results/archive/v07-measurements.jsonl') if (R / 'results/archive/v07-measurements.jsonl').exists() else sha(R / 'results/measurements.jsonl')), indent=2) + '\n')
    table = '\n'.join(f"| {r['model']} | {r['valid']}/{r['attempted']} | {r['strict_valid']}/{r['attempted']} | {r['mean']:.6f} | {r['minimum']:.6f}–{r['maximum']:.6f} | {r['attempts_above_fixed_specialist']} | {r['attempts_above_tuned_specialist']} |" for r in summaries)
    text = '# H02 follow-up results\n\nRetrospective replication on the same frozen Brain Invaders 2012 split. Original plus two fresh, no-feedback submissions per model. Equal-person ROC-AUC; larger is better. Means include every numerically valid attempt; failures and format compliance are shown separately. No best-of-three model selection.\n\n| Model | Valid | Strict valid | Mean | Range | Attempts > fixed specialist | Attempts > tuned specialist |\n|---|---:|---:|---:|---:|---:|---:|\n' + table
    text += f"\n\nOriginal fixed xDAWN reference: **{fixed_score:.6f}**. Tuned reference status: **{tuned['status']}**."
    if tuned['status'] == 'measured':
        text += f" Tuned xDAWN test score: **{tuned['score']:.6f}**, chosen configuration `{json.dumps(tuned['selected_configuration'])}`; total selection/refit/inference {tuned['seconds']:.2f}s. The choice used only five-fold training-person validation, not the test score."
    text += '\n\nThis study adds six generation attempts and one specialist attempt separately from the original suite. It adds no dataset, cohort, task or family. Original 75-attempt macro comparisons retain their frozen scores and reference policy. Three generations do not establish a stable population ranking; this task and follow-up plan were selected after seeing the original results.\n\n[All attempts and references](../../../results/replications/H02.json) · [CSV](../../../results/replications/H02.csv) · [Frozen amendment](amendment.md) · [Verification](verification.json) · [Generation provenance](generation-provenance.json)\n'
    (D / 'results.md').write_text(text)
    print(json.dumps(dict(generation_summary=summaries, tuned_reference=tuned.get('score'),
                         rescored=len(verification)), indent=2))

if __name__ == '__main__':
    main()
