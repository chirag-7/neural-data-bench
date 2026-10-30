"""Materialize the static site's data from canonical registries and measured results."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];D=R/'website/data';D.mkdir(exist_ok=True)
for src,name in [('registry/catalog.json','catalog.json'),('analysis/summary.json','summary.json'),('results/measurements.jsonl','measurements.jsonl'),('results/measurements.csv','measurements.csv'),('results/C05.json','C05.json'),('results/M04.json','M04.json')]:shutil.copy(R/src,D/name)
print('Website data synchronized from canonical source files.')
