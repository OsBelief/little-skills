#!/usr/bin/env python3
"""
APK 编译和安装脚本
用于 Android TV 盒子应用（Becky/Coral）的自动化编译和安装

**重要**: 每次执行都会重新编译，确保安装最新代码！

用法:
    python install_apk.py <variant_build_type> <device_address> [options]

示例:
    python install_apk.py anchorPrivDebug 172.33.50.2:5353
    python install_apk.py privDebug 172.33.106.69:5555
    python install_apk.py gillPrivRelease 192.168.1.100:5555 --clean
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path


def parse_variant_and_build_type(full_variant):
    """
    解析完整的 variant 字符串，提取 variant 和 build type

    例如:
    - anchorPrivDebug -> variant='anchorPriv', build_type='Debug'
    - privDebug -> variant='priv', build_type='Debug'
    - anchorPrivRelease -> variant='anchorPriv', build_type='Release'
    - gillPubDebug -> variant='gillPub', build_type='Debug'
    - gillPubRelease -> variant='gillPub', build_type='Release'
    """
    if full_variant.endswith('Debug'):
        variant = full_variant[:-5]  # 移除 'Debug'
        build_type = 'Debug'
    elif full_variant.endswith('Release'):
        variant = full_variant[:-7]  # 移除 'Release'
        build_type = 'Release'
    else:
        # 默认为 Release
        variant = full_variant
        build_type = 'Release'

    return variant, build_type


def run_command(cmd, description, check=True, cwd=None):
    """执行命令并显示输出"""
    print(f"\n🔧 {description}...")
    print(f"命令: {' '.join(cmd)}")
    if cwd:
        print(f"工作目录: {cwd}")

    result = subprocess.run(
        cmd,
        cwd=cwd,  # 指定工作目录
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if result.stdout:
        # 只显示重要信息，避免输出过多
        lines = result.stdout.split('\n')
        important_lines = []
        for line in lines:
            # 跳过 UP-TO-DATE 的任务
            if 'UP-TO-DATE' in line:
                continue
            # 显示错误、警告、构建结果
            if any(keyword in line for keyword in ['BUILD', 'FAILED', 'Success', 'error', 'Error', '> Task', 'Deprecated']):
                important_lines.append(line)
            # 显示空行和重要分隔符
            elif line.strip() == '' or line.startswith('>'):
                important_lines.append(line)

        if important_lines:
            print('\n'.join(important_lines[-50:]))  # 只显示最后50行重要信息

    if check and result.returncode != 0:
        print(f"❌ {description}失败，返回码: {result.returncode}")
        sys.exit(result.returncode)

    return result


def is_device_connected(device_address):
    """检查指定设备是否已连接"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # 检查输出中是否包含目标设备地址
        return device_address in result.stdout
    except subprocess.TimeoutExpired:
        return False


def find_project_root():
    """
    智能查找项目根目录

    从当前目录向上查找，直到找到包含项目标记的目录。
    项目标记包括：gradlew, settings.gradle, app/, eapp/ 等
    """
    # 从当前目录开始查找
    current = Path.cwd()

    # 项目根目录的标记（至少包含其中一个）
    project_markers = [
        "gradlew",
        "settings.gradle",
        "settings.gradle.kts",
        "build.gradle",
        "build.gradle.kts"
    ]

    # 模块标记（至少包含其中一个）
    module_markers = ["app", "eapp"]

    # 向上遍历目录树
    for parent in [current] + list(current.parents):
        # 检查是否包含项目标记
        has_project_marker = any((parent / marker).exists() for marker in project_markers)

        # 检查是否包含模块标记
        has_module_marker = any((parent / marker).is_dir() for marker in module_markers)

        # 同时满足项目标记和模块标记，认为是项目根目录
        if has_project_marker and has_module_marker:
            return parent

    # 如果找不到，返回当前目录
    print("⚠️  未找到项目根目录标记，使用当前目录")
    return current


