import numpy as np
from sklearn.neighbors import KNeighborsRegressor

def fit_predict(train_x, train_y, test_x):
    # Landmark indices (each has x, y, z):
    # HeadF=0, HeadB=1, HeadL=2, SpineF=3, SpineM=4, SpineL=5
    # Features: [HeadF_x, HeadF_y, HeadF_z, HeadB_x, ..., SpineL_z] -> 6*3=18
    # Masked HeadF frames: indices 12:19
    HEADF_IDX = 0
    HEADF_COORDS = [0,1,2]
    MASK_START, MASK_END = 12, 19  # 7-frame gap (inclusive)

    # Features to use for KNN predictors: all except HeadF (coords 3:18)
    FEAT_IDX = list(range(3, 18))
    n_neighbors = 5

    n_test, n_time, n_feat = test_x.shape
    test_pred = np.copy(test_x)

    # Precompute train predictors and mask for animal separation
    # All train_x and train_y come from animals 1-3; test_x is from animals 4-5.
    # So, it's enough just to fit on all train windows.
    
    # For each masked frame
    for t in range(MASK_START, MASK_END+1):
        # Prepare predictors/targets for this frame
        X_train = train_x[:, t, FEAT_IDX].copy()       # (Ntrain, 15)
        y_train = train_y[:, t, :3].copy()             # (Ntrain, 3)

        # Exclude training samples with any missing predictors or targets
        mask = (~np.isnan(X_train).any(axis=1)) & (~np.isnan(y_train).any(axis=1))
        X_train_valid = X_train[mask]
        y_train_valid = y_train[mask]  # (n_valid, 3)

        # Prepare test predictors for this frame
        X_test = test_x[:, t, FEAT_IDX].copy()   # (Ntest, 15)

        # For each HeadF coordinate (x, y, z), fit a separate regressor
        for i in range(3):
            y_train_coord = y_train_valid[:, i]
            # Only fit/predict if y_train_coord has enough samples
            if X_train_valid.shape[0] >= n_neighbors:
                knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights='uniform', metric='minkowski', p=2)
                knn.fit(X_train_valid, y_train_coord)
                # Predict for all test set
                y_pred = knn.predict(X_test)
            else:
                # Not enough data, fall back to global mean (from train set, for this coordinate)
                finite = np.isfinite(y_train_coord)
                y_pred = np.full(X_test.shape[0], np.nanmean(y_train_coord[finite]))
            # Place predictions into output at masked slots
            test_pred[:, t, i] = y_pred
    # At this point, masked HeadF positions (coords 0,1,2 at frames 12:19) have been imputed.
    return test_pred
