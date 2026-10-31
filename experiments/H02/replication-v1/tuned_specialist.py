"""Retrospective, training-person-only xDAWN selection. Never load test labels."""
from pathlib import Path
import hashlib, importlib.metadata, json, time
import numpy as np
from pyriemann.estimation import XdawnCovariances
from pyriemann.tangentspace import TangentSpace
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

R = Path(__file__).resolve().parents[3]
D = R / 'experiments/H02/replication-v1'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def classifier(c):
    return LogisticRegression(C=c, class_weight='balanced', solver='liblinear',
                              max_iter=1000, random_state=20261030)

def representation(x, y, xt, nfilter, classes):
    cov = XdawnCovariances(nfilter=nfilter, classes=classes,
                          estimator='oas', xdawn_estimator='oas')
    tangent = TangentSpace(metric='riemann', tsupdate=False)
    scale = StandardScaler()
    a = scale.fit_transform(tangent.fit_transform(cov.fit_transform(x, y)))
    b = scale.transform(tangent.transform(cov.transform(xt)))
    return a, b

def main():
    spec = json.loads((D / 'run-spec.json').read_text())
    assert sha(Path(__file__)) == spec['sealed_files'][str(Path(__file__).relative_to(R))]
    assert sha(R / 'data/cache/H02/data.npz') == spec['data_sha256']
    # Access only these named arrays. Test targets and test person IDs are never loaded.
    with np.load(R / 'data/cache/H02/data.npz') as z:
        x, y, xt, groups = (z[k] for k in ['train_x', 'train_y', 'test_x', 'train_groups'])
    x = x.astype(float) * 1e-6
    xt = xt.astype(float) * 1e-6
    configurations = spec['specialist_grid']
    folds = list(GroupKFold(n_splits=5).split(x, y, groups))
    oof = np.full((len(configurations), len(y)), np.nan)
    fold_records = []
    start = time.perf_counter()
    for fold, (tr, va) in enumerate(folds):
        tr_groups, va_groups = np.unique(groups[tr]), np.unique(groups[va])
        assert not set(tr_groups) & set(va_groups)
        fold_records.append(dict(fold=fold, train_people=tr_groups.tolist(),
                                 validation_people=va_groups.tolist()))
        for nfilter in [2, 4]:
            for classes in [[1], [0, 1]]:
                a, b = representation(x[tr], y[tr], x[va], nfilter, classes)
                for i, config in enumerate(configurations):
                    if config['nfilter'] == nfilter and config['classes'] == classes:
                        oof[i, va] = classifier(config['C']).fit(a, y[tr]).decision_function(b)
        print('completed training-only fold', fold, flush=True)
    assert np.isfinite(oof).all()
    candidates = []
    for i, config in enumerate(configurations):
        scores = [dict(person=int(g), score=float(roc_auc_score(y[groups == g], oof[i, groups == g])))
                  for g in np.unique(groups)]
        candidates.append(dict(index=i, **config, validation_score=float(np.mean([v['score'] for v in scores])),
                               validation_people=scores))
    chosen = max(range(len(candidates)), key=lambda i: candidates[i]['validation_score'])
    selected = configurations[chosen]
    choice = dict(chosen_index=chosen, selected=selected, candidates=candidates, folds=fold_records,
                  selection='equal-person training-only OOF ROC-AUC; exact ties resolved by grid order',
                  test_labels_loaded=False, seconds_to_selection=time.perf_counter() - start)
    # Persist selection before test inference and before any scorer can access test labels.
    (D / 'selection.json').write_text(json.dumps(choice, indent=2) + '\n')
    np.savez_compressed(D / 'validation-predictions.npz', predictions=oof)
    a, b = representation(x, y, xt, selected['nfilter'], selected['classes'])
    pred = classifier(selected['C']).fit(a, y).decision_function(b)
    p = R / 'results/predictions/H02/replication-v1--xdawn-tslr-tuned.npz'
    np.savez_compressed(p, predictions=pred)
    info = dict(model='xdawn-tslr-tuned', seconds=time.perf_counter() - start,
                prediction_file=str(p.relative_to(R)), prediction_sha256=sha(p),
                selected_configuration=selected, selection_file=str((D / 'selection.json').relative_to(R)),
                selection_sha256=sha(D / 'selection.json'), test_labels_loaded=False,
                code_sha256=sha(Path(__file__)),
                packages={n: importlib.metadata.version(n) for n in ['pyriemann', 'numpy', 'scipy', 'scikit-learn']})
    (D / 'specialist-runtime.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info), flush=True)

if __name__ == '__main__':
    main()
