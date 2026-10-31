"""Fixed original AIND byte chunks; no simulated inputs or label split."""
from pathlib import Path
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parents[2]
def manifest():return json.loads((R/'data/manifests/B07.json').read_text())
def load():
    arrays=[]
    for row in manifest()['files']:
        raw=(R/row['path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        arrays.append(np.frombuffer(raw,dtype='<i2').copy().reshape(4096,384))
    return arrays
def metric(items):
    assert len(items)==16 and all(x['lossless'] for x in items)
    bits=[8*x['compressed_bytes']/(4096*384) for x in items]
    return dict(score=float(np.mean(bits)),metric='encoded_bits_per_int16_sample',direction='lower',per_unit=bits,
                compression_ratio=float(16/np.mean(bits)),raw_bits_per_sample=16,
                all_recordings_byte_exact=True,n_recordings=16,n_source_animals=14)
