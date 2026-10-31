"""Reacquire only the frozen B07 byte ranges; abort on any changed source bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,urllib.request
R=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def acquire(row):
 target=R/row['path'];meta=R/row['metadata_path'];target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and meta.exists() and sha(target.read_bytes())==row['sha256'] and sha(meta.read_bytes())==row['metadata_sha256']:return
 mb=urllib.request.urlopen(row['metadata_source'],timeout=60).read();assert sha(mb)==row['metadata_sha256']
 req=urllib.request.Request(row['source_url'],headers={'Range':f"bytes={row['range_start']}-{row['range_end']}",'If-Match':row['source_etag']})
 with urllib.request.urlopen(req,timeout=90) as response:
  assert response.status==206 and response.headers['Content-Range']==row['content_range'] and response.headers['ETag']==row['source_etag'];raw=response.read(row['bytes']+1)
 assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
 target.write_bytes(raw);meta.write_bytes(mb)
if __name__=='__main__':
 rows=json.loads((R/'data/manifests/B07.json').read_text())['files']
 with ThreadPoolExecutor(4) as pool:list(pool.map(acquire,rows))
 print('All16 frozen chunks and original metadata match their SHA256s.')
