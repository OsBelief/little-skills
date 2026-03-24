---
name: ones
description: 查询和管理 ONES 项目管理平台的工作项与 Wiki。支持查询 Bug/缺陷/需求/任务、状态流转、添加评论、变更负责人、登记/查询/修改工时、下载工作项附件、获取 Wiki 页面内容。典型场景："查询我的 Bug"、"按编号查详情"、"更新负责人/状态"、"登记工时"、"下载工作项附件"、"按链接读取 wiki 页面"、"查询环境信息"。
allowed-tools: Bash, Read, Write
---

# ONES 项目管理 Skill

## 适用范围

- 工作项查询：按编号、负责人、项目、类型筛选
- 工作项修改：标题、描述、负责人、优先级、截止时间
- 状态流转：按工作流合法变更状态
- 任务讨论：发送评论、查看评论
- 工时管理：登记、查询、修改、删除
- 附件下载：按工作项编号或 URL 下载全部附件并校验大小
- Wiki 查询：按 Wiki URL 或 pageUUID 获取页面详情与正文内容
- 环境信息查询：当用户问环境机器/IP/入口地址时，优先读取指定 Wiki 页面

## Preflight

每次调用前检查凭据：

```bash
ONES_TOKEN="${ONES_TOKEN:-$(grep -E '^ONES_TOKEN=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
ONES_USER_UUID="${ONES_USER_UUID:-$(grep -E '^ONES_USER_UUID=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
ONES_TEAM_UUID="${ONES_TEAM_UUID:-$(grep -E '^ONES_TEAM_UUID=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"
ONES_TEAM_UUID="${ONES_TEAM_UUID:-AQzvsooq}"  # 默认团队 UUID
export ONES_TOKEN ONES_USER_UUID ONES_TEAM_UUID
[ -n "$ONES_TOKEN" ] || { echo "MISSING: ONES_TOKEN"; exit 3; }
[ -n "$ONES_USER_UUID" ] || { echo "MISSING: ONES_USER_UUID"; exit 3; }
```

`ONES_TOKEN`/`ONES_USER_UUID` 缺失时提示用户：
1. 浏览器打开 `https://nones.xylink.com` 并登录
2. F12 → Application → Cookies → `nones.xylink.com`
3. 将 `ones-lt` 和 `ones-uid` 的值告诉我

用户提供后执行 `mkdir -p ~/.xyinfpilot` 并追加写入 `~/.xyinfpilot/.env`：`ONES_TOKEN=<值>` / `ONES_USER_UUID=<值>`，然后继续执行。

> **OpenClaw环境重要**：
- 配置完成后记录状态到 `memory/YYYY-MM-DD.md`（不写凭据值），避免下次会话重复询问。
- **平台地址使用 `http://nones.xylink.com:30011`（替代 `https://nones.xylink.com`）**

## 前提条件

- 平台地址：`https://nones.xylink.com`不通就用`http://nones.xylink.com:30011`
- 认证头：
  - `Ones-Auth-Token: {ONES_TOKEN}`
  - `Ones-User-Id: {ONES_USER_UUID}`
- 团队 UUID：优先使用 `ONES_TEAM_UUID`，若无则从任务 URL 中提取（`/team/{teamUUID}/`）
- Token **永久有效**（仅改密码/登出时失效），API 返回 401 时提示用户重新获取

## 操作决策树

