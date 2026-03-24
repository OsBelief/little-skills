---
name: jenkins-build-trigger
description: Jenkins CI/CD build trigger for remotely triggering Jenkins job builds via API. Use when user needs to trigger Jenkins builds for specific projects and branches. Supports multi-level job paths (e.g. /job/project/job/branch/), handles CSRF Crumb authentication automatically, and provides build status URLs. Common triggers include trigger Jenkins build, start Jenkins job, deploy to environment, build project branch, compile project, or any reference to triggering/starting/launching Jenkins jobs.
---

# Jenkins Build Trigger

通过 Jenkins API 远程触发项目构建的自动化工具。

## 快速开始

### 基本用法

```bash
# 触发指定项目和分支的构建
trigger_build.sh --project becky --branch private_v3.11

# 使用完整 Job 路径
trigger_build.sh --job-path "job/becky/job/private_v3.11"

# 自定义 Jenkins 服务器
trigger_build.sh --url http://jenkins.company.com:8080 --project myproject --branch main
```

### 典型场景

**场景 1: 触发开发环境构建**
```bash
trigger_build.sh --project myapp --branch develop
```

**场景 2: 触发特定版本的构建**
```bash
trigger_build.sh --job-path "job/myapp/job/release-1.0"
```

**场景 3: 延迟触发（用于队列控制）**
```bash
trigger_build.sh --project myapp --branch main --delay 5sec
```

## 工作流程

脚本自动执行以下步骤：

1. **解析参数** - 支持 `--job-path` 或 `--project` + `--branch` 两种方式指定 Job
2. **获取 CSRF Crumb** - 从 Jenkins 获取防跨站请求伪造 Token
3. **发送构建请求** - 使用 Cookie 会话和 Crumb 触发构建
4. **返回结果** - 显示构建状态和查看链接

## 参数说明

| 参数 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `--url` | 否 | Jenkins 服务器地址 | `http://10.0.0.60:8080` |
| `--job-path` | 是* | 完整 Job 路径 | - |
| `--project` | 是* | 项目名称 | - |
| `--branch` | 是* | 分支名称 | - |
| `--delay` | 否 | 延迟启动时间 | `0sec` |

*注: `--job-path` 与 `--project`+`--branch` 二选一

## Job 路径规则

Jenkins 支持多级 Job 组织结构：

### 单级 Job
```
job/my-project/
```
触发方式:
```bash
trigger_build.sh --project my-project --branch master
```

### 多级 Job（常见于多分支项目）
```
job/my-project/job/feature-branch/
```
触发方式:
```bash
trigger_build.sh --project my-project --branch feature-branch
# 或
trigger_build.sh --job-path "job/my-project/job/feature-branch"
```

### 三级 Job（组织内的项目）
```
job/organization/job/team/job/project/
```
触发方式:
```bash
trigger_build.sh --job-path "job/organization/job/team/job/project"
```

## 环境变量

可通过环境变量设置默认值：

```bash
# 设置默认 Jenkins URL
export JENKINS_URL="http://jenkins.example.com:8080"

# 然后可以省略 --url 参数
trigger_build.sh --project myapp --branch main
```

## 认证说明

当前版本支持：
- ✅ 匿名访问（Jenkins 未启用认证）
- ✅ CSRF 保护（自动处理 Crumb）

如需**用户名/密码认证**，请修改脚本添加：

```bash
# 在 curl 命令中添加认证
-u "$JENKINS_USER:$JENKINS_TOKEN"
```

## 输出信息

成功触发后，脚本会返回：

```
✅ 构建触发成功！

📊 查看构建状态:
  - 构建页面: http://jenkins/job/project/job/branch/
  - 构建历史: http://jenkins/job/project/job/branch/builds
  - 控制台日志: http://jenkins/job/project/job/branch/lastBuild/console
```

## 错误处理

### HTTP 403 - 认证失败

**原因:**
- Jenkins 启用了认证但未提供凭据
- 用户无权触发该 Job
- CSRF Token 无效

**解决:**
- 浏览器登录后手动触发
- 配置 API Token 并更新脚本

### HTTP 404 - Job 不存在

**原因:**
- Job 路径错误
- Job 未创建或已删除

**解决:**
- 检查 Job 路径拼写
- 在 Jenkins UI 确认 Job 存在

### 连接超时

**原因:**
- 网络不可达
- Jenkins 服务未运行
- 防火墙阻止

**解决:**
- 检查网络连接
- 确认 Jenkins 服务状态
- 检查防火墙规则

## 集成示例

### 在 CI/CD 脚本中使用

```bash
#!/bin/bash
# deploy.sh

DEPLOY_PROJECT=$1
DEPLOY_BRANCH=$2

echo "🚀 开始部署: $DEPLOY_PROJECT/$DEPLOY_BRANCH"

# 触发 Jenkins 构建（使用相对于 skill 目录的路径）
./scripts/trigger_build.sh \
    --project "$DEPLOY_PROJECT" \
    --branch "$DEPLOY_BRANCH"

if [ $? -eq 0 ]; then
    echo "✅ 部署触发成功"
else
    echo "❌ 部署触发失败"
    exit 1
fi
```

### 批量触发多个项目

```bash
#!/bin/bash
# batch-build.sh

PROJECTS=("becky" "webapp" "api")
BRANCH="private_v3.11"

for project in "${PROJECTS[@]}"; do
    echo "📦 触发 $project 构建..."
    trigger_build.sh --project "$project" --branch "$BRANCH"
done
```

## 故障排除

### 1. Crumb 获取失败

如果看到 `⚠️ 警告: 无法获取 Crumb`，说明 Jenkins 可能：
- 禁用了 CSRF 保护（可忽略警告）
- 需要认证（需配置凭据）

### 2. 构建未在 UI 显示

可能原因：
- 构建在队列中等待
- Job 配置了安静期
- 上一个构建仍在运行

检查方式：访问 `Build History` 查看队列状态

### 3. 权限问题

确保当前用户：
- 对 Job 有 `Build` 权限
- 对 Job 所在文件夹有 `Read` 权限
- 如果是匿名访问，确保 Job 未设置为"需要认证"

## 最佳实践

1. **使用环境变量管理多环境**
   ```bash
   export JENKINS_URL="http://prod-jenkins:8080"  # 生产环境
   export JENKINS_URL="http://test-jenkins:8080"  # 测试环境
   ```

2. **日志记录**
   ```bash
   trigger_build.sh --project myapp --branch main 2>&1 | tee build.log
   ```

3. **结合其他工具**
   ```bash
   # 等待构建完成
   trigger_build.sh --project myapp --branch main
   # 然后使用其他工具监控构建状态
   ```

## 相关资源

- [Jenkins Remote Access API](https://www.jenkins.io/doc/book/using/remote-access-api/)
- [Jenkins CSRF Protection](https://www.jenkins.io/doc/book/security/csrf-protection/)
- [Jenkins CLI](https://www.jenkins.io/doc/book/managing/cli/)
