"""Frozen CPU-sized adaptation of original sbibm C2ST, plus sliced W2."""
from pathlib import Path
import numpy as np
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPClassifier

def validate(pred):
    pred=np.asarray(pred)
    if pred.shape!=(10,10000,10) or not np.isfinite(pred).all():
        raise ValueError('Require finite posterior draws with shape(10,10000,10)')
    return pred

def sliced_w2(pred,ref,precision):
    eig,U=np.linalg.eigh(precision);root=(U*np.sqrt(eig))@U.T
    rng=np.random.default_rng(1729);dirs=rng.standard_normal((10,128));dirs/=np.linalg.norm(dirs,axis=0)
    projection=root@dirs
    return np.sqrt(np.mean((np.sort(pred@projection,axis=0)-np.sort(ref@projection,axis=0))**2))

def diagnostics(draws):
    half=len(draws)//2;chains=np.stack([draws[:half],draws[-half:]])
    W=chains.var(axis=1,ddof=1).mean(axis=0);B=half*chains.mean(axis=1).var(axis=0,ddof=1)
    rhat=np.sqrt(((half-1)/half*W+B/half)/np.maximum(W,1e-30))
    a=draws[:-1]-draws[:-1].mean(axis=0);b=draws[1:]-draws[1:].mean(axis=0)
    ac=(a*b).sum(axis=0)/np.maximum(np.sqrt((a*a).sum(axis=0)*(b*b).sum(axis=0)),1e-30)
    return dict(mean=draws.mean(axis=0).tolist(),sd=draws.std(axis=0,ddof=1).tolist(),
                split_chain_rhat=rhat.tolist(),lag_one_correlation=ac.tolist(),
                caution='One chain split in two; not independent-chain convergence certification')

def score(pred,ref,precision,audit_path):
    pred=validate(pred);n=4000;fold_predictions=np.empty((10,n),dtype=np.int8)
    labels=np.r_[np.zeros(2000,dtype=np.int8),np.ones(2000,dtype=np.int8)]
    fold_ids=np.empty(n,dtype=np.int8);all_scores=[];all_folds=[];distances=[];diag=[]
    for j in range(10):
        A=ref[j,::5].astype(np.float32);B=pred[j,::5].astype(np.float32)
        center=A.mean(axis=0);scale=A.std(axis=0,ddof=1)
        if not np.isfinite(scale).all() or np.any(scale<=0):raise ValueError('Invalid reference variance')
        data=np.concatenate([(A-center)/scale,(B-center)/scale]);scores=[]
        for k,(train,test) in enumerate(KFold(5,shuffle=True,random_state=1).split(data)):
            clf=MLPClassifier(activation='relu',hidden_layer_sizes=(100,100),max_iter=10000,
                              solver='adam',random_state=1)
            clf.fit(data[train],labels[train]);guess=clf.predict(data[test]).astype(np.int8)
            fold_predictions[j,test]=guess;fold_ids[test]=k;scores.append(float(np.mean(guess==labels[test])))
        all_folds.append(scores);all_scores.append(float(np.float32(np.mean(scores))))
        distances.append(float(sliced_w2(pred[j],ref[j],precision)));diag.append(diagnostics(pred[j]))
        print('scored_observation',j+1,'c2st',all_scores[-1],flush=True)
    audit_path=Path(audit_path);audit_path.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(audit_path,predicted_class=fold_predictions,true_class=labels,fold_id=fold_ids,
                        fold_accuracy=np.asarray(all_folds),per_observation_c2st=np.asarray(all_scores))
    return dict(score=float(np.mean(all_scores)),metric='c2st_accuracy_2000',direction='lower',
                chance_target=.5,per_unit=all_scores,per_observation_sliced_w2=distances,
                sliced_w2=float(np.mean(distances)),posterior_diagnostics=diag,
                metric_scope='Custom 2000-draw C2ST; original simulator-only SBI leaderboard not reproduced')
