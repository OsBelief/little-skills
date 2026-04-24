# GitLab Workflow 手动执行命令参考

## 目录
- [前置准备](#前置准备)
- [步骤 1: 获取当前用户信息](#步骤-1-获取当前用户信息)
- [步骤 2: 创建 Issue](#步骤-2-创建-issue)
- [步骤 3: 创建远程分支](#步骤-3-创建远程分支)
- [步骤 4: 本地创建并切换分支](#步骤-4-本地创建并切换分支)
- [步骤 5: 创建 Merge Request](#步骤-5-创建-merge-request)
- [完整一键执行](#完整一键执行)

---

## 前置准备

```bash
# API 基础地址
BASE='https://gitlab.xylink.com/api/v4'

# Token（从 ~/.xyinfpilot/.env 读取）
TOKEN=$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env | head -n1 | cut -d= -f2- | sed 's/^"//; s/"$//')

# 项目路径编码（从 git remote 自动推断）
PROJECT_PATH=$(git remote get-url origin | sed -E 's|ssh://git@[^/]*/||' | sed 's|\.git$||')
PROJ=$(echo -n "$PROJECT_PATH" | jq -sRr @uri)

# 验证 Token 有效性
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/user" | jq -r '.name // "TOKEN 无效"'
```

---

## 步骤 1: 获取当前用户信息

```bash
USER_INFO=$(curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/user")
USER_ID=$(echo "$USER_INFO" | jq -r '.id')
USER_NAME=$(echo "$USER_INFO" | jq -r '.name')

echo "用户: $USER_NAME (ID: $USER_ID)"
```

---

## 步骤 2: 创建 Issue

```bash
ISSUE_TITLE="fix_#594465_log_print_optimize"
ISSUE_DESCRIPTION="自动创建的工作流 issue"

ISSUE_RESPONSE=$(curl -sS --request POST \
  --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/issues" \
  --data-urlencode "title=${ISSUE_TITLE}" \
  --data-urlencode "description=${ISSUE_DESCRIPTION}" \
  --data "assignee_id=${USER_ID}")

ISSUE_IID=$(echo "$ISSUE_RESPONSE" | jq -r '.iid')
ISSUE_WEB_URL=$(echo "$ISSUE_RESPONSE" | jq -r '.web_url')

echo "Issue: #$ISSUE_IID - $ISSUE_WEB_URL"
```

---

## 步骤 3: 创建远程分支

```bash
BASE_BRANCH="private_v3.11"

# 先检查分支是否已存在
BRANCH_CHECK=$(curl -sS --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/repository/branches/${ISSUE_TITLE}" | jq -r '.name')

if [ "$BRANCH_CHECK" = "$ISSUE_TITLE" ]; then
  echo "分支已存在，跳过创建"
else
  BRANCH_RESPONSE=$(curl -sS --request POST \
    --header "PRIVATE-TOKEN: $TOKEN" \
    "$BASE/projects/$PROJ/repository/branches" \
    --data-urlencode "branch=${ISSUE_TITLE}" \
    --data-urlencode "ref=${BASE_BRANCH}")

  BRANCH_NAME=$(echo "$BRANCH_RESPONSE" | jq -r '.name')

  if [ "$BRANCH_NAME" = "null" ] || [ -z "$BRANCH_NAME" ]; then
    echo "创建分支失败:"
    echo "$BRANCH_RESPONSE" | jq -r '.message // .error'
  else
    echo "分支创建成功: $BRANCH_NAME"
  fi
fi
```

---

## 步骤 4: 本地创建并切换分支

```bash
# 拉取最新远程引用（包括步骤 3 通过 API 新创建的远程分支）
git fetch origin

# 检查本地分支是否已存在
if git rev-parse --verify "$ISSUE_TITLE" >/dev/null 2>&1; then
  git checkout "$ISSUE_TITLE"
  echo "切换到已有分支: $ISSUE_TITLE"
else
  # track 远程已创建的分支
  git checkout -b "$ISSUE_TITLE" "origin/$ISSUE_TITLE"
  echo "创建并切换到分支: $ISSUE_TITLE (tracking origin/$ISSUE_TITLE)"
fi
```

---

## 步骤 5: 创建 Merge Request

```bash
# 先检查 MR 是否已存在
EXISTING_MR=$(curl -sS --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/merge_requests?source_branch=${ISSUE_TITLE}&target_branch=${BASE_BRANCH}" \
  | jq -r '.[0].iid')

if [ "$EXISTING_MR" != "null" ] && [ -n "$EXISTING_MR" ]; then
  MR_WEB_URL=$(curl -sS --header "PRIVATE-TOKEN: $TOKEN" \
    "$BASE/projects/$PROJ/merge_requests/${EXISTING_MR}" | jq -r '.web_url')
  echo "MR 已存在: !${EXISTING_MR} - $MR_WEB_URL"
else
  MR_DESCRIPTION="Closes #${ISSUE_IID}"

  MR_RESPONSE=$(curl -sS --request POST \
    --header "PRIVATE-TOKEN: $TOKEN" \
    "$BASE/projects/$PROJ/merge_requests" \
    --data-urlencode "source_branch=${ISSUE_TITLE}" \
    --data-urlencode "target_branch=${BASE_BRANCH}" \
    --data-urlencode "title=${ISSUE_TITLE}" \
    --data-urlencode "description=${MR_DESCRIPTION}" \
    --data "assignee_id=${USER_ID}" \
    --data "remove_source_branch=false")

  MR_IID=$(echo "$MR_RESPONSE" | jq -r '.iid')
  MR_WEB_URL=$(echo "$MR_RESPONSE" | jq -r '.web_url')

  if [ "$MR_IID" = "null" ] || [ -z "$MR_IID" ]; then
    echo "创建 MR 失败:"
    echo "$MR_RESPONSE" | jq -r '.message // .error'
  else
    echo "MR 创建成功: !${MR_IID} - $MR_WEB_URL"
  fi
fi
```

---

## 完整一键执行

将以下变量替换为实际值后执行：

```bash
ISSUE_TITLE="<issue 标题，如 fix_#594465_log_print_optimize>"
BASE_BRANCH="<基础分支，如 private_v3.11>"
ISSUE_DESCRIPTION="<issue 描述>"

# === 前置准备 ===
BASE='https://gitlab.xylink.com/api/v4'
TOKEN=$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env | head -n1 | cut -d= -f2- | sed 's/^"//; s/"$//')
PROJECT_PATH=$(git remote get-url origin | sed -E 's|ssh://git@[^/]*/||' | sed 's|\.git$||')
PROJ=$(echo -n "$PROJECT_PATH" | jq -sRr @uri)

# === 获取用户 ===
USER_ID=$(curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/user" | jq -r '.id')

# === 创建 Issue ===
ISSUE_IID=$(curl -sS --request POST --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/issues" \
  --data-urlencode "title=${ISSUE_TITLE}" \
  --data-urlencode "description=${ISSUE_DESCRIPTION}" \
  --data "assignee_id=${USER_ID}" | jq -r '.iid')
echo "Issue: #$ISSUE_IID"

# === 创建远程分支 ===
curl -sS --request POST --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/repository/branches" \
  --data-urlencode "branch=${ISSUE_TITLE}" \
  --data-urlencode "ref=${BASE_BRANCH}" | jq -r '.name' && echo "分支已创建"

# === 本地 track 远程分支 ===
git fetch origin && git checkout -b "$ISSUE_TITLE" "origin/$ISSUE_TITLE"

# === 创建 MR ===
curl -sS --request POST --header "PRIVATE-TOKEN: $TOKEN" \
  "$BASE/projects/$PROJ/merge_requests" \
  --data-urlencode "source_branch=${ISSUE_TITLE}" \
  --data-urlencode "target_branch=${BASE_BRANCH}" \
  --data-urlencode "title=${ISSUE_TITLE}" \
  --data-urlencode "description=Closes #${ISSUE_IID}" \
  --data "assignee_id=${USER_ID}" \
  --data "remove_source_branch=false" | jq '{iid, web_url}'
```
