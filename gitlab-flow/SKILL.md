---
name: gitlab-flow
description: GitLab 工作流自动化 - 一键创建 issue、分支和 MR。当用户需要"创建 GitLab issue"、"启动开发工作流"、"准备功能开发"、"创建开发分支"、"初始化 GitLab 工作流"时使用此技能。支持自动化流程：创建 issue → 创建分支 → 创建 MR，全部分配给当前用户。快速调用：/gitlab-flow
allowed-tools: Bash, Skill
---

# GitLab 完整工作流工具

这个 skill 实现了 GitLab 的完整开发工作流：创建 Issue → 创建分支 → 创建 MR，并自动关联和分配。

## 触发场景

当用户提到以下需求时使用此 skill：
- "创建 GitLab issue 和分支"
- "准备开发新功能"
- "创建 issue、分支和 MR"
- "启动开发工作流"
- "创建 fix_#594465_xxx 这样的工作流"

## 工作流程

**推荐做法：使用辅助脚本**

此 skill 提供了一个自动化脚本 `scripts/create_workflow.sh`，它可以一次性完成整个工作流。使用方法：

```bash
# 基本用法
./scripts/create_workflow.sh <issue_title> <base_branch> [issue_description]

# 示例
./scripts/create_workflow.sh "fix_#594465_log_print_optimize" "private_v3.11"
./scripts/create_workflow.sh "fix_#594465_log_print_optimize" "private_v3.11" "优化日志打印"
```

这个脚本会自动完成所有步骤并提供彩色输出和错误处理。

**手动执行步骤**

如果需要手动控制每个步骤，可以按照以下流程：

### 步骤 1: 收集必要信息

在开始工作流之前,需要确认以下信息：

**必需参数：**
- `issue_title` - Issue 标题（格式如：`fix_#594465_log_print_optimize`）
- `base_branch` - 基础分支名称（如：`private_v3.11`）

**可选参数：**
- `issue_description` - Issue 描述（默认为"自动创建的工作流 issue"）

### 步骤 2: 检查环境

脚本会自动检查：
- 是否在 git 仓库中
- GitLab Token 是否可用
- 基础分支是否存在

### 步骤 3: 执行工作流

脚本会按顺序执行：
1. 获取项目信息（从 git remote）
2. 验证 GitLab Token
3. 获取当前用户信息
4. 创建 GitLab Issue
5. 创建远程分支
6. 创建本地分支并切换
7. 创建 Merge Request 并关联 Issue

### 步骤 4: 返回结果

脚本会输出：
- Issue 链接和 ID
- 分支名称
- MR 链接和 ID
- 所有资源已分配给当前用户

## 错误处理

在任何步骤失败时：
1. 向用户报告具体失败步骤
2. 显示错误信息（API 响应）
3. 如果部分成功，提供已创建资源的链接
4. 建议用户手动完成剩余步骤

## 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `401 Unauthorized` | Token 无效或过期 | 重新创建 token |
| `404 Project Not Found` | 项目路径错误 | 检查 `git remote -v` |
| `409 Branch already exists` | 分支已存在 | 使用不同的分支名或删除现有分支 |
| `400 Invalid reference` | 基础分支不存在 | 检查 `base_branch` 参数 |

## 使用示例

**示例 1: 基本用法**
```
用户: 创建工作流 fix_#594465_log_print_optimize，基于 private_v3.11 分支

步骤：
1. 从当前仓库推断项目 ID
2. 创建 issue "fix_#594465_log_print_optimize"
3. 从 private_v3.11 创建分支 "fix_#594465_log_print_optimize"
4. 创建 MR → private_v3.11
5. 返回 issue 和 MR 链接
```

**示例 2: 带描述**
```
用户: 创建 issue fix_#594465_xxx，基于 master，描述是"优化日志打印"

额外步骤：
- 在创建 issue 时使用提供的描述
- 其余流程相同
```

## 注意事项

1. **分支命名**：分支名与 issue 标题保持一致，便于追踪
2. **自动关联**：MR 描述中使用 "Closes #issue_iid" 确保合并后自动关闭 issue
3. **权限检查**：确保 token 有 `api` 权限（创建 issue/MR 需要）
4. **项目访问**：确保用户有项目访问权限（Developer 或更高角色）
5. **本地仓库**：确保在 git 仓库目录中执行，以便推断项目信息

## API 端点参考

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取当前用户 | GET | `/user` |
| 创建 Issue | POST | `/projects/:id/issues` |
| 创建分支 | POST | `/projects/:id/repository/branches` |
| 创建 MR | POST | `/projects/:id/merge_requests` |
