"""Materialize site data from canonical registries/results; never hand-enter scores."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];D=R/'website/data';D.mkdir(exist_ok=True)
for src,name in [('registry/catalog.json','catalog.json'),('analysis/summary.json','summary.json'),('results/measurements.jsonl','measurements.jsonl'),('results/measurements.csv','measurements.csv')]:shutil.copy(R/src,D/name)
shutil.copy(R/'registry/excluded-candidates.json',D/'exclusions.json')
for p in (R/'results').glob('*.json'):shutil.copy(p,D/p.name)
print('Website data synchronized from canonical sources.')
