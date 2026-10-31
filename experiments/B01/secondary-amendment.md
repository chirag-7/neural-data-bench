# Post-hoc event-accounting sensitivity

Added during the bounded preview 0.6 review after all original scores were visible. This is an exploratory secondary diagnostic, not a replacement for the frozen mean ground-truth-unit accuracy or a prospectively chosen endpoint. Original model programs, inputs, truth, predictions, unit matches and tolerance are unchanged. No model generation, refitting or threshold search is performed.

The original primary metric averages TP/(TP+FN+FP) over true units. False-positive events in entirely unmatched output units do not enter that average. Existing unit-count diagnostics flag this limitation, but a second scalar helps quantify it. Keep the exact official Hungarian unit mapping; sum its true-positive event count, then count **all** emitted and true events:

- TP = sum of matched true-positive events under the existing one-to-one unit assignment.
- FP = number of all emitted events − TP, including unmatched/redundant output units.
- FN = number of all ground-truth events − TP, including missed true units.
- Micro event precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2TP/(2TP+FP+FN).

This combines event detection and unit identity. It weights events rather than true units and is sensitive to firing rates; neither diagnostic alone establishes biological sorting quality. Redundant-unit events count as incorrect under one-to-one identity even if their timestamps resemble a different matched cluster. This is deliberately **not** SpikeInterface's pooled per-GT precision, which can omit unmatched output units.

The implementation reads the pinned SpikeInterface raw-count table, checks conservation of true/emitted events and independently reproduces pairwise time matches. A perfect prediction, an unmatched extra event and an extra duplicate cluster provide hand-checkable fixtures. See [code](secondary_audit.py), [results](secondary-audit.json), and [official comparison documentation](https://spikeinterface.readthedocs.io/en/stable/api.html). No current-SOTA or population-generalization claim.
