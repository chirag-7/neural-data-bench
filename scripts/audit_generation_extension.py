"""Re-score retained successful extension outputs; never re-run model procedures."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'experiments/generation-extension-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def one(p):
 r=json.loads(p.read_text());assert sha(R/r['prediction_file'])==r['prediction_sha256'];assert sha(R/r['submission_file'])==r['submission_sha256']
 t,s,m=r['benchmark_id'],r['slice_id'],r['model'];d=p.parent/'audits';before=set(d.glob('*')) if d.exists() else set()
 log=B/'orchestration-logs'/t/m/(s+'-saved-audit.log');log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w') as f:v=subprocess.run([sys.executable,str(R/'scripts/extension_evaluate.py'),'--audit-saved',t,s,m],cwd=R,env=os.environ.copy(),stdout=f,stderr=subprocess.STDOUT,timeout=3900)
 assert v.returncode==0,log
 new=set(d.glob('*'))-before;assert len(new)==1
 audit=next(iter(new))/'result.json';a=json.loads(audit.read_text())
 if t in {'B07','B08'}:assert a and all(x['status']=='passed' for x in a);delta=None
 else:delta=abs(a['score']-r['score']);assert delta<1e-10,(t,m,delta)
 out=dict(benchmark_id=t,slice_id=s,model=m,status='passed',absolute_score_delta=delta,prediction_sha256=r['prediction_sha256'],original_result_file=str(p.relative_to(R)),original_result_sha256=sha(p),audit_result_file=str(audit.relative_to(R)),audit_result_sha256=sha(audit))
 print(t,s,m,'audit passed',flush=True);return out
if __name__=='__main__':
 report=B/'saved-output-audits.json'
 prior=json.loads(report.read_text())['records'] if report.exists() else []
 checked={r['original_result_sha256'] for r in prior}
 paths=sorted(p for p in (B/'artifacts').glob('*/*/*/result.json') if json.loads(p.read_text())['status']=='measured' and sha(p) not in checked)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=prior+list(pool.map(one,paths))
 (B/'saved-output-audits.json').write_text(json.dumps(dict(policy='Independent fresh-process scoring or decoding of saved outputs; no procedure re-execution or new generation',records=rows),indent=2)+'\n')
 print('All saved-output audits passed:',len(rows))
