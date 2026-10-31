"""Retrospective panel analysis. Reads immutable scores; never fits models or edits results.

All primary statistics are dimensionless directions/ranks, with slices -> tasks ->
families. Resampling describes this convenience panel's composition sensitivity,
not biological, generation or provider uncertainty. Exact sign flips require a
symmetric independent-family null that this observational panel cannot establish.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv, hashlib, itertools, json, math
import numpy as np
from scipy.stats import rankdata

R = Path(__file__).resolve().parents[1]
D = R / 'analysis/macro-patterns'
MODELS = ['gpt-5.6-sol', 'gpt-6-sol', 'gpt-6.1-sol']
PAIRS = list(itertools.combinations(MODELS, 2))
OBS_EXCLUDE = {'B01', 'B03', 'L06', 'M04', 'N05', 'B08'}
ALL_EXCLUDE = {'M04', 'N05', 'B08'}
TOL = 1e-9
SEED = 20261031

def read(p): return json.loads((R / p).read_text())
def digest(p): return hashlib.sha256((R / p).read_bytes()).hexdigest()
def valid(r): return bool(r and r.get('status') == 'measured' and isinstance(r.get('score'), (int, float)) and math.isfinite(r['score']))
def sign(x): return 1 if x > TOL else -1 if x < -TOL else 0
def mean(xs): return float(np.mean(xs)) if len(xs) else None
def dump(p, x): (D / p).write_text(json.dumps(x, indent=2, allow_nan=False) + '\n')
def csvout(p, rows):
    if not rows: return
    with (D / p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)

def grouped(rows):
    ts = defaultdict(list)
    for r in rows: ts[r['benchmark_id']].append(r)
    tasks = []
    for t, rs in sorted(ts.items()):
        tasks.append(dict(benchmark_id=t, family_code=t[0], n_slices=len(rs),
                          win_fraction=mean([r['outcome'] == 'win' for r in rs]),
                          loss_fraction=mean([r['outcome'] == 'loss' for r in rs]),
                          tie_fraction=mean([r['outcome'] == 'tie' for r in rs]),
                          failure_fraction=mean([r['outcome'] == 'failed_or_missing' for r in rs]),
                          net_direction=mean([r['signed_direction'] for r in rs])))
    fs = defaultdict(list)
    for t in tasks: fs[t['family_code']].append(t)
    families = [dict(family_code=f, n_tasks=len(v), **{k:mean([r[k] for r in v]) for k in
                ['win_fraction','loss_fraction','tie_fraction','failure_fraction','net_direction']}) for f,v in sorted(fs.items())]
    return dict(n_tasks=len(tasks), n_families=len(families), n_slices=len(rows),
                slice_counts=dict(Counter(r['outcome'] for r in rows)),
                task_equal_win_fraction=mean([r['win_fraction'] for r in tasks]),
                family_equal_win_fraction=mean([r['win_fraction'] for r in families]),
                family_equal_net_direction=mean([r['net_direction'] for r in families]),
                tasks=tasks, families=families)

def family_diagnostics(g):
    """Exact two-sided sign-flip diagnostic and finite-panel composition sensitivity."""
    a = np.array([r['net_direction'] for r in g['families']]); n = len(a)
    signs = np.array(list(itertools.product([-1, 1], repeat=n)), dtype=float)
    null = signs @ a / n
    obs = float(a.mean())
    p = float(np.mean(np.abs(null) >= abs(obs)-1e-12))
    rng = np.random.default_rng(SEED)
    wi = np.array([r['win_fraction'] for r in g['families']])
    sampled = rng.integers(0, n, size=(20000, n))
    boot = wi[sampled].mean(axis=1)
    loo = [{'omitted_family':g['families'][i]['family_code'],
            'family_equal_win_fraction':float(np.delete(wi,i).mean()),
            'family_equal_net_direction':float(np.delete(a,i).mean())} for i in range(n)]
    return dict(exact_family_signflip_two_sided_p=p, enumerated_sign_patterns=2**n,
                family_composition_bootstrap_percentile95=list(map(float,np.quantile(boot,[.025,.975]))),
                bootstrap_replicates=20000, seed=SEED,
                leave_one_family_out=loo,
                leave_one_family_win_range=[min(x['family_equal_win_fraction'] for x in loo),max(x['family_equal_win_fraction'] for x in loo)],
                assumptions='Conditional sign symmetry and independent family contrasts; neither random sampling nor randomized model assignment occurred. Diagnostic p-values do not prove general neuroscience progress. Bootstrap intervals reflect resampled benchmark families only.')

def holm(ps):
    order = np.argsort(ps); adjusted = [None]*len(ps); running=0.
    for k,i in enumerate(order):
        running=max(running,min(1.,(len(ps)-k)*ps[i])); adjusted[i]=running
    return adjusted

def main():
    D.mkdir(parents=True, exist_ok=True)
    files=['results/measurements.jsonl','analysis/summary.json','registry/catalog.json']
    hashes={p:digest(p) for p in files}
    records=[json.loads(x) for x in (R/files[0]).read_text().splitlines()]
    summary=read('analysis/summary.json');catalog=read('registry/catalog.json')
    lookup={(r['benchmark_id'],r['slice_id'],r['model']):r for r in records}
    keys=sorted({(r['benchmark_id'],r['slice_id']) for r in records if r['model'] in MODELS})
    task_names={e['id']:e['task'] for e in catalog['entries']}
    paired=[]; slice_rows=[]
    for older,newer in PAIRS:
        variants={}
        for scope,exclude in [('observed',OBS_EXCLUDE),('synthetic_inclusive',ALL_EXCLUDE)]:
            for compliance in ['all_submissions','strict']:
                for missing in ['denominator','complete_cases','failure_penalized']:
                    rs=[]
                    for t,sid in keys:
                        if t in exclude:continue
                        a=lookup.get((t,sid,older));b=lookup.get((t,sid,newer))
                        if compliance=='strict' and not all(r and r['strict_format_compliant'] for r in [a,b]):continue
                        av,bv=valid(a),valid(b)
                        if not(av and bv) and missing=='complete_cases':continue
                        v=sign((b['score']-a['score'])*(1 if b['direction']=='higher' else -1)) if av and bv else 0
                        outcome='win' if v==1 else 'loss' if v==-1 else 'tie' if av and bv else 'failed_or_missing'
                        if missing=='failure_penalized' and av!=bv:
                            v=1 if bv else -1;outcome='win' if bv else 'loss'
                        r=dict(benchmark_id=t,slice_id=sid,older=older,newer=newer,outcome=outcome,signed_direction=v,
                               older_valid=av,newer_valid=bv,metric=(b or a).get('metric'),direction=(b or a).get('direction'),older_score=a.get('score') if av else None,newer_score=b.get('score') if bv else None,raw_delta=(b['score']-a['score']) if av and bv else None)
                        rs.append(r)
                        if scope=='observed' and compliance=='all_submissions' and missing=='denominator':slice_rows.append(r)
                    name=f'{scope}__{compliance}__{missing}';g=grouped(rs);variants[name]=g
                    if scope=='observed' and compliance=='all_submissions' and missing in ['denominator','failure_penalized']:g.update(family_diagnostics(g))
        primary=variants['observed__all_submissions__denominator']
        old=next(x for x in summary['paired_macro_summaries'] if x['older']==older and x['newer']==newer)['observed_data']
        assert abs(primary['family_equal_win_fraction']-old['family_equal_win_fraction'])<1e-12
        paired.append(dict(older=older,newer=newer,descriptive_denominator=primary,variants=variants))
    adj=holm([p['descriptive_denominator']['exact_family_signflip_two_sided_p'] for p in paired])
    for p,q in zip(paired,adj):p['descriptive_denominator']['holm_adjusted_p_three_version_pairs']=q
    conservative_ps=[p['variants']['observed__all_submissions__failure_penalized']['exact_family_signflip_two_sided_p'] for p in paired]
    for p,q in zip(paired,holm(conservative_ps)):
        p['main_conservative']=p['variants']['observed__all_submissions__failure_penalized']
        p['main_conservative']['holm_adjusted_p_three_version_pairs']=q
    common_keys={(t,sid) for t,sid in keys if t not in OBS_EXCLUDE and all(valid(lookup.get((t,sid,m))) and lookup[(t,sid,m)]['strict_format_compliant'] for m in MODELS)}
    for p in paired:
        rs=[r for r in slice_rows if r['older']==p['older'] and r['newer']==p['newer'] and (r['benchmark_id'],r['slice_id']) in common_keys]
        p['common_three_model_strict']=grouped(rs)

    # Preference indicators do not average unrelated native score magnitudes.
    task_rows=[]
    for r in slice_rows:r['analysis_policy']='descriptive_denominator_missing_as_neutral'
    for p in paired:
        for t in p['descriptive_denominator']['tasks']:task_rows.append(dict(older=p['older'],newer=p['newer'],task=task_names[t['benchmark_id']],analysis_policy='descriptive_denominator_missing_as_neutral',**t))
    csvout('paired-slices.csv',slice_rows);csvout('paired-tasks.csv',task_rows)
    family_rows=[dict(older=p['older'],newer=p['newer'],analysis_policy='descriptive_denominator_missing_as_neutral',**f) for p in paired for f in p['descriptive_denominator']['families']]
    csvout('paired-families.csv',family_rows)
    csvout('main-conservative-tasks.csv',[dict(older=p['older'],newer=p['newer'],analysis_policy='newer_only_failure_loss',**t) for p in paired for t in p['main_conservative']['tasks']])
    csvout('main-conservative-families.csv',[dict(older=p['older'],newer=p['newer'],analysis_policy='newer_only_failure_loss',**t) for p in paired for t in p['main_conservative']['families']])
    conservative_slices=[]
    for source in slice_rows:
        r=dict(source);r['analysis_policy']='newer_only_failure_loss'
        if r['older_valid'] != r['newer_valid']:
            r['signed_direction']=1 if r['newer_valid'] else -1;r['outcome']='win' if r['newer_valid'] else 'loss'
        conservative_slices.append(r)
    csvout('main-conservative-slices.csv',conservative_slices)

    # Descriptive reference strata. Keep failures, one task's slices together.
    ref_rows=[];ref_summaries=[]
    for model in MODELS:
        for ref in summary['reference_envelopes']:
            t,sid=ref['benchmark_id'],ref['slice_id']
            if t in OBS_EXCLUDE:continue
            r=lookup.get((t,sid,model));v=sign((r['score']-ref['score'])*(1 if ref['direction']=='higher' else -1)) if valid(r) else 0
            ref_rows.append(dict(benchmark_id=t,slice_id=sid,model=model,reference=ref['model'],reference_class=ref['reference_class'],
                                 outcome='win' if v==1 else 'loss' if v==-1 else 'tie' if valid(r) else 'failed_or_missing',
                                 signed_direction=v,strict=bool(r and r['strict_format_compliant']),metric=ref['metric'],direction=ref['direction'],model_score=r.get('score') if valid(r) else None,reference_score=ref['score'],raw_delta=r['score']-ref['score'] if valid(r) else None))
        for cls in sorted({r['reference_class'] for r in ref_rows if r['model']==model}):
            rs=[r for r in ref_rows if r['model']==model and r['reference_class']==cls]
            ref_summaries.append(dict(model=model,reference_class=cls,**grouped(rs),strict=grouped([r for r in rs if r['strict']])))
    csvout('reference-slices.csv',ref_rows)

    # Complete-case within-slice three-model ranks, averaged task then family.
    rank_rows=[];rank_summaries=[];monotonic=[]
    for t,sid in keys:
        if t in OBS_EXCLUDE:continue
        rs=[lookup.get((t,sid,m)) for m in MODELS]
        if not all(valid(r) for r in rs):continue
        # rankdata's exact equality convention is separate from directional 1e-9 ties.
        values=np.array([r['score'] for r in rs])*(1 if rs[0]['direction']=='higher' else -1)
        ranks=rankdata(-values,method='average')
        for m,rank in zip(MODELS,ranks):rank_rows.append(dict(benchmark_id=t,slice_id=sid,model=m,rank=float(rank)))
        monotonic.append(dict(benchmark_id=t,slice_id=sid,
                              monotonic_improvement=bool(sign(values[1]-values[0])>=0 and sign(values[2]-values[1])>=0 and sign(values[2]-values[0])>0),
                              newest_best=bool(values[2]>=max(values)-TOL),
                              newest_worse_than_both=bool(values[2]<min(values[:2])-TOL)))
    for model in MODELS:
        ts=defaultdict(list)
        for r in rank_rows:
            if r['model']==model:ts[r['benchmark_id']].append(r['rank'])
        fs=defaultdict(list)
        for t,v in ts.items():fs[t[0]].append(mean(v))
        rank_summaries.append(dict(model=model,n_tasks=len(ts),n_families=len(fs),n_slices=len([r for r in rank_rows if r['model']==model]),
                                   task_equal_mean_rank=mean([mean(v) for v in ts.values()]),family_equal_mean_rank=mean([mean(v) for v in fs.values()]),
                                   family_ranks={f:mean(v) for f,v in sorted(fs.items())}))
    csvout('three-model-ranks.csv',rank_rows);csvout('monotonic-slices.csv',monotonic)

    # Predeclared/calculated metric sensitivity and source-shift case studies.
    calcium=[]
    for r in read('results/C06.json'):
        if not valid(r):continue
        animals=defaultdict(list)
        for cell in r['cell_results']:animals[str(cell['animal'])].append(cell)
        calcium.append(dict(model=r['model'],pearson=r['score'],
                            relative_count_error=mean([mean([v['relative_error'] for v in cs]) for cs in animals.values()]),
                            signed_relative_count_bias=mean([mean([v['relative_bias'] for v in cs]) for cs in animals.values()])))
    b01=[dict(model=r['model'],primary=r['score'],posthoc_event_f1=r['posthoc_secondary_metrics']['all_event_f1'])
         for r in read('results/B01.json') if valid(r) and r.get('posthoc_secondary_metrics')]
    e06=[dict(model=r['model'],slice_id=r['slice_id'],mse=r['score']) for r in read('results/E06.json') if valid(r)]
    reliability=[dict(model=m,attempts=sum(r['model']==m for r in records),numeric_valid=sum(r['model']==m and valid(r) for r in records),
                      strict_numeric_valid=sum(r['model']==m and valid(r) and r['strict_format_compliant'] for r in records),
                      failed_tasks=[r['benchmark_id'] for r in records if r['model']==m and not valid(r)],
                      overline_slices=[r['benchmark_id']+'/'+r['slice_id'] for r in records if r['model']==m and valid(r) and not r['strict_format_compliant']]) for m in MODELS]
    monotonic_summary=dict(complete_slices=len(monotonic),monotonic_slices=sum(r['monotonic_improvement'] for r in monotonic),
                           newest_best_slices=sum(r['newest_best'] for r in monotonic),newest_worse_than_both_slices=sum(r['newest_worse_than_both'] for r in monotonic),
                           complete_tasks=len({r['benchmark_id'] for r in monotonic}),
                           all_slices_monotonic_tasks=[t for t in sorted({r['benchmark_id'] for r in monotonic}) if all(r['monotonic_improvement'] for r in monotonic if r['benchmark_id']==t)],
                           not_independent='Slices share sources/programs. Counts are descriptive; no binomial slice-independence test.')
    category_patterns=[]
    for p in paired:
        for fam in p['main_conservative']['families']:
            ts=[t for t in p['main_conservative']['tasks'] if t['family_code']==fam['family_code']]
            category_patterns.append(dict(older=p['older'],newer=p['newer'],family_code=fam['family_code'],n_tasks=len(ts),positive_tasks=sum(t['net_direction']>1e-9 for t in ts),negative_tasks=sum(t['net_direction']< -1e-9 for t in ts),neutral_tasks=sum(abs(t['net_direction'])<=1e-9 for t in ts),task_ids=','.join(t['benchmark_id'] for t in ts)))
    csvout('category-signals.csv',category_patterns)
    out=dict(analysis_revision='2026-10-31-v12',measurement_snapshot='0.11',retrospective=True,input_sha256=hashes,
             model_order=MODELS,native_metrics_never_pooled=True,
             scopes=dict(observed_exclusions=sorted(OBS_EXCLUDE),synthetic_inclusive_exclusions=sorted(ALL_EXCLUDE)),
             numerical_tie_tolerance=TOL,category_patterns=category_patterns,pairwise=paired,reference_strata=ref_summaries,ranks=rank_summaries,
             monotonicity=monotonic_summary,reliability=reliability,
             case_studies=dict(C06=calcium,B01=b01,E06=e06),
             uncertainty='One generated program/model/task. Public labels, nonrandom panel, shared sources and unequal references prevent biological or general-model population inference. No fitted scaling law or predictor-of-success regression.',
             multiplicity='Only three observed-scope family sign-flip version diagnostics receive Holm adjustment as one declared retrospective family. Other variants are sensitivity descriptions; reference strata have no significance tests.')
    for p,h in hashes.items():assert digest(p)==h,'Input changed during analysis'
    out['diagnostic_policy']='Main conservative diagnostic scores newer-only numerical failure as loss, older-only failure as win; no numeric score imputed. Historical denominator treatment is separately retained as sensitivity. Three main contrasts Holm-adjusted; no searching for a favorable significance claim.'
    csvout('task-context.csv',[dict(benchmark_id=e['id'],family=e['family_code'],task=e['task'],source_type='fully_synthetic' if e['id'] in ['B01','B03','L06','M04'] else 'deterministic_file' if e['id']=='N05' else 'observed_with_artificial_corruption' if e['id'] in ['A14','H16'] else 'observed',executed_slice=e.get('executed_slice',''),limitations=e['limitations']) for e in catalog['entries'] if e['id'] in {t for t,sid in keys}])
    dump('statistics.json',out)
    write_plot(out)
    print(json.dumps(dict(pairwise=[dict(pair=p['older']+' -> '+p['newer'],win=p['descriptive_denominator']['family_equal_win_fraction'],net=p['main_conservative']['family_equal_net_direction'],p=p['main_conservative']['exact_family_signflip_two_sided_p'],holm=p['main_conservative']['holm_adjusted_p_three_version_pairs'],composition_interval=p['descriptive_denominator']['family_composition_bootstrap_percentile95']) for p in paired],monotonicity=monotonic_summary,ranks=rank_summaries),indent=2))

def write_plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(1,2,figsize=(12,5.3),layout='constrained')
    colors=['#8c78a8','#4c7e92','#b47e42']
    for i,p in enumerate(out['pairwise']):
        g=p['descriptive_denominator'];lo,hi=g['family_composition_bootstrap_percentile95'];v=g['family_equal_win_fraction']
        ax[0].errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=colors[i],capsize=5)
        ax[0].text(v,i+.12,f'{v:.3f}',ha='center',fontsize=9)
    ax[0].set(yticks=range(3),yticklabels=['6 vs 5.6','6.1 vs 5.6','6.1 vs 6'],xlim=(0,1),xlabel='Family-equal directional win fraction',title='Version comparisons: observed-data panel')
    ax[0].set_ylim(-.4,2.5);ax[0].axvline(.5,color='#999',ls=':',lw=1);ax[0].invert_yaxis()
    # 0.5 is a descriptive reference; ties/failures mean it is not a calibrated null.
    classes=['conventional_baseline','conventional_domain_reference','historical_specialist','local_specialist','pretrained_specialist']
    for i,m in enumerate(MODELS):
        vals=[next((r['task_equal_win_fraction'] for r in out['reference_strata'] if r['model']==m and r['reference_class']==c),np.nan) for c in classes]
        ax[1].barh(np.arange(len(classes))+(i-1)*.23,vals,height=.22,color=colors[i],label=m.replace('gpt-','').replace('-sol',' Sol'))
    ax[1].set(yticks=range(len(classes)),yticklabels=['Conventional baseline (12 tasks)','Conventional domain (2)','Archived specialist (4)','Local specialist (5)','Pretrained specialist (1)'],xlim=(0,1),xlabel='Task-equal win fraction within evidence stratum',title='Win fractions differ across reference strata')
    ax[1].invert_yaxis();ax[1].legend(fontsize=8,loc='lower right')
    fig.suptitle('Exploratory patterns across 24 observed-data tasks',fontsize=14,weight='bold')
    fig.text(.5,-.045,'Left: 20,000 family-resampling composition intervals, not biological/generation confidence. Right: unequal tasks/budgets; not a causal reference-class effect. The 0.5 line is descriptive, not a calibrated null.\nNative metric sizes are never averaged. B08 ambiguous contract excluded; fully synthetic and deterministic tasks excluded.',ha='center',fontsize=9)
    fig.savefig(D/'macro-patterns.png',dpi=180,bbox_inches='tight');fig.savefig(D/'macro-patterns.pdf',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
