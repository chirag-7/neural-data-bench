# Electrical and human/mesoscopic imaging admission review — v0.4

Checked on **2026-10-30**. This bounded review covers **H01–H19 and I01–I09**; I10 is maintained by the central coordinator. It screens whether particular public resources support auditable local experiments. It is not an exhaustive literature search, a claim of complete field coverage, or a PRISMA-compliant review.

The [machine-readable decisions](admission-v04-electrical.json) contain a concrete reason, primary sources, license/access evidence, remaining gate and check date for every one of the 28 entries. The [query and access log](searches-v04-electrical.jsonl) preserves the actual search strings and source attempts, including timeouts, publisher redirects and failed filename guesses. Failed web-tool access is distinguished from successful direct-file acquisition.

## What was admitted

Three explicit slices have local data, frozen preparation code, documented splits, fixed numerical references and acquisition hashes. Six umbrella/tool entries remain **source-only**; nineteen are **deferred** behind specified gates. These labels concern execution admission, not the scientific value of the resource. No candidate is permanently rejected merely because the full dataset is large or this review did not implement its adapter.

| Entry | Executable slice | Independent unit and main boundary |
|---|---|---|
| [H01](../experiments/H01/protocol.md) | PhysioNet left/right motor imagery; 5 training and 3 held-out participants; 24 original EDF files | Participant holdout; only one small dataset slice, with no population-wide or current-SOTA claim |
| [H16](../experiments/H16/protocol.md) | EEGdenoiseNet EOG-mixture repair; 2000 training and 600 held-out component pairs | Disjoint component rows; participant identities unavailable; semisynthetic target |
| [I07](../experiments/I07/protocol.md) | FRESH two-second left/right finger tapping; 7 training and 3 held-out participants | Participant holdout; condition is blocked by recording session |

These are **T3 code-generation experiments with external numerical fitting**. Model outputs are executable estimators; they are not demonstrations of language models directly reading long neural recordings in their context windows. Shared preparation constrains the tested problem and does not evaluate every step of a laboratory workflow. Numerical model comparisons belong in the [central results](../results/) and analysis, separately from this admission review.

## Motor imagery: a concrete split, not an imported leaderboard

