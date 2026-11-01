import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV

def fit_predict(train_x, train_y, test_x):
    # 1. Impute missing values (median imputation trained only on train_x)
    imputer = SimpleImputer(strategy='median')
    train_x_imp = imputer.fit_transform(train_x)
    test_x_imp = imputer.transform(test_x)

    # 2. Robust scaling (scale using train-set median/IQR only)
    scaler = RobustScaler()
    train_x_scaled = scaler.fit_transform(train_x_imp)
    test_x_scaled = scaler.transform(test_x_imp)

    # 3. Set up balanced random forest classifier
    rf = RandomForestClassifier(
        n_estimators=100,  # reasonable tradeoff time/variance
        class_weight='balanced',
        random_state=42,
        n_jobs=1  # keep deterministic resource usage
    )

    # 4. Hyperparameter grid (avoid overfitting)
    param_grid = {
        'max_depth': [3, 5, 7, None],
        'min_samples_leaf': [1, 5, 10]
    }
    # 5 stratified folds for validation with balanced accuracy
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(
        rf,
        param_grid=param_grid,
        scoring='balanced_accuracy',
        cv=cv,
        n_jobs=1,
        refit=True
    )
    grid.fit(train_x_scaled, train_y)
    best_model = grid.best_estimator_

    # 5. Predict with optimal model
    y_pred = best_model.predict(test_x_scaled)
    # We require integer output.
    y_pred = y_pred.astype(int)
    return y_pred
