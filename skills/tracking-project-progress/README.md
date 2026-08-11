# Tracking Project Progress

English | [简体中文](README_CN.md)

A portable Agent Skill and Claude Code plugin that gives coding agents a durable, project-local progress board. It is designed for the awkward moment when a long implementation is interrupted and a fresh model has to rediscover what happened.

The board captures only continuation-critical state: objective, current focus, task status, decisions, changed files, verification evidence, blockers, and one concrete next action.

## Why this exists

Conversation history is a poor project database. It may be compacted, split across sessions, or unavailable to the next agent. Git preserves code changes, but it does not explain which requirement is active, what remains unverified, or why a technical choice was made.

This project adds a small recovery layer without replacing Git, issues, or implementation plans.

## Features

- Portable [Agent Skills](https://agentskills.io/specification) package
- Automatic discovery from coding, bug-fix, refactor, migration, resume, and handoff requests
- Tested Python-standard-library board CLI
- Human-readable Markdown board backed by machine-readable JSON
- Atomic, lock-protected, revisioned state updates
- Append-only event history
- Claude Code lifecycle hooks:
  - inject existing board context on session start;
  - initialize and record the board after successful source edits;
  - require a checkpoint before a code-changing turn stops
- No network calls, telemetry, hosted service, or runtime dependency installation

## Board files

The Skill creates these files in the target repository:

```text
.project-board/
├── state.json    # machine-readable source of truth
├── board.md      # human-readable rendered board
└── events.jsonl  # append-only revision audit trail
```

Teams may commit this directory when shared continuity is valuable, or add it to their own `.gitignore` when the board is local working state.

## Install

### Agent Skills clients

Install the portable Skill with the community `skills` installer:

```bash
npx skills add https://github.com/Byctor/tracking-project-progress --skill tracking-project-progress
```

Choose the desired supported agent and user- or project-level scope when prompted.

### Claude Code plugin marketplace

Run these commands inside Claude Code:

```text
/plugin marketplace add Byctor/tracking-project-progress
/plugin install tracking-project-progress@tracking-project-progress
```

Restart or run `/reload-plugins` after updating hook files.

### Claude Code development checkout

```bash
git clone https://github.com/Byctor/tracking-project-progress.git
claude --plugin-dir ./tracking-project-progress
```

The installed skill is available as `/tracking-project-progress:tracking-project-progress`; Claude may also load it automatically when its description matches the coding task.

## Usage

Ask the agent to start or resume a non-trivial coding task. The Skill will resolve its bundled CLI and follow this lifecycle:

1. resume the existing board or initialize one from the real user objective;
2. reconcile the board with Git status, diffs, and focused tests;
3. keep one small task in progress;
4. record meaningful changed files and exact verification outcomes;
5. checkpoint a factual summary and one executable next action.

Manual invocation is also supported:

```text
Use tracking-project-progress to resume this repository and continue the current implementation.
```

## CLI

The Skill tells the agent to run the bundled utility; maintainers can run it directly:

```bash
python3 skills/tracking-project-progress/scripts/project_board.py --help
```

Core commands:

| Command | Purpose |
| --- | --- |
| `ensure` | Create a board or refine its objective |
| `resume` | Print a compact recovery packet |
| `task-add` | Add a task with a stable ID |
| `task-update` | Change task status or notes |
| `record-file` | Record a changed file and require checkpointing |
| `checkpoint` | Save summary, focus, next action, evidence, and decisions |
| `validate` | Verify schema and invariants |
| `render` | Regenerate `board.md` from `state.json` |

Example:

```bash
CLI="skills/tracking-project-progress/scripts/project_board.py"

python3 "$CLI" ensure \
  --objective "Add token refresh with regression coverage" \
  --project-root "$PWD"

python3 "$CLI" checkpoint \
  --summary "Refresh parser implemented; focused tests pass" \
  --focus "Authentication regression coverage" \
  --next "Run the complete authentication test suite" \
  --verification "python3 -m unittest tests.test_refresh::pass (4 tests)" \
  --project-root "$PWD"
```

## Portability

The core follows the open Agent Skills directory format and uses only Python's standard library. Claude Code hooks are an optional adapter; agents without lifecycle hooks follow the same start, work, verification, and checkpoint rules from `SKILL.md`.

See Anthropic's [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), and [Claude Code plugin guide](https://code.claude.com/docs/en/plugins) for the platform concepts used here.

## Safety and privacy

- The project makes no network requests and sends no telemetry.
- The board stores paths, summaries, decisions, and test commands in the target repository. Do not put secrets or credentials in checkpoint text.
- Corrupt or unsupported state is preserved instead of overwritten.
- The Skill does not grant permission to commit, push, open issues, or contact external services.
- Review third-party Skills like software before installing them; Skill instructions and scripts execute with the agent's available permissions.

## Limitations

- Portable Agent Skills cannot guarantee lifecycle execution. The Claude Code plugin hooks provide stronger automatic behavior.
- Version 0.1 has no hosted UI, GitHub Projects synchronization, or IDE panel.
- One board is maintained per Git worktree.
- Concurrent updates are serialized locally; semantic merging across separate machines is outside this release.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts skills/tracking-project-progress/scripts
uvx --python 3.11 --from skills-ref agentskills validate skills/tracking-project-progress
claude plugin validate . --strict
```

Behavioral evaluation prompts and preserved baseline results live in [`evals/`](evals/).

## License

Apache-2.0. See [`LICENSE`](LICENSE).
