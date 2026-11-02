"""Check classification coverage, provenance and immutable-source bindings; no model calls."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((R/p).read_text())
d=load('registry/task-facets-v1.json');catalog=load('registry/catalog.json');measured={t['benchmark_id'] for t in load('analysis/generation-comparison-v2/generation-comparison.json')['tasks']}
a={e['benchmark_id']:e for e in d['assignments']};assert len(a)==len(d['assignments'])==92
assert set(a)=={e['id'] for e in catalog['entries']}
assert (R/'registry/task-facets-v1.json').read_bytes()==(R/'website/data/task-facets.json').read_bytes()
for path,digest in d['input_sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
for id,e in a.items():
 assert e['scope']==('executed' if id in measured else 'proposed'),id
 assert e['input_type'] in d['vocabulary']['input_type'] and e['operation'] in d['vocabulary']['operation']
 assert e['generalization'] and len(e['generalization'])==len(set(e['generalization']))
 assert all(v in d['vocabulary']['generalization'] for v in e['generalization'])
 comp=e['input_components'];assert comp==sorted(set(comp)) and all(v!='multimodal' and v in d['vocabulary']['input_type'] for v in comp)
 assert (len(comp)>1)==(e['input_type']=='multimodal')
 if len(comp)==1:assert e['input_type']==comp[0]
 assert e['rationale'] and e['source_urls'] and e['evidence']
 for ev in e['evidence']:assert hashlib.sha256((R/ev['path']).read_bytes()).hexdigest()==ev['sha256'],id
 assert (R/f'docs/task-classification/{id}.md').exists()
for id,expected in {'A09':'motion','C05':'physiological_signals','F04':'images_video','G01':'spike_events','I10':'tables','K01':'tables','K04':'tables','K06':'tables','N05':'files','H16':'physiological_signals','L06':'spike_events'}.items():assert a[id]['input_type']==expected,id
assert not any(a[id]['input_type']=='multimodal' for id in measured)
assert a['D02']['generalization']==['new_conditions'] and a['N05']['generalization']==['no_transfer']
assert a['E06']['generalization']==['within_source','new_conditions']
with (R/'docs/task-classification/assignments.csv').open() as f:assert {x['benchmark_id'] for x in csv.DictReader(f)}==set(a)
print('Task facets: 92 active contracts, 30 executed / 62 proposed; valid provenance, vocabulary, source bindings and website copy.')