The original [PhysioNet EEGMMI v1.0.0 record](https://physionet.org/content/eegmmidb/1.0.0/) provides real multichannel EEG, embedded task labels and ODC-By-1.0 terms. H01 uses only unilateral **imagery** runs, maps event meanings using the run condition, delays epochs after cue onset, and holds out complete participants. Channels, sampling frequency, finite epochs and participant separation are checked during preparation.

The [MOABB PhysionetMI page](https://moabb.neurotechx.com/docs/generated/moabb.datasets.PhysionetMI.html) and [MNE CSP example](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html) support task interpretation and the traditional CSP/LDA reference. Their published/tutorial scores use other splits or conditions. They cannot supply a same-protocol “current best” number for this custom eight-person slice. Its three held-out participants are the units for population-generalization uncertainty; 135 trials are not 135 independent people.

## EEGdenoiseNet: known source recovery is not pristine physiology

The [original EEGdenoiseNet paper](https://arxiv.org/html/2009.11662v4) describes real EEG/EOG components that were preprocessed and inspected, then linearly mixed for evaluation. The EEG target itself reflects algorithmic cleaning and expert selection. A known clean component is a valid reconstruction target for this construction; it is not an independent, pristine measurement of latent neural physiology during real simultaneous artifact contamination.

H16 pins the [original repository](https://github.com/ncclabsustech/EEGdenoiseNet) at commit `8d290661146c7189c98cc04812d37371d4b9426c`. Components are split before mixing; neither source indices nor exact duplicate component bytes cross the split. No physiological component is reused to manufacture independent SNR replications. This establishes **component disjointness**, not participant or source-recording independence: the distributed arrays lack row-level participant identities.

The pinned [original preparation code](https://raw.githubusercontent.com/ncclabsustech/EEGdenoiseNet/8d290661146c7189c98cc04812d37371d4b9426c/code/benchmark_networks/data_prepare.py) uses `10 log10(RMS ratio)` for its SNR labels. That differs from conventional power-SNR dB. H16 preserves the literal original convention and paired mixture normalization, states the exact temporal-RRMSE equation, and checks its zero/identity references. The repository MIT license was inspected; original physiological-source provenance remains relevant, and raw component arrays/mixtures are not redistributed here. EMG removal and real artifact type/event detection remain separate tasks.

## FRESH: condition labels resolve a narrow task; cortical truth remains unknown

The original [FRESH organizer description](https://openfnirs.org/community/fresh/welcome-to-the-fnirs-fresh-project/) resolves the four session conditions and confirms left/right finger tapping. It also makes clear that the original project asks scientific activation hypotheses. The later [FRESH study](https://doi.org/10.1038/s42003-025-08412-1) studies reproducibility across analysis teams. Majority agreement between laboratories is not gold-standard cortical activation and is not used as a correctness target here.

The [versioned NEMAR FRESH record](https://www.nemar.org/dataset/on005963) provides a CC0 mirror of OpenNeuro ds005963. I07 verifies the SNIRF measurement schema, actual voltage units, wavelengths and channel order against BIDS metadata; all twenty selected SNIRF files match the publisher's SHA-256 manifest. Inputs are baseline-relative, dimensionless natural-log optical density. They are **not** HbO/HbR concentration estimates; no unreported pathlength factor or Beer–Lambert conversion is inserted.

Hand condition is blocked by session. A held-out-person classifier can still exploit recurring session order, instrument or systemic physiology differences. Consequently, classifier accuracy is a condition-prediction diagnostic and cannot prove localized motor-cortical decoding. A stronger endpoint would interleave conditions within recordings and test new sessions/sites. The [2026 processing-optimization study](https://doi.org/10.1007/s12021-026-09772-7) and [overprocessing analysis](https://doi.org/10.1007/s12652-026-05074-7) are additional relevant methodology literature: tuning a pipeline toward an expected scientific conclusion does not by itself establish that conclusion's truth.

## Why other resources remain outside this execution release

- **Umbrella overlap:** [NeuralBench](https://facebookresearch.github.io/neuroai/neuralbench/index.html), [OmniEEG-Bench](https://arxiv.org/abs/2606.00815), [EEG-Arena](https://eeg.fm/benchmarks/) and [Brain-Score](https://www.brain-score.org/) need canonical task/dataset decomposition and distinct model interfaces. A suite plus its constituent dataset is not independent repeated evidence.
- **Continuous-event validity:** [SzCORE](https://epilepsybenchmarks.com/framework/) motivates continuous patient-held-out seizure scoring, including false alarms/hour. Balanced selected seizure clips cannot replace that endpoint. Human/rodent sleep staging likewise needs complete subject/night or laboratory separation.
- **Incomplete annotations:** The original [DREAMS release](https://zenodo.org/records/2650142) explicitly warns that one expert's spindle annotations end after 1000 seconds. Treating the remainder of an 1800-second excerpt as true negatives is excluded. A correctly masked or separately validated annotation protocol remains a candidate; original usage terms and artifact schemas also need deliberate handling.
- **Access agreements:** [NSD](https://www.naturalscenesdataset.org/) and [fastMRI](https://fastmri.med.nyu.edu/) require actual access steps and usage terms; no investigator identity, institutional application or agreement was invented. [Algonauts](https://algonautsproject.com/2025/challenge.html) withholds test responses for remote scoring. BraTS requires a specific release/track rather than pooled years.
- **Ground truth and geometry:** Bycycle output is not independent expert burst truth. Phantom localization requires an actual forward model. [Tractometer](https://tractometer.org/ismrm2015/tools/) documents differing scorer/truth versions and coordinate conventions that must match. [ConfUSIus](https://confusius.tools/latest/user-guide/datasets/) supports small, anonymous filtered downloads, so full-dataset size is not a reason to declare it impossible; an actual experimental target and held-out-animal scorer still need validation.

This review supports transparent admission decisions and three constrained experiments. It does not establish comprehensive electrical/neuroimaging model superiority, verify present SOTA across these modalities, or close the documented coverage gaps.
