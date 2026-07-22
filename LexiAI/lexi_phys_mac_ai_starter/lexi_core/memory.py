from datetime import datetime, timezone
import json
from .config import MEMORY_PATH

def save_memory(role: str, content: str, tags=None):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    item = {
        "time": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "content": content,
        "tags": tags or []
    }
    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def load_recent_memory(limit: int = 20):
    if not MEMORY_PATH.exists():
        return []
    lines = MEMORY_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    items = []
    for line in lines[-limit:]:
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items
