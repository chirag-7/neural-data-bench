"""Auditable API-generation extension evaluator. Never writes original experiment paths.

--freeze seals this runner, original adapters/scorers/protocols/data and runtime.
--one TASK SLICE MODEL runs once; prediction procedure and scoring are separate
processes. The procedure has a 180-second wall timeout (including setup), scorer
1800 seconds. Initial failures remain immutable. No auto-repair or regeneration.
AST checks are contract checks, not a security sandbox: run trusted reviewed code.
"""
from pathlib import Path
import argparse, ast, datetime, hashlib, importlib.metadata, importlib.util
import json, os, platform, subprocess, sys, time, traceback
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'experiments/generation-extension-v1'
SEAL = BASE / 'execution-seal.json'
MODELS = ['gpt-4.1-2025-04-14', 'gpt-5-2025-08-07']
BATCH = {'A15', 'B03', 'C06', 'E06', 'K05', 'K06'}
GROUPED = {'H02', 'K04', 'M01'}
RUNTIME_PACKAGES = ['numpy', 'scipy', 'scikit-learn', 'pandas', 'h5py', 'spikeinterface']

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')

def runtime():
    return dict(python=sys.version, executable=str(Path(sys.executable).resolve()),
                platform=platform.platform(), executable_sha256=sha(Path(sys.executable).resolve()),
                packages={p: importlib.metadata.version(p) for p in RUNTIME_PACKAGES},
                package_entry_sha256={p: sha(importlib.util.find_spec(p).origin) for p in ['numpy', 'scipy', 'sklearn', 'pandas', 'h5py', 'spikeinterface']})

def manifest():
    return json.loads((BASE / 'manifest.json').read_text())

def entry(task, sid, model):
    assert model in MODELS, model
    found = next(t for t in manifest()['tasks'] if t['benchmark_id'] == task)
    assert sid in found['original_slices'], (task, sid)
    return found

def files_to_seal():
    paths = {Path(__file__).resolve(), BASE / 'manifest.json', ROOT / 'results/measurements.jsonl'}
    for t in manifest()['tasks']:
        task = t['benchmark_id']; d = ROOT / f'experiments/{task}'
        paths.add(ROOT / t['prompt_file'])
        # Original source and descriptive contracts, excluding generated submissions.
        for p in d.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('gpt-') and p.suffix in {'.py', '.md', '.json', '.txt'}:
                paths.add(p)
        if task == 'C05':
            paths.update((ROOT / 'data/cache/spikefinder').glob('*.csv'))
        elif task == 'M04': paths.add(ROOT / 'data/cache/cognitive-v1.npz')
        elif task in {'B07', 'B08'}:
            m = ROOT / f'data/manifests/{task}.json'; paths.add(m)
            paths.update(ROOT / f['path'] for f in json.loads(m.read_text())['files'])
        elif task == 'N05':
            paths.update(ROOT / f'data/cache/N05/{n}' for n in ['fixture.nwb', 'expected.json', 'tolerances.json'])
        elif task == 'B01':
            paths.update(ROOT / f'data/cache/B01/{n}' for n in ['inputs.npz', 'truth.npz'])
        else:
            for cache in (ROOT / 'data/cache').glob(task + '*'):
                for name in ['data.npz', 'metadata.json']:
                    if (cache / name).exists(): paths.add(cache / name)
        m = ROOT / f'data/manifests/{task}.json'
        if m.exists(): paths.add(m)
    for name in ['expansion.py', 'evaluate.py', 'workflow.py']:
        paths.add(ROOT / 'scripts' / name)
    return sorted(paths)

def freeze():
    if SEAL.exists(): raise FileExistsError('Execution seal exists; preserve it')
    for t in manifest()['tasks']:
        assert sha(ROOT / t['prompt_file']) == t['prompt_sha256']
        for specpath in (ROOT / f'experiments/{t["benchmark_id"]}').rglob('run-spec.json'):
            spec = json.loads(specpath.read_text())
            for name, digest in spec.get('frozen_files', {}).items():
                assert sha(ROOT / name) == digest, 'Original frozen input changed: ' + name
    value = dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 policy='One initial attempt; 180 seconds procedure, 1800 seconds scorer; independent saved-payload decode',
                 b08_amendment='heapq is additionally allowed, matching the explicit repaired harness; original prompt bytes unchanged',
                 files={str(p.relative_to(ROOT)): sha(p) for p in files_to_seal()}, runtime=runtime())
    dump(SEAL, value)
    return dict(seal_file=str(SEAL.relative_to(ROOT)), seal_sha256=sha(SEAL), n_files=len(value['files']))

