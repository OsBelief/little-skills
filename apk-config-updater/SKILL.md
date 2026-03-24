---
name: apk-config-updater
description: PackageConfig 项目 APK 配置更新工具。用于更新 config 目录中的 JSON 配置文件中的 APK/包信息。用户可通过 /apk-config-updater 命令直接调用，提供 APK/包下载链接后自动解析包信息并更新到匹配的配置文件中。使用场景：(1) 用户执行 /apk-config-updater 命令并提供 APK 下载链接，(2) 需要批量更新多个平台或渠道的包配置，(3) 需要更新非 APK 包（如 .pkg, .tar.gz 等）的配置信息。
---

# APK 配置更新工具

## 概述

此技能用于 PackageConfig 项目中**全自动**更新 config 目录的 JSON 配置文件。通过提供 APK/包下载链接，自动解析包信息并更新到指定平台的配置文件中。

**✅ 核心特性：100% 自动化流程**
- 自动解析 APK 包名和版本号
- 自动搜索包含该包的配置文件
- 自动执行更新，无需用户确认
- 自动检查并回滚新增的包
- 自动输出执行结果报告

用户只需提供下载链接，系统将自动完成所有操作。

## 核心原则

**⚠️ 只更新已存在的包，绝不新增包**

**✅ 全自动流程，无需用户确认**

1. **严格限制**：只能更新配置文件中已经存在的包，不允许在任何平台中新增包
2. **前置检查**：使用 `git grep` 搜索包含该包的平台，只更新这些平台
3. **自动执行**：直接执行 Gradle 任务，无需用户确认
4. **后置验证**：自动检查 git diff，自动回滚任何新增的包，无需用户确认
5. **双重保险**：前置搜索 + 后置检查，确保不会意外新增

**为什么需要后置检查？**
- Gradle 任务 `genExtPkgInfo` 的设计缺陷会在所有指定配置文件中追加包（即使不存在）
- 即使前置搜索正确，执行时也可能因参数错误导致意外新增
- 后置检查作为最后一道防线，**自动**检测并**自动**回滚新增的配置

**重要说明**：整个流程从解析、搜索、更新到检查回滚，**完全自动执行，不需要任何用户确认**。系统会自动输出执行进度和最终结果。

## 用户命令调用

用户可以通过 `/apk-config-updater <url>` 命令直接调用此技能：

```
/apk-config-updater http://10.0.0.65/builds/prd/deb/private_v3.11/20260303_154217/release/deb_release_103.11.4-29542062.apk
```

### 命令参数

- `<url>`: APK/包下载链接（必填）

### 可选参数

在命令后可以添加额外参数：

```
/apk-config-updater <url> [选项]
```

选项：
- `--platform <platform>`: 指定目标平台（如 hankapp_ge300）
- `--channel <channel>`: 指定渠道（priv/pub）
- `--group <group>`: 指定 group 名称
- `--add-new`: 允许在不包含该包的平台中新增配置（默认只更新已存在的包）
- `--all`: 更新所有平台

示例：
```
/apk-config-updater http://example.com/app.apk --platform hankapp_ge300 --channel pub
/apk-config-updater http://example.com/app.apk --all
/apk-config-updater http://example.com/app.apk --all --add-new
```

## 工作流程

**⚠️ 全自动执行流程：无需任何用户确认步骤**

当用户执行 `/apk-config-updater <url>` 命令时，系统将**自动**按以下步骤处理：

### 1. 解析 URL 和包信息

从 URL 中提取信息：
- 文件名：从 URL 路径中获取（如 `deb_release_103.11.4-29542062.apk`）
- 包类型：判断是 APK 还是其他格式
- 版本号：尝试从文件名中提取（如 `103.11.4-29542062`）

### 2. 确定目标平台

**核心原则：只更新已存在的包，绝不新增包**

**重要限制**：Gradle 任务 `genExtPkgInfo` 会在所有指定的配置文件中追加包（即使不存在）。因此必须先搜索，只传递包含该包的平台参数。

按优先级确定目标平台：

**优先级 1：用户明确指定**
如果命令中包含 `--platform` 参数，使用指定的平台（需谨慎，可能在不包含该包的平台中新增）

