# 项目进展看板

[English](README.md) | 简体中文

这是一个可移植的 Agent Skill 和 Claude Code 插件，为代码开发智能体提供持久化、项目本地的进展看板。它专门解决长时间开发被中断后，新模型必须重新梳理项目现状这一棘手问题。

看板只记录继续开发所必需的状态：目标、当前重点、任务状态、技术决策、变更文件、验证证据、阻塞项，以及一个明确可执行的下一步操作。

## 为什么需要它

对话历史并不是可靠的项目数据库。上下文可能被压缩、分散在多个会话中，或者下一个智能体根本无法访问。Git 能保存代码变更，却无法说明当前正在落实哪项需求、哪些内容仍未验证，以及当初为什么做出某个技术选择。

本项目增加了一个轻量的恢复层，但不会取代 Git、问题跟踪系统或实施计划。

## 功能特性

- 可移植的 [Agent Skills](https://agentskills.io/specification) 软件包
- 可从代码开发、缺陷修复、重构、迁移、恢复进度和工作交接等请求中自动发现
- 经过测试、仅使用 Python 标准库的看板命令行工具
- 由机器可读 JSON 支撑的人类可读 Markdown 看板
- 原子化、带锁保护并具有修订版本的状态更新
- 仅追加写入的事件历史记录
- Claude Code 生命周期钩子：
  - 会话开始时注入已有看板上下文；
  - 成功修改源代码后初始化看板并记录变更；
  - 代码变更回合结束前要求创建检查点
- 不发起网络请求，不收集遥测数据，不依赖托管服务，也不会在运行时安装依赖

## 看板文件

该 Skill 会在目标代码仓库中创建以下文件：

```text
.project-board/
├── state.json    # 机器可读的唯一事实来源
├── board.md      # 供人阅读的渲染后看板
└── events.jsonl  # 仅追加写入的修订审计记录
```

如果团队需要共享开发连续性，可以提交这个目录；如果看板只用于本地工作，也可以将其加入项目自己的 `.gitignore`。

## 安装

### Agent Skills 客户端

使用社区提供的 `skills` 安装器安装可移植 Skill：

```bash
npx skills add https://github.com/Byctor/tracking-project-progress --skill tracking-project-progress
```

出现提示时，选择需要支持的智能体以及用户级或项目级安装范围。

### Claude Code 插件市场

在 Claude Code 中运行以下命令：

```text
/plugin marketplace add Byctor/tracking-project-progress
/plugin install tracking-project-progress@tracking-project-progress
```

更新钩子文件后，请重启 Claude Code 或运行 `/reload-plugins`。

### Claude Code 开发检出

```bash
git clone https://github.com/Byctor/tracking-project-progress.git
claude --plugin-dir ./tracking-project-progress
```

安装后的 Skill 可通过 `/tracking-project-progress:tracking-project-progress` 调用；当其描述与当前开发任务匹配时，Claude 也可能自动加载它。

## 使用方式

让智能体开始或恢复一项非简单的代码开发任务。Skill 会解析其内置命令行工具，并按照以下生命周期工作：

1. 恢复已有看板，或根据用户的真实目标初始化看板；
2. 结合 Git 状态、差异和聚焦测试核对看板内容；
3. 始终只保持一项小任务处于进行中；
4. 记录有意义的变更文件和准确的验证结果；
5. 在检查点保存事实性摘要和一个可执行的下一步操作。

也支持手动调用：

```text
使用 tracking-project-progress 恢复此代码仓库的进展，并继续当前实现。
```

## 命令行工具

Skill 会指示智能体运行内置工具；维护者也可以直接运行它：

```bash
python3 skills/tracking-project-progress/scripts/project_board.py --help
```

核心命令：

| 命令 | 用途 |
| --- | --- |
| `ensure` | 创建看板或完善其目标 |
| `resume` | 输出紧凑的恢复信息包 |
| `task-add` | 使用稳定的标识符添加任务 |
| `task-update` | 更新任务状态或备注 |
| `record-file` | 记录变更文件并要求创建检查点 |
| `checkpoint` | 保存摘要、重点、下一步、证据和决策 |
| `validate` | 校验数据结构和不变量 |
| `render` | 根据 `state.json` 重新生成 `board.md` |

示例：

```bash
CLI="skills/tracking-project-progress/scripts/project_board.py"

python3 "$CLI" ensure \
  --objective "添加令牌刷新功能及回归测试" \
  --project-root "$PWD"

python3 "$CLI" checkpoint \
  --summary "刷新解析器已实现，聚焦测试通过" \
  --focus "身份验证回归测试" \
  --next "运行完整的身份验证测试套件" \
  --verification "python3 -m unittest tests.test_refresh::pass（4 项测试）" \
  --project-root "$PWD"
```

## 可移植性

核心部分遵循开放的 Agent Skills 目录格式，并且只使用 Python 标准库。Claude Code 钩子属于可选适配层；不支持生命周期钩子的智能体，会根据 `SKILL.md` 遵循相同的启动、工作、验证和检查点规则。

本项目采用的平台概念可参考 Anthropic 的 [Agent Skills 概览](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)、[编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)和 [Claude Code 插件指南](https://code.claude.com/docs/en/plugins)。

## 安全与隐私

- 本项目不会发起网络请求，也不会发送遥测数据。
- 看板会在目标代码仓库中保存路径、摘要、决策和测试命令。请勿在检查点文本中写入密钥或凭据。
- 损坏或版本不受支持的状态会被保留，而不是被覆盖。
- 该 Skill 不会授予提交代码、推送分支、创建问题或联系外部服务的权限。
- 安装第三方 Skill 前应像审查软件一样进行检查；Skill 指令和脚本会使用智能体已有的权限执行。

## 局限性

- 可移植的 Agent Skills 无法保证生命周期操作一定执行。Claude Code 插件钩子能够提供更强的自动化保障。
- 0.1 版本不提供托管界面、GitHub Projects 同步或 IDE 面板。
- 每个 Git 工作树维护一个看板。
- 并发更新会在本地串行执行；不同机器之间的语义合并不属于当前版本范围。

## 开发

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts skills/tracking-project-progress/scripts
uvx --python 3.11 --from skills-ref agentskills validate skills/tracking-project-progress
claude plugin validate . --strict
```

行为评估提示词和保留的基线结果位于 [`evals/`](evals/) 目录。

## 许可证

本项目使用 Apache-2.0 许可证，详见 [`LICENSE`](LICENSE)。
