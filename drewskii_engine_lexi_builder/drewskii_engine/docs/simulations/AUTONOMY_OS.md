# Autonomy OS — Event-Sourced Control Simulation

**Classification:** Research prototype / control simulation only.  
Not a certified vehicle, drone, or industrial RTOS.

## Architecture

```text
EventLog  ←  ControlLoop @ N Hz
                │
                ├─ SensorFusion
                ├─ WorldModel
                ├─ SafetySupervisor  (hard gate)
                ├─ DecisionCore      (MPC-like action search)
                └─ Predictor
         SystemState (single source of truth)
```

## Components
| Class | Role |
|---|---|
| `EventLog` | Append-only event backbone (+ JSONL export) |
| `SystemState` | pose, velocity, covariance, temperature, safe |
| `SensorFusion` | Noisy measurement blend |
| `WorldModel` | Obstacle distance + thermal view |
| `Predictor` | One-step kinematics |
| `DecisionCore` | Discrete action cost minimization |
| `SafetySupervisor` | Temp / obstacle / speed / pose limits |
| `ControlLoop` | Threaded RT-period simulation |
| `AutonomyOS` | Start / stop / run_for / summary |

## CLI

```text
autonomy
autonomy 2.0
autonomy 3.0 400
```

## Python

```python
from brain.autonomy_os import AutonomyOS

aos = AutonomyOS(hz=50, max_ticks=300)
summary = aos.run_for(seconds=2.0)
print(summary)
for e in aos.replay_log()[-5:]:
    print(e)
```

## Safety
- Simulation sandbox only  
- Safety supervisor can hard-stop the loop  
- Do not connect to real actuators without independent safety engineering  

## Artifacts
`workspace/deliverables/simulations/autonomy_os/` (md, json, jsonl)
