#!/usr/bin/env python3
"""
JSON 格式化辅助脚本
从日志中提取 JSON 并格式化,支持嵌套 JSON 字符串和截断处理
"""

import json
import re
import sys
from typing import Optional, Tuple


def extract_json_from_log(log_line: str) -> Tuple[Optional[str], bool]:
    """
    从日志行中提取 JSON

    Args:
        log_line: 日志行文本

    Returns:
        (json_string, is_truncated): 提取的 JSON 字符串和是否截断
    """
    # 尝试多种模式提取 JSON

    # 模式 1: key={json} - 匹配 m=, data=, json= 等字段后的 JSON
    pattern1 = r'(\w+)\s*=\s*(\{.*)'
    match1 = re.search(pattern1, log_line)
    if match1:
        json_str = match1.group(2)
        # 检查是否截断
        is_truncated = not is_json_complete(json_str)
        return json_str, is_truncated

    # 模式 2: 直接查找 { ... }
    start_idx = log_line.find('{')
    if start_idx != -1:
        json_str = log_line[start_idx:]
        is_truncated = not is_json_complete(json_str)
        return json_str, is_truncated

    return None, False


def is_json_complete(json_str: str) -> bool:
    """
    检查 JSON 字符串是否完整

    Args:
        json_str: JSON 字符串

    Returns:
        是否完整
    """
    # 去除空白字符后的检查
    stripped = json_str.strip()

    # 简单检查括号是否匹配
    open_braces = stripped.count('{')
    close_braces = stripped.count('}')
    open_brackets = stripped.count('[')
    close_brackets = stripped.count(']')

    # 对于转义的 JSON 字符串,需要更复杂的检查
    # 这里做简单处理:如果最后一个字符不是 } 或 ],可能截断
    if stripped.endswith('{') or stripped.endswith('[') or stripped.endswith(','):
        return False
    if stripped.endswith('"') and not is_string_complete(stripped):
        return False

    # 检查括号平衡
    if open_braces > close_braces or open_brackets > close_brackets:
        return False

    return True


def is_string_complete(s: str) -> bool:
    """
    检查字符串中的引号是否平衡(考虑转义)

    Args:
        s: 字符串

    Returns:
        引号是否平衡
    """
    in_string = False
    i = 0
    while i < len(s):
        if s[i] == '\\':
            i += 2  # 跳过转义字符
            continue
        if s[i] == '"':
            in_string = not in_string
        i += 1
    return not in_string


def format_json(json_str: str, max_depth: int = 5, current_depth: int = 0) -> str:
    """
    格式化 JSON,处理嵌套的 JSON 字符串

    Args:
        json_str: JSON 字符串
        max_depth: 最大解析深度
        current_depth: 当前深度

    Returns:
        格式化后的 JSON 字符串
    """
    if current_depth >= max_depth:
        # 达到最大深度,不再解析嵌套
        try:
            obj = json.loads(json_str)
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except:
            return json_str

    # 检查是否截断
    if not is_json_complete(json_str):
        return format_truncated_json(json_str)

    try:
        # 尝试解析 JSON
        obj = json.loads(json_str)

        # 如果是字典,检查是否有嵌套的 JSON 字段
        if isinstance(obj, dict):
            # 需要递归解析的字段名
            nested_json_fields = [
                'commonJson', 'multiScreen', 'multiScreen1', 'multiScreen2', 'multiScreen3',
                'customizedLayout', 'notifySet', 'config', 'settings', 'options',
                'data', 'payload', 'metadata'
            ]

            for key in nested_json_fields:
                if key in obj and isinstance(obj[key], str):
                    # 尝试解析嵌套的 JSON
                    try:
                        nested_obj = json.loads(obj[key])
                        # 如果成功解析,继续递归
                        formatted_nested = format_json(
                            json.dumps(nested_obj, ensure_ascii=False),
                            max_depth,
                            current_depth + 1
                        )
                        # 将格式化后的嵌套 JSON 转回对象
                        obj[key] = json.loads(formatted_nested)
                    except:
                        # 解析失败,保持原样
                        pass

        return json.dumps(obj, ensure_ascii=False, indent=2)

    except json.JSONDecodeError as e:
        # JSON 解析失败,可能是截断或格式错误
        return format_truncated_json(json_str)


def format_truncated_json(json_str: str) -> str:
    """
    格式化截断的 JSON(不补全)

    Args:
        json_str: 截断的 JSON 字符串

    Returns:
        部分格式化的 JSON
    """
    lines = []
    indent_level = 0
    indent = '  '

    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        char = json_str[i]

        # 处理转义
        if escape_next:
            i += 1
            continue

        if char == '\\':
            escape_next = True
            i += 1
            continue

        # 字符串状态切换
        if char == '"':
            in_string = not in_string

        if not in_string:
            if char == '{' or char == '[':
                # 添加换行和缩进
                lines.append(char)
                indent_level += 1
                # 检查是否有后续内容
                if i + 1 < len(json_str) and json_str[i + 1].strip():
                    lines.append(indent * indent_level)
            elif char == '}' or char == ']':
                indent_level = max(0, indent_level - 1)
                lines.append(char)
            elif char == ',':
                lines.append(char)
                # 检查是否有后续内容
                if i + 1 < len(json_str) and json_str[i + 1].strip():
                    lines.append(indent * indent_level)
            elif char == ':':
                lines.append(char + ' ')
            else:
                # 其他字符
                if char.strip():
                    # 如果当前行还没有内容,添加缩进
                    if not lines or not lines[-1].strip():
                        lines.append(indent * indent_level)
                    # 添加字符
                    if lines:
                        lines[-1] += char
                    else:
                        lines.append(char)
        else:
            # 在字符串内,直接添加字符
            if not lines:
                lines.append(char)
            else:
                lines[-1] += char

        i += 1

    return '\n'.join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: format_json.py '<log_line_or_json>'")
        sys.exit(1)

    input_text = ' '.join(sys.argv[1:])

    # 尝试提取 JSON
    json_str, is_truncated = extract_json_from_log(input_text)

    if json_str is None:
        print("未找到 JSON,请检查输入")
        print(f"输入: {input_text}")
        sys.exit(1)

    # 格式化
    formatted = format_json(json_str)

    # 输出
    print("格式化结果:")
    print("=" * 80)
    print(formatted)
    print("=" * 80)

    if is_truncated:
        print("\n注意: JSON 在日志中被截断,输出仅到截断位置,未补全")


if __name__ == '__main__':
    main()
