import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score

# CONSTANTS
LANDMARKS = ["nose","left_ear","right_ear","neck","left_hip","right_hip","tail_base"]
NUM_LANDMARKS = 7
MICE = 2
COORDS = 2  # x/y
time_offsets = np.array([-15, -5, -1, 0, 1, 5, 15])
SEED = 42

# Helper utility to unflatten a (7 temporal,28) input to (7 temporal,2 mice,2 coords,7 lms)
def unflatten_pose(x):
    # Input: (win,28)
    # Output: (win,2,2,7)
    return x.reshape((x.shape[0], MICE, COORDS, NUM_LANDMARKS))

def get_features(batch_x):
    # batch_x: (N,7,28)
    N = batch_x.shape[0]
    features = []
    for i in range(N):
        seq = unflatten_pose(batch_x[i])        # (7,2,2,7)
        feats = []
        ref_idx = 3  # offset 0 (center)
        # Positions at each time offset
        poses = seq # (win,2,2,7)
        # Animal body part statistics
        for t in range(poses.shape[0]):
            # For each animal per time step
            for m in range(2):
                # Keypoint positions (2,7)
                xys = poses[t,m] #(2,7)
                # Pairwise distances between bodyparts (21 upper triangle)
                pdists = np.linalg.norm(xys[:,None,:]-xys[:,:,None],axis=0)
                udist = pdists[np.triu_indices(NUM_LANDMARKS,1)]
                feats.extend(udist)
            # Between-animal measures
            # Central points
            for lm in [0,3,6]:  # nose, neck, tail base
                xy0 = poses[t,0,:,lm]
                xy1 = poses[t,1,:,lm]
                d = np.linalg.norm(xy0-xy1)
                feats.append(d)
        # Nose to nose distances across window
        noses0 = poses[:,0,:,0]  # (win,2)
        noses1 = poses[:,1,:,0]
        nose2nose = np.linalg.norm(noses0-noses1,axis=1) #(win,)
        feats.extend([
            nose2nose[3],          # at center
            nose2nose.min(),
            nose2nose.max(),
            nose2nose.std(),
         ])
        # For the focal frame, compute mouse1->mouse2 nose-neck-tail vectors
        for msrc in [0,1]:
            mtgt = 1-msrc
            for m in [msrc,mtgt]:
                nose = poses[3,m,:,0]
                neck = poses[3,m,:,3]
                tail = poses[3,m,:,6]
                # Body axis vector (nose-tail)
                body_vec = tail - nose
                feats.extend(body_vec)
                head_vec = nose - neck
                # body angle
                angle = np.arctan2(body_vec[1],body_vec[0])
                feats.append(angle)
                # head angle
                hangle = np.arctan2(head_vec[1],head_vec[0])
                feats.append(hangle)
            # nose-nose vector
            n0 = poses[3,msrc,:,0]
            n1 = poses[3,mtgt,:,0]
            v = n1-n0
            feats.extend(v)  # x,y
            normv = np.linalg.norm(v)
            feats.append(normv)
        # Displacements (frame-to-frame motion)
        for m in [0,1]:
            noses = poses[:,m,:,0]
            disp = np.diff(noses,axis=0) #(6,2)
            # 2-norm of displacements (velocity)
            norms = np.linalg.norm(disp,axis=1)
            vstat = [disp.mean(), disp.std(), norms.mean(), norms.std()]
            feats.extend(vstat)
        # Temporal context differences (nose-to-nose at each offset relative to center)
        nn_center = nose2nose[3]
        diffs = nose2nose-nn_center
        feats.extend(diffs)
        features.append(feats)
    return np.array(features, dtype=np.float32)

def fit_predict(train_x, train_y, test_x):
    np.random.seed(SEED)
    train_feat = get_features(train_x)
    test_feat = get_features(test_x)
    # Model
    model = HistGradientBoostingClassifier(max_iter=150, random_state=SEED, max_leaf_nodes=15, learning_rate=0.15, l2_regularization=2.0, min_samples_leaf=24)
    # Simple CV for model confidence
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    val_scores = []
    for train_idx, val_idx in skf.split(train_feat, train_y):
        model_c = HistGradientBoostingClassifier(max_iter=150, random_state=SEED, max_leaf_nodes=15, learning_rate=0.15, l2_regularization=2.0, min_samples_leaf=24)
        model_c.fit(train_feat[train_idx], train_y[train_idx])
        val_pred = model_c.predict(train_feat[val_idx])
        val_scores.append(f1_score(train_y[val_idx], val_pred, average="macro"))
    # Fit full model
    model.fit(train_feat, train_y)
    preds = model.predict(test_feat)
    return preds
