"""Normalize bounded screening evidence and connect every card to its actual execution."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def main():
 c=json.loads((R/'registry/catalog.json').read_text());byid={};
 for p in sorted((R/'literature').glob('admission-v04-*.json')):
  o=json.loads(p.read_text());rows=o.get('entries',o.get('decisions',[]))
  for row in rows:
   t=row.get('benchmark_id',row.get('id'));d=dict(row);d['evidence_file']=str(p.relative_to(R));d['raw_decision']=d.get('decision',d.get('admission',d.get('status')))
   if t not in byid or t=='F04' and 'cell-workflow'in p.name:byid[t]=d
 assert set(byid)=={e['id'] for e in c['entries']},set(e['id'] for e in c['entries'])-set(byid)
 measured={p.stem for p in (R/'results').glob('*.json')};decisions=[]
 extra={'H01':['https://physionet.org/content/eegmmidb/1.0.0/'],'I07':['https://openneuro.org/datasets/ds005963/versions/1.0.0','https://doi.org/10.1038/s42003-025-08412-1'],'H16':['https://github.com/ncclabsustech/EEGdenoiseNet'],'A09':['https://doi.org/10.17617/3.3R0QYI'],'A14':['https://zenodo.org/records/18405201'],'E01':['https://dandiarchive.org/dandiset/000140/0.220113.0408','https://github.com/neurallatents/nlb_tools'],'F04':['https://doi.org/10.5281/zenodo.6868362','https://huggingface.co/datasets/open-retina/open-retina'],'L04':['https://mark-kramer.github.io/Case-Studies-Python/09.html','https://github.com/Mark-Kramer/Case-Studies-Python'],'N05':['https://alleninstitute.github.io/AllenSDK/cell_types.html'],'I10':['https://doi.org/10.1371/journal.pone.0184661']}
 slices={'A09':'CalMS21 Task1,3Hz centers and seven pose offsets,19 test recordings','A14':'Rat7M six-landmark31frame windows;7frame artificialHeadF gap;heldout rats4–5','D02':'One Allen cell,4train/2test negative-current sweeps;500Hz passive voltage-deflection interpolation','E01':'NLBMC_Maze_Small99train/100test movement-aligned trials;20ms supervised107→35neuron readout','F04':'Goldin2022 retina,3160trainimages/30testimages×30repeats,41neurons,18×18imagefeatures','H01':'PhysioNet motorimagery;5train/3heldout subjects,225/135epochs','H16':'EEGdenoiseNet clean+EOG2000train/600test component-disjoint mixtures','I07':'FRESH opticaldensity tapping condition,7train/3test subjects;condition/session confounded','I10':'MRIQC600ABIDEtrain/265DS030test,68numeric IQMs,rater1exclude labels','K01':'Allen mouse ephys11features→spiny/aspiny morphology,donor-disjoint1356/457cells','L04':'One real rat placecell,20mscounts,chronological60/40split with1sgap;position/velocity','N05':'One real legacyNWB file sharedD02;61deterministic fields,6sweeps'}
 for e in c['entries']:
  t=e['id'];d=byid[t];raw=d['raw_decision'];status='measured' if t in measured else 'deferred' if raw=='deferred' else 'candidate_pending_validation'
  e['execution_admission']=status;e['admission_reason']=d['reason'];e['execution_status']='measured exploratory slice' if status=='measured' else 'not evaluated';e['admission_evidence_file']=d['evidence_file'];e['review_depth']=d.get('check_type',d.get('review_scope','Bounded admission assessment; actual access and license facts in linked evidence'));e['source_urls']=list(dict.fromkeys(e['source_urls']+d.get('source_urls',[])+d.get('primary_sources',[])+extra.get(t,[])))
  if t in slices:e['executed_slice']=slices[t];e['verification']='Acquired data, frozen custom-slice protocol, unchanged model submissions, scored predictions and execution/failure records available; see experiments/'+t
  if t=='L04':e['original_mapping_preserved']='Originally proposed synthetic GLM construction; new execution is real-data encoding only';e['data']='Real rat hippocampal spike counts and position/velocity';e['resource']='Kramer real place-cell case study; custom count-encoding diagnostic';e['ground_truth']='Measured extracellular spike counts';e['recommended_metrics']='Held-out Poisson bits/spike relative to training-mean null; goodness-of-fit/coverage remains unexecuted';e['recommended_split']='Chronological split with gap; one cell/preparation';e['limitations']='No known generating parameters; no animal generalization or completed time-rescaling calibration'
  if t=='F04':e['executed_source_deviation']='Goldin2022 reusable retina release is the measured slice; other listed CRCNS datasets not thereby evaluated'
  ds=dict(benchmark_id=t,decision=status,reason=d['reason'],date='2026-10-30',source_screen_decision=raw,evidence_file=d['evidence_file'],source_urls=e['source_urls'],review_depth=e['review_depth'],permanent_rejection=False);decisions.append(ds)
  folder=R/f'benchmarks/{e["family_code"]}/{t}'
  for name in ['README.md','worklog.md']:
   p=folder/name;s=p.read_text();marker='\n## v0.4 admission and execution\n';s=s.split(marker)[0]
   s+=marker+'\nDecision: **'+status+'** (2026-10-30). '+d['reason']+'\n\n[Source-linked admission evidence](../../../'+d['evidence_file']+'). '
   if status=='measured':s+='[Actual protocol and artifacts](../../../experiments/'+t+'). [Central task results](../../../results/'+t+'.json).\n'
   else:s+='This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.\n'
   p.write_text(s)
  p=folder/'data.json';data=json.loads(p.read_text());data['v04_admission']=ds
  if t in slices:data['executed_slice']=slices[t]
  dump(p,data);dump(folder/'references.json',dict(benchmark_id=t,source_urls=e['source_urls'],admission_evidence=d['evidence_file']))
 for fam in c['families']:
  text='# '+fam['name']+'\n\n[Taxonomy](../../docs/taxonomy.md) · [Project](../../README.md)\n\n'+fam['data_types']+'\n\nOperations: '+fam['tasks']+'\n\n'
  for entry in c['entries']:
   if entry['family_code']==fam['code']:text+='- ['+entry['id']+' — '+entry['task']+']('+entry['id']+'/README.md) · '+entry['execution_admission']+'\n'
  (R/f'benchmarks/{fam["code"]}/README.md').write_text(text)
 c['release']='0.4';c['verification']='Every entry has a bounded admission assessment; review depth varies and inherited URLs were not all refetched. Only measured slices have acquired/scored data. Exhaustive literature and currentbest are not established.'
 dump(R/'registry/catalog.json',c);dump(R/'registry/admission-decisions.json',decisions)
 sources=json.loads((R/'literature/sources.json').read_text());known={s['url']:s for s in sources}
 for e in c['entries']:
  for u in e['source_urls']:
   if u not in known:known[u]=dict(id='S'+hashlib.sha256(u.encode()).hexdigest()[:10],url=u,benchmark_ids=[],evidence='v0.4 bounded source/admission assessment; actual verification depth in task evidence',reviewed_on='2026-10-30')
   if e['id'] not in known[u]['benchmark_ids']:known[u]['benchmark_ids'].append(e['id'])
 dump(R/'literature/sources.json',list(known.values()))
 print('All',len(decisions),'entries screened:',{s:sum(d['decision']==s for d in decisions) for s in ['measured','candidate_pending_validation','deferred']},'sourceURLs',len(known))
if __name__=='__main__':main()
