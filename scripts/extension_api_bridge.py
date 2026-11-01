"""Loopback-only, memory-only credential bridge for the two approved model snapshots.

Never logs/returns/persists the API key. Only frozen prompts and bounded Responses
requests can be forwarded to api.openai.com. No API calls occur before user entry.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import hashlib,json,secrets,threading,time,urllib.request,urllib.error,urllib.parse
R=Path(__file__).resolve().parents[1];D=R/'experiments/generation-extension-v1'
manifest=json.loads((D/'manifest.json').read_text())
PROMPTS={t['prompt_sha256']:t['benchmark_id'] for t in manifest['tasks']}
MODELS={'gpt-5-2025-08-07':(1.25,10,24000),'gpt-4.1-2025-04-14':(2,8,8192)}
NONCE=secrets.token_urlsafe(24);KEY=None;LIMIT=15.;SPENT=0.;LEDGER=[];DONE=set();LOCK=threading.Lock()
PORT=8766;ORIGIN=f'http://127.0.0.1:{PORT}';BASE='/'+NONCE
def scrub(value):return value.replace(KEY,'[REDACTED]') if KEY else value
def persist():
 (D/'api-cost-ledger.json').write_text(json.dumps(dict(budget_usd=LIMIT,conservative_spent_or_reserved_usd=SPENT,requests=LEDGER,credential_persisted=False),indent=2)+'\n')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,code,data,html=False):
  raw=data.encode() if isinstance(data,str) else json.dumps(data).encode();self.send_response(code)
  self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json');self.send_header('Cache-Control','no-store')
  self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.headers.get('Host')!=f'127.0.0.1:{PORT}':return self.send(403,{'error':'Host rejected'})
  if self.path==BASE+'/':
   return self.send(200,'''<!doctype html><title>Neural Data Bench · temporary API access</title><style>body{font:18px system-ui;max-width:700px;margin:70px auto;padding:24px;color:#243746}input{display:block;width:95%;padding:14px;margin:15px 0}button{padding:12px 20px}small{display:block;line-height:1.6}</style><h1>Temporary benchmark API access</h1><p>Paste the dedicated OpenAI API key below. It is sent only to this local process and kept in memory; it is never written to a file, chat, repository or website.</p><p>The process can call only GPT-5 and GPT-4.1 with the 30 frozen benchmark prompts. Its conservative application spending ceiling is <b>$15</b>.</p><form method="post" action="credential"><label>Dedicated API key<input type="password" name="api_key" autocomplete="off" required autofocus></label><button>Provide temporary access</button></form><small>Do not close the local server process during the benchmark. The OpenAI key itself expires in seven days and can be revoked in your account.</small>''',True)
  if self.path==BASE+'/status':return self.send(200,dict(ready=KEY is not None,conservative_spent_usd=SPENT,budget_usd=LIMIT,requests=len(LEDGER),completed_generations=len(DONE)))
  prefix=BASE+'/models/'
  if self.path.startswith(prefix) and self.path[len(prefix):] in MODELS:
   if not KEY:return self.send(409,{'error':'API key not supplied'})
   return self.forward('GET','https://api.openai.com/v1/models/'+self.path[len(prefix):])
  return self.send(404,{'error':'Not found'})
 def do_POST(self):
  global KEY,SPENT
  if self.headers.get('Host')!=f'127.0.0.1:{PORT}':return self.send(403,{'error':'Host rejected'})
  size=int(self.headers.get('Content-Length','0'))
  if size>1000000:return self.send(413,{'error':'Request too large'})
  body=self.rfile.read(size)
  if self.path==BASE+'/credential':
   if self.headers.get('Origin')!=ORIGIN:return self.send(403,{'error':'Origin rejected'})
   if KEY:return self.send(409,{'error':'Credential already supplied'})
   key=urllib.parse.parse_qs(body.decode()).get('api_key',[''])[0].strip()
   if not key.startswith('sk-') or len(key)<30:return self.send(400,{'error':'Expected a valid OpenAI API key'})
   KEY=key;return self.send(200,'<title>Access ready</title><h1>Temporary access is ready</h1><p>The key is held only in the local process memory. You can return to Codex.</p>',True)
  if self.path!=BASE+'/responses':return self.send(404,{'error':'Not found'})
  if not KEY:return self.send(409,{'error':'API key not supplied'})
  try:
   obj=json.loads(body);model=obj['model'];rates=MODELS[model];prompt=obj['input'];task=PROMPTS[hashlib.sha256(prompt.encode()).hexdigest()]
   assert isinstance(prompt,str) and obj.get('store') is False and not obj.get('tools')
   assert 0<obj['max_output_tokens']<=rates[2]
   assert set(obj)<= {'model','input','max_output_tokens','reasoning','text','store'}
   if model.startswith('gpt-5'):assert obj.get('reasoning')=={'effort':'high'}
   else:assert not obj.get('reasoning')
  except (KeyError,AssertionError,TypeError,ValueError):return self.send(400,{'error':'Request does not match approved frozen generation policy'})
  reserve=((len(prompt.encode())+4096)*rates[0]+obj['max_output_tokens']*rates[1])/1000000
  with LOCK:
   if (task,model) in DONE:return self.send(409,{'error':'A completed generation already exists; no silent repeats'})
   if SPENT+reserve>LIMIT:return self.send(402,{'error':'Conservative application budget would be exceeded'})
   SPENT+=reserve;row=dict(task=task,model=model,reserved_max_usd=reserve,status='dispatched',time_unix=time.time());LEDGER.append(row);persist()
  return self.forward('POST','https://api.openai.com/v1/responses',obj,row,rates,reserve)
 def forward(self,method,url,obj=None,row=None,rates=None,reserve=0):
  global SPENT
  request=urllib.request.Request(url,data=json.dumps(obj).encode() if obj else None,method=method,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request,timeout=600) as response:result=json.load(response);request_id=response.headers.get('x-request-id')
   if row is not None:
    usage=result.get('usage',{});cost=(usage.get('input_tokens',0)*rates[0]+usage.get('output_tokens',0)*rates[1])/1000000
    with LOCK:
     if 'input_tokens' in usage and 'output_tokens' in usage:SPENT+=cost-reserve
     row.update(status=result.get('status','received'),request_id=request_id,usage=usage,actual_uncached_rate_usd=cost,returned_model=result.get('model'))
     DONE.add((row['task'],row['model']));persist()
   return self.send(200,result)
  except urllib.error.HTTPError as exc:
   error=scrub(exc.read().decode())
   if row is not None:
    with LOCK:row.update(status='http_error',http_status=exc.code,error=error[:3000]);persist()
   return self.send(exc.code,{'upstream_error':error})
  except Exception as exc:
   if row is not None:
    with LOCK:row.update(status='transport_error',error=scrub(str(exc)));persist()
   return self.send(502,{'error':'Upstream transport failed; reservation retained for safety'})
if __name__=='__main__':
 print(ORIGIN+BASE+'/',flush=True)
 try:ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
 finally:KEY=None
