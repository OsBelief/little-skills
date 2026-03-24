---
name: gitlab
description: 操作 GitLab 私有化部署平台。支持查询项目、仓库文件、分支，创建/合并 MR，触发 Pipeline，以及仓库搜索（代码/提交/文件树）。使用场景包括"查询项目列表"、"搜索代码"、"获取文件内容"、"触发构建"、"创建合并请求"、"查看 Pipeline 状态"、"查找包含关键字的文件"。
allowed-tools: Bash, Read, Write
---

# GitLab API Skill

- 实例：`https://gitlab.xylink.com`（Web 443 / SSH 10022）
- API Base：`/api/v4`
- 项目标识：数字 ID 或 URL 编码路径（`/` → `%2F`）

## Preflight

每次调用前检查凭据：

```bash
GITLAB_ACCESS_TOKEN="${GITLAB_ACCESS_TOKEN:-$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
export GITLAB_ACCESS_TOKEN
[ -n "$GITLAB_ACCESS_TOKEN" ] || { echo "MISSING: GITLAB_ACCESS_TOKEN"; exit 3; }
```

缺失时提示用户：前往 `https://gitlab.xylink.com/-/user_settings/personal_access_tokens` 创建 Personal Access Token（勾选 `read_api` / `api` 权限），将值告知我后执行 `mkdir -p ~/.xyinfpilot` 并追加写入 `~/.xyinfpilot/.env`：`GITLAB_ACCESS_TOKEN=<token>`，然后继续执行。

> **OpenClaw 环境**：配置完成后记录状态到 `memory/YYYY-MM-DD.md`（不写凭据值），避免下次会话重复询问。

## 功能导航

| 场景 | 端点 |
|------|-----|
| 查找项目 | `GET /projects?membership=true&search=<kw>` |
| **代码搜索** | `GET /projects/:id/search?scope=blobs&search=<kw>&ref=<branch>` |
| 提交搜索 | `GET /projects/:id/search?scope=commits&search=<kw>` |
| 读取文件 | `GET /projects/:id/repository/files/:encoded_path/raw?ref=<ref>` |
| 目录树 | `GET /projects/:id/repository/tree?path=<dir>&recursive=true` |
| 按文件查提交 | `GET /projects/:id/repository/commits?ref_name=<branch>&path=<file>` |
| 分支列表 | `GET /projects/:id/repository/branches` |
| 创建 MR | `POST /projects/:id/merge_requests` |
| 触发 Pipeline | `POST /projects/:id/pipeline` |

## 仓库搜索工作流（重点）

搜索到文件后，用 search 结果中的 `path` + `ref` 拼接 raw 读取链路：
1. `scope=blobs` 搜索 → 获得 `path`（文件路径）
2. URL 编码 `path`（`/` → `%2F`）→ 调用 `/repository/files/:encoded_path/raw?ref=<ref>` 读取内容
3. 如需浏览目录 → 用 `/repository/tree?path=<dir>&recursive=true`
4. 如需追溯变更 → 用 `/repository/commits?path=<file>`

详细命令语法：参阅 [reference/commands.md](reference/commands.md)


