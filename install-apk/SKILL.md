---
name: install-apk
description: Android APK 编译和安装工具。用于 Android TV 盒子应用（Becky）的自动化编译和设备安装。使用场景：(1) 编译指定构建变体（如 anchorPrivDebug, gillPrivRelease, perchPrivDebug 等）并生成 APK，(2) 通过 ADB 连接到网络设备（IP:PORT 格式），(3) 安装 APK 到指定设备。当用户需要编译、安装 Android 应用时使用此技能。
---

# APK 编译和安装

## AI 执行说明

**重要**: 当用户执行 `/install-apk` 命令时，AI 需要执行 skill 目录中的脚本，而不是项目目录中的脚本。

**正确做法**:
```bash
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py <variant_build_type> <device> [options]
```

**错误做法**:
```bash
# ❌ 不要在项目目录下查找 scripts 目录
python scripts/install_apk.py <variant_build_type> <device>
```

**替代方案**: 如果脚本执行失败，AI 可以手动执行以下步骤：
1. 编译: `./gradlew assemble<Variant><BuildType>`
2. 查找 APK: `find eapp/build/outputs/apk -name "*<variant>*<build_type>*.apk"`
3. 连接设备: `adb connect <IP:PORT>` (如果未连接)
4. 安装 APK: `adb -s <device> install -r <apk_path>`

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

技能将自动执行以下步骤：

1. **解析构建变体** - 从 `anchorPrivDebug` 格式解析出 variant=`anchorPriv` 和 buildType=`Debug`
2. **编译 APK** - 执行 `./gradlew assemble<Variant><BuildType>`（默认不清理，可使用 `--clean` 参数清理）
3. **查找 APK** - 在 `eapp/build/outputs/apk/<variant>/<build_type>/` 目录定位生成的文件
4. **智能连接设备** - 检查设备连接状态，已连接则复用，未连接则自动连接
5. **安装 APK** - 执行 `adb -s <设备地址> install -r <apk_path>`（使用 `-s` 参数指定设备，避免多设备冲突）

## 可用参数

使用完整参数格式时：

```bash
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py <variant_build_type> <device> [options]
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
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py anchorPrivDebug 172.33.50.2:5353

# 编译前清理
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py anchorPrivDebug 172.33.50.2:5353 --clean

# 编译 Release 版本
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py gillPubRelease 192.168.1.100:5555
```

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

编译后的 APK 文件位于：

**Release 版本：**
```
eapp/build/outputs/apk/<variant>/release/eapp-<variant>-release.apk
```

**Debug 版本：**
```
eapp/build/outputs/apk/<variant>/debug/eapp-<variant>-debug.apk
```

脚本会根据构建类型（debug/release）自动在相应位置搜索 APK：
- `eapp/build/outputs/apk/<variant>/<build_type>/eapp-<variant>-<build_type>.apk`
- `eapp/build/outputs/apk/<variant>/<build_type>/eapp-<variant>-<build_type>-unsigned.apk`
- `eapp/build/outputs/apk/<variant>/<build_type>/eapp.apk`
- 递归搜索整个 `eapp/build/outputs/apk/` 目录

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
./gradlew assembleAnchorPrivRelease

# 只编译 Debug APK
./gradlew assembleAnchorPrivDebug

# APK 位于
ls -lh eapp/build/outputs/apk/anchorPriv/release/  # Release 版本
ls -lh eapp/build/outputs/apk/anchorPriv/debug/    # Debug 版本
```

### 持续集成

在 CI/CD 管道中使用：

```bash
#!/bin/bash
VARIANT_BUILD_TYPE="${1:-anchorPrivDebug}"  # 或 anchorPrivRelease, gillPubDebug 等
DEVICE="${2:-172.33.50.2:5353}"
CLEAN="${3:-}"  # 可选，传 "--clean" 则清理

# 编译并安装（使用 skill 目录中的脚本）
python /Users/colorful/.claude/skills/install-apk/scripts/install_apk.py $VARIANT_BUILD_TYPE $DEVICE $CLEAN
```
