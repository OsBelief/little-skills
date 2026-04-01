---
name: install-apk
description: Android APK 编译和安装工具。用于 Android TV 盒子应用（Becky）的自动化编译和设备安装。使用场景：(1) 编译指定构建变体（如 anchorPrivDebug, gillPrivRelease, perchPrivDebug 等）并生成 APK，(2) 通过 ADB 连接到网络设备（IP:PORT 格式），(3) 安装 APK 到指定设备。当用户需要编译、安装 Android 应用时使用此技能。
---

# APK 编译和安装

## ⚠️ 核心原则

**🔥 每次执行都必须重新编译！**

- ✅ 每次运行 `/install-apk` 都会执行完整的编译流程
- ✅ 确保安装的是最新代码编译的 APK
- ❌ 禁止跳过编译步骤使用旧 APK
- ❌ 禁止为了"快速"而复用之前的编译产物

## AI 执行说明

**⚠️ 重要**: 脚本需要能够找到项目根目录才能执行编译。

**✅ 推荐做法（从项目目录执行）**:
```bash
# 方式 1: 从项目目录执行（自动检测项目根目录）
cd /path/to/project && python ~/.claude/skills/install-apk/scripts/install_apk.py <variant_build_type> <device>

# 方式 2: 使用 --project-dir 参数（从任何目录执行）
python ~/.claude/skills/install-apk/scripts/install_apk.py <variant_build_type> <device> --project-dir /path/to/project

# 方式 3: 使用环境变量
PROJECT_DIR=/path/to/project python ~/.claude/skills/install-apk/scripts/install_apk.py <variant_build_type> <device>
```

**📝 参数说明**:
- `variant_build_type`: 完整构建变体（如 pearlDebug, anchorPrivDebug, gillPubRelease）
- `device`: 设备地址（如 172.33.50.40:5555）
- `--project-dir`: 项目根目录路径（可选，默认从当前目录向上查找）
- `--clean`: 编译前清理（可选）

**🔥 关键原则**: 每次都必须重新编译！

**替代方案**: 如果脚本执行失败，AI 可以手动执行以下步骤（**必须按顺序全部执行**）：
1. ✅ **编译**: `./gradlew assemble<Variant><BuildType>` (每次都要执行！)
2. ✅ **查找 APK**: `find app/build/outputs/apk -name "*<variant>*<build_type>*.apk"` (或 `eapp/build/outputs/apk`)
3. ✅ **连接设备**: `adb connect <IP:PORT>` (如果未连接)
4. ✅ **安装 APK**: `adb -s <device> install -r <apk_path>`

**禁止行为**:
- ❌ 跳过编译步骤，直接使用旧的 APK
- ❌ 为了"快速安装"而忽略重新编译
- ❌ 编译后多次安装时复用旧 APK（每次都要重新编译）

## 快速开始

编译并安装 APK 到设备的标准命令格式：

```
install-apk <variant_build_type> <device_address>
```

**参数：**
- `variant_build_type`: 完整构建变体，格式为 `<variant><Debug|Release>`（如 anchorPrivDebug, gillPubRelease, perchPrivDebug）
- `device_address`: 设备网络地址，格式 `IP:PORT`（如 172.33.50.2:5353）

**示例：**
```bash
# 编译并安装 anchorPrivDebug 版本
install-apk anchorPrivDebug 172.33.50.2:5353

# 编译并安装 anchorPrivRelease 版本
install-apk anchorPrivRelease 172.33.50.2:5353

# 编译并安装 gillPrivDebug 版本
install-apk gillPrivDebug 192.168.1.100:5555
```

## 工作流程

⚠️ **重要**: 每次执行都会重新编译，确保安装最新代码！

技能将自动执行以下步骤：

1. **智能检测项目** - 自动检测项目结构（app 模块或 eapp 模块）
2. **解析构建变体** - 从 `privDebug` 或 `anchorPrivDebug` 格式解析出 variant 和 buildType
3. **🔥 编译 APK** - 执行 `./gradlew assemble<Variant><BuildType>`（**每次必执行**，默认不清理，可使用 `--clean` 参数清理）
4. **查找 APK** - 在 `app/build/outputs/apk/` 或 `eapp/build/outputs/apk/` 目录定位生成的文件
5. **智能连接设备** - 检查设备连接状态，已连接则复用，未连接则自动连接
6. **安装 APK** - 执行 `adb -s <设备地址> install -r <apk_path>`（使用 `-s` 参数指定设备，避免多设备冲突）

