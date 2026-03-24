---
name: commit-review
description: 智能化 Git commit 创建和代码 review 工具。当用户需要创建 Git commit、进行代码审查、提交代码时使用。支持从分支名自动提取 issue ID 和 commit 类型，生成符合规范的 commit message。适用于所有 Git 仓库的提交和审查场景。每当用户提到 git commit、提交代码、commit review、smart-commit 时都应该使用此 skill。
---

# Git Commit Review

这个 skill 帮助你创建符合规范的 Git commit message，并对代码变更进行 review。

## 从分支名提取信息

Git 分支名通常遵循以下格式：
```
<type>_<id>_<description>
```

例如：`fix_#596754_cloud_config_default_layout_1`

- **type** (类型): fix, feat, refactor, docs, test, chore 等
- **id** (问题 ID): #596754 或其他 issue/MR 编号

## Commit Message 格式

生成的 commit message 必须遵循以下格式：

```
<type>: <description> [<id>]
```

例如：
```
fix: cloud config default layout [#596754]
```

### 规则

1. **类型（type）**：必须从分支名中提取
   - `fix` - 修复 bug
   - `feat` - 新功能
   - `refactor` - 重构
   - `docs` - 文档变更
   - `test` - 测试相关
   - `chore` - 构建/工具链相关
   - `style` - 代码格式（不影响代码运行的变动）
   - `perf` - 性能优化
   - 其他自定义类型

2. **描述（description）**：
   - 最多 **20 个单词**
   - 使用英文
   - 使用现在时态（"add" 而不是 "added"）
   - 首字母小写
   - 不要以句号结尾

