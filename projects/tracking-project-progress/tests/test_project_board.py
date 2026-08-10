from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "tracking-project-progress" / "scripts" / "project_board.py"


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args, "--project-root", str(project_root)],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


def load_state(project_root: Path) -> dict:
    return json.loads((project_root / ".project-board" / "state.json").read_text(encoding="utf-8"))


class ProjectBoardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name).resolve()

    def test_ensure_creates_resumeable_board(self) -> None:
        result = run_cli(self.root, "ensure", "--objective", "Add token refresh")

        self.assertEqual(result.returncode, 0, result.stderr)
        state = load_state(self.root)
        self.assertEqual(state["schema_version"], "1.0")
        self.assertEqual(state["revision"], 1)
        self.assertEqual(state["project"]["objective"], "Add token refresh")
        self.assertEqual(state["status"], "active")
        self.assertTrue((self.root / ".project-board" / "board.md").exists())
        self.assertTrue((self.root / ".project-board" / "events.jsonl").exists())

        resumed = run_cli(self.root, "resume")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("Add token refresh", resumed.stdout)
        self.assertIn("Next action", resumed.stdout)

    def test_task_commands_enforce_unique_ids_and_single_active_task(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Ship sync").returncode, 0)

        added = run_cli(
            self.root,
            "task-add",
            "--id",
            "sync-tests",
            "--title",
            "Add sync command tests",
            "--status",
            "doing",
        )
        self.assertEqual(added.returncode, 0, added.stderr)
        duplicate = run_cli(
            self.root,
            "task-add",
            "--id",
            "sync-tests",
            "--title",
            "Duplicate",
        )
        self.assertEqual(duplicate.returncode, 2)
        second_active = run_cli(
            self.root,
            "task-add",
            "--id",
            "sync-cli",
            "--title",
            "Implement sync command",
            "--status",
            "doing",
        )
        self.assertEqual(second_active.returncode, 2)

        updated = run_cli(
            self.root,
            "task-update",
            "--id",
            "sync-tests",
            "--status",
            "done",
            "--notes",
            "Focused tests pass",
        )
        self.assertEqual(updated.returncode, 0, updated.stderr)
        state = load_state(self.root)
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertEqual(state["tasks"][0]["notes"], "Focused tests pass")

    def test_record_file_marks_dirty_and_checkpoint_clears_it(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Add token refresh").returncode, 0)

        recorded = run_cli(self.root, "record-file", "--path", "src/auth.py")
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        recorded_again = run_cli(self.root, "record-file", "--path", str(self.root / "src/auth.py"))
        self.assertEqual(recorded_again.returncode, 0, recorded_again.stderr)
        state = load_state(self.root)
        self.assertEqual(state["changed_files"], ["src/auth.py"])
        self.assertTrue(state["session"]["needs_checkpoint"])

        checkpointed = run_cli(
            self.root,
            "checkpoint",
            "--summary",
            "Implemented refresh parsing",
            "--focus",
            "Token refresh",
            "--next",
            "Add expiry tests",
            "--verification",
            "python3 -m unittest tests.test_auth::pass",
        )
        self.assertEqual(checkpointed.returncode, 0, checkpointed.stderr)
        state = load_state(self.root)
        self.assertFalse(state["session"]["needs_checkpoint"])
        self.assertEqual(state["session"]["last_summary"], "Implemented refresh parsing")
        self.assertEqual(state["next_action"], "Add expiry tests")
        self.assertEqual(
            state["verifications"][-1],
            {
                "at": state["verifications"][-1]["at"],
                "command": "python3 -m unittest tests.test_auth",
                "outcome": "pass",
            },
        )

    def test_record_file_rejects_paths_outside_project(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Safe paths").returncode, 0)
        outside = self.root.parent / "secret.py"

        result = run_cli(self.root, "record-file", "--path", str(outside))

        self.assertEqual(result.returncode, 2)
        self.assertIn("outside", result.stderr.lower())
        self.assertEqual(load_state(self.root)["changed_files"], [])

    def test_checkpoint_rejects_blank_recovery_fields(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Durable handoff").returncode, 0)

        for flag, value in (("--summary", "  "), ("--focus", "\t"), ("--next", "\n")):
            arguments = {
                "--summary": "Implemented the parser",
                "--focus": "Parser verification",
                "--next": "Run the full test suite",
            }
            arguments[flag] = value
            result = run_cli(
                self.root,
                "checkpoint",
                "--summary",
                arguments["--summary"],
                "--focus",
                arguments["--focus"],
                "--next",
                arguments["--next"],
            )

            self.assertEqual(result.returncode, 2, (flag, result.stderr))

        self.assertEqual(load_state(self.root)["revision"], 1)

    def test_validate_rejects_blank_recovery_state(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Validate handoff").returncode, 0)
        state_path = self.root / ".project-board" / "state.json"

        for field_path in (("current_focus",), ("next_action",), ("session", "last_summary")):
            state = load_state(self.root)
            target = state
            for key in field_path[:-1]:
                target = target[key]
            target[field_path[-1]] = "   "
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_cli(self.root, "validate")

            self.assertEqual(result.returncode, 2, (field_path, result.stderr))
            self.assertIn("non-empty", result.stderr)
            state = load_state(self.root)
            target = state
            for key in field_path[:-1]:
                target = target[key]
            target[field_path[-1]] = "restored"
            state_path.write_text(json.dumps(state), encoding="utf-8")

    def test_validate_rejects_malformed_nested_entries_and_paths(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Validate nested data").returncode, 0)
        state_path = self.root / ".project-board" / "state.json"
        invalid_mutations = (
            lambda state: state["tasks"].append(
                {"id": "Not Kebab", "title": "", "status": "todo", "notes": 7}
            ),
            lambda state: state["decisions"].append(
                {"at": "", "decision": "", "rationale": "because"}
            ),
            lambda state: state["verifications"].append(
                {"at": "now", "command": "", "outcome": "pass"}
            ),
            lambda state: state["changed_files"].append("../outside.py"),
            lambda state: state["blockers"].append("  "),
            lambda state: state["blockers"].append("None"),
        )

        for mutate in invalid_mutations:
            state = load_state(self.root)
            mutate(state)
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_cli(self.root, "validate")

            self.assertEqual(result.returncode, 2, result.stderr)
            state_path.unlink()
            self.assertEqual(run_cli(self.root, "ensure", "--objective", "Validate nested data").returncode, 0)

    def test_task_add_rejects_invalid_identifier_and_empty_title(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Valid tasks").returncode, 0)

        invalid_id = run_cli(
            self.root,
            "task-add",
            "--id",
            "Build Feature",
            "--title",
            "Build the feature",
        )
        empty_title = run_cli(
            self.root,
            "task-add",
            "--id",
            "build-feature",
            "--title",
            "  ",
        )

        self.assertEqual(invalid_id.returncode, 2, invalid_id.stderr)
        self.assertEqual(empty_title.returncode, 2, empty_title.stderr)
        self.assertEqual(load_state(self.root)["tasks"], [])

    def test_checkpoint_can_clear_resolved_blockers(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Resolve blocker").returncode, 0)
        blocked = run_cli(
            self.root,
            "checkpoint",
            "--summary",
            "Cannot run integration tests",
            "--focus",
            "Integration verification",
            "--next",
            "Obtain test credentials",
            "--status",
            "blocked",
            "--blocker",
            "Missing test credentials",
        )
        self.assertEqual(blocked.returncode, 0, blocked.stderr)

        resumed = run_cli(
            self.root,
            "checkpoint",
            "--summary",
            "Credentials received",
            "--focus",
            "Integration verification",
            "--next",
            "Run integration tests",
            "--status",
            "active",
            "--clear-blockers",
        )

        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(load_state(self.root)["blockers"], [])

    def test_blocked_status_requires_a_real_blocker(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Track blockers").returncode, 0)

        missing = run_cli(
            self.root,
            "checkpoint",
            "--summary",
            "Work paused",
            "--focus",
            "External dependency",
            "--next",
            "Wait for dependency",
            "--status",
            "blocked",
        )
        placeholder = run_cli(
            self.root,
            "checkpoint",
            "--summary",
            "Work paused",
            "--focus",
            "External dependency",
            "--next",
            "Wait for dependency",
            "--blocker",
            "None",
        )

        self.assertEqual(missing.returncode, 2, missing.stderr)
        self.assertEqual(placeholder.returncode, 2, placeholder.stderr)
        self.assertEqual(load_state(self.root)["revision"], 1)

    def test_corrupt_state_is_preserved(self) -> None:
        board_dir = self.root / ".project-board"
        board_dir.mkdir()
        state_path = board_dir / "state.json"
        state_path.write_text("{broken", encoding="utf-8")

        result = run_cli(self.root, "ensure", "--objective", "Do not overwrite")

        self.assertEqual(result.returncode, 2)
        self.assertIn("corrupt", result.stderr.lower())
        self.assertEqual(state_path.read_text(encoding="utf-8"), "{broken")

    def test_validate_rejects_unsupported_schema(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Validate schema").returncode, 0)
        state_path = self.root / ".project-board" / "state.json"
        state = load_state(self.root)
        state["schema_version"] = "99.0"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        result = run_cli(self.root, "validate")

        self.assertEqual(result.returncode, 2)
        self.assertIn("schema_version", result.stderr)

    def test_mutations_increment_revision_and_append_events(self) -> None:
        self.assertEqual(run_cli(self.root, "ensure", "--objective", "Audit changes").returncode, 0)
        self.assertEqual(run_cli(self.root, "record-file", "--path", "src/app.py").returncode, 0)
        self.assertEqual(
            run_cli(
                self.root,
                "checkpoint",
                "--summary",
                "Recorded app change",
                "--focus",
                "App",
                "--next",
                "Run tests",
            ).returncode,
            0,
        )

        state = load_state(self.root)
        events = [
            json.loads(line)
            for line in (self.root / ".project-board" / "events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(state["revision"], 3)
        self.assertEqual([event["revision"] for event in events], [1, 2, 3])
        self.assertEqual([event["type"] for event in events], ["initialized", "file_recorded", "checkpointed"])


if __name__ == "__main__":
    unittest.main()