## 可用参数

使用完整参数格式时：

```bash
python ./scripts/install_apk.py <variant_build_type> <device> [options]
```

**参数说明：**
- `variant_build_type`: 完整构建变体名称（必需）
  - 格式：`<variant><Debug|Release>`
  - 例如：`anchorPrivDebug`, `anchorPrivRelease`, `gillPubDebug`, `perchPrivRelease`
- `device`: 设备地址（必需），格式 `IP:PORT`

**选项：**
- `--clean`: 编译前执行 clean 清理构建缓存（默认不执行）

**完整示例：**
```bash
# 编译并安装（不清理，默认行为）
python ./scripts/install_apk.py privDebug 172.33.106.69:5555
python ./scripts/install_apk.py anchorPrivDebug 172.33.50.2:5353

# 编译前清理
python ./scripts/install_apk.py anchorPrivDebug 172.33.50.2:5353 --clean

# 编译 Release 版本
python ./scripts/install_apk.py gillPubRelease 192.168.1.100:5555
```

## 支持的项目

脚本会自动检测并支持以下项目：

### Coral 项目
- **应用模块**: `app`
- **APK 命名**: `Coral_<variant><build_type>_版本号-构建号.apk`
- **支持变体**: `privDebug`, `privRelease`, `pubDebug`, `pubRelease`

### Becky 项目
- **应用模块**: `eapp`
- **APK 命名**: `eapp-<variant>-<build_type>.apk`
- **支持变体**: `anchorPrivDebug`, `anchorPrivRelease`, `gillPubDebug`, `perchPrivDebug` 等

**自动检测**:
- 脚本会自动检测项目使用的是 `app` 还是 `eapp` 模块
- 根据检测结果在正确的目录查找 APK
- 无需手动指定项目类型

## 构建变体

Becky 项目支持以下变体，使用时需要在变体名后添加 `Debug` 或 `Release`：

| 基础变体 | 平台 | 渠道 | 完整示例 |
|---------|------|------|---------|
| `anchorPub` | hankapp_ae800, hankapp_ae800v2, hankapp_ge300 | pub | `anchorPubDebug`, `anchorPubRelease` |
| `anchorPriv` | hankapp_ae800, hankapp_ae800v2, hankapp_ge300, hankapp_ae800_windbell | priv | `anchorPrivDebug`, `anchorPrivRelease` |
| `gillPub` | hankapp | pub | `gillPubDebug`, `gillPubRelease` |
| `gillPriv` | hankapp | priv | `gillPrivDebug`, `gillPrivRelease` |
| `perchPriv` | perchapp | pub, priv | `perchPrivDebug`, `perchPrivRelease` |

## 设备连接

### 网络设备连接

对于 Android TV 盒子，通常使用网络 ADB 连接：

```bash
# 标准格式
adb connect <IP>:<PORT>

# 常用端口
# 5353 - 某些设备的默认 ADB 端口
# 5555 - Android 标准网络 ADB 端口
```

### 智能设备连接

脚本采用智能连接逻辑：
- **检查连接状态** - 首先检查目标设备是否已连接
- **复用现有连接** - 如果设备已连接，直接使用现有连接进行安装
- **自动连接** - 如果设备未连接，自动执行连接操作
- **显示设备列表** - 显示当前所有已连接的设备
- **精确安装** - 使用 `adb -s <设备地址>` 精确指定目标设备

这样可以避免断开已有的 ADB 连接，并在多设备环境下确保安装到正确的设备。

### 手动检查设备

如果连接有问题，可以手动检查：

```bash
# 查看已连接的设备
adb devices -l

# 手动连接
adb connect 172.33.50.2:5353

# 测试连接
adb shell getprop ro.build.version.release
```

## APK 位置

