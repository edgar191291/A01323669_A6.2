#!/usr/bin/env python3
"""
storage.py

Helper functions to persist application data in JSON files.

Key requirement: if invalid data is found, print an error and continue execution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def ensure_file_exists(path: Path) -> None:
    """
    Ensure the JSON file exists. If it does not, create it with an empty list [].

    The application stores collections (hotels/customers/reservations) as JSON lists.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
    except OSError as exc:
        _print_error(f"Cannot create data file '{path}': {exc}")


def read_json_list(path: Path) -> list[dict[str, Any]]:
    """
    Read a JSON file expected to contain a list of objects (dict).

    If the file is missing, invalid JSON, or not a list, prints an error and returns [].
    """
    ensure_file_exists(path)

    try:
        raw = path.read_text(encoding="utf-8-sig").strip()
        if not raw:
            _print_error(f"Empty file '{path}'. Using empty list [].")
            return []

        data = json.loads(raw)
        if not isinstance(data, list):
            _print_error(f"Invalid format in '{path}': expected a JSON list. Using [].")
            return []

        # Keep only dict items; ignore invalid entries but continue
        cleaned: list[dict[str, Any]] = []
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                cleaned.append(item)
            else:
                _print_error(
                    f"Invalid item type at index {idx} in '{path}': "
                    f"expected object/dict, got {type(item).__name__}. Skipping."
                )
        return cleaned

    except json.JSONDecodeError as exc:
        _print_error(f"Invalid JSON in '{path}': {exc}. Using empty list [].")
        return []
    except OSError as exc:
        _print_error(f"Cannot read file '{path}': {exc}. Using empty list [].")
        return []


def write_json_list(path: Path, data: list[dict[str, Any]]) -> None:
    """
    Write a list of dicts to a JSON file.

    Uses an atomic write (write temp file then replace) to reduce corruption risk.
    On error, prints an error and continues (does not raise).
    """
    ensure_file_exists(path)

    if not isinstance(data, list):
        _print_error(
            "write_json_list expected a list; got a non-list value. Skipping write."
            )
        return

    tmp_path = path.with_suffix(path.suffix + ".tmp")

    try:
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_path.write_text(payload + "\n", encoding="utf-8")
        tmp_path.replace(path)
    except (OSError, TypeError) as exc:
        _print_error(f"Cannot write file '{path}': {exc}.")
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError as cleanup_exc:
            _print_error(f"Cannot cleanup temp file '{tmp_path}': {cleanup_exc}.")
