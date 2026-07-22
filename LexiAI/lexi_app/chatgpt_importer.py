#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.memory import upsert_project_files

try:
    from .project_scanner import ProjectScanner
except ImportError:
    from project_scanner import ProjectScanner


CHAT_LOGS_DIR = ROOT / "chat_logs"
WORKSPACE_DIR = ROOT / "workspace"

CONVERSATION_FILE_RE = re.compile(r"^conversations(?:[_-]?\d+)?\.json$", re.IGNORECASE)
SKIPPED_ASSET_NAMES = {
    "account.json",
    "chat.html",
    "conversations.json",
    "message_feedback.json",
    "model_comparisons.json",
    "shared_conversations.json",
    "user.json",
}
ASSET_DIR_MARKERS = {
    "attachments",
    "files",
    "file_uploads",
    "library",
    "project_files",
    "uploads",
}
ASSET_SUFFIXES = {
    ".csv",
    ".doc",
    ".docx",
    ".gif",
    ".jpeg",
    ".jpg",
    ".jsonl",
    ".md",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".py",
    ".rtf",
    ".txt",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}


@dataclass
class ImportResult:
    source: str
    output_dir: str
    files_dir: str
    conversations_imported: int
    messages_imported: int
    assets_copied: int
    indexed_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "output_dir": self.output_dir,
            "files_dir": self.files_dir,
            "conversations_imported": self.conversations_imported,
            "messages_imported": self.messages_imported,
            "assets_copied": self.assets_copied,
            "indexed_count": self.indexed_count,
        }


