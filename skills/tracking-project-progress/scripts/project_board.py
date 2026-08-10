#!/usr/bin/env python3
"""Create and maintain a durable project progress board."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator


BOARD_DIR_NAME = ".project-board"
SCHEMA_VERSION = "1.0"
PROJECT_STATUSES = {"active", "blocked", "complete"}
TASK_STATUSES = {"todo", "doing", "done", "blocked"}
LOCK_TIMEOUT_SECONDS = 3.0
STALE_LOCK_SECONDS = 30.0
PLACEHOLDER_BLOCKERS = {"none", "n/a", "no blocker", "no blockers"}


class BoardError(Exception):
    """A user-correctable board error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def resolve_project_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    current = Path.cwd().resolve()
    probe = current
    while probe != probe.parent:
        if (probe / ".git").exists():
            return probe
        probe = probe.parent
    return current


def board_paths(root: Path) -> tuple[Path, Path, Path]:
    board_dir = root / BOARD_DIR_NAME
    return board_dir / "state.json", board_dir / "board.md", board_dir / "events.jsonl"


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def write_state(path: Path, state: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def load_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BoardError(
            f"Board state is corrupt at {path}; it was preserved unchanged. "
            "Repair or restore state.json before continuing."
        ) from exc
    except OSError as exc:
        raise BoardError(f"Cannot read board state at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BoardError(f"Board state at {path} must be a JSON object.")
    return value


@contextmanager
def board_lock(root: Path) -> Iterator[None]:
    board_dir = root / BOARD_DIR_NAME
    board_dir.mkdir(parents=True, exist_ok=True)
    lock_dir = board_dir / ".lock"
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            lock_dir.mkdir()
            (lock_dir / "owner.json").write_text(
                json.dumps({"pid": os.getpid(), "created_at": utc_now()}),
                encoding="utf-8",
            )
            break
        except FileExistsError:
            try:
                age = time.time() - lock_dir.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > STALE_LOCK_SECONDS:
                shutil.rmtree(lock_dir, ignore_errors=True)
                continue
            if time.monotonic() >= deadline:
                raise BoardError(
                    f"Timed out waiting for board lock {lock_dir}. "
                    "If no other agent is updating the board, remove that directory and retry."
                )
            time.sleep(0.05)
    try:
        yield
    finally:
        shutil.rmtree(lock_dir, ignore_errors=True)


def validate_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "revision",
        "created_at",
        "updated_at",
        "project",
        "status",
        "phase",
        "current_focus",
        "next_action",
        "tasks",
        "decisions",
        "verifications",
        "changed_files",
        "blockers",
        "session",
    }
    for key in sorted(required - state.keys()):
        errors.append(f"missing required field: {key}")
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SCHEMA_VERSION}, got {state.get('schema_version')!r}"
        )
    if state.get("status") not in PROJECT_STATUSES:
        errors.append(f"invalid project status: {state.get('status')!r}")
    if not isinstance(state.get("revision"), int) or state.get("revision", 0) < 1:
        errors.append("revision must be a positive integer")
    for key in ("created_at", "updated_at", "phase", "current_focus", "next_action"):
        if not isinstance(state.get(key), str) or not state.get(key).strip():
            errors.append(f"{key} must be a non-empty string")
    project = state.get("project")
    if not isinstance(project, dict) or not all(
        isinstance(project.get(key), str) and project.get(key).strip()
        for key in ("name", "root", "objective")
    ):
        errors.append("project must contain non-empty name, root, and objective strings")
    tasks = state.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
    else:
        identifiers: set[str] = set()
        doing = 0
        for task in tasks:
            if not isinstance(task, dict):
                errors.append("each task must be an object")
                continue
            task_id = task.get("id")
            if not isinstance(task_id, str) or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id
            ):
                errors.append("each task id must use lowercase kebab-case")
            elif task_id in identifiers:
                errors.append(f"duplicate task id: {task_id}")
            else:
                identifiers.add(task_id)
            if not isinstance(task.get("title"), str) or not task.get("title").strip():
                errors.append(f"task {task_id!r} requires a non-empty title")
            if not isinstance(task.get("notes"), str):
                errors.append(f"task {task_id!r} notes must be a string")
            if task.get("status") not in TASK_STATUSES:
                errors.append(f"invalid task status for {task_id!r}: {task.get('status')!r}")
            if task.get("status") == "doing":
                doing += 1
        if doing > 1:
            errors.append("only one task may have status 'doing'")
    decisions = state.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
    else:
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict) or not all(
                isinstance(decision.get(key), str) and decision.get(key).strip()
                for key in ("at", "decision", "rationale")
            ):
                errors.append(
                    f"decision at index {index} requires non-empty at, decision, and rationale strings"
                )

    verifications = state.get("verifications")
    if not isinstance(verifications, list):
        errors.append("verifications must be a list")
    else:
        for index, verification in enumerate(verifications):
            if not isinstance(verification, dict) or not all(
                isinstance(verification.get(key), str) and verification.get(key).strip()
                for key in ("at", "command", "outcome")
            ):
                errors.append(
                    f"verification at index {index} requires non-empty at, command, and outcome strings"
                )

    changed_files = state.get("changed_files")
    if not isinstance(changed_files, list):
        errors.append("changed_files must be a list")
    else:
        seen_paths: set[str] = set()
        for value in changed_files:
            path = PurePosixPath(value) if isinstance(value, str) else None
            if (
                path is None
                or not value.strip()
                or not path.parts
                or path.is_absolute()
                or path.as_posix() != value
                or ".." in path.parts
                or path.parts[0] in {".git", BOARD_DIR_NAME}
            ):
                errors.append(f"invalid project-relative changed file: {value!r}")
            elif value in seen_paths:
                errors.append(f"duplicate changed file: {value}")
            else:
                seen_paths.add(value)

    blockers = state.get("blockers")
    if not isinstance(blockers, list):
        errors.append("blockers must be a list")
    elif any(
        not isinstance(blocker, str)
        or not blocker.strip()
        or blocker.strip().lower() in PLACEHOLDER_BLOCKERS
        for blocker in blockers
    ):
        errors.append("blockers must contain only real, non-empty descriptions")
    else:
        if state.get("status") == "blocked" and not blockers:
            errors.append("blocked project status requires at least one blocker")
        if state.get("status") == "complete" and blockers:
            errors.append("complete project status cannot retain active blockers")
    session = state.get("session")
    if not isinstance(session, dict):
        errors.append("session must be an object")
    else:
        if not isinstance(session.get("last_summary"), str) or not session.get(
            "last_summary"
        ).strip():
            errors.append("session.last_summary must be a non-empty string")
        if not isinstance(session.get("needs_checkpoint"), bool):
            errors.append("session.needs_checkpoint must be a boolean")
    return errors


