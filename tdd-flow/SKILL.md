---
name: tdd-flow
description: Use when ready to start coding after spec analysis and technical design are done. Enforces strict TDD five-step discipline. Triggers on "TDD", "写测试", "先写测试", "开始开发", "tdd-flow", "五步法", or after plan-design is completed.
---

# TDD 五步法 — 让测试锁死需求

**技术方案确认后，不直接写实现，先用测试把需求钉死。**

严格五步，每步等用户确认。AI 不得跳步、不得偷写实现、不得篡改已提交的测试。

## 前置条件

需要 `spec/` 目录下已有：
- 需求分析文档（`/spec-analysis` 生成）
- 技术方案文档（`/plan-design` 生成）

没有则引导用户先完成前两步。

## 代码探索（写测试前必做）

**先理解项目再写测试，不要凭空生成。** 按优先级使用以下工具探索代码库：

1. **`mcp__augment-context-engine__codebase-retrieval`**（最优先）—— 语义搜索，找相似实现、测试模式、项目约定
2. **`mcp__jetbrains__*`** —— IDE 索引搜索，精准定位
   - `search_in_files_by_text/regex`：搜索已有测试文件、断言风格
   - `find_files_by_glob`：找测试目录结构（`**/test/**`、`**/*Test.java`）
   - `get_file_text_by_path`：读取已有测试代码，学习项目测试风格
   - `get_file_problems`：检查代码问题
3. **`smart_search`** —— 结构化搜索兜底

**必须搞清楚的：**
- 项目用什么测试框架？（看 pom.xml / package.json / requirements.txt）
- 已有测试怎么写的？（找 3 个同类测试文件，学习断言风格、mock 方式、命名规范）
- 测试目录结构是什么？（`src/test/java/...` or `__tests__/` or `tests/`）
- 怎么跑测试？（`mvn test` / `npm test` / `pytest`）

## 流程

```
读取 spec + design → ① 只写测试 → ② 确认 Red → ③ 提交测试 → ④ AI 写实现(Green) → ⑤ Review 提交
                       ↑                                           │
                       └───────── 测试没全绿，继续修实现 ──────────┘
```

## ① 只写测试（Red - 写）

**读取 `spec/` 下的需求分析和技术方案**，基于接口清单和数据模型生成测试用例。

**铁律：此阶段只生成测试代码，不生成任何实现代码。**

要做的：
- 根据技术方案中的接口清单，为每个接口写测试
- 覆盖正常流程 + 异常流程 + 边界条件
- 测试框架跟随项目（自动检测 JUnit/Jest/pytest/Google Test 等）
- 测试文件命名跟随项目约定

必须覆盖的测试场景：
- **正常流程**：核心业务路径
- **参数校验**：缺参数、类型错误、超限值
- **权限校验**：无权限访问、越权操作
- **安全校验**：非法文件类型、路径穿越、超大文件
- **边界条件**：空列表、上限值、并发

**输出给用户时明确标注：**
> 以下是测试代码，不包含任何实现。请确认测试用例是否覆盖了你关心的场景。

**🚨 如果 AI 在此阶段生成了实现代码，立即删除并警告用户。**

## ② 确认 Red（Red - 验）

跑测试，**确认全部失败**。

- 如果有测试意外通过 → 说明测试无效（可能断言写错了），必须修复
- 全部失败 = 测试有效，进入下一步
- 展示测试运行结果给用户确认

**输出格式：**
> 测试运行结果：X 个测试，X 个失败，0 个通过。
> 全部 Red ✅ 测试有效，可以提交。

## ③ 所动测试代码（锁定）

锁定测试代码。**从此刻起，测试文件进入锁定状态。**

- 提交信息格式：`test: add tests for [功能名称] (Red)`
- 提交后告知用户：「测试已锁定，后续 AI 只能写实现，不会修改测试文件」

**🔒 锁定规则：步骤 ④ 中 AI 不得修改任何测试文件。如果 AI 尝试修改，必须拒绝并警告。**

## ④ AI 写实现（Green）

**告诉 AI：让所有测试通过，不许修改测试文件。**

### 实现要求：完整、生产级、一次性交付

**不是写空壳或 demo 代码，而是按照项目现有风格写完整的生产代码。** 一次性生成所有需要的文件：

1. **再次探索代码库**（用 aug/jet MCP），搞清楚：
   - 现有 REST Resource 怎么写的？（Jersey 注解、包路径、异常处理）
   - Service 层的接口 + 实现模式（是否有 interface/impl 分离）
   - Model / DTO / PO 放在哪个包下？命名规范？
   - Mapper 怎么写的？XML 还是注解？
   - 配置类、常量类的位置和风格

2. **生成完整代码**，至少包含：
   - REST Resource（接口层）—— 跟随项目 Jersey 风格
   - Service 接口 + 实现 —— 跟随项目 interface/impl 模式
   - Model / DTO / PO —— 请求体、响应体、数据库实体
   - Mapper —— 数据库访问层
   - 配置 / 常量 —— 如有需要

3. **跟随项目风格**，不要引入项目中没用过的框架或模式

### 执行流程

- AI 生成所有实现文件
- 跑测试
- 全绿 → 进入 ⑤
- 没全绿 → AI 继续修实现（微循环），但**绝不改测试**

**微循环上限：3 轮。** 超过 3 轮没全绿，停下来让用户介入分析，不要死磕。

**输出格式：**
> 实现完成。测试运行结果：X 个测试，X 个通过，0 个失败。
> 全部 Green ✅ 可以 Review。
>
> 生成文件清单：
> - `src/main/java/.../resource/XxxResource.java`（REST 接口）
> - `src/main/java/.../service/XxxService.java`（Service 接口）
> - `src/main/java/.../service/impl/XxxServiceImpl.java`（Service 实现）
> - `src/main/java/.../po/XxxPO.java`（数据库实体）
> - `src/main/java/.../mapper/XxxMapper.java`（Mapper）
> - ...

## ⑤ Review 并提交

用户 Review AI 写的实现代码：
- 代码风格是否符合项目规范？
- 有没有性能问题？
- 有没有安全隐患？
- 逻辑是否清晰？

确认后提交：
- 提交信息格式：`feat: implement [功能名称] (Green)`

## 铁律

- **每步等用户确认**，不要自动跳到下一步
- **① 不写实现**：AI 偷写就删掉，零容忍
- **③ 之后测试锁定**：AI 改测试就拒绝，零容忍
- **④ 微循环上限 3 轮**：超过就停，不死磕
- **测试框架不强制**：跟随项目，自动检测
- **先提交测试，再提交实现**：两次独立提交，不混在一起
