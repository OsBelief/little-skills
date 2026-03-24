## 支持的操作

### 1. 部署服务（推荐）

使用 `deploy` 命令触发 Pipeline，需要显式指定 `--pipeline-name`，并使用 `--service` 或 `--deploy-arch` 决定架构。

**⚠️ 重要**：必须使用 `--json` 参数获取 `pipelineRunName`，用于后续监控和取消操作。

**推荐用法**:
```bash
# 触发构建并获取 pipelineRunName（推荐）
result=$(cicd-client deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy --deploy-arch x86 --json)
pipelineRunName=$(echo "$result" | jq -r '.pipelineRunName')

# JSON 输出格式示例：
# {"success":true,"pipelineRunName":"bm-release-5.2-20260104-25","pipelineName":"bm-release-5.2-20251226","env":"private-5.2","deploy":true}
```

**普通用法**:
```bash
# 仅构建
cicd-client deploy --pipeline-name <pipeline-name> --env <env-name> --deploy-arch x86

# 构建并部署
cicd-client deploy --pipeline-name <pipeline-name> --env <env-name> --deploy --deploy-arch x86

# 指定服务（用于自动判断 Java/x86）
cicd-client deploy --pipeline-name <pipeline-name> --env <env-name> --service <service-name> --deploy

# 非 Java 服务需要指定架构
cicd-client deploy --pipeline-name <pipeline-name> --env <env-name> --deploy --deploy-arch multi
```

### 2. 直接触发 Pipeline

使用 `trigger` 命令直接指定 Pipeline 名称触发。

**推荐用法**:
```bash
# 触发并获取 pipelineRunName（推荐）
result=$(cicd-client trigger --pipeline-name <pipeline-name> --env <env-name> --deploy --json)
pipelineRunName=$(echo "$result" | jq -r '.pipelineRunName')
```

**普通用法**:
```bash
# 仅构建
cicd-client trigger --pipeline-name <pipeline-name> --env <env-name>

# 构建并部署
cicd-client trigger --pipeline-name <pipeline-name> --env <env-name> --deploy

# 多架构部署
cicd-client trigger --pipeline-name <pipeline-name> --env <env-name> --deploy --deploy-arch multi
```

### 3. 状态监控

查询 Pipeline 运行状态和历史记录。

**示例**:
```bash
# 查看特定 Pipeline Run 的状态（推荐）
cicd-client run-status --pipeline-run-name <pipeline-run-name>

# 查看特定 Pipeline Run 的状态（JSON 格式）
cicd-client run-status --pipeline-run-name <pipeline-run-name> --json

# 比如
cicd-client run-status --pipeline-run-name bm-release-5.2-20251226-22

# 查看 Pipeline 的历史记录（通过内部 API）
cicd-client status --pipeline-name <pipeline-name> --limit 5

# 等待构建完成
cicd-client wait --pipeline-name <pipeline-run-name> --timeout 600
```

**说明**:
- `run-status`: 通过 Dashboard API 直接查询 Pipeline Run 状态，推荐使用
- `status`: 通过内部 API 查询历史记录，某些 Pipeline 可能查不到

### 4. 日志查看

获取 Pipeline 运行的详细日志，支持查看所有步骤或特定步骤的日志。

**示例**:
```bash
# 获取 Pipeline Run 的完整日志
cicd-client logs --pipeline-run-name <pipeline-run-name>

# 获取特定 Step 的日志
cicd-client logs --pipeline-run-name <pipeline-run-name> --step-name <step-name>

# 输出 JSON 格式（用于程序化处理）
cicd-client logs --pipeline-run-name <pipeline-run-name> --json

# 使用 verbose 模式查看详细执行过程
cicd-client --verbose logs --pipeline-run-name <pipeline-run-name>
```

### 5. 取消 Pipeline Run

取消正在执行或已完成的 Pipeline Run。

