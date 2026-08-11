# Notion Worklog

Notion Worklog 是一个 Codex Skill 项目，用来把零碎的工作口述记录写入 Notion，并在需要时生成周报/月报。

它的目标是降低日常记录成本：

1. 你通过 Codex 或 Claude Code 输入粗糙的工作随手记。
2. Skill 自动写入 Notion 的对应日期页面。
3. 一段时间后，Skill 读取这些混乱记录，整理成领导可读的周报/月报。
4. 生成的报告再写回 Notion。

## 项目结构

```text
notion-worklog/
  README.md
  skill/
    SKILL.md
```

`skill/SKILL.md` 是实际可安装的 Skill 内容。

## Notion 前置配置

这个项目需要 Notion 连接具备读写权限。前置条件分两层：

1. **AI 工具连接层**：Codex / Claude Code 必须连接到 Notion，并且该连接允许读写。
2. **Notion 页面权限层**：连接只能访问当前 Notion 用户有权限访问的页面；如果使用传统 Notion integration，则还需要把目标父页面分享给该 integration。

官方资料要点：

- [Notion MCP](https://www.notion.com/help/notion-mcp) 是给 AI 助手使用的连接方式，可让 AI app 实时读取和写入 Notion 页面；它不会绕过 Notion 权限，通常以当前连接用户的权限为边界。
- [Notion connection capabilities](https://developers.notion.com/reference/capabilities) 将权限拆成 `Read content`、`Update content`、`Insert content` 等能力。本项目至少需要：
  - `Read content`：读取随手记和历史报告。
  - `Insert content`：创建根页面、日期页面、周报/月报页面。
  - `Update content`：向已有随手记页面追加内容，或更新已有报告。
- [Notion internal connections](https://developers.notion.com/guides/get-started/internal-connections) 的权限属于 connection 本身；把父页面分享给 connection 后，connection 可访问该父页面及其子页面。

## 推荐 Notion 布局

Skill 默认使用两个根页面：

- `工作随手记`：保存原始记录。
- `工作报告`：保存生成的周报/月报。

默认页面树：

```text
工作随手记
  YYYY-MM-DD 随手记

工作报告
  周报
    YYYY-Www 工作周报
  月报
    YYYY-MM 工作月报
```

如果这两个根页面不存在，Skill 应引导 Codex 或 Claude Code 创建它们。

## 安装

推荐用软链接安装，这样项目目录就是唯一维护源：

```bash
rm -rf ~/.codex/skills/notion-worklog
ln -s /Users/byctor/Projects/notion-worklog/skill ~/.codex/skills/notion-worklog
```

修改已安装 Skill 后，重启 Codex 或新开会话，让 Skill 元数据重新加载。

## 使用方式

记录工作随手记：

```text
工作随手记：今天和产品确认审批流先做最小版本，王工接口字段明天再确认。
```

```text
工作记一下：下午把演示材料改了一版，发给领导看了。
```

```text
会议记录：客户希望下周三前看到演示版，风险是测试数据还没给。
```

生成报告：

```text
用 notion-worklog 生成上周周报并写回 Notion。
```

```text
基于工作随手记生成 2026-06 月报，参考最近两个月月报的风格。
```

## 触发边界

本项目刻意避免使用泛化的 `记一下` 作为触发词，因为已有文章记忆系统处理文章链接。

用于工作记录：

```text
工作记一下：...
```

不要用于文章记忆：

```text
记一下：https://example.com/article
```

文章链接、论文链接、阅读记忆请求应交给文章记忆系统。

## 权限验证步骤

第一次使用前，建议做一次最小读写测试：

1. 在 Codex 中确认 Notion 插件已连接。
2. 搜索当前用户信息，确认连接可用。
3. 创建一个私有测试页。
4. 在测试页下创建一个子页。
5. Fetch 子页，确认能读取正文和父子路径。
6. 向子页追加一段内容。
7. 再次 Fetch 子页，确认追加内容存在。

本地验证结果：

- 验证日期：2026-06-05
- 当前 Notion 用户：`ByctorH`
- 创建测试页成功：`notion-worklog 权限测试 2026-06-05`
- 创建子页成功：`2026-06-05 随手记测试`
- Fetch 读取成功。
- `insert_content` 追加内容成功。
- 再次 Fetch 已读到追加内容。

结论：当前 Codex Notion connector 已具备本项目需要的核心读写链路：搜索、创建页面、创建子页、读取页面、追加内容。

## 常见问题

### 搜不到 `工作随手记` 或 `工作报告`

可能原因：

- 根页面尚未创建。
- 页面名称不一致。
- 当前 Notion 连接没有该页面访问权限。
- 该页面在另一个 workspace 中。

处理方式：

1. 让 Skill 创建默认根页面。
2. 或明确告诉 Skill 使用哪个 Notion 页面作为根页面。
3. 如果使用传统 integration，把目标父页面分享给 integration。

### 可以创建页面，但不能更新页面

通常是连接缺少 `Update content` 能力，或目标页面权限不足。需要重新检查 Notion 连接授权或页面分享权限。

### 可以读，不能写

通常是连接只具备读取能力，或当前 AI app 的 Notion 连接被配置成只读。需要切换到支持写入的 Notion MCP / connector，或在 Notion / AI app 的连接设置中重新授权。
