# J08: Real synaptic-punctum instance segmentation with separate expert raters

This endpoint uses real fluorescence microscopy and human annotations from [SynAPSeg](https://doi.org/10.1371/journal.pcbi.1014571), pinned [Zenodo record 18988899](https://doi.org/10.5281/zenodo.18988899). The authoritative API confirms **CC BY 4.0**, resolving the earlier map’s licensing uncertainty. This is a genuine neuroscience image-analysis operation: locate and separate fluorescent synaptic-protein puncta. These are anatomical proxies; they do not establish functional synapses or EM connectivity.

## Frozen selection before evaluated-model generation

Use all 27 original 2D training fields in `TrainingDatasets/2D/raw_datasets/`. Use only **Dataset1 and Dataset2** from the separate `BenchmarkDatasets.zip` as test images; the article states those complete benchmark images were excluded from model training and validation. Dataset1 is PSD95-FingR in cultured neurons; Dataset2 is immunolabeled VGluT1. Dataset3 is a 3D tissue volume and is excluded from this 2D endpoint; projecting that volume would change the task.

Normalize each original image using its own intensity percentiles 1 and 99.8, then clip to [0,1]. This unsupervised per-image transform uses no object labels. Tile training fields on a fixed nonoverlapping 128×128 grid from the top-left. Retain crops with at least one valid manually annotated pixel; no object-count or test-performance filter. Keep source-field IDs for every crop. ROI TIFFs determine where training labels are known; absent ROI files indicate a fully labeled field according to the release. Unannotated regions and edge padding have `train_y=-1` and must not become negative training examples. Channel1 explicitly provides that annotation-coverage mask. Channel0 retains original measured intensity context, with only geometric crop padding set to zero.

For test, pad the two entire images to 727×546 and supply a channel1 mask of their original spatial extents. Test-mask geometry does not reveal object positions. Original image sizes are 727×546 and 80×204. Do not randomly split pixels or patches from a test field into training. The release does not provide enough identifiers to establish independence by animal/culture; claim held-out fields only, not unseen-animal generalization. Fields and crops within source preparations may remain correlated.

## Targets and object definition

Training labels are manually painted punctum masks. Positive IDs identify instances locally and have no global class meaning; zero denotes annotated background. Five experts A–E independently labeled each benchmark field. **All five raters remain separate**, equally weighted; do not select a favorable expert or manufacture majority-vote oracle labels.

Raw expert TIFFs reuse paint IDs across disconnected puncta. The author’s pinned `fig2_intrarater_var_analysis.py::format_annot` splits connected components separately within each painted value, using full connectivity, then removes components smaller than four pixels/voxels. Some annotations for 2D Dataset2 are stored as 3D stacks: the author applies this cleanup in their original dimensionality, then maximum-projects the cleaned labels when paired with a 2D image. We reproduce that documented policy; array axes are inspected and recorded. Other images are not projected. This resolves storage semantics rather than estimating missing labels.

## Predictions and scorer

Model API: `fit_predict(train_x, train_y, test_x)` returns one nonnegative integer instance-label image per test field, shape `(2,727,546)`. Inputs are `N,C,Y,X`, with intensity and validity channels. Training labels are `(N,128,128)`; hidden test labels are `(2,5,727,546)`. Background is zero; different puncta require distinct positive IDs. Binary semantic segmentation alone can merge touching puncta and is penalized accordingly.

Primary: **mean instance F1 at IoU ≥0.5**, computed separately for each image/expert pair, then equally averaged over two images and five experts. One-to-one Hungarian assignment maximizes the number of qualifying matches first and IoU second. `F1=2TP/(2TP+FP+FN)`. Both empty sets score1; only one empty set scores0. Ignore geometric padding. Predictions undergo the same documented disconnected-ID and <4-pixel cleanup before matching. This is an explicit custom multi-rater endpoint, not the paper’s spatial-centroid consensus score or a claim to reproduce its full benchmark aggregate. Report all ten image/rater values and human–human agreement as descriptive context; two images do not justify specimen-level significance tests.

## Credible archived specialist reference

The original benchmark ZIP also contains author-deposited prediction masks named `annotated_predStardist_v3.6.0.8_Labels_2025_1221.tiff` for both 2D images. These are a separate **archived StarDist specialist reference**, never training targets. Preserve their source-member hashes, apply the same cleanup and scorer, and identify evidence as archived predictions rescored. No weights or outputs are inferred from paper numbers, and no weight inference is falsely claimed.

Training crops, feature representations, optimization budgets and historical model selection differ between this general-code diagnostic and the archived specialist. The article explicitly discusses choosing models based on benchmark behavior; historical test exposure cannot be ruled out for that specialist. Exclude it from strict matched-budget or pristine-test superiority claims. It remains a useful transparent practical pipeline reference; **current SOTA is unverified**.

## Source and acquisition integrity

The official source scripts and toolkit are pinned separately in `source-manifest.json`, with their BSD-3-Clause licenses. Dataset archives are checked against the publisher’s MD5 and retained SHA256; each relevant member also has a checksum/ZIP CRC. The initial long archive transfer needed resumption; the completed original ZIP is validated before final admission. Prepared array shapes, crop origins, field IDs, mask transformations and archived reference names are in `data-manifest.json`. Raw data stay in ignored `data/cache/J08/`.
