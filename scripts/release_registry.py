"""Maintain an active benchmark catalog and preserve every archived candidate decision."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
RELEASE='0.9'
def read(p):return json.loads((R/p).read_text())
def dump(p,o):p=R/p;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def main():
 c=read('registry/catalog.json');history=R/'registry/catalog-history/v04-114.json'
 if not history.exists():dump('registry/catalog-history/v04-114.json',c);dump('registry/catalog-history/v04-admission-decisions.json',read('registry/admission-decisions.json'));dump('registry/catalog-history/v04-current-best.json',read('registry/current-best.json'))
 historical=json.loads(history.read_text());all_entries={e['id']:e for e in historical['entries']}
 for e in c['entries']:all_entries[e['id']]=e
 audit=read('literature/active-pruning-v05.json');removals={e['benchmark_id']:e for e in audit['entries'] if e['decision']=='REMOVE_ACTIVE'}
 extra={
 'H03':('Unresolved original dataset rights; original Nakanishi data are downloadable but author repository and MOABB/NEMAR metadata provide no verified data license.','Obtain explicit original data permission or select a separately licensed SSVEP release.','literature/source-verification-v05-ssvep.json'),
 'I01':('Algonauts original test responses require remote challenge scoring and data access steps; no locally verifiable held-out target release for this protocol. Archived from the runnable catalog, not declared scientifically invalid.','Complete authorized access and official scoring contract, or define a licensed public-response split with explicit deviation.','literature/admission-v04-electrical.json'),
 'I02':('NSD requires a data-access agreement; the required access process has not been completed. Removed from the active local execution list until access is established.','User-authorized source access and a frozen stimulus/subject split with neural labels.','literature/admission-v04-electrical.json'),
 'I05':('fastMRI brain access requires an investigator application/data agreement; no credentialed acquisition is available in this release.','Complete authorized access and pin brain release,subject split and reconstruction scorer.','literature/admission-v04-electrical.json')}
 for t,(reason,requirement,source) in extra.items():removals[t]=dict(benchmark_id=t,decision='REMOVE_ACTIVE',reason=reason,reactivation_requirements=requirement,evidence_file=source,source_urls=all_entries[t]['source_urls'],reviewed_on='2026-10-30',review_depth='Source-specific access/rights screen, no data acquisition claim',preserve_evidence_archive=True)
 additions={
 'B01':dict(executed_slice='Blind unsupervised sorting of one10second32channel MEArec simulation; official unit/event scorer',resource='Standard SpikeInterface/MEArec fixture; MountainSort5 reference',data='Simulated filtered extracellular voltage32kHz,32channels; hidden generated spike events',ground_truth='Known simulation spike events and neuron IDs; not paired biological truth',source_urls=['https://gin.g-node.org/NeuralEnsemble/ephy_testing_data','https://spikeinterface.readthedocs.io/en/0.96.1/modules/comparison/plot_3_compare_sorter_with_ground_truth.html','https://github.com/flatironinstitute/mountainsort5'],admission_evidence_file='literature/admission-v05-extracellular.json',recommended_metrics='Mean GT-unit accuracy/Jaccard; precision/recall and redundant/extra-unit diagnostics',recommended_split='One scored unsupervised recording; no independent recording-generalization claim',limitations='Short stationary public simulation, no drift/real paired/animal generalization. Extra unit diagnostics required.'),
 'G01':dict(executed_slice='FALCON M2 custom cross-day finger-velocity decoding:1169train/754testtrials,96causalfeatures,twooutputs,one monkey',resource='FALCON M2 public calibration NWBs; custom chronological split',source_urls=['https://dandiarchive.org/dandiset/000953','https://github.com/snel-repo/falcon-challenge'],admission_evidence_file='literature/admission-v05-bci.json',recommended_metrics='Variance-weighted R² and perdayR², native velocityAU',recommended_split='Oct19/20training;Oct27/28heldout; no minival or official FALCONscore',limitations='One monkey,two testdays; fixed causal features but no closed-loop/online latency evaluation. Full sourceSHAreported,partial extractedbufferhashesverified.'),
 'H02':dict(executed_slice='Brain Invaders2012 calibration runs: 15 training and10 held-out people; 11,481/7,663 epochs,16 EEG channels; equal-person ROC-AUC.',resource='Brain Invaders2012 v3 / Zenodo2649069; custom subject-held-out ERP diagnostic',dataset_group='Brain Invaders2012',executed_source_deviation='The earlier BNCI2014_008 proposal remains unrun; this is a separately licensed alternate ERP source.',review_depth='All25 original archives checksum-verified; MAT/CSV markers independently compared, grouped scorer fixtures and frozen model procedure documented',data='Stimulus-locked16channel EEG epochs,128Hz,0–1s afterflash; EEG only, groundFz removed',ground_truth='Original all-flash/target event markers; higher score denotes target',source_urls=['https://zenodo.org/records/2649069','https://arxiv.org/abs/1905.05182','https://github.com/plcrodrigues/py.BI.EEG.2012-GIPSA','https://pyriemann.readthedocs.io/en/latest/auto_examples/biosignal-erp/plot_classify_EEG_tangentspace.html'],admission_evidence_file='experiments/H02/protocol.md',recommended_metrics='Frozen primary: equal-person ROC-AUC over10held-out people; pooled AUC secondary',recommended_split='People01–15 train,16–25 test; calibration runs only; training group IDs passed to all methods',limitations='One public source/fixedIDsplit, offline filtering and overlapping trials. No cross-lab,online control,currentSOTA or matched-total-effort claim.'),
 'H08':dict(executed_slice='SleepEDF fixed20:00–08:00firstnightwindows;5train/3heldoutpeople,100HzFpz-Cz;fiveclassstaging',resource='Sleep-EDF Expanded1.0.0; custom subject-held-out diagnostic with YASA checkpoint',data='Raw EEG Fpz-Cz,1440consecutive30second epochs/night',ground_truth='Independent technician R&K stages; stages3/4merged,unknown/movement excluded',source_urls=['https://physionet.org/content/sleep-edfx/1.0.0/','https://doi.org/10.13026/C2X676','https://doi.org/10.7554/eLife.70092','https://github.com/raphaelvallat/yasa_classifier'],admission_evidence_file='experiments/H08/protocol.md',recommended_metrics='Pooled fiveclassmacroF1,accuracy,balancedaccuracy,pernightmacroF1',recommended_split='FirstnightSC400–404train,SC405–407test;fixedclockwindowwithoutlabel-basedcrop',limitations='Three testpeople;singlederivation;customclockwindow not officialSleepEDF20protocol;YASANSRRpretraining differs from five targettrainingnights.'),
 'J08':dict(executed_slice='SynAPSeg2Dpuncta instances:27trainingfields,1262crops;twoheldoutwholefields×fiveexpertmasks;archivedStarDistreference',resource='SynAPSeg Zenodo18988899; 2D multi-rater instance-segmentation slice',data='Normalized microscopy intensities and known training annotation ROI/geometry masks',ground_truth='Five independent human instance annotations per held-out field; no majority oracle',source_urls=['https://zenodo.org/records/18988899','https://doi.org/10.1371/journal.pcbi.1014571'],admission_evidence_file='experiments/J08/protocol.md',recommended_metrics='Equal image/rater instanceF1 atIoU≥0.5; Hungarian objectmatching',recommended_split='All27released2Dtrainingfields vs both official2Dbenchmarkfields; crop correlations preserved',limitations='Only two testfields and unresolved animal identities. Archived StarDist optimization history differs; no inference timing or currentSOTAclaim.')}
 if (R/'registry/execution-overrides.json').exists():additions.update(read('registry/execution-overrides.json'))
 readable_slices={
 'A09':'CalMS21 Task 1: processed pose context at 3 Hz; 70 training and 19 test recordings.',
 'A14':'Rat7M: six-landmark, 31-frame windows with an artificial seven-frame HeadF gap; three training and two test rats.',
 'B01':'Blind unsupervised spike sorting of one 10-second, 32-channel stationary MEArec simulation; official unit/event matching.',
 'C05':'Spikefinder: calcium-to-spike inference on five preparations; median 40 ms correlation per preparation.',
 'D02':'One Allen cell: four training and two test negative-current sweeps; 500 Hz passive voltage interpolation.',
 'E01':'Neural Latents Benchmark: MC_Maze_Small, Area2_Bump and DMFC_RSG; held-in to held-out neuron readout using unchanged generated programs.',
 'F04':'Goldin 2022 retina: 3,160 training images and 30 test images repeated 30 times; 41 neurons, one preparation.',
 'G01':'FALCON M2 custom cross-day decoding: 1,169 training and 754 test trials, 96 causal features, two finger-velocity outputs, one monkey.',
 'H01':'PhysioNet motor imagery: five training and three held-out people; 225 training and 135 test epochs.',
 'H08':'Sleep-EDF first nights, fixed 20:00–08:00 windows: five training and three held-out people; 100 Hz Fpz-Cz EEG, five sleep stages.',
 'H16':'EEGdenoiseNet: 2,000 training and 600 test clean-plus-EOG mixtures, with disjoint source components.',
 'I07':'FRESH optical-density tapping classification: seven training and three test people; condition and session remain confounded.',
 'I10':'MRIQC: 600 ABIDE training scans and 265 DS030 test scans; 68 numeric quality metrics and rater-1 exclusion labels.',
 'J08':'SynAPSeg 2D puncta: 27 training fields yielding 1,262 crops; two held-out whole fields, five expert masks each; archived StarDist reference.',
 'K01':'Allen mouse electrophysiology: 11 features predict spiny/aspiny morphology; donor-disjoint 1,356 training and 457 test cells.',
 'L04':'One rat place cell: 20 ms spike counts predicted from position and velocity; chronological 60/40 split with a one-second gap.',
 'M04':'Synthetic two-choice Q-learning agents: recover learning rate and inverse temperature from choices and rewards.',
 'N05':'One real legacy Allen NWB file, shared with D02: extract 61 deterministic fields covering six sweeps.'}
 for t,text in readable_slices.items():
  if t in additions:additions[t]['executed_slice']=text
  else:all_entries[t]['executed_slice']=text
 for t,fields in additions.items():
  e=all_entries[t];urls=fields.pop('source_urls');e.update(fields);e['source_urls']=list(dict.fromkeys(e['source_urls']+urls));e['verification']='Actual acquired/extracted source arrays, frozen protocol, submitted programs and prediction/scorer artifacts; exact scope in experiments/'+t;e['current_best_status']='not verified; named matched specialist/reference evidence retained separately'
 measured=set()
 for p in (R/'results').glob('*.json'):
  rows=json.loads(p.read_text())
  if isinstance(rows,list) and {r.get('model') for r in rows}>={'gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol'}:measured.add(p.stem)
 assert not measured & set(removals),'Cannot prune measured failures or poor results'
 exclusions=[]
 for t,d in sorted(removals.items()):
  e=all_entries[t];exclusions.append(dict(id=t,resource=e['resource'],task=e['task'],family_code=e['family_code'],reason=d['reason'],reactivation_requirements=d['reactivation_requirements'],source_urls=d.get('source_urls',e['source_urls']),evidence_file=d['evidence_file'],review_depth=d.get('review_depth','Bounded primary-source assessment'),date='2026-10-30',historical_card=f'benchmarks/{t[0]}/{t}',permanent_rejection=False))
 active=[];decisions=[]
 for t,e in sorted(all_entries.items()):
  if t in removals:continue
  if t in measured:e['execution_admission']='measured';e['execution_status']='measured exploratory slice'
  if t in additions:e['admission_reason']='Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.'
  e['active']=True;active.append(e);decisions.append(dict(benchmark_id=t,decision=e['execution_admission'],reason=e['admission_reason'],date=e.get('execution_date','2026-10-30'),evidence_file=e['admission_evidence_file'],source_urls=e['source_urls'],review_depth=e.get('review_depth','Actual source preparation plus per-task documented checks')))
  folder=R/f'benchmarks/{t[0]}/{t}'
  for name in ['README.md','worklog.md']:
   p=folder/name;text=p.read_text().split('\n## v0.5 execution status\n')[0].split('\n## Current admission and execution\n')[0]
   if name=='README.md':
    text=re.sub(r'\*\*Resource:\*\*[^\n]*','**Resource:** '+e['resource'],text)
    text=re.sub(r'\*\*State:\*\*[^\n]*','**State:** '+e['execution_admission']+'. Current status for this exact task-resource slice; current global best remains unverified.',text)
    text=re.sub(r'Input: [^\n]*','Input: '+e['data'],text)
    text=re.sub(r'Target/ground truth: [^\n]*','Target/ground truth: '+e['ground_truth'],text)
    if t in measured:
     current='## Execution and performance\n\n**Executed slice:** '+e.get('executed_slice',e['task'])+'\n\n[Frozen protocol and artifacts](../../../experiments/'+t+'). [Measured scores and references](../../../results/'+t+'.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.\n\n'
     if t=='H02':current+='[Separate three-generation follow-up](../../../experiments/H02/replication-v1/results.md); repeated attempts are excluded from first-submission macro totals.\n\n'
     text=re.sub(r'## Execution and performance\n.*?(?=## Limitations)',lambda m:current,text,flags=re.S)
     text=re.sub(r'## Limitations\n.*?(?=## Sources)',lambda m:'## Limitations\n\n'+e['limitations']+'\n\n',text,flags=re.S)
    text=text.replace('Specialist candidates:','Mapped specialist candidates (not all evaluated):')
    text=text.replace('## v0.4 admission and execution','## Historical v0.4 admission and execution')
    if '## Sources' in text:
     before,after=text.split('## Sources',1);history='## Historical v0.4 admission and execution'
     tail=history+after.split(history,1)[1] if history in after else ''
     text=before+'## Sources\n\n'+''.join('- ['+u+']('+u+')\n' for u in e['source_urls'])+'\nSource associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.\n\n'+tail
   text+='\n## Current admission and execution\n\nPreview '+RELEASE+': '+e['execution_admission']+'. '+e['admission_reason']+'\n\n[Admission/source evidence](../../../'+e['admission_evidence_file']+').'
   if t in measured:text+=' [Actual protocol/worklog](../../../experiments/'+t+'). [Task measurements](../../../results/'+t+'.json).'
   p.write_text(text+'\n')
  if t in measured:
   method=folder/'methods.md';text=method.read_text().split('\n## Current executed protocol\n')[0];text=text.replace('No experiment admitted yet.','An explicitly scoped exploratory slice has been executed; broader proposed operations above remain separate.')
   text+='\n## Current executed protocol\n\nPreview '+RELEASE+': '+e.get('executed_slice',e['task'])+'\n\n[Actual frozen contract and implementation](../../../experiments/'+t+'). [Measured method/reference records](../../../results/'+t+'.json). The proposed checklist above does not imply every broader operation or specialist was evaluated.\n';method.write_text(text)
  dump(f'benchmarks/{t[0]}/{t}/references.json',dict(benchmark_id=t,source_urls=e['source_urls'],admission_evidence=e['admission_evidence_file']))
  p=folder/'data.json';o=json.loads(p.read_text());o['current_execution']=dict(release=RELEASE,status=e['execution_admission'],slice=e.get('executed_slice'),evidence=e['admission_evidence_file']);o['input']=e['data'];o['ground_truth']=e['ground_truth'];o['sources']=e['source_urls']
  if t in measured:
   manifest=R/f'data/manifests/{t}.json'
   if not manifest.exists():manifest=R/f'experiments/{t}/data-manifest.json'
   if not manifest.exists() and t=='C05':manifest=R/'data/manifests/spikefinder.json'
   if not manifest.exists() and t=='M04':manifest=R/'data/manifests/cognitive.json'
   if manifest.exists():o['local_manifest']=str(manifest.relative_to(R))
   o['license_status']='Actual executed-source terms recorded in linked manifest/protocol; no blanket license for all mapped resources'
   o['executed_slice']=e.get('executed_slice',e['task'])
  p.write_text(json.dumps(o,indent=2)+'\n')
 c['entries']=active;c['release']=RELEASE;c['historical_mapped_entries']=len(all_entries);c['archived_candidates']=len(exclusions);c['scope']='Active candidate catalog plus measured custom slices; excluded proposals/unresolved-access resources preserved in versioned evidence archive. Neither catalog count nor category coverage proves completeness.'
 dump('registry/catalog.json',c);dump('registry/admission-decisions.json',decisions);dump('registry/excluded-candidates.json',exclusions)
 for fam in c['families']:
  text='# '+fam['name']+'\n\n[Project](../../README.md) · [Coverage](../../docs/coverage-matrix.md)\n\n'+fam['data_types']+'\n\n'
  for e in active:
   if e['family_code']==fam['code']:text+='- ['+e['id']+' — '+e['task']+']('+e['id']+'/README.md) · '+e['execution_admission']+'\n'
  (R/f'benchmarks/{fam["code"]}/README.md').write_text(text+'\nArchived candidates remain in the [exclusion ledger](../../registry/excluded-candidates.json).\n')
 current={v['benchmark_id']:v for v in read('registry/current-best.json')}
 for e in active:
  if e['id'] in current:current[e['id']]['source_urls']=e['source_urls']
 dump('registry/current-best.json',[current[e['id']] for e in active if e['id']in current])
 sources=read('literature/sources.json');known={s['url']:s for s in sources}
 for e in active:
  for u in e['source_urls']:
   if u not in known:known[u]=dict(id='S'+hashlib.sha256(u.encode()).hexdigest()[:10],url=u,benchmark_ids=[],evidence='See task-specific verification depth; source mapping does not imply full-text/acquisition audit',reviewed_on='2026-10-30')
   if e['id']not in known[u]['benchmark_ids']:known[u]['benchmark_ids'].append(e['id'])
 dump('literature/sources.json',list(known.values()));print('Active',len(active),'archived',len(exclusions),'measured',len(measured),'sourceURLs',len(known))
if __name__=='__main__':main()
