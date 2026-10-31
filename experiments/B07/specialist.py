"""Fixed codecs selected from original benchmark families, not a SOTA search."""
from pathlib import Path
import subprocess,zlib
import numpy as np
R=Path(__file__).resolve().parents[2]
BIN=R.parents[1]/'work/wavpack-runtime/bin'
def compress(array,method):
    if method=='wavpack-high':
        return subprocess.run([str(BIN/'wavpack'),'--raw-pcm-ex=30000,16,384','-hh','-m','-q','-y','-','-o','-'],input=array.tobytes(),capture_output=True,check=True).stdout
    if method=='delta-blosc-zstd':
        from numcodecs import Blosc
        from numcodecs.blosc import set_nthreads
        set_nthreads(1);d=np.empty_like(array);d[0]=array[0];d[1:]=array[1:]-array[:-1]
        return Blosc(cname='zstd',clevel=9,shuffle=Blosc.BITSHUFFLE).encode(np.ascontiguousarray(d.T))
    return zlib.compress(array.tobytes(),9)
def decompress(blob,shape,dtype,method):
    if method=='wavpack-high':
        data=subprocess.run([str(BIN/'wvunpack'),'-r','-q','-','-o','-'],input=blob,capture_output=True,check=True).stdout
        return np.frombuffer(data,dtype=dtype).copy().reshape(shape)
    if method=='delta-blosc-zstd':
        from numcodecs import Blosc
        data=Blosc(cname='zstd',clevel=9,shuffle=Blosc.BITSHUFFLE).decode(blob)
        delta=np.frombuffer(data,dtype=dtype).reshape(shape[1],shape[0]).T
        return np.cumsum(delta,axis=0,dtype=np.int64).astype(dtype)
    return np.frombuffer(zlib.decompress(blob),dtype=dtype).copy().reshape(shape)
