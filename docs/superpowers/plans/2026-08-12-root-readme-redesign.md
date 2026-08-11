# Root README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the root README with a polished Chinese-first guide that introduces all four canonical Skills and includes the existing Daily News sample image.

**Architecture:** Keep the change documentation-only and rooted in canonical package files. Use a consistent section template for each Skill, progressive disclosure for the tall image and English summary, and relative links so the README remains portable across GitHub clones.

**Tech Stack:** GitHub Flavored Markdown, conservative GitHub-supported HTML, shell/Python validation, `skills-ref` Agent Skills validator.

## Global Constraints

- The README must introduce exactly the four Skills listed in `MIGRATION.md`.
- Chinese is the primary narrative; English appears in a collapsed summary.
- Reuse `skills/daily-news-briefing/assets/sample-card.png`; do not create visual assets for Skills that have none.
- Derive capability claims from the current package README and `SKILL.md` files.
- Preserve the existing copy-based installation model for `~/.codex/skills/` and `~/.agents/skills/`.

---

### Task 1: Rewrite the root README

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `MIGRATION.md`, `skills/*/README.md`, `skills/*/SKILL.md`, and `skills/daily-news-briefing/assets/sample-card.png`
- Produces: a root `README.md` whose stable section anchors are `skills-overview`, `tracking-project-progress`, `frontend-ui-visual-gate`, `notion-worklog`, `daily-news-briefing`, `installation`, and `repository-layout`

- [ ] **Step 1: Replace the opening and overview**

Use a centered `<div align="center">` containing `Skills`, the Chinese/English positioning lines, and links to the four stable section anchors. Follow it with a canonical-repository note and a three-column overview table: Skill, solves, use when.

- [ ] **Step 2: Add the four parallel Skill sections**

For each section, use this exact content contract, substituting the concrete values in the mapping below:

```markdown
## 📍 `tracking-project-progress`

把目标、任务、决策、改动文件、验证、阻塞和下一步保存为仓库内可恢复的项目进度板。

**核心能力**

- 创建并恢复 `.project-board/` 中的持久状态
- 在任务中断、上下文压缩或交接后快速续接
- 保存精确验证证据、关键决策与一个可执行的下一步

**适合在这些时候使用：** 功能开发、缺陷修复、重构、迁移、多文件修改、项目恢复和任务交接。

```text
使用 tracking-project-progress 继续这个多文件迁移，并维护可恢复的进度板。
```

[查看 README](./skills/tracking-project-progress/README.md) · [查看 SKILL.md](./skills/tracking-project-progress/SKILL.md)
```

Repeat that structure with these concrete heading, link, and example mappings; the value proposition, capability bullets, and trigger sentence must use the source-backed wording defined in the design document:

| Heading | README link | SKILL link | Example prompt |
| --- | --- | --- | --- |
| `## 📍 tracking-project-progress` | `./skills/tracking-project-progress/README.md` | `./skills/tracking-project-progress/SKILL.md` | `使用 tracking-project-progress 继续这个多文件迁移，并维护可恢复的进度板。` |
| `## 🎨 frontend-ui-visual-gate` | `./skills/frontend-ui-visual-gate/README.md` | `./skills/frontend-ui-visual-gate/SKILL.md` | `使用 frontend-ui-visual-gate，先确认视觉方向，再实现这个页面。` |
| `## 📝 notion-worklog` | `./skills/notion-worklog/README.md` | `./skills/notion-worklog/SKILL.md` | `工作随手记：今天完成审批流最小版本，并确认了下周的接口联调计划。` |
| `## ☀️ daily-news-briefing` | `./skills/daily-news-briefing/README.md` | `./skills/daily-news-briefing/SKILL.md` | `使用 daily-news-briefing 生成今天的暖色新闻简报卡片。` |

- [ ] **Step 3: Add the existing Daily News visual**

