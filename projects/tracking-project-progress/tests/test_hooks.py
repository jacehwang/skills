from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_project_board import CLI, load_state, run_cli


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = REPO_ROOT / "scripts"


def run_hook(name: str, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOKS_DIR / name)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name).resolve()

    def test_session_start_prints_existing_resume_packet(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Resume this objective").returncode, 0)

        result = run_hook("hook_session_start.py", {"cwd": str(self.root), "source": "resume"})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Resume this objective", result.stdout)
        self.assertIn("Project Progress Board", result.stdout)

    def test_session_start_without_board_only_injects_instruction(self) -> None:
        result = run_hook("hook_session_start.py", {"cwd": str(self.root), "source": "startup"})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tracking-project-progress", result.stdout)
        self.assertFalse((self.root / ".project-board").exists())

    def test_post_tool_initializes_and_tracks_code_file(self) -> None:
        source = self.root / "src" / "app.py"
        payload = {
            "cwd": str(self.root),
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "print('ok')"},
        }

        result = run_hook("hook_post_tool.py", payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        state = load_state(self.root)
        self.assertIn("src/app.py", state["changed_files"])
        self.assertTrue(state["session"]["needs_checkpoint"])

    def test_post_tool_ignores_documentation_and_board_files(self) -> None:
        for path in (self.root / "README.md", self.root / ".project-board" / "board.md"):
            result = run_hook(
                "hook_post_tool.py",
                {"cwd": str(self.root), "tool_name": "Edit", "tool_input": {"file_path": str(path)}},
            )
            self.assertEqual(result.returncode, 0, result.stderr)

        self.assertFalse((self.root / ".project-board" / "state.json").exists())

    def test_stop_blocks_dirty_board(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Checkpoint work").returncode, 0)
        self.assertEqual(run_cli(self.root, "record-file", "--path", "src/app.py").returncode, 0)

        result = run_hook("hook_stop.py", {"cwd": str(self.root), "stop_hook_active": False})

        self.assertEqual(result.returncode, 2)
        self.assertIn("checkpoint", result.stderr.lower())
        self.assertIn("--next", result.stderr)

    def test_stop_allows_clean_board_and_avoids_repeat_loop(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Checkpoint work").returncode, 0)
        clean = run_hook("hook_stop.py", {"cwd": str(self.root), "stop_hook_active": False})
        self.assertEqual(clean.returncode, 0, clean.stderr)

        self.assertEqual(run_cli(self.root, "record-file", "--path", "src/app.py").returncode, 0)
        repeated = run_hook("hook_stop.py", {"cwd": str(self.root), "stop_hook_active": True})
        self.assertEqual(repeated.returncode, 0, repeated.stderr)


if __name__ == "__main__":
    unittest.main()
