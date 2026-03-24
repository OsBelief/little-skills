#!/bin/bash
# Jenkins Build Trigger Script
# 用于触发 Jenkins 项目的构建

set -e

# 默认值
JENKINS_URL="${JENKINS_URL:-http://10.0.0.60:8080}"
JOB_PATH=""
PROJECT=""
BRANCH=""
DELAY="0sec"
COOKIE_FILE="/tmp/jenkins_cookies_$$_$(date +%s).txt"

# 帮助信息
show_help() {
    cat << EOF
用法: trigger_build.sh [选项]

触发 Jenkins 项目构建

选项:
  --url URL              Jenkins 服务器地址 (默认: http://10.0.0.60:8080)
  --job-path PATH        完整的 Job 路径 (如: job/becky/job/private_v3.11)
  --project NAME         项目名称
  --branch NAME          分支名称
  --delay TIME           延迟启动时间 (默认: 0sec)
  -h, --help             显示此帮助信息

示例:
  # 使用 Job 路径触发
  trigger_build.sh --job-path "job/becky/job/private_v3.11"

  # 使用项目和分支触发
  trigger_build.sh --project becky --branch private_v3.11

  # 自定义 Jenkins URL
  trigger_build.sh --url http://jenkins.example.com:8080 --project myproject --branch main

环境变量:
  JENKINS_URL            Jenkins 服务器地址

注意:
  - --job-path 优先级高于 --project 和 --branch
  - 需要能访问 Jenkins 服务器的网络连接
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            JENKINS_URL="$2"
            shift 2
            ;;
        --job-path)
            JOB_PATH="$2"
            shift 2
            ;;
        --project)
            PROJECT="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "❌ 未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 构建 Job 路径
if [ -n "$JOB_PATH" ]; then
    # 使用提供的完整 Job 路径
    FULL_PATH="$JOB_PATH"
elif [ -n "$PROJECT" ] && [ -n "$BRANCH" ]; then
    # 从项目和分支构建路径
    FULL_PATH="job/${PROJECT}/job/${BRANCH}"
else
    echo "❌ 错误: 必须指定 --job-path 或 (--project 和 --branch)"
    show_help
    exit 1
fi

# 构建 URL
BUILD_URL="${JENKINS_URL}/${FULL_PATH}/build?delay=${DELAY}"

echo "📦 Jenkins 构建触发器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Jenkins URL: $JENKINS_URL"
echo "Job 路径: $FULL_PATH"
echo "延迟: $DELAY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 清理函数
cleanup() {
    rm -f "$COOKIE_FILE"
}
trap cleanup EXIT

# 步骤 1: 获取 CSRF Crumb
echo "🔐 步骤 1: 获取 CSRF Crumb..."
CRUMB_RESPONSE=$(curl -s -c "$COOKIE_FILE" "${JENKINS_URL}/crumbIssuer/api/xml" 2>&1)

if echo "$CRUMB_RESPONSE" | grep -q "<crumb>"; then
    CRUMB=$(echo "$CRUMB_RESPONSE" | grep -o '<crumb>[^<]*</crumb>' | sed 's/<crumb>\(.*\)<\/crumb>/\1/')
    CRUMB_FIELD=$(echo "$CRUMB_RESPONSE" | grep -o '<crumbRequestField>[^<]*</crumbRequestField>' | sed 's/<crumbRequestField>\(.*\)<\/crumbRequestField>/\1/')
    echo "✅ Crumb 获取成功: ${CRUMB:0:20}..."
else
    echo "⚠️  警告: 无法获取 Crumb，可能 Jenkins 未启用 CSRF 保护或需要认证"
    CRUMB=""
    CRUMB_FIELD="Jenkins-Crumb"
fi

# 步骤 2: 触发构建
echo "🚀 步骤 2: 触发构建..."
echo "构建 URL: $BUILD_URL"
echo ""

# 发送构建请求
if [ -n "$CRUMB" ]; then
    # 使用 Crumb
    HTTP_CODE=$(curl -X POST "$BUILD_URL" \
        -b "$COOKIE_FILE" \
        -H "$CRUMB_FIELD: $CRUMB" \
        -s -o /dev/null -w "%{http_code}" 2>&1)
else
    # 不使用 Crumb（适用于禁用 CSRF 的情况）
    HTTP_CODE=$(curl -X POST "$BUILD_URL" \
        -s -o /dev/null -w "%{http_code}" 2>&1)
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查响应
case $HTTP_CODE in
    201)
        echo "✅ 构建触发成功！"
        echo ""
        echo "📊 查看构建状态:"
        echo "  - 构建页面: ${JENKINS_URL}/${FULL_PATH}/"
        echo "  - 构建历史: ${JENKINS_URL}/${FULL_PATH}/builds"
        echo "  - 控制台日志: ${JENKINS_URL}/${FULL_PATH}/lastBuild/console"
        exit 0
        ;;
    403)
        echo "❌ 认证失败 (403)"
        echo ""
        echo "可能的原因:"
        echo "  1. Jenkins 启用了认证，需要提供用户名和 API Token"
        echo "  2. CSRF Token 无效或过期"
        echo "  3. 用户没有触发此 Job 的权限"
        echo ""
        echo "解决方法:"
        echo "  - 在浏览器中登录 Jenkins 并手动触发"
        echo "  - 配置 Jenkins API Token 并修改脚本支持认证"
        exit 1
        ;;
    404)
        echo "❌ Job 不存在 (404)"
        echo ""
        echo "请检查:"
        echo "  - Job 路径是否正确: $FULL_PATH"
        echo "  - Job 是否存在于 Jenkins 中"
        exit 1
        ;;
    *)
        echo "❌ 未知错误 (HTTP $HTTP_CODE)"
        echo ""
        echo "请检查 Jenkins 服务器状态和配置"
        exit 1
        ;;
esac
