# M01: held-out-mouse conditional choice prediction

## Scientific question and source

Predict the probability of a real mouse's next choice given its current visual stimulus, known experimenter block probability and five observed past choices/feedbacks. This is a conditional one-step forecast, not cognitive parameter recovery, multi-step rollout, neural decoding or a causal model of decision making.

Original data: [IBL December2019 behavior release](https://figshare.com/articles/dataset/11636748),228602597-byte source ZIP, publisher MD5 verified, CC BY4.0 explicitly identified by original Figshare API. The retained original README warns of beta quality/missing events. No automatic inference that these data meet a current release's quality policies. Paper: [A standardized and reproducible method to measure decision-making in mice](https://elifesciences.org/articles/63711). Original [GLM source](https://github.com/int-brain-lab/paper-behavior/blob/24b094226a84c8609c97cfd36c8387ea7c5d61e0/figure5_GLM_modelfit.py) supplies the reference's stimulus/history/block basis; MIT author-code license retained separately from CC BY data terms.

## Selection before scores

Inventory every source choice file. For each globally named mouse choose its latest structurally complete session by date,run,lab, requiring choice,left/right contrast,feedback and block-prior arrays. Do not select by accuracy, trial inclusion, training status, observed model performance or contrast difficulty. Use first≤1000source trials. This retains all100archived animals, across nine labs. Hash `M01-v1:` plus mouse name to partition modulo5:0test,otherwise train. Result83train/17test mice. Both groups contain the same nine labs; this is **not held-out-lab validation**.

Divide each session into nonoverlapping six-trial blocks. Target original indices5,11,17,...; preceding five trials are permitted history. Exclude target nonresponses (choice0),invalid blockprior or both-current-contrasts missing. Absent-side contrast NaN becomes0. Past invalid/nonresponse choices become0; missing past feedback becomes0. Retain all other eligible targets. Result7696training/1842test examples. Preserve target/history source indices and each selected member's SHA256. Source feedback/reward fields from the target trial are never predictors.

**Leakage control:** no scored target can be part of another example's history, in either partition. This prevents batch reconstruction of scored test labels through a later row's past-choice field. Rows must not be joined, ordered or matched across examples by generated procedures. Observed histories are supplied once perindependent conditional prediction; they are not generated model rollouts.

## Contract

`fit_predict(train_x,train_y,test_x,train_groups)` returns one finite probability in[0,1] pertest row. Label1=sourcechoice+1(turnCW),label0=sourcechoice-1(turnCCW). Models learn how stimulus sign maps to that convention.13features: contrastLeft,contrastRight,probabilityLeft,past choice lags1..5,past feedback lags1..5. Current contrast/prior are0..1; choice/feedback histories -1/0/+1. Experimenter block probability is privileged task metadata, not an explicitly cued animal observation; it is provided equally to all methods.

Training mouse IDs support grouped validation. Test mouse IDs and all targets remain scorer-only. No identifiers,current/future response,feedback,reaction time,session quality or inclusion flag is a predictor. Fit normalization,imputation and supervised tuning on training mice only; fixed perrow features permitted. No test-fitted adaptation.

Primary: binary negative log-likelihood averaged within each test mouse, then equally across17mice. Clip probabilities to[1e-6,1−1e-6] only in the fixed scorer. Lower is better. Pooled loss/accuracy are secondary. Constant0.5 and oracle fixtures validate scoring only, not model/reference results.

## Fixed references and model procedure

Conventional baseline predicts the training mean choice probability.

Named domain reference: **paper-inspired behavioral GLM**. Signed categorical contrast coefficients for all observed nonzero training contrasts; previous-choice×rewarded and previous-choice×unrewarded terms; centered block prior; intercept. Logistic regression C=1e6 approximates unpenalized MLE,lbfgs,max_iter1000,seed20261030; equal total weight pertraining mouse. Train once on all training mice. This is a pooled transfer adaptation of the original peranimal GLM, not a reproduction of the original paper's fitted parameters or published performance. It deliberately uses only lag1 as in that basis; all five lags remain available as common data to all methods. No test-driven tuning.

One high-reasoning, no-tool/no-feedback submission perexact requested Sol version. General NumPy/SciPy/sklearn imports only, no specialized package/weights/network/files during generation; code fewer than240lines;180second one-thread numerical subprocess budget,requested4GB not enforced. Retain failures and formatting deviations without repair. Freeze all scientific artifacts and both reference definitions before any generation or fitted-method test score. Same runtime ceiling does not establish matched total development or tuning effort.

## Limits

One historical public archive, one selected session peranimal, modest event counts and nine overlapping labs. Target histories and known blockprior define a narrower conditional task than autonomous prediction from stimuli alone. Outcomes reflect behavior, not neural dynamics or recovered latent parameters. No current-SOTA, unseen-laboratory or universal scaling claim.
