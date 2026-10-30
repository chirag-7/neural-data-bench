"""Acquire the five original test preparations; pin sources and hash every file."""
from pathlib import Path
import hashlib, json, urllib.request, zipfile
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cache/spikefinder'
PIN='def1f8c2c5268eb71e83f57c265d4b3c102fb5f8'
RAW=f'https://raw.githubusercontent.com/berenslab/spikefinder_analysis/{PIN}/'
manifest=[]
manifest_path=ROOT/'data/manifests/spikefinder.json'
expected={f['path']:f['sha256'] for f in json.loads(manifest_path.read_text())['files']} if manifest_path.exists() else {}
def fetch(url,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NeuralDataBench/0.3'}),timeout=120) as f:p.write_bytes(f.read())
    manifest.append(dict(path=str(p.relative_to(ROOT)),source=url,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,acquired_on='2026-10-30',license_status='Upstream data terms apply; redistribution not granted by this repository'))
archive=DATA/'spikefinder.train.zip'
fetch('https://s3.amazonaws.com/neuro.datasets/challenges/spikefinder/spikefinder.train.zip',archive)
with zipfile.ZipFile(archive) as z:
    for d in range(1,6):
        for kind in ['calcium','spikes']:
            name=f'{d}.train.{kind}.csv';p=DATA/name;p.write_bytes(z.read('spikefinder.train/'+name))
            manifest.append(dict(path=str(p.relative_to(ROOT)),source=f'{manifest[0]["source"]}#spikefinder.train/{name}',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,acquired_on='2026-10-30',license_status='Upstream data terms apply'))
for d in range(1,6):
    for kind in ['calcium','spikes']:fetch(RAW+f'data/raw/truth/{d}.test.{kind}.csv',DATA/f'{d}.test.{kind}.csv')
    for method in ['deneux','speiser','friedrich','rupprecht']:
        fetch(RAW+f'data/raw/{method}/{d}.test.spikes.csv',DATA/f'{d}.{method}.csv')
fetch(RAW+'spikefinder_eval.py',DATA/'spikefinder_eval.py')
fetch(RAW+'data/results_30_06_17.csv',DATA/'results_30_06_17.csv')
for item in manifest:
    prior=expected.get(item['path'])
    if prior is not None and item['sha256']!=prior:
        raise ValueError('Acquired bytes differ from the published manifest: '+item['path'])
manifest_path.write_text(json.dumps(dict(pin=PIN,files=manifest),indent=2))
print('Acquired and hashed',len(manifest),'files')