def check(task=None):
    seal = json.loads(SEAL.read_text())
    assert runtime() == seal['runtime'], 'Runtime changed after seal'
    # Every case checks shared runner, central source ledger, task and slice sources/data.
    for name, digest in seal['files'].items():
        if task and not (name.startswith(f'experiments/{task}/') or name.startswith(f'data/cache/{task}') or task == 'C05' and name.startswith('data/cache/spikefinder/') or task == 'M04' and name == 'data/cache/cognitive-v1.npz' or name.startswith('scripts/') or name in {'results/measurements.jsonl', 'experiments/generation-extension-v1/manifest.json', f'data/manifests/{task}.json'}):
            continue
        assert sha(ROOT / name) == digest, 'Sealed file changed: ' + name
    if task in {'B07', 'B08'}:
        for f in module(task).manifest()['files']: assert sha(ROOT / f['path']) == f['sha256']
    return seal

def module(task, name='adapter', sid=None):
    if task == 'E01' and sid in {'area2_bump', 'dmfc_rsg'}: name = f'slices/{sid}/adapter'
    if task == 'E06' and sid == 'taxis': name = 'slices/taxis/adapter'
    p = ROOT / f'experiments/{task}/{name}.py'
    spec = importlib.util.spec_from_file_location('extension_' + task + '_' + name.replace('/', '_'), p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def submission(task, model):
    path = BASE / 'submissions' / task / (model + '.json')
    obj = json.loads(path.read_text())
    assert isinstance(obj['code'], str) and isinstance(obj['description'], str)
    return path, obj

def namespace(task, code):
    allowed = {'numpy', 'scipy', 'sklearn', 'math', 'collections', 'functools', 'itertools', 'statistics', 'gc'}
    if task in {'B07', 'B08'}: allowed |= {'zlib', 'bz2', 'lzma', 'struct', 'json', 'io', 'base64'}
    if task == 'B08': allowed.add('heapq')
    if task == 'N05': allowed = {'numpy', 'h5py', 'math', 'json', 're', 'collections', 'functools', 'itertools', 'statistics'}
    for n in ast.walk(ast.parse(code)):
        if isinstance(n, ast.Import) and any(v.name.split('.')[0] not in allowed for v in n.names): raise ValueError('Disallowed import')
        if isinstance(n, ast.ImportFrom) and (n.module or '').split('.')[0] not in allowed: raise ValueError('Disallowed import')
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'open', 'exec', 'eval', 'compile', '__import__', 'input', 'breakpoint'}: raise ValueError('Disallowed call')
    ns = {}; exec(compile(code, 'extension-generated', 'exec'), ns)
    return ns

def folder(task, sid, model): return BASE / 'artifacts' / task / model / sid

def load(task, sid):
    if task == 'C05':
        import pandas as pd
        get = lambda k: pd.read_csv(ROOT / f'data/cache/spikefinder/{sid}.{k}.csv').to_numpy(float)
        return get('train.calcium'), get('train.spikes'), get('test.calcium'), get('test.spikes')
    return module(task, sid=sid).load()

def groups(task):
    if task in GROUPED: return module(task).train_groups().copy()
    if task in {'C06', 'K05', 'K06'}:
        with np.load(ROOT / f'data/cache/{task}/data.npz') as z:
            g = z['train_groups'].copy()
            if task == 'K05': return dict(group_ids=g, block_ids=z['train_blocks'].copy())
            if task == 'K06': return dict(group_ids=g, cv_fold=z['train_cv_fold'].copy())
            return g
    return None