脚本会自动检测项目结构并查找 APK：

**Coral 项目 (app 模块):**
```
app/build/outputs/apk/<variant>/debug/Coral_<variant><build_type>_*.apk
app/build/outputs/apk/<variant>/release/Coral_<variant><build_type>_*.apk

示例:
- app/build/outputs/apk/priv/debug/Coral_privDebug_103.11.5-29575109.apk
- app/build/outputs/apk/priv/release/Coral_privRelease_103.11.5-29575109.apk
```

**Becky 项目 (eapp 模块):**
```
eapp/build/outputs/apk/<variant>/debug/eapp-<variant>-debug.apk
eapp/build/outputs/apk/<variant>/release/eapp-<variant>-release.apk
```

脚本会根据检测到的模块自动在相应位置搜索 APK：
- 精确匹配常见命名模式
- 支持通配符匹配版本号
- 递归搜索整个 `app/build/outputs/apk/` 或 `eapp/build/outputs/apk/` 目录
- 自动选择最新的 APK（按修改时间）

## 手动启动应用和查看日志

安装完成后，如果需要手动启动应用或查看日志：

```bash
# 手动启动应用
adb shell am start -n com.ainemo.becky/com.ainemo.becky.eapp.activity.SplashActivity

# 查看应用日志
adb logcat -s Becky AndroidRuntime '*:E'
```

## 常见问题

### 编译失败

如果 Gradle 编译失败：
1. 检查网络连接（可能需要下载依赖）
2. 尝试手动执行 `./gradlew clean`
3. 检查 JDK 版本是否正确

### ADB 连接失败

如果无法连接到设备：
1. 确认设备和电脑在同一网络
2. 检查设备是否启用了网络 ADB
3. 尝试手动 `adb connect <IP:PORT>`
4. 检查防火墙设置

### APK 安装失败

常见原因：
- **签名不匹配**: 使用 `-r` 参数重新安装
- **存储空间不足**: 清理设备存储
- **版本冲突**: 卸载旧版本后重新安装
- **多设备冲突**: 脚本已自动使用 `-s` 参数指定设备，通常不会出现此问题

### 多设备环境

当有多个设备同时连接时：
- 脚本自动使用 `adb -s <设备地址>` 精确指定目标设备
- 不会影响其他已连接的设备
- 可以安全地在多设备环境下使用

示例场景：
```bash
# 设备 A 和设备 B 同时在线
adb devices
# 172.33.50.1:5353  device  (stan 设备)
# 172.33.50.2:5353  device  (anchor 设备)

# 安全地安装到 stan 设备，不会影响 anchor 设备
install-apk stanDebug 172.33.50.1:5353
```

## 高级用法

### 批量安装到多个设备

```bash
# 安装到多个设备（首次清理，后续不清理）
install-apk anchorPrivDebug 172.33.50.2:5353 --clean
for device in "172.33.50.3:5353" "172.33.50.4:5353"; do
    install-apk anchorPrivDebug $device  # 复用编译产物
done
```

### 仅编译不安装

```bash
# 只编译 Release APK
./gradlew assemblePrivRelease

# 只编译 Debug APK
./gradlew assemblePrivDebug

# APK 位于（根据项目不同而不同）
ls -lh app/build/outputs/apk/priv/release/  # Coral 项目 Release 版本
ls -lh app/build/outputs/apk/priv/debug/    # Coral 项目 Debug 版本
ls -lh eapp/build/outputs/apk/anchorPriv/release/  # Becky 项目 Release 版本
ls -lh eapp/build/outputs/apk/anchorPriv/debug/    # Becky 项目 Debug 版本
```

### 持续集成

在 CI/CD 管道中使用：

```bash
#!/bin/bash
VARIANT_BUILD_TYPE="${1:-anchorPrivDebug}"  # 或 anchorPrivRelease, gillPubDebug 等
DEVICE="${2:-172.33.50.2:5353}"
CLEAN="${3:-}"  # 可选，传 "--clean" 则清理

# 编译并安装（使用 skill 目录中的脚本）
python ./scripts/install_apk.py $VARIANT_BUILD_TYPE $DEVICE $CLEAN
```
