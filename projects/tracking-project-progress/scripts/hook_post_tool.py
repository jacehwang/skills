#!/usr/bin/env python3
"""Capture successful Claude Code source edits in the project board."""

from __future__ import annotations

import sys

from hook_common import (
    board_state_path,
    concise_error,
    is_trackable_file,
    project_root,
    read_payload,
    run_board,
)


def main() -> int:
    payload = read_payload()
    if payload.get("tool_name") not in {"Write", "Edit"}:
        return 0
    root = project_root(payload)
    tool_input = payload.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not is_trackable_file(root, file_path):
        return 0
    if not board_state_path(root).exists():
        objective = (
            f"Maintain coding progress for {root.name}; refine this objective from the current request."
        )
        ensured = run_board(root, "ensure", "--objective", objective)
        if ensured.returncode != 0:
            print(f"project-board hook: {concise_error(ensured)}", file=sys.stderr)
            return 0
    recorded = run_board(root, "record-file", "--path", str(file_path))
    if recorded.returncode != 0:
        print(f"project-board hook: {concise_error(recorded)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

