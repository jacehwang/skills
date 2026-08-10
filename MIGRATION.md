# Migration Map / 迁移映射

This document records how the four canonical Skill packages were consolidated into `JaceHwang/Skills` before their obsolete source repositories were removed.

本文记录四个权威 Skill 包迁入 `JaceHwang/Skills` 的方式，以及删除旧来源仓库前保留的历史证据。

| Source / 来源 | Final path / 最终路径 | Preservation / 保留方式 |
| --- | --- | --- |
| Installed local `frontend-ui-visual-gate` | [`skills/frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | Copied from the installed and forward-tested package. / 从已安装并完成前测的包复制。 |
| Installed local `notion-worklog` | [`skills/notion-worklog`](./skills/notion-worklog) | Copied from the installed package and supplemented with Codex UI metadata. / 从已安装包复制，并补充 Codex UI 元数据。 |
| `JaceHwang/tracking-project-progress` at `a13839ec5d2a4d399cb9f383890e5d252981cf0a` | [`skills/tracking-project-progress`](./skills/tracking-project-progress) | Its full history was attached by Git subtree, then the standards-compliant package was extracted from `skills/tracking-project-progress` in that source tree. / 使用 Git subtree 接入完整历史，再提取符合规范的 Skill 包。 |
| `JaceHwang/daily-news-briefing` `master` at `84015a052532eb20b10e68d772173afd1e86437e` | [`skills/daily-news-briefing`](./skills/daily-news-briefing) | Its full history was attached by Git subtree before the package was normalized for Codex. / 先使用 Git subtree 接入完整历史，再按 Codex 规范整理包结构。 |

## History Evidence / 历史证据

- Tracking subtree split: `a13839ec5d2a4d399cb9f383890e5d252981cf0a`
- Daily News subtree split: `84015a052532eb20b10e68d772173afd1e86437e`
- Tracking original release: `tracking-project-progress v0.1.0`
- Tracking release commit: `b9b98d78bc93b4c3efa8a4a6ec65702c8f219950`
- Canonical namespaced tag: `tracking-project-progress-v0.1.0`

Both source commits remain ancestors of the canonical default branch. The namespaced tag avoids collisions with releases from other Skills in the monorepo.

两个来源提交均保留为权威默认分支的祖先提交。命名空间标签可避免不同 Skill 的版本标签冲突。

## Repository Transition / 仓库调整

The obsolete `JaceHwang/skills` fork of `anthropics/skills` was removed before `JaceHwang/codex-skills` was renamed to `JaceHwang/Skills`. The standalone `tracking-project-progress` and `daily-news-briefing` repositories were removed only after the canonical `main` branch passed structural, runtime, documentation, and history checks.

在将 `JaceHwang/codex-skills` 重命名为 `JaceHwang/Skills` 前，先删除从 `anthropics/skills` fork 的旧 `JaceHwang/skills`。只有在权威 `main` 分支通过结构、运行、文档和历史校验后，才删除独立的 `tracking-project-progress` 与 `daily-news-briefing` 仓库。

`frontend-ui-visual-gate` and `notion-worklog` had no standalone GitHub repositories to delete. `JaceHwang/codex-usage-sidebar` remains an independent plugin repository and is intentionally not part of this Skills monorepo.

`frontend-ui-visual-gate` 与 `notion-worklog` 原本没有独立 GitHub 仓库，因此无需删除。`JaceHwang/codex-usage-sidebar` 继续作为独立插件仓库保留，不属于本 Skills 总仓库。

## Package Normalization / 包规范化

- `tracking-project-progress` keeps only `SKILL.md`, `agents/`, `scripts/`, and `references/` from its former full project repository.
- `daily-news-briefing` uses two-field Skill frontmatter, generated `agents/openai.yaml`, and only essential scripts, configuration, dependencies, references, and assets.
- `frontend-ui-visual-gate` keeps its validated visual-direction gate behavior.
- `notion-worklog` keeps its existing workflow and gains generated `agents/openai.yaml` metadata.

- `tracking-project-progress` 仅保留原完整项目中的 `SKILL.md`、`agents/`、`scripts/` 和 `references/`。
- `daily-news-briefing` 使用双字段 Skill frontmatter、生成的 `agents/openai.yaml`，以及必要的脚本、配置、依赖、参考资料和资源。
- `frontend-ui-visual-gate` 保留已验证的视觉方向门禁行为。
- `notion-worklog` 保留原工作流，并新增生成的 `agents/openai.yaml` 元数据。