Immediately after the Daily News detail links, add a collapsed `<details>` block with summary `查看实际生成效果 / Preview generated card`. Inside it, center an image referencing `./skills/daily-news-briefing/assets/sample-card.png`, set descriptive alt text, and use `width="420"` so the 1200×6286 source remains readable without dominating the page by default.

- [ ] **Step 4: Add installation, repository layout, and English summary**

Document clone/copy installation, the Daily News dependency command, a compact tree containing `MIGRATION.md`, `README.md`, and the four package directories, and a source-of-record note. End with a collapsed English summary containing the same four Skills in a compact table plus installation commands.

- [ ] **Step 5: Run focused README checks**

Run:

```bash
git diff --check
rg -n '^## .*`(tracking-project-progress|frontend-ui-visual-gate|notion-worklog|daily-news-briefing)`' README.md
rg -n 'skills/daily-news-briefing/assets/sample-card.png' README.md
```

Expected: no whitespace errors, exactly four Skill-heading matches, and one sample-image reference.

- [ ] **Step 6: Commit the README implementation**

```bash
git add README.md
git commit -m "docs: showcase four canonical Skills"
```

### Task 2: Validate repository documentation and packages

**Files:**
- Verify: `README.md`
- Verify: `skills/daily-news-briefing/assets/sample-card.png`
- Verify: `skills/*/SKILL.md`

**Interfaces:**
- Consumes: the completed root README from Task 1
- Produces: fresh evidence that all local links, HTML structure, package manifests, and Daily News behavior remain valid

- [ ] **Step 1: Validate local README links and required content**

Run this link and coverage validator:

```bash
python3 - <<'PY'
from pathlib import Path
import re

root = Path.cwd()
text = (root / "README.md").read_text(encoding="utf-8")
targets = re.findall(r"\[[^]]*\]\(([^)]+)\)", text)
targets += re.findall(r'<img[^>]+src="([^"]+)"', text)
missing = []
for target in targets:
    target = target.split("#", 1)[0]
    if not target or re.match(r"^(https?|mailto):", target):
        continue
    candidate = root / target.removeprefix("./")
    if not candidate.exists():
        missing.append(target)
assert not missing, f"missing local targets: {missing}"
for name in (
    "tracking-project-progress",
    "frontend-ui-visual-gate",
    "notion-worklog",
    "daily-news-briefing",
):
    assert text.count(name) >= 4, f"insufficient root README coverage for {name}"
print("README links and four-Skill coverage: OK")
PY
```

- [ ] **Step 2: Validate balanced HTML disclosure markup**

Run this structural validator:

```bash
python3 - <<'PY'
from pathlib import Path
import re

text = Path("README.md").read_text(encoding="utf-8")
for tag in ("details", "summary", "div", "p", "a"):
    opens = len(re.findall(fr"<{tag}(?:\s|>)", text, flags=re.I))
    closes = len(re.findall(fr"</{tag}>", text, flags=re.I))
    assert opens == closes, f"unbalanced <{tag}>: {opens} opening, {closes} closing"
assert re.search(r'<img[^>]+src="\./skills/daily-news-briefing/assets/sample-card\.png"', text)
print("README HTML structure: OK")
PY
```

- [ ] **Step 3: Validate all four Skill packages**

```bash
for skill_dir in skills/daily-news-briefing skills/frontend-ui-visual-gate skills/notion-worklog skills/tracking-project-progress; do
  uvx --python 3.11 --from skills-ref agentskills validate "$skill_dir"
done
```

Expected: four `Valid skill` results.

- [ ] **Step 4: Run the Daily News regression suite**

```bash
python3 -m unittest discover -s skills/daily-news-briefing/tests -v
```

Expected: 12 tests run with `OK`.

- [ ] **Step 5: Review the final diff and commit the plan record**

```bash
git diff origin/main...HEAD --check
git diff --stat origin/main...HEAD
git status --short --branch
```

Expected: only the design document, implementation plan, and root README differ from `origin/main`; the working tree is clean after commits.
