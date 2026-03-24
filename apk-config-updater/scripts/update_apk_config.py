#!/usr/bin/env python3
"""
APK 配置更新脚本
自动调用 Gradle 任务更新 config 目录中的 JSON 配置文件
"""

import argparse
import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path


def find_project_root():
    """查找 PackageConfig 项目根目录"""
    project_root = Path.cwd()
    if not (project_root / "build.gradle").exists():
        # 尝试查找项目根目录
        current = Path.cwd()
        while current != current.parent:
            if (current / "build.gradle").exists():
                project_root = current
                break
            current = current.parent
        else:
            return None
    return project_root


def get_apk_package_name(url: str, project_root: Path) -> str:
    """
    通过下载 APK 并使用 aapt 获取包名

    Args:
        url: APK 下载链接
        project_root: 项目根目录

    Returns:
        str: APK 包名
    """
    print(f"正在解析 APK 包信息: {url}")

    # 创建临时目录下载 APK
    with tempfile.TemporaryDirectory() as temp_dir:
        apk_path = Path(temp_dir) / "temp.apk"

        # 下载 APK
        download_cmd = ["curl", "-f", "-o", str(apk_path), url]
        try:
            subprocess.run(download_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"下载 APK 失败: {e}")
            return None

        # 查找 aapt 工具
        sdk_dir = os.environ.get('ANDROID_HOME')
        if not sdk_dir:
            local_properties = project_root / "local.properties"
            if local_properties.exists():
                with open(local_properties, 'r') as f:
                    for line in f:
                        if line.startswith('sdk.dir='):
                            sdk_dir = line.split('=')[1].strip()
                            break

        if not sdk_dir:
            print("无法找到 Android SDK，请设置 ANDROID_HOME 环境变量或配置 local.properties")
            return None

        # 尝试常见的 build-tools 版本
        aapt_path = None
        build_tools_dir = Path(sdk_dir) / "build-tools"
        if build_tools_dir.exists():
            # 按版本号排序，选择最新的
            versions = sorted([d.name for d in build_tools_dir.iterdir() if d.is_dir()], reverse=True)
            for version in versions:
                potential_aapt = build_tools_dir / version / "aapt"
                if potential_aapt.exists():
                    aapt_path = potential_aapt
                    break

        if not aapt_path:
            print("无法找到 aapt 工具")
            return None

        # 使用 aapt 获取包名
        cmd = [str(aapt_path), "dump", "badging", str(apk_path)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            for line in result.stdout.split('\n'):
                if line.startswith('package: name='):
                    # 解析包名，格式: package: name='com.example.app' versionCode='1' versionName='1.0'
                    package_name = line.split("'")[1]
                    print(f"APK 包名: {package_name}")
                    return package_name
        except subprocess.CalledProcessError as e:
            print(f"解析 APK 失败: {e}")
            return None

    return None


def search_package_in_configs(package_name: str, project_root: Path) -> dict:
    """
    在所有配置文件中搜索包含指定包的平台

    Args:
        package_name: 包名
        project_root: 项目根目录

    Returns:
        dict: {平台名: [渠道列表]}
    """
    config_dir = project_root / "config"
    platforms = {}

    print(f"\n正在搜索包 '{package_name}' 在配置文件中的存在情况...")

    # 遍历所有渠道目录
    for channel_dir in config_dir.iterdir():
        if not channel_dir.is_dir():
            continue

        channel = channel_dir.name
        print(f"\n检查渠道: {channel}")

        # 遍历该渠道下的所有平台配置文件
        for config_file in channel_dir.glob("*.json"):
            platform = config_file.stem

            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 检查 apkList 中是否包含该包
                found = False
                for item in config.get('apkList', []):
                    if item.get('packageName') == package_name:
                        found = True
                        break

                if found:
                    if platform not in platforms:
                        platforms[platform] = []
                    platforms[platform].append(channel)
                    print(f"  ✓ 找到: {platform}.json")
                else:
                    print(f"  - 未找到: {platform}.json")

            except Exception as e:
                print(f"  ! 读取 {config_file.name} 失败: {e}")

    return platforms


def run_gradle_task(url: str, platform: str, channel: str = None, pkg_name: str = None,
                    group: str = None, version: str = None, add_new: bool = False) -> int:
    """
    执行 Gradle genExtPkgInfo 任务

    Args:
        url: APK/包下载链接
        platform: 目标平台 (如 hankapp_ge300, 或多个平台用逗号分隔)
        channel: 发布渠道 (priv/pub)，默认为 all
        pkg_name: 非 APK 包必填，包名
        group: 包所属 group 名，默认从已有配置获取
        version: 包版本名
        add_new: 是否允许在不包含该包的平台中新增配置（默认不允许）

    Returns:
        int: 退出码，0 表示成功
    """
    project_root = find_project_root()
    if not project_root:
        print("错误: 未找到 PackageConfig 项目根目录 (build.gradle)")
        return 1

    print(f"项目根目录: {project_root}")

    # 默认行为：只更新已存在的包，不新增（除非指定 --add-new）
    if platform == "all" and not add_new:
        # 先获取包名
        if url.endswith(".apk"):
            package_name = get_apk_package_name(url, project_root)
            if not package_name:
                print("错误: 无法获取 APK 包名")
                return 1
        else:
            if not pkg_name:
                print("错误: 非 APK 文件必须提供包名参数")
                return 1
            package_name = pkg_name

        # 搜索包含该包的平台
        platforms = search_package_in_configs(package_name, project_root)

        if not platforms:
            print(f"\n警告: 未找到包含包 '{package_name}' 的平台配置")
            print("没有配置被更新")
            print("提示: 如果需要新增配置，请使用 --add-new 参数")
            return 0

        # 构建平台列表（不包含渠道前缀，让 Gradle 自动处理所有渠道）
        platform_list = list(platforms.keys())

        if not platform_list:
            print("没有需要更新的平台")
            return 0

        # 更新 platform 为具体的平台列表（不指定 channel，Gradle 会自动更新所有渠道）
        platform = ",".join(platform_list)
        print(f"\n筛选后的平台列表: {platform}")
        print("注意: 将更新这些平台在所有渠道中的配置")

    # 构建命令
    cmd = ["./gradlew", "genExtPkgInfo", f"-Purl={url}", f"-Pplatform={platform}"]

    if channel:
        cmd.append(f"-Pchannel={channel}")

    if pkg_name:
        cmd.append(f"-PpkgName={pkg_name}")

    if group:
        cmd.append(f"-Pg={group}")

    if version:
        cmd.append(f"-Pv={version}")

    print(f"\n执行命令: {' '.join(cmd)}\n")

    # 执行命令
    result = subprocess.run(cmd, cwd=project_root, capture_output=False, text=True)

    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="更新 PackageConfig 项目中的 APK 配置信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 更新单个平台的 APK
  %(prog)s -u https://example.com/app.apk -p hankapp_ge300

  # 更新多个平台
  %(prog)s -u https://example.com/app.apk -p hankapp_ge300,hankapp_ae800

  # 更新所有包含该包的平台（默认行为，不新增）
  %(prog)s -u https://example.com/app.apk -p all

  # 更新所有平台，包括不包含该包的平台（新增配置）
  %(prog)s -u https://example.com/app.apk -p all --add-new

  # 指定渠道 (priv/pub)
  %(prog)s -u https://example.com/app.apk -p hankapp_ge300 -c pub

  # 更新非 APK 包 (需要指定包名)
  %(prog)s -u https://example.com/app.pkg -p all -n NC90

  # 指定 group 和版本
  %(prog)s -u https://example.com/app.apk -p hankapp_ge300 -g dev -v 1.0.0
        """
    )

    parser.add_argument(
        "-u", "--url",
        required=True,
        help="APK/包下载 URL (必填)"
    )

    parser.add_argument(
        "-p", "--platform",
        required=True,
        help="目标平台，如 hankapp_ge300；支持多个平台用逗号分隔；使用 'all' 表示所有平台 (必填)"
    )

    parser.add_argument(
        "-c", "--channel",
        choices=["priv", "pub", "all"],
        default=None,
        help="发布渠道：priv (分区云), pub (公有云), all (所有)，默认为 all"
    )

    parser.add_argument(
        "-n", "--pkg-name",
        help="非 APK 包必填，包名"
    )

    parser.add_argument(
        "-g", "--group",
        help="包所属 group 名，默认从已有配置中获取，不存在则使用 'master'"
    )

    parser.add_argument(
        "-v", "--version",
        help="包版本名"
    )

    parser.add_argument(
        "--add-new",
        action="store_true",
        help="允许在不包含该包的平台中新增配置（默认只更新已存在的包）"
    )

    args = parser.parse_args()

    # 验证：非 APK 文件必须提供包名
    if not args.url.endswith(".apk") and not args.pkg_name:
        print("错误: 非 APK 文件必须提供包名参数 (-n/--pkg-name)")
        return 1

    return run_gradle_task(
        url=args.url,
        platform=args.platform,
        channel=args.channel,
        pkg_name=args.pkg_name,
        group=args.group,
        version=args.version,
        add_new=args.add_new
    )


if __name__ == "__main__":
    sys.exit(main())