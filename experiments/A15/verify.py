"""Independent raw-source, units, split, rasterization, and toy scorer audit; no methods."""
from pathlib import Path
import csv,hashlib,io,json,tarfile,importlib.util
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CACHE=ROOT/'data/cache/A15'
def run():
    manifest=json.loads((HERE/'source.json').read_text())
    for row in manifest['files']:
        p=ROOT/row['path'];raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        check=row.get('upstream_checksum')
        if check and check['type'].upper()=='MD5':assert hashlib.md5(raw).hexdigest()==check['value']
    assert hashlib.sha256((CACHE/'data.npz').read_bytes()).hexdigest()==manifest['prepared']['sha256']
    das=json.loads((CACHE/'das-dataset-metadata.json').read_text())['data'];original=json.loads((CACHE/'original-figshare-metadata.json').read_text())
    assert das['license']['rightsIdentifier']=='CC0-1.0' and original['license']['name']=='CC BY 4.0'
    source_files=das['files'];names=[]
    for bird in ['bl26lb16','gr41rd51','gy6or6','or60yw70']:
        selected=sorted([f['label'] for f in source_files if f['label'].startswith(bird+'_') and f['label'].endswith('.npz')],key=lambda x:hashlib.sha256(x.encode()).hexdigest())[:20];names.extend(selected)
    with tarfile.open(CACHE/'source-gy6or6-260312.tar.gz') as t:
        p='gy6or6/032612/gy6or6_baseline_260312_0907.3729.wav.csv';raw=t.extractfile(p).read();orig=list(csv.DictReader(io.StringIO(raw.decode())))
    converted=list(csv.DictReader((CACHE/'gy6or6_baseline_260312_0907.3729_annotations.csv').open()));a=sorted(converted,key=lambda r:float(r['start_seconds']));b=sorted(orig,key=lambda r:float(r['onset_s']))
    assert len(a)==len(b)==90 and [r['name'] for r in a]==[r['label'] for r in b]
    a_times=np.array([[float(r['start_seconds']),float(r['stop_seconds'])] for r in a])/1000;b_times=np.array([[float(r['onset_s']),float(r['offset_s'])] for r in b]);np.testing.assert_allclose(a_times,b_times,rtol=0,atol=1e-12)
    with np.load(CACHE/'data.npz',allow_pickle=False) as z:d={k:z[k] for k in z.files}
    records=json.loads((CACHE/'row-manifest.json').read_text());assert len(records)==80 and sorted(r['recording']+'.npz' for r in records)==sorted(names)
    assert set(d['train_groups'])=={'bl26lb16','gr41rd51','gy6or6'} and set(d['test_groups'])=={'or60yw70'}
    assert set(d['train_units']).isdisjoint(d['test_units']);event_count=0
    for split in ['train','test']:
        rows=[r for r in records if r['split']==split];assert [r['recording'] for r in rows]==d[split+'_units'].tolist()
        for i,r in enumerate(rows):
            with np.load(CACHE/(r['recording']+'.npz'),allow_pickle=False) as z:
                wave=z['data'];assert wave.dtype==np.float16 and int(z['samplerate'])==32000
            n=len(wave);np.testing.assert_array_equal(d[split+'_x'][i,:n],wave.astype(np.float32));assert np.isnan(d[split+'_x'][i,n:]).all()
            ann=list(csv.DictReader((CACHE/(r['recording']+'_annotations.csv')).open()));events=np.array(sorted((float(z['start_seconds'])/1000,float(z['stop_seconds'])/1000) for z in ann));event_count+=len(events)
            actual=d[split+'_events'][i];actual=actual[np.isfinite(actual[:,0])];np.testing.assert_array_equal(actual,events)
            centres=(np.arange(n//32)+.5)/1000;mask=np.any((centres[:,None]>=events[:,0]-1e-12)&(centres[:,None]<events[:,1]-1e-12),axis=1).astype(np.int8)
            np.testing.assert_array_equal(d[split+'_y'][i,:len(mask)],mask);assert np.all(d[split+'_y'][i,len(mask):]==-1)
    assert event_count==6935
    spec=importlib.util.spec_from_file_location('adapter',HERE/'adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    assert adapter.event_f1([[.11,.19]],[[.1,.2]])[0]==1.
    assert abs(adapter.event_f1([[.1,.2],[.1,.2]],[[.1,.2]])[0]-2/3)<1e-12
    assert adapter.event_f1([[.121,.2]],[[.1,.2]])[0]==0.
    assert adapter.event_f1([[.1,.221]],[[.1,.2]])[0]==0.
    assert adapter.event_f1([[.1,1.29]],[[.1,1.1]])[0]==1.
    report=dict(benchmark_id='A15',status='prepared and verified; not frozen',source_files_verified=len(manifest['files']),source_md5_verified=True,license_checks=['DAS CC0-1.0','Original CC BY4.0'],unit_verification=dict(original_events=90,all_labels_match=True,max_error_seconds=float(np.max(abs(a_times-b_times))),factor_from_mislabeled_DAS_columns=.001),n_whole_recordings=80,source_events=event_count,train_birds=3,test_birds=1,checks=['Deterministic filename-hash selection','No source recording or bird crosses outer split','Every raw waveform and valid/padding sample reconstructed','All original event bounds and1ms target rasterization reconstructed','Toy one-to-one matching and onset/offset tolerances'],method_runs=0,model_calls=0,real_slice_method_scores=0)
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':run()
