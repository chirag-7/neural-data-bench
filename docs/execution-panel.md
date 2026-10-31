# Executed panel

30 measured task IDs. Exact scores and caveats:[findings](../analysis/findings.md); source contracts:[experiments](../experiments/).

- [A09](../experiments/A09): CalMS21 Task 1: processed pose context at 3 Hz; 70 training and 19 test recordings.
- [A14](../experiments/A14): Rat 7 M: six-landmark, 31-frame windows with an artificial seven-frame HeadF gap; three training and two test rats.
- [B01](../experiments/B01): Blind unsupervised spike sorting of one 10-second, 32-channel stationary MEArec simulation; official unit/event matching.
- [B07](../experiments/B07): AIND/IBL original 16 recordings; fixed 4096 x 384 int16 chunks, exact-byte lossless compression;14 source animals.
- [C05](../experiments/C05): Spikefinder: calcium-to-spike inference on five preparations; median 40 ms correlation per preparation.
- [D02](../experiments/D02): One Allen cell: four training and two test negative-current sweeps; 500 Hz passive voltage interpolation.
- [E01](../experiments/E01): Neural Latents Benchmark: MC_Maze_Small, Area 2_Bump and DMFC_RSG; held-in to held-out neuron readout using unchanged generated programs.
- [F04](../experiments/F04): Goldin 2022 retina: 3, 160 training images and 30 test images repeated 30 times; 41 neurons, one preparation.
- [G01](../experiments/G01): FALCON M2 custom cross-day decoding: 1, 169 training and 754 test trials, 96 causal features, two finger-velocity outputs, one monkey.
- [H01](../experiments/H01): PhysioNet motor imagery: five training and three held-out people; 225 training and 135 test epochs.
- [H02](../experiments/H02): Brain Invaders 2012 calibration runs: 15 training and 10 held-out people; 11, 481/7, 663 epochs, 16 EEG channels; equal-person ROC-AUC.
- [H08](../experiments/H08): Sleep-EDF first nights, fixed 20: 00–08: 00 windows: five training and three held-out people; 100 Hz Fpz-Cz EEG, five sleep stages.
- [H16](../experiments/H16): EEGdenoiseNet: 2, 000 training and 600 test clean-plus-EOG mixtures, with disjoint source components.
- [I07](../experiments/I07): FRESH optical-density tapping classification: seven training and three test people; condition and session remain confounded.
- [I10](../experiments/I10): MRIQC: 600 ABIDE training scans and 265 DS030 test scans; 68 numeric quality metrics and rater-1 exclusion labels.
- [J08](../experiments/J08): SynAPSeg 2 D puncta: 27 training fields yielding 1, 262 crops; two held-out whole fields, five expert masks each; archived StarDist reference.
- [K01](../experiments/K01): Allen mouse electrophysiology: 11 features predict spiny/aspiny morphology; donor-disjoint 1, 356 training and 457 test cells.
- [K04](../experiments/K04): DLPFC HumanPilot donor-held-out expression-to-layer transfer; two train donors/eight sections versus one test donor/four sections;500 genes.
- [L06](../experiments/L06): All ten original sbibm Bernoulli GLM observations; known design/likelihood/prior,10,000 posterior draws each;2,000-draw C2 ST primary.
- [L04](../experiments/L04): One rat place cell: 20 ms spike counts predicted from position and velocity; chronological 60/40 split with a one-second gap.
- [M01](../experiments/M01): IBL real conditional choices;83 train/17 test mice, nonoverlapping six-trial target/history blocks and known experimenter blockprior.
- [M04](../experiments/M04): Synthetic two-choice Q-learning agents: recover learning rate and inverse temperature from choices and rewards.
- [N05](../experiments/N05): One real legacy Allen NWB file, shared with D02: extract 61 deterministic fields covering six sweeps.

C05 has five preparations; E01 has three official source slices, all reusing original programs. B01 post-hoc event F1 is a separate sensitivity, not another independent task or a changed primary. H02 passes training-person IDs explicitly. Budget/memory/adaptation limits are part of each contract.

