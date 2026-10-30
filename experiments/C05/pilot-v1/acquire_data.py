"""Fetch public data into work/spikefinder, then verify the recorded hashes."""
from pathlib import Path
import hashlib, io, json, urllib.request, zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DATA=ROOT/'work/spikefinder'
PIN='def1f8c2c5268eb71e83f57c265d4b3c102fb5f8'
RAW=f'https://raw.githubusercontent.com/berenslab/spikefinder_analysis/{PIN}/'

def fetch(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        request=urllib.request.Request(url,headers={'User-Agent':'NeuralDataObservatoryResearch/0.2'})
        with urllib.request.urlopen(request,timeout=90) as r:path.write_bytes(r.read())
    print(path.name,path.stat().st_size)

archive=ROOT/'work/spikefinder.train.zip'
fetch('https://s3.amazonaws.com/neuro.datasets/challenges/spikefinder/spikefinder.train.zip',archive)
with zipfile.ZipFile(archive) as z:
    for kind in ['calcium','spikes']:
        p=DATA/f'1.train.{kind}.csv';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(z.read(f'spikefinder.train/1.train.{kind}.csv'))
fetch(RAW+'data/raw/truth/1.test.calcium.csv',DATA/'reference/1.test.calcium.csv')
fetch(RAW+'data/raw/truth/1.test.spikes.csv',DATA/'reference/truth.test.spikes.csv')
fetch(RAW+'spikefinder_eval.py',DATA/'reference/spikefinder_eval.py')
fetch(RAW+'data/results_30_06_17.csv',DATA/'reference/results_30_06_17.csv')
for name in ['deneux','speiser','friedrich','rupprecht']:
    fetch(RAW+f'data/raw/{name}/1.test.spikes.csv',DATA/f'reference/{name}.test.spikes.csv')
manifest=HERE/'results.json'
if manifest.exists():
    for rel,expected in json.loads(manifest.read_text())['input_hashes'].items():
        actual=hashlib.sha256((DATA/rel).read_bytes()).hexdigest()
        if actual!=expected:raise ValueError('Hash mismatch: '+rel)
    print('Input hashes match the published pilot manifest.')
