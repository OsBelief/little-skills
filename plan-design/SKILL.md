---
name: plan-design
description: Use when spec analysis is done and need to create technical design with architecture diagrams and sequence diagrams. Triggers on "技术方案", "设计方案", "出方案", "plan mode", "画序列图", "技术设计", or after spec-analysis is completed.
---

# Plan Mode — 技术方案设计

**需求分析确认后，进入技术方案设计。输出一份带 Mermaid 图的 HTML 文档，可直接浏览器打开。**

## 前置条件

需要 `spec/` 目录下已有确认的需求分析文档（由 `/spec-analysis` 生成）。如果没有，先引导用户完成需求分析。

## 流程

```
读取 spec 分析 → ① 摸清现有服务 → ② 架构设计 → ③ 序列图 → ④ 安全设计 → ⑤ 落盘 HTML
                   （问用户）
```

## ① 摸清现有服务

**先问再画，不要凭空设计。** 必须向用户确认：

- 涉及的功能是新建服务还是在已有服务上扩展？已有服务叫什么？
- 文件/对象存储方案：云端(S3/MinIO) / 本地存储 / NAS？
- 服务间通信方式：REST / gRPC / Kafka / 混合？
- 是否有消息队列？用于什么场景？
- 依赖的外部服务（大模型、ASR、第三方API）接口形态？
- 终端/客户端怎么跟后端交互？直接调API / 信令推送？

**不要假设，全部问清楚。**

## ② 架构设计

基于用户回答，输出：

- **服务职责划分图**：哪个服务管什么，边界清晰
- **数据模型**：核心表结构（ER 图）
- **接口清单**：新增/变更的 REST 接口表

## ③ 序列图

按场景拆分，每个场景一张序列图。典型场景切分：

- 核心主流程（如：上传、查询、下载）
- 异步/事件流程（如：消息消费、定时任务）
- 异常/降级流程

**序列图要标注到具体服务名，不要用泛化的"后端"。**

## ④ 安全设计

**每个方案必须包含安全审查。** 逐项检查：

### 输入校验
- 文件上传：格式白名单校验（不信任 Content-Type，校验文件头魔数）
- 文件大小限制（单文件 + 总量）
- 文件名过滤（防路径穿越：`../`、空字节、特殊字符）
- 上传数量限制（防资源耗尽）

### 存储安全
- 存储路径不可由客户端指定（服务端生成随机路径）
- 文件名重命名存储（原始文件名仅存元数据）
- 存储目录权限隔离（不同会议/租户隔离）

### 访问控制
- 下载/删除接口必须校验权限（不能仅凭 fileId 就能下载）
- 权限校验在服务端执行，不信任前端传的身份
- 敏感操作（删除、批量导出）记录审计日志

### 传输安全
- 文件传输走 HTTPS
- 大文件上传支持断点续传 or 分片上传
- 防重复提交（幂等性）

### 其他
- 30天清理任务要有幂等保护（防止重复删除报错）
- 大模型解析失败不能阻塞主流程
- 并发上传的竞态条件处理（文件数计数准确性）

**有安全风险就在图中用红色 note 标注。**

## ⑤ 落盘 HTML

生成一份**可浏览器直接打开**的 HTML 文档，使用 Mermaid CDN 渲染图表。

### 落盘规则

- **路径**：`spec/{迭代版本号}/{需求简称}-design.html`
- **命名示例**：`spec/20260626/meeting-doc-upload-design.html`
- 与需求分析文档同目录，通过 `-design` 后缀区分

### HTML 模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>[需求标题] — 技术实现方案</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  /* 统一样式：白底卡片、彩色 note 条、表格 */

  /* 强制 Mermaid 图表白底（兼容 IDEA 内置浏览器等深色渲染环境） */
  .mermaid svg { background: #ffffff !important; }
  .mermaid rect.background { fill: #ffffff !important; }
</style>
</head>
<body>

<h1>[标题]</h1>
<p class="subtitle">[一句话描述方案定位]</p>

<!-- 图1: 架构总览 -->
<div class="diagram-container">
  <h2>图1: 架构总览</h2>
  <pre class="mermaid">graph TB ...</pre>
</div>

<!-- 图2: 数据模型 -->
<!-- 图3-N: 各场景序列图 -->
<!-- 安全设计 note -->
<!-- 新增接口表 -->
<!-- ⚠️ 待明确事项 -->

<script>mermaid.initialize({startOnLoad:true, theme: 'default', ...});</script>
</body>
</html>
```

### Mermaid 图表白底要求（必须遵守）

**所有生成的 HTML 文档中，Mermaid 图表必须使用白色背景。** 通过以下两种方式确保：

1. **CSS 强制覆盖**（必加）：
```css
.mermaid svg { background: #ffffff !important; }
.mermaid rect.background { fill: #ffffff !important; }
```

2. **Mermaid 初始化使用 `default` 主题**（不要用 `dark` 或 `forest`）：
```javascript
mermaid.initialize({ startOnLoad: true, theme: 'default' });
```

**原因**：部分环境（如 JetBrains IDE 内置浏览器）会将 Mermaid 默认渲染为深色背景，导致文字不可见。CSS `!important` 覆盖可确保在所有环境下图表都是白底黑字。

### 图表类型对照

| 内容 | Mermaid 图类型 |
|------|-------------|
| 服务职责划分 | `graph TB` |
| 数据模型 | `erDiagram` |
| 各场景交互流程 | `sequenceDiagram` |
| 分支/判断逻辑 | `flowchart TD` |
| 代码结构/类关系 | `classDiagram` |
| 开发计划 | `gantt` |

### 样式规范

- 用 `.note-red` 标注安全风险点
- 用 `.note-green` 标注设计亮点/复用点
- 用 `.note` (黄色) 标注约束条件
- 用 `.note-blue` 标注补充说明
- 每张图后紧跟 note 说明设计意图

## 铁律

- **先问现有服务，再画架构图**，不要凭空设计
- **安全设计不是可选项**，每个方案必须包含
- **序列图标注到具体服务名**，不要用"后端"、"服务器"等泛称
- **HTML 可直接打开**，不依赖本地构建工具
- **落盘后告知用户文件路径**，方便后续开发引用