def procedure(task, sid, model):
    check(task); d = folder(task, sid, model); path, obj = submission(task, model)
    code = obj['code']; ns = namespace(task, code); (d / 'submission.py').write_text(code)
    np.random.seed(0); began = time.perf_counter()
    if task in {'B07', 'B08'}:
        a = module(task); arrays = a.load(); items = []
        for j, (array, src) in enumerate(zip(arrays, a.manifest()['files'])):
            t = time.perf_counter()
            b = ns['compress'](array.copy()) if task == 'B07' else ns['compress'](array[0].copy(), array[1].copy())
            enc = time.perf_counter() - t
            if not isinstance(b, (bytes, bytearray, memoryview)): raise ValueError('Encoder must return bytes-like')
            b = bytes(b); p = d / f'{j:02d}.bin'; p.write_bytes(b)
            decoder = namespace(task, code)['decompress']; t = time.perf_counter()
            decoded = decoder(b, array.shape, '<i2') if task == 'B07' else decoder(b)
            dec = time.perf_counter() - t
            item = dict(recording=src['recording'], compressed_file=str(p.relative_to(ROOT)), compressed_bytes=len(b), compressed_sha256=sha(p), encode_seconds=enc, decode_seconds=dec)
            if task == 'B07':
                assert isinstance(decoded, np.ndarray) and decoded.shape == array.shape and decoded.dtype == np.dtype('<i2')
                raw = np.ascontiguousarray(decoded).tobytes(); assert raw == array.tobytes(), 'Not byte exact'
                item.update(lossless=True, origin=src['origin'], animal=src['animal'], source_sha256=src['sha256'], decoded_sha256=hashlib.sha256(raw).hexdigest())
            else:
                tt, yy = decoded; err = a.validate(tt, yy, *array)
                item.update(n_events=len(array[0]), max_timing_error_seconds=err, labels_exact=True)
            items.append(item); dump(d / 'partial-audit.json', items)
        dump(d / 'predictions.json', items)
    elif task == 'N05': dump(d / 'predictions.json', ns['extract'](str(ROOT / 'data/cache/N05/fixture.nwb')))
    else:
        if task == 'M04':
            with np.load(ROOT / 'data/cache/cognitive-v1.npz') as z: pred = ns['estimate'](z['choices'].copy(), z['rewards'].copy())
        elif task == 'L06':
            X, Y, Q = module(task).inputs(); pred = ns['sample_posterior'](X.copy(), Y.copy(), Q.copy(), 10000, 20261031)
        elif task == 'B01':
            x, fs, pos = module(task).load(); pred = ns['sort'](x.copy(), fs, pos.copy())
        else:
            x, y, xt, _ = load(task, sid)
            args = (x.copy(), y.copy(), xt.copy())
            if task in BATCH or task in GROUPED: args += (groups(task),)
            pred = ns['fit_predict'](*args)
        np.savez_compressed(d / 'predictions.npz', predictions=np.asarray(pred))
    elapsed = time.perf_counter() - began
    return dict(seconds=elapsed, submission_file=str(path.relative_to(ROOT)), submission_sha256=sha(path), code_sha256=hashlib.sha256(code.encode()).hexdigest(), description=obj['description'], code_lines=len(code.splitlines()), line_limit_compliant=len(code.splitlines()) < (180 if task == 'C05' else 240), line_limit_exclusive=180 if task == 'C05' else 240)

def audit_one(task, sid, model, index):
    check(task); d = folder(task, sid, model); _, obj = submission(task, model)
    a = module(task); array = a.load()[index]; items = json.loads((d / 'predictions.json').read_text()); item = items[index]
    p = ROOT / item['compressed_file']; assert sha(p) == item['compressed_sha256']; decoder = namespace(task, obj['code'])['decompress']
    decoded = decoder(p.read_bytes(), array.shape, '<i2') if task == 'B07' else decoder(p.read_bytes())
    if task == 'B07':
        assert isinstance(decoded, np.ndarray) and decoded.shape == array.shape and decoded.dtype == np.dtype('<i2')
        assert np.ascontiguousarray(decoded).tobytes() == array.tobytes()
        return dict(index=index, status='passed', compressed_sha256=sha(p), lossless=True)
    err = a.validate(*decoded, *array)
    return dict(index=index, status='passed', compressed_sha256=sha(p), labels_exact=True, max_timing_error_seconds=err)