**示例**:
```bash
# 取消特定的 Pipeline Run
cicd-client cancel --pipeline-run-name <pipeline-run-name>

# 示例
cicd-client cancel --pipeline-run-name bm-release-5.2-20251226-24

# 使用 verbose 模式查看详细信息
cicd-client --verbose cancel --pipeline-run-name <pipeline-run-name>
```

**使用场景**:
- 取消错误触发的构建
- 停止正在运行的构建
- 清理失败的构建记录

**注意事项**:
- 此操作不可撤销
- 取消正在运行的 Pipeline 可能需要几秒钟生效
- 某些已完成的 Pipeline Run 可能无法取消

### 6. 环境管理

列出和管理部署环境。

**环境类别**:
- `publicCloud` - 公有云环境
- `zoneCloud` - 专区云环境
- `hybridCloud` - 混合云环境

**示例**:
```bash
# 列出所有公有云环境
cicd-client envs --category publicCloud

# 列出所有可用环境
cicd-client envs --all
```

### 7. 服务发现

查询可用的服务和分支。

**示例**:
```bash
# 列出所有服务
cicd-client services
```

### 8. Pipeline 名称查询

当用户只提供模糊名称或服务名时，先通过 API 查询候选的 Pipeline 名称并让用户确认。

**示例**:
```bash
# 按 Pipeline 名称关键字查询
curl -s -H "Authorization: Bearer $DEVOPS_TOKEN" \
  "https://devops.xylink.com/devops-gateway-prd/version-resource/pipeline/listPipelineRuns?pageNum=1&pageSize=20&pipelineName=<keyword>"

# 按服务名过滤
curl -s -H "Authorization: Bearer $DEVOPS_TOKEN" \
  "https://devops.xylink.com/devops-gateway-prd/version-resource/pipeline/listPipelineRuns?pageNum=1&pageSize=20&serverName=<service-name>"
```

## 参数映射表

| 自然语言 | 参数名 | 值 | 说明 |
|---------|--------|-----|------|
| 测试环境 | env | (用户指定) | 测试环境标识 |
| 开发环境 | env | (用户指定) | 开发环境标识 |
| 生产环境 | env | (用户指定) | 生产环境标识 |
| 部署 | deploy | true | 构建后部署 |
| 仅构建 | deploy | false | 只构建不部署 |
| 公有云 | envCategory | publicCloud | 公有云环境 |
| 专区云 | envCategory | zoneCloud | 专区云环境 |
| 混合云 | envCategory | hybridCloud | 混合云环境 |
| 多架构 | deployArch | multi | 多架构部署 |
| 单架构 | deployArch | single | 单架构部署 |

## 命令行工具参考

### 通用参数

所有命令都支持以下通用参数：

```bash
cicd-client [通用参数] <command> [命令参数]
```

**通用参数**:
- `--base-url URL`: API 基础 URL
- `--verbose` / `-v`: 显示详细日志
- `--debug`: 显示调试日志

### 可用命令

#### services - 列出所有服务
```bash
cicd-client services
```

#### envs - 列出环境
```bash
cicd-client envs [--category CATEGORY] [--all]
```
**参数**:
- `--category`: 环境类别 (publicCloud, zoneCloud, hybridCloud)
- `--all`: 列出所有类别的环境

#### deploy - 部署服务（推荐）
```bash
cicd-client deploy --pipeline-name NAME --env ENV [OPTIONS]
```
**参数**:
- `--pipeline-name`: Pipeline 名称 (必需)
- `--env`: 目标环境 (必需)
- `--service`: 服务名 (可选，未提供时需指定 `--deploy-arch`)
- `--deploy`: 是否部署 (可选)
- `--apply`: 是否应用 (可选)
- `--env-category`: 环境类别 (可选，默认 zoneCloud)
- `--deploy-arch`: 部署架构 (可选，未提供 `--service` 时必填)
- `--iteration`: 迭代选择 (可选，默认 `snapshot(当前默认迭代)`)
- `--wait`: 等待完成 (可选)
- `--json`: **以 JSON 格式输出结果，包含 pipelineRunName（推荐使用）**

