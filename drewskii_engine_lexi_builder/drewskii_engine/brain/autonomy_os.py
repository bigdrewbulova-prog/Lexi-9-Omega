"""
Autonomy OS — event-sourced control-loop simulation for Lexi-9-Omega / Drewskii.Engine.

CLASSIFICATION: RESEARCH PROTOTYPE / CONTROL SIMULATION ONLY

This is a software architecture demo:
  EventLog → SystemState → SensorFusion → WorldModel → Predictor
  → DecisionCore (MPC-like) → SafetySupervisor → ControlLoop

It does NOT:
- drive real vehicles, drones, or industrial machinery without separate certification
- bypass physical e-stops or regulatory safety cases
- claim production RTOS / ISO 26262 readiness

Safe use: architecture teaching, digital-twin sandbox, decision/safety unit tests.
"""
from __future__ import annotations

import json
import math
import random
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text


# ============================================================
# EVENT LOG (Event-Sourced Backbone)
# ============================================================


class EventLog:
    """Append-only in-memory event log with optional disk export."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def record(self, event: dict[str, Any]) -> None:
        with self._lock:
            self.events.append(dict(event))

    def replay(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.events)

    def clear(self) -> None:
        with self._lock:
            self.events.clear()

    def export_jsonl(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            lines = self.events
            with path.open("w", encoding="utf-8") as handle:
                for event in lines:
                    handle.write(json.dumps(event, ensure_ascii=True) + "\n")
        return path


# ============================================================
# STATE MODEL (Single Source of Truth)
# ============================================================


@dataclass
class SystemState:
    pose: float = 0.0
    velocity: float = 0.0
    covariance: float = 0.1
    temperature: float = 25.0
    safe: bool = True
    tick: int = 0
    last_action: float = 0.0
    stop_reason: str = ""

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)

    def copy(self) -> "SystemState":
        return SystemState(**asdict(self))


# ============================================================
# SENSOR FUSION LAYER
# ============================================================


class SensorFusion:
    """1D complementary-style pose update with measurement noise."""

    def __init__(self, process_alpha: float = 0.8, noise_std: float = 0.05) -> None:
        self.process_alpha = process_alpha
        self.noise_std = noise_std

    def update(self, state: SystemState, rng: random.Random) -> SystemState:
        measurement = state.pose + rng.gauss(0.0, self.noise_std)
        a = self.process_alpha
        state.pose = a * state.pose + (1.0 - a) * measurement
        state.covariance = max(1e-6, state.covariance * 0.95)
        return state


# ============================================================
# WORLD MODEL
# ============================================================


class WorldModel:
    def update(self, state: SystemState) -> dict[str, Any]:
        # Toy world: obstacle approaches as pose increases
        return {
            "obstacle_distance": max(0.0, 10.0 - state.pose),
            "temperature": state.temperature,
            "speed": abs(state.velocity),
        }


# ============================================================
# PREDICTION ENGINE
# ============================================================


class Predictor:
    def simulate(self, state: SystemState, action: float, dt: float = 1.0) -> float:
        # Simple discrete kinematics: pose' ≈ pose + velocity + action
        return state.pose + state.velocity * dt + action * dt


# ============================================================
# DECISION CORE (MPC-like placeholder)
# ============================================================


class DecisionCore:
    def __init__(self, predictor: Predictor, actions: list[float] | None = None) -> None:
        self.predictor = predictor
        self.actions = actions or [-1.0, -0.5, 0.0, 0.5, 1.0]

    def decide(self, state: SystemState, world: dict[str, Any]) -> float:
        best_action = 0.0
        lowest_cost = float("inf")
        obstacle = float(world.get("obstacle_distance", 10.0))

        for action in self.actions:
            predicted_pose = self.predictor.simulate(state, action)
            # Prefer staying near origin-ish progress without hitting obstacle zone
            cost = abs(predicted_pose - 5.0)  # soft goal near pose=5
            cost += 2.0 / (obstacle + 0.25)
            cost += 0.15 * abs(action)
            cost += 0.05 * abs(state.velocity + action)
            if cost < lowest_cost:
                lowest_cost = cost
                best_action = action
        return best_action


# ============================================================
# SAFETY SUPERVISOR
# ============================================================


class SafetySupervisor:
    def __init__(
        self,
        max_temperature: float = 80.0,
        min_obstacle_distance: float = 1.0,
        max_speed: float = 8.0,
        max_pose: float = 50.0,
    ) -> None:
        self.max_temperature = max_temperature
        self.min_obstacle_distance = min_obstacle_distance
        self.max_speed = max_speed
        self.max_pose = max_pose

    def check(self, state: SystemState, world: dict[str, Any]) -> tuple[bool, str]:
        if world.get("temperature", state.temperature) > self.max_temperature:
            return False, "temperature_limit"
        if world.get("obstacle_distance", 99.0) < self.min_obstacle_distance:
            return False, "obstacle_proximity"
        if abs(state.velocity) > self.max_speed:
            return False, "speed_limit"
        if abs(state.pose) > self.max_pose:
            return False, "pose_limit"
        if not state.safe:
            return False, "already_unsafe"
        return True, "ok"


# ============================================================
# CONTROL LOOP (RT Kernel Simulation)
# ============================================================


class ControlLoop(threading.Thread):
    def __init__(
        self,
        state: SystemState,
        decision_core: DecisionCore,
        safety: SafetySupervisor,
        log: EventLog,
        *,
        hz: float = 100.0,
        max_ticks: int | None = 500,
        rng_seed: int = 7,
        on_tick: Callable[[SystemState, dict[str, Any]], None] | None = None,
    ) -> None:
        super().__init__(daemon=True)
        self.state = state
        self.decision_core = decision_core
        self.safety = safety
        self.log = log
        self.running = True
        self.hz = hz
        self.dt = 1.0 / hz
        self.max_ticks = max_ticks
        self.fusion = SensorFusion()
        self.world_model = WorldModel()
        self.rng = random.Random(rng_seed)
        self.on_tick = on_tick
        self._stop = threading.Event()

    def stop(self) -> None:
        self.running = False
        self._stop.set()

    def run(self) -> None:
        while self.running and not self._stop.is_set():
            start_time = time.perf_counter()
            self.state.tick += 1

            # Perception
            self.fusion.update(self.state, self.rng)
            world = self.world_model.update(self.state)

            # Safety gate (hard supervisor)
            ok, reason = self.safety.check(self.state, world)
            if not ok:
                self.state.safe = False
                self.state.stop_reason = reason
                self.log.record(
                    {
                        "type": "safety_stop",
                        "timestamp": time.time(),
                        "tick": self.state.tick,
                        "reason": reason,
                        **self.state.snapshot(),
                        **world,
                    }
                )
                self.running = False
                break

            # Decide + act
            action = self.decision_core.decide(self.state, world)
            self.state.last_action = action
            self.state.velocity += action * self.dt * 10.0  # scale for visible dynamics
            self.state.pose += self.state.velocity * self.dt
            self.state.temperature += abs(action) * 0.05

            event = {
                "type": "control_tick",
                "timestamp": time.time(),
                "tick": self.state.tick,
                "action": action,
                **self.state.snapshot(),
                **world,
            }
            self.log.record(event)
            if self.on_tick:
                self.on_tick(self.state, world)

            if self.max_ticks is not None and self.state.tick >= self.max_ticks:
                self.state.stop_reason = "max_ticks"
                self.log.record(
                    {
                        "type": "stop",
                        "timestamp": time.time(),
                        "tick": self.state.tick,
                        "reason": "max_ticks",
                    }
                )
                self.running = False
                break

            # RT period
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.0, self.dt - elapsed)
            if sleep_time:
                self._stop.wait(sleep_time)


# ============================================================
# AUTONOMY OS CORE
# ============================================================


class AutonomyOS:
    """High-level autonomy OS façade for simulation runs."""

    CLASSIFICATION = (
        "CONTROL SIMULATION ONLY — not a certified vehicle/robot runtime"
    )

    def __init__(
        self,
        *,
        hz: float = 50.0,
        max_ticks: int | None = 300,
        rng_seed: int = 7,
    ) -> None:
        self.state = SystemState()
        self.log = EventLog()
        self.predictor = Predictor()
        self.decision_core = DecisionCore(self.predictor)
        self.safety = SafetySupervisor()
        self.hz = hz
        self.max_ticks = max_ticks
        self.rng_seed = rng_seed
        self.control_loop: ControlLoop | None = None
        self._started_at: float | None = None

    def start(self) -> None:
        if self.control_loop and self.control_loop.is_alive():
            raise RuntimeError("Control loop already running")
        self.state = SystemState()
        self.log.clear()
        self.control_loop = ControlLoop(
            self.state,
            self.decision_core,
            self.safety,
            self.log,
            hz=self.hz,
            max_ticks=self.max_ticks,
            rng_seed=self.rng_seed,
        )
        self._started_at = time.time()
        self.log.record(
            {
                "type": "start",
                "timestamp": self._started_at,
                "hz": self.hz,
                "max_ticks": self.max_ticks,
                "classification": self.CLASSIFICATION,
            }
        )
        self.control_loop.start()

    def stop(self, timeout: float = 5.0) -> None:
        if not self.control_loop:
            return
        self.control_loop.stop()
        self.control_loop.join(timeout=timeout)
        self.log.record(
            {
                "type": "operator_stop",
                "timestamp": time.time(),
                "tick": self.state.tick,
                "safe": self.state.safe,
                "stop_reason": self.state.stop_reason or "operator_stop",
            }
        )

    def run_for(self, seconds: float = 3.0) -> dict[str, Any]:
        """Blocking convenience: start, wait, stop, return summary + export paths."""
        self.start()
        try:
            deadline = time.time() + max(0.05, seconds)
            while time.time() < deadline:
                if not self.control_loop or not self.control_loop.is_alive():
                    break
                time.sleep(0.02)
        finally:
            self.stop()
        return self.summary(write_artifacts=True)

    def replay_log(self) -> list[dict[str, Any]]:
        return self.log.replay()

    def summary(self, write_artifacts: bool = False) -> dict[str, Any]:
        events = self.log.replay()
        ticks = [e for e in events if e.get("type") == "control_tick"]
        safety_stops = [e for e in events if e.get("type") == "safety_stop"]
        report = {
            "classification": self.CLASSIFICATION,
            "ticks": len(ticks),
            "total_events": len(events),
            "final_state": self.state.snapshot(),
            "safe": self.state.safe,
            "stop_reason": self.state.stop_reason or (
                safety_stops[-1]["reason"] if safety_stops else "completed"
            ),
            "hz": self.hz,
            "max_ticks": self.max_ticks,
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
        if ticks:
            report["pose_min"] = min(e["pose"] for e in ticks)
            report["pose_max"] = max(e["pose"] for e in ticks)
            report["temp_max"] = max(e["temperature"] for e in ticks)
        if write_artifacts:
            report["artifact_paths"] = self._write_artifacts(report, events)
        return report

    def _write_artifacts(
        self, report: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "autonomy_os"
        out.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        stem = f"{stamp}-autonomy_os_run"
        json_path = out / f"{stem}.json"
        jsonl_path = out / f"{stem}.jsonl"
        md_path = out / f"{stem}.md"

        write_json(json_path, report)
        self.log.export_jsonl(jsonl_path)
        md = (
            "# Autonomy OS Run Report\n\n"
            f"**{self.CLASSIFICATION}**\n\n"
            f"- ticks: `{report['ticks']}`\n"
            f"- safe: `{report['safe']}`\n"
            f"- stop_reason: `{report['stop_reason']}`\n"
            f"- final pose/vel/temp: "
            f"`{report['final_state']['pose']:.3f}` / "
            f"`{report['final_state']['velocity']:.3f}` / "
            f"`{report['final_state']['temperature']:.2f}`\n"
        )
        write_text(md_path, md)
        return {
            "markdown": str(md_path),
            "json": str(json_path),
            "jsonl": str(jsonl_path),
        }


def demo(seconds: float = 2.0, hz: float = 50.0, max_ticks: int = 200) -> dict[str, Any]:
    aos = AutonomyOS(hz=hz, max_ticks=max_ticks)
    return aos.run_for(seconds=seconds)


if __name__ == "__main__":
    summary = demo()
    print(json.dumps(summary, indent=2))
    print("\n--- Event Log (last 5) ---")
    # quick replay tail via new instance not available; re-run short log print from file if present
    paths = summary.get("artifact_paths", {})
    if paths.get("jsonl"):
        lines = Path(paths["jsonl"]).read_text(encoding="utf-8").strip().splitlines()
        for line in lines[-5:]:
            print(line)
