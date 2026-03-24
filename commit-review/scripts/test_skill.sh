#!/bin/bash

# Git Commit Review Skill 测试脚本

echo "================================"
echo "Git Commit Review Skill 测试"
echo "================================"
echo ""

# 获取当前分支名
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $BRANCH_NAME"
echo ""

# 解析分支名
# 格式: <type>_<id>_<description>
# 例如: fix_#596754_cloud_config_default_layout_1

# 提取类型（第一个下划线之前的部分）
TYPE=$(echo "$BRANCH_NAME" | cut -d'_' -f1)
echo "类型: $TYPE"

# 提取 ID（查找 # 开头的部分）
ID=$(echo "$BRANCH_NAME" | grep -o '#[0-9]*')
echo "ID: $ID"

# 提取描述部分（ID 之后的部分）
DESCRIPTION_PART=$(echo "$BRANCH_NAME" | sed "s/${TYPE}_${ID}_//" | sed 's/_/ /g')
echo "描述部分: $DESCRIPTION_PART"
echo ""

# 生成 commit message
COMMIT_MESSAGE="${TYPE}: ${DESCRIPTION_PART} [${ID}]"
echo "生成的 Commit Message:"
echo "$COMMIT_MESSAGE"
echo ""

# 检查描述长度
WORD_COUNT=$(echo "$DESCRIPTION_PART" | wc -w | tr -d ' ')
echo "描述单词数: $WORD_COUNT"

if [ $WORD_COUNT -gt 20 ]; then
    echo "⚠️  警告: 描述超过 20 个单词，将被截断"
    TRUNCATED=$(echo "$DESCRIPTION_PART" | cut -d' ' -f1-20)
    COMMIT_MESSAGE="${TYPE}: ${TRUNCATED}... [${ID}]"
    echo "截断后的 Commit Message:"
    echo "$COMMIT_MESSAGE"
fi
echo ""

# 显示 git 状态
echo "================================"
echo "Git 状态"
echo "================================"
git status --short
echo ""

# 如果有暂存的变更，显示 diff
if git diff --staged --quiet; then
    echo "没有暂存的变更"
else
    echo "暂存的变更:"
    git diff --staged --stat
fi
echo ""

echo "================================"
echo "测试完成"
echo "================================"
