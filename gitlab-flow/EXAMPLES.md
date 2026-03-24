# GitLab Workflow Skill 使用示例

本文档展示了如何在实际工作中使用 gitlab-workflow skill。

## 示例场景

### 场景 1: 修复 Bug

**用户需求**: 修复日志打印优化的问题

**对话示例**:
```
用户: 创建 GitLab 工作流：fix_#594465_log_print_optimize，基于 private_v3.11 分支

Claude: 好的，我来为你创建完整的 GitLab 工作流。

[执行脚本...]

✓ 工作流创建完成

创建的资源：
  Issue:   #12345 - https://gitlab.xylink.com/AndroidClient/CallModule/-/issues/12345
  分支:    fix_#594465_log_print_optimize
  MR:      !67890 - https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67890

所有项目已分配给你，可以开始开发了！
```

### 场景 2: 开发新功能

**用户需求**: 添加新的用户配置功能

**对话示例**:
```
用户: 准备开发新功能，创建 issue feat_#600000_user_config，从 master 分支创建，描述是"添加用户自定义配置功能"

Claude: 好的，我来创建这个开发工作流。

[执行脚本...]

✓ 工作流创建完成

创建的资源：
  Issue:   #12346 - https://gitlab.xylink.com/AndroidClient/CallModule/-/issues/12346
  分支:    feat_#600000_user_config
  MR:      !67891 - https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67891

所有项目已分配给你，可以开始开发了！
```

### 场景 3: 代码重构

**用户需求**: 重构视频处理模块

**对话示例**:
```
用户: 一键创建 GitLab 工作流，issue 标题 refactor_#601000_video_cleanup，基础分支是 develop

Claude: 好的，我来为你创建重构工作流。

[执行脚本...]

✓ 工作流创建完成

创建的资源：
  Issue:   #12347 - https://gitlab.xylink.com/AndroidClient/CallModule/-/issues/12347
  分支:    refactor_#601000_video_cleanup
  MR:      !67892 - https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67892

所有项目已分配给你，可以开始开发了！
```

## 实际使用流程

### 完整开发流程示例

```bash
# 1. 开始新任务
cd /path/to/CallModule

# 2. 让 Claude 创建工作流
# 对话: "创建 GitLab 工作流：fix_#594465_log_print_optimize，基于 private_v3.11"

# 3. Claude 自动执行以下操作：
#    - 创建 issue: #12345
#    - 创建远程分支: fix_#594465_log_print_optimize
#    - 创建本地分支并切换
#    - 创建 MR: !67890

# 4. 开始开发
git status  # 已经在新分支上了
# ... 进行代码修改 ...

# 5. 提交代码
git add .
git commit -m "fix: optimize log print for better readability"

# 6. 推送到远程
git push  # 分支已经在远程了，直接 push 即可

# 7. 在 GitLab 上查看 MR
# 链接: https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67890

# 8. 请求代码审查
# 在 MR 页面分配给审查者

# 9. 审查通过后合并 MR
# 合并后 issue 会自动关闭（因为 MR 描述包含 "Closes #12345"）
```

## 常用命令

### 查看工作流状态

```bash
# 查看当前分支
git branch --show-current

# 查看 issue 列表
# GitLab Web: https://gitlab.xylink.com/AndroidClient/CallModule/-/issues

# 查看 MR 列表
# GitLab Web: https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests
```

### 切换工作流

```bash
# 切换到主分支
git checkout private_v3.11

# 切换回工作分支
git checkout fix_#594465_log_print_optimize
```

## 最佳实践

### 1. Issue 标题命名

遵循约定式提交规范：

```bash
# Bug 修复
fix_#<issue_number>_<description>

# 新功能
feat_#<issue_number>_<description>

# 重构
refactor_#<issue_number>_<description>

# 文档
docs_#<issue_number>_<description>

# 测试
test_#<issue_number>_<description>

# 性能优化
perf_#<issue_number>_<description>
```

### 2. Commit 消息规范

```bash
# 格式
<type>: <description>

# 示例
fix: optimize log print for better readability
feat: add user configuration support
refactor: cleanup video processing module
docs: update API documentation
```

### 3. MR 描述模板

虽然脚本会自动创建基本的 MR 描述，但你可以在创建后编辑添加更多信息：

```markdown
## 功能描述
简要描述这个 MR 做了什么

## 修改内容
- 修改点 1
- 修改点 2
- 修改点 3

## 测试
- 测试场景 1
- 测试场景 2

## 截图（如果有）
[上传截图]

## Checklist
- [ ] 代码已通过本地测试
- [ ] 代码符合项目规范
- [ ] 已更新相关文档
- [ ] 无合并冲突

Closes #<issue_id>
```

### 4. 分支管理

```bash
# 开发完成后，如果 MR 被拒绝需要继续修改
git add .
git commit -m "fix: address review comments"
git push

# 如果 MR 合并后需要清理本地分支
git checkout private_v3.11
git branch -d fix_#594465_log_print_optimize  # 删除本地分支
# 远程分支会在 MR 合并时自动删除（如果设置了 remove_source_branch）
```

## 团队协作

### 分配审查者

在 MR 创建后：

1. 访问 MR 链接
2. 在右侧侧边栏找到 "Reviewers"
3. 点击 "Assign reviewer"
4. 选择审查者

### 请求审查

在团队聊天工具中（如 Slack、钉钉）：

```
@reviewer_name 请审查 MR: !67890
链接: https://gitlab.xylink.com/AndroidClient/CallModule/-/merge_requests/67890
描述: 修复日志打印优化问题
```

### 处理审查意见

```bash
# 获取最新代码
git fetch origin
git rebase origin/private_v3.11

# 修改代码
# ... 进行修改 ...

# 提交修改
git add .
git commit -m "fix: address review comments"

# 推送到远程
git push
```

## 常见问题

### Q1: 如果创建的 issue 不符合要求怎么办？

A: 直接在 GitLab 上编辑 issue，修改标题和描述。

### Q2: 如果分支名有误怎么办？

A: 删除本地和远程分支，重新创建工作流：

```bash
git checkout private_v3.11
git branch -D wrong_branch_name
git push origin --delete wrong_branch_name
```

### Q3: 如果 MR 创建失败怎么办？

A: 可以在 GitLab Web UI 手动创建 MR：
1. 访问项目的 "Merge Requests" 页面
2. 点击 "New merge request"
3. 选择源分支和目标分支
4. 在描述中添加 `Closes #<issue_id>`

### Q4: 如何批量创建多个工作流？

A: 可以创建一个 shell 脚本：

```bash
#!/bin/bash
WORKFLOWS=(
  "fix_#594465_log_print_optimize:private_v3.11"
  "fix_#594466_audio_bug:private_v3.11"
  "feat_#600000_new_feature:master"
)

for workflow in "${WORKFLOWS[@]}"; do
  IFS=':' read -r title base <<< "$workflow"
  ~/.claude/skills/gitlab-workflow/scripts/create_workflow.sh "$title" "$base"
done
```

## 总结

使用 gitlab-workflow skill 可以：

1. ✅ **节省时间** - 自动化重复性工作
2. ✅ **减少错误** - 避免手动操作的遗漏
3. ✅ **保持一致性** - 统一的命名和流程
4. ✅ **自动关联** - Issue 和 MR 自动关联
5. ✅ **提高效率** - 一键启动开发工作流

让开发者专注于代码本身，而不是繁琐的项目管理操作。
