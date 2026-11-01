import numpy as np
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif

# Deterministic seed
RANDOM_STATE = 42

# Feature selection parameters
N_FEATURES = 120

# The main function
def fit_predict(train_x, train_y, test_x):
    # Reshape (n_trials, 136, 8) -> (n_trials, 136*8) = (n_trials, 1088)
    n_train = train_x.shape[0]
    n_test = test_x.shape[0]
    train_x_flat = train_x.reshape((n_train, -1))
    test_x_flat = test_x.reshape((n_test, -1))

    # Standardize (mean=0, std=1) using only the training set statistics
    scaler = StandardScaler()
    train_x_std = scaler.fit_transform(train_x_flat)
    test_x_std = scaler.transform(test_x_flat)

    # Univariate feature selection (top N_FEATURES)
    selector = SelectKBest(f_classif, k=N_FEATURES)
    train_x_sel = selector.fit_transform(train_x_std, train_y)
    test_x_sel = selector.transform(test_x_std)

    # Linear SVM, balanced classes, deterministic
    clf = LinearSVC(class_weight='balanced', dual=False, max_iter=10000, random_state=RANDOM_STATE)
    clf.fit(train_x_sel, train_y)
    pred_y = clf.predict(test_x_sel)

    # Return as integer numpy array
    return pred_y.astype(int)

# End of code.
