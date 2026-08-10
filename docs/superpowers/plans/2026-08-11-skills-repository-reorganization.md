# Skills Repository Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a non-fork `JaceHwang/Skills` monorepo containing exactly four validated Skill packages, preserve both standalone source histories, and remove the obsolete fork and migrated source repositories.

**Architecture:** Work on `codex/reorganize-skills-repository` from the current `JaceHwang/codex-skills` default branch. Attach `daily-news-briefing` history with a subtree merge, normalize all retained packages beneath `skills/`, validate locally, merge through a pull request, and only then perform the ordered GitHub rename and deletions. Keep `JaceHwang/codex-usage-sidebar` untouched.

**Tech Stack:** Git/Git subtree, GitHub CLI and REST API, Markdown, YAML, Python 3, `skill-creator` validation scripts.

## Global Constraints

- Final `skills/` directories: `daily-news-briefing`, `frontend-ui-visual-gate`, `notion-worklog`, and `tracking-project-progress` only.
- Preserve source commits `a13839ec5d2a4d399cb9f383890e5d252981cf0a` and `84015a052532eb20b10e68d772173afd1e86437e` in the canonical repository history.
- Preserve the Tracking release point as `tracking-project-progress-v0.1.0` at `b9b98d78bc93b4c3efa8a4a6ec65702c8f219950`.
- Keep `JaceHwang/codex-usage-sidebar` available and unchanged.
- Do not delete or rename any GitHub repository until the final branch passes every local validation gate and is merged to `main`.
- Do not commit generated output, virtual environments, Python caches, credentials, or local configuration.

---

### Task 1: Import Daily News History and Preserve the Tracking Release Point

**Files:**
- Create: `imports/daily-news-briefing/**` (temporary subtree path)
- Create: Git tag `tracking-project-progress-v0.1.0`
- Test: Git ancestry and source HEAD assertions

**Interfaces:**
- Consumes: approved design commit and the current source repository HEADs.
- Produces: a branch whose object graph contains both standalone project histories before either source can be deleted.

- [ ] **Step 1: Recheck source HEADs before import**

Run:

```bash
test "$(git ls-remote https://github.com/JaceHwang/tracking-project-progress.git HEAD | awk '{print $1}')" = a13839ec5d2a4d399cb9f383890e5d252981cf0a
test "$(git ls-remote https://github.com/JaceHwang/daily-news-briefing.git HEAD | awk '{print $1}')" = 84015a052532eb20b10e68d772173afd1e86437e
```

Expected: both commands exit `0`; otherwise update the design constants and import the new HEAD before continuing.

- [ ] **Step 2: Import the Daily News repository as a subtree**

Run:

```bash
git remote add daily-news-briefing https://github.com/JaceHwang/daily-news-briefing.git
git fetch daily-news-briefing master
git subtree add --prefix=imports/daily-news-briefing daily-news-briefing master -m "migrate: import daily-news-briefing history"
```

Expected: `imports/daily-news-briefing/SKILL.md` exists and the subtree merge commit has source commit `84015a052532eb20b10e68d772173afd1e86437e` as a parent.

- [ ] **Step 3: Add the namespaced Tracking tag**

Run:

```bash
git cat-file -e b9b98d78bc93b4c3efa8a4a6ec65702c8f219950^{commit}
git tag -a tracking-project-progress-v0.1.0 b9b98d78bc93b4c3efa8a4a6ec65702c8f219950 -m "tracking-project-progress v0.1.0"
```

Expected: `git rev-parse tracking-project-progress-v0.1.0^{commit}` prints `b9b98d78bc93b4c3efa8a4a6ec65702c8f219950`.

- [ ] **Step 4: Verify both source histories are reachable**

Run:

```bash
git merge-base --is-ancestor a13839ec5d2a4d399cb9f383890e5d252981cf0a HEAD
git merge-base --is-ancestor 84015a052532eb20b10e68d772173afd1e86437e HEAD
```

Expected: both commands exit `0`.

### Task 2: Reduce the Working Tree to Four Skill Packages

**Files:**
- Create: `skills/tracking-project-progress/**`
- Create: `skills/daily-news-briefing/**`
- Delete: `projects/**`
- Delete: `plugins/**`
- Delete: `skills/grill-me/**`
- Delete: `skills/hatch-pet/**`
- Delete: `skills/README.md`
- Delete: `imports/**`

**Interfaces:**
- Consumes: existing Tracking package and imported Daily News subtree.
- Produces: exactly four directories below `skills/`, with source histories retained in Git ancestry.

- [ ] **Step 1: Record the failing precondition**

Run:

```bash
test "$(find skills -mindepth 1 -maxdepth 1 -type d -print | sed 's#skills/##' | sort | paste -sd, -)" = "daily-news-briefing,frontend-ui-visual-gate,notion-worklog,tracking-project-progress"
```

Expected before reorganization: failure because `grill-me`, `hatch-pet`, and missing retained packages make the directory set incorrect.

- [ ] **Step 2: Extract Tracking and move Daily News into final paths**

Run:

