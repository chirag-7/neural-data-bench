"""Independent rational-arithmetic cross-check of lag tables and retained source scores."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib, json, math

ROOT=Path(__file__).resolve().parents[1]
def main():
    d=json.loads((ROOT/'analysis/generation-lags-v1/lag-analysis.json').read_text())
    source=json.loads((ROOT/'analysis/generation-comparison-v2/generation-comparison.json').read_text())
    assert d['n_tasks']==30 and d['n_families']==14 and len(d['task_pairs'])==180 and len(d['summaries'])==18
    assert d['models']==source['models']
    for path,h in d['input_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    lookup={t['benchmark_id']:t for t in source['tasks']}
    counts={};seen=set()
    for row in d['task_pairs']:
        key=(row['benchmark_id'],row['older'],row['newer']);assert key not in seen;seen.add(key)
        t=lookup[row['benchmark_id']];values=[F(str(t['scores'][m])) for m in d['models']]
        i,j=[d['models'].index(row[k]) for k in ['older','newer']];assert row['lag']==j-i and j>i
        assert row['direction']==t['direction'] and row['metric']==t['metric']
        assert row['older_score']==t['scores'][row['older']] and row['newer_score']==t['scores'][row['newer']]
        delta=(values[j]-values[i])*(1 if t['direction']=='higher' else -1)
        a,b,c,e=sorted(values);q1=(a+3*b)/4;q3=(3*c+e)/4;iqr=q3-q1
        for name,value in [('direction_adjusted_delta',delta),('q1',q1),('q3',q3),('panel_iqr',iqr)]:assert math.isclose(row[name],float(value),rel_tol=1e-10,abs_tol=1e-12),(key,name)
        raw='better' if delta>F('1e-9') else 'worse' if delta< -F('1e-9') else 'numerical_tie'
        assert row['raw']==raw
        ratio=delta/iqr if iqr else None
        if ratio is not None:
            assert math.isclose(row['normalized_gap'],float(ratio),rel_tol=1e-10,abs_tol=1e-12)
            # Unit/origin changes cancel exactly in the rational ratio.
            transformed=[v*7+123 for v in values];aa,bb,cc,ee=sorted(transformed)
            transformed_iqr=(3*cc+ee-aa-3*bb)/4
            assert (transformed[j]-transformed[i])*(1 if t['direction']=='higher' else -1)/transformed_iqr==ratio
        for analysis in ['raw','iqr_0.1','iqr_0.5']:
            if analysis=='raw':expected=raw
            elif raw=='numerical_tie':expected='within_band'
            elif ratio is None:expected='not_estimable'
            else:
                limit=F(analysis.split('_')[1])+F('1e-12')
                expected='better' if ratio>limit else 'worse' if ratio < -limit else 'within_band'
            assert row[analysis]==expected,(key,analysis)
            counts.setdefault((row['older'],row['newer'],analysis),Counter())[expected]+=1
    for s in d['summaries']:
        c=counts[s['older'],s['newer'],s['analysis']]
        assert sum(s['counts'].values())==30 and all(s['counts'][k]==c[k] for k in s['counts'])
        for outcome,ids in s['task_ids'].items():
            assert len(ids)==s['counts'][outcome]
            assert set(ids)=={r['benchmark_id'] for r in d['task_pairs'] if (r['older'],r['newer'])==(s['older'],s['newer']) and r[s['analysis']]==outcome}
    expected={1:[(19,11,0),(25,4,1),(20,9,1)],2:[(25,5,0),(24,5,1)],3:[(28,2,0)]}
    for lag, triples in expected.items():
        rows=[s for s in d['summaries'] if s['lag']==lag and s['analysis']=='raw']
        assert [(r['counts']['better'],r['counts']['worse'],r['counts']['numerical_tie']) for r in rows]==triples
    for analysis, triples in [('iqr_0.1',[(19,8,3),(24,4,2),(14,6,10),(25,5,0),(24,4,2),(27,2,1)]),('iqr_0.5',[(16,8,6),(18,4,8),(6,3,21),(22,4,4),(20,1,9),(25,2,3)])]:
        assert [(s['counts']['better'],s['counts']['worse'],s['counts']['within_band']) for s in d['summaries'] if s['analysis']==analysis]==triples
    assert (ROOT/'website/data/generation-lags.json').read_bytes()==(ROOT/'analysis/generation-lags-v1/lag-analysis.json').read_bytes()
    assert d['methods']['threshold_status'].startswith('Analyst-selected')
    print('Lag cross-check passed:180 source-matched task pairs; independent exact quartiles/ratios; all18 summaries and displayed snapshot counts; source hashes and synchronized website data.')

if __name__=='__main__':main()
