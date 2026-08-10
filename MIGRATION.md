# Migration Map / 迁移映射

| Source / 来源 | Destination / 目标位置 | Migration method / 迁移方式 |
| --- | --- | --- |
| Local `frontend-ui-visual-gate` | [`skills/frontend-ui-visual-gate`](./skills/frontend-ui-visual-gate) | Copied from the installed, validated skill. / 从已安装且已验证的 skill 复制。 |
| Local `grill-me` | [`skills/grill-me`](./skills/grill-me) | Copied from the installed custom skill. / 从已安装的自定义 skill 复制。 |
| Local `hatch-pet` | [`skills/hatch-pet`](./skills/hatch-pet) | Copied with scripts, references, metadata, and license. / 连同脚本、参考资料、元数据和许可证复制。 |
| Local `notion-worklog` | [`skills/notion-worklog`](./skills/notion-worklog) | Copied from the installed custom skill. / 从已安装的自定义 skill 复制。 |
| `JaceHwang/tracking-project-progress` | [`projects/tracking-project-progress`](./projects/tracking-project-progress) | Git subtree with source history. / 使用保留源码历史的 Git subtree。 |
| `JaceHwang/codex-usage-sidebar` | [`plugins/codex-usage-sidebar`](./plugins/codex-usage-sidebar) (plugin package: [`plugins/codex-usage-sidebar/plugins/codex-usage-sidebar`](./plugins/codex-usage-sidebar/plugins/codex-usage-sidebar)) | Git subtree with source history. / 使用保留源码历史的 Git subtree。 |

The obsolete draft pull request in the forked `JaceHwang/skills` repository is intentionally not a source of record. Its `frontend-ui-visual-gate` content is migrated from the installed local skill and the draft PR is closed after this repository is validated.

fork 的 `JaceHwang/skills` 仓库中错误创建的 draft PR 不再作为权威来源。`frontend-ui-visual-gate` 以已安装的本地 skill 为准完成迁移；本仓库验证后会关闭该 draft PR。

## Post-migration normalization / 迁入后规范化

The `tracking-project-progress` subtree retains its upstream history. Seven inherited terminal blank lines were normalized after import so the monorepo passes `git diff --check`; this is a whitespace-only change with no behavioral impact.

`tracking-project-progress` 子树保留了上游提交历史。导入后规范化了 7 处继承的文件末尾空行，使总仓库通过 `git diff --check`；这只是空白字符调整，不影响行为。
