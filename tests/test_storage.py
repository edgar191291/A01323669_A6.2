# pylint: disable=missing-function-docstring,consider-using-with
# pylint: disable=missing-function-docstring
# !/usr/bin/env python3
"""
test_storage.py

Unit tests for storage.py.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.storage import read_json_list, write_json_list


class StorageTestCase(unittest.TestCase):
    """Tests for JSON storage helpers."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_read_missing_file_creates_and_returns_empty(self) -> None:
        path = self.base / "missing.json"
        data = read_json_list(path)
        self.assertEqual(data, [])
        self.assertTrue(path.exists())
        self.assertEqual(path.read_text(encoding="utf-8"), "[]")

    def test_read_empty_file_returns_empty(self) -> None:
        path = self.base / "empty.json"
        path.write_text("", encoding="utf-8")
        data = read_json_list(path)
        self.assertEqual(data, [])

    def test_read_invalid_json_returns_empty(self) -> None:
        path = self.base / "bad.json"
        path.write_text("{bad json", encoding="utf-8")
        data = read_json_list(path)
        self.assertEqual(data, [])

    def test_read_non_list_json_returns_empty(self) -> None:
        path = self.base / "not_list.json"
        path.write_text('{"a":1}', encoding="utf-8")
        data = read_json_list(path)
        self.assertEqual(data, [])

    def test_read_list_filters_non_dict_items(self) -> None:
        path = self.base / "mixed.json"
        path.write_text('[{"a":1}, 2, "x"]', encoding="utf-8")
        data = read_json_list(path)
        self.assertEqual(data, [{"a": 1}])

    def test_read_utf8_bom_is_supported(self) -> None:
        path = self.base / "bom.json"
        path.write_text("\ufeff[]", encoding="utf-8")
        data = read_json_list(path)
        self.assertEqual(data, [])

    def test_write_json_list_writes_pretty_json(self) -> None:
        path = self.base / "out.json"
        write_json_list(path, [{"a": 1}])
        text = path.read_text(encoding="utf-8")
        self.assertIn('"a"', text)
        self.assertIn("1", text)

    def test_write_json_list_rejects_non_list(self) -> None:
        path = self.base / "out2.json"
        write_json_list(path, "not-a-list")  # type: ignore[arg-type]
        self.assertTrue(path.exists())  # created as []
        self.assertEqual(path.read_text(encoding="utf-8"), "[]")

    def test_write_json_list_handles_non_serializable(self) -> None:
        path = self.base / "bad_write.json"
        write_json_list(path, [{"a": object()}])  # object() no es JSON serializable
        # Debe seguir existiendo el archivo (creado por ensure_file_exists)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
