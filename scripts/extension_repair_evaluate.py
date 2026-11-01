"""Versioned manual repairs through the unchanged sealed original evaluator."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,time,traceback
import extension_evaluate as e
R=e.ROOT;B=R/'experiments/generation-repairs-v1';REV='r1'
def spec(task,model):return json.loads((B/'submissions'/task/model/(REV+'.json')).read_text())
def submission(task,model):
 p=B/'submissions'/task/model/(REV+'.json');return p,json.loads(p.read_text())
def folder(task,sid,model):return B/'artifacts'/task/model/REV/sid
def worker(phase,task,sid,model,timeout,index=None,log_dir=None):
 cmd=[sys.executable,str(Path(__file__).resolve()),'--revision',REV,'--phase',phase,task,sid,model]
 if index is not None:cmd+=['--index',str(index)]
 dest=(log_dir or folder(task,sid,model))/(phase+(f'-{index:02d}' if index is not None else '')+'.log')
 try:
  p=subprocess.run(cmd,cwd=R,env=e.env(),capture_output=True,text=True,timeout=timeout);dest.write_text(p.stdout+'\n'+p.stderr)
  if p.returncode:raise RuntimeError(p.stderr[-5000:])
  return json.loads(p.stdout.strip().splitlines()[-1])
 except subprocess.TimeoutExpired as x:
  dest.write_text(str(x.stdout or '')+'\n'+str(x.stderr or ''));raise TimeoutError(f'{phase} exceeded {timeout} seconds')
def main():
 global REV
 p=argparse.ArgumentParser();p.add_argument('--revision',default='r1');p.add_argument('--one',nargs=3);p.add_argument('--phase',nargs=4);p.add_argument('--index',type=int);p.add_argument('--audit',nargs=3);a=p.parse_args();REV=a.revision
 seal=json.loads((B/'runner-seal.json').read_text());assert e.sha(Path(__file__))==seal['runner_sha256'];assert e.sha(Path(e.__file__))==seal['original_runner_sha256']
 e.folder=folder;e.submission=submission;e.worker=worker;e.MODELS+=['gpt-5.6-sol','gpt-6.1-sol']
 if a.one:
  t,s,m=a.one;v=spec(t,m);assert e.sha(B/'submissions'/t/m/(REV+'.json'))==json.loads((B/'submission-seals'/t/m/(REV+'.json')).read_text())['sha256']
  r=e.one(t,s,m);d=folder(t,s,m);(d/'runner-result.json').write_bytes((d/'result.json').read_bytes())
  r.update(run_id='generation-repairs-v1',code_repaired=True,no_new_generation=True,repair_revision=REV,repair_type=v['repair_type'],patch_description=v['patch_description'],original_key={'benchmark_id':t,'slice_id':s,'model':m},original_code_sha256=v['original_code_sha256'],test_labels_used_for_patch=False,manual_debugging=True,superiority_eligible=False,superiority_reason='Manual debugging after observed failure; final usability only, not fresh model capability.')
  e.dump(d/'result.json',r);print(json.dumps(r,allow_nan=False));return
 if a.audit:
  t,s,m=a.audit;d=folder(t,s,m);r=json.loads((d/'result.json').read_text());assert e.sha(R/r['prediction_file'])==r['prediction_sha256'];assert e.sha(R/r['submission_file'])==r['submission_sha256']
  if t in {'B07','B08'}:e.decode_audit(t,s,m);result={'status':'passed','fresh_decode_audit_sha256':e.sha(d/'fresh-decode-audit.json')}
  else:
   result=e.score(t,s,m);assert abs(result['score']-r['score'])<1e-10;result['status']='passed'
  e.dump(d/'saved-output-audit.json',result);print(json.dumps({'status':'passed','task':t,'model':m}));return
 phase,t,s,m=a.phase
 result=e.procedure(t,s,m) if phase=='procedure' else e.audit_one(t,s,m,a.index) if phase=='decode' else e.score(t,s,m)
 print(json.dumps(result,allow_nan=False))
if __name__=='__main__':main()
