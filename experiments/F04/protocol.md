# F04: real retinal image-to-count encoding, frozen slice v1

## Endpoint and resource selection

Predict expected spike counts for all 41 recorded mouse retinal ganglion cells during a 300 ms natural-image presentation. This is image-conditioned retinal encoding from measured extracellular spikes, not simulated activity or calcium deconvolution. The custom slice uses one **Goldin et al. (2022)** recording processed by OpenRetina, adding a concrete reusable resource to the registry's broad F04 retinal/sensory task. It is not an execution of an official CRCNS protocol, a temporal flicker benchmark, or a claim to reproduce the complete paper.

The [primary paper](https://doi.org/10.1038/s41467-022-33242-8) describes multielectrode recordings from real mouse and axolotl retinal ganglion cells, natural images flashed for 300 ms, and intervening 300 ms gray screens. The [original dataset](https://doi.org/10.5281/zenodo.6868362) is publicly released under CC BY 4.0 according to its Zenodo API metadata. [OpenRetina's primary loader documentation](https://open-retina.org/api_reference/data_io/goldin_2022/) explicitly links this processed mirror to that paper and dataset.

### A restricted source was rejected

The initially investigated [Neuromatch GLM tutorial](https://compneuro.neuromatch.io/tutorials/W1D3_GeneralizedLinearModels/student/W1D3_Tutorial1.html) offers `RGCdata.mat`, real full-field flicker responses from Uzzell and Chichilnisky (2004). Its acknowledgment restricts that particular dataset to tutorials and requires express author permission before publication or distribution. We did not acquire it, infer permissive data rights from the course license, or use it for this research release. Goldin/OpenRetina provides a separately reusable alternative; no email was sent to authors.

## Provenance and raw fields

Processed source file: `marre_lab/goldin_2022/mouse-session-1_structured_data.h5`, 151,245,128 bytes. Pin OpenRetina dataset revision `fc7b91e93c9bd4e76d4e3205fcbcc6a31601985a`. Record source URL, hash, original DOI and processing attribution in `data/manifests/F04.json`. Original and processed data licenses remain separate from the repository's code license; processed OpenRetina data are CC BY-SA 4.0 according to its dataset card. Raw/prepared image arrays remain in ignored cache.

Use these HDF5 fields directly:

- `train/stimulus`: 3,160 natural images, each 108×108 normalized intensity pixels.
- `train/response/binned`: 41×3,160 **nonnegative integer measured spike counts**.
- `test/stimulus`: 30 held-out natural images, each 108×108 pixels.
- `test/repeats/cell0` through `cell40`: each 30 repeats×30 images of nonnegative integer measured counts.

`test/response/binned` contains trial averages, which are fractional counts. It is used only for an integrity check: averaging `test/repeats/cellN` over repeats must reproduce that stored mean. We do **not** replace all observed test counts by these means. `firing_rate_300ms` fields are not used; an acquisition check confirmed their numerical factor of 1/0.3 relative to counts. Neither smoothing nor count-to-Hz conversion is applied to the targets.

## Split, inputs and units

Preserve the source's training/test partition. Hash every image at original float32 precision: all 3,160 training images and all 30 test images are individually unique, with **zero exact image-hash overlap across partitions**. This detects exact duplicates; it cannot exclude visually similar crops or shared upstream source photographs. The source file does not provide acquisition timestamps, so no chronological holdout is claimed.

Each image is reduced using fixed 6×6 pixel block averages, giving an 18×18 image flattened in row-major order into 324 numerical features. This is a response-independent, predeclared input transform; it fits no statistics or receptive fields. Model programs receive the same reduced pixels and all 41 training-count columns. No spike-triggered average, source fitted model, cell label, test response, firing-rate summary or response-derived feature enters x.

Training arrays have shapes `(3160,324)` and `(3160,41)`. Test arrays have shapes `(900,324)` and `(900,41)`: repeat-major order, then image-minor order, retaining all 30 actual measured responses to each held-out image. A deterministic expected-count predictor should return the same prediction for identical image rows; it must not sample spike outcomes. Test rows are grouped by the 30 image identities. All neurons and presentations remain from one retinal session; they are not 41 or 900 independent animals.

The output is expected **counts per 300 ms image presentation**, not spikes/second. The response window length and interstimulus interval are physical metadata, not an inferred continuous bin rate. This static-flash resource does not support the originally contemplated stimulus-history GLM without additional source timing/stimulus-sequence information; such temporal history is excluded from this slice.

## Primary score and references

Primary metric is mean Poisson negative log-likelihood,

`mean(mu - y*log(mu) + logGamma(y+1))`,

over 900 held-out presentations and 41 neurons, with lower values better. Predictions are expected counts and must be finite and positive; any numerical floor or failure policy is recorded centrally. Repeated-image and neuron responses may be correlated and overdispersed. The Poisson score is a predictive rule, not evidence that the biological process is Poisson.

The simple anchor predicts each neuron's mean TRAINING count for every held-out image. Never estimate the null from test counts. This anchor enables paired improvement over a constant-rate reference, provided a shared scoring convention is used.

The domain-informed conventional reference is a regularized linear-nonlinear-Poisson encoding model. Fit StandardScaler and 48-component whitened PCA using only permitted training images, followed by independent PoissonRegressor models for all 41 neurons. Select alpha from 0.001, 0.1 and 1 using mean Poisson NLL on the final 20% of training indices; training-only PCA/scaling must be refit within that selection split. Refit the selected configuration on all training images. A neuron with zero training spikes gets a small fixed positive count. This is a transparent regularized encoding baseline, not verified current SOTA, and the 18×18 input restriction precludes importing full-image CNN scores from other studies.

## Limits on conclusions

Only one mouse session and 30 held-out unique images are included. Image-blocked uncertainty could characterize performance on these images, but it does not support an animal-population interval. Downsampling removes spatial detail. OpenRetina pixels were already normalized upstream; our train-only preprocessing cannot retrospectively prove that upstream global normalization used no held-out images. Original per-cell identities beyond the session's neuron indices are unavailable in this processed file. Widely available public data and benchmark examples may occur in model pretraining. Model-generated code comparisons here measure single-shot supervised estimator construction, not direct LLM spike inference or native vision-foundation-model quality.

## Worklog

- 2026-10-30: Investigated and excluded the publication-restricted Neuromatch RGC tutorial source.
- 2026-10-30: Located the OpenRetina author-linked Goldin loader, inspected dataset file sizes, verified original Zenodo license metadata, and acquired one 151 MB recording rather than the whole retinal corpus.
- 2026-10-30: Inspected exact HDF5 fields, dimensions, count integrality and repeated-response orientation; verified test repeat means against stored aggregate means and checked image-hash separation.
- 2026-10-30: Froze input reduction, complete-neuron target set, source split, per-presentation count endpoint, primary metric, train-mean anchor and train-only baseline selection before any model/test performance was observed.
- Model outputs, prediction hashes, runtime and actual test results are maintained by the central harness after preparation.
