# Codex Skills Monorepo Migration

## Goal

Create a GitHub repository owned by JaceHwang for personal Codex skill work, rather than publishing to the forked `JaceHwang/skills` repository.

## Structure

```text
skills/     Directly installable custom skills
projects/   Complete skill-development repositories with tests and tooling
plugins/    Complete Codex-related plugin repositories
```

## Sources

- Local custom skills: `frontend-ui-visual-gate`, `grill-me`, `hatch-pet`, and `notion-worklog`.
- Self-owned GitHub repositories: `tracking-project-progress` and `codex-usage-sidebar`.

## Invariants

1. Direct skills retain their installed directory layout.
2. Imported repositories retain source history through Git subtree merges.
3. Source repositories and the fork remain untouched.
4. The fork-only draft PR is closed after the new repository contains a validated migration.
5. Root documentation explains both English and Chinese installation and provenance.

## Verification

- Validate every standalone skill and the imported tracking skill with `quick_validate.py`.
- Run the tracking project test suite from its imported project root.
- Run the Usage Sidebar offline test scripts and validate its JSON manifests.
- Compare local skill directories against their migrated copies.
- Run `git diff --check` and `git fsck --no-dangling`.

## 迁移说明

该总仓库用于集中管理 JaceHwang 自建的 Codex skill、skill 开发项目和插件。独立 skill 放在 `skills/`；需要保留测试、hooks 和完整源码的项目放在 `projects/` 或 `plugins/`。GitHub 源仓库通过 Git subtree 导入，以保留提交历史；原始仓库和 fork 不会被删除。
