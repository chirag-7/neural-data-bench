import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline

def fit_predict(train_x, train_y, test_x):
    # Deterministic seed for reproducibility
    RANDOM_SEED = 42
    np.random.seed(RANDOM_SEED)  # For numpy random state

    # Robust median imputation for train/test leakage safety
    imputer = SimpleImputer(strategy='median')
    scaler = RobustScaler()

    # Prepare hyperparameter grid
    max_depth_grid = [3,5,7,9,13,17,21]
    best_macro_f1 = -np.inf
    best_max_depth = None

    # Impute and fit scaler on train data only
    train_x_imp = imputer.fit_transform(train_x)
    scaler.fit(train_x_imp)
    train_x_scaled = scaler.transform(train_x_imp)

    # Hyperparameter search with StratifiedKFold for macro F1
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    for md in max_depth_grid:
        oof_preds = np.zeros(train_y.shape, dtype=int)
        for fold, (tr_idx, va_idx) in enumerate(skf.split(train_x_scaled, train_y)):
            X_tr, X_va = train_x_scaled[tr_idx], train_x_scaled[va_idx]
            y_tr = train_y[tr_idx]

            clf = RandomForestClassifier(
                n_estimators=100,
                max_depth=md,
                class_weight='balanced',
                random_state=RANDOM_SEED
            )
            clf.fit(X_tr, y_tr)
            preds_va = clf.predict(X_va)
            oof_preds[va_idx] = preds_va
        macro_f1 = f1_score(train_y, oof_preds, average='macro')
        if macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_max_depth = md

    # Build final pipeline with the best max_depth
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler()),
        ('clf', RandomForestClassifier(
            n_estimators=100,
            max_depth=best_max_depth,
            class_weight='balanced',
            random_state=RANDOM_SEED
        ))
    ])
    pipeline.fit(train_x, train_y)

    # Predict test data
    preds = pipeline.predict(test_x)
    return preds.astype(int)
