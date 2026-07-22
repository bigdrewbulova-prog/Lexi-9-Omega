# RetroCausalEngine — Simulation Spec

**Classification:** RESEARCH PROTOTYPE / NUMERICAL SIMULATION ONLY

## What it is
A **goal-conditioned optimizer** that treats a `FutureState` as a *target design envelope* and reverse-optimizes current simulation parameters toward it.

- **Future state** = desired metrics (not a prophecy, not physical time)
- **Retro** = optimize backward from goals to parameters
- **Consistency filter** = reject/repair discontinuous or envelope-violating jumps in parameter space

## What it is not
- Physical retrocausality or time travel
- Closed timelike curve hardware
- Finished exotic-matter / fold engines
- Medical or weapons tooling

## API

```python
from brain.retro_causal import RetroCausalEngine, FutureState, CurrentParams

engine = RetroCausalEngine(micro_window=1e-12, consistency_threshold=0.08, max_iters=120)
future = FutureState(
    target_mass_density=16.5,
    target_fold_strength=0.44,
    target_authority=0.95,
    target_entropy_efficiency=1.04,
)
report = engine.optimize(future, CurrentParams())
print(engine.execute_post_synthesis(target_mass=16.8, target_authority=0.97))
```

## CLI

```text
retro
retro 16.8 0.97
```

## Optimizer
- Prefer **SciPy L-BFGS-B** when `scipy` is installed
- Else **NumPy bounded Newton stand-in** for the quadratic objective

## Artifacts
Written under:

`workspace/deliverables/simulations/retro_causal/`
