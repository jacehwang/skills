# Tracking Project Progress — Design

## Product goal

Create an open-source Agent Skill that gives coding agents a durable, project-local progress board. The board must let a fresh session recover the project's objective, current focus, completed work, decisions, verification evidence, changed files, blockers, and next action without reconstructing the entire history.

The repository is both:

1. a portable Agent Skills package named `tracking-project-progress`; and
2. a Claude Code plugin that adds lifecycle hooks for automatic initialization, changed-file capture, session resume context, and checkpoint enforcement.

## Scope

Version 0.1 covers non-trivial coding work: new features, bug fixes, refactors, migrations, and multi-step project maintenance. It does not replace issue trackers, Git history, or implementation plans. It stores only concise coordination state needed to continue work reliably.

## Design principles

- **Project-local truth:** write state to `.project-board/` inside the target repository.
- **Portable core:** the Skill and its Python utility use only the Agent Skills open format and Python standard library.
- **Deterministic mutations:** agents call a tested CLI instead of editing state JSON by hand.
- **Human-readable output:** `board.md` is regenerated after every mutation.
- **Machine-readable source:** `state.json` is the source of truth; `events.jsonl` is an append-only audit trail.
- **Resume first:** an existing board is read before planning or editing code.
- **Checkpoint before stop:** code-changing sessions record a summary, verification, and one concrete next action.
- **Graceful portability:** lifecycle hooks strengthen Claude Code behavior; other agents follow the same lifecycle from `SKILL.md`.

## Repository layout

```text
tracking-project-progress/
├── .claude-plugin/plugin.json
├── .github/workflows/ci.yml
├── docs/superpowers/
│   ├── specs/
│   └── plans/
├── evals/
│   ├── scenarios.md
│   ├── baseline/
│   └── skill-enabled/
├── hooks/hooks.json
├── scripts/
│   ├── hook_session_start.py
│   ├── hook_post_tool.py
│   └── hook_stop.py
├── skills/tracking-project-progress/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/board-schema.md
│   └── scripts/project_board.py
├── tests/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

Human-facing open-source documentation remains at repository root. The Skill directory contains only agent-facing instructions and resources.

## Board model

`.project-board/state.json` contains:

- `schema_version`, `revision`, `created_at`, `updated_at`
- `project`: name, canonical root, objective
- `status`: `active`, `blocked`, or `complete`
- `phase`, `current_focus`, and `next_action`
- `tasks`: stable ID, title, status, optional notes
- `decisions`: timestamp, decision, rationale
- `verifications`: timestamp, command, outcome
- `changed_files`: normalized project-relative paths
- `blockers`: active blocker descriptions
- `session`: last summary and whether a checkpoint is required

Every mutation acquires an atomic directory lock, writes a temporary file, calls `os.replace`, increments `revision`, regenerates `board.md`, and appends an event to `events.jsonl`. Paths outside the project root are rejected.

## CLI contract

The bundled `project_board.py` exposes:

- `ensure`: create the board if missing and optionally refine its objective.
- `resume`: print a compact recovery packet for an agent.
- `task-add`: add a uniquely identified task.
- `task-update`: change task status or notes.
- `record-file`: record a changed project-relative file and mark the session dirty.
- `checkpoint`: save the latest summary, focus, next action, status, decisions, blockers, and verification evidence; clear the dirty marker.
- `validate`: verify schema, enum values, unique task IDs, paths, and required resume fields.
- `render`: regenerate `board.md` from `state.json`.

All commands accept `--project-root`; otherwise they resolve the nearest Git root and fall back to the current directory.

## Skill lifecycle

1. **Start or resume:** run `resume`. If no board exists, run `ensure` using the user's coding objective.
2. **Orient:** compare board state with Git status and the current request. Correct stale focus or tasks before editing.
3. **Plan:** create or update small tasks with exactly one task in `doing` unless work is intentionally blocked.
4. **Work:** after meaningful code changes, record changed files; after tests, record exact commands and outcomes.
5. **Checkpoint:** after a milestone, before handoff, and before ending a code-changing session, save a concise summary and one executable next action.
6. **Complete:** mark the board complete only when the user-requested objective is verified, not merely when a local subtask passes.

## Claude Code adapter

The plugin adds three hooks:

- `SessionStart`: if a board exists, print its resume packet into Claude's context; otherwise print a short instruction to activate the Skill for coding work.
- `PostToolUse` for `Write|Edit`: when the affected path looks like source, test, configuration, or migration code, call `record-file`. The first matching edit automatically initializes the board if necessary.
- `Stop`: if a code edit marked the session dirty and no checkpoint followed, exit with code 2 and give Claude a precise checkpoint instruction. A successful checkpoint clears the condition, allowing the session to stop.

Hooks never make network calls, never inspect files outside the project root, and do not create a board for read-only sessions.

## Error handling and safety

- Corrupt JSON is never overwritten; commands fail with a recovery-oriented error.
- Unsupported schema versions fail closed.
- Lock acquisition times out with the lock path and remediation advice.
- All writes are atomic and UTF-8.
- Hook failures report concise diagnostics but do not expose file contents.
- The Skill must not commit, push, open issues, or contact external services unless another explicitly invoked workflow authorizes it.

## Testing strategy

### Skill evaluations

Run at least three fresh-context scenarios without the Skill and preserve outputs as the RED baseline. Repeat them with the Skill installed and compare:

1. starting a multi-file feature from an empty repository;
2. resuming after interruption from existing code and partial notes;
3. attempting to finish after code edits without recording verification or a next action.

Success means the Skill-enabled agent creates or resumes the board before code work, keeps state concise, records evidence, and leaves a specific next action.

### Automated tests

- CLI unit tests cover creation, resume, task transitions, checkpoints, validation, path safety, event logging, and atomic revision updates.
- Hook tests feed representative JSON on stdin and assert context injection, automatic file capture, and Stop enforcement.
- Structure tests validate Agent Skills frontmatter, internal references, plugin JSON, hook configuration, executable syntax, and line-count limits.
- CI runs on Python 3.11 and 3.13, then validates the Skill with `skills-ref`.

## Distribution and maintenance

- License: Apache-2.0.
- Releases use semantic versioning beginning at `0.1.0`.
- GitHub Actions run tests and standards validation for pushes and pull requests.
- Installation paths documented in README:
  - Agent Skills clients: `npx skills add <repository-url> --skill tracking-project-progress`
  - Claude Code development: `claude --plugin-dir <repository-path>`
  - Claude Code marketplace installation after a marketplace release.
- Contributions require tests for behavioral changes and an evaluation when Skill instructions change.

## Non-goals for version 0.1

- Hosted dashboards or databases
- Automatic GitHub Issues/Projects synchronization
- IDE graphical panels
- Semantic reconstruction of old conversations
- Network services or telemetry
- Multiple boards per Git worktree

These can be added later without changing the project-local board contract.
