"""Portable integrity checks without raw-data downloads, scientific dependencies or model calls."""
from pathlib import Path
import hashlib,json,re,urllib.parse
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'registry/catalog.json').read_text());ids=[e['id'] for e in c['entries']];assert len(ids)==len(set(ids))
for p in R.rglob('*.md'):
 if 'data/cache' in str(p) or '.git' in p.parts:continue
 for raw in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  target=raw.strip('<>').split('#')[0]
  if not target or re.match(r'\w+://',target):continue
  assert (p.parent/urllib.parse.unquote(target)).exists(),f'Broken link {p}: {target}'
records=[json.loads(line) for line in (R/'results/measurements.jsonl').read_text().splitlines()]
for r in records:
 assert r['benchmark_id'] in ids
 if r['status']=='measured':
  assert isinstance(r['score'],(float,int));p=R/r['prediction_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['prediction_sha256']
for a,b in [('registry/catalog.json','website/data/catalog.json'),('analysis/summary.json','website/data/summary.json'),('results/measurements.jsonl','website/data/measurements.jsonl'),('results/measurements.csv','website/data/measurements.csv')]:
 assert (R/a).read_bytes()==(R/b).read_bytes(),f'Stale site data: {b}'
for task,base in [('C05','experiments/C05/pilot-v1'),('M04','experiments/M04')]:
 for p in json.loads((R/f'experiments/{task}/generation-provenance.json').read_text()):
  code=json.loads((R/base/(p['requested_model']+'.json')).read_text())['code'];assert hashlib.sha256(code.encode()).hexdigest()==p['code_sha256'];assert p['tool_events']==0
decisions=json.loads((R/'registry/admission-decisions.json').read_text());assert {x['benchmark_id'] for x in decisions}==set(ids)
for e in c['entries']:
 assert (R/e['admission_evidence_file']).exists()
for d in (R/'experiments').iterdir():
 if not (d/'run-spec.json').exists() or d.name in ['C05','M04']:continue
 spec=json.loads((d/'run-spec.json').read_text());assert hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest()==spec['prompt_sha256']
 codepath=d/('reference.py' if d.name=='N05' else 'adapter.py');assert hashlib.sha256(codepath.read_bytes()).hexdigest()==spec['reference_sha256' if d.name=='N05' else 'adapter_sha256']
 prov=json.loads((d/'generation-provenance.json').read_text());assert len(prov)==3
 for p in prov:
  code=json.loads((d/(p['requested_model']+'.json')).read_text())['code'];assert hashlib.sha256(code.encode()).hexdigest()==p['code_sha256'];assert p['tool_events']==0 and p['usage'] is not None
for task in set(r['benchmark_id'] for r in records if r['model'] in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']):
 for model in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']:assert any(r['benchmark_id']==task and r['model']==model for r in records)
assert not any('luna' in r['model'] for r in records)
print(f'Integrity checks passed: {len(ids)} task cards, {len(records)} records, linked files, predictions, provenance and synchronized site data.')
