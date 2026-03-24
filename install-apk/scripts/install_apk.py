#!/usr/bin/env python3
"""
APK 编译和安装脚本
用于 Android TV 盒子应用（Becky）的自动化编译和安装

用法:
    python install_apk.py <variant_build_type> <device_address> [options]

示例:
    python install_apk.py anchorPrivDebug 172.33.50.2:5353
    python install_apk.py gillPrivRelease 192.168.1.100:5555 --clean
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path


def parse_variant_and_build_type(full_variant):
    """
    解析完整的 variant 字符串，提取 variant 和 build type

    例如:
    - anchorPrivDebug -> variant='anchorPriv', build_type='Debug'
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


def run_command(cmd, description, check=True):
    """执行命令并显示输出"""
    print(f"\n🔧 {description}...")
    print(f"命令: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if result.stdout:
        print(result.stdout)

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


def find_apk(variant, build_type, project_root):
    """查找编译生成的 APK 文件"""
    build_type_lower = build_type.lower()
    # APK 通常在以下位置
    possible_paths = [
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"eapp-{variant}-{build_type_lower}.apk",
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"eapp-{variant}-{build_type_lower}-unsigned.apk",
        project_root / "eapp" / "build" / "outputs" / "apk" / f"{variant}" / build_type_lower / f"eapp.apk",
    ]

    for path in possible_paths:
        if path.exists():
            print(f"✅ 找到 APK: {path}")
            return path

    # 如果没找到，尝试搜索
    print("⚠️  未在预期位置找到 APK，搜索中...")
    build_dir = project_root / "eapp" / "build" / "outputs" / "apk"
    if build_dir.exists():
        for apk_file in build_dir.rglob("*.apk"):
            if variant in str(apk_file) and build_type_lower in str(apk_file):
                print(f"✅ 找到 APK: {apk_file}")
                return apk_file

    print(f"❌ 未找到 variant '{variant}' build type '{build_type}' 对应的 APK 文件")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="编译并安装 Becky APK 到指定设备",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("variant_build_type",
                       help="完整构建变体，格式: <variant><Debug|Release>，如 anchorPrivDebug, gillPubRelease")
    parser.add_argument("device", help="设备地址，格式: IP:PORT (如 172.33.50.2:5353)")
    parser.add_argument("--clean", action="store_true", help="编译前执行 clean（默认不执行）")

    args = parser.parse_args()

    # 解析 variant 和 build type
    variant, build_type = parse_variant_and_build_type(args.variant_build_type)

    # 获取项目根目录
    script_dir = Path(__file__).parent.parent.parent.parent.parent
    project_root = script_dir / "Documents" / "xylink" / "workspace" / "becky2" / "becky"

    if not project_root.exists():
        # 尝试当前目录
        project_root = Path.cwd()

    print(f"📁 项目根目录: {project_root}")
    print(f"🔨 构建变体: {variant}")
    print(f"🔨 构建类型: {build_type}")
    os.chdir(project_root)

    # 1. 清理（可选）
    if args.clean:
        run_command(["./gradlew", "clean"], "清理项目")

    # 2. 编译 APK
    print(f"\n📦 开始编译: {variant}{build_type}")
    gradle_task = f"assemble{variant[0].upper()}{variant[1:]}{build_type}"
    run_command(["./gradlew", gradle_task], f"编译 {variant}{build_type}")

    # 3. 查找 APK
    apk_path = find_apk(variant, build_type, project_root)

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


if __name__ == "__main__":
    main()