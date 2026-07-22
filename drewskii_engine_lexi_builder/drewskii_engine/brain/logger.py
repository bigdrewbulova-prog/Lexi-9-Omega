from pathlib import Path
from datetime import datetime

LOG_PATH = Path(__file__).resolve().parents[1] / "memory" / "project_log.md"


def log_event(note: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"- {timestamp}: {note}\n")
