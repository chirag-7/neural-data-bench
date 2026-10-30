"""Read immutable public HDF5 asset through cached byte ranges, no auth material saved."""
import io,json,hashlib,urllib.request
from pathlib import Path
class RangeReader(io.RawIOBase):
 def __init__(self,url,size,cache,block_size=1048576):
  self.url=url;self.size=size;self.cache=Path(cache);self.cache.mkdir(parents=True,exist_ok=True);self.block_size=block_size;self.position=0;self.requests=[]
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.position
 def seek(self,offset,whence=0):
  self.position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
  assert self.position>=0
  return self.position
 def _block(self,index):
  start=index*self.block_size;stop=min(self.size,start+self.block_size)-1;p=self.cache/f'{index:08d}.bin'
  if not p.exists():
   request=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{stop}'})
   with urllib.request.urlopen(request,timeout=120) as r:
    assert r.status==206,'Server must honor byte ranges; refusing entire large download'
    value=r.read();assert len(value)==stop-start+1
   p.write_bytes(value)
  b=p.read_bytes();assert len(b)==stop-start+1
  self.requests.append({'start':start,'stop':stop,'sha256':hashlib.sha256(b).hexdigest()})
  return b
 def read(self,size=-1):
  if size<0:size=self.size-self.position
  size=min(size,self.size-self.position)
  if size<=0:return b''
  chunks=[]
  while size:
   index=self.position//self.block_size;offset=self.position%self.block_size;b=self._block(index);take=min(size,len(b)-offset)
   chunks.append(b[offset:offset+take]);self.position+=take;size-=take
  return b''.join(chunks)
 def readinto(self,b):
  value=self.read(len(b));b[:len(value)]=value;return len(value)
 def manifest(self):
  unique={r['start']:r for r in self.requests}
  return {'asset_url':self.url,'asset_total_bytes':self.size,'whole_file_downloaded':False,'whole_file_sha256_verified':False,'block_size':self.block_size,'fetched_blocks':sorted(unique.values(),key=lambda r:r['start']),'unique_bytes_read':sum(r['stop']-r['start']+1 for r in unique.values())}