**自动行为**:
- 若提供 `--service`，从 API 获取服务类型，Java 服务自动使用 x86 架构
- 默认使用当前迭代 `snapshot(当前默认迭代)`

#### trigger - 触发 Pipeline
```bash
cicd-client trigger --pipeline-name NAME --env ENV [OPTIONS]
```
**参数**:
- `--pipeline-name`: Pipeline 名称 (必需)
- `--env`: 目标环境 (必需)
- `--deploy`: 是否部署 (可选)
- `--apply`: 是否应用 (可选)
- `--env-category`: 环境类别 (可选)
- `--deploy-arch`: 部署架构 (可选)
- `--iteration`: 迭代选择 (可选，默认 `snapshot(当前默认迭代)`)
- `--wait`: 等待完成 (可选)
- `--json`: **以 JSON 格式输出结果，包含 pipelineRunName（推荐使用）**

#### status - 查看状态
```bash
cicd-client status --pipeline-name NAME [--limit N]
```
**参数**:
- `--pipeline-name`: Pipeline 名称 (必需)
- `--limit`: 记录数量 (可选，默认 10)

#### run-status - 查看 Pipeline Run 状态（推荐）
```bash
cicd-client run-status --pipeline-run-name NAME [--json]
```
**参数**:
- `--pipeline-run-name`: Pipeline Run 名称 (必需)
- `--json`: 以 JSON 格式输出 (可选)

**返回字段**:
- `status`: 状态 (Running, Completed, Succeeded, Failed, PipelineRunTimeout)
- `message`: 详细信息
- `startTime`: 开始时间
- `completionTime`: 完成时间
- `isRunning`, `isSucceeded`, `isFailed`: 布尔状态标志

#### wait - 等待 Pipeline 完成
```bash
cicd-client wait --pipeline-name NAME [--timeout SECONDS]
```
**参数**:
- `--pipeline-name`: Pipeline 名称 (必需)
- `--timeout`: 超时时间（秒）(可选，默认 600)

#### logs - 获取日志
```bash
cicd-client logs --pipeline-run-name NAME [--step-name STEP] [--json]
```
**参数**:
- `--pipeline-run-name`: Pipeline Run 名称 (必需)
- `--step-name`: Step 名称 (可选)
- `--json`: 以 JSON 格式输出 (可选)

#### cancel - 取消 Pipeline Run
```bash
cicd-client cancel --pipeline-run-name NAME
```
**参数**:
- `--pipeline-run-name`: Pipeline Run 名称 (必需)

**返回**:
- 成功: 显示取消成功消息
- 失败: 显示错误原因

**使用场景**:
- 取消错误触发的构建
- 停止正在运行的构建
- 清理失败的构建记录

## 常见场景

### 场景 1: 部署到测试环境
```bash
# 指定 Pipeline 并部署
cicd-client deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy --deploy-arch x86
```

### 场景 2: 仅构建不部署
```bash
cicd-client deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy-arch x86
```

### 场景 3: 查看构建状态
```bash
# 推荐：使用 Pipeline Run 名称
cicd-client run-status --pipeline-run-name <pipeline-run-name>

# 或查看历史记录
cicd-client status --pipeline-name <pipeline-name> --limit 5
```

### 场景 4: 查看构建日志
```bash
cicd-client logs --pipeline-run-name <pipeline-run-name>
```

### 场景 5: 取消构建
```bash
cicd-client cancel --pipeline-run-name bm-release-5.2-20251226-24
```

## 常见研发场景操作指南

### 场景 1: 构建 Docker 镜像并部署到测试环境

**用户需求**：编译代码、构建 Docker 镜像、部署到 private-5.2 测试环境

**操作流程**：
1. 确认 `pipeline_name`、`env`、`deploy-arch/ service`
2. 触发构建和部署
3. 等待构建完成
4. 查看构建日志确认结果

