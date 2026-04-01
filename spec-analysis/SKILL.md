---
name: spec-analysis
description: Use when receiving a new requirement/spec (from ONES wiki, PDF, or text) and need to analyze it before planning or coding. Triggers on "分析需求", "需求分析", "看看这个spec", "analyze spec", "analyze requirement", or when user shares a spec document.
---

# Spec 需求分析

**拿到 Spec，不写代码，不出计划，先把需求聊透。**

7 个 Phase，每步输出后等用户确认再继续。发现模糊点必须标注 `⚠️ 待明确` 让用户决策。

## 流程

```
Spec 获取 → ⓪ 抓取内容 → ① 提炼本质 → ② 划范围 → ③ 影响分析 → ④ 架构挑战 → ⑤ 澄清问题 → ⑥ 确认并落盘
  (URL/PDF/文本)                                                       ↕ 反复讨论
```

## ⓪ 抓取 Spec 内容

**根据输入来源自动选择获取方式：**

- **ONES Wiki URL**（`nones.xylink.com/wiki/...`）→ 走 agent-browser 流程（见下方）
- **PDF 文件** → 用 Read 工具直接读取
- **用户粘贴的文本** → 直接使用

### ONES Wiki 抓取流程（agent-browser CLI）

**必须使用 `agent-browser` CLI 命令（Bash 工具执行），禁止使用 `chrome-devtools` MCP 工具。**

ONES Wiki 需要登录认证，且图片通过 API 加载，必须用 agent-browser 在浏览器上下文中操作。

**Step 1: 打开页面**
```bash
agent-browser open "<URL>" && agent-browser wait --load networkidle
```

**Step 2: 登录（ONES 必须登录，无需检查，直接执行）**

凭证存储在 `~/.xyinfpilot/.env`（`ONES_USERNAME` / `ONES_PASSWORD`），读取后直接填写登录：

```bash
source <(grep -E "ONES_USERNAME|ONES_PASSWORD" ~/.xyinfpilot/.env)
agent-browser snapshot -i
# 直接填写登录表单（邮箱 ref 和密码 ref 从 snapshot 获取）
agent-browser fill @邮箱ref "$ONES_USERNAME"
agent-browser fill @密码ref "$ONES_PASSWORD"
agent-browser click @登录ref
agent-browser wait --load networkidle
```

**Step 3: 提取文本内容**
```bash
agent-browser get text body
```

**Step 4: 提取并下载图片**

一次性下载所有图片到 `/tmp/spec-images/`，然后用 Read 工具查看。

**为避免 shell 转义问题，JS 代码写入临时文件再执行：**

```bash
# 1) 找出所有业务图片 URL
cat <<'JSEOF' > /tmp/find_imgs.js
(function(){
  var imgs = document.querySelectorAll("img"), results = [];
  imgs.forEach(function(img) {
    if (img.naturalWidth > 50 && img.src.indexOf("/wiki/api/wiki/editor/") !== -1)
      results.push({i: results.length, src: img.src, w: img.naturalWidth, h: img.naturalHeight});
  });
  return JSON.stringify(results);
})()
JSEOF
agent-browser eval "$(cat /tmp/find_imgs.js)"

# 2) 批量 fetch 到 window 变量（将上一步的 src 列表填入 srcs 数组）
cat <<'JSEOF' > /tmp/fetch_imgs.js
(function(){
  var srcs = [/* 替换为上一步提取的 src 列表 */];
  var results = [], promises = srcs.map(function(src, i) {
    return fetch(src, {credentials: "include"}).then(function(r) { return r.blob(); }).then(function(blob) {
      return new Promise(function(resolve) {
        var reader = new FileReader();
        reader.onloadend = function() { results.push({i: i, b64: reader.result}); resolve(); };
        reader.readAsDataURL(blob);
      });
    });
  });
  return Promise.all(promises).then(function() {
    window.__specImages = results.sort(function(a, b) { return a.i - b.i; });
    return JSON.stringify({count: results.length});
  });
})()
JSEOF
agent-browser eval "$(cat /tmp/fetch_imgs.js)"

# 3) 逐张导出到本地（用 pageId 作为子目录，避免多需求混淆）
mkdir -p /tmp/spec-images/{pageId}
for i in $(seq 0 $((N-1))); do
  agent-browser eval "(function(){return window.__specImages[$i].b64.split(',')[1]})()" \
    | tr -d '"\n' | base64 -d > "/tmp/spec-images/{pageId}/img_$(printf '%02d' $i).png"
done

# 4) 用 Read 工具查看图片（Read 支持直接查看图片文件）
```

