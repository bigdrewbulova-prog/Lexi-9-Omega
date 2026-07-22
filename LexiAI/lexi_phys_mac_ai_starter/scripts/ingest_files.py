from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "sources.json"
OUT = ROOT / "data" / "index" / "lexi_index.json"

def read_text(path: Path, max_chars=25000):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""

def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    exts = set(cfg.get("extensions", []))
    items = []
    seen = set()

    for folder in cfg.get("folders", []):
        folder_path = Path(folder).expanduser()
        if not folder_path.exists():
            print(f"skip missing: {folder_path}")
            continue

        for p in folder_path.rglob("*"):
            if not p.is_file():
                continue
            if exts and p.suffix.lower() not in exts:
                continue
            try:
                if p.stat().st_size > 5_000_000:
                    continue
            except Exception:
                continue

            text = read_text(p)
            if not text.strip():
                continue

            digest = hashlib.sha256(str(p).encode("utf-8")).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)

            items.append({
                "id": digest,
                "path": str(p),
                "name": p.name,
                "suffix": p.suffix.lower(),
                "text": text
            })
            print(f"indexed: {p}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone. Indexed {len(items)} files -> {OUT}")

if __name__ == "__main__":
    main()
