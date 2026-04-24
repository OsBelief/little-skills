#!/bin/bash

# GitLab Workflow 创建脚本
# 用法: ./create_workflow.sh <issue_title> <base_branch> [issue_description]

# 设置 UTF-8 编码，确保中文正确处理
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

set -e

# 参数检查
if [ $# -lt 2 ]; then
  echo "用法: $0 <issue_title> <base_branch> [issue_description]"
  echo ""
  echo "示例:"
  echo "  $0 fix_#594465_log_print_optimize private_v3.11"
  echo "  $0 fix_#594465_log_print_optimize private_v3.11 '优化日志打印'"
  exit 1
fi

ISSUE_TITLE="$1"
BASE_BRANCH="$2"
ISSUE_DESCRIPTION="${3:-自动创建的工作流 issue}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}ℹ${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

log_step() {
  echo -e "${YELLOW}▶${NC} $1"
}

# 检查 jq 依赖
if ! command -v jq >/dev/null 2>&1; then
  log_error "jq 未安装，请执行: brew install jq"
  exit 1
fi

# 检查是否在 git 仓库中
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log_error "不在 git 仓库中"
  exit 1
fi

log_info "GitLab Workflow 创建工具"
echo ""

# 步骤 1: 获取项目信息
log_step "步骤 1/7: 获取项目信息..."
GIT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$GIT_REMOTE" ]; then
  log_error "找不到 git remote origin"
  exit 1
fi

# 提取项目路径
PROJECT_PATH=$(echo "$GIT_REMOTE" | sed -E 's|ssh://git@[^/]*/||' | sed 's|\.git$||')
log_info "项目路径: $PROJECT_PATH"

# 检查基础分支是否存在
if ! git rev-parse --verify "origin/$BASE_BRANCH" >/dev/null 2>&1; then
  log_error "基础分支 $BASE_BRANCH 不存在"
  exit 1
fi

log_info "基础分支: $BASE_BRANCH"
echo ""

# 步骤 2: 检查 GitLab Token
log_step "步骤 2/7: 检查 GitLab Token..."
GITLAB_ACCESS_TOKEN="${GITLAB_ACCESS_TOKEN:-$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env 2>/dev/null | head -n1 | cut -d= -f2-)}"

if [ -z "$GITLAB_ACCESS_TOKEN" ]; then
  log_error "未找到 GITLAB_ACCESS_TOKEN"
  echo ""
  echo "请执行以下步骤："
  echo "  1. 前往 https://gitlab.xylink.com/-/user_settings/personal_access_tokens"
  echo "  2. 创建 Personal Access Token（勾选 api 权限）"
  echo "  3. 执行: mkdir -p ~/.xyinfpilot"
  echo "  4. 执行: echo 'GITLAB_ACCESS_TOKEN=<token>' >> ~/.xyinfpilot/.env"
  exit 1
fi

log_info "找到 GitLab Access Token"
echo ""

# 步骤 3: 获取当前用户信息
log_step "步骤 3/7: 获取当前用户信息..."
USER_INFO=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
  "https://gitlab.xylink.com/api/v4/user")

USER_ID=$(echo "$USER_INFO" | jq -r '.id')
USER_NAME=$(echo "$USER_INFO" | jq -r '.name')
USER_USERNAME=$(echo "$USER_INFO" | jq -r '.username')

if [ -z "$USER_ID" ] || [ "$USER_ID" = "null" ]; then
  log_error "无法获取用户信息，请检查 token"
  exit 1
fi

log_info "当前用户: $USER_NAME (@$USER_USERNAME)"
echo ""

# 步骤 4: 创建 Issue
log_step "步骤 4/7: 创建 GitLab Issue..."
ENCODED_PROJECT_PATH=$(echo -n "$PROJECT_PATH" | jq -sRr @uri)

ISSUE_RESPONSE=$(curl -s --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
  "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/issues" \
  --data-urlencode "title=${ISSUE_TITLE}" \
  --data-urlencode "description=${ISSUE_DESCRIPTION}" \
  --data "assignee_id=${USER_ID}")

ISSUE_ID=$(echo "$ISSUE_RESPONSE" | jq -r '.iid')
ISSUE_WEB_URL=$(echo "$ISSUE_RESPONSE" | jq -r '.web_url')

if [ -z "$ISSUE_ID" ] || [ "$ISSUE_ID" = "null" ]; then
  log_error "创建 Issue 失败"
  echo "$ISSUE_RESPONSE" | jq -r '.message // .error'
  exit 1
fi

log_info "Issue 创建成功: #$ISSUE_ID"
echo "  链接: $ISSUE_WEB_URL"
echo ""

