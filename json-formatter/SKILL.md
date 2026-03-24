---
name: json-formatter
description: 从日志输出中提取和格式化 JSON。当用户提供包含 JSON 的日志行时使用此 skill,如 Android/Java 日志、应用日志、服务器日志等。处理嵌套的 JSON 字符串(双编码 JSON),支持截断日志的精确格式化(不补全)。当用户提到"格式化 JSON"、"解析日志中的 JSON"、"美化 JSON"、"提取 JSON"或粘贴包含 JSON 的日志时触发。
---

# JSON 格式化工具

这个 skill 从日志输出中提取 JSON 并格式化,使其易于阅读。

## 核心功能

### 1. 识别日志中的 JSON

常见的日志格式:
```
03-24 09:34:58.041  1187  1910 I SdkJni  : n2a f=onConfMgmtStateChanged, m={"key":"value"}
[2024-03-24 09:34:58] INFO  com.example.Logger: {"data":"..."}
ERROR: {"error":"message","details":{...}}
```

**如何提取 JSON:**
- 查找日志中的 JSON 开始标记(通常是 `{`)
- 如果 JSON 在特定字段后(如 `m=`、`data=`、`json=`),提取该字段后的内容
- 忽略日志前缀(时间戳、进程 ID、日志级别、tag 等)

### 2. 处理嵌套的 JSON 字符串

日志中常见双编码 JSON - JSON 字符串的值本身也是 JSON:

```json
{
  "commonJson": "{\"multiScreen\":\"{\\\"noContent\\\":[...]}\",...}",
  "config": "{\"enabled\":true,\"settings\":\"{\\\"value\\\":123}\"}"
}
```

**格式化策略:**
- 首先格式化最外层 JSON
- 识别值是 JSON 字符串的字段(如 `commonJson`, `multiScreen1/2/3`, `customizedLayout`, `notifySet` 等)
- 递归解析和格式化这些嵌套的 JSON 字符串
- 展示完整的多层结构

### 3. 精确截断处理

**当日志被截断时:**

输入:
```json
{"user":"alice","items":[{"id":1,"name":"item1"},{"id":2,"nam
```

输出(精确到截断点,不补全):
```json
{
  "user": "alice",
  "items": [
    {
      "id": 1,
      "name": "item1"
    },
    {
      "id": 2,
      "nam
```

**重要规则:**
- 绝对不补全截断的 JSON
- 不添加闭合的括号、引号或大括号
- 在截断点停止,保持原始的不完整状态
- 如果截断发生在字符串中间,保持字符串未闭合状态

### 4. 输出格式

使用以下规则:
- 2 空格缩进
- 键值对在不同行
- 数组和对象的每个元素换行
- 保持原始数据类型(数字、布尔值、null)

## 工作流程

1. **分析输入**
   - 识别是否为日志行或纯 JSON 字符串
   - 如果是日志,定位 JSON 起始位置
   - 检查是否完整或被截断

2. **提取 JSON**
   - 对于日志,去除前缀提取 JSON 部分
   - 对于纯 JSON,直接使用

3. **解析和格式化**
   - 解析外层 JSON(如果可能)
   - 识别嵌套的 JSON 字段
   - 递归解析嵌套的 JSON 字符串
   - 应用格式化规则

4. **输出**
   - 使用中文说明
   - 展示格式化后的 JSON
   - 如果截断,标注截断位置
   - 对于多层 JSON,可提供结构说明

## 识别嵌套 JSON 的提示

这些字段名通常包含嵌套 JSON:
- `commonJson`
- `multiScreen`, `multiScreen1`, `multiScreen2`, `multiScreen3`
- `customizedLayout`
- `notifySet`
- `config`, `settings`, `options`
- `data`, `payload`, `metadata`
- 任何值以 `"{` 开头的字段

## 错误处理

- 如果 JSON 完全无效,告知用户并提供原始输入
- 如果部分嵌套 JSON 无法解析,跳过该部分继续格式化其余内容
- 明确说明哪些部分格式化失败

## 示例

**示例 1: 简单日志**
```
输入: 03-24 09:34:58.041 1187 1910 I SdkJni : m={"name":"test","value":123}
输出: 格式化后的 JSON
```

**示例 2: 嵌套 JSON**
```
输入: {"config":"{\"a\":1,\"b\":2}"}
输出: 完全展开的格式化 JSON
```

**示例 3: 截断的 JSON**
```
输入: {"key":"value","nested":{"array":[1,2,
输出: 在 [1,2, 处停止的格式化结果
```

## 注意事项

- 始终使用中文与用户交互
- 保留原始数据的完整性
- 对于大型 JSON,可考虑提供摘要或部分展开
- 如果用户需要特定格式,按需调整
