"""Download exact reviewed DAS audio/annotations and source unit/rights evidence."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[2]
def acquire():
    m=json.loads(Path(__file__).with_name('source.json').read_text())
    for row in m['files']:
        p=ROOT/row['path'];p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            b=urllib.request.urlopen(row['url'],timeout=240).read()
            if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise ValueError('Changed upstream content: '+row['url'])
            p.write_bytes(b)
        assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    selected_names=json.loads(Path(__file__).with_name('selection.json').read_text())
    chosen=[dict(name=Path(r['path']).name,url=r['url'],bytes=r['bytes'],sha256=r['sha256'],original_checksum=r.get('upstream_checksum')) for r in m['files'] if Path(r['path']).name in selected_names]
    (ROOT/'data/cache/A15/selected-source-files.json').write_text(json.dumps(chosen,indent=2)+'\n')
    return m
if __name__=='__main__':
    m=acquire();print(m['benchmark_id'],len(m['files']),'source files verified')