**关键经验：**
- JS 代码写入临时文件再用 `$(cat /tmp/xxx.js)` 传入，避免 shell 转义问题
- `agent-browser eval` 返回带引号的 JSON 字符串，保存前必须 `tr -d '"\n'`
- 必须用浏览器 `fetch(url, {credentials:"include"})` 下载，curl 无法通过认证
- 浏览器 close 后 session 丢失，一次性完成所有操作再 close
- 先批量 fetch 到 `window.__specImages`，再逐张导出，避免反复 fetch

**Step 5: 关闭浏览器**
```bash
agent-browser close
```

**完成后输出：** 告知用户共获取到多少文字内容和多少张图片，列出图片索引表（编号 + 简要描述），然后进入 Phase ①。

## ① 提炼本质

一句话说清这个需求要解决什么问题，用简图还原痛点场景。

**输出格式：**
> **需求本质：** [一句话]
>
> **场景还原：** [简图或文字描述当前痛点]

## ② 划范围

本迭代做什么、不做什么，一张表说清。**Spec 中未明确标注优先级的功能，标记 `⚠️ 待明确` 让用户确认是否纳入本迭代。**

| 本迭代 (P0) | 非本迭代 (P1/P2) |
|-------------|-----------------|
| 功能A       | 功能X (P2)      |

## ③ 影响分析

两张清单同等重要：

**要改的：**
| 模块 | 改什么 | 主要/次要 |
|------|--------|----------|

**不用改的（明确列出，防止过度开发）：**
- ...

## ④ 架构挑战

**这是最关键的一步。** 主动质疑功能归属：

- 这个功能放在 Spec 暗示的服务里合理吗？
- 功能的生命周期跟宿主服务一致吗？（不一致就该拆出来）
- 未来扩展时，当前归属会不会成为障碍？

**判断原则：按生命周期归属，不按 UI 入口归属。**

有结论就给结论，有争议就标 `⚠️ 待明确` 抛给用户讨论。

## ⑤ 澄清问题

**只列对开发有实际影响的问题，不造假设性问题。** 每个问题必须说明：不澄清会导致什么后果。

必查清单（逐项过，有就提，没有就跳过）：
- 存储方案（云/本地/混合）
- 性能约束（并发、超时、大数据量）
- 老版本兼容
- 权限边界条件
- 数据生命周期（留多久、谁清理）
- 异步失败处理
- 服务间数据流转的 key（ID 映射关系）

**格式：**
> 1. `⚠️` [问题] —— 不澄清后果：[xxx]

## ⑥ 确认并落盘

汇总所有分析，生成结构化文档，**保存到项目 `spec/` 目录下**。

### 落盘规则

- **路径**：`spec/{迭代版本号}/{需求简称}.md`
- **命名示例**：`spec/20260626/meeting-doc-upload.md`
- 迭代版本号从 Spec 中提取（如 0626 迭代 → `20260626`），提取不到则问用户
- 需求简称用英文短横线连接，简洁明了

### 文档模板

```markdown
# 需求分析：[标题]

> 分析日期：[YYYY-MM-DD]
> 迭代版本：[版本号]
> Spec 来源：[ONES链接 或 文件路径]

## 1. 需求本质
[一句话]

## 2. 本迭代范围 (P0)
| 功能 | 说明 |
|------|------|

## 3. 非本迭代 (P1/P2)
| 功能 | 优先级 | 说明 |
|------|--------|------|

## 4. 影响范围
### 要改的
| 模块 | 改动内容 | 改动量 |
|------|----------|--------|

### 不用改的
- ...

## 5. 架构决策
| 决策点 | 结论 | 理由 |
|--------|------|------|

## 6. 关键约束（非功能性需求）
| 维度 | 要求 |
|------|------|

## 7. ⚠️ 待明确事项
| # | 问题 | 影响 | 状态 |
|---|------|------|------|
```

**落盘后告知用户文件路径**，后续 Plan Mode 可直接引用此文件。

## 铁律

- **每个 Phase 输出后停下来等用户确认**，不要一口气跑完
- **发现模糊就标 `⚠️ 待明确`**，不要替用户做假设
- **用户判断优先**，AI 提挑战但不做决策
- **表格 > 长文**，简图 > 文字描述