**优先级 2：使用 `--all`（默认推荐）**
- **先**使用 git grep 搜索所有配置文件，查找包含该包的平台
- 示例命令：`git grep -l "com\.xylink\.deb" config/`
- 提取平台和渠道信息（如 `config/priv/hankapp.json` → 渠道=priv, 平台=hankapp）
- **只**对这些平台执行 Gradle 任务
- 构造平台参数：按渠道分组，如 `-Pplatform=hankapp,hankapp_ae1000 -Pchannel=priv`

**优先级 3：从 URL 推断**（可选）
- 尝试从 URL 路径中推断平台信息作为参考

### 3. 下载并解析包

使用 Gradle 任务 `genExtPkgInfo` 处理：

```bash
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=<platform>
```

如果是 APK 文件：
- 下载 APK
- 使用 aapt 解析包名、版本号
- 计算 MD5

如果是其他包格式（.pkg, .tar.gz 等）：
- 下载包文件
- 从文件名或参数获取版本号
- 计算 MD5
- **必须指定 `-PpkgName` 参数**

### 4. 自动更新配置文件（无需用户确认）

**重要原则：只更新已存在的包，不新增包**

**Gradle 任务的实际行为**：
- 读取目标配置文件 `config/{channel}/{platform}.json`
- 根据包名和 group 查找匹配的配置项
- 更新匹配项的信息（版本、MD5、URL、时间戳等）
- **⚠️ 问题：如果配置文件中不包含该包，仍然会追加新的配置项**

**因此，必须通过限制目标平台来避免新增**：
1. 先用 git grep 搜索包含该包的配置文件
2. 将这些文件按渠道分组
3. **自动**对每个渠道执行 Gradle 任务，只指定该渠道中包含该包的平台（无需用户确认）

示例：
```bash
# 假设搜索结果为：
# config/priv/hankapp.json
# config/priv/hankapp_ae1000.json
# config/priv/hankapp_zcth.json
# config/pub/hankapp.json

# 分区云渠道
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp,hankapp_ae1000,hankapp_zcth -Pchannel=priv

# 公有云渠道
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp -Pchannel=pub
```

### 5. 自动验证并报告结果

**重要：自动执行后检查，防止意外新增（无需用户确认）**

执行 Gradle 任务后，**自动**检查是否有新增的包，无需用户确认：

```bash
# 自动检查每个修改的文件，判断是更新还是新增
for file in $(git diff --name-only); do
  # 提取该文件中目标包的 diff 片段
  PKG_DIFF=$(git diff "$file" | sed -n "/\"packageName\": \"$PKG_NAME\"/,/^    },*$/p")

  # 检查该包的 diff 中是否有删除的 version 或 buildTime
  # 注意：正则表达式必须匹配以 - 开头的行
  if echo "$PKG_DIFF" | grep -E "^-.*(\"version\"|\"buildTime\"|\"md5\")" > /dev/null; then
    echo "[✓ UPDATE] $file - 包 $PKG_NAME 已更新"
  else
    echo "[✗ NEW] $file - 检测到包 $PKG_NAME 是新增，自动回滚整个文件..."
    git checkout "$file"
  fi
done
```

**自动检查逻辑**：
- 提取目标包的 diff 片段（从 packageName 到下一个对象结束）
- 使用 `grep -E` 和正确的正则表达式，检查是否有以 `-` 开头的删除行
- 如果该片段中有删除的 version/buildTime/md5 行，说明是更新现有包
- 如果该片段中只有新增内容（以 `+` 开头），说明是新增包，**自动回滚**整个文件

**自动输出报告**（无需用户确认）：
- 更新的平台和渠道
- 包名和版本
- 修改的配置文件路径
- 如果有文件被自动回滚，说明回滚原因
- 如果更新了多个文件，列出所有修改

## 完整使用示例

### 示例 1：自动匹配并更新（默认行为）

```
/apk-config-updater http://10.0.0.65/builds/prd/deb/private_v3.11/20260303_154217/release/deb_release_103.11.4-29542062.apk
```

