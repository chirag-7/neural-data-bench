import struct, zlib, heapq, numpy as np
_H=1<<31; _Q=1<<30; _T=3<<30; _M=(1<<32)-1
class _E:
    def __init__(self):
        self.lo=0; self.hi=_M; self.pending=0
        self.buf=bytearray(); self.cur=0; self.nb=0
    def _out(self,b):
        self.cur=(self.cur<<1)|b; self.nb+=1
        if self.nb==8:
            self.buf.append(self.cur); self.cur=0; self.nb=0
    def _emit(self,b):
        self._out(b)
        while self.pending:
            self._out(1-b); self.pending-=1
    def put(self,a,b,total):
        r=self.hi-self.lo+1
        self.hi=self.lo+(r*b//total)-1
        self.lo=self.lo+(r*a//total)
        while True:
            if self.hi<_H: self._emit(0)
            elif self.lo>=_H:
                self._emit(1); self.lo-=_H; self.hi-=_H
            elif self.lo>=_Q and self.hi<_T:
                self.pending+=1; self.lo-=_Q; self.hi-=_Q
            else: break
            self.lo=(self.lo<<1)&_M
            self.hi=((self.hi<<1)&_M)|1
    def finish(self):
        self.pending+=1; self._emit(0 if self.lo<_Q else 1)
        if self.nb: self.buf.append(self.cur<<(8-self.nb))
        return bytes(self.buf)
class _D:
    def __init__(self,data):
        self.data=data; self.pos=0; self.mask=0
        self.lo=0; self.hi=_M; self.code=0
        for _ in range(32): self.code=(self.code<<1)|self._in()
    def _in(self):
        if not self.mask:
            self.byte=self.data[self.pos] if self.pos<len(self.data) else 0
            self.pos+=1; self.mask=128
        b=1 if self.byte&self.mask else 0; self.mask>>=1
        return b
    def target(self,total):
        r=self.hi-self.lo+1
        return ((self.code-self.lo+1)*total-1)//r
    def take(self,a,b,total):
        r=self.hi-self.lo+1
        self.hi=self.lo+(r*b//total)-1
        self.lo=self.lo+(r*a//total)
        while True:
            if self.hi<_H: pass
            elif self.lo>=_H:
                self.lo-=_H; self.hi-=_H; self.code-=_H
            elif self.lo>=_Q and self.hi<_T:
                self.lo-=_Q; self.hi-=_Q; self.code-=_Q
            else: break
            self.lo=(self.lo<<1)&_M
            self.hi=((self.hi<<1)&_M)|1
            self.code=((self.code<<1)&_M)|self._in()
def _tree(a):
    n=len(a); b=[0]*(n+1)
    for i in range(1,n+1):
        b[i]+=int(a[i-1]); j=i+(i&-i)
        if j<=n: b[j]+=b[i]
    return b
def _add(b,i,x):
    i+=1
    while i<len(b): b[i]+=x; i+=i&-i
def _sum(b,i):
    s=0
    while i: s+=b[i]; i-=i&-i
    return s
def _find(b,x):
    i=0; step=1<<((len(b)-1).bit_length()-1)
    while step:
        j=i+step
        if j<len(b) and b[j]<=x: i=j; x-=b[j]
        step>>=1
    return i
def _put(a,x):
    x=int(x)
    while x>=128: a.append((x&127)|128); x>>=7
    a.append(x)
def _get(a,p):
    x=0; s=0
    while True:
        c=a[p]; p+=1; x|=(c&127)<<s
        if c<128: return x,p
        s+=7
def _gamma_e(e,x):
    q=x.bit_length()-1
    for _ in range(q): e.put(0,1,2)
    e.put(1,2,2)
    for s in range(q-1,-1,-1):
        b=(x>>s)&1; e.put(b,b+1,2)
def _bit_d(d):
    b=d.target(2); d.take(b,b+1,2); return b
def _gamma_d(d):
    q=0
    while _bit_d(d)==0: q+=1
    x=1<<q
    for s in range(q-1,-1,-1): x|=_bit_d(d)<<s
    return x
def compress(times, labels):
    t=np.asarray(times,dtype=np.float64).reshape(-1)
    y=np.asarray(labels,dtype=np.int32).reshape(-1)
    n=len(t)
    if len(y)!=n: raise ValueError('length mismatch')
    origin=float(t[0]) if n else 0.0
    ticks=np.floor((t-origin)*10000.0+0.5).astype(np.int64)
    vals=np.unique(y).astype('<i4'); k=len(vals)
    ids=np.searchsorted(vals,y).astype(np.int64) if n else np.empty(0,np.int64)
    counts=np.bincount(ids,minlength=k).astype(np.int64).tolist()
    last=[None]*k; refr=[None]*k
    for q in range(n):
        j=int(ids[q]); u=int(ticks[q]); old=last[j]
        if old is not None:
            gap=u-old
            if refr[j] is None or gap<refr[j]: refr[j]=gap
        last[j]=u
    refr=[0 if x is None else x for x in refr]
    delta=np.empty(n,dtype=np.int64)
    if n:
        delta[0]=ticks[0]; delta[1:]=ticks[1:]-ticks[:-1]
    dc=[0]*257
    for x in delta: dc[min(int(x),256)]+=1
    m=bytearray(); _put(m,n); m.extend(struct.pack('<d',origin)); _put(m,k)
    m.extend(vals.tobytes())
    for x in counts: _put(m,x)
    for x in refr: _put(m,x)
    for x in dc: _put(m,x)
    zm=zlib.compress(bytes(m),9); head=bytearray(b'B8'); _put(head,len(zm)); head.extend(zm)
    if not n: return bytes(head)
    e=_E(); dtree=_tree(dc); rem=counts[:]; ltree=_tree(rem)
    pending=[]; tick=0
    for q in range(n):
        x=int(delta[q]); c=min(x,256); total=n-q
        a=_sum(dtree,c); e.put(a,a+dc[c],total)
        dc[c]-=1; _add(dtree,c,-1)
        if c==256: _gamma_e(e,x-255)
        tick+=x
        while pending and pending[0][0]<=tick:
            _,j=heapq.heappop(pending); _add(ltree,j,rem[j])
        j=int(ids[q]); total=_sum(ltree,k); a=_sum(ltree,j)
        e.put(a,a+rem[j],total); _add(ltree,j,-1); rem[j]-=1
        if refr[j] and rem[j]:
            _add(ltree,j,-rem[j]); heapq.heappush(pending,(tick+refr[j],j))
    head.extend(e.finish()); return bytes(head)
def decompress(blob):
    if not isinstance(blob,(bytes,bytearray,memoryview)): raise TypeError('blob')
    b=bytes(blob)
    if b[:2]!=b'B8': raise ValueError('bad blob')
    zlen,p=_get(b,2); meta=zlib.decompress(b[p:p+zlen]); payload=b[p+zlen:]
    p=0; n,p=_get(meta,p); origin=struct.unpack_from('<d',meta,p)[0]; p+=8
    k,p=_get(meta,p)
    vals=np.frombuffer(meta,dtype='<i4',count=k,offset=p).copy(); p+=4*k
    counts=[]; refr=[]
    for _ in range(k): x,p=_get(meta,p); counts.append(x)
    for _ in range(k): x,p=_get(meta,p); refr.append(x)
    dc=[]
    for _ in range(257): x,p=_get(meta,p); dc.append(x)
    if not n: return np.empty(0,np.float64),np.empty(0,np.int32)
    d=_D(payload); dtree=_tree(dc); rem=counts[:]; ltree=_tree(rem)
    pending=[]; ticks=np.empty(n,np.int64); ids=np.empty(n,np.int64); tick=0
    for q in range(n):
        total=n-q; v=d.target(total); c=_find(dtree,v); a=_sum(dtree,c)
        d.take(a,a+dc[c],total); dc[c]-=1; _add(dtree,c,-1)
        x=c if c<256 else 255+_gamma_d(d); tick+=x; ticks[q]=tick
        while pending and pending[0][0]<=tick:
            _,j=heapq.heappop(pending); _add(ltree,j,rem[j])
        total=_sum(ltree,k); v=d.target(total); j=_find(ltree,v); a=_sum(ltree,j)
        d.take(a,a+rem[j],total); ids[q]=j; _add(ltree,j,-1); rem[j]-=1
        if refr[j] and rem[j]:
            _add(ltree,j,-rem[j]); heapq.heappush(pending,(tick+refr[j],j))
    times=origin+ticks.astype(np.float64)*0.0001
    labels=vals[ids].astype(np.int32,copy=False)
    return times,labels