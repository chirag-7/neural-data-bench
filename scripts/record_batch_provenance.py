"""Preserve exact generation evidence once; never regenerate or alter submissions."""
from pathlib import Path
import argparse,hashlib,json,shutil
from expansion import ROOT as R,MODELS
W=R.parents[1]/'work'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(task):
 d=R/f'experiments/{task}';folder=d/'generation-events';folder.mkdir(exist_ok=True);provenance=[];evidence=[]
 for model in MODELS:
  dest=folder/(model+'.jsonl');source=W/'expansion-models'/f'{task}-{model}.jsonl'
  if dest.exists():assert dest.read_bytes()==source.read_bytes()
  else:shutil.copyfile(source,dest)
  events=[json.loads(s) for s in dest.read_text().splitlines() if s.strip()];obj=json.loads((d/(model+'.json')).read_text())
  messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message'];assert json.loads(messages[-1])==obj
  ntools=sum(e.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for e in events);assert ntools==0
  usage=next(e['usage'] for e in reversed(events) if e['type']=='turn.completed')
  provenance.append(dict(requested_model=model,reasoning_effort='high',generation_replicates=1,user_prompt_sha256=sha(d/'prompt.txt'),code_sha256=hashlib.sha256(obj['code'].encode()).hexdigest(),code_lines=len(obj['code'].splitlines()),usage=usage,tool_events=ntools,effective_context='Identical explicit prompt across versions; CLI/provider hidden context not verified identical',command_policy=['exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox read-only','model_reasoning_effort=high']))
  evidence.append(dict(model=model,event_file=str(dest.relative_to(R)),sha256=sha(dest),tool_events=ntools,submission_matches_final_generation_event=True))
 for name,value in [('generation-provenance.json',provenance),('generation-event-files.json',evidence)]:
  path=d/name;text=json.dumps(value,indent=2)+'\n'
  if path.exists():assert path.read_text()==text
  else:path.write_text(text)
 print(task,'three unchanged submissions,no-tool events and usage retained')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('tasks',nargs='+');a=p.parse_args()
 for task in a.tasks:record(task)
