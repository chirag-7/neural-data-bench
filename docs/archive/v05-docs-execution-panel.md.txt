# Executed panel

18 measured IDs; exact scores and references in [findings](../analysis/findings.md). Frozen contracts and actual data provenance under [experiments](../experiments/).

- [A09](../experiments/A09): CalMS21 Task1,3Hz centers and seven pose offsets,19 test recordings
- [A14](../experiments/A14): Rat7M six-landmark31frame windows;7frame artificialHeadF gap;heldout rats4–5
- [B01](../experiments/B01): Blind unsupervised sorting of one10second32channel MEArec simulation; official unit/event scorer
- [C05](../experiments/C05): Calcium-to-spike inference
- [D02](../experiments/D02): One Allen cell,4train/2test negative-current sweeps;500Hz passive voltage-deflection interpolation
- [E01](../experiments/E01): NLBMC_Maze_Small99train/100test movement-aligned trials;20ms supervised107→35neuron readout
- [F04](../experiments/F04): Goldin2022 retina,3160trainimages/30testimages×30repeats,41neurons,18×18imagefeatures
- [G01](../experiments/G01): FALCON M2 custom cross-day finger-velocity decoding:1169train/754testtrials,96causalfeatures,twooutputs,one monkey
- [H01](../experiments/H01): PhysioNet motorimagery;5train/3heldout subjects,225/135epochs
- [H08](../experiments/H08): SleepEDF fixed20:00–08:00firstnightwindows;5train/3heldoutpeople,100HzFpz-Cz;fiveclassstaging
- [H16](../experiments/H16): EEGdenoiseNet clean+EOG2000train/600test component-disjoint mixtures
- [I07](../experiments/I07): FRESH opticaldensity tapping condition,7train/3test subjects;condition/session confounded
- [I10](../experiments/I10): MRIQC600ABIDEtrain/265DS030test,68numeric IQMs,rater1exclude labels
- [J08](../experiments/J08): SynAPSeg2Dpuncta instances:27trainingfields,1262crops;twoheldoutwholefields×fiveexpertmasks;archivedStarDistreference
- [K01](../experiments/K01): Allen mouse ephys11features→spiny/aspiny morphology,donor-disjoint1356/457cells
- [L04](../experiments/L04): One real rat placecell,20mscounts,chronological60/40split with1sgap;position/velocity
- [M04](../experiments/M04): Cognitive model and parameter recovery
- [N05](../experiments/N05): One real legacyNWB file sharedD02;61deterministic fields,6sweeps

C05 has five preparations; E01 has MC_Maze_Small, Area2_Bump and DMFC_RSG source slices. Each remains one task ID for macro weighting. E01 transfers unchanged task-specific-prompt programs to new array shapes; this is not a fresh prompt per source. B01/M04 are fully synthetic; A14/H16 have artificial corruption; D02/N05 share a source file.

The 180-second, one-numerical-thread code track favors bounded offline arrays. Approximate memory budgets were requested but not enforced. Generation and data preparation time differ from estimator execution time. See [reproduction](reproduce.md) for separate specialist stacks and [admissions](../registry/admission-decisions.json) for unrun endpoints.
