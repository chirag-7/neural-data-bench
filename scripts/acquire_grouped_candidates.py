"""Acquire exact K04/M01 source bytes from the committed release manifests."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, urllib.request
R=Path(__file__).resolve().parents[1]
def acquire(item):
    p=(R/item['path']).resolve()
    assert p.is_relative_to((R/'data/cache').resolve()), 'Source cache paths only'
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        temp=p.with_suffix(p.suffix+'.partial')
        with urllib.request.urlopen(item['url'],timeout=120) as response,temp.open('wb') as out:
            while chunk:=response.read(1024*1024):out.write(chunk)
        assert temp.stat().st_size==item['bytes']
        assert hashlib.sha256(temp.read_bytes()).hexdigest()==item['sha256'], 'Source bytes changed; do not alter frozen manifest'
        temp.replace(p)
    assert p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
    if item.get('publisher_md5'):assert hashlib.md5(p.read_bytes()).hexdigest()==item['publisher_md5']
    print(p.relative_to(R), 'source identity verified', flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('task',choices=['K04','M01']);args=parser.parse_args()
    manifest=json.loads((R/f'data/manifests/{args.task}.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(acquire,manifest['files']))
