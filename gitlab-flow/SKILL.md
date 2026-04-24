---
name: gitlab-flow
description: GitLab 工作流自动化 - 一键创建 issue、分支和 MR。当用户需要"创建 GitLab issue"、"启动开发工作流"、"准备功能开发"、"创建开发分支"、"初始化 GitLab 工作流"时使用此技能。支持自动化流程：创建 issue → 创建分支 → 创建 MR，全部分配给当前用户。快速调用：/gitlab-flow
allowed-tools: Bash, Skill
---

# GitLab 完整工作流工具

实现 GitLab 开发工作流：创建 Issue → 创建分支 → 创建 MR，自动关联和分配。

## 触发场景

- "创建 GitLab issue 和分支"
- "准备开发新功能"
- "创建 issue、分支和 MR"
- "启动开发工作流"
- "创建 fix_#594465_xxx 这样的工作流"

## Preflight

### Token 检查（每次调用前必须执行）

```bash
GITLAB_ACCESS_TOKEN="${GITLAB_ACCESS_TOKEN:-$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
export GITLAB_ACCESS_TOKEN
[ -n "$GITLAB_ACCESS_TOKEN" ] || { echo "MISSING: GITLAB_ACCESS_TOKEN"; exit 3; }
```

缺失时提示用户：前往 `https://gitlab.xylink.com/-/user_settings/personal_access_tokens` 创建 Personal Access Token（勾选 `api` 权限），将值告知后执行 `mkdir -p ~/.xyinfpilot` 并追加写入 `~/.xyinfpilot/.env`：`GITLAB_ACCESS_TOKEN=<token>`，然后继续执行。

### 依赖检查

```bash
command -v jq >/dev/null 2>&1 || { echo "MISSING: jq"; echo "安装: brew install jq"; exit 3; }
```

## 依赖声明

| 依赖 | 类型 | 说明 |
|------|------|------|
| `GITLAB_ACCESS_TOKEN` | 环境变量 | 存储于 `~/.xyinfpilot/.env`，配置方式同 `gitlab` skill |
| `jq` | 系统工具 | JSON 解析，安装：`brew install jq` |
| `gitlab` skill | 兄弟 skill | Token 配置参阅 `skills/gitlab/SKILL.md` |

## 执行策略

### 策略 A：自动化脚本（推荐）

适用场景：一键完成全部工作流，无需逐步干预。

```bash
bash ~/.claude/skills/gitlab-flow/scripts/create_workflow.sh \
  "fix_#594465_log_print_optimize" "private_v3.11" "优化日志打印"
```

脚本自动完成全部 7 步并输出彩色结果。脚本内部已包含 Token 检查和 jq 依赖检查。

### 策略 B：手动逐步执行

适用场景：逐步确认结果、脚本失败后重试某步骤。

手动执行前必须先完成上方 Preflight 检查，然后按照 [reference/commands.md](reference/commands.md) 中的命令模板逐步操作。

## 脚本工作流程（策略 A 内部步骤）

1. 获取项目信息（从 `git remote get-url origin` 推断）
2. 验证 GitLab Token
3. 获取当前用户信息
4. 创建 GitLab Issue
5. 创建远程分支（如不存在）
6. 创建本地分支并 track 远程分支
7. 创建 MR 并在描述中写入 `Closes #issue_iid`

## 错误处理

在任何步骤失败时：
1. 向用户报告具体失败步骤
2. 显示错误信息（API 响应）
3. 如果部分成功，提供已创建资源的链接
4. 建议用 [reference/commands.md](reference/commands.md) 中的命令手动完成剩余步骤

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `MISSING: GITLAB_ACCESS_TOKEN` | Token 未配置 | 执行 Preflight 中的配置步骤 |
| `MISSING: jq` | jq 未安装 | `brew install jq` |
| `401 Unauthorized` | Token 无效或过期 | 重新创建 token |
| `404 Project Not Found` | 项目路径错误 | 检查 `git remote -v` |
| `409 Branch already exists` | 分支已存在 | 使用不同的分支名或删除现有分支 |
| `400 Invalid reference` | 基础分支不存在 | 检查 `base_branch` 参数 |

## 注意事项

1. **分支命名**：分支名与 issue 标题保持一致，便于追踪
2. **自动关联**：MR 描述中使用 `Closes #issue_iid` 确保合并后自动关闭 issue
3. **权限检查**：确保 token 有 `api` 权限
4. **本地仓库**：确保在 git 仓库目录中执行

## 参考文档

- [reference/commands.md](reference/commands.md) — 手动执行工作流的完整 curl 命令模板
