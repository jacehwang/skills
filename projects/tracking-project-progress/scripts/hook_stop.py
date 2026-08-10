#!/usr/bin/env python3
"""Require a project-board checkpoint before a code-changing turn stops."""

from __future__ import annotations

import json
import sys

from hook_common import board_state_path, project_root, read_payload


def main() -> int:
    payload = read_payload()
    root = project_root(payload)
    state_path = board_state_path(root)
    if not state_path.exists():
        return 0
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    session = state.get("session") if isinstance(state, dict) else None
    dirty = isinstance(session, dict) and session.get("needs_checkpoint") is True
    if not dirty or payload.get("stop_hook_active") is True:
        return 0
    print(
        "Project board checkpoint required before stopping. Activate "
        "`tracking-project-progress`, record the exact verification outcome, and run "
        "`checkpoint` with `--summary`, `--focus`, and one concrete `--next` action. "
        "Do not claim overall completion if broader verification is still missing.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

