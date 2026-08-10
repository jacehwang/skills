# Skills

JaceHwang's canonical monorepo for reusable Codex and Agent Skills.

[English](#english) | [中文](#中文)

## English

This repository contains exactly four directly installable Skills. Each package is self-contained under `skills/<name>` and follows the current Codex Skill structure.

### Included Skills

| Skill | Purpose | Typical triggers |
| --- | --- | --- |
| [`tracking-project-progress`](./skills/tracking-project-progress) | Maintain a durable project board for multi-step coding work, interruptions, resumes, and handoffs. | Feature implementation, bug fixes, refactors, migrations, project resume, handoff |
| [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | Confirm whether to generate visual mockups and align on a selected direction before frontend implementation. | New or changed pages, components, layouts, responsive behavior, interaction states, visual styling |
| [`notion-worklog`](./skills/notion-worklog) | Capture freeform work notes in Notion and turn them into weekly or monthly leader-facing reports. | Work notes, meeting notes, weekly reports, monthly reports, work summaries |
| [`daily-news-briefing`](./skills/daily-news-briefing) | Generate a warm-toned PNG news briefing with weather, GitHub trends, AI/tech news, domestic news, and a quote. | Daily digest, morning briefing, news summary card |

### Install

Clone the monorepo, then copy the desired package into Codex's personal Skill directory:

```bash
git clone https://github.com/JaceHwang/Skills.git
mkdir -p ~/.codex/skills
cp -R Skills/skills/tracking-project-progress ~/.codex/skills/
```

Replace `tracking-project-progress` with `frontend-ui-visual-gate`, `notion-worklog`, or `daily-news-briefing` to install another package. Codex also recognizes `~/.agents/skills/` as a cross-runtime Skill location.

`daily-news-briefing` additionally requires Python 3.9+ and its Python dependencies:

```bash
python3 -m pip install -r ~/.codex/skills/daily-news-briefing/requirements.txt
```

### Repository Policy

This monorepo is the source of record for these four Skills. Their prior standalone repositories were consolidated only after source history and runtime behavior were verified. See [`MIGRATION.md`](./MIGRATION.md) for commit provenance and retained history.

## 中文

这是 JaceHwang 维护的 Codex 与 Agent Skills 权威总仓库，只收录四个可直接安装的 Skill。每个包均位于 `skills/<name>`，并按照当前 Codex Skill 结构整理。

### 收录的 Skills

| Skill | 用途 | 典型触发场景 |
| --- | --- | --- |
| [`tracking-project-progress`](./skills/tracking-project-progress) | 为多步骤开发、任务中断、恢复和交接维护持久化项目进度板。 | 功能开发、缺陷修复、重构、迁移、恢复项目、任务交接 |
| [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | 前端实现前先询问是否生成效果图，并以用户选定的视觉方向作为后续开发门禁。 | 新建或调整页面、组件、布局、响应式行为、交互状态和视觉样式 |
| [`notion-worklog`](./skills/notion-worklog) | 将工作随手记写入 Notion，并从零散记录生成面向管理者的周报或月报。 | 工作记录、会议记录、周报、月报、工作总结 |
| [`daily-news-briefing`](./skills/daily-news-briefing) | 生成包含天气、GitHub 趋势、AI/科技新闻、国内新闻和每日名言的暖色 PNG 简报。 | 每日新闻摘要、晨报、新闻卡片 |

### 安装

克隆总仓库，再将需要的 Skill 复制到 Codex 个人目录：

```bash
git clone https://github.com/JaceHwang/Skills.git
mkdir -p ~/.codex/skills
cp -R Skills/skills/tracking-project-progress ~/.codex/skills/
```

将 `tracking-project-progress` 替换为 `frontend-ui-visual-gate`、`notion-worklog` 或 `daily-news-briefing`，即可安装其他包。Codex 同时识别跨运行时目录 `~/.agents/skills/`。

`daily-news-briefing` 还需要 Python 3.9+ 及其依赖：

```bash
python3 -m pip install -r ~/.codex/skills/daily-news-briefing/requirements.txt
```

### 仓库原则

本仓库是这四个 Skill 的唯一权威来源。旧独立仓库仅在源码历史和运行行为验证通过后才被合并并删除。提交来源和历史保留方式见 [`MIGRATION.md`](./MIGRATION.md)。