## Batch 0.11 additions

- [B03](../experiments/B03): Eight complete noisy SpikeInterface simulations, four train/four test; rigid motion from processed detected-peak rasters, explicitly synthetic.
- [B08](../experiments/B08): Seven complete FALCON M2 spike-event streams, one monkey; 50-us timing-lossy compression with exact labels/order. Two whitelist failures retained; whole task retrospectively excluded from aggregates.
- [C06](../experiments/C06): All CASCADE DS04 cells/recordings; two training/two test fish; native-rate smoothed spike counts. Primary Pearson accompanied by count error/bias.
- [E06](../experiments/E06): One ZAPBench brain, 256 neurons, 43 main and 12 unseen-taxis windows; same programs reused on dependent slices.
- [K05](../experiments/K05): Orthogonal Circle-panel fractions from anonymous bulk-expression columns; five training/three test donors, with block/replicate-aware scoring.
- [K06](../experiments/K06): Allen-only PV/SST waveform classification; 11 training/five test mice, 136/71 cells.
- [A15](../experiments/A15): Complete numeric acoustic recordings from three training birds/one test bird, 60/20 recordings; annotated-event F1. GPT-5.6's numeric output is line-noncompliant.

Current totals are 30 task IDs, 37 slices per model and 111 attempts: 107 numeric outputs and four execution failures. Strict-format-valid counts are 28 / 36 / 36. [Current release](release-v11.md). The dated release snapshots below are historical, not current totals.

## Separate H02 generation follow-up (0.7)

Six new submissions plus one train-only CV-selected specialist are retained in the [separate ledger](../results/replications/H02.json). Original attempt 1 is included for context, giving three attempts per model on the same dataset. These do not increase first-submission macro denominators. The historical 19-task/75-attempt 0.7 snapshot is preserved. Preview 0.8 added K04/M01 to reach 21 tasks/81 attempts; preview 0.9 adds L06 to reach 22 tasks/84 attempts. [Plan, outcomes and verification](../experiments/H02/replication-v1/results.md).

Preview 0.9 adds L06 as one synthetic posterior task, giving 22 tasks/84 first-submission attempts. The three generated programs pass all strict runtime/format rules. Local Polya–Gamma and Laplace references share the same inputs. The prior 0.8 ledger and H02 follow-up remain unchanged.

Preview 0.10 adds B07, giving 23 tasks/111 first-submission attempts. Its 16 per-recording outputs count as one task/slice, not 16 independent tasks. The previous 0.9 ledger is preserved.

## Preview 0.11 parallel batch

Seven new task IDs add eight slices and 21 generated programs, with 24 model/slice attempts and 11 reference outputs. E06 taxis reuses the original programs unchanged. All 35 new records, including two B08 whitelist failures, remain in the ledger. Independent audits verify saved outputs and original source/scorer identities; A15 GPT-5.6 numeric validity does not override its line-limit violation. Central totals are 30 tasks, 37 slices/model and 111 attempts (107 numerically valid, four failed), with 90 original programs.

- [A15](../experiments/A15): 80 whole recordings: 60 from three training birds, 20 from one unseen test bird; 1,519 test annotated events.
- [B03](../experiments/B03): Eight independent 90-second simulations, 64 contacts/neurons; four train and four test recordings.
- [B08](../experiments/B08): All seven original G01 FALCON M2 recordings: 1,052,545 events, four days, one monkey.
- [C06](../experiments/C06): All 15 neurons / 45 recordings, 81.66 minutes; two training and two held-out test fish.
- [E06](../experiments/E06): One zebrafish brain/session; 272 training windows, 43 temporal-tail tests and 12 unseen-taxis tests; same programs reused.
- [K05](../experiments/K05): 63 eligible bulk samples: 39 train/24 test, five/three donors and seven/four blocks.
- [K06](../experiments/K06): 207 cells from 16 mice: 136 train/11 mice, 71 test/five mice.

[Full native results, limitations and audits](batch-v11.md). The central analysis and website update once per audited batch.
