# Follow-on BCI and EEG admission investigation

Checked **2026-10-30**. This bounded investigation targets the unmeasured intracortical BCI family and two candidate EEG paradigms. It is not an exhaustive review. See [dated decisions](admission-v05-bci.json), [actual source/query log](searches-v05-bci.jsonl), and the [G01 protocol](../experiments/G01/protocol.md).

## G01 now has a substantive real-data slice

The [FALCON M2 release](https://dandiarchive.org/dandiset/000953/draft) provides 96-channel macaque intracortical activity and two measured finger-velocity targets. Original metadata declares CC-BY-4.0 and explicitly notes that its apparent split “subjects” are partitions of **one monkey**. The original [FALCON documentation](https://github.com/snel-repo/falcon-challenge) distinguishes calibration, small minival and private evaluation data; those distinctions are retained.

Small minival files were initially attractive but contain only two trials per run. Fourteen total trials were not considered sufficient to justify a useful new broad decoding slice. The larger calibration NWBs contain mostly unused high-rate raw voltage. Anonymous HTTP byte-range access instead made their spike times, kinematics, masks and trial tables inexpensive to extract. This provided **1169 training trials and 754 held-out trials**, without downloading the full multi-gigabyte fullband recordings.

G01 uses all seven public **held-in-calibration** files, with complete Oct 19/20 days for training and later Oct 27/28 days for testing. This is a **custom zero-shot chronological split**, not the official FALCON few-shot adaptation/evaluation protocol or leaderboard score. There is no test-day labeled calibration. Minival and calibration are not mixed because source documentation warns of subset overlap.

The [manifest](../data/manifests/G01.json) pins source asset UUID/blob identities, provider-reported checksums and each extracted buffer/NPZ checksum. Partial extraction does not independently verify the whole-file SHA-256; the record states that limitation. The causal binning/filtering implementation matches the pinned official reference numerically on all seven files. The frozen ridge reference's weak cross-day performance was preserved without test-feedback tuning. Exceeding this local reference would not establish superiority over current specialist SOTA, which remains unverified for this custom split.

H1 human recordings were screened as an alternative. Their small size is convenient, but the original description adds human-data nonredistribution terms despite its CC-BY metadata. M2 was chosen; no H1 arrays or predictions are part of this release. NLB reaching datasets remain useful for behavior decoding, but same-session releases were not relabeled as evidence of cross-day robustness.

## H02 P300: compact, real and downloadable; adapter still needed

The [original BNCI data page](https://bnci-horizon-2020.eu/database/data-sets) labels BNCI2014-008 as an eight-person ALS P300-speller dataset with CC BY-NC-ND 4.0 terms. The original [A01 MATLAB file](https://bnci-horizon-2020.eu/database/data-sets/008-2014/A01.mat) was downloaded and parsed: 21,548,593 bytes, eight named EEG channels, a 347,704×8 continuous matrix, actual `y`/`y_stim` event channels and 35 trial boundaries. The class array explicitly identifies NonTarget and Target. [The source-verification receipt](source-verification-v05-p300.json) retains its SHA-256; raw EEG remains scratch/local data.

A useful next protocol is participant-held-out ERP target detection, preserving natural imbalance, with **training-only xDAWN plus shrinkage LDA or BLDA**, AUROC primary and balanced accuracy secondary. Exact sample indexing, epochs, filtering and acquisition units must be checked against the original description and loader. Results must be kept separate from character-selection accuracy that averages repeated flashes. Local noncommercial analysis is distinct from sharing adapted waveform arrays; the original terms remain visible, and no blanket claim that analysis is prohibited is made.

The original EPFL P300 subject URL also returned a valid ZIP byte-range response, but its full subject archive is approximately267 MB and its dataset license remains unverified. Its mixed clinical/healthy population, repeated sessions and known channel-rank issue require deliberate handling; an unshrunk covariance xDAWN method can fail on that rank deficiency, as [MOABB documents](https://moabb.neurotechx.com/docs/generated/moabb.datasets.EPFLP300.html).

## H03 SSVEP: verified content, unresolved dataset license

The [author-hosted Nakanishi2015 repository](https://github.com/mnakanishi/12JFPM_SSVEP) provides ten directly downloadable subject files and explicit target-frequency ordering. One pinned file was verified as finite float64 data with shape 12 targets × 8 channels × 1114 samples × 15 blocks at 256 Hz; [the verification receipt](source-verification-v05-ssvep.json) gives its exact URL and SHA-256.

The [original paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140703) supports standard CCA with sinusoid references as the calibration-free specialist and extended/individual-template CCA when personal calibration is available. These are distinct regimes. Whole blocks must stay together; subject holdout is a separate test. Onset/latency cropping and response-time assumptions for information-transfer rate must be frozen without test-score tuning.

However, the original repository lacks an explicit data license and [MOABB source metadata](https://raw.githubusercontent.com/NeuroTechX/moabb/develop/moabb/datasets/ssvep_nakanishi.py) records it as Unknown. The article's CC-BY license is not automatically a license for external data arrays. H03 is therefore source-verified but deferred from execution pending clarified terms or an explicitly licensed alternative; it is not declared bad or inaccessible.
