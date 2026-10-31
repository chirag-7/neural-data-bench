"""Acquire exact public-source files; refuses content changed from reviewed hashes."""
from pathlib import Path
import json,hashlib,urllib.request
ROOT=Path(__file__).resolve().parents[2]
def acquire():
    manifest=json.loads((Path(__file__).with_name('source.json')).read_text())
    for row in manifest['files']:
        path=ROOT/row['path'];path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():
            raw=urllib.request.urlopen(row['url'],timeout=240).read()
            if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
                raise ValueError('Upstream content changed: '+row['url'])
            path.write_bytes(raw)
        assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    return manifest
if __name__=='__main__':
    m=acquire();print(m['benchmark_id'],len(m['files']),'source files verified')
