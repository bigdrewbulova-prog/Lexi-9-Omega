from pathlib import Path

import pytest

from app.memory import LocalMemory
from app.security import OpenVASManager


def test_preview_scan_returns_safe_plan(tmp_path: Path):
    memory = LocalMemory(base_dir=tmp_path)
    manager = OpenVASManager(memory)

    plan = manager.preview_scan("core", "127.0.0.1", "Full and fast")

    assert plan["stage"] == "preview"
    assert plan["target"] == "127.0.0.1"
    assert plan["auto_execute"] is False
    assert plan["safety"]["network_scan_from_lexi"] is False


def test_request_scan_requires_owner_approval(tmp_path: Path):
    memory = LocalMemory(base_dir=tmp_path)
    manager = OpenVASManager(memory)

    with pytest.raises(PermissionError):
        manager.request_scan("core", "127.0.0.1", "Full and fast", owner_approved=False)


def test_request_scan_logs_without_executing(tmp_path: Path):
    memory = LocalMemory(base_dir=tmp_path)
    manager = OpenVASManager(memory)

    result = manager.request_scan("core", "localhost", "Discovery", owner_approved=True)

    assert result["status"] == "requested_not_started"
    assert result["scan_id"].startswith("LEXI-SCAN-")
    assert result["execution_mode"] == "manual_only"
    assert memory.logs_path.exists()
    log_text = memory.logs_path.read_text(encoding="utf-8")
    assert "scan_requested" in log_text


def test_invalid_target_rejected(tmp_path: Path):
    memory = LocalMemory(base_dir=tmp_path)
    manager = OpenVASManager(memory)

    with pytest.raises(ValueError):
        manager.preview_scan("core", "127.0.0.1; rm -rf /", "Full and fast")