```bash
# 指定 Pipeline，触发构建和部署
{SKILL_DIR}/scripts/cicd-client.sh --verbose deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy --deploy-arch x86

# 可选：等待构建完成（超时 10 分钟）
{SKILL_DIR}/scripts/cicd-client.sh --verbose wait --pipeline-name <pipeline-run-name> --timeout 600

# 查看构建日志
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <pipeline-run-name>
```

### 场景 2: 仅构建不部署（快速验证）

**用户需求**：快速验证代码能否编译通过，不进行实际部署

**操作流程**：
1. 触发仅构建（不部署）
2. 查看构建状态
3. 如有问题查看详细日志

```bash
# 仅构建，不部署
{SKILL_DIR}/scripts/cicd-client.sh --verbose deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy-arch x86

# 查看最近的构建记录
{SKILL_DIR}/scripts/cicd-client.sh --verbose status --pipeline-name <pipeline-name> --limit 5

# 如果构建失败，查看详细日志
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <failed-pipeline-run-name>
```

### 场景 3: 多架构部署（ARM + x86）

**用户需求**：为支持多种 CPU 架构的环境构建镜像

**操作流程**：
1. 指定多架构参数
2. 触发构建和部署
3. 验证多架构镜像

```bash
# 多架构构建和部署
{SKILL_DIR}/scripts/cicd-client.sh --verbose deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy --deploy-arch multi

# 查看构建日志，确认多架构构建成功
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <pipeline-run-name>
```

### 场景 4: 查看构建历史和失败原因

**用户需求**：排查最近构建失败的原因

**操作流程**：
1. 查看最近的构建记录
2. 定位失败的构建
3. 查看失败构建的详细日志
4. 分析特定步骤的日志

```bash
# 查看最近 10 次构建记录
{SKILL_DIR}/scripts/cicd-client.sh --verbose status --pipeline-name <pipeline-name> --limit 10

# 查看失败构建的完整日志
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <failed-pipeline-run-name>

# 查看特定失败步骤的日志（如编译步骤）
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <failed-pipeline-run-name> --step-name build
```

### 场景 5: 部署到生产环境（谨慎操作）

**用户需求**：将验证通过的版本部署到生产环境

**操作流程**：
1. 确认当前版本已在测试环境验证
2. 触发生产环境部署
3. 实时追踪部署进度
4. 验证部署结果

```bash
# 部署到生产环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose deploy --pipeline-name <pipeline-name> --env production --deploy --deploy-arch x86

# 等待部署完成并实时查看状态
{SKILL_DIR}/scripts/cicd-client.sh --verbose wait --pipeline-name <pipeline-run-name> --timeout 900

# 查看部署日志确认成功
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <pipeline-run-name>
```

### 场景 6: 收集 CICD 触发参数

**用户需求**：确认 Pipeline 触发所需的参数

**触发方式**：用户说"配置 cicd"、"初始化 cicd 参数"

**操作流程**：
1. 获取可用的环境和服务列表（用于选择）
2. 引导用户确认 `pipeline_name`、`env`
3. 引导用户确认 `service` 或 `deploy-arch`

```bash
# 获取服务列表
{SKILL_DIR}/scripts/cicd-client.sh --verbose services

# 获取所有可用环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose envs --all

# 然后使用 AskUserQuestion 工具引导用户确认参数
```

### 场景 7: 查看特定环境的可用服务

**用户需求**：了解某个环境类别下有哪些可部署的环境

**操作流程**：
```bash
# 查看公有云环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose envs --category publicCloud

# 查看专区云环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose envs --category zoneCloud

# 查看混合云环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose envs --category hybridCloud

# 查看所有环境
{SKILL_DIR}/scripts/cicd-client.sh --verbose envs --all
```

### 场景 8: 编译项目并打包（仅编译阶段）