3. **ID（id）**：
   - 必须从分支名中提取
   - 格式：[#596754] 或 [#596754]
   - **默认值**：如果提取不到 ID，使用 `#0`

4. **类型的默认值**：
   - **默认值**：如果提取不到类型，使用 `fix`

## 工作流程

### 1. 获取当前分支名

使用 `git rev-parse --abbrev-ref HEAD` 获取当前分支名。

### 2. 解析分支名

从分支名中提取类型和 ID：

**提取规则**：
- 类型（第一个下划线之前的部分）
  - 如果提取不到，默认使用 `fix`
- ID（第一个以 # 开头的部分）
  - 如果提取不到，默认使用 `#0`

**示例解析：**

**示例 1：标准格式**
分支名：`fix_#596754_cloud_config_default_layout_1`
- 类型：`fix`
- ID：`#596754`

**示例 2：无 ID**
分支名：`fix_add_user_authentication`
- 类型：`fix`
- ID：`#0`（默认值）

**示例 3：无类型**
分支名：`#123456_add_feature`
- 类型：`fix`（默认值）
- ID：`#123456`

**示例 4：无类型和 ID**
分支名：`master` 或 `main` 或 `develop`
- 类型：`fix`（默认值）
- ID：`#0`（默认值）

**示例 5：完整格式**
分支名：`feature_#123456_add_user_authentication`
- 类型：`feature`
- ID：`#123456`

### 3. 分析代码变更并生成描述

**关键原则**：描述必须根据实际的代码变更来总结，而不是从分支名提取。

**步骤：**

1. **查看代码差异**：
   - 运行 `git diff --staged` 查看已暂存的变更
   - 如果没有暂存的变更，运行 `git diff` 查看工作区的变更
   - 分析变更的文件、函数、逻辑

2. **生成描述**：
   - 阅读代码差异，理解实际做了什么修改
   - 生成简洁的英文描述，说明变更的核心内容
   - 限制在 **20 个单词**以内
   - 使用现在时态（"add" 而不是 "added"）
   - 首字母小写，不要以句号结尾

3. **描述生成指南**：
   - **添加新功能**：add [what feature]
   - **修复 bug**：fix [what problem]
   - **重构**：refactor [what part]
   - **性能优化**：optimize [what]
   - **文档更新**：update [what documentation]
   - **删除代码**：remove [what]
   - **移动代码**：move [what] to [where]

**选项 A：使用用户提供的描述**
如果用户提供了自定义描述，直接使用用户的描述（但仍然要检查是否符合20个单词的限制）。

**选项 B：自动生成描述**
如果用户没有提供描述，根据代码变更自动生成描述。

**示例：**

**场景 1：用户未提供描述**
- 分支：`fix_#596754_cloud_config_default_layout_1`
- 代码变更：修改了 LayoutManager.java，添加了默认布局配置
- 分析代码：添加了对多屏内容的默认布局配置
- 生成描述：`add default layout config for multi-screen content`
- 最终 commit message：`fix: add default layout config for multi-screen content [#596754]`

**场景 2：用户提供描述**
- 分支：`fix_#596754_cloud_config_default_layout_1`
- 用户描述："fix default layout issue in cloud config scenario"
- 最终 commit message：`fix: fix default layout issue in cloud config scenario [#596754]`

**场景 3：删除冗余代码**
- 代码变更：删除了 onCloudConfigChanged 方法中重复的布局配置代码
- 分析代码：移除重复的配置设置
- 生成描述：`remove duplicate layout configuration code`
- 最终 commit message：`refactor: remove duplicate layout configuration code [#596754]`

**场景 4：使用默认值（无 ID）**
- 分支：`fix_add_user_authentication`
- 类型：`fix`
- ID：`#0`（默认值）
- 描述：`add user authentication`
- 最终 commit message：`fix: add user authentication [#0]`

**场景 5：使用默认值（无类型和 ID）**
- 分支：`master`
- 类型：`fix`（默认值）
- ID：`#0`（默认值）
- 描述：`update configuration`
- 最终 commit message：`fix: update configuration [#0]`

### 4. 检查代码变更

在创建 commit 之前，检查代码变更：
1. 运行 `git status` 查看未跟踪文件和修改
2. 运行 `git diff --staged` 查看已暂存的变更
3. 运行 `git diff` 查看未暂存的变更
4. 确认要提交的文件

**重要**：只提交相关的文件。不要提交：
- `.env` 或其他包含敏感信息的文件
- 临时文件
- 二进制文件（除非必要）
- 不相关的文件

### 5. 创建 Commit

1. **添加文件**：
   - 如果用户指定了文件，只添加这些文件
   - 如果没有指定，询问用户要提交哪些文件，或者使用 `git add -A` 添加所有变更

2. **创建 commit**：
   使用 HEREDOC 格式确保 commit message 格式正确：
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>: <description> [<id>]

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```

3. **验证**：
   运行 `git log -1` 查看 commit 是否成功创建

## Commit Review

### 检查清单

在创建 commit 后，进行以下检查：

1. **格式检查**：
   - [ ] Commit message 格式正确：`<type>: <description> [<id>]`
   - [ ] 类型是有效的 commit 类型
   - [ ] 描述在 20 个单词以内
   - [ ] ID 格式正确（包含 #）

2. **内容检查**：
   - [ ] 提交的文件与 commit message 相关
   - [ ] 没有提交敏感信息
   - [ ] 没有提交不必要的文件
   - [ ] 代码变更符合预期

3. **最佳实践**：
   - [ ] Commit message 清晰描述了变更内容
   - [ ] 一个 commit 只做一件事
   - [ ] 没有破坏性变更（如果有，应该在 message 中说明）

### Review 输出格式

向用户展示 review 结果：

```
✅ Commit Message 格式检查通过
✅ 提交内容验证通过
✅ 最佳实践检查通过

Commit 信息：
- 类型: fix
- 描述: move multi-screen layout config to initialization
- ID: #596754
- 完整 message: fix: move multi-screen layout config to initialization [#596754]

提交的文件：
- call/src/main/java/com/xylink/call/layout/LayoutManager.java

代码变更摘要：
- 添加 TWO_SCREEN_CONTENT、THREE_SCREEN_PEOPLE、THREE_SCREEN_CONTENT 的默认布局配置
- 移除 onCloudConfigChanged 方法中的重复配置代码

📝 建议: <如果有改进建议>
```

## 错误处理

如果遇到以下情况，向用户报告并请求确认：

1. **分支名格式不正确**：
   - 无法从分支名提取类型或 ID
   - 提示用户手动输入类型和 ID

2. **描述超过 20 个单词**：
   - 截断描述并显示截断后的版本
   - 询问用户是否接受

3. **没有变更可提交**：
   - 提示用户当前没有变更需要提交

4. **暂存区为空**：
   - 提示用户需要先 `git add` 文件
   - 或者使用 `git add -A` 添加所有变更

## 使用示例

### 示例 1：基本用法（自动生成描述）

用户说："创建 commit"

操作：
1. 获取分支名：`fix_#596754_cloud_config_default_layout_1`
2. 提取信息：type=`fix`, id=`#596754`
3. 查看代码变更：`git diff --staged`
4. 分析变更：LayoutManager.java 中添加了多屏内容的默认布局配置
5. 生成描述：`add default layout config for multi-screen content`
6. 最终 commit message：`fix: add default layout config for multi-screen content [#596754]`
7. 创建 commit
8. Review 并输出结果

### 示例 2：自定义描述

用户说："创建 commit，描述是'fix default layout issue in layout manager'"

操作：
1. 获取分支名：`fix_#596754_cloud_config_default_layout_1`
2. 提取信息：type=`fix`, id=`#596754`
3. 使用用户描述：`fix default layout issue in layout manager`
4. 最终 commit message：`fix: fix default layout issue in layout manager [#596754]`
5. 创建 commit
6. Review 并输出结果

### 示例 3：指定文件

用户说："只提交 LayoutManager.java 文件"

操作：
1. 获取分支名：`fix_#596754_cloud_config_default_layout_1`
2. 提取信息：type=`fix`, id=`#596754`
3. 只添加 `LayoutManager.java`：`git add LayoutManager.java`
4. 查看该文件的代码变更
5. 分析并生成描述
6. 生成 commit message：`fix: <根据代码变更生成的描述> [#596754]`
7. 创建 commit
8. Review 并输出结果

## 命令触发词

当用户使用以下命令或短语时，应该触发此 skill：
- `/git-commit`
- `/commit-review`
- `/smart-commit`
- "创建 commit"
- "提交代码"
- "git commit"
- "提交"
- "代码审查"
- "commit review"

## 注意事项

1. **始终使用中文回复用户**
2. **在执行任何 git 操作前，先向用户展示将要执行的命令**
3. **在创建 commit 前，展示完整的 commit message 供用户确认**
4. **如果用户不满意，允许修改后再提交**
5. **不要自动 push，除非用户明确要求**
6. **在提交前检查是否有 pre-commit hook，如果有，告知用户**
