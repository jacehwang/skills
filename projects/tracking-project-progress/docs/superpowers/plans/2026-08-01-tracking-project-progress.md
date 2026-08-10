# Tracking Project Progress Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a portable Agent Skill plus Claude Code plugin that automatically creates, resumes, updates, and checkpoints a project-local development progress board.

**Architecture:** A Python-standard-library CLI owns `.project-board/state.json`, renders `board.md`, and appends `events.jsonl`. The portable Skill teaches the lifecycle; Claude Code hooks call the same CLI at session start, after code edits, and before stop.

**Tech Stack:** Agent Skills `SKILL.md`, Python 3.11+, `unittest`, Claude Code plugin JSON/hooks, GitHub Actions, `skills-ref` validation.

## Global Constraints

- Skill name and directory are exactly `tracking-project-progress`.
- The Skill conforms to the Agent Skills specification and keeps `SKILL.md` below 500 lines.
- Runtime scripts use only the Python standard library and make no network calls.
- Board state lives only under `<project-root>/.project-board/`.
- State mutations are lock-protected, atomic, revisioned, and auditable.
- A code-changing session cannot stop in the Claude Code adapter while its checkpoint flag is dirty.
- Human-facing repository documentation stays outside the Skill directory.
- Apache-2.0 license and semantic version `0.1.0` are used for the first release.

---

### Task 1: Record failing skill baselines

**Files:**
- Create: `evals/scenarios.md`
- Create: `evals/baseline/scenario-1.md`
- Create: `evals/baseline/scenario-2.md`
- Create: `evals/baseline/scenario-3.md`

**Interfaces:**
- Consumes: fresh agent contexts without this Skill.
- Produces: three preserved outputs and a failure analysis that later Skill evaluations must improve.

- [ ] **Step 1: Write three behavior scenarios**

Define exact prompts for feature start, interrupted-session resume, and attempted stop after uncheckpointed edits. Each rubric requires board creation/resume, concise state, verification evidence, and a concrete next action.

- [ ] **Step 2: Run each prompt without the Skill**

Use fresh agent contexts. Do not mention the intended Skill, file names, or expected implementation.

- [ ] **Step 3: Save outputs verbatim**

Store each response with `result: fail` and list only observable missing behaviors.

- [ ] **Step 4: Commit the RED evidence**

```bash
git add evals
git commit -m "test: capture project-board baseline failures"
```

### Task 2: Implement the board CLI with TDD

**Files:**
- Create: `tests/test_project_board.py`
- Create: `skills/tracking-project-progress/scripts/project_board.py`
- Create: `skills/tracking-project-progress/references/board-schema.md`

**Interfaces:**
- Consumes: `--project-root` plus CLI subcommand arguments.
- Produces: `ensure`, `resume`, `task-add`, `task-update`, `record-file`, `checkpoint`, `validate`, and `render` commands; exit code 0 on success and 2 on user-correctable validation failure.

- [ ] **Step 1: Write failing creation and resume tests**

```python
def test_ensure_creates_resumeable_board(self):
    result = run_cli(self.root, "ensure", "--objective", "Add token refresh")
    self.assertEqual(result.returncode, 0, result.stderr)
    state = load_state(self.root)
    self.assertEqual(state["project"]["objective"], "Add token refresh")
    self.assertIn("Add token refresh", run_cli(self.root, "resume").stdout)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_project_board.ProjectBoardTests.test_ensure_creates_resumeable_board -v`

Expected: FAIL because `project_board.py` does not exist.

- [ ] **Step 3: Implement root resolution, default state, atomic writes, event append, and Markdown rendering**

Use `Path.resolve()`, `.project-board/.lock`, `tempfile.NamedTemporaryFile`, `os.replace`, UTC ISO-8601 timestamps, and deterministic JSON formatting.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest tests.test_project_board.ProjectBoardTests.test_ensure_creates_resumeable_board -v`

Expected: PASS.

- [ ] **Step 5: Write failing task, changed-file, and checkpoint tests**

```python
def test_record_file_marks_dirty_and_checkpoint_clears_it(self):
    run_cli(self.root, "ensure", "--objective", "Add token refresh")
    run_cli(self.root, "record-file", "--path", "src/auth.py")
    self.assertTrue(load_state(self.root)["session"]["needs_checkpoint"])
    run_cli(
        self.root,
        "checkpoint",
        "--summary", "Implemented refresh parsing",
        "--focus", "Token refresh",
        "--next", "Add expiry tests",
        "--verification", "python -m unittest:pass",
    )
    state = load_state(self.root)
    self.assertFalse(state["session"]["needs_checkpoint"])
    self.assertEqual(state["next_action"], "Add expiry tests")