**用户需求**：只执行编译和打包，不构建 Docker 镜像

**说明**：通常 Pipeline 会包含多个阶段（编译、打包、构建镜像、部署），如果只需要编译：

```bash
# 触发构建但不部署（包含编译和打包）
{SKILL_DIR}/scripts/cicd-client.sh --verbose deploy --pipeline-name <pipeline-name> --env private-5.2 --deploy-arch x86

# 查看编译步骤的日志
{SKILL_DIR}/scripts/cicd-client.sh --verbose logs --pipeline-run-name <pipeline-run-name> --step-name compile
```

## 操作原则

1. **优先使用 deploy 命令**：必须提供 `--pipeline-name`
2. **启用 verbose 模式**：使用 `--verbose` 让用户了解执行过程
3. **合理设置超时**：构建任务通常需要 5-10 分钟，部署可能更长
4. **查看详细日志**：构建失败时必须查看完整日志定位问题
5. **确保参数完整**：确认 `pipeline_name`、`env`、`deploy-arch/ service`
6. **注意架构选择**：Java 服务自动使用 x86，其他服务需要明确指定
7. **生产部署谨慎**：部署到生产环境前必须在测试环境验证
8. **等待构建完成**：重要部署应该等待完成并验证结果
9. **使用后台监控**：长时间构建使用后台 Task 监控，不阻塞主对话

## 后台 Task 监控

构建部署任务通常需要 5-10 分钟完成。为避免阻塞主对话，可以使用 Task 工具在后台监控构建进度。

### 启动后台监控

**⚠️ 关键要求：必须使用后台模式**

触发构建后，立即启动后台 Task 监控构建进度：

```python
Task(
    description="监控构建进度直到完成",
    prompt="""监控 Pipeline Run <pipelineRunName> 的构建状态，直到完成。

使用命令查询状态：
~/.claude/plugins/cache/rd-marketplace/rd-plugin/1.0.0/skills/cicd-trigger/scripts/cicd-client.sh run-status --pipeline-run-name <pipelineRunName> --json

监控逻辑：
1. 每 30 秒检查一次构建状态
2. 检查以下情况时立即返回：
   - 构建成功：status 为 "Succeeded" 或 "Completed"
   - 构建失败：status 为 "Failed" 或 "PipelineRunTimeout"
   - 构建已取消：返回 404 或包含 "not found"
   - 超时：30 分钟内无状态变化
3. 异常处理：网络错误或命令失败时重试 3 次（间隔 10 秒）

返回 JSON 格式结果：
{
  "status": "成功|失败|已取消|超时",
  "pipelineRunName": "<pipelineRunName>",
  "duration": "X分Y秒",
  "errorMessage": "失败原因（如有）"
}""",
    subagent_type="general-purpose",
    run_in_background=True,  # ⚠️ 必需：后台运行，不阻塞主对话
    model="haiku"
)
```

**关键说明**：
- `run_in_background=True` 是**必需的**，否则会阻塞主 Agent 5-10 分钟
- Task 会在后台每 30 秒检查一次构建状态
- 主对话立即继续，不受影响

### 立即返回给用户

触发构建和启动后台监控后，**立即返回**以下信息：

```
✅ 构建已触发
Pipeline Run: access-master-5.2-xxx
预计完成时间: 5-10 分钟

⏳ 我已在后台启动监控，构建完成时会自动通知你
💡 你可以继续其他工作，无需等待

📝 你也可以随时说：
- "查看构建状态" - 手动检查进度
- "查看构建日志" - 查看详细日志
```

**不要**：
- ❌ 不要等待构建完成
- ❌ 不要阻塞主对话
- ❌ 不要立即验证镜像（构建还没完成）

记录 Task ID，用于后续检查结果。

### 检查后台任务结果

在用户的后续交互中，使用 `TaskOutput` 工具**非阻塞地**检查后台任务：

```python
TaskOutput(
    task_id="<task-id>",  # 启动后台监控时返回的 Task ID
    block=False  # 关键：非阻塞检查
)
```

