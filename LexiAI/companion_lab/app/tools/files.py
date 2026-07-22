from pathlib import Path
from typing import List


def list_directory(path: str) -> List[str]:
    root = Path(path)
    if not root.exists() or not root.is_dir():
        return []
    return [str(child) for child in root.iterdir()]


def read_file(path: str) -> str:
    root = Path(path)
    if not root.exists() or not root.is_file():
        return ""
    return root.read_text(encoding="utf-8")
