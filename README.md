# Codex Skills

Personal monorepo for JaceHwang's Codex skills, skill-development projects, and Codex-related plugins.

[English](#english) | [中文](#中文)

## English

### What's here

| Location | Contents | Origin |
| --- | --- | --- |
| [`skills/`](./skills) | Standalone, directly installable Codex skills | Local custom skills |
| [`projects/tracking-project-progress/`](./projects/tracking-project-progress) | Skill-development project with tests, hooks, and documentation | `JaceHwang/tracking-project-progress` |
| [`plugins/codex-usage-sidebar/`](./plugins/codex-usage-sidebar) | Full Codex Usage Sidebar source; its plugin package is nested at [`plugins/codex-usage-sidebar/plugins/codex-usage-sidebar/`](./plugins/codex-usage-sidebar/plugins/codex-usage-sidebar) | `JaceHwang/codex-usage-sidebar` |

### Standalone skills

- [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate): align visual direction with the user before frontend UI architecture or implementation.
- [`grill-me`](./skills/grill-me): interview a plan or decision until its assumptions and dependencies are explicit.
- [`hatch-pet`](./skills/hatch-pet): create and validate Codex-compatible animated pets and spritesheets.
- [`notion-worklog`](./skills/notion-worklog): capture work notes in Notion and create weekly or monthly reports.
- [`tracking-project-progress`](./projects/tracking-project-progress/skills/tracking-project-progress): maintain a durable project board for non-trivial coding work.

### Install a skill in Codex

Copy the desired skill directory into Codex's default skills directory:

```bash
cp -R skills/frontend-ui-visual-gate ~/.codex/skills/
```

Codex also recognizes `~/.agents/skills/` as a cross-runtime skills directory. Use the source path under `projects/tracking-project-progress/skills/` for `tracking-project-progress`.

### Migration policy

This repository centralizes owned skill work without deleting its original repositories. The two GitHub source repositories are imported as Git subtrees so their source and history remain available here. See [`MIGRATION.md`](./MIGRATION.md) for the source-to-destination map.

## 中文

这是 JaceHwang 维护的 Codex Skills 总仓库，集中保存自建 skill、skill 开发项目和 Codex 相关插件。

### 目录说明

| 位置 | 内容 | 来源 |
| --- | --- | --- |
| [`skills/`](./skills) | 可直接安装的独立 Codex skill | 本机自定义 skill |
| [`projects/tracking-project-progress/`](./projects/tracking-project-progress) | 含测试、hooks 和文档的 skill 开发项目 | `JaceHwang/tracking-project-progress` |
| [`plugins/codex-usage-sidebar/`](./plugins/codex-usage-sidebar) | 完整的 Codex Usage Sidebar 源码；其插件包位于 [`plugins/codex-usage-sidebar/plugins/codex-usage-sidebar/`](./plugins/codex-usage-sidebar/plugins/codex-usage-sidebar) | `JaceHwang/codex-usage-sidebar` |

### 已收录 skill

- [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate)：在前端 UI 架构和编码前先与用户确认视觉方向。
- [`grill-me`](./skills/grill-me)：持续追问计划或决策，明确其假设与依赖。
- [`hatch-pet`](./skills/hatch-pet)：创建并验证兼容 Codex 的动画宠物与精灵图。
- [`notion-worklog`](./skills/notion-worklog)：将工作随手记写入 Notion，并生成周报或月报。
- [`tracking-project-progress`](./projects/tracking-project-progress/skills/tracking-project-progress)：为非简单编码工作维护可恢复的项目进度板。

### 在 Codex 中安装

将所需 skill 目录复制到 Codex 的默认目录：

```bash
cp -R skills/frontend-ui-visual-gate ~/.codex/skills/
```

Codex 同时识别跨运行时目录 `~/.agents/skills/`。`tracking-project-progress` 的源路径位于 `projects/tracking-project-progress/skills/`。

### 迁移原则

本仓库集中管理自建 skill，不删除原始仓库。两个 GitHub 源仓库通过 Git subtree 导入，以保留其源码和提交历史。完整来源映射见 [`MIGRATION.md`](./MIGRATION.md)。
A personal monorepo for Codex skills, supporting tools, and plugins.