#### 检查时机
1. **用户的下一次交互时** - 无论用户问什么，先检查一次
2. **定期检查** - 如果用户持续对话，每次交互都检查
3. **用户明确查询时** - 用户说"查看构建状态"时

#### 结果处理

**情况 1：任务尚未完成**
```
# TaskOutput 返回 status: running
# 不采取任何行动，继续正常对话
# 下次交互时再检查
```

**情况 2：构建成功**
```
# TaskOutput 返回 status: completed, success: true
# 主动告知用户：

✅ 构建完成！
Pipeline Run: access-master-5.2-xxx
状态：成功
耗时：约 6 分钟

需要验证部署的镜像版本吗？
```

**情况 3：构建失败**
```
# TaskOutput 返回 status: completed, success: false
# 主动告知用户：

❌ 构建失败
Pipeline Run: access-master-5.2-xxx
失败原因：[从日志中提取]

需要查看详细日志吗？
```

**情况 4：构建已取消**
```
# TaskOutput 返回包含 "已取消" 或 "cancelled" 信息
# 主动告知用户：

✅ 构建已取消
Pipeline Run: access-master-5.2-xxx
状态：已取消
原因：用户主动取消

后台监控已自动停止。
```

**情况 5：任务超时**
```
# TaskOutput 返回 status: timeout
# 主动告知用户：

⚠️ 构建监控超时（30分钟）
Pipeline Run: access-master-5.2-xxx

构建可能仍在进行中，请说：
- "查看构建状态" - 检查当前状态
- "查看构建日志" - 查看进度日志
```

### 后台监控机制说明

#### 关键原则

1. **必须使用后台模式**
   - `Task(run_in_background=True)` 是**必需的**
   - 不设置会导致主对话阻塞 5-10 分钟
   - 这会严重影响用户体验

2. **非阻塞检查**
   - 使用 `TaskOutput(task_id, block=False)`
   - **不要** 使用 `block=True`（会阻塞）
   - 每次用户交互时检查一次即可

3. **主动通知**
   - 检测到任务完成时，主动告知用户
   - 无论用户问什么，先检查后台任务
   - 确保用户不会错过构建结果

#### 工作流时间线

```
T=0秒:    用户请求 "构建部署到 5.2dev"
T=1秒:    触发构建 + 启动后台 Task
T=2秒:    返回用户 "已在后台监控"
T=3秒:    用户可以继续其他工作（不阻塞）
T=30秒:   后台 Task 第 1 次检查状态（构建中...）
T=60秒:   后台 Task 第 2 次检查状态（构建中...）
T=90秒:   用户问其他问题，顺便检查 TaskOutput（构建中...）
          → 正常回答用户问题
...
T=300秒:  后台 Task 检测到构建成功
T=310秒:  用户下次交互，检查 TaskOutput
          → 主动通知："✅ 构建成功！"
```

#### 错误场景处理

| 场景 | 结果 | 解决方案 |
|------|------|----------|
| 忘记设置 run_in_background=True | 主对话阻塞 5-10 分钟 | 在文档中多次强调此参数 |
| 使用 block=True 检查 | 每次检查都阻塞 | 始终使用 block=False |
| 构建超时（>30分钟） | 后台 Task 超时返回 | 通知用户，提供手动查询选项 |
| 用户触发后离开很久再回来 | 下次交互检查 TaskOutput | 主动告知结果，即使已过去很久 |

### 取消构建和停止监控

#### 1. 取消正在运行的构建

如果用户想取消刚刚触发的构建，使用 `cancel` 命令：

```bash
{SKILL_DIR}/scripts/cicd-client.sh cancel --pipeline-run-name <pipeline-run-name>
```

**示例**：
```
用户: "取消刚刚的构建"
Agent: 使用 cancel 命令取消 Pipeline Run

{SKILL_DIR}/scripts/cicd-client.sh cancel --pipeline-run-name bm-release-5.2-20251226-25

响应：✅ Pipeline Run bm-release-5.2-20251226-25 已成功取消
```

