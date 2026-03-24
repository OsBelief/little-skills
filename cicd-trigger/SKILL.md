---
name: cicd-trigger
description: 当用户需要【构建】【部署】【编译】【发布】【打包】【发版】服务时使用此 skill。支持触发 CICD Pipeline、查看构建状态和日志、取消构建。典型触发词：构建服务、部署到环境、编译代码、打包应用、构建 Docker 镜像、启动 Pipeline、发布版本。此 skill 专注于触发新的构建和部署操作，不用于查看已部署服务的运行状态或镜像版本（请使用 k8s-status skill）。
allowed-tools: Bash, Read, Edit, Write, AskUserQuestion, Task, TaskOutput
---

# CICD Trigger Skill

## Preflight

每次调用前检查凭据：

```bash
DEVOPS_TOKEN="${DEVOPS_TOKEN:-$(grep -E '^DEVOPS_TOKEN=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
export DEVOPS_TOKEN
[ -n "$DEVOPS_TOKEN" ] || { echo "MISSING: DEVOPS_TOKEN"; exit 3; }
```

缺失时提示用户：前往 DevOps 平台个人设置页面获取 Access Token，将值告知我后执行 `mkdir -p ~/.xyinfpilot` 并追加写入 `~/.xyinfpilot/.env`：`DEVOPS_TOKEN=<token>`，然后继续执行。

> **OpenClaw 环境**：配置完成后记录状态到 `memory/YYYY-MM-DD.md`（不写凭据值），避免下次会话重复询问。

## 核心原则

1. **优先用 `--service` 让工具自动解析**，避免手动查找 pipeline 名称
2. **所有触发操作必须加 `--json`**，只有 JSON 模式才能获取 `pipelineRunName` 用于监控
3. **触发成功后立即返回用户，后台异步监控**，不要阻塞等待

---

## 触发流程（决策树）

### Step 1：执行首次触发

```bash
scripts/cicd-client.sh deploy --service <svc> --env <env> [--deploy] --json
```

> 仅构建不部署时去掉 `--deploy`

### Step 2：根据返回 JSON 决策

```
result.resolved == false
  → 多个置顶 Pipeline，展示 candidates 让用户选择
  → 用户选择后：带 --pipeline-name <选择> 重新触发

result.needsServiceSelection == true
  → 多服务 Pipeline，展示 deployServices 列表
  → 询问用户："该 Pipeline 会同时构建以下服务，请选择您要更新的服务"
  → 用户选择后：带 --pipeline-name <pipelineName> --deploy-server <选择> 重新触发

result.success == true
  → 触发成功，提取 pipelineRunName → Step 3
```

> 错误处理：工具返回非零退出码时，检查错误信息。常见原因：服务名拼写错误、无置顶 Pipeline（提示用 `list-pipelines --server-name <svc>` 查询）、Token 过期。

### Step 3：后台监控 + 立即答复用户

- 用 **Task 工具**（haiku 模型，`run_in_background=True`）每 30 秒执行一次：
  ```bash
  scripts/cicd-client.sh run-status --pipeline-run-name <pipelineRunName> --json
  ```
- 同时立即告知用户触发结果，不等待监控完成
- 后续对话中通过 `TaskOutput(block=False)` 汇报构建状态

---

## 命令速查

| 场景 | 命令 |
|------|------|
| 自动解析并触发 | `deploy --service <svc> --env <env> --deploy --json` |
| 指定 pipeline 触发 | `deploy --pipeline-name <name> --env <env> --deploy --json` |
| 指定子服务触发 | `deploy --pipeline-name <name> --deploy-server <svc> --env <env> --deploy --json` |
| 查询置顶 pipelines | `list-pipelines --server-name <svc> --topped` |
| 查构建状态 | `run-status --pipeline-run-name <name> --json` |
| 查构建日志 | `logs --pipeline-run-name <name>` |
| 取消构建 | `cancel --pipeline-run-name <name>` |

---

## 业务知识

### 环境映射

| 用户说法 | env 参数值 | 说明 |
|---------|-----------|------|
| 5.2dev / dev环境 | `private-5.2` | 默认开发环境 |
| 5.2qa / qa环境 | `private-5.2-qa` | QA 测试环境 |
| 5.2ha | `private-5.2ha` | 高可用环境 |
| 公有云 | `public-5.2` | 公有云环境 |

环境名不确定时，用 `scripts/cicd-client.sh envs --all` 列出所有环境。

### 架构规则

- **Java 服务**（绝大多数）：`deploy` 自动推断为 `x86`，无需指定
- **C++ 服务**（如 dmcu 系列）：工具会触发多服务选择流程（`needsServiceSelection`）
- **显式指定**：`--deploy-arch x86`（单架构）或 `--deploy-arch multi`（多架构）

### 多服务 Pipeline 说明

dmcu 等 C++ Pipeline 一次构建多个服务（nmst、hls、ma、dmcu、nmsa、ivr、dmcu-x86），必须让用户明确选择目标服务后才触发，避免误更新其他服务。

---

## 参考文档

- [reference/commands.md](reference/commands.md) — 完整命令参数、状态字段说明、故障排除