def score(task, sid, model, audit_dir=None):
    check(task); d = folder(task, sid, model)
    if task in {'B07', 'B08'}:
        items = json.loads((d / 'predictions.json').read_text()); audit = json.loads((d / 'fresh-decode-audit.json').read_text())
        assert len(audit) == len(items) == (16 if task == 'B07' else 7) and all(v['status'] == 'passed' for v in audit)
        enc = sum(v['encode_seconds'] for v in items); dec = sum(v['decode_seconds'] for v in items)
        if task == 'B07': result = module(task).metric(items)
        else:
            per = [8 * v['compressed_bytes'] / v['n_events'] for v in items]
            result = dict(score=float(np.mean(per)), metric='mean_encoded_bits_per_event_50us', direction='lower', per_unit=per, n_recordings=7, n_source_animals=1, n_events=sum(v['n_events'] for v in items), max_timing_error_seconds=max(v['max_timing_error_seconds'] for v in items))
        return dict(**result, n_units=len(items), encode_seconds=enc, decode_seconds=dec, fresh_decode_audit_file=str((d / 'fresh-decode-audit.json').relative_to(ROOT)), fresh_decode_audit_sha256=sha(d / 'fresh-decode-audit.json'))
    if task == 'N05':
        from workflow import score as file_score
        return file_score(json.loads((d / 'predictions.json').read_text()))
    with np.load(d / 'predictions.npz') as z: pred = z['predictions']
    if task == 'M04':
        from evaluate import nll
        with np.load(ROOT / 'data/cache/cognitive-v1.npz') as z: truth, c, r = z['truth'], z['choices'], z['rewards']
        if pred.shape != truth.shape or not np.isfinite(pred).all() or np.any(pred < [.01, .1]) or np.any(pred > [.99, 10]): raise ValueError('Invalid parameter estimate')
        per = np.mean(np.abs(pred - truth) / [.98, 9.9], axis=1)
        return dict(score=float(per.mean()), metric='range_normalized_mae', direction='lower', per_unit=per.tolist(), per_parameter_mae=np.mean(abs(pred-truth), axis=0).tolist(), nll_per_trial=float(np.mean([nll(p, cc, rr)[0] / len(cc) for p, cc, rr in zip(pred, c, r)])), n_units=len(truth))
    if task == 'L06':
        a = module(task); _, _, Q = a.inputs(); p = (audit_dir or d) / 'scorer-audit.npz'; result = module(task, 'scorer').score(pred, a.references(), Q, p)
        return dict(**result, n_units=10, scorer_audit_file=str(p.relative_to(ROOT)), scorer_audit_sha256=sha(p))
    if task == 'B01':
        a = module(task); pred = a.validate_events(pred); sc = a.score(pred)
        return dict(score=sc['mean_gt_accuracy'], metric='mean_gt_accuracy', direction='higher', n_units=sc['n_gt_units'], per_unit=list(sc['per_gt_unit_accuracy'].values()), scoring_diagnostics=sc)
    x, y, xt, truth = load(task, sid)
    if task == 'C05':
        from evaluate import score as calcium_score
        if pred.shape != truth.shape or not np.isfinite(pred[np.isfinite(xt)]).all() or np.min(pred[np.isfinite(xt)]) < -1e-10: raise ValueError('Invalid output at finite inputs')
        return dict(**calcium_score(pred, truth), metric='median_pearson_40ms', direction='higher', n_units=truth.shape[1])
    a = module(task, sid=sid)
    if task == 'E01': return dict(score=a.score(pred, truth), metric='bits_per_spike', direction='higher', n_units=len(truth))
    if task in BATCH: return dict(**a.score(pred, truth, xt), n_units=len(truth))
    if task in GROUPED: return dict(**a.score(pred, truth), n_units=len(truth))
    from expansion import metadata, scoring
    return dict(**scoring(task, pred, truth, xt, metadata(task)), n_units=len(truth))

def env():
    value = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    # Absolute paths remain valid for fresh workers regardless of process CWD.
    work = ROOT.parents[1] / 'work'
    value['PYTHONPATH'] = os.pathsep.join(str(work / n) for n in ['cell-deps', 'pilot-deps', 'spike-deps'] if (work / n).exists())
    return value

