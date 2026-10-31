"""Pinned original Spikepack writer/reader, transported as an explicit byte frame."""
from pathlib import Path
import sys,tempfile,json,struct,zlib
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent/'upstream'))
from spikepack import write_blosc,read_blosc
from numcodecs.blosc import set_nthreads
def compress(times,labels,method):
 if method=='spikepack':
  set_nthreads(1)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);write_blosc(p,times_seconds=times,labels=labels,quantization_us=100)
   files=sorted(p.iterdir());header=json.dumps([(x.name,x.stat().st_size) for x in files],separators=(',',':')).encode()
   return struct.pack('<I',len(header))+header+b''.join(x.read_bytes() for x in files)
 origin=float(times[0]);ticks=np.rint((times-origin)/1e-4).astype('<u8');delta=np.diff(np.r_[np.uint64(0),ticks]).astype('<u8')
 return struct.pack('<dQ',origin,len(times))+zlib.compress(delta.tobytes()+labels.astype('<i4').tobytes(),9)
def decompress(blob,method):
 if method=='spikepack':
  n=struct.unpack('<I',blob[:4])[0];entries=json.loads(blob[4:4+n]);offset=4+n
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   for name,size in entries:
    assert Path(name).name==name;(p/name).write_bytes(blob[offset:offset+size]);offset+=size
   assert offset==len(blob);out=read_blosc(p);return out['times'],out['labels']
 origin,n=struct.unpack('<dQ',blob[:16]);raw=zlib.decompress(blob[16:]);ticks=np.cumsum(np.frombuffer(raw[:n*8],dtype='<u8'),dtype=np.uint64)
 return origin+ticks.astype(float)*1e-4,np.frombuffer(raw[n*8:],dtype='<i4').copy()
