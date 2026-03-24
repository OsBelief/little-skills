# PackageConfig 配置文件格式参考

## 配置文件结构

配置文件位于 `config/{channel}/{platform}.json`，其中：
- `channel`: 渠道目录 (`priv` 或 `pub`)
- `platform`: 平台名称 (如 `hankapp_ge300`, `hankapp_ae800` 等)

## JSON 结构

```json
{
    "distFolder": "becky",
    "rpmVersion": "",
    "rpmName": "ainemo-vulture-{platform}-release",
    "apkList": [
        {
            "packageName": "com.xylink.launcher",
            "version": "1.12.0-278",
            "buildTime": 1763972315009,
            "name": "launcher_focusRelease_1.12.0-278.apk",
            "path": "http://10.0.0.65/builds/dev/Launcher/master/.../launcher.apk",
            "bypassParams": {
                "group": "master"
            },
            "md5": "15da58513e81d154ed3e9de2c1d80bd1"
        }
    ],
    "rpmRelease": "",
    "jsonFilename": "app_pkt_info_{platform}.json"
}
```

## 字段说明

### 顶层字段
- `distFolder`: RPM 包分发文件夹名称
- `rpmVersion`: RPM 版本号
- `rpmName`: RPM 包名称
- `apkList`: APK/包信息列表
- `rpmRelease`: RPM 发布版本
- `jsonFilename`: JSON 配置文件名

### APK/包信息字段 (apkList 中每一项)
- `packageName`: 包名（必填）
- `version`: 版本号，格式为 `x.y.z-buildNumber`
- `buildTime`: 构建时间戳（毫秒）
- `name`: APK/包文件名
- `path`: 下载 URL
- `bypassParams.group`: 分组名称（默认为 "master"）
- `md5`: 文件 MD5 校验和
- `buildType` (可选): 构建类型，1 表示保持最新

## 常见平台列表

### 分区云 (priv/)
- `hankapp_ge300` - Hank GE300
- `hankapp_ae800` - Hank AE800
- `hankapp_ae800v2` - Hank AE800 V2
- `hankapp_ae1000` - Hank AE1000
- `hankapp_me40II` - Hank ME40II
- `hankapp` - Hank 通用

### 公有云 (pub/)
- `hankapp_ge300` - Hank GE300
- `hankapp_ae800` - Hank AE800
- `hankapp_ae800_windbell` - Hank AE800 Windbell
- `hankapp_ae800v2` - Hank AE800 V2
- `hankapp_ae1000` - Hank AE1000
- `hankapp` - Hank 通用

## Gradle 任务参数说明

### genExtPkgInfo 任务

```bash
./gradlew genExtPkgInfo -Purl=<url> -Pplatform=<platform> [options]
```

#### 必填参数
- `-Purl`: APK/包下载 URL
- `-Pplatform`: 目标平台
  - 单个平台: `hankapp_ge300`
  - 多个平台: `hankapp_ge300,hankapp_ae800`
  - 所有平台: `all`

#### 可选参数
- `-Pchannel`: 发布渠道
  - `priv` - 分区云
  - `pub` - 公有云
  - 不指定或 `all` - 所有渠道

- `-PpkgName`: 非 APK 包的包名（当 URL 不是 .apk 文件时必填）

- `-Pg`: 包所属 group 名
  - 不指定时从已有配置中根据包名获取
  - 如果找不到则使用默认值 `master`

- `-Pv`: 包版本名
  - 不指定时尝试从 URL 中解析
  - 如果解析失败则报错

## 工作流程

1. **下载文件**: 从 URL 下载 APK/包文件
2. **解析信息**:
   - APK: 使用 aapt 工具解析包信息
   - 其他包: 从文件名或参数获取版本信息
3. **计算 MD5**: 对下载的文件计算 MD5 校验和
4. **更新配置**: 将包信息追加或更新到对应平台的配置文件中
5. **保存**: 生成格式化的 JSON 配置文件

## 更新逻辑

- 根据包名和 group 组合成唯一键
- 如果该键已存在，则更新对应的包信息
- 如果该键不存在，则追加新的包信息
- 如果包有 `buildType: 1`，会从上次构建中获取最新版本