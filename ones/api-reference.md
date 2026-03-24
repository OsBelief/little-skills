# ONES API 参考文档

> 官方文档：https://docs.ones.cn/project/open-api-doc/graphql/introduction.html

## 目录

- [1. 认证 (Authentication)](#1-认证-authentication) — 登录获取 token
- [2. GraphQL 接口](#2-graphql-接口) — 请求格式和端点
- [3. 工作项查询 (Tasks)](#3-工作项查询-tasks) — 字段定义、筛选条件、各类查询示例
- [4. 分页查询](#4-分页查询) — buckets 分页机制
- [5. 项目查询 (Projects)](#5-项目查询-projects) — 产品和项目列表
- [6. 任务类型查询 (Issue Types)](#6-任务类型查询-issue-types) — 获取缺陷/需求/任务类型 UUID
- [7. 工作项操作 (REST API)](#7-工作项操作-rest-api) — 添加、更新、删除工作项
- [8. 属性查询 (Fields)](#8-属性查询-fields) — 工作项属性定义和自定义字段
- [9. 工时操作 (Manhour)](#9-工时操作-manhour) — 登记、查询、修改、删除工时
- [10. 常用状态分类](#10-常用状态分类)
- [11. 错误处理](#11-错误处理)
- [12. 完整调用示例](#12-完整调用示例)
- [13. 工作项详情查询 (REST API)](#13-工作项详情查询-rest-api) — 按 UUID/序号获取详情、批量获取
- [14. 状态流转 (Transit)](#14-状态流转-transit) — 查询可用流转、执行状态变更
- [15. 任务讨论/评论 (Message)](#15-任务讨论评论-message) — 发送评论、获取讨论消息
- [16. 工作项统计 (Task Stats)](#16-工作项统计-task-stats)
- [17. 复制工作项](#17-复制工作项)
- [18. 消息通知](#18-消息通知) — 通知列表、筛选项目消息
- [19. 工作项附件下载 (Attachments)](#19-工作项附件下载-attachments) — 列表、下载链接、完整下载脚本
- [20. Wiki 页面获取 (Wiki Pages)](#20-wiki-页面获取-wiki-pages) — 按 URL/UUID 读取页面正文

---

## 概述

ONES API 包含 GraphQL 查询接口和 REST 操作接口，用于工作项的查询和管理。

---

## 1. 认证 (Authentication)

### 1.0 认证说明（重要）

> **ONES token 永久有效**（官方文档：无过期时间），仅在用户改密码、被移出团队或主动登出时失效。

**使用方式**：直接读取 `~/.xyinfpilot/.env` 中的 `ONES_TOKEN` 和 `ONES_USER_UUID`，无需调用登录接口。

若不存在，引导用户从浏览器 Cookie 中一次性获取（见 §11.4）。

### 1.1 用户登录

**URL:**
```
POST https://{host}/project/api/project/auth/login
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| email | string | email/phone 二选一 | 用户邮箱 |
| phone | string | email/phone 二选一 | 用户手机号 |
| password | string | ✅ | 用户密码 |

> 📝 `email` 和 `phone` 同时存在时只有 `email` 生效

**请求体示例:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| user | object | 用户信息对象 |
| user.uuid | string | 用户唯一标识，用于 `Ones-User-Id` 请求头 |
| user.email | string | 用户邮箱 |
| user.name | string | 用户名称 |
| user.token | string | 认证令牌，用于 `Ones-Auth-Token` 请求头 |
| user.phone | string | 用户手机号 |
| user.avatar | string | 用户头像URL |
| user.status | int | 用户状态 (1=正常) |
| user.license_types | int[] | 许可证类型列表 |
| teams | array | 用户所属团队列表 |
| teams[].uuid | string | 团队UUID，用于API路径中的 `:teamUUID` |
| teams[].name | string | 团队名称 |
| teams[].owner | string | 团队所有者UUID |
| teams[].status | int | 团队状态 |
| teams[].type | string | 团队类型 (free/pro/enterprise) |
| teams[].member_count | int | 团队成员数量 |
| teams[].org_uuid | string | 所属组织UUID |
| org | object | 组织信息 |
| org.uuid | string | 组织UUID |
| org.name | string | 组织名称 |

**响应示例:**
```json
{
  "user": {
    "uuid": "Gq8ZZZ7F",
    "email": "user@example.com",
    "name": "用户名",
    "name_pinyin": "yonghuming",
    "title": "",
    "avatar": "",
    "phone": "",
    "create_time": 1547538969719424,
    "status": 1,
    "channel": "uGq8ZZZ7FflUZ6X5J7pqNlQclsWmkTUD",
    "token": "vBRxnkWypojEA2xxqe92GhhXW3f2FbjC9xZ1A2p7kW0mFhskEwX0wHDpvYZJkpM3",
    "license_types": [1, 2, 3, 4, 5]
  },
  "teams": [
    {
      "uuid": "U66S45tG",
      "status": 1,
      "name": "团队名称",
      "owner": "Gq8ZZZ7F",
      "logo": "",
      "cover_url": "",
      "domain": "",
      "create_time": 1547538969731072,
      "expire_time": -1,
      "type": "pro",
      "member_count": 6,
      "org_uuid": "369VHsHp",
      "workdays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
      "workhours": 800000
    }
  ],
  "org": {
    "uuid": "369VHsHp",
    "name": "组织名称",
    "org_type": 0
  }
}
```

---

## 2. GraphQL 接口

### 2.1 接口说明

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/items/graphql
```

**请求头:**
| Header | 值 | 必填 | 说明 |
|--------|---|-----|------|
| Content-Type | application/json | ✅ | 内容类型 |
| Ones-Auth-Token | {token} | ✅ | 登录返回的token |
| Ones-User-Id | {user_uuid} | ✅ | 登录返回的user.uuid |
| Referer | https://{host} | 推荐 | 来源URL |

**请求体参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| query | string | ✅ | GraphQL 查询语句 |
| variables | object | ❌ | 查询变量，用于动态传参 |
| variables.filter | object | ❌ | 筛选条件 |
| variables.orderBy | object | ❌ | 排序条件 |

**请求体示例:**
```json
{
  "query": "query TASKS($filter: Filter, $orderBy: OrderBy) { tasks(filter: $filter, orderBy: $orderBy) { uuid name } }",
  "variables": {
    "filter": {
      "assign_in": ["用户UUID"]
    },
    "orderBy": {
      "createTime": "DESC"
    }
  }
}
```

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| data | object | 查询结果数据 |
| data.{queryName} | array/object | 查询的数据内容 |
| errors | array | 错误信息 (仅在出错时) |

---

## 3. 工作项查询 (Tasks)

### 3.1 Task 对象字段

**常用字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 工作项唯一标识 |
| key | string | 工作项key (如 task-xxxxxxx) |
| name | string | 工作项标题 |
| summary | string | 工作项摘要 (同name) |
| number | int | 工作项编号 |
| desc | string | 纯文本描述 |
| desc_rich | string | 富文本描述 (HTML) |
| status | Status | 状态对象 |
| priority | Option | 优先级对象 |
| assign | User | 负责人对象 |
| owner | User | 创建人对象 |
| watchers | [User] | 关注者列表 |
| project | Project | 所属项目 |
| sprint | Sprint | 所属迭代 |
| issueType | IssueType | 任务类型 |
| parent | Task | 父任务 |
| subtasks | [Task] | 子任务列表 |
| createTime | int | 创建时间 (Unix时间戳，微秒) |
| updateTime | int | 更新时间 (Unix时间戳，微秒) |
| deadline | int | 截止日期 (Unix时间戳，秒) |
| estimatedHours | int | 预估工时 |
| remainingManhour | int | 剩余工时 |
| totalManhour | int | 总工时 |
| path | string | 任务路径 |
| position | int | 排序位置 |

**关联对象字段:**

**Status (状态):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 状态UUID |
| name | string | 状态名称 |
| category | string | 状态分类 (to_do/in_progress/done) |

**User (用户):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 用户UUID |
| name | string | 用户名称 |
| email | string | 用户邮箱 |
| avatar | string | 用户头像URL |

**Option (选项，如优先级):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 选项UUID |
| value | string | 选项值/名称 |

**IssueType (任务类型):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 类型UUID |
| name | string | 类型名称 (需求/缺陷/任务等) |
| icon | string | 图标 |

**Project (项目):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 项目UUID |
| name | string | 项目名称 |

**Sprint (迭代):**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 迭代UUID |
| name | string | 迭代名称 |

### 3.2 Filter 筛选条件

**通用筛选操作符:**
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `_in` | 包含在列表中 | `assign_in: ["uuid1", "uuid2"]` |
| `_equal` | 等于 | `uuid_equal: "xxx"` |
| `_match` | 模糊匹配 | `name_match: "关键词"` |
| `_range` | 范围 | `createTime_range: { quick: "last_7_days" }` |

**嵌套对象筛选:**
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `{object}: { uuid_in: [] }` | 对象UUID匹配 | `status: { uuid_in: ["xxx"] }` |
| `{object}: { category_in: [] }` | 对象分类匹配 | `status: { category_in: ["to_do"] }` |

**时间范围快捷值:**
| 值 | 说明 |
|---|---|
| `today` | 今天 |
| `yesterday` | 昨天 |
| `this_week` | 本周 |
| `last_7_days` | 最近7天 |
| `last_14_days` | 最近14天 |
| `this_month` | 本月 |
| `last_30_days` | 最近30天 |
| `this_quarter` | 本季度 |
| `this_year` | 今年 |

### 3.3 基础查询 - 获取任务列表

**GraphQL:**
```graphql
{
  tasks(
    filter: {
      project_in: ["项目UUID"]
    }
    orderBy: {
      createTime: DESC
    }
  ) {
    uuid
    name
    number
    summary
    desc
    status { uuid name category }
    priority { uuid value }
    assign { uuid name email }
    owner { uuid name }
    createTime
    deadline
    issueType { uuid name }
    project { uuid name }
    sprint { uuid name }
  }
}
```

**响应示例:**
```json
{
  "data": {
    "tasks": [
      {
        "uuid": "DU6krHBNNKSnnHNj",
        "name": "修复登录页面Bug",
        "number": 44,
        "summary": "修复登录页面Bug",
        "desc": "登录页面在IE浏览器下显示异常",
        "status": {
          "uuid": "4HfKoazf",
          "name": "待处理",
          "category": "to_do"
        },
        "priority": {
          "uuid": "7tKAV46c",
          "value": "高"
        },
        "assign": {
          "uuid": "DU6krHBN",
          "name": "张三",
          "email": "zhangsan@example.com"
        },
        "owner": {
          "uuid": "DU6krHBN",
          "name": "张三"
        },
        "createTime": 1566182532175312,
        "deadline": 1567296000,
        "issueType": {
          "uuid": "GLLfcQxq",
          "name": "缺陷"
        },
        "project": {
          "uuid": "DU6krHBNXuPAbpv8",
          "name": "产品开发项目"
        },
        "sprint": {
          "uuid": "3XX1trc1",
          "name": "Sprint 1"
        }
      }
    ]
  }
}
```

### 3.4 按负责人筛选

```graphql
{
  tasks(filter: { assign_in: ["用户UUID"] }) {
    uuid
    name
    assign { uuid name }
    status { uuid name category }
  }
}
```

### 3.5 按创建人筛选

```graphql
{
  tasks(filter: { owner_in: ["用户UUID"] }) {
    uuid
    name
    owner { uuid name }
  }
}
```

### 3.6 按任务类型筛选 (缺陷/需求/任务)

```graphql
{
  tasks(filter: { issueType_in: ["任务类型UUID"] }) {
    uuid
    name
    issueType { uuid name }
  }
}
```

### 3.7 按状态筛选

```graphql
{
  tasks(
    filter: {
      status: { uuid_in: ["状态UUID"] }
    }
  ) {
    uuid
    name
    status { uuid name category }
  }
}
```

**按状态分类筛选:**
```graphql
{
  tasks(
    filter: {
      status: { category_in: ["to_do", "in_progress"] }
    }
  ) {
    uuid
    name
    status { uuid name category }
  }
}
```

### 3.8 按创建时间筛选

**方法1 - 使用快捷时间范围:**
```graphql
{
  tasks(
    filter: {
      createTime_range: { quick: "last_30_days" }
    }
  ) {
    uuid
    name
    createTime
  }
}
```

**方法2 - 使用日期范围:**
```graphql
{
  tasks(
    filter: {
      createTime_range: {
        from: "2024-01-01",
        to: "2024-12-31"
      }
    }
  ) {
    uuid
    name
    createTime
  }
}
```

### 3.9 按截止日期筛选

```graphql
{
  tasks(
    filter: {
      deadline_range: { quick: "this_week" }
    }
  ) {
    uuid
    name
    deadline
  }
}
```

### 3.10 按标题模糊搜索

```graphql
{
  tasks(
    filter: {
      name_match: "搜索关键词"
    }
  ) {
    uuid
    name
  }
}
```

> ⚠️ `name_match` 应放在 filter 条件的最下面以提高筛选性能

### 3.11 按迭代筛选

```graphql
{
  tasks(filter: { sprint_in: ["迭代UUID"] }) {
    uuid
    name
    sprint { uuid name }
  }
}
```

### 3.12 组合筛选示例

```graphql
{
  tasks(
    filter: {
      project_in: ["项目UUID"]
      assign_in: ["用户UUID"]
      issueType_in: ["缺陷类型UUID"]
      status: { category_in: ["to_do", "in_progress"] }
      createTime_range: { quick: "last_30_days" }
    }
    orderBy: { createTime: DESC }
  ) {
    uuid
    name
    number
    summary
    status { uuid name category }
    priority { uuid value }
    assign { uuid name }
    owner { uuid name }
    createTime
    deadline
  }
}
```

---

## 4. 分页查询

### 4.1 使用 buckets 分页

**请求:**
```graphql
{
  buckets(
    groupBy: { tasks: {} }
    pagination: {
      first: 10
      after: "游标值"
      preciseCount: false
    }
  ) {
    key
    pageInfo {
      count
      totalCount
      startCursor
      endCursor
      hasNextPage
      unstable
    }
    tasks(
      filter: { project_in: ["项目UUID"] }
      orderBy: { number: ASC }
    ) {
      uuid
      number
      name
    }
  }
}
```

**Pagination 参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| first | int | 向后翻页获取的数量 (默认0) |
| after | string | 向后翻页的游标 (空字符串=从头开始) |
| last | int | 向前翻页获取的数量 (默认0) |
| before | string | 向前翻页的游标 (空字符串=从末尾开始) |
| limit | int | 获取数量 (可替代first/last) |
| preciseCount | boolean | 是否返回精确总数 (false更快但不精确) |

**PageInfo 响应字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| count | int | 当前页数据条数 |
| totalCount | int | 总数据条数 |
| startCursor | string | 当前页起始游标 |
| endCursor | string | 当前页结束游标 |
| hasNextPage | boolean | 是否有下一页 |
| unstable | boolean | 数据是否不稳定 |

**响应示例:**
```json
{
  "data": {
    "buckets": [
      {
        "key": "bucket.0.__all",
        "pageInfo": {
          "count": 10,
          "totalCount": 177,
          "startCursor": "70bbN1HY6ZkKAAAAdGFzay1HQXk2dUwzbVhTY0o0SmRq",
          "endCursor": "70bbN1HY6ZkTAAAAdGFzay1HQXk2dUwzbUVadHZlS1Vu",
          "hasNextPage": true,
          "unstable": false
        },
        "tasks": [
          { "number": 11, "uuid": "GAy6uL3mXScJ4Jdj", "name": "任务1" },
          { "number": 12, "uuid": "GAy6uL3mTy9xJ656", "name": "任务2" }
        ]
      }
    ]
  }
}
```

---

## 5. 项目查询 (Projects)

### 5.1 获取所有产品 (GraphQL)

```graphql
{
  products(orderBy: { createTime: DESC }) {
    uuid
    name
    key
    owner { uuid name }
    assign { uuid name }
    createTime
    taskCount
    taskCountToDo
    taskCountInProgress
    taskCountDone
  }
}
```

**Product 字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 产品UUID |
| name | string | 产品名称 |
| key | string | 产品key |
| owner | User | 创建者 |
| assign | User | 负责人 |
| createTime | int | 创建时间 |
| taskCount | int | 总任务数 |
| taskCountToDo | int | 待处理任务数 |
| taskCountInProgress | int | 进行中任务数 |
| taskCountDone | int | 已完成任务数 |

### 5.2 获取当前用户项目列表 (REST API)

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/projects/my_project
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |
| Referer | https://{host} | 推荐 |

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| projects | array | 项目列表 |
| projects[].uuid | string | 项目UUID |
| projects[].name | string | 项目名称 |
| projects[].assign | string | 负责人UUID |
| projects[].status_uuid | string | 状态UUID |
| projects[].status_category | string | 状态分类 |
| projects[].announcement | string | 项目公告 |
| projects[].deadline | int | 截止日期 |
| projects[].is_pin | boolean | 是否置顶 |
| projects[].status | int | 项目状态 (1=正常) |
| projects[].task_update_time | int | 任务最后更新时间 |
| projects[].program_uuid | string | 所属项目集UUID |
| archive_projects | array | 归档项目列表 |
| server_update_stamp | int | 服务器更新时间戳 |

**响应示例:**
```json
{
  "projects": [
    {
      "uuid": "DU6krHBNRJ8sVGyN",
      "name": "产品开发项目",
      "assign": "DU6krHBN",
      "status_uuid": "to_do",
      "status_category": "to_do",
      "announcement": "",
      "deadline": 0,
      "is_pin": false,
      "status": 1,
      "is_open_email_notify": false,
      "task_update_time": 1565863546,
      "program_uuid": ""
    }
  ],
  "archive_projects": [],
  "server_update_stamp": 1566200426835856
}
```

---

## 6. 任务类型查询 (Issue Types)

### 6.1 获取项目的任务类型

```graphql
{
  issueTypes(
    filter: {
      projects: { uuid_in: ["项目UUID"] }
    }
  ) {
    uuid
    name
    icon
  }
}
```

**响应示例:**
```json
{
  "data": {
    "issueTypes": [
      { "uuid": "GLLfcQxq", "name": "需求", "icon": "requirement" },
      { "uuid": "4sBPV4Eh", "name": "缺陷", "icon": "bug" },
      { "uuid": "3D2UjSN6", "name": "任务", "icon": "task" }
    ]
  }
}
```

### 6.2 获取子任务类型

```graphql
{
  issueTypes(
    filter: {
      projects: { uuid_in: ["项目UUID"] }
      subIssueType_in: [true]
    }
  ) {
    uuid
    name
  }
}
```

---

## 7. 工作项操作 (REST API)

### 7.1 添加工作项

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/tasks/add2
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |
| Referer | https://{host} | 推荐 |

**调用权限:** `create_tasks`

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| tasks | array | ✅ | 要创建的工作项列表 |
| tasks[].uuid | string | ✅ | 工作项UUID (创建者uuid + 随机8位字符) |
| tasks[].owner | string | ✅ | 创建者UUID |
| tasks[].assign | string | ✅ | 负责人UUID |
| tasks[].summary | string | ✅ | 任务标题 |
| tasks[].project_uuid | string | ✅ | 项目UUID |
| tasks[].issue_type_uuid | string | ✅ | 任务类型UUID |
| tasks[].parent_uuid | string | ❌ | 父任务UUID (创建子任务时) |
| tasks[].desc_rich | string | ❌ | 富文本描述 (HTML格式) |
| tasks[].priority | string | ❌ | 优先级UUID |
| tasks[].deadline | int | ❌ | 截止日期 (Unix时间戳，秒) |
| tasks[].sprint_uuid | string | ❌ | 迭代UUID |
| tasks[].field_values | array | ❌ | 自定义属性值列表 |

> 📝 **UUID生成规则:** 创建者UUID(8位) + 随机8位字符 = 16位

**请求体示例:**
```json
{
  "tasks": [
    {
      "uuid": "DU6krHBNNKSnnHNj",
      "owner": "DU6krHBN",
      "assign": "DU6krHBN",
      "summary": "新建任务标题",
      "parent_uuid": "",
      "project_uuid": "DU6krHBNXuPAbpv8",
      "issue_type_uuid": "GLLfcQxq",
      "desc_rich": "<p>任务描述内容</p>",
      "priority": "7tKAV46c",
      "field_values": []
    }
  ]
}
```

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| tasks | array | 创建成功的工作项列表 |
| tasks[].uuid | string | 工作项UUID |
| tasks[].number | int | 工作项编号 |
| tasks[].status | int | 状态 (1=正常) |
| tasks[].status_uuid | string | 状态UUID |
| tasks[].create_time | int | 创建时间 (微秒) |
| tasks[].server_update_stamp | int | 服务器更新时间戳 |
| tasks[].field_values | array | 属性值列表 |
| tasks[].watchers | array | 关注者UUID列表 |
| bad_tasks | array | 创建失败的任务列表 |

**响应示例:**
```json
{
  "tasks": [
    {
      "uuid": "DU6krHBNNKSnnHNj",
      "owner": "DU6krHBN",
      "assign": "DU6krHBN",
      "tags": "",
      "sprint_uuid": null,
      "project_uuid": "DU6krHBNXuPAbpv8",
      "issue_type_uuid": "GLLfcQxq",
      "sub_issue_type_uuid": "",
      "status_uuid": "4HfKoazf",
      "create_time": 1566182532175312,
      "deadline": null,
      "status": 1,
      "summary": "新建任务标题",
      "desc": "任务描述内容",
      "desc_rich": "<p>任务描述内容</p>",
      "parent_uuid": "",
      "position": 0,
      "number": 44,
      "priority": "7tKAV46c",
      "assess_manhour": 0,
      "total_manhour": 0,
      "remaining_manhour": null,
      "watchers": ["DU6krHBN"],
      "field_values": [
        {
          "field_uuid": "field001",
          "type": 2,
          "value": "新建任务标题",
          "value_type": 0
        }
      ],
      "server_update_stamp": 1566182532300576,
      "subtasks": [],
      "path": "DU6krHBNNKSnnHNj"
    }
  ],
  "bad_tasks": []
}
```

### 7.2 更新工作项

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/tasks/update3
```

> 📝 `update2` 用于手机App，`update3` 用于Web端（速度更快）

**调用权限:** `update_tasks`

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| tasks | array | ✅ | 要更新的工作项列表 |
| tasks[].uuid | string | ✅ | 工作项UUID |
| tasks[].summary | string | ❌ | 标题 |
| tasks[].desc_rich | string | ❌ | 富文本描述 |
| tasks[].assign | string | ❌ | 负责人UUID |
| tasks[].status_uuid | string | ❌ | 状态UUID |
| tasks[].priority | string | ❌ | 优先级UUID |
| tasks[].deadline | int | ❌ | 截止日期 (Unix时间戳，秒) |
| tasks[].sprint_uuid | string | ❌ | 迭代UUID |
| tasks[].field_values | array | ❌ | 自定义属性值列表 |

**不可更新字段:**
`watchers`, `owner`, `create_time`, `update_time`, `number`, `total_manhour`, `assess_manhour`, `remaining_manhour`, `estimate_variance`, `time_progress`

**请求体示例:**
```json
{
  "tasks": [
    {
      "uuid": "DU6krHBNNKSnnHNI",
      "status_uuid": "newStatusUUID",
      "assign": "newAssignUUID",
      "desc_rich": "<p>更新后的描述内容</p>"
    }
  ]
}
```

**响应参数:** 同添加工作项

### 7.3 删除工作项

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/tasks/delete
```

**调用权限:** `delete_tasks`

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| tasks | array | ✅ | 要删除的任务UUID列表 |

**请求体示例:**
```json
{
  "tasks": ["DU6krHBNNKSnnHNj"]
}
```

**响应示例:**
```json
{
  "server_update_stamp": 1566200426835856
}
```

---

## 8. 属性查询 (Fields)

### 8.1 获取工作项属性定义

```graphql
{
  fields(
    filter: {
      pool_in: ["task"],
      context: { type_equal: "team" }
    }
  ) {
    uuid
    name
    fieldType
    allowEmpty
    required
    builtIn
    defaultValue
    aliases
  }
}
```

**Field 响应字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 属性UUID |
| name | string | 属性显示名称 |
| fieldType | string | 属性类型 (text/status/option等) |
| allowEmpty | boolean | 是否允许为空 |
| required | boolean | 是否必填 |
| builtIn | boolean | 是否为固有属性 |
| defaultValue | any | 默认值 |
| aliases | string[] | 属性别名列表 |

**响应示例:**
```json
{
  "data": {
    "fields": [
      {
        "aliases": ["uuid"],
        "allowEmpty": false,
        "builtIn": true,
        "defaultValue": null,
        "fieldType": "text",
        "name": "[UUID]",
        "required": false,
        "uuid": null
      },
      {
        "aliases": ["status"],
        "allowEmpty": false,
        "builtIn": false,
        "defaultValue": null,
        "fieldType": "status",
        "name": "任务状态",
        "required": false,
        "uuid": "field_status_uuid"
      }
    ]
  }
}
```

**属性筛选语法:**
| builtIn | 语法格式 | 示例 |
|---------|----------|------|
| `true` | `field_operand` | `assign_in: [...]` |
| `false` | `_field_operand` | `_LNCtECAx_in: [...]` |

---

## 9. 工时操作 (Manhour)

### 9.1 添加工时 (GraphQL Mutation)

```graphql
mutation {
  addManhour(
    task: "{任务UUID}"
    hours: 100000
    start_time: 1598966836
    type: estimated
    description: "工作内容描述"
    owner: "{用户UUID}"
    hours_format: "avg"
  ) {
    key
    hours
    type
    description
    startTime
    owner { uuid name }
    task { key name }
  }
}
```

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| task | string | ✅ | 任务UUID |
| mode | string | ✅ | 工时登记模式，需与团队设置一致；实测值为 `"detailed"` |
| hours | int | ✅ | 工时数值，800000 = 8小时，100000 = 1小时（与登录响应 `teams[].workhours` 同比例） |
| start_time | int | ✅ | 开始时间 (Unix时间戳，秒) |
| type | enum | ✅ | 工时类型: estimated(预估)/recorded(登记) |
| description | string | ❌ | 工作内容描述 |
| owner | string | ✅ | 工时记录者UUID |
| hours_format | string | ❌ | 工时格式 |

> ⚠️ `mode` 为必填，缺少时报 `MissingParameter.Manhour.mode`；值需与团队工时模式匹配，不匹配报 409 `ModeChangedByManager`。实测 `"detailed"` 为正确值。
> ⚠️ `hours` 单位不是毫秒，而是与团队 `workhours` 配置相同的比例单位（登录响应 `teams[].workhours` 字段值即 8 小时对应值）。

### 9.2 查询工时

```graphql
query {
  manhours(
    filter: {
      owner_in: ["{用户UUID}"],
      task_in: ["{任务UUID}"]
    }
    orderBy: {
      createTime: DESC,
      startTime: DESC
    }
  ) {
    key
    hours
    startTime
    description
    type
    owner { uuid name avatar }
  }
}
```

**Manhour 响应字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| key | string | 工时记录key |
| hours | int | 工时数值（800000 = 8小时，100000 = 1小时） |
| startTime | int | 开始时间 |
| description | string | 描述 |
| type | string | 类型 (estimated/recorded) |
| owner | User | 记录者 |

### 9.3 修改工时

```graphql
mutation {
  updateManhour(
    key: "manhour-2CjkDZto"
    hours: 2000000
  ) {
    key
    hours
    type
    owner { uuid name }
  }
}
```

### 9.4 删除工时

```graphql
mutation {
  deleteManhour(key: "manhour-BEA9LMgd") {
    key
  }
}
```

---

## 10. 常用状态分类

| category | 说明 | 常见状态名 |
|----------|------|-----------|
| `to_do` | 未开始 | 待处理、待开发、待评审 |
| `in_progress` | 进行中 | 开发中、测试中、修复中 |
| `done` | 已完成 | 已完成、已关闭、已验收 |

---

## 11. 错误处理

### 11.1 常见错误码

| HTTP状态码 | errcode | 说明 |
|------------|---------|------|
| 200 | - | 成功 |
| 401 | Unauthorized | Token无效或过期 |
| 401 | AuthFailure.CaptchaWrong | 登录需要图形验证码（见 §11.4） |
| 403 | Forbidden | 无权限访问 |
| 500 | ServerError | GraphQL语法错误或参数不匹配 |
| 813 | - | 账号过期 |

### 11.2 错误响应格式

```json
{
  "code": 500,
  "errcode": "ServerError",
  "type": "ServerError"
}
```

### 11.3 账号过期响应

```json
{
  "is_owner": true,
  "expire_time": 1578053867,
  "csm": {
    "email": "support@ones.ai",
    "name": "客服",
    "title": "客户成功经理",
    "phone": "400-xxx-xxxx"
  }
}
```

### 11.4 首次获取 Token

ONES token **永久有效**（官方文档明确：无过期时间），只需获取一次。

引导用户：
1. 浏览器打开 `https://nones.xylink.com` 并登录
2. F12 → Application → Cookies → `nones.xylink.com`
3. 将 `ones-lt` 和 `ones-uid` 的值告诉 Agent

Agent 收到后自行写入 `~/.xyinfpilot/.env` 并继续执行任务：
```
ONES_TOKEN=<ones-lt 的值>
ONES_USER_UUID=<ones-uid 的值>
```

Token 失效场景（仅以下情况）：改密码 / 被移出团队 / 主动登出 → 重新执行上述步骤。

---

## 12. 完整调用示例

### 12.1 cURL 示例 - 查询我负责的缺陷

```bash
curl -X POST \
  'https://ones.example.com/project/api/project/team/{teamUUID}/items/graphql' \
  -H 'Content-Type: application/json' \
  -H 'Ones-Auth-Token: {token}' \
  -H 'Ones-User-Id: {user_uuid}' \
  -d '{
    "query": "{ tasks(filter: { assign_in: [\"{user_uuid}\"], issueType_in: [\"{缺陷类型UUID}\"], createTime_range: { quick: \"last_30_days\" } }, orderBy: { createTime: DESC }) { uuid name number status { name category } priority { value } createTime deadline } }"
  }'
```

### 12.2 Shell 脚本示例

```bash
#!/bin/bash
ONES_HOST="https://ones.example.com"
TEAM_UUID="your_team_uuid"
TOKEN="your_token"
USER_UUID="your_user_uuid"

# GraphQL 查询
QUERY='{ tasks(filter: { assign_in: ["'$USER_UUID'"] }, orderBy: { createTime: DESC }) { uuid name number status { name category } priority { value } } }'

curl -s -X POST \
  "${ONES_HOST}/project/api/project/team/${TEAM_UUID}/items/graphql" \
  -H "Content-Type: application/json" \
  -H "Ones-Auth-Token: ${TOKEN}" \
  -H "Ones-User-Id: ${USER_UUID}" \
  -d "{\"query\": \"$QUERY\"}" | jq .
```

---

## 13. 工作项详情查询 (REST API)

### 13.1 根据 UUID 或序号获取工作项详情

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/task/{taskUUIDOrNumber}/info
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |
| Referer | https://{host} | 推荐 |

**调用权限:** `view_tasks`

**路径参数:**
| 参数 | 说明 |
|------|------|
| taskUUIDOrNumber | 工作项UUID(16位) 或 工作项序号(数字) |

**响应:** 完整的工作项对象，包含所有属性、子任务、field_values 等

### 13.2 批量获取工作项详情

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/tasks/info?ids={uuid1},{uuid2}
POST https://{host}/project/api/project/team/{teamUUID}/tasks/info
```

**GET 方式参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| ids | string | 逗号分隔的UUID列表 |

**POST 方式请求体:**
```json
{
  "ids": ["uuid1", "uuid2"]
}
```

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| tasks | array | 工作项列表 |
| count | int | 成功获取数量 |
| errors | array | 失败的工作项和错误码 |

---

## 14. 状态流转 (Transit)

### 14.1 获取工作项可用的状态流转

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/transitions
```

**请求头:** 同认证请求头

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| transitions | array | 可用的状态流转列表 |
| transitions[].uuid | string | 流转UUID |
| transitions[].name | string | 流转名称 |
| transitions[].start_status_uuid | string | 起始状态UUID |
| transitions[].end_status_uuid | string | 目标状态UUID |

**响应示例:**
```json
{
  "transitions": [
    {
      "uuid": "XFqxUtYS",
      "name": "编码",
      "start_status_uuid": "91eU4d1d",
      "end_status_uuid": "QqwAjenN"
    },
    {
      "uuid": "DnJMePHp",
      "name": "联调",
      "start_status_uuid": "91eU4d1d",
      "end_status_uuid": "QzsnSzWt"
    }
  ]
}
```

### 14.2 执行状态流转

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/transit
```

**请求头:** 同认证请求头

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| transition_uuid | string | ✅ | 流转UUID（从 transitions 接口获取） |

**请求体示例:**
```json
{
  "transition_uuid": "XFqxUtYS"
}
```

**响应示例:**
```json
{
  "code": 200,
  "errcode": "OK",
  "type": "OK"
}
```

> ⚠️ **重要说明:**
> - 状态流转受工作流约束，不能直接通过 `update3` 的 `status_uuid` 修改状态
> - 必须先调用 `transitions` 获取当前状态可流转的目标，再用 `transit` 执行流转
> - 如果尝试非法流转，会返回 `403 AccessDenied.Transition`

---

## 15. 任务讨论/评论 (Message)

### 15.1 发送评论到任务讨论

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/send_message
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |
| Referer | https://{host} | 推荐 |

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| uuid | string | ✅ | **消息UUID**（非用户UUID），每次发送必须新生成唯一值，如 `uuid.uuid4().hex[:8]`；重复提交同一值返回 409 |
| text | string | 与resource_uuid二选一 | 评论文本内容，换行用 `\n` |
| resource_uuid | string | 与text二选一 | 关联资源UUID |

**请求体示例:**
```json
{
  "uuid": "a3f9c2d1",
  "text": "已知晓，正在排查处理中。"
}
```

**响应示例:**
```json
{
  "code": 200,
  "errcode": "OK",
  "type": "OK"
}
```

**HTTP状态码:** 200(成功)、400(参数错误)、403(权限不足)、404(任务不存在)、409(uuid重复，重新生成后重试)

> ⚠️ **注意**：`nones.xylink.com` 使用内网自签证书，所有 HTTPS 请求需跳过 SSL 校验（curl 加 `-k`，Python 使用 `ssl.CERT_NONE`）。

### 15.2 获取任务讨论消息

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/messages?since={timestamp}&max={timestamp}&count={count}
```

**URL参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| since | int64 | 最小时间戳(不包含)，纳秒 |
| max | int64 | 最大时间戳(不包含)，纳秒 |
| count | int | 返回消息最大数量(最大100) |

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| messages | array | 消息列表 |
| messages[].uuid | string | 消息UUID |
| messages[].ref_type | string | 引用类型 (task/project) |
| messages[].ref_id | string | 引用ID |
| messages[].type | string | 消息类型 (discussion/system) |
| messages[].from | string | 发送者UUID (BOT=系统) |
| messages[].to | string | 目标UUID |
| messages[].send_time | int64 | 发送时间 (纳秒) |
| messages[].text | string | 评论内容 |
| count | int | 消息数量 |
| has_next | boolean | 是否有更多消息 |

**响应示例:**
```json
{
  "messages": [
    {
      "uuid": "3wkkE4zc",
      "ref_type": "task",
      "ref_id": "8RnWsWnmFqbkedbN",
      "type": "discussion",
      "from": "8RnWsWnm",
      "to": "8RnWsWnmFqbkedbN",
      "send_time": 1460543624049663,
      "text": "已知晓，正在排查处理中。"
    }
  ],
  "count": 1,
  "has_next": false
}
```

---

## 16. 工作项统计 (Task Stats)

### 16.1 获取工作项统计数据

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/task_stats
```

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| task_count_by_project | array | 各项目的任务统计 (to_do/in_progress/done) |
| task_count_by_sprint | array | 各迭代的任务统计 |
| server_update_stamp | int | 服务器更新时间戳 |

---

## 17. 复制工作项

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/copy
```

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| project_uuid | string | ✅ | 目标项目UUID |
| issue_type_uuid | string | ✅ | 目标工作项类型UUID |

**响应:** 新复制任务的完整对象

---

## 18. 消息通知

### 18.1 根据团队获取消息通知列表

**URL:**
```
POST https://{host}/project/api/project/organization/{orgUUID}/list_notice
```

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| team_uuids | array | ✅ | 团队UUID列表 |
| since | int64 | ✅ | 开始时间 (秒) |

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| notices | array | 通知列表 |
| notices[].task_uuid | string | 工作项UUID |
| notices[].is_read | boolean | 是否已读 |
| notices[].message | object | 消息对象 |

### 18.2 筛选项目消息通知

**URL:**
```
POST https://{host}/project/api/project/team/{teamUUID}/filter_message
```

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| project | string | ✅ | 项目UUID (空=全部) |
| user | string | ✅ | 用户UUID (空=全部) |
| begin | int64 | ✅ | 开始时间 (纳秒) |
| end | int64 | ✅ | 结束时间 (纳秒，间隔不超7天) |

---

## 19. 工作项附件下载 (Attachments)

本章提供附件下载的完整使用方法，适用于用户要求“下载某工作项的附件”场景。

### 19.1 获取工作项附件列表

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/task/{taskUUID}/attachments?count={count}
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |

**URL参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| count | int | 否 | 返回数量上限，建议 100 |

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| count | int | 附件数量 |
| has_next | boolean | 是否有更多附件 |
| attachments | array | 附件列表 |
| attachments[].uuid | string | 附件UUID |
| attachments[].name | string | 文件名 |
| attachments[].mime | string | MIME类型 |
| attachments[].size | int | 文件字节数 |
| attachments[].create_time | int64 | 创建时间（微秒） |
| attachments[].url | string | 可能为空，不建议直接依赖 |

**响应示例:**
```json
{
  "count": 1,
  "has_next": false,
  "attachments": [
    {
      "uuid": "LJaCRBgS",
      "name": "终端运行日志_2026-02-07_09-48-30.zip",
      "mime": "application/zip",
      "size": 16321477,
      "create_time": 1772265292820622,
      "url": ""
    }
  ]
}
```

### 19.2 获取附件详情和临时下载链接

**URL:**
```
GET https://{host}/project/api/project/team/{teamUUID}/res/attachment/{attachmentUUID}
```

**请求头:** 同上

**响应参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| uuid | string | 附件UUID |
| ref_type | string | 关联对象类型（如 task） |
| ref_id | string | 关联工作项UUID |
| name | string | 文件名 |
| mime | string | MIME类型 |
| size | int | 文件字节数 |
| hash | string | 文件哈希标识 |
| url | string | 临时签名下载URL（有时效） |

**响应示例:**
```json
{
  "uuid": "LJaCRBgS",
  "type": "file",
  "ref_type": "task",
  "ref_id": "FfJduo1aF9I2EOjV",
  "name": "终端运行日志_2026-02-07_09-48-30.zip",
  "mime": "application/zip",
  "size": 16321477,
  "hash": "lk83oGhw_0ibgxgFNSHhgZjiFJAA",
  "url": "https://{host}/api/project/file/attachment/{hash}?e=...&token=..."
}
```

### 19.3 详细使用流程（按工作项编号下载全部附件）

#### Step 1：工作项编号转 taskUUID

先调用 GraphQL 查询工作项 UUID：

```graphql
{
  tasks(filter: { number_in: [593934] }) {
    uuid
    number
    name
  }
}
```

#### Step 2：获取附件列表

调用 `GET /task/{taskUUID}/attachments?count=100` 获取 `attachments[].uuid`。

#### Step 3：逐个获取下载链接并下载

对每个 `attachmentUUID` 调用 `GET /res/attachment/{attachmentUUID}`，取返回 `url` 后立即下载。

#### Step 4：下载后做大小校验

对比 API 的 `size` 与本地文件实际字节数，不一致则标记为失败并重试。

#### Shell 脚本模板（可直接用）

```bash
#!/usr/bin/env bash
set -euo pipefail

ONES_HOST="https://nones.xylink.com"
TEAM_UUID="<team_uuid>"
TOKEN="<token>"
USER_UUID="<user_uuid>"
TASK_NUMBER="${1:-593934}"
TARGET_DIR="$HOME/Downloads/ones-${TASK_NUMBER}-attachments"
mkdir -p "$TARGET_DIR"

# 1) 编号 -> taskUUID
TASK_UUID=$(
  curl -sS -X POST "${ONES_HOST}/project/api/project/team/${TEAM_UUID}/items/graphql" \
    -H "Content-Type: application/json" \
    -H "Ones-Auth-Token: ${TOKEN}" \
    -H "Ones-User-Id: ${USER_UUID}" \
    -d "{\"query\":\"{ tasks(filter:{ number_in:[${TASK_NUMBER}] }) { uuid } }\"}" \
  | jq -r '.data.tasks[0].uuid // empty'
)

if [ -z "$TASK_UUID" ]; then
  echo "未找到工作项编号: ${TASK_NUMBER}，或当前账号无权限。"
  exit 1
fi

# 2) 获取附件列表
ATT_JSON=$(
  curl -sS -X GET "${ONES_HOST}/project/api/project/team/${TEAM_UUID}/task/${TASK_UUID}/attachments?count=100" \
    -H "Content-Type: application/json" \
    -H "Ones-Auth-Token: ${TOKEN}" \
    -H "Ones-User-Id: ${USER_UUID}"
)

ATT_COUNT=$(printf '%s' "$ATT_JSON" | jq -r '.count // 0')
if [ "$ATT_COUNT" = "0" ]; then
  echo "工作项 ${TASK_NUMBER} 无附件。"
  exit 0
fi

REPORT="${TARGET_DIR}/download-report.tsv"
printf 'uuid\tname\texpected_size\tactual_size\tstatus\tpath\n' > "$REPORT"

# 3) 逐个下载并校验
printf '%s' "$ATT_JSON" | jq -r '.attachments[].uuid' | while IFS= read -r ATT_UUID; do
  DETAIL=$(
    curl -sS -X GET "${ONES_HOST}/project/api/project/team/${TEAM_UUID}/res/attachment/${ATT_UUID}" \
      -H "Content-Type: application/json" \
      -H "Ones-Auth-Token: ${TOKEN}" \
      -H "Ones-User-Id: ${USER_UUID}"
  )

  NAME=$(printf '%s' "$DETAIL" | jq -r '.name')
  URL=$(printf '%s' "$DETAIL" | jq -r '.url')
  EXPECTED=$(printf '%s' "$DETAIL" | jq -r '.size')
  OUT="${TARGET_DIR}/${NAME}"

  # 避免重名覆盖
  if [ -e "$OUT" ]; then
    OUT="${TARGET_DIR}/${ATT_UUID}_${NAME}"
  fi

  if curl -fL --retry 2 --connect-timeout 15 --max-time 300 -o "$OUT" "$URL" >/dev/null 2>&1; then
    ACTUAL=$(stat -f%z "$OUT")
    if [ "$ACTUAL" = "$EXPECTED" ]; then
      STATUS="ok"
    else
      STATUS="size_mismatch"
    fi
  else
    ACTUAL=0
    STATUS="download_failed"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$ATT_UUID" "$NAME" "$EXPECTED" "$ACTUAL" "$STATUS" "$OUT" >> "$REPORT"
done

echo "下载目录: ${TARGET_DIR}"
echo "报告文件: ${REPORT}"
```

### 19.4 常见问题与排查

1. `AuthFailure.CaptchaWrong`：账号登录需要验证码。优先复用已登录会话 token（`ones-lt`）与 user id（`ones-uid`）。
2. `404`（附件接口）：路径写错。附件列表应使用 `/task/{taskUUID}/attachments`，附件详情应使用 `/res/attachment/{attachmentUUID}`。
3. 列表返回 `count=0`：该工作项确实无附件，或当前账号无可见权限。
4. 下载 URL 失效：`url` 为临时签名链接，过期后重新调用附件详情接口获取新链接。
5. 大小不一致：网络中断或下载不完整，建议重试并保留校验报告。

---

## 20. Wiki 页面获取 (Wiki Pages)

本章用于“按 ONES Wiki 链接读取页面内容”场景。给定链接示例：

`https://nones.xylink.com/wiki/#/team/AQzvsooq/space/CGENJVj8/page/5E8iYrdn`

可直接解析出：`teamUUID=AQzvsooq`、`spaceUUID=CGENJVj8`、`pageUUID=5E8iYrdn`。

### 20.1 URL 解析规则

- 入口路由：`/wiki/#/team/{teamUUID}/space/{spaceUUID}/page/{pageUUID}`
- 若链接中已包含 `spaceUUID`，优先走带 `space` 的页面详情接口
- 若仅有 `pageUUID`，先调用不带 `space` 的详情接口反查 `space_uuid`

### 20.2 获取页面详情（推荐，带 space 路由）

**URL:**
```
GET https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/page/{pageUUID}?version=0
```

**请求头:**
| Header | 值 | 必填 |
|--------|---|-----|
| Content-Type | application/json | ✅ |
| Ones-Auth-Token | {token} | ✅ |
| Ones-User-Id | {user_uuid} | ✅ |

**URL参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| version | int | 否 | 版本号。**不传** = 最新版；`0` = 初始版（第 0 版）；`N` = 第 N 版 |

**关键返回字段:**
| 字段 | 类型 | 说明 |
|------|------|------|
| uuid | string | 页面 UUID |
| space_uuid | string | 页面组 UUID |
| title | string | 页面标题 |
| content | string | 页面内容（HTML） |
| version | int | 页面版本 |
| updated_time | int | 更新时间（秒） |

### 20.3 获取页面详情（不带 space 路由）

**URL:**
```
GET https://{host}/wiki/api/wiki/team/{teamUUID}/page/{pageUUID}?version=0
```

适用场景：只有 `pageUUID`，需要先获得 `space_uuid` 或快速读取页面。

### 20.4 获取页面组页面列表（用于导航/校验）

**URL:**
```
GET https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/pages?status=1
```

**说明：**
- `status=1`：正常页面
- 可用于校验目标页面是否在指定页面组内，以及生成页面树索引

### 20.5 常见问题

1. 返回 404：`pageUUID` 或 `spaceUUID` 不存在，或页面无访问权限。
2. 返回 401：token 失效（改密码/登出后常见），需重新获取 `ones-lt`。
3. 返回内容无 `content`：可能命中权限/加密页策略，需确认账号对页面的可见权限。
4. 请求路径写错：Wiki 接口必须走 `/wiki/api/wiki/...`，不能走 `/project/api/project/...`。
5. **`?version=0` 不是最新版**：`version=0` 取的是第 0 版（初始版），要取最新版必须**不传 version 参数**。
6. **content 返回 JSON 字符串**（如 `{"version":173...}`）：说明页面使用新版协同编辑器格式，实际渲染内容在前端处理，API 层面该字段不含可读文本。

---

## 21. Wiki 页面写入 (Wiki Write)

ONES **没有直接更新页面内容的接口**，必须通过"创建草稿 → 发布草稿"三步完成写入。

> ⚠️ **重要限制：新版协同编辑器页面无法通过 API 写入内容**
>
> 判断方法：GET 页面详情，若返回 `ref_type: 6`（含 `ref_uuid` 字段），说明页面使用新版协同编辑器。
> 此类页面的实际内容存储在协同文档（`ref_uuid`）中，浏览器通过 WebSocket 加载，草稿流程只能更新 legacy `content` 字段（浏览器不读取），页面视觉上不会变化。
> 官方公开 API 中**没有**写入协同文档的接口，此类页面只能通过浏览器手动编辑。
>
> **旧版页面**（无 `ref_type` 或 `ref_type != 6`）：草稿流程有效，`content` 字段即浏览器渲染的 HTML。

### 21.1 流程概览

```
Step 1: 读取页面（获取 title/version）
Step 2: 清理旧草稿（若该页已有草稿则删除）
Step 3: 创建页面草稿（drafts/add，status=2）
Step 4: 获取草稿详情（取 from_version/create_time）
Step 5: 发布草稿（draft/{uuid}/update，is_published=true）
```

### 21.2 清理旧草稿

**URL:**
```
GET https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/drafts
```
遍历返回的 `drafts[]`，若 `page_uuid == 目标pageUUID`，则删除：
```
POST https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/draft/{draftUUID}/delete
```
> 跳过此步骤，`drafts/add` 会返回 817（用户已存在页面草稿）。

### 21.3 创建页面草稿

**URL:**
```
POST https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/drafts/add
```

**请求体:**
| 字段 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| page_uuid | string | ✅ | 目标页面 UUID |
| status | int | ✅ | 固定为 `2`（page 页面草稿，区别于 1=space 临时草稿）|
| title | string | ✅ | 页面标题（保持原标题或新标题）|
| content | string | ✅ | 新内容（HTML 格式，如 `<p>文字</p>`）|

**关键返回字段:** `uuid`（draftUUID）、`create_time`

### 21.4 发布草稿

**URL:**
```
POST https://{host}/wiki/api/wiki/team/{teamUUID}/space/{spaceUUID}/draft/{draftUUID}/update
```

**请求体（必须包含完整字段，缺字段返回 500）:**
| 字段 | 类型 | 必填 | 说明 |
|------|------|-----|------|
| uuid | string | ✅ | 草稿 UUID |
| space_uuid | string | ✅ | 页面组 UUID |
| page_uuid | string | ✅ | 页面 UUID |
| from_version | int | ✅ | 取草稿详情的 `from_version`（通常为 `-1`）|
| title | string | ✅ | 页面标题 |
| content | string | ✅ | 新内容（HTML）|
| status | int | ✅ | 固定为 `2` |
| create_time | int | ✅ | 草稿创建时间（微秒，`create_time * 1000000`）|
| updated_time | int | ✅ | 当前时间（微秒，`int(time.time()) * 1000000`）|
| is_published | bool | ✅ | 固定为 `true`，触发发布 |
| is_forced | bool | ✅ | 固定为 `true`，强制覆盖避免版本冲突 |

**成功响应:**
```json
{"team_uuid": "...", "space_uuid": "...", "page_uuid": "...", "draft_uuid": "...", "status": 3}
```
`status: 3` 表示已发布。

### 21.5 常见问题

1. **发布返回 500**：请求体字段不完整，必须包含 21.4 中全部字段。
2. **创建草稿返回 817**：该页已有草稿，先调用删除接口。
3. **创建草稿返回 819**：版本冲突，`is_forced: true` 可强制覆盖。
4. **直接 PUT/POST 页面路径返回 404**：ONES 没有直接更新页面的接口，必须走草稿流程。
5. **时间戳单位**：`create_time`/`updated_time` 字段单位为微秒（秒 × 1000000）。

---


