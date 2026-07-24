# Kinetic-Cognitive Architecture: Space as an Emotional Resonator

**Classification:** Architectural concept / immersive UX simulation only.

## Thesis
In the kineto-cognitive manifold, space is dynamic—it coexists with the user, adapting to movement and cognitive state in a continuous feedback loop.

## Applications

### Adaptive floor plans
| Cognitive / movement pattern | Spatial response |
|---|---|
| Creative energy + exploratory path | **Expand** — more openness, freer movement |
| Deep focus + stillness | **Constrict** — intimate cocoon, warmer/quieter (exits remain) |
| Public gallery flow | **Drift** — subtle color, acoustic, floor-grain shifts |

### Public spaces
Museums/galleries adapt wall color temperature, absorption, and floor texture from pace, dwell/attention, and interaction—without biometric coercion.

## Module

```python
from brain.space_resonator import SpaceEmotionalResonator, MovementSample
from brain.cognitive_kinetic import CognitiveState

engine = SpaceEmotionalResonator()
report = engine.run(profile="deep_focus", archetype="deep_work")
print(engine.format_report(report))

report = engine.run(
    profile="activation",
    archetype="creative",
    movement=MovementSample(speed=0.5, path_entropy=0.8, attention=0.6, interaction=0.5),
)
```

## CLI

```text
resonator
resonator deep_focus deep_work
resonator activation creative
resonator anxious_arrival meditative
resonator deep_focus gallery
```

## Archetypes
`deep_work` · `creative` · `meditative` · `gallery` · `public_plaza`

## Safety
- Constrict ≠ lockdown; exits always available  
- Scale factors are design scores for media/kinetic scenery  
- Opt-in / self-report preferred over covert biometrics  
- Not medical; not unreviewed structural engineering  

## Related
- `cognitive_kinetic.py` — body-scale kinetic cues  
- `space_resonator.py` — room/building-scale emotional envelope  

## Artifacts
`workspace/deliverables/simulations/space_resonator/`