#### 2. 停止后台监控任务

**当前行为（已优化）**：
- ✅ Pipeline Run 已被取消
- ✅ **后台监控任务会在下一个检查周期自动停止**（最多 30 秒）
- ℹ️ 你也可以通过界面手动立即停止（如果不想等待）

**手动停止方法**：

**方法 1：通过 Claude Code 界面**
- 在 Claude Code 界面找到运行中的后台任务
- 点击停止或取消按钮
- 任务提示可能显示为 "Monitor build progress until completion (running)"

**方法 2：等待自动超时**
- 后台任务会在 30 分钟后自动超时停止
- 这期间不会影响你进行其他操作

**方法 3：重启会话**
- 关闭当前 Claude Code 会话
- 重新开始新会话
- 旧的后台任务会被清理

#### 3. 已实现的功能

后台监控任务能够：
1. ✅ **自动检测取消状态**：定期检查 Pipeline 是否被取消（每 30 秒）
2. ✅ **智能停止**：检测到取消后自动停止监控
3. ✅ **通知用户**：主动告知"构建已被取消，监控已停止"

#### 4. 最佳实践

**场景 1：需要取消构建**
```
1. 用户: "取消刚刚的构建"
2. Agent: 使用 cancel 命令取消构建
3. Agent: "✅ 构建已取消。后台监控会在 30 秒内自动停止。"
4. 【自动】后台 Task 下次检查时检测到取消，自动停止
5. 【可选】用户也可以通过界面立即手动停止
```

**场景 2：取消后继续其他工作**
```
1. 用户: "取消刚刚的构建"
2. Agent: 取消构建成功
3. 用户: 继续其他工作（后台任务自动超时，不影响）
```

**场景 3：取消并重新触发**
```
1. 用户: "取消刚刚的构建"
2. Agent: 取消构建成功
3. 用户: "重新部署到 5.2dev"
4. Agent: 触发新的构建和监控（新的 Task ID）
```

### 常见问题

**Q: 取消构建后，为什么后台监控还在运行？**

A: ✅ **已优化**：后台监控现在会自动检测 Pipeline 是否被取消。检测到取消后，会在下一个检查周期（最多 30 秒）自动停止。如果你不想等待，可以通过界面手动立即停止。

**Q: 后台监控会影响系统性能吗？**

A: 不会。后台监控只是每 30 秒发送一次状态查询，资源占用极少。

**Q: 如何避免多个后台监控任务堆积？**

A:
- 每次触发新构建前，先取消之前的构建
- 通过界面停止不需要的后台任务
- 后台任务会在 30 分钟后自动超时清理

**Q: 能否在触发构建时就不启动后台监控？**

A: 可以。后台监控是可选的，你可以只触发构建，然后手动使用 `run-status` 或 `status` 命令查询状态。

## 镜像命名规范

DevOps 平台构建的 Docker 镜像遵循统一的命名规范，标签包含了完整的版本和构建信息。

### 镜像标签格式

**完整格式**:
```
<registry>/<project>/<service-name>-rpm:<branch>-<iteration>-<commit_date>-<timestamp>-<commit_hash>-<devops_build_time>
```

**示例**:
```
10.0.7.133/private_cloud/private-basic-management-rpm:release-5.2-3.2-20251226-20251218105112-29a14829-1766649568
```

### 标签字段说明

| 字段位置 | 字段名称           | 说明                        | 示例值                |
|----------|--------------------|-----------------------------|----------------------|
| 1        | branch             | 分支名                      | release-5.2          |
| 2        | iteration          | 所属迭代版本                | 3.2                  |
| 3        | commit_date        | 代码提交日期 (YYYYMMDD)     | 20251226             |
| 4        | timestamp          | 代码提交时间戳 (YYYYMMDDHHMMSS) | 20251218105112   |
| 5        | commit_hash        | Git Commit Hash (前8位)     | 29a14829             |
| 6        | devops_build_time  | DevOps 构建镜像时间 (Unix时间戳) | 1766649568      |