```
用户想做什么？
│
├─ 查询工作项 → GraphQL: POST /team/{teamUUID}/items/graphql
│  ├─ 按条件批量查询 → tasks(filter: {...})
│  ├─ 按编号查详情 → tasks(filter: { number_in: [编号] })
│  └─ 查用户/项目/类型 → users / products / issueTypes
│
├─ 下载附件 → REST（4步），详见 api-reference.md §19
│  ├─ 编号/URL → taskUUID（GraphQL 或 URL 直取）
│  ├─ 拉附件列表 → GET /task/{taskUUID}/attachments?count=100
│  ├─ 逐个拉下载链接 → GET /res/attachment/{attachmentUUID}
│  └─ 下载文件并校验大小，默认输出 ~/Downloads/ones-{编号}-attachments
│
├─ 获取 Wiki 页面内容 → REST（2~3步），详见 api-reference.md §20
│  ├─ 已有 wiki URL（含 team/space/page）→ 直取 teamUUID/spaceUUID/pageUUID
│  ├─ 已有 pageUUID 但无 spaceUUID → GET /wiki/api/wiki/team/{teamUUID}/page/{pageUUID}
│  └─ 获取页面详情正文 → GET /wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/page/{pageUUID}
│
├─ 写入/更新 Wiki 页面内容 → REST（3步），详见 api-reference.md §21
│  ├─ 前提：先 GET 页面详情，检查是否有 ref_type=6 字段
│  ├─ 若 ref_type=6（新版协同编辑器）→ 无法通过 API 写入，告知用户只能浏览器手动编辑
│  ├─ 若无 ref_type=6（旧版页面）→ 走草稿三步流程
│  │  ├─ 第1步：清理旧草稿 → GET .../drafts → POST .../draft/{uuid}/delete
│  │  ├─ 第2步：创建页面草稿 → POST .../drafts/add（status=2）
│  │  └─ 第3步：发布草稿 → POST .../draft/{draftUUID}/update（is_published=true，需完整字段）
│  └─ 详见 api-reference.md §21
│
├─ 查询环境信息（如“qa52 的 main 机器 IP”）
│  ├─ 先拉取固定知识源页面 A：/team/AQzvsooq/space/CGENJVj8/page/5E8iYrdn
│  ├─ 再拉取固定知识源页面 B：/team/AQzvsooq/space/EYvdiwVh/page/GQ6GXNUX
│  ├─ 对比两页信息，优先使用更新时间更新、字段更完整的一侧
│  └─ 若两页都无明确答案，明确告知“文档未提供该信息”，不要臆测
│
├─ 修改工作项属性 → REST: POST /team/{teamUUID}/tasks/update3
│  ├─ 改负责人 → assign 字段（需先查用户 UUID）
│  ├─ 改优先级 → priority 字段
│  ├─ 改描述 → desc_rich 字段（HTML）
│  ├─ 改标题 → summary 字段
│  └─ 改截止日期/迭代 → deadline / sprint_uuid
│
├─ 变更状态 → 必须两步走，不能用 update3
│  ├─ 第1步：GET /team/{teamUUID}/task/{taskUUID}/transitions
│  └─ 第2步：POST /team/{teamUUID}/task/{taskUUID}/transit
│
├─ 添加评论 → POST /team/{teamUUID}/task/{taskUUID}/send_message
│  ├─ 请求体必须包含 uuid（消息 UUID，非用户 UUID）+ text
│  ├─ uuid 必须每次新生成（8位随机字符），重复提交同一 uuid 返回 409
│  ├─ HTTPS 内网证书需忽略 SSL 校验（curl -k 或 Python ssl.CERT_NONE）
│  └─ 详见本文档「添加评论操作指南」
│
├─ 查看评论 → GET /team/{teamUUID}/task/{taskUUID}/messages
│  ├─ 可选参数：count（最多100）、since/max（纳秒时间戳）
│  └─ 返回 messages 数组，type=discussion 为用户发送的评论
│
├─ 创建工作项 → POST /team/{teamUUID}/tasks/add2
│
├─ 登记工时（用户说"登记/填工时"）→ addManhour
│  ├─ **type 必须用 recorded**（实际工时），不要用 estimated
│  ├─ **必须用 variables 格式传参**（type 作为 JSON 字符串传入），不能内联写枚举
│  ├─ hours 换算：1天=800000，0.5天=400000，0.6天=480000，0.4天=320000，0.1天=80000
│  ├─ start_time：当天 00:00:00 CST 的 Unix 秒级时间戳（CST = UTC+8，需减去 28800）
│  └─ Example（curl）:
│     ```bash
│     curl -sk 'https://nones.xylink.com/project/api/project/team/{teamUUID}/items/graphql?t=AddManhour' \
│       -H 'content-type: application/json;charset=UTF-8' \
│       -H 'ones-auth-token: {token}' \
│       -H 'ones-user-id: {userUUID}' \
│       --data-raw '{"query":"mutation AddManhour { addManhour (mode: $mode owner: $owner task: $task type: $type start_time: $start_time hours: $hours description: $description) { key } }","variables":{"mode":"detailed","owner":"{userUUID}","task":"{taskUUID}","type":"recorded","start_time":1773277200,"hours":480000,"description":"工作描述"}}'
│     ```
│
└─ 查看工作项详情(REST) → GET /team/{teamUUID}/task/{taskUUIDOrNumber}/info
```


## URL 解析

- 工作项 URL：`https://{host}/project/#/team/{teamUUID}/task/{taskUUID}`
- Wiki URL：`https://{host}/wiki/#/team/{teamUUID}/space/{spaceUUID}/page/{pageUUID}`
- 附件下载优先级：URL 直取 UUID > 编号查 UUID

## 环境信息查询默认知识源

当用户问题包含环境信息关键词（如：`环境`、`qa`、`main`、`机器`、`IP`、`地址`、`入口`）时，默认先读取以下两个 Wiki 页面：

