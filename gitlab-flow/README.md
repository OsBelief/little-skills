# GitLab Workflow Skill

GitLab 完整工作流工具，一键创建 issue、分支和 MR。

## 功能特性

- ✅ 自动创建 GitLab Issue
- ✅ 从基础分支创建新分支
- ✅ 本地自动创建并切换到新分支
- ✅ 自动创建 Merge Request
- ✅ MR 自动关联 Issue（合并后自动关闭）
- ✅ 所有资源自动分配给当前用户
- ✅ 彩色输出和友好的错误提示

## 安装

将此 skill 目录复制到你的 Claude Code skills 目录：

```bash
cp -r gitlab-workflow ~/.claude/skills/
```

## 使用方法

### 方式 1: 使用辅助脚本（推荐）

```bash
# 基本用法
cd /path/to/your/repo
~/.claude/skills/gitlab-workflow/scripts/create_workflow.sh \
  "fix_#594465_log_print_optimize" \
  "private_v3.11"

# 带描述
~/.claude/skills/gitlab-workflow/scripts/create_workflow.sh \
  "fix_#594465_log_print_optimize" \
  "private_v3.11" \
  "优化日志打印，提高代码可读性"
```

### 方式 2: 在 Claude Code 中使用

直接在对话中告诉 Claude 你的需求：

```
创建 GitLab 工作流：issue 标题为 fix_#594465_log_print_optimize，基于 private_v3.11 分支
```

Claude 会自动调用此 skill 并完成所有步骤。

## 前置要求

1. **GitLab Access Token**

   前往 https://gitlab.xylink.com/-/user_settings/personal_access_tokens 创建 token，需要勾选 `api` 权限。

2. **配置 Token**

   ```bash
   mkdir -p ~/.xyinfpilot
   echo 'GITLAB_ACCESS_TOKEN=your_token_here' >> ~/.xyinfpilot/.env
   ```

3. **Git 仓库**

   确保在 git 仓库中执行，脚本会自动从 `git remote get-url origin` 获取项目信息。

## 工作流程

```
开始
  ↓
检查环境（git 仓库、token、基础分支）
  ↓
获取项目信息和用户信息
  ↓
创建 GitLab Issue → 获得 Issue ID
  ↓
创建远程分支
  ↓
创建本地分支并切换
  ↓
创建 MR（描述中包含 "Closes #issue_id"）
  ↓
完成！返回 Issue 和 MR 链接
```

## 输出示例

```
ℹ 步骤 1/7: 获取项目信息...
ℹ 项目路径: AndroidClient/CallModule
ℹ 基础分支: private_v3.11

ℹ 步骤 2/7: 检查 GitLab Token...
ℹ 找到 GitLab Access Token

ℹ 步骤 3/7: 获取当前用户信息...
ℹ 当前用户: Cheng Zhenhua (@chengzhenhua)

ℹ 步骤 4/7: 创建 GitLab Issue...
ℹ Issue 创建成功: #12345
  链接: https://gitlab.xylink.com/AndroidClient/CallModule/-/issues/12345

ℹ 步骤 5/7: 创建新分支...
ℹ 分支创建成功: fix_#594465_log_print_optimize

ℹ 步骤 6/7: 本地创建并切换分支...
ℹ 本地分支创建成功: fix_#594465_log_print_optimize
ℹ 分支推送到远程

ℹ 步骤 7/7: 创建 Merge Request...
ℹ MR 创建成功: #67890

✓ 工作流创建完成

创建的资源：
  Issue:   #12345 - https://gitlab.xylink.com/AndroidClient/CallModule/-/issues/12345
  分支:    fix_#594465_log_print_optimize
  MR:      !67890 - https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67890

所有项目已分配给你，可以开始开发了！
```

## 错误处理

脚本会检查常见错误并提供清晰的错误信息：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `不在 git 仓库中` | 当前目录不是 git 仓库 | 切换到 git 仓库目录 |
| `找不到 git remote origin` | 未配置 git remote | 配置 `git remote add origin` |
| `未找到 GITLAB_ACCESS_TOKEN` | Token 未配置 | 按照前置要求配置 token |
| `基础分支不存在` | 指定的基础分支在远程不存在 | 检查分支名是否正确 |
| `创建 Issue 失败` | Token 权限不足或项目不存在 | 检查 token 权限和项目路径 |
| `分支已存在` | 分支名已被使用 | 使用不同的分支名或删除现有分支 |

## 分支命名规范

建议遵循以下命名规范：

- **Bug 修复**: `fix_#<issue_number>_<description>`
  - 例如: `fix_#594465_log_print_optimize`

- **新功能**: `feat_#<issue_number>_<description>`
  - 例如: `feat_#600000_add_user_profile`

- **重构**: `refactor_#<issue_number>_<description>`
  - 例如: `refactor_#601000_cleanup_code`

- **文档**: `docs_#<issue_number>_<description>`
  - 例如: `docs_#602000_update_readme`

## 注意事项

1. **MR 关联 Issue**: MR 描述中使用 "Closes #issue_id"，这样当 MR 合并后会自动关闭 Issue
2. **权限要求**: Token 需要 `api` 权限，用户需要项目的 Developer 或更高角色
3. **分支推送**: 脚本会自动推送分支到远程
4. **重复执行**: 如果 issue/分支/MR 已存在，脚本会跳过创建步骤

## 技术细节

- 使用 GitLab API v4
- 依赖 `curl` 和 `jq` 工具
- 支持私有化部署的 GitLab（https://gitlab.xylink.com）
- 自动从 git remote 推断项目路径

## License

MIT