处理流程：
1. 下载 APK 并解析包名（`com.xylink.deb`）
2. 搜索所有配置文件，查找包含该包的平台
   ```bash
   git grep -l "com\.xylink\.deb" config/
   ```
3. 自动筛选出匹配的平台（如 hankapp_ae1000, hankapp, hankapp_zcth）
4. 按渠道分组执行更新
   ```bash
   # 分区云
   ./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp,hankapp_ae1000,hankapp_zcth -Pchannel=priv
   # 公有云
   ./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp -Pchannel=pub
   ```
5. **执行后检查**，自动回滚新增的包
   ```bash
   PKG_NAME="com.xylink.deb"
   for file in $(git diff --name-only); do
     if git diff "$file" | grep -q "^-.*\"packageName\": \"$PKG_NAME\""; then
       echo "[UPDATE] $file - 已更新"
     else
       echo "[NEW] $file - 检测到新增，正在回滚..."
       git checkout "$file"
     fi
   done
   ```
6. 报告更新的文件和跳过的平台

### 示例 2：指定平台

```
/apk-config-updater https://example.com/launcher.apk --platform hankapp_ge300 --channel pub
```

处理流程：
1. 明确指定平台为 `hankapp_ge300`，渠道为 `pub`
2. 直接更新 `config/pub/hankapp_ge300.json`
3. 查找并更新 launcher 相关配置

### 示例 3：更新所有包含该包的平台（默认行为）

```
/apk-config-updater https://example.com/app.apk --all
```

处理流程：
1. 下载 APK 并解析包名
2. 搜索所有配置文件，查找包含该包的平台
3. **只更新**包含该包的平台配置
4. **跳过**不包含该包的平台（不会新增配置）
5. 报告更新的文件和跳过的平台

**这是默认行为**，避免在不相关的平台中新增不必要的包。

### 示例 4：更新所有平台（包括新增）

```
/apk-config-updater https://example.com/app.apk --all --add-new
```

处理流程：
1. 设置平台为 `all`
2. 更新所有渠道和平台的配置文件
3. 在不包含该包的平台中**新增配置**
4. 报告所有更新的文件

**使用场景**：
- 需要向所有平台推送新包
- 确保包在所有平台中都存在

## APK 和非 APK 包处理

### APK 文件（.apk）

自动处理，无需额外参数：
```bash
/apk-config-updater http://example.com/app.apk
```

### 非 APK 包（.pkg, .tar.gz, .zip 等）

需要提供包名，有两种方式：

**方式 1：在命令中指定**
```
/apk-config-updater http://example.com/app.pkg --pkg-name NC90
```

**方式 2：从文件名推断**
如果 URL 包含包名信息，可以从 URL 中提取：
```
/apk-config-updater http://example.com/nc90image-1.3.6-324.pkg
# 自动推断包名为 NC90
```

## 渠道处理

### 默认行为（推荐）

**不指定渠道参数时，Gradle 会自动更新所有渠道**

根据 README.md 文档说明：
- `-Pchannel` 可省略
- 默认更新全部渠道（priv 和 pub）
- 这意味着可以一次性更新所有渠道的配置

```bash
# 不指定 channel，自动更新所有渠道
/apk-config-updater <url> --platform hankapp_ae1000,hankapp

# Gradle 会自动处理：
# - config/priv/hankapp_ae1000.json
# - config/pub/hankapp_ae1000.json
```

**优势**：
- ✅ 一条命令完成所有渠道的更新
- ✅ 简化执行流程
- ✅ 避免分两次执行

### 指定特定渠道

如果只想更新特定渠道，可以手动指定：

```
/apk-config-updater <url> --platform hankapp_ge300 --channel priv   # 仅更新分区云
/apk-config-updater <url> --platform hankapp_ge300 --channel pub    # 仅更新公有云
```

## 配置文件结构

配置文件位于 `config/{channel}/{platform}.json`：