def detect_app_module(project_root):
    """
    检测项目使用的是哪个应用模块
    返回: 'app' 或 'eapp'
    """
    if (project_root / "app" / "build.gradle").exists() or \
       (project_root / "app" / "build.gradle.kts").exists():
        return "app"
    elif (project_root / "eapp" / "build.gradle").exists() or \
         (project_root / "eapp" / "build.gradle.kts").exists():
        return "eapp"
    else:
        # 默认尝试 app
        print("⚠️  无法检测应用模块，默认使用 'app'")
        return "app"


def get_apk_version_info(apk_path):
    """使用 aapt 从 APK 中提取版本号和包名"""
    try:
        result = subprocess.run(
            ["aapt", "dump", "badging", str(apk_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 解析 package: name='com.xxx' versionCode='123' versionName='1.0.0'
            match = re.search(
                r"package:\s*name='(?P<name>[^']+)'\s*versionCode='(?P<code>[^']+)'\s*versionName='(?P<version>[^']+)'",
                result.stdout
            )
            if match:
                return {
                    "package_name": match.group("name"),
                    "version_code": match.group("code"),
                    "version_name": match.group("version"),
                }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def find_apk(variant, build_type, project_root, app_module):
    """查找编译生成的 APK 文件"""
    build_type_lower = build_type.lower()

    # 根据检测到的模块构建可能的路径
    module_prefix = "eapp" if app_module == "eapp" else "Coral"

    possible_paths = [
        # Coral 项目 (app 模块)
        project_root / "app" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"{module_prefix}_{variant}{build_type}_*.apk",
        # Becky 项目 (eapp 模块)
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"eapp-{variant}-{build_type_lower}.apk",
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"eapp-{variant}-{build_type_lower}-unsigned.apk",
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / "eapp.apk",
    ]

    # 尝试精确匹配
    for path_pattern in possible_paths:
        if '*' in str(path_pattern):
            # 使用 glob 处理通配符
            matching_files = list(path_pattern.parent.glob(path_pattern.name))
            if matching_files:
                apk_path = matching_files[0]
                print(f"✅ 找到 APK: {apk_path}")
                return apk_path
        else:
            if path_pattern.exists():
                print(f"✅ 找到 APK: {path_pattern}")
                return path_pattern

    # 如果没找到，尝试递归搜索
    print("⚠️  未在预期位置找到 APK，开始搜索...")
    build_dir = project_root / app_module / "build" / "outputs" / "apk"
    if build_dir.exists():
        # 查找所有包含 variant 和 build_type 的 APK
        apk_files = []
        for apk_file in build_dir.rglob("*.apk"):
            if variant.lower() in str(apk_file).lower() and build_type_lower in str(apk_file).lower():
                apk_files.append(apk_file)

        # 选择最新的 APK（按修改时间）
        if apk_files:
            apk_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            print(f"✅ 找到 APK: {apk_files[0]}")
            return apk_files[0]

    print(f"❌ 未找到 variant '{variant}' build type '{build_type}' 对应的 APK 文件")
    print(f"   搜索目录: {build_dir}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="**每次都会重新编译，确保安装最新代码！**\n\n编译并安装 APK 到指定设备",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从项目目录执行（自动检测项目根目录）
  %(prog)s privDebug 172.33.106.69:5555
  %(prog)s anchorPrivDebug 172.33.50.2:5353
  %(prog)s gillPubRelease 192.168.1.100:5555 --clean

  # 从任何目录执行（指定项目目录）
  %(prog)s pearlDebug 172.33.50.40:5555 --project-dir /path/to/project
        """
    )
    parser.add_argument("variant_build_type",
                       help="完整构建变体，格式: <variant><Debug|Release>，如 privDebug, anchorPrivDebug, gillPubRelease")
    parser.add_argument("device", help="设备地址，格式: IP:PORT (如 172.33.50.2:5353)")
    parser.add_argument("--clean", action="store_true", help="编译前执行 clean（默认不执行）")
    parser.add_argument("--project-dir", type=str, default=None,
                       help="项目根目录路径（可选，默认从当前目录向上查找）")

    args = parser.parse_args()

    # 解析 variant 和 build type
    variant, build_type = parse_variant_and_build_type(args.variant_build_type)

    # 确定项目根目录（优先级：命令行参数 > 环境变量 > 智能查找）
    project_dir_arg = args.project_dir or os.environ.get("PROJECT_DIR")

    if project_dir_arg:
        # 用户明确指定了项目目录
        project_root = Path(project_dir_arg).resolve()
        if not project_root.exists():
            print(f"❌ 指定的项目目录不存在: {project_root}")
            sys.exit(1)
    else:
        # 智能查找项目根目录
        project_root = find_project_root()

        # 检测是否在 skill 目录中执行
        current_dir = Path.cwd()
        if (current_dir / "skill.md").exists() or "skills" in str(current_dir):
            print("\n⚠️  检测到可能从 skill 目录执行")
            print(f"   当前目录: {current_dir}")
            print(f"   检测到的项目根目录: {project_root}")
            print("\n💡 建议:")
            print("   1. 从项目目录执行脚本:")
            print(f"      cd {project_root} && python ~/.claude/skills/install-apk/scripts/install_apk.py {args.variant_build_type} {args.device}")
            print("   2. 或使用 --project-dir 参数:")
            print(f"      python ~/.claude/skills/install-apk/scripts/install_apk.py {args.variant_build_type} {args.device} --project-dir {project_root}")

            # 检查找到的项目根目录是否有效
            if not (project_root / "gradlew").exists():
                print(f"\n❌ 在检测到的项目根目录中未找到 gradlew: {project_root}")
                print("   请使用 --project-dir 参数明确指定项目目录")
                sys.exit(1)

    # 检测应用模块（app 或 eapp）
    app_module = detect_app_module(project_root)

    print(f"📁 项目根目录: {project_root}")
    print(f"📱 应用模块: {app_module}")
    print(f"🔨 构建变体: {variant}")
    print(f"🔨 构建类型: {build_type}")
    print(f"⚠️  注意: 每次都会重新编译，确保安装最新代码！")

    # 注意：不再使用 os.chdir，而是在每个命令中指定 cwd 参数
    # os.chdir(project_root)

    # 1. 清理（可选）
    if args.clean:
        run_command(["./gradlew", "clean"], "清理项目", cwd=project_root)

    # 2. 编译 APK（每次都重新编译）
    print(f"\n📦 开始编译: {variant}{build_type}")
    gradle_task = f"assemble{variant[0].upper()}{variant[1:]}{build_type}"
    run_command(["./gradlew", gradle_task], f"编译 {variant}{build_type}", cwd=project_root)

    # 3. 查找 APK
    apk_path = find_apk(variant, build_type, project_root, app_module)

    # 3.1 提取并打印版本信息
    version_info = get_apk_version_info(apk_path)
    if version_info:
        print(f"📋 包名: {version_info['package_name']}")
        print(f"📋 版本号: {version_info['version_name']} (versionCode: {version_info['version_code']})")
    else:
        print("⚠️  无法获取 APK 版本信息（aapt 可能未安装）")

    # 4. 连接设备（智能连接逻辑）
    device_addr = args.device
    print(f"\n📱 检查设备连接: {device_addr}")

    # 检查设备是否已连接
    if is_device_connected(device_addr):
        print(f"✅ 设备 {device_addr} 已连接，无需重新连接")
    else:
        print(f"⚠️  设备 {device_addr} 未连接，开始连接...")
        # 尝试连接
        result = run_command(
            ["adb", "connect", device_addr],
            f"连接设备 {device_addr}",
            check=False
        )

        # 等待设备就绪
        print("⏳ 等待设备就绪...")
        run_command(["adb", "wait-for-device"], "等待设备")

    # 检查连接状态
    result = subprocess.run(
        ["adb", "devices"],
        capture_output=True,
        text=True
    )
    print(f"\n当前连接的设备:\n{result.stdout}")

    # 5. 安装 APK（使用 -s 参数指定设备，避免多设备冲突）
    print(f"\n📲 安装 APK: {apk_path.name}")
    run_command(
        ["adb", "-s", device_addr, "install", "-r", str(apk_path)],
        "安装 APK"
    )

    print("\n✅ 完成!")
    if version_info:
        print(f"✅ 已安装 v{version_info['version_name']} 到设备 {device_addr}")
    else:
        print(f"✅ 已安装最新编译的版本到设备 {device_addr}")


if __name__ == "__main__":
    main()