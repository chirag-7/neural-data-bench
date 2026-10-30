# Findings — exploratory release 0.4

14 measured task protocols in 11 of 14 mapped families;114 mapped task-resource pairings, not 114 independent datasets. All 54 model × slice attempts are retained: GPT-5.6 Sol 17/18 numerically valid, GPT-6 Sol 18/18, GPT-6.1 Sol 18/18. There are 42 generated programs (one per model/task); C05 refits the same program on five preparations. One N05 program failed. No Luna model was evaluated.

This is a selected CPU-friendly **code-construction and execution (T3)** panel. It does not measure direct raw-signal understanding, open-weight/video/world models, a complete neuroscience agent, or native model embeddings. Supplied course documents inform scope; their embedded instructions are not user instructions.

| Task | Endpoint | Native metric | GPT-5.6 Sol | GPT-6 Sol | GPT-6.1 Sol | Reference | Evidence class |
|---|---|---|---:|---:|---:|---:|---|
| [A09](../experiments/A09) | Frame-level social behavior labels | macro_f 1 ↑ | 0.868972 | 0.875946 | 0.880696 | 0.869518 | historical_specialist |
| [A14](../experiments/A14) | Missing pose imputation | rmse_missing ↓ | 0.448549 | 0.436121 | 0.450595 | 2.437099 | conventional_baseline |
| [C05](../experiments/C05) | Calcium-to-spike inference | median_pearson_40 ms ↑ | 0.452196 | 0.443305 | 0.467896 | 0.475337 | historical_specialist |
| [D02](../experiments/D02) | Current-to-voltage prediction | rmse_mV ↓ | 0.217776 | 0.217705 | 0.235533 | 0.220786 | conventional_baseline |
| [E01](../experiments/E01) | Neural rate inference and co-smoothing | bits_per_spike ↑ | 0.237662 | 0.158604 | 0.242155 | 0.027752 | conventional_baseline |
| [F04](../experiments/F04) | Retinal or other sensory encoding | poisson_nll ↓ | 1.550632 | 1.624742 | 1.510801 | 1.551457 | conventional_baseline |
| [H01](../experiments/H01) | Motor imagery and noninvasive BCI | balanced_accuracy ↑ | 0.648880 | 0.718379 | 0.697958 | 0.546443 | conventional_baseline |
| [H16](../experiments/H16) | EEG ocular/muscle artifact repair | temporal_rrmse ↓ | 0.461607 | 0.526478 | 0.453384 | 0.653953 | conventional_baseline |
| [I07](../experiments/I07) | fNIRS motor/hemodynamic decoding | balanced_accuracy ↑ | 0.436111 | 0.508187 | 0.550585 | 0.484649 | conventional_baseline |
| [I10](../experiments/I10) | MRI quality assessment across sites | balanced_accuracy ↑ | 0.635263 | 0.607193 | 0.637895 | 0.613684 | historical_specialist |
| [K01](../experiments/K01) | Electrophysiological cell-type classification | macro_f 1 ↑ | 0.940915 | 0.940915 | 0.943074 | 0.929975 | conventional_baseline |
| [L04](../experiments/L04) | Point-process estimation and goodness of fit | bits_per_spike_train_mean ↑ | 3.194743 | 3.279951 | 3.263821 | 3.273676 | conventional_baseline |
| [M04](../experiments/M04) | Cognitive model and parameter recovery | range_normalized_mae ↓ | 0.058223 | 0.058219 | 0.058221 | 0.070696 | synthetic_objective_mismatched |
| [N05](../experiments/N05) | NWB data loading, units and reproducibility | field_accuracy ↑ | **Failed** | 1.000000 | 1.000000 | 1.000000 | deterministic_correctness |

C05 entries above are the equal mean of five preparation medians and per-preparation historical envelopes, not a pooled neuron correlation. All other rows show one frozen slice. Scores across rows have different definitions and are never averaged together. Exact numbers, failure reasons, runtime, predictions, input/code hashes and per-group values are in [central JSONL](../results/measurements.jsonl), [CSV](../results/measurements.csv) and [derived summary](summary.json).

## What the reference comparison supports