def require_valid(state: dict[str, Any]) -> None:
    errors = validate_state(state)
    if errors:
        raise BoardError("Invalid board state:\n- " + "\n- ".join(errors))


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(state: dict[str, Any]) -> str:
    tasks = state["tasks"]
    task_lines = ["| ID | Task | Status | Notes |", "| --- | --- | --- | --- |"]
    if tasks:
        task_lines.extend(
            f"| `{markdown_cell(task['id'])}` | {markdown_cell(task['title'])} | "
            f"{markdown_cell(task['status'])} | {markdown_cell(task.get('notes', ''))} |"
            for task in tasks
        )
    else:
        task_lines.append("| — | No tasks recorded | — | — |")

    def bullets(items: list[Any], formatter: Callable[[Any], str]) -> list[str]:
        return [f"- {formatter(item)}" for item in items] or ["- None recorded"]

    lines = [
        "# Project Progress Board",
        "",
        "## Snapshot",
        "",
        f"- **Project:** {state['project']['name']}",
        f"- **Objective:** {state['project']['objective']}",
        f"- **Status:** {state['status']}",
        f"- **Phase:** {state['phase']}",
        f"- **Current focus:** {state['current_focus']}",
        f"- **Next action:** {state['next_action']}",
        f"- **Last summary:** {state['session']['last_summary']}",
        f"- **Revision:** {state['revision']}",
        "",
        "## Tasks",
        "",
        *task_lines,
        "",
        "## Changed files",
        "",
        *bullets(state["changed_files"], lambda item: f"`{item}`"),
        "",
        "## Verification",
        "",
        *bullets(
            state["verifications"],
            lambda item: f"`{item['command']}` — {item['outcome']} ({item['at']})",
        ),
        "",
        "## Decisions",
        "",
        *bullets(
            state["decisions"],
            lambda item: f"{item['decision']} — {item['rationale']} ({item['at']})",
        ),
        "",
        "## Blockers",
        "",
        *bullets(state["blockers"], str),
        "",
        "## Resume instructions",
        "",
        "Read this board, reconcile it with Git status and tests, then execute the next action.",
        "",
    ]
    return "\n".join(lines)


