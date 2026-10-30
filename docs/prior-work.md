# Prior work and novelty boundary

[Original detailed map](neuroscience_benchmark_research_map.md) · [Extension review](../literature/extension-audit.md)

| Primary work | Existing contribution | Implication for this project |
|---|---|---|
| [NeuralBench](https://arxiv.org/abs/2605.08495), [official suite](https://facebookresearch.github.io/neuroai/neuralbench/index.html) | Unified brain-model evaluation; first EEG release spans 36 tasks and 94 datasets | Reuse protocols; neuroscience-pretrained vs task-specific comparison already exists. Do not relabel these as general text-model results. |
| [BrainWideBench](https://arxiv.org/abs/2609.22064), [IBL summary](https://www.iblcore.org/resources/benchmarking/ibl-brainwidebench/) | Across-animal behavior decoding, dynamics and anatomy from multi-region spikes | Direct prior umbrella neural-representation suite; use animal splits and server scoring. |
| [NLB](https://neurallatents.github.io/) | Neural latent/dynamics evaluation | Prediction quality and representation evaluation are established. |
| [Brain4FMs](https://arxiv.org/abs/2602.11558), [AdaBrain-Bench](https://arxiv.org/abs/2507.09882) | Electrical-brain foundation-model evaluation and BCI adaptation | More overlapping work; compare procedure, not a blanket claim of first benchmarking. |
| [NeuroDiscoveryBench](https://github.com/allenai/neurodiscoverybench), [ScienceAgentBench](https://arxiv.org/abs/2410.05080) | Data-grounded scientific analysis agent evaluation | Most directly related to T3/T4 workflow evaluation. |
| [NeuroClaw/NeuroBench](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html), [BrainAgent](https://arxiv.org/abs/2606.25400) | Neuroscience workflows and EEG agent tasks | Must distinguish tool use, rubric scores and numerical prediction accuracy. |
| [BrainBench](https://www.nature.com/articles/s41562-024-02046-9) | Neuroscience result prediction from text | Related scientific knowledge task; does not establish neural-array analysis ability. |
| [NeuroBench neuromorphic](https://www.nature.com/articles/s41467-025-56739-4) | Algorithm and hardware efficiency framework | Different benchmark with the same short name; useful resource accounting. |
| [HippoUnit](https://doi.org/10.1371/journal.pcbi.1008114), [computational modeling guide](https://elifesciences.org/articles/49547) | Mechanistic validation, parameter/model recovery | Prediction accuracy is insufficient for explanatory modeling. |
| [ZAPBench](https://google-research.github.io/zapbench/) | Whole-brain optical activity forecasting | Extends species/scale beyond primate and mouse spike suites. |

The defensible contribution is a versioned cross-lab **evidence map plus reproducible controlled evaluation infrastructure**, linking track-specific general-model runs and specialist evidence across modalities. The current empirical contribution is small: one biological benchmark transfer audit and one synthetic recovery wrapper. A “first comprehensive benchmark,” “current state of all general models,” or universal general-over-specialist result is not established. A systematic brain-imaging foundation-model review also exists ([2026 review](https://doi.org/10.1016/j.neuroimage.2026.121877)); it covers a narrower domain than all lab workflows and does not remove the need for a fresh task-level assessment.