```

- [ ] **Step 6: Verify RED, implement minimal mutations, then verify GREEN**

Run the named test before and after implementation. Reject absolute paths and `..` traversal; de-duplicate changed files and task IDs.

- [ ] **Step 7: Write failing validation and corruption-safety tests**

Cover unsupported schema versions, corrupt JSON preservation, invalid enums, duplicate task IDs, and empty next actions during checkpoint.

- [ ] **Step 8: Implement validation and lock timeout behavior, then run the full file**

Run: `python3 -m unittest tests.test_project_board -v`

Expected: all tests pass with no warnings.

- [ ] **Step 9: Commit the CLI**

```bash
git add tests/test_project_board.py skills/tracking-project-progress/scripts/project_board.py skills/tracking-project-progress/references/board-schema.md
git commit -m "feat: add durable project board CLI"
```

### Task 3: Implement Claude Code hooks with TDD

**Files:**
- Create: `tests/test_hooks.py`
- Create: `scripts/hook_session_start.py`
- Create: `scripts/hook_post_tool.py`
- Create: `scripts/hook_stop.py`
- Create: `hooks/hooks.json`

**Interfaces:**
- Consumes: Claude Code hook JSON on stdin and `CLAUDE_PROJECT_DIR` or `cwd`.
- Produces: resume context on stdout, deterministic changed-file capture, and Stop exit code 2 only when `needs_checkpoint` is true.

- [ ] **Step 1: Write failing hook tests**

```python
def test_post_tool_initializes_and_tracks_code_file(self):
    payload = {"cwd": str(self.root), "tool_input": {"file_path": str(self.root / "src/app.py")}}
    result = run_hook("hook_post_tool.py", payload)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("src/app.py", load_state(self.root)["changed_files"])

def test_stop_blocks_dirty_board(self):
    make_dirty_board(self.root)
    result = run_hook("hook_stop.py", {"cwd": str(self.root)})
    self.assertEqual(result.returncode, 2)
    self.assertIn("checkpoint", result.stderr.lower())
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_hooks -v`

Expected: FAIL because hook scripts do not exist.

- [ ] **Step 3: Implement minimal hook adapters**

Use subprocess calls to the bundled CLI. Filter generated files, `.git/`, `.project-board/`, documentation-only extensions, and paths outside the project root.

- [ ] **Step 4: Add hook configuration**

Configure `SessionStart`, `PostToolUse` with matcher `Write|Edit`, and `Stop` using `${CLAUDE_PLUGIN_ROOT}` paths.

- [ ] **Step 5: Verify GREEN and commit**

Run: `python3 -m unittest tests.test_hooks -v`

```bash
git add tests/test_hooks.py scripts hooks
git commit -m "feat: automate project board lifecycle in Claude Code"
```

### Task 4: Author and validate the Agent Skill

**Files:**
- Create: `skills/tracking-project-progress/SKILL.md`
- Create: `skills/tracking-project-progress/agents/openai.yaml`
- Create: `tests/test_skill_structure.py`

**Interfaces:**
- Consumes: coding requests involving feature implementation, bug fixes, refactors, migrations, handoffs, or interrupted work.
- Produces: a consistent start-or-resume, orient, plan, work, verify, and checkpoint lifecycle using the bundled CLI.

- [ ] **Step 1: Scaffold the Skill with the official local skill initializer**

Run `init_skill.py tracking-project-progress` against a temporary directory, then move only the generated required metadata files into the existing Skill directory without overwriting tested resources.

- [ ] **Step 2: Write failing structure tests**

Assert exact directory/name match, required discovery keywords, under-500-line body, existing relative references, executable CLI syntax, and no human-facing README inside the Skill.

- [ ] **Step 3: Verify RED**

Run: `python3 -m unittest tests.test_skill_structure -v`

Expected: FAIL because `SKILL.md` and agent metadata are missing.

- [ ] **Step 4: Write the minimal Skill instructions**

The description names both behavior and triggers. The body includes the lifecycle, exact command examples, state rules, completion rule, hook portability note, and common recovery cases. Detailed schema stays in `references/board-schema.md`.

- [ ] **Step 5: Generate Codex UI metadata and verify GREEN**

Run the local `generate_openai_yaml.py` with display name `Project Progress Board`, a concise short description, and a default prompt that asks to resume and maintain the current project's board.

Run:

```bash
python3 -m unittest tests.test_skill_structure -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/tracking-project-progress
```

- [ ] **Step 6: Commit the Skill**

```bash
git add skills/tracking-project-progress/SKILL.md skills/tracking-project-progress/agents tests/test_skill_structure.py
git commit -m "feat: add tracking project progress skill"
```

### Task 5: Package the open-source plugin and repository

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.github/workflows/ci.yml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `LICENSE`
- Create: `CHANGELOG.md`
- Create: `tests/test_repository_metadata.py`

**Interfaces:**
- Consumes: repository clone or GitHub URL.
- Produces: local plugin loading, Agent Skills installation, repeatable CI, contribution guidance, and release metadata.

- [ ] **Step 1: Write failing repository metadata tests**

Validate plugin name/version, hook file existence, Apache license marker, CI test command, install commands, and absence of unresolved placeholder tokens.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_repository_metadata -v`

