#!/usr/bin/env python3
"""Inject project-board recovery context at Claude Code session start."""

from __future__ import annotations

from hook_common import board_state_path, concise_error, project_root, read_payload, run_board


def main() -> int:
    payload = read_payload()
    root = project_root(payload)
    if not board_state_path(root).exists():
        print(
            "For non-trivial coding work, activate `tracking-project-progress` before "
            "substantive edits so this project gets a durable progress board."
        )
        return 0
    result = run_board(root, "resume")
    if result.returncode == 0:
        print(result.stdout, end="")
    else:
        print(f"Project board could not be resumed: {concise_error(result)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

