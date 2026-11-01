"""Preserve repair-v1 round1; seal metadata/runtime corrections before rescoring.

N05 revision2 follows internal HDF5 aliases with cycle protection. B08 only
repeats independent decoding with absolute preexisting dependency paths; no
encoder is repeated and all original common-procedure outputs are preserved.
"""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments/repairs-v1';RESULT=ROOT/'results/repairs-v1.json'
s=importlib.util.spec_from_file_location('repair_round1',ROOT/'scripts/repair_failed.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def env():
 e=dict(os.environ,**old.THREADS)
 e['PYTHONPATH']=os.pathsep.join(str(Path(p).resolve()) for p in e.get('PYTHONPATH','').split(os.pathsep) if p)
 return e
def check(folder):
 spec=json.loads((folder/'run-spec.json').read_text())
 for rel,h in spec['frozen_files'].items():assert sha(ROOT/rel)==h,rel
 return spec

def prepare():
 assert json.loads(RESULT.read_text())['status']=='complete'
 archive=ROOT/'results/repairs-v1/round-1.json';assert not archive.exists();archive.parent.mkdir(exist_ok=True);archive.write_bytes(RESULT.read_bytes())
 folder=BASE/'N05/revision-2';folder.mkdir(exist_ok=False)
 source=ROOT/'experiments/N05/gpt-5.6-sol.json';before=json.loads(source.read_text())['code']
 target='        handle.visititems(visitor)\n        result = {}'
 replacement='''        def visit_paths(group, ancestors):
            address = h5py.h5o.get_info(group.id).addr
            if address in ancestors:
                return
            active = ancestors | {address}
            for name in group:
                link = group.get(name, getlink=True)
                if isinstance(link, h5py.ExternalLink):
                    continue
                try:
                    obj = group[name]
                except (KeyError, OSError):
                    continue
                visitor(obj.name.lstrip("/"), obj)
                if isinstance(obj, h5py.Group):
                    visit_paths(obj, active)
        visit_paths(handle, set())
        result = {}'''
 assert before.count(target)==1;after=before.replace(target,replacement)
 (folder/'gpt-5.6-sol.py').write_text(after)
 (folder/'patch.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='original/gpt-5.6-sol.py',tofile='repairs-v1/N05/revision-2/gpt-5.6-sol.py')))
 rationale='Original object traversal deduplicates aliases. Round1 link traversal ignored internal SoftLinks and did not recursively follow alias groups. Revision2 walks metadata paths, follows internal hard/soft links, refuses external-file links and uses ancestor object addresses to prevent cycles. Existing role/unit/sweep selection and numerical calculations remain unchanged. No expected answers or measured numerical constants added. Original249line noncompliance remains visible; no cosmetic trimming.'
 (folder/'rationale.md').write_text('# N05 repair revision2\n\n'+rationale+'\n')
 files=[source,ROOT/'experiments/N05/run-spec.json',ROOT/'data/cache/N05/fixture.nwb',ROOT/'data/cache/N05/expected.json',ROOT/'data/cache/N05/tolerances.json',ROOT/'scripts/workflow.py',ROOT/'scripts/repair_failed.py',Path(__file__).resolve(),archive]+list(folder.iterdir())
 write(folder/'run-spec.json',dict(track='posthoc-repairs-v1',revision=2,benchmark_id='N05',rationale=rationale,
  original_code_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_code_sha256=hashlib.sha256(after.encode()).hexdigest(),
  timeout_seconds=180,numerical_threads=1,no_test_targets_in_patch_logic=True,no_new_model_calls=True,
  frozen_files={str(p.relative_to(ROOT)):sha(p) for p in files},status='sealed before repaired execution and scoring'))
 folder=BASE/'B08/decode-revision-2';folder.mkdir(exist_ok=False)
 records=[];files=[Path(__file__).resolve(),ROOT/'scripts/repair_failed.py',BASE/'B08/run-spec.json',archive]
 for method in old.METHODS['B08']:
  log=BASE/'B08/execution'/f'{method}.txt'
  row=json.JSONDecoder().raw_decode(log.read_text().lstrip())[0]
  assert row['status']=='measured' and row['method']==method
  payload=ROOT/row['prediction_file'];assert sha(payload)==row['prediction_sha256']
  items=json.loads(payload.read_text());assert len(items)==7
  records.append(row);files.extend([log,payload]);files.extend(ROOT/i['compressed_file'] for i in items)
 programfiles=[BASE/'B08'/(m+'.py') for m in old.MODELS]+[ROOT/'experiments/B08/reference.py']
 files+=programfiles
 write(folder/'common-procedure-results.json',records);files.append(folder/'common-procedure-results.json')
 write(folder/'run-spec.json',dict(track='posthoc-repairs-v1',benchmark_id='B08',revision=2,
  status='sealed before fresh independent decoding and verification',encoder_rerun=False,algorithm_changes=False,
  rationale='All5common-procedure encode+decode runs completed within180seconds. Round1 reference independent decoding failed only because inherited relative PYTHONPATH resolved from its isolated directory. Correct runtime resolution to absolute existing paths; unchanged code/payloads, fresh independent decode all5methods under same explicit heapq allowance.',
  dependency_paths=env().get('PYTHONPATH','').split(os.pathsep),timeout_seconds_per_verification=180,numerical_threads=1,
  frozen_files={str(p.relative_to(ROOT)):sha(p) for p in files}))
 files=[]
 for p in (BASE/'C05/source').glob('*.ipynb'):files.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)))
 write(BASE/'C05/source-notebook-evidence.json',dict(pin='def1f8c2c5268eb71e83f57c265d4b3c102fb5f8',files=files,
  findings='Original Process submissions notebook loads CSV with headers and calls upstream score(data,truth) directly for Speiser/Deneux. No special orientation/shift/header or interpolation correction is applied. The upstream score jointly masks missing predictions/labels. json_reformat notebook reformats leaderboard score metadata, not raw scientific prediction arrays.',
  conclusion='No complete archived values recoverable by documented source alignment. Four original complete-support cases remain not repairable without new predictions. No altered-contract diagnostic score used.'))
 print('Follow-up runtime and N05metadata revisions sealed; round1 report retained unchanged.')