```json
{
    "apkList": [
        {
            "packageName": "vulture.app.diagnostics",
            "version": "103.11.4-29542062",
            "buildTime": 1754013126618,
            "name": "diagnosticsService-release_103.11.0-100.apk",
            "path": "http://10.0.0.65/builds/...",
            "bypassParams": {
                "group": "master"
            },
            "md5": "df4bf1d6c68e29297072eaa7d05329e2"
        }
    ]
}
```

## 常见平台列表

### 分区云 (config/priv/)
- `hankapp_ge300` - Hank GE300
- `hankapp_ae800` - Hank AE800
- `hankapp_ae800v2` - Hank AE800 V2
- `hankapp_ae1000` - Hank AE1000
- `hankapp_me40II` - Hank ME40II

### 公有云 (config/pub/)
- `hankapp_ge300` - Hank GE300
- `hankapp_ae800` - Hank AE800
- `hankapp_ae800_windbell` - Hank AE800 Windbell
- `hankapp_ae800v2` - Hank AE800 V2
- `hankapp_ae1000` - Hank AE1000

## 错误处理

### URL 无效
- 检查 URL 格式
- 确认网络可访问

### 检测到新增的包（自动回滚）
- **后置检查发现新增时，自动执行 `git checkout` 回滚，无需用户确认**
- **自动**向用户报告哪些文件被回滚及回滚原因
- 建议用户检查是否搜索到了正确的平台列表
- 如果确实需要新增，应手动操作并说明原因

### 无法确定平台
- 默认使用 `--all` 自动搜索包含该包的平台
- 如果找不到任何包含该包的平台，报告错误
- **不支持自动新增，用户需手动操作**

### 非 APK 文件缺少包名
- 尝试从 URL 推断包名
- 如果失败，提示用户提供 `--pkg-name` 参数

### 配置文件不存在
- 检查平台名称是否正确
- 确认渠道（priv/pub）是否存在

## 执行命令

最终通过执行 Gradle 任务完成更新：

```bash
./gradlew genExtPkgInfo \
  -Purl=<url> \
  -Pplatform=<platform> \
  [-Pchannel=<channel>] \
  [-PpkgName=<package_name>] \
  [-Pg=<group>] \
  [-Pv=<version>]
```

## 完整工作流程总结

**标准流程（推荐）**

**⚠️ 全自动执行，无需任何用户确认步骤**

```bash
# 1. 下载并解析 APK，获取包名
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=dummy 2>&1 | grep "packageName"

# 2. 搜索包含该包的配置文件
PKG_NAME="com.xylink.deb"
git grep -l "$PKG_NAME" config/

# 3. 解析结果，按渠道分组
# 例如结果：
# config/priv/hankapp.json
# config/priv/hankapp_ae1000.json
# config/pub/hankapp.json

# 4. 按渠道执行更新（自动执行，无需确认）
# 分区云渠道
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp,hankapp_ae1000 -Pchannel=priv

# 公有云渠道
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=hankapp -Pchannel=pub

# 5. 自动检查并回滚新增的包（自动执行，无需确认）
for file in $(git diff --name-only); do
  # 提取该文件中目标包的 diff 片段
  PKG_DIFF=$(git diff "$file" | sed -n "/\"packageName\": \"$PKG_NAME\"/,/^    },*$/p")

  # 检查该包的 diff 中是否有删除的 version 或 buildTime
  if echo "$PKG_DIFF" | grep -E "^-.*(\"version\"|\"buildTime\"|\"md5\")" > /dev/null; then
    echo "[✓ UPDATE] $file"
  else
    echo "[✗ NEW] $file - 正在自动回滚..."
    git checkout "$file"
  fi
done

# 6. 自动验证并输出结果
git diff --stat
```

**关键检查点**
- ✓ 步骤 2：使用 git grep 确保只更新包含该包的平台
- ✓ 步骤 4：自动执行更新，无需用户确认
- ✓ 步骤 5：自动检查并回滚新增的包，无需用户确认
- ✓ 步骤 6：自动验证并输出结果
- ✓ **整个流程 100% 自动化，零交互**

## 资源

### scripts/update_apk_config.py

Python 脚本封装了 Gradle 任务，提供额外的命令行接口。

### references/config_format.md

详细的配置文件格式说明，包括 JSON 结构、字段定义和更新规则。
