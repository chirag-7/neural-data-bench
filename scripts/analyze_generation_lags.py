"""Exploratory lag/IQR sensitivities from retained scores; no fitting or model calls."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import csv, hashlib, json, math, statistics

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'analysis/generation-comparison-v2/generation-comparison.json'
OUT = ROOT / 'analysis/generation-lags-v1'
RAW_TOL = 1e-9
RATIO_TOL = 1e-12
THRESHOLDS = (0.1, 0.5)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def native_class(delta):
    return 'better' if delta > RAW_TOL else 'worse' if delta < -RAW_TOL else 'numerical_tie'

def main():
    source = json.loads(SOURCE.read_text())
    models = source['models']
    task_rows, summaries = [], []
    pairs = sorted(combinations(range(len(models)), 2), key=lambda p: (p[1]-p[0], p[0]))
    for i, j in pairs:
        counts = {name: Counter() for name in ['raw', 'iqr_0.1', 'iqr_0.5']}
        ids = {name: {} for name in counts}
        for task in source['tasks']:
            values = [task['scores'][m] for m in models]
            complete = all(isinstance(v, (int, float)) and math.isfinite(v) for v in values)
            pair_complete = all(values[k] is not None for k in (i, j))
            delta = (values[j]-values[i]) * (1 if task['direction']=='higher' else -1) if pair_complete else None
            raw = native_class(delta) if delta is not None else 'incomplete'
            q1, _, q3 = statistics.quantiles(values, n=4, method='inclusive') if complete else (None, None, None)
            scale = q3-q1 if complete else None
            ratio = delta/scale if scale is not None and scale > 0 else None
            row = dict(benchmark_id=task['benchmark_id'], family=task['family_code'], metric=task['metric'], direction=task['direction'], lag=j-i, older=models[i], newer=models[j], older_score=values[i], newer_score=values[j], direction_adjusted_delta=delta, q1=q1, q3=q3, panel_iqr=scale, normalized_gap=ratio, raw=raw)
            for threshold in THRESHOLDS:
                key = f'iqr_{threshold}'
                if not complete:
                    outcome = 'not_estimable'
                elif raw == 'numerical_tie':
                    outcome = 'within_band'
                elif ratio is None:
                    outcome = 'not_estimable'
                else:
                    outcome = 'better' if ratio > threshold + RATIO_TOL else 'worse' if ratio < -threshold - RATIO_TOL else 'within_band'
                row[key] = outcome
            for name in counts:
                outcome = row[name]
                counts[name][outcome] += 1
                ids[name].setdefault(outcome, []).append(task['benchmark_id'])
            task_rows.append(row)
        for name, counter in counts.items():
            keys = ['better', 'worse', 'numerical_tie', 'incomplete'] if name=='raw' else ['better', 'worse', 'within_band', 'not_estimable']
            summaries.append(dict(lag=j-i, older=models[i], newer=models[j], analysis=name, n_tasks=len(source['tasks']), counts={k:counter[k] for k in keys}, task_ids={k:ids[name].get(k, []) for k in keys}))
    methods = dict(
        estimand='Descriptive task counts on the final repair-assisted panel; each task once.',
        order=models, lag='Ordinal model-index distance; not time, parameter count or training compute.',
        scale='IQR of the same four model task means; inclusive linear quantiles (Hyndman-Fan type 7). With sorted a<=b<=c<=d: Q1=.25a+.75b; Q3=.75c+.25d.',
        formula='R = preferred-direction sign * (later score - earlier score) / panel IQR',
        thresholds=list(THRESHOLDS), threshold_status='Analyst-selected post-hoc sensitivity bands, not validated small/large effect standards or equivalence margins.',
        raw_numerical_tie_tolerance=RAW_TOL, normalized_boundary_tolerance=RATIO_TOL,
        within_band='Absolute normalized gap at or below threshold (plus boundary tolerance), including raw numerical ties. Not evidence of equivalence or randomness.',
        missing_or_zero_scale='Missing four-model scores: normalization not estimable. Zero IQR: no ratio; numerical pair ties within band, other pairs not estimable. Never add epsilon to the denominator.',
        invariance='Ratio is invariant to positive affine changes of native score units/origin, apart from the separately retained native numerical-tie tolerance. Not invariant to nonlinear metric transformations.',
        limitations=['Only four selected model points define each spread: estimates can be unstable and change with the model roster.', 'A large ratio can still be a tiny or practically unimportant native difference. This is not Cohen d, biological variability, error reduction, a z-score or a signal-to-noise ratio.', 'IQR is a robust spread statistic in general; that does not make this four-point application a robust inferential result.', 'Lags share tasks/models and are not independent repetitions. No pooled lag p-values, significance, confidence intervals or scaling-law fit are claimed.', 'Convenience tasks, overlapping sources, unequal wrappers and selective repairs limit generalization. J08 GPT-4.1 has a documented manual training-budget adaptation.', 'C2ST retains the original lower-is-better direction, but the diagnostic target is 0.5; near-chance ordering need not indicate a better sampler.'],
        stronger_next_analysis='Predeclare task-specific worthwhile-effect/equivalence margins; rescore with paired resampling of independent people, animals or recordings; preserve hierarchy and metric aggregation; repeat model generations under matched conditions. Report unresolved intervals rather than forcing small/large labels.',
        citations=[{'title':'NIST: Measures of Scale', 'url':'https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm', 'supports':'IQR as a robust measure of spread, not the selected thresholds or conclusions.'}])
    data = dict(revision='generation-lags-v1', n_tasks=len(source['tasks']), n_families=len({t['family_code'] for t in source['tasks']}), models=models, thresholds=list(THRESHOLDS), methods=methods, summaries=summaries, task_pairs=task_rows, input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [SOURCE, Path(__file__).resolve()]})
    dump(OUT/'lag-analysis.json', data)
    dump(OUT/'methods.json', methods)
    dump(ROOT/'website/data/generation-lags.json', data)
    for name, rows in [('task-pairs.csv', task_rows), ('comparison-counts.csv', [dict(lag=s['lag'],older=s['older'],newer=s['newer'],analysis=s['analysis'],n_tasks=s['n_tasks'],**s['counts']) for s in summaries])]:
        with (OUT/name).open('w', newline='') as f:
            # Raw and normalized summaries use different outcome columns.
            keys = list(dict.fromkeys(k for row in rows for k in row))
            writer=csv.DictWriter(f, fieldnames=keys, lineterminator='\n'); writer.writeheader(); writer.writerows(rows)
    lines=['# Model-generation lag and change-size sensitivities', '', 'Six comparisons across 30 tasks / 14 categories, grouped into three lag-1, two lag-2 and one lag-3 comparisons. Lag is ordinal, not elapsed time or training compute. No new model calls, fitted predictions or score changes.', '', '**These are descriptive, repair-assisted results. IQR bands are exploratory panel-relative gaps, not statistically established small/large changes, significance tests or practical equivalence.**', '', '## Methods', '', '`R = direction-adjusted native score change / IQR(four model task means)`.', '', methods['scale'], '', methods['within_band'], '', methods['missing_or_zero_scale'], '', 'The native tie tolerance is 1e-9; normalized threshold comparisons allow 1e-12 numerical tolerance. The thresholds 0.1 and 0.5 were selected after inspecting this panel and are sensitivity choices, not accepted universal effect-size standards.', '']
    for name, title in [('raw','Any numerical change'),('iqr_0.1','Changes exceeding 0.1 panel IQR'),('iqr_0.5','Changes exceeding 0.5 panel IQR')]:
        last = 'Numerical tie | Incomplete' if name=='raw' else 'Within band | Not estimable'
        lines += [f'## {title}', '', f'| Lag | Earlier → later | Better | Worse | {last} |', '|---|---|---:|---:|---:|---:|']
        for s in summaries:
            if s['analysis']!=name: continue
            c=s['counts']; extra=[c[k] for k in (['numerical_tie','incomplete'] if name=='raw' else ['within_band','not_estimable'])]
            lines.append(f"| {s['lag']} | {s['older']} → {s['newer']} | {c['better']} | {c['worse']} | {extra[0]} | {extra[1]} |")
        lines += ['']
    lines += ['## Interpretation and limits', '', 'The endpoint direction survives both filters: 28/2/0 numerical better/worse/ties becomes 27/2/1 and 25/2/3 better/worse/within-band at 0.1 and 0.5 IQR. The 5.6→6.1 comparison changes from 20/9/1 to 14/6/10 and 6/3/21. These are conditional descriptions of this selected panel, not evidence for a scaling exponent or a causal slowdown.', '']
    lines += ['- '+x for x in methods['limitations']]
    lines += ['', 'The standardized gaps are sensitive to metric choice, particularly nonlinear transformations, and to which four models are included. Positive affine unit changes cancel in the ratio. Native scores remain the basis for practical decisions.', '', '## Stronger inference', '', methods['stronger_next_analysis'], '', '## Audit and reproduce', '', '`python3 scripts/analyze_generation_lags.py` followed by `python3 scripts/check_generation_lags.py`. No raw data loading, fitting or API calls.', '', '- [Full methods](methods.json)', '- [Every native difference, IQR, ratio and classification](task-pairs.csv)', '- [All comparison counts](comparison-counts.csv)', '- [Machine-readable evidence, task IDs and source hashes](lag-analysis.json)', '- [Current four-model source scores](../generation-comparison-v2/task-scores.csv)', '- [Macro patterns and original-attempt sensitivity](../generation-patterns-v1/report.md)', '- [Manual repairs](../../experiments/generation-repairs-v1/README.md)', '- [NIST: Measures of Scale](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm) (supports the scale statistic; not these thresholds).']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print('Derived six lag comparisons, three tables and 180 auditable task-pair rows; no model calls.')

if __name__=='__main__':
    main()
