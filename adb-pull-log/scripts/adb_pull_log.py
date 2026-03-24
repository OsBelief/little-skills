#!/usr/bin/env python3
"""
ADB 日志拉取工具
从 Android TV 设备拉取日志文件到本地计算机
"""

import sys
import subprocess
import os
from datetime import datetime

def run_command(cmd):
    """执行 shell 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"

def main():
    """主函数"""
    # 解析参数
    device = sys.argv[1] if len(sys.argv) > 1 else "172.33.50.2:5353"
    source_file = sys.argv[2] if len(sys.argv) > 2 else "logcat_full.log"

    # 默认路径
    source_path = f"/data/log/{source_file}"
    desktop_path = os.path.expanduser("~/Desktop")

    print("═══════════════════════════════════════")
    print("  ADB 日志拉取工具")
    print("═══════════════════════════════════════")
    print(f"\n目标设备: {device}")
    print(f"源文件: {source_path}")

    # [1/5] 检查设备连接和权限
    print("\n[1/5] 检查设备连接和权限...")

    # 检查设备连接
    success, stdout, _ = run_command(f"adb devices | grep '{device}'")
    if not success or not stdout:
        print(f"  ✗ 设备未连接")
        print("\n建议:")
        print("  1. 检查设备是否开机并连接到网络")
        print("  2. 确认 ADB 调试已启用")
        print("  3. 验证 IP 地址和端口是否正确")
        print("  4. 尝试手动执行：adb connect", device)
        return 1
    print("  ✓ 设备已连接")

    # 检查 root 权限
    success, stdout, _ = run_command(f"adb -s {device} shell whoami")
    if not success or stdout != "root":
        print(f"  ✗ 未获取 root 权限（当前用户：{stdout if stdout else 'unknown'}）")
        print("\n正在尝试获取 root 权限...")
        print(f"→ 调用 /adb-connect {device}")

        # 调用 adb-connect skill
        skills_dir = os.path.expanduser("~/.claude/skills")
        connect_script = os.path.join(skills_dir, "adb-connect/scripts/adb_connect.py")
        connect_success, connect_output, _ = run_command(
            f"python {connect_script} {device}"
        )

        if not connect_success:
            print(f"\n✗ 无法获取 root 权限")
            return 1

        # 重新验证权限
        success, stdout, _ = run_command(f"adb -s {device} shell whoami")
        if not success or stdout != "root":
            print(f"\n✗ 仍未获取 root 权限")
            return 1

        print(f"  ✓ 已获取 root 权限（通过 adb-connect）")
    else:
        print("  ✓ 已获取 root 权限")

    # [2/5] 检查源文件
    print("\n[2/5] 检查源文件...")

    success, stdout, _ = run_command(f"adb -s {device} shell ls -lh {source_path}")
    if not success or not stdout:
        print(f"  ✗ 文件不存在：{source_path}")

        # 尝试列出可用的日志文件
        print("\n可用的日志文件：")
        success, stdout, _ = run_command(f"adb -s {device} shell 'ls -lh /data/log/*.log 2>/dev/null'")
        if success and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")

        print("\n建议:")
        print("  1. 检查文件名是否正确")
        print("  2. 确认日志目录是否为 /data/log/")
        print("  3. 尝试拉取其他可用的日志文件")
        return 1

    # 解析文件大小
    parts = stdout.split()
    if len(parts) >= 5:
        size_str = parts[4]
        print(f"  ✓ 文件存在")
        print(f"  大小: {size_str}")
    else:
        print(f"  ✓ 文件存在")

    # [3/5] 检查本地目标文件
    print("\n[3/5] 检查本地目标文件...")

    target_file = source_file
    target_path = os.path.join(desktop_path, target_file)

    if os.path.exists(target_path):
        print(f"  ⚠ ~/Desktop/{target_file} 已存在")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 处理文件扩展名
        if '.' in target_file:
            name, ext = target_file.rsplit('.', 1)
            target_file = f"{name}_{timestamp}.{ext}"
        else:
            target_file = f"{target_file}_{timestamp}"

        target_path = os.path.join(desktop_path, target_file)
        print(f"  → 自动重命名为: {target_file}")
    else:
        print(f"  ✓ ~/Desktop/{target_file} 可用")

    # [4/5] 拉取日志文件
    print("\n[4/5] 正在拉取日志文件...")

    success, stdout, stderr = run_command(
        f"adb -s {device} pull {source_path} {target_path}"
    )

    if not success:
        print(f"  ✗ 拉取失败")
        if stderr:
            print(f"  错误信息: {stderr}")
        return 1

    print("  ✓ 拉取完成")

    # [5/5] 显示文件信息
    print("\n[5/5] 显示文件信息...")

    if os.path.exists(target_path):
        # 获取文件大小
        size_bytes = os.path.getsize(target_path)

        # 转换为可读格式
        if size_bytes < 1024:
            size_readable = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_readable = f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_readable = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_readable = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

        # 获取文件行数（仅对文本文件）
        line_count = 0
        try:
            success, stdout, _ = run_command(f"wc -l '{target_path}'")
            if success and stdout:
                line_count = stdout.split()[0]
        except:
            pass

        print(f"  本地路径: ~/Desktop/{target_file}")
        print(f"  文件大小: {size_readable}")
        if line_count:
            print(f"  文件行数: {line_count} 行")
    else:
        print(f"  ✗ 文件未找到: {target_path}")
        return 1

    print("\n═══════════════════════════════════════")
    print("✓ 拉取成功！")
    print(f"  日志已保存到: ~/Desktop/{target_file}")
    print("═══════════════════════════════════════")

    return 0

if __name__ == "__main__":
    sys.exit(main())