- [ ] **Step 3: Add manifest, docs, license, changelog, and CI**

Document portable installation with `npx skills add`, Claude Code development with `--plugin-dir`, board file behavior, privacy, limitations, commands, and contribution tests.

- [ ] **Step 4: Verify GREEN and full local suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts skills/tracking-project-progress/scripts
git diff --check
```

- [ ] **Step 5: Commit packaging**

```bash
git add .claude-plugin .github .gitignore README.md CONTRIBUTING.md SECURITY.md LICENSE CHANGELOG.md tests/test_repository_metadata.py
git commit -m "docs: package project progress board for open source"
```

### Task 6: Forward-test the Skill and close observed gaps

**Files:**
- Create: `evals/skill-enabled/scenario-1.md`
- Create: `evals/skill-enabled/scenario-2.md`
- Create: `evals/skill-enabled/scenario-3.md`
- Modify if required: `skills/tracking-project-progress/SKILL.md`
- Modify if required: relevant tests and scripts

**Interfaces:**
- Consumes: the three baseline prompts in fresh contexts with the Skill explicitly available.
- Produces: comparable outputs demonstrating each rubric item and regression tests for every discovered gap.

- [ ] **Step 1: Run all scenarios with the Skill**

Use fresh contexts and provide the Skill path without revealing expected answers or baseline diagnoses.

- [ ] **Step 2: Save outputs and score observable behavior**

Require creation/resume before code work, concise state, exact verification commands, and a concrete next action.

- [ ] **Step 3: For each failure, write a reproducing test before changing instructions or code**

Run the test to confirm failure, implement the smallest correction, then rerun the scenario.

- [ ] **Step 4: Commit evaluation evidence**

```bash
git add evals skills tests scripts
git commit -m "test: verify project progress skill behavior"
```

### Task 7: Final audit and GitHub release

**Files:**
- Modify: `README.md` with final repository URL and install commands.
- Modify: `CHANGELOG.md` only if release notes changed during validation.

**Interfaces:**
- Consumes: authenticated GitHub CLI and a clean, fully verified local repository.
- Produces: public GitHub repository, pushed `main`, and `v0.1.0` release.

- [ ] **Step 1: Run the completion audit**

Map every design requirement to a test, file, hook configuration, evaluation result, or command output. Treat missing evidence as incomplete work.

- [ ] **Step 2: Run fresh release verification**

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts skills/tracking-project-progress/scripts
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/tracking-project-progress
agentskills validate skills/tracking-project-progress
git diff --check
git status --short
```

- [ ] **Step 3: Create the public repository and add the remote**

Use the authenticated GitHub account, repository name `tracking-project-progress`, public visibility, Apache-2.0 metadata, and the existing local source without auto-generated files.

- [ ] **Step 4: Replace the README repository URL, commit, and push**

```bash
git add README.md
git commit -m "docs: add public repository links"
git push -u origin main
```

- [ ] **Step 5: Tag and publish version 0.1.0**

```bash
git tag -a v0.1.0 -m "tracking-project-progress v0.1.0"
git push origin v0.1.0
```

Create GitHub release notes from `CHANGELOG.md` and confirm the release page and clone/install commands resolve.
