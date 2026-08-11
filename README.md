<div align="center">

# Skills

**四个可直接安装的 Codex / Agent Skills，让重复工作变成可靠流程。**

<sub>Four focused Skills for durable development, visual alignment, Notion worklogs, and daily news briefings.</sub>

<p>
  <a href="#tracking-project-progress">项目进度</a>&nbsp; · &nbsp;
  <a href="#frontend-ui-visual-gate">视觉门禁</a>&nbsp; · &nbsp;
  <a href="#notion-worklog">Notion 工作日志</a>&nbsp; · &nbsp;
  <a href="#daily-news-briefing">每日新闻简报</a>
</p>

</div>

> [!NOTE]
> 这是 `JaceHwang/Skills` 的权威仓库。每个 Skill 都是 `skills/<name>` 下可独立安装的自包含包；来源提交与迁移证据见 [`MIGRATION.md`](./MIGRATION.md)。

<a id="skills-overview"></a>

## 一览

| Skill | 解决什么问题 | 适合什么时候使用 |
| --- | --- | --- |
| [`tracking-project-progress`](./skills/tracking-project-progress) | 用仓库内的持久进度板保存开发上下文，让中断后的任务可以准确续接。 | 功能开发、缺陷修复、重构、迁移、多文件修改、恢复与交接 |
| [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | 在前端编码前先确认视觉预期与选定方向，减少“做完才发现不是想要的”返工。 | 页面、组件、布局、响应式、交互状态、样式和 UI 文案调整 |
| [`notion-worklog`](./skills/notion-worklog) | 将零散工作口述写入 Notion，再整理为可汇报的周报或月报。 | 工作随手记、会议记录、待办、周报、月报和工作总结 |
| [`daily-news-briefing`](./skills/daily-news-briefing) | 采集天气与多源资讯，生成暖色调 PNG 新闻简报卡片。 | 每日新闻摘要、晨报、科技资讯汇总和图片简报 |

---

<a id="tracking-project-progress"></a>

## 📍 `tracking-project-progress`

把目标、任务、决策、改动文件、验证、阻塞和下一步保存为仓库内可恢复的项目进度板。

**核心能力**

- 创建 `.project-board/state.json`、`board.md` 和 `events.jsonl`，同时服务机器恢复、人类阅读与修订审计。
- 在会话中断、上下文压缩或任务交接后，先恢复真实进度，再与 Git 状态和测试证据核对。
- 约束同一时间只有一个进行中任务，并在里程碑处记录精确验证结果、关键决策和一个可执行的下一步。

**适合在这些时候使用：** 功能开发、缺陷修复、重构、迁移、多文件修改、项目恢复和任务交接。

```text
使用 tracking-project-progress 继续这个多文件迁移，并维护可恢复的进度板。
```

[查看 README](./skills/tracking-project-progress/README.md) · [查看 SKILL.md](./skills/tracking-project-progress/SKILL.md)

---

<a id="frontend-ui-visual-gate"></a>

## 🎨 `frontend-ui-visual-gate`

在前端架构和编码前完成视觉方向对齐，让用户先确认“看起来怎样、感受如何”，再进入实现。

**核心能力**

- 门禁 A 主动询问是否先生成 2–4 种效果图，并收集专业、可信、轻松、高效等目标心理感受。
- 用户选择生图后，门禁 B 要求明确选定单一方向或组合方案；未选择前不会进入架构与编码。
- 用视觉决策简报固定必须保留、明确避开、响应式意图与无障碍底线，作为开发和回归验证的依据。

**适合在这些时候使用：** 新建或调整页面、组件、布局、主题、字体、颜色、间距、交互状态、响应式行为、动效和 UI 文案。

```text
使用 frontend-ui-visual-gate，先确认视觉方向，再实现这个页面。
```

[查看 README](./skills/frontend-ui-visual-gate/README.md) · [查看 SKILL.md](./skills/frontend-ui-visual-gate/SKILL.md)

---

<a id="notion-worklog"></a>

## 📝 `notion-worklog`

把粗糙、零散的工作口述低成本写入 Notion，并在需要时整理成面向管理者的周报或月报。

**核心能力**

- 按上海时区定位每日页面，将原始口述归入已完成、进行中、待办、会议、决策、风险或计划。
- 汇总目标周期内的随手记，并参考历史报告保持连续性，生成结果导向的周报或月报。
- 保留原始措辞与来源链接；资料不足时标记“待补充”，不虚构进度、指标、阻塞或计划。

**适合在这些时候使用：** 工作随手记、工作待办、会议记录、生成周报、生成月报和工作汇报。普通文章链接的“记一下”不属于它的触发范围。

```text
工作随手记：今天完成审批流最小版本，并确认了下周的接口联调计划。
```

[查看 README](./skills/notion-worklog/README.md) · [查看 SKILL.md](./skills/notion-worklog/SKILL.md)

---

<a id="daily-news-briefing"></a>

## ☀️ `daily-news-briefing`

从多种在线来源采集信息，生成包含天气、趋势、新闻与名言的暖色调每日简报卡片。

**核心能力**

- 聚合多城市天气、GitHub Trending、Product Hunt、AI/科技动态、国内热点和每日名言。
- 使用 Pillow 输出动态高度 PNG，同时保存 Markdown、HTML 和按日期留存的源数据。
- 提供集中配置、跨平台中文字体、翻译积压与静态名言等回退机制，并允许 Agent 预填受限来源。

**适合在这些时候使用：** 每日新闻摘要、晨间简报、开发与产品趋势汇总，以及需要直接发送的图片新闻卡片。

```text
使用 daily-news-briefing 生成今天的暖色新闻简报卡片。
```

[查看 README](./skills/daily-news-briefing/README.md) · [查看 SKILL.md](./skills/daily-news-briefing/SKILL.md)

<details>
<summary><strong>查看实际生成效果 / Preview generated card</strong></summary>

<br />

<p align="center">
  <a href="./skills/daily-news-briefing/assets/sample-card.png">
    <img src="./skills/daily-news-briefing/assets/sample-card.png" alt="Daily News Briefing 生成的暖色新闻简报卡片" width="420" />
  </a>
</p>

</details>

---

<a id="installation"></a>

## 安装

克隆仓库，然后复制需要的 Skill：

```bash
git clone https://github.com/JaceHwang/Skills.git
mkdir -p ~/.codex/skills
cp -R Skills/skills/tracking-project-progress ~/.codex/skills/
```

将 `tracking-project-progress` 换成另外三个目录名即可安装其他 Skill。Codex 也识别跨运行时目录 `~/.agents/skills/`。

`daily-news-briefing` 额外需要 Python 3.9+ 及其依赖：

```bash
python3 -m pip install -r ~/.codex/skills/daily-news-briefing/requirements.txt
```

<a id="repository-layout"></a>

## 仓库结构

```text
Skills/
├── README.md
├── MIGRATION.md
└── skills/
    ├── tracking-project-progress/
    ├── frontend-ui-visual-gate/
    ├── notion-worklog/
    └── daily-news-briefing/
```

每个子目录都包含作为执行入口的 `SKILL.md`，并按需携带 `agents/`、`scripts/`、`references/`、配置或资源。旧项目仅在历史、结构和运行验证完成后才合并到本仓库；详细来源与保留方式请参阅 [`MIGRATION.md`](./MIGRATION.md)。

---

<details>
<summary><strong>English summary</strong></summary>

## Four focused, installable Skills

This is the canonical monorepo for four self-contained Codex and Agent Skills:

| Skill | What it does | Use it for |
| --- | --- | --- |
| [`tracking-project-progress`](./skills/tracking-project-progress) | Maintains a durable, repository-local project board with tasks, decisions, changed files, verification, blockers, and one next action. | Multi-step development, interruptions, resumes, migrations, and handoffs |
| [`frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | Aligns visual expectations and requires an explicit direction before frontend architecture or implementation. | Pages, components, responsive behavior, interaction states, styling, and UI copy |
| [`notion-worklog`](./skills/notion-worklog) | Captures rough work notes in Notion and turns them into traceable weekly or monthly reports. | Work notes, meetings, todos, summaries, and manager-facing reports |
| [`daily-news-briefing`](./skills/daily-news-briefing) | Produces a warm-toned PNG briefing with weather, developer trends, product launches, AI/tech news, domestic news, and a quote. | Daily digests, morning briefings, and shareable news cards |

### Install

```bash
git clone https://github.com/JaceHwang/Skills.git
mkdir -p ~/.codex/skills
cp -R Skills/skills/tracking-project-progress ~/.codex/skills/
```

Replace `tracking-project-progress` with any other package name. Cross-runtime clients can use `~/.agents/skills/`. Daily News also requires the dependencies in its `requirements.txt`.

</details>
