# Codex 工作流迁移

## 使用方式

在 Codex 中打开本仓库，并让其先阅读根目录 `AGENTS.md`。这些指引随 Git 文件生效，无需安装 Claude 或用 Claude 调用 Codex。

本次迁移增加 Codex 的项目入口；原始会话、成果和分支保留。GitHub 上的文件可以接续，但 Anthropic 云端会话状态、Claude 的 resume 列表、账号凭据和本机 MCP 配置不会自动导入 Codex。

## 接续既有分支

以下清单是 2026-11-14 检查时的来源快照。各分支可能包含 main 尚未合并的成果；不要只看 main 或批量合并所有分支。

| 来源分支 | 检查时提交 | 文件数 |
| --- | --- | --- |
| `claude/build-small-game-A3S9q` | `9948493f4b8d8fdb3a6149fad05838e1b11285d4` | 5 |

选择与用户当前任务匹配的来源分支，先查看差异，再以它为起点建立新的 Codex 工作分支：

```bash
git fetch origin
# 用上表实际分支替换 <来源分支>；用任务名称替换 <任务>
git switch -c codex/<任务> origin/<来源分支>
# 迁移 PR 合入 main 后，将 Codex 指引带入当前分支
git restore --source=origin/main -- AGENTS.md CODEX_MIGRATION.md
```

如果迁移 PR 尚未合入 main，应将最后一行的 `origin/main` 换成迁移 PR 的分支。检查本地同名文件与差异后再执行；已存在的指引应手动合并。项目源码继续使用来源分支的版本；按任务审阅后再通过 PR 合并。

## 兼容边界

- `.claude` 技能与 MCP 如有需要，应逐项检查依赖和工具能力后适配；历史技能导出包作为资料保存，不能仅改名便视为可运行。
- 本仓库扫描到的 main 与 Claude 来源分支未发现 `.claude/` 配置或 Claude 专属 GitHub Actions 工作流，因此没有替换自动触发器。
- 文档迁移不改变 Codex 账号级设置，也不自动创建或导入聊天。

## 本分支的接续来源

本 Codex 分支直接从 `claude/build-small-game-A3S9q`（`9948493f4b8d8fdb3a6149fad05838e1b11285d4`）建立，保留完整历史与全部项目文件，并增加 Codex 指引。原 Claude 来源分支保持原样。