def one_n05():
 folder=BASE/'N05/revision-2';spec=check(folder);code=(folder/'gpt-5.6-sol.py').read_text();ns=old.code_namespace(code,'N05')
 start=time.perf_counter();answer=ns['extract'](str(ROOT/'data/cache/N05/fixture.nwb'));elapsed=time.perf_counter()-start
 sys.path.insert(0,str(ROOT/'scripts'));import workflow
 scored=workflow.score(answer);path=folder/'answer.json';write(path,answer)
 return dict(benchmark_id='N05',method='gpt-5.6-sol',repair_track='posthoc-repairs-v1',repair_revision=2,status='measured',original_status='failed',
  repair_kind='manual_minimal_algorithm_patch',original_first_attempt_replaced=False,new_model_calls=0,seconds=elapsed,
  code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240,code_sha256=hashlib.sha256(code.encode()).hexdigest(),
  repair_spec_sha256=sha(folder/'run-spec.json'),prediction_file=str(path.relative_to(ROOT)),prediction_sha256=sha(path),**scored)

def decode_method(row):
 method=row['method'];folder=BASE/'B08/decode-revision-2';dest=folder/method;dest.mkdir(exist_ok=False)
 items=json.loads((ROOT/row['prediction_file']).read_text());program=BASE/'B08'/(method+'.py') if method in old.MODELS else ROOT/'experiments/B08/reference.py'
 plan=dict(method=method,program=str(program.relative_to(ROOT)),program_file_sha256=sha(program),payloads=items,output_dir=str(dest.relative_to(ROOT)),report_file=str((dest/'audit.json').relative_to(ROOT)))
 pp=dest/'plan.json';write(pp,plan)
 proc=subprocess.run([sys.executable,str(ROOT/'scripts/repair_failed.py'),'decode','--plan',str(pp)],env=env(),capture_output=True,text=True,timeout=180,cwd=dest)
 (dest/'stdout.txt').write_text(proc.stdout);(dest/'stderr.txt').write_text(proc.stderr);assert proc.returncode==0,proc.stderr[-2500:]
 report=json.loads((dest/'audit.json').read_text());assert report['pid']!=os.getpid() and report['code_sha256']==row['code_sha256'] and not report['encoder_invoked'] and not report['source_arrays_loaded']
 adapter=old.module(ROOT/'experiments/B08/adapter.py','b08_repair_revision2');arrays=adapter.load();errors=[]
 for decoded,saved,(times,labels) in zip(report['items'],items,arrays):
  p=ROOT/decoded['decoded_file'];assert sha(p)==decoded['sha256']
  assert decoded['times_sha256']==saved['decoded_times_sha256'] and decoded['labels_sha256']==saved['decoded_labels_sha256']
  with np.load(p,allow_pickle=False) as z:errors.append(adapter.validate(z['times'],z['labels'],times,labels))
 assert len(errors)==7
 out=dict(row,repair_revision=2,encoder_rerun=False,independent_decode=dict(status='passed',fresh_process=True,n_recordings=7,max_timing_error_seconds=max(errors),report_file=str((dest/'audit.json').relative_to(ROOT)),report_sha256=sha(dest/'audit.json')))
 print('B08',method,'fresh decode passed',row['score'],flush=True);return out