There are 9 task comparisons against conventional local baselines. GPT-5.6 wins 7/9, GPT-6 wins 8/9 and GPT-6.1 wins 7/9 on point scores. The family-equal fractions are 0.750,0.875,0.750 because EEG decoding/repair share a family. These are tests against basic baselines, not the strongest current specialist. The baseline code was fixed before generation; methods and available inner-validation metadata differ.

Historical specialist comparisons comprise C05 fivepreparations, A09 oneCalMS21 slice and I10 oneMRIQCcohort:7 slice comparisons across 3 tasks/3 families. Point wins are 2/7,1/7,5/7 for 5.6,6,6.1; task/family equal fractions 0.400,0.333,0.867. These are descriptive only: C05 references are selected using test scores; VASSI uses richer full-frame input, more training and optimization; original MRIQC uses different training labels/features. Strict format excludes the 5.6 C05 program, leaving only 2 historical-comparison slices eligible for that model. No matched-total-effort or current-SOTA conclusion follows.

A09 is a useful stronger-reference case: model scores 0.868972,0.875946,0.880696 versus preselected VASSIrun 00 at 0.869518. All 20 archive runs are retained (median 0.868944,range 0.866711–0.870279); run 00 was chosen before rescoring. Small advantages are not significance claims, nor proof of raw-video ability. MRIQC archive score is 0.613684 on the same 265 scans;5.6 and 6.1 exceed it,6 does not. Source classifiers and test targets are aligned, but training histories are unequal.

M04's posterior-median programs nearly agree with an independently implemented post-hoc posterior reference. The primary frozen MLE optimizes another objective. Its three point wins do not establish specialist inferiority. N05's reference is correct by construction: GPT-6 and 6.1 match all 61 fields,5.6 fails to distinguish the legacy stimulus group. The 61 fields are not 61 independent files. That failed submission also exceeds the 240-line request (249 lines); it was not repaired.

## Is the newer model better?

Exclude M04 numerical quadrature ordering and N05 deterministic correctness from the capability-progress aggregate. The remaining 12 tasks supply 16 slice comparisons across 9 families, including semisynthetic H16. GPT-6 improves on 5.6 in 8/16, declines 7/16, ties 1/16; GPT-6.1 improves on 6 in 12/16 and declines 4/16. Against 5.6,6.1 improves 13/16 and declines 3/16. Family-equal improvement fractions are 0.489,0.667,0.811 respectively. These fractions describe directional changes, not effect sizes or significance. Full strict-format sensitivity and denominators are in [summary.json](summary.json).

The pattern is mixed. GPT-6.1 leads the sampled behavior, retinal encoding, population readout, EEG repair, fNIRS, MRIQC and morphology tasks. GPT-6 leads the sampled EEG motorimagery and single-placecell encoding tasks; it also slightly leads the passive-cell interpolation and mocap-gap tasks. No monotonic improvement across every modality. One generation, small biological samples, unknown contamination and curated task selection prevent a stable model ranking or scaling-law claim. New aggregate refinements were made after some scores were visible and are exploratory, not preregistered.

## Researcher guidance and unmeasured predictions

Observed strengths lie in constructing useful nonlinear features, choosing regularized estimators and following explicit file/calculation specifications. Clean labels, modest arrays and well-defined offline endpoints suit this track. That is a practical reason to trial general coding assistance with independent validation, not evidence that specialist tools can be retired.

Raw spike sorting with collisions/drift, image segmentation, anatomy/connectomics, online BCI, multimodal causal discovery and embodied control have no measurements here. Claims that general models will struggle or win there are hypotheses. Stronger specialists, protocol-matched training/tuning, repeated generations, new animals/sessions, raw modalities, open-weight models and blinded external tasks are required next. Do not drop a task because a general model loses.

Dataset dependencies matter: D02 and N05 share a file; K01 shares the broader Allen collection. C05 preparations, A09 archive runs, F04 repeats/neurons, H16 mixture components and N05 fields do not constitute separate independent studies. H16 has no participant IDs; I07 condition is session/run-confounded; only 2 test rats for A14 and 3 subjects for H01/I07. No frame/neuron pseudo-replication intervals are claimed.