# 步骤 5: 创建分支
log_step "步骤 5/7: 创建新分支..."

# 检查分支是否已存在
BRANCH_EXISTS=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
  "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/repository/branches/${ISSUE_TITLE}" | jq -r '.name')

if [ "$BRANCH_EXISTS" = "$ISSUE_TITLE" ]; then
  log_info "分支 $ISSUE_TITLE 已存在，跳过创建"
else
  BRANCH_RESPONSE=$(curl -s --request POST \
    --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
    "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/repository/branches" \
    --data-urlencode "branch=${ISSUE_TITLE}" \
    --data-urlencode "ref=${BASE_BRANCH}")

  BRANCH_NAME=$(echo "$BRANCH_RESPONSE" | jq -r '.name')

  if [ -z "$BRANCH_NAME" ] || [ "$BRANCH_NAME" = "null" ]; then
    log_error "创建分支失败"
    echo "$BRANCH_RESPONSE" | jq -r '.message // .error'
    exit 1
  fi

  log_info "分支创建成功: $BRANCH_NAME"
fi
echo ""

# 步骤 6: 本地创建并切换分支
log_step "步骤 6/7: 本地创建并切换分支..."

# 拉取最新远程引用（包括步骤 5 通过 API 新创建的远程分支）
git fetch origin >/dev/null 2>&1

# 检查本地分支是否存在
if git rev-parse --verify "$ISSUE_TITLE" >/dev/null 2>&1; then
  log_info "本地分支 $ISSUE_TITLE 已存在，切换到该分支"
  git checkout "$ISSUE_TITLE" 2>/dev/null || {
    log_error "切换分支失败"
    exit 1
  }
else
  # track 远程已创建的分支（步骤 5 通过 API 创建）
  git checkout -b "$ISSUE_TITLE" "origin/$ISSUE_TITLE" 2>/dev/null || {
    log_error "创建本地分支失败（track 远程分支 $ISSUE_TITLE）"
    exit 1
  }
  log_info "本地分支创建成功（tracking origin/$ISSUE_TITLE）: $ISSUE_TITLE"
fi

log_info "本地分支就绪"
echo ""

# 步骤 7: 创建 Merge Request
log_step "步骤 7/7: 创建 Merge Request..."

# 检查 MR 是否已存在
EXISTING_MR=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
  "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/merge_requests?source_branch=${ISSUE_TITLE}&target_branch=${BASE_BRANCH}" | jq -r '.[0].iid')

if [ "$EXISTING_MR" != "null" ] && [ -n "$EXISTING_MR" ]; then
  log_info "MR 已存在: !${EXISTING_MR}"
  MR_WEB_URL=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
    "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/merge_requests/${EXISTING_MR}" | jq -r '.web_url')
else
  # 构建 MR 描述：关联信息在前，Issue 描述在后
  if [ -n "$ISSUE_DESCRIPTION" ] && [ "$ISSUE_DESCRIPTION" != "自动创建的工作流 issue" ]; then
    MR_DESCRIPTION="Closes #${ISSUE_ID}

---

${ISSUE_DESCRIPTION}"
  else
    MR_DESCRIPTION="Closes #${ISSUE_ID}"
  fi

  MR_RESPONSE=$(curl -s --request POST \
    --header "PRIVATE-TOKEN: $GITLAB_ACCESS_TOKEN" \
    "https://gitlab.xylink.com/api/v4/projects/${ENCODED_PROJECT_PATH}/merge_requests" \
    --data-urlencode "source_branch=${ISSUE_TITLE}" \
    --data-urlencode "target_branch=${BASE_BRANCH}" \
    --data-urlencode "title=${ISSUE_TITLE}" \
    --data-urlencode "description=${MR_DESCRIPTION}" \
    --data "assignee_id=${USER_ID}" \
    --data "remove_source_branch=false")

  MR_ID=$(echo "$MR_RESPONSE" | jq -r '.iid')
  MR_WEB_URL=$(echo "$MR_RESPONSE" | jq -r '.web_url')

  if [ -z "$MR_ID" ] || [ "$MR_ID" = "null" ]; then
    log_error "创建 MR 失败"
    echo "$MR_RESPONSE" | jq -r '.message // .error'
    exit 1
  fi

  log_info "MR 创建成功: !${MR_ID}"
fi

echo ""
echo -e "${GREEN}✓ 工作流创建完成${NC}"
echo ""
echo "创建的资源："
echo "  Issue:   #$ISSUE_ID - $ISSUE_WEB_URL"
echo "  分支:    $ISSUE_TITLE"
echo "  MR:      !${MR_ID} - $MR_WEB_URL"
echo ""
echo "所有项目已分配给你，可以开始开发了！"