def import_chatgpt_export(
    source: Path | str,
    output_root: Path | str = ROOT,
    scan_after: bool = True,
    max_files: int = 1000,
) -> ImportResult:
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"ChatGPT export not found: {source_path}")

    output_root_path = Path(output_root).expanduser().resolve()
    chat_logs_dir = output_root_path / "chat_logs"
    workspace_dir = output_root_path / "workspace"
    chat_logs_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    with _prepared_export(source_path) as export_root:
        import_id = _import_id(source_path)
        output_dir = _unique_dir(chat_logs_dir / f"chatgpt_{import_id}")
        files_dir = _unique_dir(workspace_dir / "chatgpt_files" / import_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        files_dir.mkdir(parents=True, exist_ok=True)

        conversations, message_count = _write_conversations(export_root, output_dir)
        assets_copied = _copy_assets(export_root, files_dir)
        indexed_count = _scan_outputs([output_dir, files_dir], max_files) if scan_after else 0

    return ImportResult(
        source=str(source_path),
        output_dir=str(output_dir),
        files_dir=str(files_dir),
        conversations_imported=conversations,
        messages_imported=message_count,
        assets_copied=assets_copied,
        indexed_count=indexed_count,
    )


class _prepared_export:
    def __init__(self, source_path: Path) -> None:
        self.source_path = source_path
        self._tmp: Optional[tempfile.TemporaryDirectory[str]] = None

    def __enter__(self) -> Path:
        if self.source_path.is_dir():
            return self.source_path
        if not zipfile.is_zipfile(self.source_path):
            raise ValueError(f"Expected a ChatGPT export ZIP or extracted folder: {self.source_path}")

        self._tmp = tempfile.TemporaryDirectory(prefix="lexi_chatgpt_export_")
        target = Path(self._tmp.name)
        try:
            with zipfile.ZipFile(self.source_path) as archive:
                _safe_extract(archive, target)
        except Exception:
            self._tmp.cleanup()
            self._tmp = None
            raise
        return target

    def __exit__(self, *_exc: object) -> None:
        if self._tmp:
            self._tmp.cleanup()


def _safe_extract(archive: zipfile.ZipFile, target: Path) -> None:
    target = target.resolve()
    for member in archive.infolist():
        member_path = (target / member.filename).resolve()
        if target != member_path and target not in member_path.parents:
            raise ValueError(f"Unsafe path in ZIP export: {member.filename}")
    archive.extractall(target)


def _import_id(source_path: Path) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{_slug(source_path.stem, 'export', max_len=36)}"


def _unique_dir(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.name}_{index}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not choose a unique output folder for {path}")


def _write_conversations(export_root: Path, output_dir: Path) -> tuple[int, int]:
    manifest_path = output_dir / "manifest.jsonl"
    messages_path = output_dir / "messages.jsonl"
    seen_ids: set[str] = set()
    conversation_count = 0
    message_count = 0

    with manifest_path.open("w", encoding="utf-8") as manifest_file, messages_path.open(
        "w", encoding="utf-8"
    ) as messages_file:
        for conversation in _iter_conversations(export_root):
            conversation_id = str(conversation.get("id") or conversation.get("conversation_id") or "")
            if not conversation_id:
                conversation_id = _slug(conversation.get("title") or "conversation", "conversation")
            if conversation_id in seen_ids:
                continue
            seen_ids.add(conversation_id)

            title = _clean_title(conversation.get("title") or "Untitled conversation")
            created_at = _time_label(conversation.get("create_time"))
            updated_at = _time_label(conversation.get("update_time"))
            messages = list(_messages_from_conversation(conversation))
            file_name = _conversation_file_name(conversation_count + 1, title, created_at)
            markdown_path = output_dir / file_name
            _write_markdown(markdown_path, conversation_id, title, created_at, updated_at, messages)

            manifest = {
                "conversation_id": conversation_id,
                "title": title,
                "created_at": created_at,
                "updated_at": updated_at,
                "message_count": len(messages),
                "markdown_path": str(markdown_path),
                "project": _project_metadata(conversation),
            }
            manifest_file.write(json.dumps(manifest, ensure_ascii=True, sort_keys=True) + "\n")

            for message in messages:
                row = {
                    "conversation_id": conversation_id,
                    "title": title,
                    "role": message["role"],
                    "created_at": message["created_at"],
                    "text": message["text"],
                    "attachments": message["attachments"],
                }
                messages_file.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")

            conversation_count += 1
            message_count += len(messages)

    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# ChatGPT Export Import",
                "",
                f"Imported conversations: {conversation_count}",
                f"Imported messages: {message_count}",
                "",
                "Files:",
                "- `manifest.jsonl`: one row per conversation.",
                "- `messages.jsonl`: one row per message.",
                "- `*.md`: readable conversation transcripts for LexiAI scanning.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return conversation_count, message_count


def _iter_conversations(export_root: Path) -> Iterator[dict[str, Any]]:
    files = sorted(
        path
        for path in export_root.rglob("*.json")
        if CONVERSATION_FILE_RE.match(path.name)
    )
    for path in files:
        data = _load_json(path)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    yield item
        elif isinstance(data, dict):
            items = data.get("conversations")
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        yield item


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _messages_from_conversation(conversation: dict[str, Any]) -> Iterator[dict[str, Any]]:
    if isinstance(conversation.get("messages"), list):
        for message in conversation["messages"]:
            normalized = _normalize_message(message)
            if normalized:
                yield normalized
        return

    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return

    nodes = _ordered_nodes(conversation, mapping)
    for node in nodes:
        raw_message = node.get("message") if isinstance(node, dict) else None
        if not isinstance(raw_message, dict):
            continue
        normalized = _normalize_message(raw_message)
        if normalized:
            yield normalized


def _ordered_nodes(conversation: dict[str, Any], mapping: dict[str, Any]) -> list[dict[str, Any]]:
    current_node = conversation.get("current_node")
    if current_node in mapping:
        ordered: list[dict[str, Any]] = []
        seen: set[str] = set()
        node_id = current_node
        while node_id and node_id in mapping and node_id not in seen:
            seen.add(node_id)
            node = mapping[node_id]
            if isinstance(node, dict):
                ordered.append(node)
                node_id = node.get("parent")
            else:
                break
        ordered.reverse()
        if ordered:
            return ordered

    nodes = [node for node in mapping.values() if isinstance(node, dict)]
    return sorted(nodes, key=_node_sort_key)


def _node_sort_key(node: dict[str, Any]) -> tuple[float, str]:
    message = node.get("message") if isinstance(node.get("message"), dict) else {}
    raw_time = message.get("create_time") if isinstance(message, dict) else None
    try:
        timestamp = float(raw_time)
    except (TypeError, ValueError):
        timestamp = 0.0
    return timestamp, str(node.get("id") or "")


def _normalize_message(message: dict[str, Any]) -> Optional[dict[str, Any]]:
    role = (
        message.get("role")
        or (message.get("author") or {}).get("role")
        or message.get("sender")
        or "unknown"
    )
    content = _content_to_text(message.get("content"))
    attachments = _attachments(message)
    if not content and not attachments:
        return None
    return {
        "role": str(role),
        "created_at": _time_label(message.get("create_time") or message.get("created_at")),
        "text": content,
        "attachments": attachments,
    }


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, dict):
        return ""

    parts = content.get("parts")
    if isinstance(parts, list):
        rendered = [_part_to_text(part) for part in parts]
        return "\n\n".join(part for part in rendered if part).strip()

    for key in ("text", "content", "result"):
        value = content.get(key)
        if isinstance(value, str):
            return value.strip()

    return ""


