# Skills Repository Reorganization Design

**Date:** 2026-08-10
**Status:** Approved direction (option 1: preserve source history)

## Objective

Turn `JaceHwang/codex-skills` into the canonical `JaceHwang/Skills` repository. The final repository must expose exactly four installable Skill packages:

1. `tracking-project-progress`
2. `frontend-ui-visual-gate`
3. `notion-worklog`
4. `daily-news-briefing`

After the final repository is published and verified, delete the obsolete fork `JaceHwang/skills` and the two existing standalone source repositories, `JaceHwang/tracking-project-progress` and `JaceHwang/daily-news-briefing`. Keep the unrelated standalone plugin repository `JaceHwang/codex-usage-sidebar`.

`frontend-ui-visual-gate` and `notion-worklog` do not currently have standalone GitHub repositories, so there is no corresponding remote repository to delete for either Skill.

## Final Repository Shape

The default branch will contain only four directories under `skills/`:

```text
Skills/
├── .gitignore
├── MIGRATION.md
├── README.md
├── docs/
│   └── superpowers/
│       ├── plans/
│       └── specs/
└── skills/
    ├── daily-news-briefing/
    ├── frontend-ui-visual-gate/
    ├── notion-worklog/
    └── tracking-project-progress/
```

Repository-level documentation is allowed, but no other Skill, plugin, or full project tree may remain. In particular, remove `grill-me`, `hatch-pet`, `plugins/codex-usage-sidebar`, and the full `projects/tracking-project-progress` tree after extracting its Skill package.

## Skill Normalization

### tracking-project-progress

Move the existing package from `projects/tracking-project-progress/skills/tracking-project-progress` to `skills/tracking-project-progress`. Retain only the package contents required by the Skill:

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/project_board.py`
- `references/board-schema.md`

The existing subtree merge already connects source commit `a13839ec5d2a4d399cb9f383890e5d252981cf0a` to the aggregate repository history. Preserve that ancestry while removing the surrounding project checkout from the final tree. Preserve the original `v0.1.0` release point with the namespaced tag `tracking-project-progress-v0.1.0` so it cannot collide with future tags from other Skills. Record the original release name and source commit in `MIGRATION.md`.

### frontend-ui-visual-gate

Keep the current package under `skills/frontend-ui-visual-gate` without behavioral changes. Revalidate its `SKILL.md` and `agents/openai.yaml` after the repository reorganization.

### notion-worklog

Keep the current package under `skills/notion-worklog` without behavioral changes. Generate `agents/openai.yaml` from the final `SKILL.md` so the Skill has the same discoverable UI metadata as the other three packages.

### daily-news-briefing

Import `JaceHwang/daily-news-briefing` from its current `master` commit, `84015a052532eb20b10e68d772173afd1e86437e`, using a subtree merge so the complete source history remains reachable after the standalone repository is deleted. Then normalize the imported package under `skills/daily-news-briefing`:

- Keep essential executable and supporting content: `SKILL.md`, `scripts/`, `config/`, `assets/`, `references/`, and `requirements.txt`.
- Restrict YAML frontmatter to `name` and `description`; preserve the current compatibility, dependency, license, author, and version information in the body.
- Add `agents/openai.yaml` generated from the final `SKILL.md`.
- Remove the package-level `README.md`; preserve necessary operating instructions in `SKILL.md` or a focused file under `references/`.
- Do not commit generated `output/` artifacts, Python caches, virtual environments, credentials, or local configuration.

The source repository has no issues, pull requests, tags, or releases, so its Git commit history is the complete remote state that needs preservation.

## Repository Documentation

Rewrite the root `README.md` as a bilingual English/Chinese catalog. It must:

- identify `JaceHwang/Skills` as the canonical repository;
- list exactly the four included Skills and describe their triggers and purposes;
- show installation commands for each Skill from the monorepo;
- explain that individual source repositories were consolidated and removed;
- link to `MIGRATION.md` for commit and history provenance.

Rewrite `MIGRATION.md` to map every retained Skill to its source, final path, and preservation method. Remove references that describe `codex-usage-sidebar`, `grill-me`, or `hatch-pet` as current repository contents. Historical statements may mention removed content only when needed to explain the reorganization.

## Validation Gates

No GitHub repository may be deleted until all of the following pass on the proposed final commit:

1. `skills/` contains exactly the four approved directory names.
2. Every Skill passes the current `skill-creator` `quick_validate.py` check.
3. Every `agents/openai.yaml` file is valid and consistent with its `SKILL.md`.
4. `tracking-project-progress` passes Python compilation and a temporary-project CLI round trip (`ensure`, task mutation, checkpoint, and `validate`).
5. `daily-news-briefing` passes Python compilation, dependency installation in an isolated environment, and a generation smoke test without committing generated output.
6. Root README links and installation paths resolve.
7. `git diff --check` reports no whitespace errors and the working tree is clean.
8. The final Git history contains the current source commits for `tracking-project-progress` and `daily-news-briefing`.
9. The proposed branch is reviewed and merged into the default branch before rename or deletion begins.

## GitHub Transition Sequence

Perform external mutations in this order:

1. Push the reorganization branch to `JaceHwang/codex-skills`, open a pull request, and merge the verified commit into `main`.
2. Re-read remote `main` and verify the exact tree, Skill checks, and source commit ancestry.
3. Delete the obsolete fork `JaceHwang/skills`. This frees the case-insensitive `Skills` repository name.
4. Rename `JaceHwang/codex-skills` to `JaceHwang/Skills` and update the local `origin` URL.
5. Verify the renamed repository is owned by `JaceHwang`, is not a fork, has `main` as its default branch, and serves the verified commit.
6. Verify source HEADs have not changed since import, then delete `JaceHwang/tracking-project-progress` and `JaceHwang/daily-news-briefing`.
7. Confirm the deleted repository endpoints return not found and the canonical repository still contains both source commits and all four valid Skill packages.

Do not delete `JaceHwang/codex-usage-sidebar`. No deletion call is needed for the nonexistent `JaceHwang/frontend-ui-visual-gate` or `JaceHwang/notion-worklog` repositories.

## Failure Handling

- If any content, validation, pull request, or merge check fails, stop before deleting or renaming repositories.
- If deleting the old fork fails, leave `codex-skills` unchanged because the desired `Skills` name may still be occupied.
- If the rename succeeds but a source deletion fails, keep the remaining source repository and report the exact failure; the canonical repository remains usable.
- If either source HEAD changes after import, update the aggregate repository and repeat all validation before deletion.
- Treat successful deletion as irreversible for this workflow. The aggregate Git history and migration documentation are the recovery record.

## Completion Criteria

The work is complete only when GitHub shows a non-fork `JaceHwang/Skills` repository whose `main` branch contains exactly the four approved Skill directories, all validation gates pass, the old fork and both existing standalone source repositories are absent, and `JaceHwang/codex-usage-sidebar` remains available.
