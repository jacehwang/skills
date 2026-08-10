---
name: tracking-project-progress
description: Maintains a durable project board for coding work with objectives, tasks, decisions, changed files, verification, blockers, and next actions. Use when agents start, continue, resume, or hand off non-trivial software development such as feature implementation, bug fixes, refactors, migrations, multi-file changes, or interrupted work.
---

# Tracking Project Progress

## Core rule

Use `.project-board/` as the concise recovery layer for the coding objective. Resume it before substantive work and checkpoint it after meaningful changes, before handoff, and before ending a code-changing session.

The board complements Git history, issues, and implementation plans. Do not duplicate their full content.

## Set up the command

Resolve `SKILL_DIR` to the directory containing this `SKILL.md`, then use:

```bash
BOARD_CLI="$SKILL_DIR/scripts/project_board.py"
```

Run `python3 "$BOARD_CLI" --help` for the complete command list. The utility uses only the Python standard library.

## Start or resume

1. Try to resume before reading broad project history:

   ```bash
   python3 "$BOARD_CLI" resume --project-root "$PWD"
   ```

2. If no board exists, initialize it with the user's actual objective:

   ```bash
   python3 "$BOARD_CLI" ensure \
     --objective "Implement token refresh with regression coverage" \
     --project-root "$PWD"
   ```

3. Reconcile the board with the current request, `git status`, relevant diffs, and focused tests. Repository evidence overrides stale board text. Use `ensure --objective` again to correct an outdated objective.

4. If state JSON is corrupt or uses an unsupported schema, preserve it and report the recovery blocker. Do not replace it manually.

## Plan the current work

Represent implementation as small tasks with stable kebab-case IDs. Keep no more than one task in `doing`.

Track repository outcomes, not the agent's ceremony. Tasks should describe code, tests, migrations, review findings, or verification that materially advances the objective. Do not copy procedural steps such as “brainstorm,” “ask for approval,” “write a plan,” “self-review,” or “update the board” into the task list.

When an unspecified detail has a conventional, reversible, low-risk default and the user has asked work to begin, record the assumption as a decision and continue. Pause for clarification only when the choice would materially change a public interface, persistent data, security posture, cost, or the user's stated outcome.

```bash
python3 "$BOARD_CLI" task-add \
  --id refresh-tests \
  --title "Add failing refresh regression tests" \
  --status doing \
  --project-root "$PWD"

python3 "$BOARD_CLI" task-update \
  --id refresh-tests \
  --status done \
  --notes "Focused regression test passes" \
  --project-root "$PWD"
```

Do not mark planned work done from intent, generated code, or another agent's claim. Require repository or test evidence.

## Keep the board current

After each meaningful source, test, configuration, or migration change, record the path:

```bash
python3 "$BOARD_CLI" record-file \
  --path "src/auth/refresh.py" \
  --project-root "$PWD"
```

Claude Code hooks may record changed files automatically. Other runtimes must call `record-file` explicitly.

Capture only decisions that constrain later work. Preserve exact verification commands and observed outcomes; never translate “not run” into “pass.”

## Checkpoint

Checkpoint after a milestone, before switching agents, before an expected interruption, and before ending any session that changed code:

```bash
python3 "$BOARD_CLI" checkpoint \
  --summary "Implemented refresh parsing; focused regression passes" \
  --focus "Token refresh regression coverage" \
  --next "Run the complete authentication test suite" \
  --status active \
  --verification "python3 -m unittest tests.test_refresh::pass (4 tests)" \
  --decision "Keep cache writes atomic::An interruption must not leave partial state" \
  --project-root "$PWD"
```

Use repeated `--verification`, `--decision`, or `--blocker` flags when needed. Pair values use `left::right`; see [the board schema](references/board-schema.md).

Record only real, active blockers. Omit `--blocker` when none exist, and pass `--clear-blockers` once resolved. A `blocked` checkpoint requires at least one blocker; a `complete` checkpoint cannot retain blockers.

A valid checkpoint contains:

- a factual summary of completed and incomplete work;
- the current focus;
- one concrete, executable next action;
- exact verification performed and its result;
- unresolved blockers and consequential decisions.

## Completion and handoff

Set `--status complete` only after fresh evidence verifies the user's full objective. A passing focused test is not proof that an entire project task is complete.

Before handoff:

1. Run `validate`.
2. Confirm `.project-board/board.md` matches the latest state.
3. Tell the user the current status and next action without pasting the full board.

```bash
python3 "$BOARD_CLI" validate --project-root "$PWD"
```

If broader verification remains, keep status `active` or `blocked`, record what was not run, and make that verification the next action.

## Safety

- Never edit `state.json`, `board.md`, or `events.jsonl` by hand.
- Never record paths outside the project root.
- Never use this Skill as authorization to commit, push, open issues, or contact external services.
- Preserve unrelated user changes and existing project management artifacts.
- Keep summaries short enough for a fresh agent to scan before coding.