### Unix 时间戳转换

DevOps 构建时间使用 Unix 时间戳格式，可以转换为人类可读的日期时间：

**转换示例**:
- `1766649568` → `2025-12-25 09:39:28` (UTC+8)

**在线转换工具**:
```bash
# Linux/macOS 命令行转换
date -r 1766649568

# 或使用 Python
python3 -c "import datetime; print(datetime.datetime.fromtimestamp(1766649568))"
```

### 标签解读示例

对于镜像标签 `release-5.2-3.2-20251226-20251218105112-29a14829-1766649568`：

- **分支**: release-5.2 (5.2 版本的发布分支)
- **迭代**: 3.2 (属于 3.2 迭代)
- **代码提交日期**: 2025年12月26日
- **代码提交时间**: 2025年12月18日 10:51:12
- **代码提交**: 29a14829 (Git commit hash)
- **镜像构建时间**: 2025年12月25日 09:39:28



## 工具路径说明

所有命令都需要使用 wrapper 脚本调用：

```bash
# 正确方式（自动选择正确架构）
{SKILL_DIR}/scripts/cicd-client.sh <command> [options]

# 错误方式（直接调用二进制文件）
{SKILL_DIR}/scripts/bin/cicd-client-darwin-arm64 <command>  # ❌
```

其中 `{SKILL_DIR}` 表示 cicd-trigger skill 所在目录的绝对路径。

## 环境变量

### 必需
- `DEVOPS_TOKEN`: Bearer Token (必需，用于触发 Pipeline、查询状态等操作)

### 默认配置
- **DevOps API 地址**: 固定为 `https://devops.xylink.com`
- 可通过 `--base-url` 参数临时覆盖

### 说明
- **日志查看功能**: Dashboard API 不需要额外认证，可以直接访问。`logs` 命令只需要 `DEVOPS_TOKEN` 环境变量即可正常工作。

## 故障排除

### 启用调试日志

遇到问题时，启用调试日志查看详细信息：

```bash
# 使用 --debug 参数查看完整的 API 交互
cicd-client --debug services

# 示例：调试触发问题
cicd-client --debug trigger \
  --pipeline-name <pipeline-name> \
  --env <env-name>
```

### 认证失败
```bash
# 问题：未配置认证信息
# 解决：设置环境变量
export DEVOPS_TOKEN="your_token_here"
cicd-client services
```

### 环境不可用
```bash
# 问题：目标环境不存在
# 解决：列出可用环境
cicd-client envs --category zoneCloud
```

## 编译信息

cicd-client 使用 Rust 编写，源代码位于 `scripts/src/main.rs`。

### 编译方法

```bash
cd {SKILL_DIR}/scripts

# 编译当前平台
./build.sh native

# 编译 macOS 双架构 (x86_64 + arm64)
./build.sh macos

# 编译 Linux x86_64 (需要 zig)
./build.sh linux

# 编译 Windows x86_64 (需要 zig)
./build.sh windows

# 编译所有平台
./build.sh all

# 清理构建产物
./build.sh clean
```

### 跨平台编译要求

Linux 和 Windows 交叉编译需要安装 zig：

```bash
# macOS
brew install zig
cargo install cargo-zigbuild
```

### 产物位置

编译产物位于 `scripts/bin/` 目录：
- `cicd-client-darwin-amd64` - macOS Intel
- `cicd-client-darwin-arm64` - macOS Apple Silicon
- `cicd-client-linux-amd64` - Linux x86_64
- `cicd-client-windows-amd64.exe` - Windows x86_64

## 更多资源

- [快速开始](README.md)
- [API 文档](reference/api-endpoints.md)
- [配置指南](config/README.md)
