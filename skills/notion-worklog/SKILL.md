---
name: notion-worklog
description: Capture freeform work notes into Notion and generate weekly or monthly leader-facing work reports from messy Notion notes. Use when the user says 工作随手记, 工作记一下, 工作记录, 工作待办, 会议记录, 生成周报, 生成月报, 工作总结, 工作汇报, or explicitly asks to write/read Notion work logs. Do not use for generic 记一下 plus article links or article-memory requests.
---

# Notion Worklog

This skill provides a low-friction workflow for work logging and reporting in Notion.

The user should not need to manually create Notion note pages, choose folders, or fill database fields. The assistant decides where to place each freeform note and later turns the accumulated notes into structured weekly or monthly reports.

## Notion Page Assumptions

Default root pages:

- `工作随手记`: source notes
- `工作报告`: generated reports

If either root page does not exist, ask for permission to create it in Notion. If Notion write tools are unavailable, provide the exact Markdown content and target path for the user to create manually.

Default page tree:

```text
工作随手记
  YYYY-MM-DD 随手记

工作报告
  周报
    YYYY-Www 工作周报
  月报
    YYYY-MM 工作月报
```

Do not require a Notion database schema.

## Modes

Choose the mode from the user's request.

### Capture Mode

Use this when the user says things like:

- `工作随手记：今天和产品确认了审批流先做最小版本`
- `工作记一下：王工接口字段还没定，明天要催`
- `工作记录：下午把演示材料改了一版，发给领导看了`
- `会议记录：...`
- `工作待办：...`

Do not use capture mode for generic `记一下` requests that contain an article URL, webpage URL, paper link, blog link, newsletter link, or reading-memory intent. Those should be handled by the user's article memory system.

Workflow:

1. Treat everything after the trigger phrase as note content.
2. Determine today's date in `Asia/Shanghai` unless the user states another date.
3. Locate or create the daily Notion page:
   - `工作随手记 / YYYY-MM-DD 随手记`
4. Infer the note type:
   - completed work
   - ongoing work
   - todo
   - meeting note
   - decision
   - risk or blocker
   - future plan
   - general note
5. Append the note under the matching section on the daily page.
6. Preserve the user's raw wording, then optionally add a short normalized line when useful.
7. If project names, people, dates, or next actions are inferable, add lightweight metadata inline.

Daily page section template:

```markdown
# YYYY-MM-DD 随手记

## 已完成

## 进行中

## 待办

## 会议与沟通

## 决策与结论

## 风险与阻塞

## 计划

## 其他
```

Append format:

```markdown
- HH:mm 原文：{raw_note}
  - 类型：{inferred_type}
  - 项目：{project_or_未识别}
  - 后续动作：{next_action_or_无}
```

Rules:

- Do not ask the user where to put the note unless the target Notion workspace/page is ambiguous.
- Do not force the user to rewrite rough or casual text.
- Do not over-structure small notes.
- If the note contains private or emotional wording, preserve it in the source note but avoid surfacing it in reports unless it affects work risk.

### Report Mode

Use this when the user asks for:

- 本周周报
- 上周周报
- 本月月报
- 指定日期范围工作总结
- 基于 Notion 随手记生成汇报

Workflow:

1. Determine report type and period:
   - `本周`: Monday 00:00 to now, `Asia/Shanghai`
   - `上周`: previous Monday through Sunday
   - `本月`: first day of current month to now
   - explicit dates override defaults
2. Read source notes under `工作随手记` for the target period.
3. Read historical reports for continuity:
   - weekly report: latest 2-4 prior weekly reports when available
   - monthly report: current-month weekly reports plus latest 1-3 prior monthly reports when available
4. Extract work items from messy text:
   - completed work
   - ongoing work
   - meeting decisions
   - coordination progress
   - risks or blockers
   - todo and future plan
   - project names
   - source page links
5. Merge repeated or related fragments into work themes.
6. Convert rough notes into concise, leader-facing Chinese.
7. Write the generated report back to Notion:
   - weekly: `工作报告 / 周报 / YYYY-Www 工作周报`
   - monthly: `工作报告 / 月报 / YYYY-MM 工作月报`

## Report Structure

Default weekly report:

```markdown
# YYYY-Www 工作周报

## 一、本周重点成果

## 二、主要推进事项

## 三、会议与协同进展

## 四、风险与待协调事项

## 五、下周工作计划

## 六、参考记录
```

Default monthly report:

```markdown
# YYYY-MM 工作月报

## 一、本月核心成果

## 二、重点项目推进

## 三、协同与管理事项

## 四、风险、问题与资源需求

## 五、下月工作计划

## 六、参考记录
```

## Reporting Rules

- Prefer outcome-oriented wording over diary-style wording.
- Do not include every note. Select and consolidate what is useful for a manager.
- Do not invent progress, blockers, metrics, decisions, or future plans.
- If the source is sparse, write `待补充` rather than fabricating content.
- Historical reports are only for continuity, tone, and plan follow-up. Current-period source notes are the primary evidence.
- If a prior plan appears unresolved in current notes, phrase it neutrally as ongoing, pending, or requiring follow-up.
- Keep important claims traceable through source links in `参考记录`.
- Avoid exposing private, emotional, or low-value fragments in the final report.

## Minimal Confirmation Policy

Capture mode should usually complete without asking follow-up questions.

Ask only when:

- the Notion workspace or root page is ambiguous;
- the user asks to backdate a note but the date is unclear;
- the note appears sensitive and the user explicitly asks to include it in a report;
- writing to Notion fails.

Report mode may ask one concise clarification when the period is ambiguous. Otherwise choose the default period from the request.

## Useful User Prompts

Capture:

```text
随手记：今天和产品确认审批流先做最小版本，王工接口字段明天再确认。
```

```text
会议记录：上午开了客户同步会，客户希望下周三前看到演示版，风险是测试数据还没给。
```

Report:

```text
用 notion-worklog 生成上周周报并写回 Notion。
```

```text
基于工作随手记生成 2026-06 月报，参考最近两个月月报的风格。
```