1. `https://nones.xylink.com/wiki/#/team/AQzvsooq/space/CGENJVj8/page/5E8iYrdn`
2. `https://nones.xylink.com/wiki/#/team/AQzvsooq/space/EYvdiwVh/page/GQ6GXNUX`

执行要求：
- 两个页面都要读取，不可只读一个
- 输出结论时标明来源页面标题与更新时间
- 如存在冲突，优先采用更新时间更新的记录，并说明冲突
- 如未命中（例如未出现“qa52 main”或 IP 字段），必须明确说明“文档未命中”，并建议补充来源

## 关键陷阱（必读）

1. 状态变更不能用 `update3` 直接改 `status_uuid`，必须 `transitions` → `transit`
2. GraphQL 查询不要带 `updateTime`，否则可能报 `Malformed.GraphQL`
3. 时间戳单位不统一，转换前先确认字段单位（微秒/秒）
4. **登记工时（addManhour）必须用 `variables` 格式传参，`type` 传 `"recorded"`**：把所有参数放进 `variables` JSON 对象，`type` 作为字符串 `"recorded"` 传入；不能将参数内联写在 query 字符串里（内联枚举写法会导致 `TooMany` 等异常）
5. `addManhour` 必须传 `mode: "detailed"`
6. 工时 `hours` 不是毫秒单位（示例：`800000=8小时`，`100000=1小时`；0.6天=480000，0.5天=400000，0.4天=320000）
6. `update3` 不可更新 `owner/create_time/number/status_uuid`
7. 附件列表接口通常不直接给可用下载 URL，需再调 `/res/attachment/{attachmentUUID}`
8. 附件下载链接是临时签名 URL，过期后需要重新拉取
9. `name_match` 建议放在 filter 末尾，降低慢查询风险
10. **发送评论 uuid 是消息 ID 非用户 ID**：必须每次新生成，复用会 409
11. **内网 HTTPS 证书校验失败**：所有请求需跳过 SSL 验证（curl -k 或 Python ssl.CERT_NONE）
12. **shell heredoc 环境变量注入**：source .env 后需 `set -a` 才能导出到 python3 子进程；复杂评论内容建议写文件再执行，避免 shell 转义破坏 JSON
13. **Wiki 接口与 Project 接口域路径不同**：Wiki 使用 `/wiki/api/wiki/...`，不要误用 `/project/api/project/...`
14. **页面读取优先使用带 space 的路由**：当已知 `spaceUUID` 时，优先调用 `/space/{spaceUUID}/page/{pageUUID}`，字段更完整
15. **Wiki 无直接更新接口**：直接 PUT/POST 页面路径必然 404，必须走"草稿→发布"三步流程
16. **发布草稿必须传完整字段**：缺少 `uuid`/`from_version`/`create_time`/`updated_time` 等字段会返回 500
17. **草稿时间戳单位是微秒**：`create_time`/`updated_time` = 秒 × 1000000
18. **`?version=0` 不是最新版**：取最新版必须不传 version 参数；`version=0` 返回第 0 版（初始版）
19. **新版协同编辑器页面（ref_type=6）无法通过 API 写入**：`content` 字段是 legacy 备份，浏览器从协同文档（ref_uuid）加载内容，草稿流程不影响页面显示；此类页面只能浏览器手动编辑

## 输出规范

- 查询类：返回核心字段和筛选条件，不返回冗长原始 JSON
- 修改类：返回“变更前后关键字段 + 是否成功”
- 附件下载类：返回
  - 下载目录（默认 `~/Downloads/ones-{编号}-attachments`）
  - 文件清单（文件名/大小）
  - 校验结果（期望大小 vs 实际大小）
  - 失败项及原因（如有）

## API 参考
**本地文档没有找到查找官方文档**
- 本地文档：[api-reference.md](./api-reference.md)
- 官方文档：
- [GraphQL 官方文档](https://docs.ones.cn/project/open-api-doc/graphql/introduction.html)
- [GraphQL Schema 定义](https://docs.ones.cn/project/open-api-doc/graphql/schema.html)
- [GraphQL 示例](https://docs.ones.cn/project/open-api-doc/graphql/example.html)
- [认证 API](https://docs.ones.cn/project/open-api-doc/auth/auth.html)
- [工作项 API](https://docs.ones.cn/project/open-api-doc/project/task.html)
- [项目 API](https://docs.ones.cn/project/open-api-doc/project/project.html)
- [资源/附件 API](https://docs.ones.cn/project/open-api-doc/project/resource.html)
- [Wiki 模型总览](https://docs.ones.cn/project/open-api-doc/wiki/wiki.html)
- [Wiki 页面 API](https://docs.ones.cn/project/open-api-doc/wiki/page.html)
- [Wiki 页面组 API](https://docs.ones.cn/project/open-api-doc/wiki/space.html)

