"""H02 follow-up: immutable originals, two fresh generations, separate results."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
import numpy as np
from expansion import ROOT as R, WORK, MODELS, adapter, sha, validate_code

D = R / 'experiments/H02/replication-v1'
P = R / 'experiments/H02'
L = R / 'results/generation/H02-replication-v1'
CLI = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
ENV = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
           VECLIB_MAXIMUM_THREADS='1', MKL_NUM_THREADS='1')

def freeze():
    files = [D / 'amendment.md', D / 'tuned_specialist.py', Path(__file__),
             P / 'prompt.txt', P / 'response_schema.json', P / 'adapter.py']
    spec = dict(benchmark_id='H02', study='replication-v1', date='2026-10-30',
                status='retrospective follow-up frozen before new generation or tuned-reference fit',
                original_test_results_already_known=True, models=MODELS, new_replicates=[2, 3],
                original_replicate=1, reasoning_effort='high', timeout_seconds=180,
                line_limit_exclusive=240, memory_enforced=False,
                generation_max_wall_seconds=600, no_feedback=True,
                data_sha256=sha(R / 'data/cache/H02/data.npz'),
                sealed_files={str(p.relative_to(R)): sha(p) for p in files},
                specialist_grid=[dict(nfilter=n, classes=classes, C=c)
                                 for n in [2, 4] for classes in [[1], [0, 1]] for c in [.1, 1, 10]],
                original_macro_records_unchanged=True)
    (D / 'run-spec.json').write_text(json.dumps(spec, indent=2) + '\n')

def verify_seal():
    spec = json.loads((D / 'run-spec.json').read_text())
    for p, value in spec['sealed_files'].items():
        assert sha(R / p) == value, p
    assert sha(R / 'data/cache/H02/data.npz') == spec['data_sha256']
    return spec

def generate():
    verify_seal()
    jobs = []
    for replicate in [2, 3]:
        for model in MODELS:
            name = f'{model}--r{replicate}'
            out = D / 'generated' / (name + '.json')
            log = L / (name + '.jsonl')
            cwd = WORK / 'erp-replication-contexts' / name
            cwd.mkdir(parents=True, exist_ok=False)
            assert not out.exists() and not log.exists(), 'Never overwrite a generation attempt'
            command = [CLI, 'exec', '--ephemeral', '--ignore-user-config', '--skip-git-repo-check',
                       '--sandbox', 'read-only', '--model', model, '-c', 'model_reasoning_effort=high',
                       '--output-schema', str(P / 'response_schema.json'),
                       '--output-last-message', str(out), '--json', '-']
            stream = log.open('w')
            err = (L / (name + '.infrastructure.txt')).open('w')
            with (P / 'prompt.txt').open() as inp:
                process = subprocess.Popen(command, stdin=inp, stdout=stream, stderr=err, text=True, cwd=cwd)
            jobs.append((name, process, stream, err, time.monotonic()))
    for name, process, stream, err, start in jobs:
        try:
            process.wait(timeout=max(.1, 600 - (time.monotonic() - start)))
            code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            code = 'generation_timeout'
        stream.close()
        err.close()
        (L / (name + '.exit.json')).write_text(json.dumps(dict(exit_code=code)) + '\n')
        print(name, 'generation_exit', code, flush=True)

def one(model, replicate):
    verify_seal()
    output = D / 'generated' / f'{model}--r{replicate}.json'
    obj = json.loads(output.read_text())
    code = obj['code']
    validate_code(code)
    ns = {}
    exec(compile(code, str(output), 'exec'), ns)
    a = adapter('H02')
    x, y, xt, truth = a.load()
    groups = a.train_groups()
    np.random.seed(0)
    start = time.perf_counter()
    pred = np.asarray(ns['fit_predict'](x.copy(), y.copy(), xt.copy(), groups.copy()))
    seconds = time.perf_counter() - start
    scored = a.score(pred, truth)
    path = R / 'results/predictions/H02' / f'replication-v1--{model}--r{replicate}.npz'
    np.savez_compressed(path, predictions=pred)
    return dict(benchmark_id='H02', study='replication-v1', model=model, replicate=replicate,
                status='measured', seconds=seconds, code_sha256=hashlib.sha256(code.encode()).hexdigest(),
                code_lines=len(code.splitlines()), line_limit_compliant=len(code.splitlines()) < 240,
                description=obj['description'], prediction_file=str(path.relative_to(R)),
                prediction_sha256=sha(path), original_macro_eligible=False, **scored)

def evaluate():
    verify_seal()
    rows = []
    for replicate in [2, 3]:
        for model in MODELS:
            name = f'{model}--r{replicate}'
            log = L / (name + '.evaluation.txt')
            try:
                p = subprocess.run([sys.executable, str(Path(__file__)), 'one', '--model', model,
                                    '--replicate', str(replicate)], capture_output=True, text=True,
                                   env=ENV, timeout=180)
                log.write_text(p.stdout + '\n' + p.stderr)
                if p.returncode:
                    raise RuntimeError(p.stderr[-2000:])
                row = json.loads(p.stdout.strip().splitlines()[-1])
            except Exception as ex:
                row = dict(benchmark_id='H02', study='replication-v1', model=model,
                           replicate=replicate, status='failed', reason=str(ex), original_macro_eligible=False)
            rows.append(row)
            (D / 'new-attempts.json').write_text(json.dumps(rows, indent=2) + '\n')
            print(name, row['status'], row.get('score'), flush=True)

def specialist():
    verify_seal()
    log = D / 'specialist-execution.txt'
    try:
        p = subprocess.run([sys.executable, str(D / 'tuned_specialist.py')], env=ENV,
                           capture_output=True, text=True, timeout=180)
        log.write_text(p.stdout + '\n' + p.stderr)
        if p.returncode:
            raise RuntimeError(p.stderr[-2000:])
        info = json.loads((D / 'specialist-runtime.json').read_text())
        with np.load(R / info['prediction_file']) as z:
            pred = z['predictions']
        row = dict(benchmark_id='H02', study='replication-v1', status='measured',
                   original_macro_eligible=False, **info, **adapter('H02').score(pred, adapter('H02').load()[3]))
    except Exception as ex:
        row = dict(model='xdawn-tslr-tuned', status='failed', reason=str(ex), original_macro_eligible=False)
    (D / 'specialist-result.json').write_text(json.dumps(row, indent=2) + '\n')
    print('tuned-specialist', row['status'], row.get('score'), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'generate', 'one', 'evaluate', 'specialist'])
    parser.add_argument('--model')
    parser.add_argument('--replicate', type=int)
    args = parser.parse_args()
    if args.action == 'one':
        print(json.dumps(one(args.model, args.replicate)))
    else:
        globals()[args.action]()
