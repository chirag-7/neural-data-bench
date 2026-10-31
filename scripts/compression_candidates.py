"""Frozen B07 codec experiment; never repair a generated submission."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
from expansion import ROOT as R,MODELS
D=R/'experiments/B07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name):
    s=importlib.util.spec_from_file_location('b07_'+name,D/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def code_namespace(code):
    allowed={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc','zlib','bz2','lzma','struct','json','io','base64'}
    for n in ast.walk(ast.parse(code)):
        if isinstance(n,ast.Import) and any(x.name.split('.')[0] not in allowed for x in n.names):raise ValueError('Disallowed import')
        if isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] not in allowed:raise ValueError('Disallowed import')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','eval','exec','compile','__import__','input','breakpoint'}:raise ValueError('Disallowed call')
    ns={};exec(compile(code,'generated-codec','exec'),ns);return ns
def check():
    spec=json.loads((D/'run-spec.json').read_text())
    for name,h in spec['frozen_files'].items():assert sha(R/name)==h,name
    return spec
def freeze():
    assert not any(D.glob('gpt-*.json')) and not (R/'results/B07.json').exists()
    a=module('adapter');arrays=a.load();assert len(arrays)==16
    prompt='''Single-shot neuroscience lab codec code-construction experiment. Do not call tools, browse, read files or execute during generation. Return only JSON fields description and code.

Implement compress(array)->bytes and decompress(blob,shape,dtype)->numpy.ndarray.

Compress real Neuropixels voltage losslessly. Each call receives one C-contiguous int16 array shape(4096,384): rows are time,columns are channels,original little-endian signed16bit ADC counts. Evaluate all16 experimental source recordings,one fixed short chunk each,allchannels. Approximately0.137seconds perchunk,nominal30kHz. Source identities/labels are not predictors. No training/calibration data,source bytes or validation feedback are supplied during generation.

The decoded array must have the supplied shape and dtype (dtype string '<i2') and EXACTLY reproduce every original byte. shape/dtype are shared decoder arguments available equally to all methods and not charged as external metadata. EVERY byte of your returned blob counts,including mode selectors/headers. Codec implementation source is shared and not charged perchunk. You may use reversible transforms,channel/time reordering,predictors,entropy coding or choose among allowed standard codecs based on the current input. No lossy filtering,resampling,quantization,discarded samples/channels or learned external dictionaries. Decoder starts in a fresh namespace;it cannot access the encoder input,state or globals cached by compress. No crosschunk state or input-data lookup allowed.

Primary metric:mean encodedbits perraw scalarint16 sample over16recordings,lowerbetter. Raw storage16bits/sample. All16must decode exactly for a valid primary. Secondary encoding/decoding throughput is recorded,but quality/size is primary.

Allowed imports numpy,scipy,sklearn,math,collections,functools,itertools,statistics,gc,zlib,bz2,lzma,struct,json,io,base64. No specialist packages (no numcodecs,WavPack,Blosc),file/network/subprocess access,dynamic exec/eval,pretrainedassets or external data. BytesIO for in-memory serialization allowed. Keep all source below240lines including blanks. Deterministic implementation. One submission,no execution feedback. The entire encode+decode workload for ALL16chunks must finish in180seconds on one numerical CPUthread;approximately4GB memory requested,not enforced. Avoid pathological high-complexity predictors or codec-search loops. Runtime numpy2.3.5/scipy1.18.1/sklearn1.9.1 with standardlibrarycompression. Return concise description and complete self-contained Python code. Do not claim a score.
'''
    (D/'prompt.txt').write_text(prompt)
    (D/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
    paths=[D/n for n in ['adapter.py','specialist.py','protocol.md','runtime.json','prompt.txt','response_schema.json']]+[Path(__file__).resolve(),R/'data/manifests/B07.json']
    spec=dict(benchmark_id='B07',run_id='compression-v1',date='2026-10-31',track='T3',models=MODELS,reasoning_effort='high',generation_replicates=1,timeout_seconds=180,line_limit_exclusive=240,memory_enforced=False,
              adapter_sha256=sha(D/'adapter.py'),prompt_sha256=sha(D/'prompt.txt'),
              frozen_files={str(p.relative_to(R)):sha(p) for p in paths},status='frozen before generation and every real-slice method score')
    (D/'run-spec.json').write_text(json.dumps(spec,indent=2)+'\n');print('B07 frozen',flush=True)
def one(model):
    spec=check();a=module('adapter');arrays=a.load();source=a.manifest()['files'];general=model in MODELS;info={}
    if general:
        obj=json.loads((D/(model+'.json')).read_text());code=obj['code'];ns=code_namespace(code);enc=ns['compress'];(D/(model+'.py')).write_text(code)
        info=dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240)
    else:
        specialist=module('specialist');enc=lambda x:specialist.compress(x,model)
        info=dict(code_sha256=sha(D/'specialist.py'),selection='Fixed before any generation or real-slice method score')
    folder=R/f'results/bitstreams/B07/{model}';folder.mkdir(parents=True,exist_ok=True);items=[]
    for j,(array,src) in enumerate(zip(arrays,source)):
        start=time.perf_counter();blob=enc(array.copy());encode_s=time.perf_counter()-start
        if not isinstance(blob,(bytes,bytearray,memoryview)):raise ValueError('Encoder must return bytes-like data')
        blob=bytes(blob);bp=folder/f'{j:02d}.bin';bp.write_bytes(blob)
        if general:decoder=code_namespace(code)['decompress']
        else:decoder=lambda b,s,d:specialist.decompress(b,s,d,model)
        start=time.perf_counter();decoded=decoder(blob,array.shape,'<i2');decode_s=time.perf_counter()-start
        if not isinstance(decoded,np.ndarray) or decoded.shape!=array.shape or decoded.dtype!=np.dtype('<i2'):raise ValueError('Wrong decoder shape/dtype')
        raw=np.ascontiguousarray(decoded).tobytes();lossless=raw==array.tobytes()
        item=dict(recording=src['recording'],origin=src['origin'],animal=src['animal'],compressed_file=str(bp.relative_to(R)),compressed_bytes=len(blob),compressed_sha256=sha(bp),decoded_sha256=hashlib.sha256(raw).hexdigest(),source_sha256=src['sha256'],lossless=lossless,encode_seconds=encode_s,decode_seconds=decode_s)
        items.append(item);(folder/'partial-audit.json').write_text(json.dumps(items,indent=2)+'\n')
        if not lossless:raise ValueError('Not byte-exact on recording '+str(j))
    metric=a.metric(items);p=R/f'results/predictions/B07/compression-v1--{model}.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(items,indent=2)+'\n')
    enc=sum(v['encode_seconds'] for v in items);dec=sum(v['decode_seconds'] for v in items);raw_bytes=sum(v['bytes'] for v in source)
    return dict(benchmark_id='B07',slice_id='compression-v1',model=model,status='measured',date='2026-10-31',track='T3' if general else 'reference',reference_type='local_specialist_reproduction' if model in ['wavpack-high','delta-blosc-zstd'] else 'local_reproduction',n_units=16,seconds=enc+dec,encode_seconds=enc,decode_seconds=dec,compression_MB_s=raw_bytes/enc/1e6,decompression_MB_s=raw_bytes/dec/1e6,prediction_file=str(p.relative_to(R)),prediction_sha256=sha(p),prompt_sha256=spec['prompt_sha256'],truth_type='original_experimental_voltage_bytes',superiority_eligible=False,superiority_reason='Custom shortchunks; no streaming/global-best/equal-implementation-effort claim',**info,**metric)
def evaluate():
    p=R/'results/B07.json';rows=json.loads(p.read_text()) if p.exists() else [];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
    for model in MODELS+['wavpack-high','delta-blosc-zstd','task-baseline']:
        assert not any(r['model']==model for r in rows),'Preserve existing attempts'
        log=R/f'results/execution/B07-compression-v1-{model}.txt'
        try:
            out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',model],capture_output=True,text=True,env=env,timeout=180);log.write_text(out.stdout+'\n'+out.stderr)
            if out.returncode:raise RuntimeError(out.stderr[-2200:])
            row=json.loads(out.stdout.strip().splitlines()[-1])
        except Exception as ex:row=dict(benchmark_id='B07',slice_id='compression-v1',model=model,status='failed',date='2026-10-31',reason=str(ex))
        rows.append(row);p.write_text(json.dumps(rows,indent=2)+'\n');print(model,row['status'],row.get('score'),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze()
    elif sys.argv[1]=='one':print(json.dumps(one(sys.argv[2])))
    else:evaluate()