def evaluate():
 folder=BASE/'B08/decode-revision-2';check(folder);check(BASE/'N05/revision-2')
 archive=ROOT/'results/repairs-v1/round-1.json';prior=json.loads(archive.read_text());rows=json.loads((folder/'common-procedure-results.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:redecoded=list(pool.map(decode_method,rows))
 log=BASE/'N05/revision-2/execution.txt'
 try:
  p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one-n05'],env=env(),capture_output=True,text=True,timeout=180)
  log.write_text(p.stdout+'\n'+p.stderr);assert p.returncode==0,p.stderr[-3000:];n05=json.loads(p.stdout.strip().splitlines()[-1])
 except Exception as exc:n05=dict(benchmark_id='N05',method='gpt-5.6-sol',repair_revision=2,status='repair_failed',reason=str(exc),original_first_attempt_replaced=False)
 j08=next(r for r in prior['attempts'] if r['benchmark_id']=='J08')
 final=[j08,n05]+redecoded
 def normalized(row,history=False):
  row=dict(row);row['model']=row.get('model',row['method']);task=row['benchmark_id']
  row['original_key']=dict(benchmark_id=task,slice_id='batch-v11' if task=='B08' else 'expansion-v1',model=row['model'])
  row['repair_type']=row.get('repair_kind','harness_only' if task=='B08' else 'manual_minimal_algorithm_patch')
  row['repair_revision']=row.get('repair_revision',1);row['history_only']=history
  return row
 final=[normalized(r) for r in final]
 history=[normalized(r,True) for r in prior['attempts']]+[r for r in final if r['benchmark_id']!='J08']
 unresolved=[dict(c,original_key=dict(benchmark_id='C05',slice_id=c['slice_id'],model=c['model']),repair_type='archived_output_incomplete_no_fabrication') for c in prior['c05_cases']]
 unresolved.extend(r for r in final if r['status']!='measured')
 for rel,h in json.loads((BASE/'original-preservation.json').read_text()).items():assert sha(ROOT/rel)==h
 for t in ['B08','J08','N05','C05']:old.check(t)
 report=dict(track='posthoc-repairs-v1',status='complete',not_single_shot=True,excluded_from_original_macro=True,new_model_calls=0,
  attempts=history,latest_successes=[r for r in final if r['status']=='measured'],unresolved=unresolved,
  repair_attempt_history_file=str(archive.relative_to(ROOT)),repair_attempt_history_sha256=sha(archive),
  original_results_and_ledger_unchanged=True,original_failures_considered=8,
  repair_assisted_failures_recovered=sum(r['status']=='measured' and r.get('original_status')=='failed' for r in final),
  controls_reexecuted=sum(r['status']=='measured' and r.get('control_originally_successful') for r in final),
  c05_cases=prior['c05_cases'],irreparable_archived_cases=4,
  caveats=['Original failures remain unchanged. This is repair-assisted output, excluded from original macro.',
  'N05original249line noncompliance and repaired-line noncompliance remain visible.',
  'First failed N05patch and first reference independent-decoder environment failures are preserved in round1 history.',
  'No missing C05scientific predictions were fabricated.'])
 write(RESULT,report);print('N05',n05['status'],n05.get('score'),flush=True);print('Repair track updated with preserved history.',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','evaluate','one-n05']);args=p.parse_args()
 if args.action=='prepare':prepare()
 elif args.action=='evaluate':evaluate()
 else:print(json.dumps(one_n05(),allow_nan=False))
