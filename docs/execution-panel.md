# Executed panel

19 measured task IDs. Exact scores and caveats:[findings](../analysis/findings.md); source contracts:[experiments](../experiments/).

- [A09](../experiments/A09): CalMS21 Task 1: processed pose context at 3 Hz; 70 training and 19 test recordings.
- [A14](../experiments/A14): Rat7 M: six-landmark, 31-frame windows with an artificial seven-frame HeadF gap; three training and two test rats.
- [B01](../experiments/B01): Blind unsupervised spike sorting of one 10-second, 32-channel stationary MEArec simulation; official unit/event matching.
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
- [L04](../experiments/L04): One rat place cell: 20 ms spike counts predicted from position and velocity; chronological 60/40 split with a one-second gap.
- [M04](../experiments/M04): Synthetic two-choice Q-learning agents: recover learning rate and inverse temperature from choices and rewards.
- [N05](../experiments/N05): One real legacy Allen NWB file, shared with D02: extract 61 deterministic fields covering six sweeps.

C05 has five preparations; E01 has three official source slices, all reusing original programs. B01 post-hoc event F1 is a separate sensitivity, not another independent task or a changed primary. H02 passes training-person IDs explicitly. Budget/memory/adaptation limits are part of each contract.