def create_state(root: Path, objective: str) -> dict[str, Any]:
    objective = objective.strip()
    if not objective:
        raise BoardError("objective must not be empty")
    now = utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": 1,
        "created_at": now,
        "updated_at": now,
        "project": {"name": root.name, "root": str(root), "objective": objective},
        "status": "active",
        "phase": "discovery",
        "current_focus": objective,
        "next_action": "Inspect the repository and define the first implementation task.",
        "tasks": [],
        "decisions": [],
        "verifications": [],
        "changed_files": [],
        "blockers": [],
        "session": {"last_summary": "Board initialized.", "needs_checkpoint": False},
    }


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def save_new_state(root: Path, state: dict[str, Any], event_type: str) -> None:
    require_valid(state)
    state_path, board_path, events_path = board_paths(root)
    write_state(state_path, state)
    atomic_write_text(board_path, render_markdown(state))
    append_event(
        events_path,
        {"at": state["updated_at"], "revision": state["revision"], "type": event_type},
    )


def mutate_state(
    root: Path,
    event_type: str,
    mutator: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    state_path, _, _ = board_paths(root)
    with board_lock(root):
        if not state_path.exists():
            raise BoardError("No project board exists. Run `ensure --objective <goal>` first.")
        state = load_state(state_path)
        require_valid(state)
        mutator(state)
        state["revision"] += 1
        state["updated_at"] = utc_now()
        save_new_state(root, state, event_type)
        return state


def command_ensure(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    state_path, _, _ = board_paths(root)
    with board_lock(root):
        if state_path.exists():
            state = load_state(state_path)
            require_valid(state)
            if args.objective and args.objective.strip() != state["project"]["objective"]:
                state["project"]["objective"] = args.objective.strip()
                state["current_focus"] = args.objective.strip()
                state["revision"] += 1
                state["updated_at"] = utc_now()
                save_new_state(root, state, "objective_updated")
        else:
            state = create_state(root, args.objective)
            save_new_state(root, state, "initialized")
    print(render_markdown(state), end="")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    state_path, _, _ = board_paths(root)
    if not state_path.exists():
        raise BoardError("No project board exists. Run `ensure --objective <goal>` first.")
    state = load_state(state_path)
    require_valid(state)
    print(render_markdown(state), end="")
    return 0


def command_task_add(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)

    def add(state: dict[str, Any]) -> None:
        if any(task["id"] == args.id for task in state["tasks"]):
            raise BoardError(f"Task id already exists: {args.id}")
        if args.status == "doing" and any(task["status"] == "doing" for task in state["tasks"]):
            raise BoardError("Only one task may have status 'doing'.")
        state["tasks"].append(
            {"id": args.id, "title": args.title, "status": args.status, "notes": args.notes or ""}
        )

    state = mutate_state(root, "task_added", add)
    print(render_markdown(state), end="")
    return 0


def command_task_update(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)

    def update(state: dict[str, Any]) -> None:
        task = next((item for item in state["tasks"] if item["id"] == args.id), None)
        if task is None:
            raise BoardError(f"Unknown task id: {args.id}")
        if args.status == "doing" and any(
            item["id"] != args.id and item["status"] == "doing" for item in state["tasks"]
        ):
            raise BoardError("Only one task may have status 'doing'.")
        if args.status is not None:
            task["status"] = args.status
        if args.notes is not None:
            task["notes"] = args.notes

    state = mutate_state(root, "task_updated", update)
    print(render_markdown(state), end="")
    return 0


def normalize_changed_path(root: Path, value: str) -> str:
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise BoardError(f"Changed file is outside the project root: {resolved}") from exc
    if not relative.parts or relative.parts[0] in {".git", BOARD_DIR_NAME}:
        raise BoardError(f"Changed file is not project source: {relative}")
    return relative.as_posix()


def command_record_file(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    relative = normalize_changed_path(root, args.path)

    def record(state: dict[str, Any]) -> None:
        if relative not in state["changed_files"]:
            state["changed_files"].append(relative)
        state["session"]["needs_checkpoint"] = True

    state = mutate_state(root, "file_recorded", record)
    print(relative)
    return 0


def parse_pair(value: str, label: str) -> tuple[str, str]:
    if "::" not in value:
        raise BoardError(f"{label} must use 'left::right' format")
    left, right = (part.strip() for part in value.rsplit("::", 1))
    if not left or not right:
        raise BoardError(f"{label} must contain non-empty values on both sides of '::'")
    return left, right


def command_checkpoint(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    for label, value in (
        ("summary", args.summary),
        ("focus", args.focus),
        ("next action", args.next),
    ):
        if not value.strip():
            raise BoardError(f"checkpoint requires a non-empty {label}")
    if any(blocker.strip().lower() in PLACEHOLDER_BLOCKERS for blocker in args.blocker):
        raise BoardError("omit --blocker when no real blocker exists")

    def checkpoint(state: dict[str, Any]) -> None:
        state["session"]["last_summary"] = args.summary.strip()
        state["session"]["needs_checkpoint"] = False
        state["current_focus"] = args.focus.strip()
        state["next_action"] = args.next.strip()
        state["status"] = args.status
        if args.clear_blockers:
            state["blockers"] = []
        if args.phase:
            state["phase"] = args.phase.strip()
        for value in args.verification:
            command, outcome = parse_pair(value, "verification")
            state["verifications"].append(
                {"at": utc_now(), "command": command, "outcome": outcome}
            )
        for value in args.decision:
            decision, rationale = parse_pair(value, "decision")
            state["decisions"].append(
                {"at": utc_now(), "decision": decision, "rationale": rationale}
            )
        for blocker in args.blocker:
            blocker = blocker.strip()
            if blocker and blocker not in state["blockers"]:
                state["blockers"].append(blocker)

    state = mutate_state(root, "checkpointed", checkpoint)
    print(render_markdown(state), end="")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    state_path, _, _ = board_paths(root)
    if not state_path.exists():
        raise BoardError("No project board exists.")
    state = load_state(state_path)
    require_valid(state)
    print(f"OK: {state_path} (revision {state['revision']})")
    return 0


def command_render(args: argparse.Namespace) -> int:
    root = resolve_project_root(args.project_root)
    state_path, board_path, _ = board_paths(root)
    state = load_state(state_path)
    require_valid(state)
    atomic_write_text(board_path, render_markdown(state))
    print(board_path)
    return 0


def add_project_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", help="Target project root; defaults to nearest Git root")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure = subparsers.add_parser("ensure", help="Create the board if it is missing")
    ensure.add_argument("--objective", required=True)
    add_project_root(ensure)
    ensure.set_defaults(handler=command_ensure)

    resume = subparsers.add_parser("resume", help="Print a compact recovery packet")
    add_project_root(resume)
    resume.set_defaults(handler=command_resume)

    task_add = subparsers.add_parser("task-add", help="Add a board task")
    task_add.add_argument("--id", required=True)
    task_add.add_argument("--title", required=True)
    task_add.add_argument("--status", choices=sorted(TASK_STATUSES), default="todo")
    task_add.add_argument("--notes")
    add_project_root(task_add)
    task_add.set_defaults(handler=command_task_add)

    task_update = subparsers.add_parser("task-update", help="Update a board task")
    task_update.add_argument("--id", required=True)
    task_update.add_argument("--status", choices=sorted(TASK_STATUSES))
    task_update.add_argument("--notes")
    add_project_root(task_update)
    task_update.set_defaults(handler=command_task_update)

    record_file = subparsers.add_parser("record-file", help="Record a changed project file")
    record_file.add_argument("--path", required=True)
    add_project_root(record_file)
    record_file.set_defaults(handler=command_record_file)

    checkpoint = subparsers.add_parser("checkpoint", help="Save a recovery checkpoint")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--focus", required=True)
    checkpoint.add_argument("--next", required=True)
    checkpoint.add_argument("--status", choices=sorted(PROJECT_STATUSES), default="active")
    checkpoint.add_argument("--phase")
    checkpoint.add_argument("--verification", action="append", default=[])
    checkpoint.add_argument("--decision", action="append", default=[])
    checkpoint.add_argument("--blocker", action="append", default=[])
    checkpoint.add_argument(
        "--clear-blockers",
        action="store_true",
        help="Remove resolved blockers before adding any new --blocker values",
    )
    add_project_root(checkpoint)
    checkpoint.set_defaults(handler=command_checkpoint)

    validate = subparsers.add_parser("validate", help="Validate board state")
    add_project_root(validate)
    validate.set_defaults(handler=command_validate)

    render = subparsers.add_parser("render", help="Regenerate board.md")
    add_project_root(render)
    render.set_defaults(handler=command_render)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.handler(args)
    except BoardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
