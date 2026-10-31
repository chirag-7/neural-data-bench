"""Reacquire exact licensed public snapshot (about 2.35GB transport, 8MB retained).
No fitting/scoring. Original bucket object generations/checksums are pinned.
"""
from pathlib import Path
import base64,hashlib,json,urllib.request
import numpy as np
from adapter import CACHE,IDS,prepare,sha
BASE='https://zapbench-release.storage.googleapis.com/'
def acquire():
 manifest=json.loads((Path(__file__).parent/'data-manifest.json').read_text())
 objects=json.loads((CACHE/'raw/source-objects.json').read_text())
 lookup={x['name']:x for x in objects};a=np.empty((7879,len(IDS)),dtype='<f4')
 for j in sorted(set((IDS//512).tolist())):
  positions=np.flatnonzero(IDS//512==j);columns=IDS[positions]%512
  for i in range(16):
   name=f'volumes/20240930/traces/c/{i}/{j}';obj=lookup[name]
   u=BASE+name+'?generation='+obj['generation']
   with urllib.request.urlopen(u,timeout=90) as r:b=r.read()
   assert len(b)==int(obj['size'])
   assert base64.b64encode(hashlib.md5(b).digest()).decode()==obj['md5Hash']
   v=np.frombuffer(b,dtype='<f4').reshape(512,512);n=min(512,7879-i*512)
   a[i*512:i*512+n,positions]=v[:n,columns]
 np.save(CACHE/'raw/traces-selected.npy',a)
 assert sha(CACHE/'raw/traces-selected.npy')==manifest['raw_subset_sha256']
 return prepare()
if __name__=='__main__':print(json.dumps(acquire(),indent=2))