def _part_to_text(part: Any) -> str:
    if isinstance(part, str):
        return part.strip()
    if isinstance(part, dict):
        for key in ("text", "content", "name", "file_name"):
            value = part.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return json.dumps(part, ensure_ascii=True, sort_keys=True)
    return str(part).strip()


def _attachments(message: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
    raw_attachments = metadata.get("attachments") or message.get("attachments") or []
    if not isinstance(raw_attachments, list):
        return []
    attachments = []
    for item in raw_attachments:
        if isinstance(item, dict):
            attachments.append(
                {
                    "name": item.get("name") or item.get("file_name") or item.get("title"),
                    "id": item.get("id") or item.get("file_id"),
                    "mime_type": item.get("mime_type") or item.get("content_type"),
                }
            )
        else:
            attachments.append({"name": str(item), "id": None, "mime_type": None})
    return attachments


def _write_markdown(
    path: Path,
    conversation_id: str,
    title: str,
    created_at: str,
    updated_at: str,
    messages: Iterable[dict[str, Any]],
) -> None:
    lines = [
        f"# {title}",
        "",
        f"- Conversation ID: {conversation_id}",
        f"- Created: {created_at or 'unknown'}",
        f"- Updated: {updated_at or 'unknown'}",
        "",
        "## Messages",
        "",
    ]
    for message in messages:
        role = _clean_title(message["role"]).title()
        created = message["created_at"] or "unknown time"
        lines.extend([f"### {role} - {created}", ""])
        if message["text"]:
            lines.extend([message["text"].strip(), ""])
        if message["attachments"]:
            lines.append("Attachments:")
            for attachment in message["attachments"]:
                name = attachment.get("name") or "unnamed"
                mime_type = attachment.get("mime_type") or "unknown type"
                lines.append(f"- {name} ({mime_type})")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _conversation_file_name(index: int, title: str, created_at: str) -> str:
    date = created_at[:10] if created_at else "unknown-date"
    return f"{index:04d}_{date}_{_slug(title, 'conversation')}.md"


def _project_metadata(conversation: dict[str, Any]) -> dict[str, Any]:
    metadata = conversation.get("metadata") if isinstance(conversation.get("metadata"), dict) else {}
    keys = ["project_id", "project_name", "conversation_template_id", "workspace_id"]
    return {
        key: conversation.get(key) or metadata.get(key)
        for key in keys
        if conversation.get(key) or metadata.get(key)
    }


def _copy_assets(export_root: Path, files_dir: Path) -> int:
    copied = 0
    manifest = []
    for path in export_root.rglob("*"):
        if not path.is_file() or _is_conversation_json(path):
            continue
        relative = path.relative_to(export_root)
        if not _looks_like_asset(relative):
            continue
        target = files_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied += 1
        manifest.append({"source_path": str(relative), "copied_path": str(target), "size": target.stat().st_size})

    manifest_path = files_dir / "asset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True), encoding="utf-8")
    return copied


def _looks_like_asset(relative: Path) -> bool:
    lower_parts = {part.lower() for part in relative.parts}
    if relative.name.lower() in SKIPPED_ASSET_NAMES:
        return False
    if lower_parts & ASSET_DIR_MARKERS:
        return True
    return relative.suffix.lower() in ASSET_SUFFIXES


def _is_conversation_json(path: Path) -> bool:
    return bool(CONVERSATION_FILE_RE.match(path.name))


def _scan_outputs(roots: list[Path], max_files: int) -> int:
    scanner = ProjectScanner(roots=[str(root) for root in roots], max_files=max_files)
    records = scanner.scan()
    return upsert_project_files(records)


def _time_label(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat(timespec="seconds")
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        try:
            return datetime.fromtimestamp(float(stripped), tz=timezone.utc).isoformat(timespec="seconds")
        except ValueError:
            return stripped
    return str(value)


def _clean_title(value: Any) -> str:
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text) or "Untitled conversation"


def _slug(value: Any, fallback: str, max_len: int = 72) -> str:
    text = _clean_title(value).lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text).strip("-._")
    if not text:
        text = fallback
    return text[:max_len].strip("-._") or fallback


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Import a ChatGPT data export into LexiAI.")
    parser.add_argument("source", help="Path to the ChatGPT export ZIP or extracted export folder.")
    parser.add_argument("--no-scan", action="store_true", help="Import files without updating LexiAI's local index.")
    parser.add_argument("--max-files", type=int, default=1000, help="Maximum imported files to index after import.")
    args = parser.parse_args(argv)

    result = import_chatgpt_export(args.source, scan_after=not args.no_scan, max_files=args.max_files)
    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
