#!/usr/bin/env python3
"""Shared helpers for Claude Code project-board hooks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
BOARD_CLI = (
    PLUGIN_ROOT
    / "skills"
    / "tracking-project-progress"
    / "scripts"
    / "project_board.py"
)
TRACKED_SUFFIXES = {
    ".bash",
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".fish",
    ".go",
    ".gradle",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsonc",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
    ".zsh",
}
TRACKED_FILENAMES = {
    "Dockerfile",
    "Gemfile",
    "Justfile",
    "Makefile",
    "Procfile",
    "Rakefile",
}
IGNORED_PARTS = {
    ".git",
    ".project-board",
    ".venv",
    "dist",
    "node_modules",
    "target",
    "vendor",
}


def read_payload() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def project_root(payload: dict[str, Any]) -> Path:
    start_value = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()
    start = Path(start_value).resolve()
    probe = start
    while probe != probe.parent:
        if (probe / ".git").exists():
            return probe
        probe = probe.parent
    return start


def board_state_path(root: Path) -> Path:
    return root / ".project-board" / "state.json"


def run_board(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BOARD_CLI), *args, "--project-root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


def is_trackable_file(root: Path, value: str | None) -> bool:
    if not value:
        return False
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return False
    if any(part in IGNORED_PARTS for part in relative.parts):
        return False
    return relative.name in TRACKED_FILENAMES or relative.suffix.lower() in TRACKED_SUFFIXES


def concise_error(result: subprocess.CompletedProcess[str]) -> str:
    message = (result.stderr or result.stdout).strip()
    return message.splitlines()[-1] if message else f"exit code {result.returncode}"

