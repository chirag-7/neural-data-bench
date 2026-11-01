"""Frozen single-shot API generations through a memory-only loopback bridge."""
from pathlib import Path
import argparse,ast,hashlib,json,time,urllib.request,urllib.error
R=Path(__file__).resolve().parents[1];D=R/'experiments/generation-extension-v1'
MODELS=['gpt-4.1-2025-04-14','gpt-5-2025-08-07']
SCHEMA={'type':'object','properties':{'description':{'type':'string'},'code':{'type':'string'}},'required':['description','code'],'additionalProperties':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def freeze():
 path=D/'generation-seal.json';assert not path.exists(),'Generation seal already exists'
 m=read(D/'manifest.json');paths=[D/'manifest.json',D/'plan.md',D/'execution-seal.json',R/'scripts/extension_api_bridge.py',Path(__file__).resolve()]+[R/t['prompt_file'] for t in m['tasks']]
 write(path,dict(study=m['study'],status='sealed_before_new_API_generations',sources={str(p.relative_to(R)):sha(p) for p in paths},models=MODELS,settings={'gpt-5-2025-08-07':dict(reasoning={'effort':'high'},max_output_tokens=24000),'gpt-4.1-2025-04-14':dict(max_output_tokens=8192)},store=False,tools=[],one_generation_per_task_model=True,no_execution_feedback=True,provider='OpenAI Responses API; Codex provider wrapper differs from historical Sol programs',prices_per_million={'gpt-5-2025-08-07':dict(input=1.25,output=10),'gpt-4.1-2025-04-14':dict(input=2,output=8)},budget_ceiling_usd=15))
 print('Generation settings and original prompt identities sealed.')
def check():
 spec=read(D/'generation-seal.json')
 for rel,h in spec['sources'].items():assert sha(R/rel)==h,rel
 return spec
def request(base,path,obj=None):
 req=urllib.request.Request(base+path,data=json.dumps(obj).encode() if obj is not None else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=660) as response:return json.load(response)
def generate(base,t,model,spec):
 dest=D/'generation'/t['benchmark_id']/model;out=D/'submissions'/t['benchmark_id']/(model+'.json')
 if (dest/'provenance.json').exists():print(t['benchmark_id'],model,'retained existing attempt',flush=True);return
 assert not dest.exists() and not out.exists(),'Partial attempt exists; audit before resuming'
 dest.mkdir(parents=True);prompt=(R/t['prompt_file']).read_text();assert hashlib.sha256(prompt.encode()).hexdigest()==t['prompt_sha256']
 body=dict(model=model,input=prompt,store=False,text={'format':dict(type='json_schema',name='neural_program',strict=True,schema=SCHEMA)},**spec['settings'][model])
 write(dest/'request.json',body);start=time.time();prov=dict(benchmark_id=t['benchmark_id'],requested_model=model,prompt_sha256=t['prompt_sha256'],request_sha256=sha(dest/'request.json'),generation_seal_sha256=sha(D/'generation-seal.json'),provider='OpenAI Responses API',tools_enabled=False,generation_replicate=1,execution_feedback=False,started_unix=start)
 try:
  response=request(base,'/responses',body);write(dest/'response.json',response)
  prov.update(response_sha256=sha(dest/'response.json'),response_id=response.get('id'),returned_model=response.get('model'),usage=response.get('usage'),provider_status=response.get('status'))
  assert response.get('status')=='completed',str(response.get('incomplete_details',response.get('error')))
  blocks=response.get('output',[]);text=''.join(c['text'] for item in blocks if item.get('type')=='message' for c in item.get('content',[]) if c.get('type')=='output_text')
  obj=json.loads(text);assert set(obj)=={'description','code'} and all(isinstance(v,str) for v in obj.values())
  write(out,obj);(dest/'submission.py').write_text(obj['code']);prov.update(status='generated',submission_file=str(out.relative_to(R)),submission_sha256=sha(out),code_sha256=hashlib.sha256(obj['code'].encode()).hexdigest(),code_lines=len(obj['code'].splitlines()))
  try:ast.parse(obj['code']);prov['python_syntax_valid']=True
  except SyntaxError:prov['python_syntax_valid']=False
 except urllib.error.HTTPError as exc:
  prov.update(status='access_or_transport_failure',http_status=exc.code,error=exc.read().decode()[:3000]);write(dest/'provenance.json',dict(prov,elapsed_seconds=time.time()-start));print(t['benchmark_id'],model,prov['status'],exc.code,flush=True);raise
 except Exception as exc:prov.update(status='generation_invalid_or_incomplete',error=str(exc))
 prov['elapsed_seconds']=time.time()-start;write(dest/'provenance.json',prov);print(t['benchmark_id'],model,prov['status'],(prov.get('usage') or {}).get('output_tokens'),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','check','probe','generate']);p.add_argument('--bridge');p.add_argument('--tasks',nargs='*');p.add_argument('--models',nargs='*',choices=MODELS);a=p.parse_args()
 if a.action=='freeze':return freeze()
 if a.action=='check':check();print('Generation seal passed.');return
 assert a.bridge and a.bridge.startswith('http://127.0.0.1:8766/'),'Only approved loopback bridge is supported'
 if a.action=='probe':
  rows=[]
  for model in MODELS:
   result=request(a.bridge,'/models/'+model);rows.append(dict(requested=model,returned=result.get('id'),object=result.get('object'),available=result.get('id')==model))
  write(D/'model-access-check.json',rows);print(json.dumps(rows));return
 spec=check();m=read(D/'manifest.json');tasks=[t for t in m['tasks'] if not a.tasks or t['benchmark_id'] in a.tasks]
 assert not a.tasks or len(tasks)==len(set(a.tasks)),'Unknown tasks'
 for t in tasks:
  for model in a.models or MODELS:generate(a.bridge,t,model,spec)
if __name__=='__main__':main()
