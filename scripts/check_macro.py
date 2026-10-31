"""Independent portable macro arithmetic check. Standard library; no scientific fitting."""
from pathlib import Path
from collections import defaultdict, Counter
from fractions import Fraction
import csv, hashlib, itertools, json, math
R=Path(__file__).resolve().parents[1];D=R/'analysis/macro-patterns'
s=json.loads((D/'statistics.json').read_text())
for p,h in s['input_sha256'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
rs=[json.loads(x) for x in (R/'results/measurements.jsonl').read_text().splitlines()]
lookup={(r['benchmark_id'],r['slice_id'],r['model']):r for r in rs}
keys={(r['benchmark_id'],r['slice_id']) for r in rs if r['model'] in s['model_order']}
ex=set(s['scopes']['observed_exclusions']);ps=[]
def valid(r):return r is not None and r['status']=='measured' and isinstance(r.get('score'),(float,int)) and math.isfinite(r['score'])
def avg(xs):return sum(xs,Fraction())/len(xs)
for p in s['pairwise']:
    tasks=defaultdict(list);counts=Counter()
    for t,sl in sorted(keys):
        if t in ex:continue
        a,b=lookup.get((t,sl,p['older'])),lookup.get((t,sl,p['newer']))
        if valid(a) and valid(b):
            d=(b['score']-a['score'])*(1 if b['direction']=='higher' else -1);v=1 if d>1e-9 else -1 if d< -1e-9 else 0
            counts['win' if v==1 else 'loss' if v==-1 else 'tie']+=1
        else:
            counts['failed_or_missing']+=1;v=1 if valid(b) and not valid(a) else -1 if valid(a) and not valid(b) else 0
        tasks[t].append(Fraction(v))
    fam=defaultdict(list)
    for t,values in tasks.items():fam[t[0]].append(avg(values))
    contrasts=[avg(v) for f,v in sorted(fam.items())];effect=avg(contrasts)
    extreme=sum(abs(avg([sign*x for sign,x in zip(signs,contrasts)]))>=abs(effect) for signs in itertools.product([-1,1],repeat=len(contrasts)))
    exact=Fraction(extreme,2**len(contrasts));ps.append(float(exact));main=p['main_conservative'];desc=p['descriptive_denominator']
    assert (len(tasks),len(fam),sum(map(len,tasks.values())))==(main['n_tasks'],main['n_families'],main['n_slices'])
    assert dict(counts)==desc['slice_counts']
    assert abs(float(effect)-main['family_equal_net_direction'])<1e-12
    assert float(exact)==main['exact_family_signflip_two_sided_p']
    for f,values in fam.items():
        r=next(r for r in main['families'] if r['family_code']==f);assert abs(float(avg(values))-r['net_direction'])<1e-12
    common={(t,sl) for t,sl in keys if t not in ex and all(valid(lookup.get((t,sl,m))) and lookup[(t,sl,m)]['strict_format_compliant'] for m in s['model_order'])}
    assert len(common)==p['common_three_model_strict']['n_slices']
    assert len({t for t,sl in common})==p['common_three_model_strict']['n_tasks']
    print(p['older'],'->',p['newer'],'effect',str(effect),'exact p',str(exact))
order=sorted(range(len(ps)),key=lambda i:ps[i]);adj={};running=0
for k,i in enumerate(order):running=max(running,min(1,(len(ps)-k)*ps[i]));adj[i]=running
for i,p in enumerate(s['pairwise']):assert p['main_conservative']['holm_adjusted_p_three_version_pairs']==adj[i]
for file,key in [('main-conservative-tasks.csv','tasks'),('main-conservative-families.csv','families')]:
    rows=list(csv.DictReader((D/file).open()))
    for p in s['pairwise']:
        sub=[r for r in rows if (r['older'],r['newer'])==(p['older'],p['newer'])]
        assert len(sub)==len(p['main_conservative'][key])
        for r in sub:
            idkey='benchmark_id' if key=='tasks' else 'family_code'
            x=next(x for x in p['main_conservative'][key] if x[idkey]==r[idkey]);assert abs(float(r['net_direction'])-x['net_direction'])<1e-12
for r in s['category_patterns']:
    p=next(p for p in s['pairwise'] if (p['older'],p['newer'])==(r['older'],r['newer']))
    ts=[t for t in p['main_conservative']['tasks'] if t['family_code']==r['family_code']]
    assert r['positive_tasks']==sum(t['net_direction']>1e-9 for t in ts) and r['n_tasks']==len(ts)
payload=json.loads((R/'website/data/macro-report.json').read_text())
assert payload['input_sha256']==s['input_sha256']
for r in payload['pairs']:
    p=next(p for p in s['pairwise'] if (p['older'],p['newer'])==(r['older'],r['newer']))
    assert r['conditional_p']==p['main_conservative']['exact_family_signflip_two_sided_p'] and r['holm_p']==p['main_conservative']['holm_adjusted_p_three_version_pairs']
assert (R/'website/data/macro-patterns.png').read_bytes()==(D/'macro-patterns.png').read_bytes()
assert set(payload['buckets'])=={'quantitative','qualitative','combined'} and {k:len(v) for k,v in payload['buckets'].items()}=={'quantitative':4,'qualitative':3,'combined':3}
print('Macro checks passed: unchanged input hashes, exact rational family effects/p-values, common support, CSV contributions and published payload.')

manifest=json.loads((D/"artifact-manifest.json").read_text())
for r in manifest["files"]:
    assert hashlib.sha256((R/r["path"]).read_bytes()).hexdigest()==r["sha256"],r["path"]
print("Macro report artifacts and analysis source hashes passed.")