def worker(phase, task, sid, model, timeout, index=None, log_dir=None):
    command = [sys.executable, str(Path(__file__).resolve()), '--phase', phase, task, sid, model]
    if index is not None: command += ['--index', str(index)]
    dest = (log_dir or folder(task, sid, model)) / (phase + (f'-{index:02d}' if index is not None else '') + '.log')
    try:
        p = subprocess.run(command, cwd=ROOT, env=env(), capture_output=True, text=True, timeout=timeout)
        dest.write_text(p.stdout + '\n' + p.stderr)
        if p.returncode: raise RuntimeError(p.stderr[-5000:])
        return json.loads(p.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout or b''; err = ex.stderr or b''
        dest.write_text((out.decode(errors='replace') if isinstance(out, bytes) else out) + '\n' + (err.decode(errors='replace') if isinstance(err, bytes) else err))
        raise TimeoutError(f'{phase} exceeded {timeout} seconds')

def decode_audit(task, sid, model, audit_dir=None):
    assert task in {'B07', 'B08'}
    d = audit_dir or folder(task, sid, model); result = []
    for j in range(16 if task == 'B07' else 7):
        result.append(worker('decode', task, sid, model, 180, j, log_dir=d))
        dump(d / 'fresh-decode-audit.json', result)
    return result

def one(task, sid, model):
    e = entry(task, sid, model); check(task); d = folder(task, sid, model)
    if d.exists(): raise FileExistsError('Preserve initial execution: ' + str(d))
    d.mkdir(parents=True)
    row = dict(benchmark_id=task, slice_id=sid, model=model, run_id='generation-extension-v1', status='failed', track='T3', generation_replicates=1, date=datetime.datetime.now(datetime.timezone.utc).date().isoformat(), prompt_sha256=e['prompt_sha256'], execution_seal_sha256=sha(SEAL), superiority_eligible=False, superiority_reason='One API generation; provider wrapper differs; custom slices and current strongest specialist unverified', no_new_generation=sid in {'area2_bump', 'dmfc_rsg', 'taxis'}, code_repaired=False)
    path, obj = submission(task, model)
    row.update(submission_file=str(path.relative_to(ROOT)), submission_sha256=sha(path), code_sha256=hashlib.sha256(obj['code'].encode()).hexdigest(), description=obj['description'], code_lines=len(obj['code'].splitlines()), line_limit_exclusive=180 if task == 'C05' else 240)
    row['line_limit_compliant'] = row['code_lines'] < row['line_limit_exclusive']
    dump(d / 'started.json', row)
    phase = 'procedure'
    try:
        info = worker('procedure', task, sid, model, 180); row.update(info); dump(d / 'procedure-result.json', info)
        if task in {'B07', 'B08'}: phase = 'independent_decode'; decode_audit(task, sid, model)
        phase = 'scoring'; start = time.perf_counter(); row.update(worker('score', task, sid, model, 1800)); row['scoring_seconds'] = time.perf_counter() - start
        pred = d / ('predictions.json' if task in {'B07', 'B08', 'N05'} else 'predictions.npz')
        row.update(status='measured', prediction_file=str(pred.relative_to(ROOT)), prediction_sha256=sha(pred), strict_format_compliant=row['line_limit_compliant'])
    except Exception as ex:
        row.update(failure_phase=phase, reason=str(ex))
        dump(d / 'failure.json', dict(exception_type=type(ex).__name__, traceback=traceback.format_exc()))
    dump(d / 'result.json', row)
    return row

def main():
    p = argparse.ArgumentParser(); p.add_argument('--freeze', action='store_true'); p.add_argument('--check', action='store_true'); p.add_argument('--one', nargs=3); p.add_argument('--audit-saved', nargs=3); p.add_argument('--phase', nargs=4); p.add_argument('--index', type=int)
    args = p.parse_args()
    if args.freeze: result = freeze()
    elif args.check: check(); result = dict(status='passed', seal_sha256=sha(SEAL))
    elif args.one: result = one(*args.one)
    elif args.audit_saved:
        task, sid, model = args.audit_saved; entry(task, sid, model)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        audit_dir = folder(task, sid, model) / 'audits' / stamp
        audit_dir.mkdir(parents=True, exist_ok=False)
        result = decode_audit(task, sid, model, audit_dir) if task in {'B07', 'B08'} else score(task, sid, model, audit_dir)
        dump(audit_dir / 'result.json', result)
    elif args.phase:
        phase, task, sid, model = args.phase; entry(task, sid, model)
        if phase == 'procedure': result = procedure(task, sid, model)
        elif phase == 'decode': result = audit_one(task, sid, model, args.index)
        else: result = score(task, sid, model)
    else: p.error('Choose --freeze, --check, --one, --audit-saved or worker --phase')
    print(json.dumps(result, allow_nan=False))

if __name__ == '__main__': main()
