"""Independently decode saved B07 payloads and recompute byte-size metrics; never encode."""
from pathlib import Path
import hashlib,importlib.util,json,sys
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'experiments/B07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify(write=True):
 spec=json.loads((D/'run-spec.json').read_text())
 for path,h in spec['frozen_files'].items():assert sha(R/path)==h,path
 sources=json.loads((R/'data/manifests/B07.json').read_text())['files'];assert len(sources)==16 and len({s['animal'] for s in sources})==14
 for s in sources:
  assert sha(R/s['path'])==s['sha256'] and sha(R/s['metadata_path'])==s['metadata_sha256']
  assert s['bytes']==4096*384*2 and s['range_start']==1000000*384*2 and s['range_end']-s['range_start']+1==s['bytes']
  assert s['content_range']==f"bytes {s['range_start']}-{s['range_end']}/{s['source_total_bytes']}"
  meta=json.loads((R/s['metadata_path']).read_text())['kwargs']
  assert meta['num_chan']==384 and np.dtype(meta['dtype'])==np.dtype('<i2') and meta['time_axis']==0 and meta['file_offset']==0
 checks=[]
 for row in json.loads((R/'results/B07.json').read_text()):
  if row['status']!='measured':continue
  assert sha(R/row['prediction_file'])==row['prediction_sha256'];items=json.loads((R/row['prediction_file']).read_text());assert len(items)==16
  sizes=[]
  for item,source in zip(items,sources):
   blob=(R/item['compressed_file']).read_bytes();assert len(blob)==item['compressed_bytes'] and sha(R/item['compressed_file'])==item['compressed_sha256']
   # Fresh implementation namespace, decoding saved bytes only; source arrays are loaded afterwards.
   if row['model'].startswith('gpt-'):
    code=json.loads((D/(row['model']+'.json')).read_text())['code'];ns={};exec(compile(code,'audit-decoder','exec'),ns);decoded=ns['decompress'](blob,(4096,384),'<i2')
   else:decoded=load_module(D/'specialist.py','audit_specialist').decompress(blob,(4096,384),'<i2',row['model'])
   assert isinstance(decoded,np.ndarray) and decoded.shape==(4096,384) and decoded.dtype==np.dtype('<i2')
   raw=np.ascontiguousarray(decoded).tobytes();assert raw==(R/source['path']).read_bytes()
   assert hashlib.sha256(raw).hexdigest()==item['decoded_sha256']==item['source_sha256']==source['sha256'] and item['lossless']
   assert (item['recording'],item['origin'],item['animal'])==(source['recording'],source['origin'],source['animal'])
   sizes.append(len(blob))
  per=[8*n/(4096*384) for n in sizes];score=sum(per)/16
  assert abs(score-row['score'])<1e-12 and per==row['per_unit'] and abs(16/score-row['compression_ratio'])<1e-12
  checks.append(dict(model=row['model'],score=score,encoded_bytes=sum(sizes),bitstreams_verified=16,all_raw_bytes_equal=True,prediction_sha256=row['prediction_sha256']))
 events=json.loads((D/'generation-event-files.json').read_text())
 for event in events:
  assert sha(R/event['event_file'])==event['sha256'] and event['tool_events']==0 and event['submission_matches_final_generation_event']
 out=dict(benchmark_id='B07',source_chunks_verified=16,source_animals=14,source_bytes_verified=sum(s['bytes'] for s in sources),frozen_hashes='passed',prediction_checks=checks,generation_checks=events,scope='Every retained successful payload decoded afresh, exact source bytes compared and size arithmetic recomputed; no encoder rerun or model repair; no global-best claim')
 if write:(D/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
 return out
if __name__=='__main__':print(json.dumps(verify(),indent=2))