```bash
cp -R projects/tracking-project-progress/skills/tracking-project-progress skills/tracking-project-progress
mv imports/daily-news-briefing skills/daily-news-briefing
```

Expected: both final `SKILL.md` files exist.

- [ ] **Step 3: Remove non-retained repository content**

Delete the exact paths listed in this task with the patch/edit workflow, including `skills/daily-news-briefing/README.md`, while leaving `README.md`, `MIGRATION.md`, `docs/`, and the four retained Skill directories intact.

- [ ] **Step 4: Verify the exact Skill directory set**

Run:

```bash
test "$(find skills -mindepth 1 -maxdepth 1 -type d -print | sed 's#skills/##' | sort | paste -sd, -)" = "daily-news-briefing,frontend-ui-visual-gate,notion-worklog,tracking-project-progress"
test ! -e projects
test ! -e plugins
test ! -e imports
```

Expected: every command exits `0`.

### Task 3: Normalize Daily News and Notion Skill Metadata

**Files:**
- Modify: `skills/daily-news-briefing/SKILL.md`
- Create: `skills/daily-news-briefing/agents/openai.yaml`
- Create: `skills/notion-worklog/agents/openai.yaml`
- Preserve: `skills/daily-news-briefing/{scripts,config,assets,references,requirements.txt}`

**Interfaces:**
- Consumes: Skill instructions and the current `skill-creator` metadata schema.
- Produces: Codex-discoverable packages with two-field frontmatter and deterministic UI metadata.

- [ ] **Step 1: Record the failing Daily News frontmatter check**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
frontmatter = Path("skills/daily-news-briefing/SKILL.md").read_text().split("---", 2)[1]
keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if line and not line.startswith(" ")]
assert keys == ["name", "description"], keys
PY
```

Expected before normalization: assertion failure listing `license`, `compatibility`, and `metadata`.

- [ ] **Step 2: Normalize Daily News instructions**

Edit `SKILL.md` so YAML frontmatter contains only `name` and `description`. Preserve Python version, dependencies, internet requirement, author, version, and MIT licensing information in a concise prerequisites section. Update all commands and links to paths that exist inside `skills/daily-news-briefing`.

- [ ] **Step 3: Generate UI metadata**

Run:

```bash
python3 /Users/byctor/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py skills/daily-news-briefing \
  --interface display_name="Daily News Briefing" \
  --interface short_description="Generate a visual daily digest from weather and news sources" \
  --interface default_prompt="Use \$daily-news-briefing to generate today's news briefing card."
python3 /Users/byctor/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py skills/notion-worklog \
  --interface display_name="Notion Worklog" \
  --interface short_description="Capture work notes and create weekly or monthly reports" \
  --interface default_prompt="Use \$notion-worklog to capture this work update in Notion."
