# Design and interpret advertising experiments

## Inputs

Hypothesis, unit of assignment, primary metric, baseline evidence, budget constraint and feasible controls.

## Procedure

1. Define one primary decision and minimum effect worth acting on. Specify assignment, exposure, exclusions, interference risks and measurement lag. Identify whether platform-native randomization exists; never invent an experiment feature.

2. Calculate required sample or duration only from supplied baseline rates/variance and declared assumptions. If no defensible inputs exist, provide a feasibility or pilot design instead of a spurious power number.

3. Freeze the primary metric, analysis window, stopping rule and treatment allocation before the run. Account for repeated looks and multiple comparisons. Keep other material changes controlled or recorded.

4. Compare outcomes with uncertainty and implementation fidelity. Nonrandom before/after analysis stays observational. Preserve failed and inconclusive tests; only promote reusable lessons through review.

## Output

Experiment plan or readout, assumptions, causal limitations and next decision.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

Use the experiment section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

A proposed baseline pilot still requires account readiness and an exact reviewed launch plan before spending; tracking deployment requires its applicable reviewed change plan. Include these prerequisites in the next action itself. Reuse already-approved review thresholds and avoid turning them into new permission gates.
