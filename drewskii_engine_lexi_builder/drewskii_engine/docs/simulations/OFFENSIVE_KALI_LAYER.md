# OffensiveKaliLayer — Constraint Pressure Simulation

**Classification:** GOVERNANCE / DESIGN SIMULATION ONLY  
**Not:** Kali Linux offensive security, network exploitation, or privilege escalation tooling.

## Metaphor map

| Method | Simulation meaning | Explicitly not |
|---|---|---|
| `scan` | Map constraint surface | Host/port recon |
| `escalate` | Raise mass/curvature pressure budget | OS privilege escalation |
| `penetrate` | Single-constraint yield estimate | Exploit a service |
| `realign_social_vectors` | Stakeholder alignment pull model | Covert influence malware |
| `full_assault` | Multi-constraint pressure report | Real-world attack campaign |

## Constraint types

- `REGULATORY`
- `PHYSICAL`
- `MATERIAL`
- `SOCIAL`
- `TEMPORAL`

## API

```python
from brain.offensive_kali_layer import (
    OffensiveKaliLayer, Constraint, ConstraintType,
)

layer = OffensiveKaliLayer()
report = layer.full_assault(
    target_name="Product Launch",
    constraints=[
        Constraint("fda_path", ConstraintType.REGULATORY, 1.3),
        Constraint("public_trust", ConstraintType.SOCIAL, 0.9),
    ],
    mass_density=16.5,
    social_pull=0.5,
)
print(report.status, report.overall_yield)
```

## CLI

```text
kali
kali 16.5
```

## Artifacts

`workspace/deliverables/simulations/constraint_kali/`
