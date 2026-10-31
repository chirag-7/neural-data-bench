# K04: donor-held-out cortical-layer label transfer

## Scientific question and source

Can one general-model-generated procedure assign curated cortical-layer/white-matter labels to expression profiles from a new human donor? This is a supervised, processed-expression diagnostic. It is distinct from unsupervised spatial-domain clustering and from histology segmentation.

Source: Maynard et al., [Transcriptome-scale spatial gene expression in the human dorsolateral prefrontal cortex](https://doi.org/10.1038/s41593-020-00787-0). Download all 12 original filtered count matrices using the authors' [raw-data links](https://github.com/LieberInstitute/HumanPilot/blob/044446d6bd8fc154aa74f7be62ec67effb1ec376/AWS_File_locations.tsv). Curated labels are the pinned [barcode/section layer map](https://github.com/LieberInstitute/HumanPilot/blob/044446d6bd8fc154aa74f7be62ec67effb1ec376/10X/barcode_level_layer_map.tsv). Author [conversion code](https://github.com/LieberInstitute/HumanPilot/blob/044446d6bd8fc154aa74f7be62ec67effb1ec376/Analysis/convert_sce.R) independently identifies section-to-donor mapping.

The original annotations were curated with histology and expression assistance. They are useful label-transfer targets, not fully orthogonal molecular ground truth. Their preparation may incorporate the full source study. No original label-generating embeddings, clusters, marker lists, coordinates or image features enter predictors.

## Source terms and identities

The authors explicitly distribute these data for analysis through HumanPilot/spatialLIBD. The repository and supplied author code carry Artistic-2.0; retained license: `UPSTREAM_LICENSE.txt`. That software license is not asserted as a separate blanket license on all remote count matrices. Raw source and prepared expression arrays remain ignored local caches; no human molecular data matrix is redistributed in this repository. Public source links, file hashes, aggregate score artifacts and minimal annotation join keys provide provenance. See [manifest](../../data/manifests/K04.json).

## Frozen input and split

Use all sections151507–151510 (Br5292) and151669–151672 (Br5595) for training; all151673–151676 (Br8100) for test. Four test sections are **one donor**. Keep every source spot with one of L1,L2,L3,L4,L5,L6,WM; exclude only absent/other annotations. Do not apply label-dependent quality, difficulty or spatial-boundary trimming. Verify positive full-library counts and identical33538-gene ordering across all files.

Normalize each spot to10000 counts using its full library, then log1p. Select the500 highest-variance non-mitochondrial genes using outer-training spots only; ties break by original gene index. Preserve chosen columns in original gene order. Shared feature selection uses both outer-training donors and is not repeated inside inner CV, so inner-validation claims must be qualified. Held-out donor expression/labels never influence gene choice or fitted transforms.

Prepared float32 arrays:33086×500 training,14243×500 test; targets0..6 map to the seven labels above. Interface `fit_predict(train_x,train_y,test_x,train_groups)` returns one integer label pertest spot. `train_groups` supplies training donor IDs equally to all methods; only the scorer receives test section IDs. Model procedures must fit further preprocessing/tuning on training only, handle two-donor validation and classes absent in one donor, and avoid test-batch adaptation or reconstructing spatial neighborhoods from row order.

## Metric and references

Primary: compute macro-F1 with all seven fixed labels in each held-out section, then mean the four section scores equally. Pooled macro-F1/accuracy are secondary. Do not interpret four section scores as four independent people or derive spot-level population confidence intervals.

Conventional reference: standardize training features and fit balanced multinomial logistic regression C=1,lbfgs,max_iter500,seed20261030.

Domain specialist: official [SingleR Python implementation](https://singler-inc.github.io/singler-py/api/singler.html), release0.5.0. Build mean prepared-expression profiles pertraining-donor×label (12 profiles; both donor IDs already available to general models). Train classic markers,num_de50 on the same500features; classify with quantile0.8,fine-tuning on,threshold0.05,one thread. Fixed before any method test score or model generation. This applies SingleR to anatomical-layer references; it is not a claim to reproduce a published spatial-clustering leaderboard. No external reference/pretraining or test-fitted reference is used. Published ARI clustering scores cannot be inserted as this supervised F1 endpoint's SOTA.

One high-reasoning, no-tool/no-feedback generation perrequested Sol model. Same general numerical imports as the original T3 panel; no specialist packages for generated programs. Fewer than240lines and180second numerical subprocess budget,one thread,requested4GB memory not enforced. References have the same numerical timeout; total development/search effort is not matched. Retain failures and format deviations without repairs. Freeze prompt,adapter,protocol,reference,runner and prepared inputs before generation and all fitted-method test scores.

## Limits

Only three total donors and one held-out donor; adjacent sections/spots are correlated. Broad cell/spatial coverage remains incomplete. Data and curated labels are public, contamination unknown. Gene selection and annotation assistance constrain interpretation. Current global best, full spatial modeling, causal biology and general molecular foundation-model capability remain unestablished.
