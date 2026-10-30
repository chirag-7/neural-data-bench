# Executed panel

The 14 measured IDs and exact scores are in [findings](../analysis/findings.md). Frozen experimental contracts, per-task source/license checks, code and actual worklogs live under [experiments](../experiments/).

- [A09](../experiments/A09): CalMS21 Task 1,3Hz centers and seven pose offsets,19 test recordings
- [A14](../experiments/A14): Rat 7M six-landmark 31 frame windows;7 frame artificialHeadF gap;heldout rats 4–5
- [C05](../experiments/C05): Calcium-to-spike inference
- [D02](../experiments/D02): One Allen cell,4 train/2 test negative-current sweeps;500Hz passive voltage-deflection interpolation
- [E01](../experiments/E01): NLBMC_Maze_Small 99 train/100 test movement-aligned trials;20 ms supervised 107→35 neuron readout
- [F04](../experiments/F04): Goldin 2022 retina,3160 trainimages/30 testimages×30 repeats,41 neurons,18×18 imagefeatures
- [H01](../experiments/H01): PhysioNet motorimagery;5 train/3 heldout subjects,225/135 epochs
- [H16](../experiments/H16): EEGdenoiseNet clean+EOG2000 train/600 test component-disjoint mixtures
- [I07](../experiments/I07): FRESH opticaldensity tapping condition,7 train/3 test subjects;condition/session confounded
- [I10](../experiments/I10): MRIQC600 ABIDEtrain/265 DS030 test,68 numeric IQMs,rater 1 exclude labels
- [K01](../experiments/K01): Allen mouse ephys 11 features→spiny/aspiny morphology,donor-disjoint 1356/457 cells
- [L04](../experiments/L04): One real rat placecell,20 mscounts,chronological 60/40 split with 1 sgap;position/velocity
- [M04](../experiments/M04): Cognitive model and parameter recovery
- [N05](../experiments/N05): One real legacyNWB file sharedD02;61 deterministic fields,6 sweeps

The current 180sCPUcode track favors bounded processed arrays. Raw-modality and foundation-model comparisons need separate model interfaces and budgets. This is a convenience-selected exploratory panel. See [admission ledger](../registry/admission-decisions.json) for unrun endpoints.
