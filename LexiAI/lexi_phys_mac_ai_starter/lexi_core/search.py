import json
from .config import INDEX_PATH

def load_index():
    if not INDEX_PATH.exists():
        return []
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def search_files(query: str, limit: int = 5):
    q = query.lower()
    scored = []
    for item in load_index():
        text = (item.get("text") or "").lower()
        path = item.get("path", "")
        score = 0
        for term in q.split():
            if term in text:
                score += text.count(term)
            if term in path.lower():
                score += 3
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]
