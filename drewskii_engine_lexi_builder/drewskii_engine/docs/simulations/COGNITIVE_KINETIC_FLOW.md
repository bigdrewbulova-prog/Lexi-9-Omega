# Cognitive Influence on Kinetic Flow

**Classification:** CONCEPT DESIGN / WELLNESS UX SIMULATION ONLY  
**Not:** medical device, diagnosis, treatment, or clinical neurofeedback product.

## Concept
Mental and emotional state scores are interconnected with how people move and engage a space. A system can adapt **kinetic feedback** (pace, haptics, floor compliance, light rhythm, breath guides) from abstract cognitive state inputs.

## Application (wellness center storyboard)
1. User self-reports or optional consumer biofeedback provides abstract scores (focus, calm, stress, energy, presence).  
2. Space maps state → kinetic mode (`deliberate` / `balanced` / `goal_oriented` / `recovery`).  
3. Environment responds: softer floor, slower pulse, breath-aligned light for high stress; clearer path and firmer response for activation.  
4. User can always override or exit.

## Example mapping
| Cognitive pattern | Kinetic response |
|---|---|
| High stress / low calm | Slow deliberate steps, cushioned floor, warm slow light, longer exhale guide |
| High energy + focus | Goal-oriented pace, clearer path, cooler edge light, waypoint haptics |
| High calm + low energy | Recovery field, minimal direction, soft haptics |

## Module API

```python
from brain.cognitive_kinetic import CognitiveKineticFlow, CognitiveState

flow = CognitiveKineticFlow()
report = flow.run(profile="anxious_arrival")
print(flow.format_report(report))

custom = CognitiveState(focus=0.6, calm=0.3, stress=0.75, energy=0.5, presence=0.4)
report = flow.run(state=custom, title="Custom session")
```

## CLI

```text
kinetic
kinetic anxious_arrival
kinetic deep_focus
kinetic activation
kinetic post_session_calm
```

## Demo profiles
- `anxious_arrival`
- `deep_focus`
- `post_session_calm`
- `activation`

## Safety / claims boundary
- No diagnosis of anxiety or other conditions.  
- “Stress” is an abstract 0–1 score.  
- Do not claim treatment outcomes.  
- Future sensors: consent + wellness-grade labeling only.  
- Movement is invited, never forced.

## Artifacts
`workspace/deliverables/simulations/cognitive_kinetic/`
