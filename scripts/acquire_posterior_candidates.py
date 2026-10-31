"""Acquire frozen L06 source bytes; never refresh or replace their manifest."""
from pathlib import Path
import hashlib,json,urllib.request
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'data/manifests/L06.json').read_text())
for entry in manifest['files']:
    path=R/entry['path'];path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        data=urllib.request.urlopen(entry['source_url'],timeout=90).read()
        assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],'Source bytes changed; acquisition stopped'
        path.write_bytes(data)
    assert path.stat().st_size==entry['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
print('All42 original immutable L06 source files acquired and verified.')