```

Expected: both `agents/openai.yaml` files exist and reference their matching `$skill-name` in `default_prompt`.

- [ ] **Step 4: Verify normalized package boundaries**

Run the frontmatter assertion from Step 1 again and verify the Daily News package contains no `README.md`, `output/`, `.venv/`, or `__pycache__/` paths.

Expected: all checks exit `0`.

- [ ] **Step 5: Commit the four-Skill working tree**

Run:

```bash
git add -A skills projects plugins imports
git commit -m "refactor: publish four canonical Skills"
```

Expected: one commit records the package extraction, normalization, and removal of non-retained content.

### Task 4: Rewrite Canonical Repository Documentation

**Files:**
- Modify: `README.md`
- Modify: `MIGRATION.md`

**Interfaces:**
- Consumes: final paths and source commit provenance from Tasks 1-3.
- Produces: bilingual installation and migration documentation that names only the four retained packages as current content.

- [ ] **Step 1: Record stale documentation references**

Run:

```bash
rg -n 'grill-me|hatch-pet|codex-usage-sidebar|projects/tracking-project-progress' README.md MIGRATION.md
```

Expected before rewriting: matches identifying stale catalog entries and paths.

- [ ] **Step 2: Rewrite the bilingual README**

Document the four Skill names, purposes, triggers, and exact copy/install commands using `skills/<name>`. Include English and Chinese sections in the same file and link to `MIGRATION.md`.

- [ ] **Step 3: Rewrite migration provenance**

Record local origins for `frontend-ui-visual-gate` and `notion-worklog`; record current source commits and history-preservation methods for Tracking and Daily News; record the namespaced Tracking release tag; explain that source repositories are removed only after final verification.

- [ ] **Step 4: Verify documentation**

Run:

```bash
for name in tracking-project-progress frontend-ui-visual-gate notion-worklog daily-news-briefing; do rg -q "$name" README.md MIGRATION.md; done
test "$(rg -c '^## English$|^## 中文$' README.md)" = 2
! rg -n 'skills/(grill-me|hatch-pet)|plugins/codex-usage-sidebar|projects/tracking-project-progress' README.md MIGRATION.md
```

Expected: all assertions exit `0`.

- [ ] **Step 5: Commit documentation**

Run:

```bash
git add README.md MIGRATION.md
git commit -m "docs: describe canonical Skills repository"
```

Expected: one documentation commit with no unrelated files.

### Task 5: Run Full Local Validation

**Files:**
- Test: all four `skills/*` packages
- Test: temporary directories outside the repository for Python environments and generated output

**Interfaces:**
- Consumes: final candidate working tree.
- Produces: fresh evidence that package structure, scripts, metadata, docs, history, and repository hygiene satisfy the design.

- [ ] **Step 1: Validate all Skill structures**

Create an isolated Python virtual environment under a `mktemp -d` directory, install `PyYAML`, and run `quick_validate.py` against each of the four `skills/*` directories.

Expected: four `Skill is valid!` results.

- [ ] **Step 2: Validate Tracking runtime behavior**

Run Python compilation, then use `skills/tracking-project-progress/scripts/project_board.py` against a temporary project root to perform `ensure`, `task-add`, `checkpoint`, and `validate`.

Expected: compilation exits `0`, command mutations succeed, and final validation reports `OK`.

- [ ] **Step 3: Validate Daily News runtime behavior**

Create another isolated virtual environment, install `skills/daily-news-briefing/requirements.txt`, compile its Python files, and run `scripts/generate.py` from a temporary copy of the Skill. Verify a PNG, Markdown, and HTML briefing are produced, then discard the temporary output.

Expected: generation exits `0` and all three output types exist.

- [ ] **Step 4: Run repository completion assertions**

Run:

```bash
git diff --check
git status --short
git merge-base --is-ancestor a13839ec5d2a4d399cb9f383890e5d252981cf0a HEAD
git merge-base --is-ancestor 84015a052532eb20b10e68d772173afd1e86437e HEAD
test "$(find skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')" = 4
```

Expected: no whitespace errors or uncommitted files, both history checks exit `0`, and the directory count is exactly four.

### Task 6: Review, Publish, and Merge

**Files:**
- Publish: branch `codex/reorganize-skills-repository`
- Publish: tag `tracking-project-progress-v0.1.0`
- Create and merge: pull request into `main`

**Interfaces:**
- Consumes: clean, fully validated local branch.
- Produces: verified final content on remote `main` before destructive repository operations.

- [ ] **Step 1: Review the complete diff against the approved design**

Inspect `git diff --stat origin/main...HEAD`, `git diff origin/main...HEAD`, the four package manifests, and source commit ancestry. Resolve every correctness finding and rerun Task 5.

- [ ] **Step 2: Push branch and tag**

Run:

```bash
git push -u origin codex/reorganize-skills-repository
git push origin tracking-project-progress-v0.1.0
```

Expected: both refs exist on `JaceHwang/codex-skills`.

- [ ] **Step 3: Open and merge the pull request**

Create a pull request describing the four retained Skills, history preservation, validation, and deferred deletion sequence. Mark it ready after review and merge it into `main`; delete the remote feature branch after merge.

- [ ] **Step 4: Re-read remote main**

Fetch `origin/main`, record the merged commit, verify the exact four-directory tree through the GitHub API, and rerun the ancestry assertions against `origin/main`.

Expected: remote `main` contains the reviewed commit and both source histories.

### Task 7: Rename and Delete GitHub Repositories

**Files:**
- Delete repository: `JaceHwang/skills`
- Rename repository: `JaceHwang/codex-skills` to `JaceHwang/Skills`
- Delete repositories: `JaceHwang/tracking-project-progress`, `JaceHwang/daily-news-briefing`
- Preserve repository: `JaceHwang/codex-usage-sidebar`

**Interfaces:**
- Consumes: verified remote `main`, unchanged source HEADs, and explicit user authorization.
- Produces: the final GitHub repository topology requested by the user.

- [ ] **Step 1: Reconfirm exact destructive targets**

Use GitHub repository metadata to assert that `JaceHwang/skills` is a fork of `anthropics/skills`, `JaceHwang/codex-skills` is owned and non-fork, and both standalone source HEADs still match the imported commits.

- [ ] **Step 2: Delete the fork and rename the aggregate**

Delete exactly `JaceHwang/skills`, then rename exactly `JaceHwang/codex-skills` to `Skills`. Update local `origin` to `https://github.com/JaceHwang/Skills.git` and fetch `main`.

- [ ] **Step 3: Verify the canonical repository before source deletion**

Assert `JaceHwang/Skills` is non-fork, owned by `JaceHwang`, defaults to `main`, serves the merged commit, exposes exactly four Skill directories, and contains both source commits and the namespaced tag.

- [ ] **Step 4: Delete migrated standalone sources**

Delete exactly `JaceHwang/tracking-project-progress` and `JaceHwang/daily-news-briefing`. Do not issue delete requests for nonexistent `frontend-ui-visual-gate` or `notion-worklog` repositories. Do not modify `JaceHwang/codex-usage-sidebar`.

- [ ] **Step 5: Perform the final external audit**

Verify the old fork and both migrated source endpoints return `404`; verify `JaceHwang/Skills` remains accessible with the exact final tree and history; verify `JaceHwang/codex-usage-sidebar` still returns `200`.

Expected: every requested deletion and preservation condition is proven by current GitHub state.
