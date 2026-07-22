from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path


class ChatGPTImporterTests(unittest.TestCase):
    def test_import_zip_writes_transcripts_assets_and_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export_dir = root / "export"
            upload_dir = export_dir / "uploads"
            upload_dir.mkdir(parents=True)
            (upload_dir / "requirements.md").write_text("# Requirements\nBuild Lexi.", encoding="utf-8")
            (export_dir / "user.json").write_text('{"email":"private@example.com"}', encoding="utf-8")
            (export_dir / "conversations.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "conv-123",
                            "title": "Build Lexi importer",
                            "create_time": 1710000000,
                            "update_time": 1710000600,
                            "current_node": "assistant-1",
                            "mapping": {
                                "root": {"id": "root", "message": None, "parent": None},
                                "user-1": {
                                    "id": "user-1",
                                    "parent": "root",
                                    "message": {
                                        "author": {"role": "user"},
                                        "create_time": 1710000001,
                                        "content": {"parts": ["Pull my ChatGPT project chats."]},
                                        "metadata": {
                                            "attachments": [
                                                {"name": "requirements.md", "mime_type": "text/markdown"}
                                            ]
                                        },
                                    },
                                },
                                "assistant-1": {
                                    "id": "assistant-1",
                                    "parent": "user-1",
                                    "message": {
                                        "author": {"role": "assistant"},
                                        "create_time": 1710000002,
                                        "content": {"parts": ["Imported and indexed."]},
                                    },
                                },
                            },
                        }
                    ]
                ),
                encoding="utf-8",
            )

            zip_path = root / "chatgpt-export.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                for path in export_dir.rglob("*"):
                    archive.write(path, path.relative_to(export_dir))

            previous_db = os.environ.get("LEXI_MEMORY_DB")
            os.environ["LEXI_MEMORY_DB"] = str(root / "memory.db")

            import brain.memory as memory
            import lexi_app.chatgpt_importer as chatgpt_importer

            try:
                importlib.reload(memory)
                importlib.reload(chatgpt_importer)

                result = chatgpt_importer.import_chatgpt_export(zip_path, output_root=root)

                self.assertEqual(result.conversations_imported, 1)
                self.assertEqual(result.messages_imported, 2)
                self.assertEqual(result.assets_copied, 1)
                self.assertGreaterEqual(result.indexed_count, 1)

                output_dir = Path(result.output_dir)
                transcript = next(output_dir.glob("*.md")).read_text(encoding="utf-8")
                self.assertIn("Build Lexi importer", transcript)
                self.assertIn("Pull my ChatGPT project chats.", transcript)
                self.assertIn("Imported and indexed.", transcript)
                self.assertTrue((Path(result.files_dir) / "uploads" / "requirements.md").exists())
                self.assertFalse((Path(result.files_dir) / "user.json").exists())
            finally:
                if previous_db is None:
                    os.environ.pop("LEXI_MEMORY_DB", None)
                else:
                    os.environ["LEXI_MEMORY_DB"] = previous_db
                importlib.reload(memory)

    def test_import_rejects_zip_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "bad-export.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("../outside.txt", "nope")

            import lexi_app.chatgpt_importer as chatgpt_importer

            with self.assertRaises(ValueError):
                chatgpt_importer.import_chatgpt_export(zip_path, output_root=root)


if __name__ == "__main__":
    unittest.main()
