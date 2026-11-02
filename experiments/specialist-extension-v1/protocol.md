# Specialist extension v1: prospective implementation/budget record

The original general-model scores and first specialist analysis are already known. This is an explicitly **post-hoc reference extension**, not a preregistered unbiased comparison. The code and data hashes below are sealed before executing any new reference on test targets. New references are never retuned after seeing test scores. Runtime failures can be repaired only with recorded old/new hashes and reasons.

All model inputs, train/test boundaries, expected outputs, scorers and equal-slice task means remain unchanged. Models receive train_x, train_y and test_x only; training-group IDs are used for validation only where the original interface provided them. G01's original interface does not provide group IDs: its model intentionally ignores them and uses chronological training validation. Test targets are only loaded by the scoring stage after predictions are saved. Original per-task source/protocol caveats remain applicable.

## New fixed procedures

| Task | Reference | Evidence class / material adaptations |
|---|---|---|
| A14 | DISK-style bidirectional GRU | Official GRU core port, summed directions, hidden64; zero initial state, interpolation-residual target and body-centering, six-landmark mask indicators; a local adaptation, not a released checkpoint or full DISK pipeline. |
| A15 | Official TweetyNet network class | Source-pinned PyTorch class; small8/16 convolution filters and hidden32; 129-bin256-sample STFT,1ms hop,128ms windows; 3,000 deterministic training chunks maximum; binary activity rather than syllable identities. |
| D02 | Passive two-exponential charging response | Nonnegative resistance components, tau1–500ms, training-only least squares; canonical mechanistic/domain reference, not a learned biophysical specialist checkpoint. |
| E01 | Low-dimensional Poisson recurrent population model | Bidirectional GRU32, latent8, log-linear held-out-neuron rates; published neural latent-model principles, not LFADS/GPFA software or leaderboard reproduction. All three existing source slices required. |
| E06 | ZAPBench NLinear architecture | Source-audited shared64→32 affine map with last-frame normalization and constant initialization, PyTorch port trained with Adam rather than original JAX infrastructure. Same model jointly predicts both original test slices. |
| F04 | Static convolutional retinal encoding model | Two softplus convolutions16channels (5×5,3×3) and per-neuron log-rate readout, Poisson likelihood; source-inspired static encoding model, not OpenRetina checkpoint or temporal stimulus model. |
| G01 | FALCON-style ridge decoder | Train-only standardization; alpha selected from1,10,100,1000,10000 on last20% chronological training rows, then refit on all training data; no cross-row test state or test calibration. |
| H16 | EEGdenoiseNet simple_CNN | Port of pinned official architecture: four64-channel kernel3 conv/BN/ReLU/dropout0.3 blocks, flatten+dense512; same original mixture/source split. |
| I07 | Hemodynamic temporal-pattern LDA | Channel mean and late-minus-early optical-density features, training-only scaling and shrinkage LDA; domain-statistical adaptation, not hemoglobin reconstruction or foundation model. |
| K06 | WaveMAP UMAP/Louvain + label transfer | Amplitude-normalized81 waveform points, training-only UMAP15neighbors and Louvain resolution1.5; training genetic labels map clusters with inverse-class weights, five nearest train embeddings transfer to new cells. This supervised outer task differs from the source unsupervised taxonomy. |
| L04 | Spline Poisson place-field GLM | Position cubic splines8knots with movement-direction interactions; alpha from0.0001,0.001,0.01,0.1 selected on chronological training holdout, then full training refit. Local canonical neural GLM, not NeMoS package execution. |

For neural networks, seed20261102, CPU only, one PyTorch/numerical thread, Adam0.001, gradient norm cap5, maximum140seconds of optimization and bounded epochs. Select checkpoint by training-validation loss, never test scores. Validation uses held-out training groups when available, otherwise every fifth training example; retinal validation groups identical training images together. Training validation is retained rather than refitting the selected checkpoint on those examples. This uses less fitting data than some general procedures, and must remain explicit. Best-source performance is not established by these short-budget adaptations. The process allowance is210seconds to cover imports; measured fit/predict may not exceed180seconds to qualify as a matched-budget run. Actual timing, steps and exceptions are recorded.

A15 thresholds0.3,0.5,0.7 are selected on validation-frame F1; fill ≤4ms gaps and remove <10ms segments, fixed before evaluation. Audio predictions preserve original1ms rasterization and event scorer. The official TweetyNet class is executed from the pinned vendored source; source licenses are retained. D02, G01, I07 and L04 are conventional/domain models and are not relabeled as packaged specialists.

## Remaining audit decisions

M01's existing scored source-inspired behavioral GLM and M04's existing objective-aligned quadrature posterior median are audited domain references; neither is promoted to a pretrained specialist. K01's small anonymous electrophysiology-feature classifier has strong conventional controls but no verified task-specific released model matching its label/input contract. K05 lacks gene identity/reference profiles required by the nominated deconvolution tools; adding those changes the information contract. N05 is deterministic legacy-NWB extraction; a parser correctness control is appropriate, not a trained predictive-specialist claim. These gaps must remain visible unless new matched evidence is actually obtained.

No new general-model calls, changed labels, test-selected hyperparameters, data splits or deleted failures are authorized by this extension. A failed or poor specialist is retained. Results may support local comparisons, not a claim that current best neuroscience methods were comprehensively reproduced.
